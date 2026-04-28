#!/usr/bin/env python3
"""
启动 Celery Worker。
"""

import sys
from pathlib import Path

backend_dir = Path(__file__).parent.parent
if str(backend_dir) not in sys.path:
    sys.path.insert(0, str(backend_dir))

from app.celery_app import celery_app

if __name__ == "__main__":
    celery_app.start()