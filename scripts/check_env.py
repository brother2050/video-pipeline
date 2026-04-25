#!/usr/bin/env python3
"""环境检查脚本"""

import shutil
import socket
import subprocess
import sys
from pathlib import Path


def check_python() -> bool:
    v = sys.version_info
    ok = v.major == 3 and v.minor >= 11
    print(f"  {'✓' if ok else '✗'} Python {v.major}.{v.minor}.{v.micro} (需要 >= 3.11)")
    return ok


def check_node() -> bool:
    try:
        result = subprocess.run(["node", "--version"], capture_output=True, text=True, timeout=5)
        version = result.stdout.strip()
        major = int(version.lstrip("v").split(".")[0])
        ok = major >= 18
        print(f"  {'✓' if ok else '✗'} Node.js {version} (需要 >= 18)")
        return ok
    except (FileNotFoundError, subprocess.TimeoutExpired, ValueError):
        print("  ✗ Node.js 未安装")
        return False


def check_ffmpeg() -> bool:
    ok = shutil.which("ffmpeg") is not None
    print(f"  {'✓' if ok else '✗'} FFmpeg {'已安装' if ok else '未安装'}")
    return ok


def check_disk() -> bool:
    try:
        import shutil as sh
        usage = sh.disk_usage(".")
        free_gb = usage.free / (1024 ** 3)
        ok = free_gb >= 10
        print(f"  {'✓' if ok else '✗'} 磁盘剩余 {free_gb:.1f} GB (需要 >= 10 GB)")
        return ok
    except Exception:
        print("  ! 无法检查磁盘空间")
        return True


def check_port(port: int) -> bool:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        in_use = s.connect_ex(("127.0.0.1", port)) == 0
    ok = not in_use
    print(f"  {'✓' if ok else '✗'} 端口 {port} {'空闲' if ok else '被占用'}")
    return ok


def main() -> None:
    print("=" * 50)
    print("  VideoPipeline 环境检查")
    print("=" * 50)

    results = [
        check_python(),
        check_node(),
        check_ffmpeg(),
        check_disk(),
        check_port(8000),
        check_port(5173),
    ]

    print("=" * 50)
    if all(results):
        print("  ✓ 所有检查通过，可以安装")
    else:
        print("  ✗ 部分检查未通过，请修复后重试")
    print("=" * 50)

    sys.exit(0 if all(results) else 1)


if __name__ == "__main__":
    main()
