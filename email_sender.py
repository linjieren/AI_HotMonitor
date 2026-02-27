# -*- coding: utf-8 -*-
"""
邮件发送：使用 smtplib 发送日报（HTML 格式）
未配置真实邮箱时，main.py 会改为把日报保存为本地 HTML 文件，便于试运行。
"""

import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.header import Header

# 从配置读取
from config import SMTP_HOST, SMTP_PORT, SMTP_USER, SMTP_PASSWORD, RECEIVER_EMAIL


def send_report(subject, html_body, to_email=None):
    """
    发送日报邮件
    :param subject: 邮件标题，如 【AI前沿日报】2026-02-26
    :param html_body: 邮件正文（HTML 字符串）
    :param to_email: 收件人，不传则用 config.RECEIVER_EMAIL
    :return: True 成功，否则抛出异常
    """
    to_email = to_email or RECEIVER_EMAIL
    msg = MIMEMultipart("alternative")
    msg["Subject"] = Header(subject, "utf-8")
    msg["From"] = Header(SMTP_USER, "utf-8")
    msg["To"] = to_email

    part = MIMEText(html_body, "html", "utf-8")
    msg.attach(part)

    with smtplib.SMTP_SSL(SMTP_HOST, SMTP_PORT) as server:
        server.login(SMTP_USER, SMTP_PASSWORD)
        server.sendmail(SMTP_USER, [to_email], msg.as_string())
    return True
