#!/usr/bin/env python3
"""
Anti-artifact object-continuity validator for AI-generated video.

Implements the tiered validator described in datasets/anti_artifact_taxonomy.json:
cheap per-frame checks (perceptual hash, frozen-frame / loop detection) run on
every frame; detector-dependent checks (object count, size/aspect drift,
teleport candidates) run every DETECT_STRIDE frames and only need a detector
that returns axis-aligned boxes with a persistent id.

Core hashing/geometry functions only need numpy, so they can be unit-tested
without opencv or a detector installed. Reading real video files and running
the bundled default detector needs opencv-python and (optionally) ultralytics:

    pip install opencv-python ultralytics

Usage:
    python validate_video.py --video clip.mp4 --out clip.events.jsonl \
        --expected "person:1,knife:1" --model yolo11n.pt

Without --model, detection_checks is skipped and only the temporal
(hash/frozen/loop) checks run -- still useful for catching freezes and loops
on any video with just numpy + opencv installed.
"""
from __future__ import annotations

import argparse
import json
import sys
from dataclasses import dataclass, field
from typing import Iterable, Optional

import numpy as np

EVENT_SEVERITY = {
    "E03_NEAR_DUPLICATE_NONLOCAL": 2,
    "E04_FREEZE_RUN": 2,
    "E05_FRAME_RECREATION_RESET": 3,
    "E06_SEQUENCE_LOOP": 3,
    "A_COUNT_MISMATCH": 3,
    "A_COUNT_CHANGE": 1,
    "B03_SIZE_DRIFT_CANDIDATE": 2,
    "B04_ASPECT_RATIO_DRIFT_CANDIDATE": 2,
    "C01_TELEPORT_CANDIDATE": 3,
    # inferred to fill gaps left blank in the source event table -- see
    # datasets/anti_artifact_taxonomy.json "notes" for why these are inferred.
    "E01_IDENTITY_SWAP": 3,
    "E02_TEMPORAL_FLICKER": 1,
    "B01_BBOX_JUMP_CANDIDATE": 2,
    "B02_IOU_DROP_CANDIDATE": 2,
}


# --------------------------------------------------------------------------
# Pure numpy building blocks (no opencv/detector required)
# --------------------------------------------------------------------------

def tiny_gray(frame: np.ndarray, width: int = 64) -> np.ndarray:
    """Downscale an HxWx3 (or HxW) frame to a `width`-wide grayscale thumbnail.

    Uses plain numpy nearest-neighbor sampling so this has no opencv/PIL
    dependency and is safe to unit-test in isolation.
    """
    if frame.ndim == 3:
        gray = frame[..., :3].astype(np.float32).mean(axis=2)
    else:
        gray = frame.astype(np.float32)

    h, w = gray.shape
    height = max(1, round(width * h / w))
    xs = np.linspace(0, w - 1, width).round().astype(int)
    ys = np.linspace(0, h - 1, height).round().astype(int)
    return gray[np.ix_(ys, xs)]


def dhash64(gray: np.ndarray) -> int:
    """64-bit difference hash of a grayscale image (perceptual fingerprint)."""
    small = tiny_gray(gray, width=9) if gray.shape[1] != 9 else gray
    if small.shape != (8, 9):
        # tiny_gray(width=9) on a non-9-wide image can round to a slightly
        # different height; force it to exactly 8x9 for a stable 64-bit hash.
        xs = np.linspace(0, small.shape[1] - 1, 9).round().astype(int)
        ys = np.linspace(0, small.shape[0] - 1, 8).round().astype(int)
        small = small[np.ix_(ys, xs)]

    bits = small[:, 1:] > small[:, :-1]
    value = 0
    for bit in bits.flatten():
        value = (value << 1) | int(bit)
    return value


def hamming64(a: int, b: int) -> int:
    """Hamming distance between two 64-bit hashes."""
    return bin((a ^ b) & 0xFFFFFFFFFFFFFFFF).count("1")


def mean_abs_diff(a: np.ndarray, b: np.ndarray) -> float:
    """Mean absolute pixel difference between two same-shaped arrays."""
    return float(np.abs(a.astype(np.float32) - b.astype(np.float32)).mean())


