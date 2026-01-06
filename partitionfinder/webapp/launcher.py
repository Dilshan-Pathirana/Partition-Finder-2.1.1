from __future__ import annotations

import argparse
import shutil
import subprocess
import sys
import time
from pathlib import Path


def _repo_root() -> Path:
    # partitionfinder/webapp/launcher.py -> partitionfinder/webapp -> partitionfinder -> repo root
    return Path(__file__).resolve().parents[2]


def _ui_dir() -> Path:
    return _repo_root() / "ui"


def _npm_executable() -> str:
    npm = shutil.which("npm")
    if not npm:
        raise RuntimeError(
            "npm was not found on PATH. Install Node.js (which includes npm) to run the UI dev server."
        )
    return npm


def _ensure_ui_dependencies(ui_dir: Path) -> None:
    node_modules = ui_dir / "node_modules"
    if node_modules.exists():
        return

    npm = _npm_executable()
    print("[webapp] ui/node_modules not found; running npm install...")
    subprocess.run([npm, "install"], cwd=str(ui_dir), check=True)


def _terminate_process(p: subprocess.Popen[object], *, name: str) -> None:
    if p.poll() is not None:
        return
    try:
        p.terminate()
    except Exception:
        return

    # Give it a moment to exit cleanly.
    deadline = time.time() + 5.0
    while time.time() < deadline:
        if p.poll() is not None:
            return
        time.sleep(0.1)

    try:
        p.kill()
    except Exception:
        pass


def main(argv: list[str] | None = None) -> int:
    if argv is None:
        argv = sys.argv[1:]

    ap = argparse.ArgumentParser(
        prog="partitionfinder-webapp",
        description="Start PartitionFinder API + UI together (single command)",
    )
    ap.add_argument("--host", default="127.0.0.1", help="Host/IP to bind both servers (default: 127.0.0.1)")
    ap.add_argument("--api-port", type=int, default=8000, help="API port (default: 8000)")
    ap.add_argument("--ui-port", type=int, default=5173, help="UI port (default: 5173)")
    args = ap.parse_args(argv)

    repo_root = _repo_root()
    ui_dir = _ui_dir()

    if not ui_dir.exists():
        raise SystemExit(f"UI folder not found: {ui_dir}")

    # Ensure deps so a single command works end-to-end.
    try:
        _ensure_ui_dependencies(ui_dir)
    except subprocess.CalledProcessError as e:
        print(f"[webapp] npm install failed (exit={e.returncode}).")
        return int(e.returncode) or 1

    print(f"[webapp] Starting API: http://{args.host}:{args.api_port}")
    api_cmd = [
        sys.executable,
        "-m",
        "uvicorn",
        "partitionfinder.api.service:app",
        "--host",
        str(args.host),
        "--port",
        str(args.api_port),
    ]

    print(f"[webapp] Starting UI : http://{args.host}:{args.ui_port}")
    npm = _npm_executable()
    ui_cmd = [npm, "run", "dev", "--", "--host", str(args.host), "--port", str(args.ui_port)]

    api_proc: subprocess.Popen[object] | None = None
    ui_proc: subprocess.Popen[object] | None = None

    try:
        api_proc = subprocess.Popen(api_cmd, cwd=str(repo_root))
        ui_proc = subprocess.Popen(ui_cmd, cwd=str(ui_dir))

        # If either process exits, stop the other and propagate a non-zero exit.
        while True:
            api_rc = api_proc.poll()
            ui_rc = ui_proc.poll()

            if api_rc is not None:
                print(f"[webapp] API exited (code={api_rc}). Stopping UI...")
                _terminate_process(ui_proc, name="ui")
                return int(api_rc)

            if ui_rc is not None:
                print(f"[webapp] UI exited (code={ui_rc}). Stopping API...")
                _terminate_process(api_proc, name="api")
                return int(ui_rc)

            time.sleep(0.25)

    except KeyboardInterrupt:
        print("\n[webapp] Ctrl+C received; stopping...")
        if ui_proc is not None:
            _terminate_process(ui_proc, name="ui")
        if api_proc is not None:
            _terminate_process(api_proc, name="api")
        return 0
