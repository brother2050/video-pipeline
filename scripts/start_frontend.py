#!/usr/bin/env python3
"""启动前端"""

import subprocess
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
    kill_port(5173)
    
    subprocess.run(
        ["npm", "run", "dev"],
        cwd=ROOT / "frontend",
    )


if __name__ == "__main__":
    main()