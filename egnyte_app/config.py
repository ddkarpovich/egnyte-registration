import os


class Config(object):
    DEBUG = True
    SECRET_KEY = os.environ.get('FLASK_SECRET_KEY', '123')
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URI', 'mysql+pymysql://user:password@localhost/dbname')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
