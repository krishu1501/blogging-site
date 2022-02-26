import os

class Auth:
    CLIENT_ID = os.environ.get('CLIENT_ID')
    CLIENT_SECRET = os.environ.get('CLIENT_SECRET')
    REDIRECT_URI = os.environ.get('REDIRECT_URI')
    SCOPE = ['https://www.googleapis.com/auth/userinfo.profile','https://www.googleapis.com/auth/userinfo.email']
    AUTH_URI = 'https://accounts.google.com/o/oauth2/auth'
    TOKEN_URI = 'https://oauth2.googleapis.com/token'
    USER_INFO = 'https://www.googleapis.com/userinfo/v2/me'

class Config:
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SECRET_KEY = 'a33513838c99d7653d18890b97824e81'
    MAIL_SERVER = 'smtp.googlemail.com'
    MAIL_PORT = 587
    MAIL_USE_TLS = True
    MAIL_USERNAME = os.environ.get('FLASKBLOG_EMAIL_USER')
    MAIL_PASSWORD = os.environ.get('FLASKBLOG_EMAIL_PASS')

class DevConfig(Config):
    SQLALCHEMY_DATABASE_URI = 'sqlite:///site.db'

class ProdConfig(Config):
    try:
        username = os.environ['RDS_USERNAME']
        password = os.environ['RDS_PASSWORD']
        host = os.environ['RDS_HOSTNAME']
        port = os.environ['RDS_PORT']
        database = os.environ['RDS_DB_NAME']
        SQLALCHEMY_DATABASE_URI = f'mysql+pymysql://{username}:{password}@{host}:{port}/{database}'
    except:
        print('Exception handled in ProdConfig. Prod variables not defined!')

config_for = {
    "dev":DevConfig,
    "prod":ProdConfig
}