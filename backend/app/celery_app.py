"""
Celery 应用配置。
"""

import os
from celery import Celery

from app.config import settings


celery_app = Celery(
    "videopipeline",
    broker=settings.celery_broker_url,
    backend=settings.celery_result_backend,
    include=[
        "app.tasks.pipeline_tasks",
        "app.tasks.compliance_tasks",
        "app.tasks.continuity_tasks",
    ],
)

celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="Asia/Shanghai",
    enable_utc=True,
    task_track_started=True,
    task_time_limit=3600,  # 1小时
    task_soft_time_limit=3000,  # 50分钟
    worker_prefetch_multiplier=1,
    worker_max_tasks_per_child=100,
    task_acks_late=True,
    task_reject_on_worker_lost=True,
    task_default_queue="default",
    task_queues={
        "default": {
            "exchange": "default",
            "routing_key": "default",
        },
        "pipeline": {
            "exchange": "pipeline",
            "routing_key": "pipeline",
        },
        "compliance": {
            "exchange": "compliance",
            "routing_key": "compliance",
        },
        "continuity": {
            "exchange": "continuity",
            "routing_key": "continuity",
        },
    },
    task_default_exchange="default",
    task_default_routing_key="default",
    task_default_delivery_mode="persistent",
)