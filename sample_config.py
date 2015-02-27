import os
basedir = os.path.abspath(os.path.dirname(__file__))

SQLALCHEMY_DATABASE_URI = 'sqlite:///' + os.path.join(basedir, 'app.db')
SQLALCHEMY_MIGRATE_REPO = os.path.join(basedir, 'db_repository')

WTF_CSRF_ENABLED = True
SECRET_KEY = 'secrethere'

SALT = 'another secret'

GA_ID = 'google analytics id here'

MAIL_SERVER = 'smtpauth.utdallas.edu'
MAIL_PORT = 587
MAIL_USE_TLS = True
MAIL_USERNAME = 'user'
MAIL_PASSWORD = 'pw'
#MAIL_SUPPRESS_SEND=False

SENDER = 'email@domain.com'
