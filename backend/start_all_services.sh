#!/bin/bash
# 一键启动所有服务：FastAPI + Celery Workers + Redis

set -e

cd "$(dirname "$0")"

echo "========================================="
echo "VideoPipeline 服务启动脚本"
echo "========================================="
echo ""

# 检查 Redis
echo "1. 检查 Redis 服务..."
if ! redis-cli ping > /dev/null 2>&1; then
    echo "   Redis 未运行，正在启动..."
    if command -v brew > /dev/null; then
        brew services start redis
    elif command -v systemctl > /dev/null; then
        sudo systemctl start redis
    else
        echo "   请手动启动 Redis：redis-server"
        exit 1
    fi
    sleep 2
    echo "   ✓ Redis 已启动"
else
    echo "   ✓ Redis 已运行"
fi

# 激活虚拟环境
echo ""
echo "2. 激活虚拟环境..."
source .venv/bin/activate
echo "   ✓ 虚拟环境已激活"

# 启动 Celery Workers
echo ""
echo "3. 启动 Celery Workers..."

# 启动流水线队列 Worker
echo "   - 启动流水线队列 Worker..."
celery -A app.celery_app worker \
    --loglevel=info \
    --queue=pipeline \
    --concurrency=4 \
    --max-tasks-per-child=100 \
    --time-limit=3600 \
    --soft-time-limit=3000 \
    --hostname=worker-pipeline@%h \
    --pidfile=/tmp/celery-pipeline.pid \
    --logfile=/tmp/celery-pipeline.log &

# 启动合规检查队列 Worker
echo "   - 启动合规检查队列 Worker..."
celery -A app.celery_app worker \
    --loglevel=info \
    --queue=compliance \
    --concurrency=2 \
    --max-tasks-per-child=100 \
    --time-limit=3600 \
    --soft-time-limit=3000 \
    --hostname=worker-compliance@%h \
    --pidfile=/tmp/celery-compliance.pid \
    --logfile=/tmp/celery-compliance.log &

# 启动连续性检查队列 Worker
echo "   - 启动连续性检查队列 Worker..."
celery -A app.celery_app worker \
    --loglevel=info \
    --queue=continuity \
    --concurrency=2 \
    --max-tasks-per-child=100 \
    --time-limit=3600 \
    --soft-time-limit=3000 \
    --hostname=worker-continuity@%h \
    --pidfile=/tmp/celery-continuity.pid \
    --logfile=/tmp/celery-continuity.log &

echo "   ✓ 所有 Celery Workers 已启动"

# 启动 FastAPI 服务器
echo ""
echo "4. 启动 FastAPI 服务器..."
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000 &
FASTAPI_PID=$!

echo ""
echo "========================================="
echo "所有服务已启动！"
echo "========================================="
echo ""
echo "服务地址："
echo "  - FastAPI:     http://localhost:8000"
echo "  - API 文档:    http://localhost:8000/docs"
echo "  - Redis:       redis://localhost:6379"
echo ""
echo "日志文件："
echo "  - Celery Pipeline:    /tmp/celery-pipeline.log"
echo "  - Celery Compliance:   /tmp/celery-compliance.log"
echo "  - Celery Continuity:  /tmp/celery-continuity.log"
echo ""
echo "按 Ctrl+C 停止所有服务"
echo ""

# 等待用户中断
trap "echo ''; echo '正在停止所有服务...'; kill $FASTAPI_PID 2>/dev/null; pkill -f 'celery.*worker'; echo '所有服务已停止'; exit 0" INT TERM

wait