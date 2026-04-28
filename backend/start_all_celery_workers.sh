#!/bin/bash
# 启动所有 Celery Workers

set -e

cd "$(dirname "$0")"

source .venv/bin/activate

echo "========================================="
echo "启动 Celery Workers"
echo "========================================="
echo ""

# 启动流水线队列 Worker
echo "启动流水线队列 Worker..."
celery -A app.celery_app worker \
    --loglevel=info \
    --queue=pipeline \
    --concurrency=4 \
    --max-tasks-per-child=100 \
    --time-limit=3600 \
    --soft-time-limit=3000 \
    --hostname=worker-pipeline@%h &

# 启动合规检查队列 Worker
echo "启动合规检查队列 Worker..."
celery -A app.celery_app worker \
    --loglevel=info \
    --queue=compliance \
    --concurrency=2 \
    --max-tasks-per-child=100 \
    --time-limit=3600 \
    --soft-time-limit=3000 \
    --hostname=worker-compliance@%h &

# 启动连续性检查队列 Worker
echo "启动连续性检查队列 Worker..."
celery -A app.celery_app worker \
    --loglevel=info \
    --queue=continuity \
    --concurrency=2 \
    --max-tasks-per-child=100 \
    --time-limit=3600 \
    --soft-time-limit=3000 \
    --hostname=worker-continuity@%h &

echo ""
echo "========================================="
echo "所有 Celery Workers 已启动"
echo "========================================="
echo ""
echo "按 Ctrl+C 停止所有 Workers"

# 等待所有后台进程
wait