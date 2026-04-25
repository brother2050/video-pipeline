.PHONY: help install dev build check clean

help:  ## 显示帮助
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | awk 'BEGIN {FS = ":.*?## "}; {printf "  \033[36m%-15s\033[0m %s\n", $$1, $$2}'

install:  ## 一键安装
	python scripts/check_env.py && python scripts/install.py

dev:  ## 启动开发环境（前后端）
	python scripts/start.py

backend:  ## 只启动后端
	python scripts/start_backend.py

frontend:  ## 只启动前端
	python scripts/start_frontend.py

build:  ## 前端构建
	cd frontend && npm run build

check:  ## 代码检查
	@echo "--- Python syntax ---"
	@find backend/app -name "*.py" -not -path "*__pycache__*" -exec python3 -m py_compile {} \; && echo "OK"
	@echo "--- TypeScript ---"
	@cd frontend && npx tsc -b --noEmit && echo "OK"

clean:  ## 清理构建产物
	find . -name "__pycache__" -type d -exec rm -rf {} + 2>/dev/null
	find . -name "*.pyc" -delete 2>/dev/null
	rm -rf frontend/dist frontend/node_modules
	rm -rf backend/.venv backend/data
	rm -rf data/projects/* data/db/*
	@echo "Cleaned"
