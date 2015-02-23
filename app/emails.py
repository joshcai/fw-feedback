from decorators import async
from flask import render_template
from flask_mail import Message
from app import mail, app

@async
def send_async_email(app, msg):
  with app.app_context():
    mail.send(msg)

def send_email(subject, recipients, text_body, html_body):
  msg = Message(subject, sender=app.config['SENDER'], recipient=recipients)
  msg.body = text_body
  msg.html = html_body
  send_async_email(app, msg)

def password_reset_email(recipient, url):
  context = { 
      'user': recipient,
      'url': url
  }
  send_email('McDermott Finalist\'s Weekend Feedback - Account Activation',
      [recipient.email],
      render_template('password_reset.txt', **context),
      render_template('password_reset.html', **context))

