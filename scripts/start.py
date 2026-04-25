#!/usr/bin/env python3
"""同时启动前后端"""

import argparse
import signal
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent


def main() -> None:
    parser = argparse.ArgumentParser(description="启动 VideoPipeline")
    parser.add_argument("--backend-only", action="store_true", help="只启动后端")
    parser.add_argument("--frontend-only", action="store_true", help="只启动前端")
    args = parser.parse_args()

    processes: list[subprocess.Popen] = []

    def shutdown(signum: int, frame: object) -> None:
        print("\n正在关闭...")
        for p in processes:
            p.terminate()
        for p in processes:
            p.wait(timeout=10)
        sys.exit(0)

    signal.signal(signal.SIGINT, shutdown)
    signal.signal(signal.SIGTERM, shutdown)

    if not args.frontend_only:
        print("启动后端...")
        p = subprocess.Popen(
            [sys.executable, str(ROOT / "scripts" / "start_backend.py")],
            cwd=ROOT,
        )
        processes.append(p)

    if not args.backend_only:
        print("启动前端...")
        p = subprocess.Popen(
            [sys.executable, str(ROOT / "scripts" / "start_frontend.py")],
            cwd=ROOT,
        )
        processes.append(p)

    print("\n" + "=" * 50)
    if not args.frontend_only:
        print("  后端: http://localhost:8000")
    if not args.backend_only:
        print("  前端: http://localhost:5173")
    print("  按 Ctrl+C 停止")
    print("=" * 50)

    for p in processes:
        p.wait()


if __name__ == "__main__":
    main()