def box_state(xyxy: tuple[float, float, float, float], frame_w: int, frame_h: int) -> dict:
    """Normalize an (x1, y1, x2, y2) box into center/area/aspect for drift checks."""
    x1, y1, x2, y2 = xyxy
    w = max(1e-6, x2 - x1)
    h = max(1e-6, y2 - y1)
    return {
        "cx": (x1 + x2) / 2 / frame_w,
        "cy": (y1 + y2) / 2 / frame_h,
        "area": (w * h) / (frame_w * frame_h),
        "aspect": w / h,
    }


def parse_expected_counts(items: str) -> dict:
    """Parse "class:count,class:count" into {class: count}, e.g. for --expected."""
    expected: dict[str, int] = {}
    for chunk in items.split(","):
        chunk = chunk.strip()
        if not chunk:
            continue
        name, _, count = chunk.partition(":")
        expected[name.strip()] = int(count) if count.strip() else 1
    return expected


# --------------------------------------------------------------------------
# Detector: thin wrapper so AntiArtifactValidator doesn't care which model
# backs it. Ships with an optional ultralytics/YOLO backend; swap in
# ByteTrack/SAM2 by implementing the same .track(frame) -> list[Track] API.
# --------------------------------------------------------------------------

@dataclass
class Track:
    id: int
    cls: str
    xyxy: tuple[float, float, float, float]
    lost: bool = False
    prev_state: Optional[dict] = None


class Detector:
    def __init__(self, model_path: Optional[str], imgsz: int = 640):
        self.imgsz = imgsz
        self.model = None
        if model_path:
            try:
                from ultralytics import YOLO  # type: ignore
            except ImportError as exc:  # pragma: no cover - optional dep
                raise ImportError(
                    "Detector(model_path=...) needs `pip install ultralytics`"
                ) from exc
            self.model = YOLO(model_path)

    def track(self, frame: np.ndarray) -> list[Track]:
        if self.model is None:
            return []
        results = self.model.track(frame, imgsz=self.imgsz, persist=True, verbose=False)
        tracks: list[Track] = []
        if not results:
            return tracks
        boxes = results[0].boxes
        if boxes is None or boxes.id is None:
            return tracks
        names = results[0].names
        for box_xyxy, box_id, box_cls in zip(boxes.xyxy.tolist(), boxes.id.tolist(), boxes.cls.tolist()):
            tracks.append(Track(id=int(box_id), cls=names[int(box_cls)], xyxy=tuple(box_xyxy)))
        return tracks


# --------------------------------------------------------------------------
# Validator: tiered checks, cheap ones every frame, detector checks every
# DETECT_STRIDE frames. Mirrors the pipeline in
# datasets/anti_artifact_taxonomy.json "validator_pipeline".
# --------------------------------------------------------------------------

