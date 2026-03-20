# AGENTS.md

## Cursor Cloud specific instructions

This is a **static content repository** (HTML, CSV, images) with no source code, build system, package manager, test framework, or runtime dependencies.

### Repository contents

- `privacy-policy.html` — Static privacy policy page for Glow Content Co (the only "application" in this repo).
- `pinterest_pins_*.csv`, `pins/`, `pinterest-pins/` — Pinterest pin data in CSV/text formats.
- `pin-images/` — JPG images used as Pinterest pin assets.

### Running the application

Serve the static files with Python's built-in HTTP server:

```sh
python3 -m http.server 8080 --directory /workspace
```

Then open `http://localhost:8080/privacy-policy.html` in a browser.

### Lint / Test / Build

There are no lint, test, or build commands. The repo has no source code or dependencies to install.
