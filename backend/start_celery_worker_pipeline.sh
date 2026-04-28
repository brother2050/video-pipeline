#!/bin/bash
# 启动 Celery Worker - 流水线队列

set -e

cd "$(dirname "$0")"

source .venv/bin/activate

celery -A app.celery_app worker \
    --loglevel=info \
    --queue=pipeline \
    --concurrency=4 \
    --max-tasks-per-child=100 \
    --time-limit=3600 \
    --soft-time-limit=3000