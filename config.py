import os
from dotenv import load_dotenv
from datetime import timedelta

basedir = os.path.abspath(os.path.dirname(__file__))
load_dotenv(os.path.join(basedir, '.env'))


class Config(object):
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'you-will-never-guess'
    # SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or \
    #     'sqlite:///' + os.path.join(basedir, 'app.db')db
    SQLALCHEMY_DATABASE_URI = 'mysql+pymysql://longscave:xiaowu@localhost/longscave'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    LOG_TO_STDOUT = os.environ.get('LOG_TO_STDOUT')
    MAIL_SERVER = os.environ.get('MAIL_SERVER')
    MAIL_PORT = int(os.environ.get('MAIL_PORT') or 25)
    MAIL_USE_TLS = os.environ.get('MAIL_USE_TLS') is not None
    MAIL_USERNAME = os.environ.get('MAIL_USERNAME')
    MAIL_PASSWORD = os.environ.get('MAIL_PASSWORD')
    ADMINS = ['your-email@example.com']
    LANGUAGES = ['en', 'es']
    MS_TRANSLATOR_KEY = os.environ.get('MS_TRANSLATOR_KEY')
    ELASTICSEARCH_URL = os.environ.get('ELASTICSEARCH_URL')
    REDIS_URL = os.environ.get('REDIS_URL') or 'redis://'
    POSTS_PER_PAGE = 25
    ARTICLES_PER_PAGE = 2
    ROWS_PER_PAGE = 5
    # Alipay -- sandbox env
    CANCEL_TIME = 60
    APP_ID_TEST = 2016101800716773
    ALIPAY_PUBLIC_KEY_PATH_TEST = os.path.join(os.getcwd(), 'app/alipay/pem/pem_test', 'alipay_public_key.pem')
    APP_PRIVATE_KEY_PATH_TEST = os.path.join(os.getcwd(), 'app/alipay/pem/pem_test', 'app_private_key.pem')

    # Alipay -- production
    APP_ID_PRD = 2021001139661958
    ALIPAY_PUBLIC_KEY_PATH_PRD = os.path.join(os.getcwd(), 'app/alipay/pem/pem_prd', 'alipay_public_key.pem')
    APP_PRIVATE_KEY_PATH_PRD = os.path.join(os.getcwd(), 'app/alipay/pem/pem_prd', 'app_private_key.pem')

