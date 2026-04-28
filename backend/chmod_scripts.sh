#!/bin/bash
# 为所有脚本添加执行权限

cd "$(dirname "$0")"

chmod +x start_celery_worker_pipeline.sh
chmod +x start_celery_worker_compliance.sh
chmod +x start_all_celery_workers.sh
chmod +x start_all_services.sh

echo "✓ 所有脚本已添加执行权限"