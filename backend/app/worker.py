from asgiref.sync import async_to_sync

from app.core.celery_app import celery_app
from app.utils.mail import send_email


@celery_app.task
def send_welcome_email(email_to: str, full_name: str):
    subject = "Welcome to TaskFlow!"
    content = f"<h1>Welcome {full_name}!</h1><p>Thanks for registering.</p>"

    async_to_sync(send_email)(email_to, subject, content)


@celery_app.task
def send_login_email(user_info: dict[str, str]):
    subject = "Login Alert"
    content: str = (
        f"<p>Hi {user_info['full_name']}, You just logged in to TaskFlow.</p>"
    )
    print("---" * 30)
    print(subject, content, user_info["email"])
    async_to_sync(send_email)(user_info["email"], subject, content)
    print("---" * 30)


@celery_app.task
def send_task_assigned_email(email_to: str, task_title: str, project_name: str):
    subject = f"New Task Assigned: {task_title}"
    content = f"<p>You have been assigned to task <b>{task_title}</b> in project <b>{project_name}</b>.</p>"
    async_to_sync(send_email)(email_to, subject, content)
