import os

class Config:
    SECRET_KEY = 'a33513838c99d7653d18890b97824e81'
    MAIL_SERVER = 'smtp.googlemail.com'
    MAIL_PORT = 587
    MAIL_USE_TLS = True
    MAIL_USERNAME = os.environ.get('FLASKBLOG_EMAIL_USER')
    MAIL_PASSWORD = os.environ.get('FLASKBLOG_EMAIL_PASS')

class DevConfig(Config):
    SQLALCHEMY_DATABASE_URI = 'sqlite:///site.db'

class ProdConfig(Config):
    SQLALCHEMY_DATABASE_URI = 'sqlite:///site.db'

config_for = {
    "dev":DevConfig,
    "prod":ProdConfig
}