class AntiArtifactValidator:
    def __init__(self, args: argparse.Namespace):
        self.args = args
        self.expected_counts = parse_expected_counts(args.expected) if args.expected else {}
        self.detector = Detector(args.model, args.imgsz) if args.model else None

        self.events: list[dict] = []
        self.hash_history: list[int] = []
        self.frozen_run = 0
        self.freeze_start: Optional[int] = None
        self.prev_gray: Optional[np.ndarray] = None
        self.prev_states: dict[int, dict] = {}
        self.prev_counts: dict[str, int] = {}

    def emit(self, event: str, frame: int, fps: float, severity: int, evidence: dict):
        self.events.append(
            {
                "event": event,
                "frame": frame,
                "time_s": round(frame / fps, 3) if fps else None,
                "severity": severity,
                "evidence": evidence,
            }
        )

    # ---- cheap, every-frame checks -------------------------------------
    def temporal_checks(self, frame_idx: int, gray: np.ndarray, fps: float):
        frame_hash = dhash64(gray)

        # E04 frozen frame: run of (near-)identical consecutive hashes.
        if self.prev_gray is not None and hamming64(frame_hash, self.hash_history[-1]) <= self.args.freeze_hamming:
            if self.frozen_run == 0:
                self.freeze_start = frame_idx - 1
            self.frozen_run += 1
        else:
            if self.frozen_run > self.args.freeze_min_run:
                self.emit(
                    "E04_FREEZE_RUN",
                    frame_idx,
                    fps,
                    EVENT_SEVERITY["E04_FREEZE_RUN"],
                    {"frame_range": [self.freeze_start, frame_idx - 1], "run_len": self.frozen_run},
                )
            self.frozen_run = 0

        # E03/E05/E06: compare against non-adjacent history for near-dupes,
        # exact resets, and periodic loops.
        for lag in self.args.loop_lags:
            if len(self.hash_history) >= lag:
                dist = hamming64(frame_hash, self.hash_history[-lag])
                if dist == 0:
                    self.emit(
                        "E05_FRAME_RECREATION_RESET",
                        frame_idx,
                        fps,
                        EVENT_SEVERITY["E05_FRAME_RECREATION_RESET"],
                        {"matches_frame": frame_idx - lag, "lag": lag},
                    )
                elif dist <= self.args.near_dup_hamming:
                    self.emit(
                        "E03_NEAR_DUPLICATE_NONLOCAL",
                        frame_idx,
                        fps,
                        EVENT_SEVERITY["E03_NEAR_DUPLICATE_NONLOCAL"],
                        {"matches_frame": frame_idx - lag, "lag": lag, "hamming": dist},
                    )

        if self.prev_gray is not None:
            sim_diff = mean_abs_diff(gray, self.prev_gray)
            if sim_diff < self.args.flicker_floor:
                pass  # near-static, handled by freeze check above
            elif self._is_periodic(frame_idx):
                self.emit(
                    "E06_SEQUENCE_LOOP",
                    frame_idx,
                    fps,
                    EVENT_SEVERITY["E06_SEQUENCE_LOOP"],
                    {"period_frames": self.args.loop_period_hint},
                )

        self.hash_history.append(frame_hash)
        self.prev_gray = gray

    def _is_periodic(self, frame_idx: int) -> bool:
        period = self.args.loop_period_hint
        if period <= 0 or len(self.hash_history) < period * 2:
            return False
        recent = self.hash_history[-period:]
        earlier = self.hash_history[-2 * period : -period]
        dists = [hamming64(a, b) for a, b in zip(recent, earlier)]
        return (sum(dists) / len(dists)) <= self.args.near_dup_hamming

    # ---- detector-dependent checks, every DETECT_STRIDE frames ---------
    def detection_checks(self, frame_idx: int, frame: np.ndarray, fps: float):
        if self.detector is None:
            return
        h, w = frame.shape[:2]
        tracks = self.detector.track(frame)

        counts: dict[str, int] = {}
        for t in tracks:
            counts[t.cls] = counts.get(t.cls, 0) + 1

        if self.expected_counts:
            for cls, expected_n in self.expected_counts.items():
                seen_n = counts.get(cls, 0)
                if seen_n != expected_n:
                    self.emit(
                        "A_COUNT_MISMATCH",
                        frame_idx,
                        fps,
                        EVENT_SEVERITY["A_COUNT_MISMATCH"],
                        {"class": cls, "expected": expected_n, "observed": seen_n},
                    )
        elif self.prev_counts:
            for cls, seen_n in counts.items():
                prev_n = self.prev_counts.get(cls, seen_n)
                if seen_n != prev_n:
                    self.emit(
                        "A_COUNT_CHANGE",
                        frame_idx,
                        fps,
                        EVENT_SEVERITY["A_COUNT_CHANGE"],
                        {"class": cls, "previous": prev_n, "observed": seen_n},
                    )
        self.prev_counts = counts

        for t in tracks:
            if t.lost:
                self.emit(
                    "E01_IDENTITY_SWAP",
                    frame_idx,
                    fps,
                    EVENT_SEVERITY["E01_IDENTITY_SWAP"],
                    {"track_id": t.id, "class": t.cls},
                )
                continue

            state = box_state(t.xyxy, w, h)
            prev = self.prev_states.get(t.id)
            if prev is not None:
                area_ratio = state["area"] / max(1e-6, prev["area"])
                if area_ratio > self.args.size_drift_ratio or area_ratio < 1 / self.args.size_drift_ratio:
                    self.emit(
                        "B03_SIZE_DRIFT_CANDIDATE",
                        frame_idx,
                        fps,
                        EVENT_SEVERITY["B03_SIZE_DRIFT_CANDIDATE"],
                        {"track_id": t.id, "class": t.cls, "area_ratio": round(area_ratio, 3)},
                    )

                aspect_ratio = state["aspect"] / max(1e-6, prev["aspect"])
                if aspect_ratio > self.args.aspect_drift_ratio or aspect_ratio < 1 / self.args.aspect_drift_ratio:
                    self.emit(
                        "B04_ASPECT_RATIO_DRIFT_CANDIDATE",
                        frame_idx,
                        fps,
                        EVENT_SEVERITY["B04_ASPECT_RATIO_DRIFT_CANDIDATE"],
                        {"track_id": t.id, "class": t.cls, "aspect_ratio": round(aspect_ratio, 3)},
                    )

                center_shift = ((state["cx"] - prev["cx"]) ** 2 + (state["cy"] - prev["cy"]) ** 2) ** 0.5
                if center_shift > self.args.teleport_shift:
                    self.emit(
                        "C01_TELEPORT_CANDIDATE",
                        frame_idx,
                        fps,
                        EVENT_SEVERITY["C01_TELEPORT_CANDIDATE"],
                        {"track_id": t.id, "class": t.cls, "center_shift": round(center_shift, 3)},
                    )
            self.prev_states[t.id] = state

    # ---- top-level driver -------------------------------------------------
    def run(self, video_path: str, output_path: Optional[str] = None) -> list[dict]:
        try:
            import cv2  # type: ignore
        except ImportError as exc:  # pragma: no cover - optional dep
            raise ImportError("run() needs `pip install opencv-python` to read video files") from exc

        cap = cv2.VideoCapture(video_path)
        if not cap.isOpened():
            raise FileNotFoundError(f"Could not open video: {video_path}")
        fps = cap.get(cv2.CAP_PROP_FPS) or 30.0

        frame_idx = 0
        while True:
            ok, frame = cap.read()
            if not ok:
                break
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            self.temporal_checks(frame_idx, gray, fps)
            if frame_idx % self.args.detect_stride == 0:
                self.detection_checks(frame_idx, frame, fps)
            frame_idx += 1
        cap.release()

        if output_path:
            with open(output_path, "w") as fh:
                for event in self.events:
                    fh.write(json.dumps(event) + "\n")
        return self.events


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--video", required=True, help="Path to the video file to validate")
    parser.add_argument("--out", default=None, help="Write flagged events as JSONL to this path")
    parser.add_argument("--model", default=None, help="Ultralytics-compatible weights path (e.g. yolo11n.pt); omit to skip detector checks")
    parser.add_argument("--imgsz", type=int, default=640)
    parser.add_argument("--expected", default=None, help='Expected object counts, e.g. "person:1,knife:1"')
    parser.add_argument("--detect-stride", type=int, default=5, dest="detect_stride", help="Run detector every N frames")
    parser.add_argument("--freeze-hamming", type=int, default=2, help="Max hash distance to count as an identical/frozen frame")
    parser.add_argument("--freeze-min-run", type=int, default=1, help="Frozen runs longer than this many frames get flagged")
    parser.add_argument("--near-dup-hamming", type=int, default=4, help="Max hash distance to count as a near-duplicate frame")
    parser.add_argument("--loop-lags", type=int, nargs="+", default=[30, 60, 90], help="Frame lags to check for recreated/reset frames")
    parser.add_argument("--loop-period-hint", type=int, default=24, help="Suspected loop period (frames) for periodicity check")
    parser.add_argument("--flicker-floor", type=float, default=0.5, help="Below this mean abs diff, treat as static rather than flicker")
    parser.add_argument("--size-drift-ratio", type=float, default=1.5, help="Frame-to-frame bbox area ratio that triggers B03")
    parser.add_argument("--aspect-drift-ratio", type=float, default=1.5, help="Frame-to-frame bbox aspect ratio change that triggers B04")
    parser.add_argument("--teleport-shift", type=float, default=0.25, help="Normalized center-shift per frame that triggers C01")
    return parser


def main(argv: Optional[Iterable[str]] = None) -> int:
    args = build_parser().parse_args(argv)
    validator = AntiArtifactValidator(args)
    events = validator.run(args.video, args.out)
    for event in events:
        print(json.dumps(event))
    print(f"# {len(events)} events flagged", file=sys.stderr)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
