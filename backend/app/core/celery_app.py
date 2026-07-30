from celery import Celery

from app.core.config import settings

celery_app = Celery(
    "worker",
    broker=f"{settings.REDIS_URL}/0",
    backend=f"{settings.REDIS_URL}/0",
    include=["app.worker"],
)

# celery_app.conf.task_routes = {
#     "app.worker.send_welcome_email": "main-queue",
#     "app.worker.send_login_email": "main-queue",
#     "app.worker.send_task_assigned_email": "main-queue",
# }
