from __future__ import annotations

import argparse
import shutil
import subprocess
import sys
from pathlib import Path

from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse

from partitionfinder.api import service as api_service


def _repo_root() -> Path:
    # partitionfinder/webapp/prod.py -> partitionfinder/webapp -> partitionfinder -> repo root
    return Path(__file__).resolve().parents[2]


def _ui_dir() -> Path:
    return _repo_root() / "ui"


def _ui_dist_dir() -> Path:
    return _ui_dir() / "dist"


def _npm_executable() -> str:
    npm = shutil.which("npm")
    if not npm:
        raise RuntimeError(
            "npm was not found on PATH. Install Node.js (which includes npm) to build the UI."
        )
    return npm


def _ensure_ui_built(*, dist_dir: Path) -> None:
    # If dist exists, assume the build is present.
    if dist_dir.exists() and (dist_dir / "index.html").exists():
        return

    ui_dir = _ui_dir()
    npm = _npm_executable()

    # Ensure deps.
    node_modules = ui_dir / "node_modules"
    if not node_modules.exists():
        print("[webapp-prod] ui/node_modules not found; running npm install...")
        subprocess.run([npm, "install"], cwd=str(ui_dir), check=True)

    print("[webapp-prod] ui/dist not found; running npm run build...")
    subprocess.run([npm, "run", "build"], cwd=str(ui_dir), check=True)


def create_app(*, dist_dir: Path | None = None) -> FastAPI:
    """Create a single-server app that serves UI + API from one port.

    - API is mounted under /api
    - UI is served from ui/dist
    - SPA routes fall back to index.html
    """

    if dist_dir is None:
        dist_dir = _ui_dist_dir()

    app = FastAPI(title="PartitionFinder Web", version="0.1")

    # Mount the existing API app under /api so the UI can call same-origin /api/*.
    app.mount("/api", api_service.app)

    index_path = dist_dir / "index.html"

    @app.get("/healthz")
    def healthz() -> dict[str, str]:
        return {"status": "ok"}

    @app.get("/")
    def ui_index() -> FileResponse:
        if not index_path.exists():
            raise HTTPException(
                status_code=500,
                detail=(
                    "UI build not found (missing ui/dist/index.html). "
                    "Run: npm install && npm run build (in ui/)"
                ),
            )
        return FileResponse(index_path)

    @app.get("/{path:path}")
    def ui_static_or_spa(path: str) -> FileResponse:
        # /api is handled by the mounted API app.
        # Serve real files if they exist; otherwise return index.html for SPA routes.
        if not index_path.exists():
            raise HTTPException(
                status_code=500,
                detail=(
                    "UI build not found (missing ui/dist/index.html). "
                    "Run: npm install && npm run build (in ui/)"
                ),
            )

        # Guard against path traversal.
        candidate = (dist_dir / path).resolve()
        if not str(candidate).startswith(str(dist_dir.resolve())):
            raise HTTPException(status_code=400, detail="Invalid path")

        if candidate.exists() and candidate.is_file():
            return FileResponse(candidate)

        # SPA fallback
        return FileResponse(index_path)

    return app


# Module-level app for uvicorn import style: `uvicorn partitionfinder.webapp.prod:app`
app = create_app()


def main(argv: list[str] | None = None) -> int:
    if argv is None:
        argv = sys.argv[1:]

    ap = argparse.ArgumentParser(
        prog="partitionfinder-webapp-prod",
        description="Run a single production server that serves UI + API from one port",
    )
    ap.add_argument("--host", default="127.0.0.1")
    ap.add_argument("--port", type=int, default=8000)
    ap.add_argument("--reload", action="store_true", help="Enable uvicorn reload (dev only)")
    ap.add_argument(
        "--no-build",
        action="store_true",
        help="Do not auto-build the UI if ui/dist is missing",
    )
    args = ap.parse_args(argv)

    dist_dir = _ui_dist_dir()

    if not args.no_build:
        try:
            _ensure_ui_built(dist_dir=dist_dir)
        except subprocess.CalledProcessError as e:
            print(f"[webapp-prod] UI build failed (exit={e.returncode}).")
            return int(e.returncode) or 1

    # Recreate app after build so it sees ui/dist.
    combined = create_app(dist_dir=dist_dir)

    import uvicorn

    uvicorn.run(combined, host=str(args.host), port=int(args.port), reload=bool(args.reload))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
