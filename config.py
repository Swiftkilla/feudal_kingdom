import os
basedir = os.path.abspath(os.path.dirname(__file__))
from datetime import timedelta


class Config(object):
    # ...
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or \
        'sqlite:///' + os.path.join(basedir, 'test_mysqlite3.db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    THREADED = True
    ALLOWED_IPS = ['192.168.0.21', '127.0.0.1:5000']
    PERMANENT_SESSION_LIFETIME = timedelta(minutes=5)
