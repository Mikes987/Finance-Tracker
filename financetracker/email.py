from flask import current_app, render_template
from flask_mail import Message
from financetracker import mail
from financetracker.models import User

def send_mail(subject, sender, recipients, text_body, html_body):
    msg = Message(subject=subject, sender=sender, recipients=recipients, body=text_body, html=html_body)
    mail.send(msg)

def request_new_password_mail(user: User):
    token = user.request_password_token()
    send_mail(subject='Reset Password Request',
              sender=current_app.config['ADMINS'][0],
              recipients=[user.email],
              text_body=render_template("emails/reset_password.txt", user=user, token=token),
              html_body=render_template("emails/reset_password.html", user=user, token=token))