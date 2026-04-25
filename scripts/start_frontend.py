#!/usr/bin/env python3
"""启动前端"""

import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent


def main() -> None:
    subprocess.run(
        ["npm", "run", "dev"],
        cwd=ROOT / "frontend",
    )


if __name__ == "__main__":
    main()
