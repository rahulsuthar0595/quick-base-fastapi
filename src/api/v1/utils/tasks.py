from fastapi import BackgroundTasks
from fastapi_mail import FastMail, MessageSchema
from fastapi_mail import ConnectionConfig
from config.config import settings

mail_conf = ConnectionConfig(
    MAIL_USERNAME=settings.MAIL_USERNAME,
    MAIL_PASSWORD=settings.MAIL_PASSWORD,
    MAIL_FROM=settings.MAIL_FROM,
    MAIL_PORT=settings.MAIL_PORT,
    MAIL_SERVER=settings.MAIL_SERVER,
    MAIL_FROM_NAME=settings.MAIL_FROM_NAME,
    MAIL_STARTTLS=True,
    MAIL_SSL_TLS=False,
    USE_CREDENTIALS=True,
    TEMPLATE_FOLDER='templates'
)


def send_account_activation_mail(background_tasks: BackgroundTasks, email: str, data: dict):
    message = MessageSchema(
        subject="User Account Activation",
        recipients=[email],
        template_body=data,
        subtype="html",
    )
    fm = FastMail(mail_conf)
    background_tasks.add_task(fm.send_message, message, template_name="verify_email.html")
