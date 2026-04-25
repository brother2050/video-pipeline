#!/usr/bin/env python3
"""一键安装脚本"""

import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent


def run(cmd: list[str], cwd: Path | None = None) -> int:
    print(f"  $ {' '.join(cmd)}")
    result = subprocess.run(cmd, cwd=cwd or ROOT)
    return result.returncode


def main() -> None:
    print("=" * 50)
    print("  VideoPipeline 安装")
    print("=" * 50)

    # 1. 环境检查
    print("\n[1/6] 环境检查...")
    rc = run([sys.executable, str(ROOT / "scripts" / "check_env.py")])
    if rc != 0:
        print("环境检查失败，请修复后重试")
        sys.exit(1)

    # 2. 创建虚拟环境
    print("\n[2/6] 创建 Python 虚拟环境...")
    venv_path = ROOT / "backend" / ".venv"
    if not venv_path.exists():
        run([sys.executable, "-m", "venv", str(venv_path)])
    else:
        print("  虚拟环境已存在，跳过")

    # 获取 venv python 路径
    if sys.platform == "win32":
        venv_python = venv_path / "Scripts" / "python.exe"
    else:
        venv_python = venv_path / "bin" / "python"

    # 3. 安装 Python 依赖
    print("\n[3/6] 安装 Python 依赖...")
    run([str(venv_python), "-m", "pip", "install", "--upgrade", "pip"])
    run([str(venv_python), "-m", "noglob", "pip", "install", "-r", str(ROOT / "backend" / "requirements.txt")])

    # 4. 初始化数据库
    print("\n[4/6] 初始化数据库...")
    db_dir = ROOT / "backend" / "data" / "db"
    db_dir.mkdir(parents=True, exist_ok=True)
    projects_dir = ROOT / "backend" / "data" / "projects"
    projects_dir.mkdir(parents=True, exist_ok=True)
    alembic_dir = ROOT / "backend" / "alembic"
    if alembic_dir.exists():
        run([str(venv_python), "-m", "alembic", "upgrade", "head"], cwd=ROOT / "backend")

    # 5. 安装前端依赖
    print("\n[5/6] 安装前端依赖...")
    frontend_dir = ROOT / "frontend"
    if (frontend_dir / "package.json").exists():
        run(["npm", "install"], cwd=frontend_dir)
    else:
        print("  frontend/package.json 不存在，跳过")

    # 6. 完成
    print("\n[6/6] 安装完成!")
    print("=" * 50)
    print("  运行 python scripts/start.py 启动服务")
    print("=" * 50)


if __name__ == "__main__":
    main()
