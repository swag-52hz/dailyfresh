from celery import Celery
from django.conf import settings
from django.core.mail import send_mail
# django环境初始化
import os
import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'dailyfresh.settings')
django.setup()

# 创建一个celery类的实例对象
app = Celery('celery_tasks.tasks', broker='redis://127.0.0.1:6379/8')

@app.task
def send_email_task(username, email, token):
    subject = '天天生鲜欢迎信息'
    message = ''
    sender = settings.EMAIL_FROM
    receiver = [email]
    html_message = '<h1>欢迎{0}注册天天生鲜会员</h1>激活账户请点击下方链接:<br/><a href="http://127.0.0.1/user/active/{1}">http://127.0.0.1/user/active/{2}</a>'.format(
        username, token, token)
    send_mail(subject, message, sender, receiver, html_message=html_message)