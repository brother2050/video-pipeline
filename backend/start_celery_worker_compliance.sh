#!/bin/bash
# 启动 Celery Worker - 合规检查队列

set -e

cd "$(dirname "$0")"

source .venv/bin/activate

celery -A app.celery_app worker \
    --loglevel=info \
    --queue=compliance \
    --concurrency=2 \
    --max-tasks-per-child=100 \
    --time-limit=3600 \
    --soft-time-limit=3000