#!/usr/bin/env python3
"""启动后端"""

import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent


def kill_port(port: int) -> None:
    """清理占用指定端口的进程"""
    try:
        subprocess.run(
            f"lsof -ti:{port} | xargs kill -9",
            shell=True,
            check=False,
            capture_output=True,
        )
    except Exception:
        pass


def main() -> None:
    kill_port(8000)
    
    venv_path = ROOT / "backend" / ".venv"
    if sys.platform == "win32":
        python = venv_path / "Scripts" / "python.exe"
    else:
        python = venv_path / "bin" / "python"

    if not python.exists():
        python = sys.executable

    subprocess.run(
        [
            str(python), "-m", "uvicorn",
            "app.main:app",
            "--host", "0.0.0.0",
            "--port", "8000",
            "--reload",
        ],
        cwd=ROOT / "backend",
    )


if __name__ == "__main__":
    main()