import os


class Config(object):
    SECRET_KEY = os.environ['SECRET_KEY']
    CSRF_ENABLED = True
    DEBUG = False #os.environ['DEBUG']
    DB_NAME = os.environ['DB_NAME']
    DB_USER = os.environ['DB_USER']
    DB_PASS = os.environ['DB_PASS']
    DB_SERVICE = os.environ['DB_SERVICE']
    DB_PORT = os.environ['DB_PORT']
    SQLALCHEMY_DATABASE_URI = 'sqlite:///test.db'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    GMAPS_KEY = 'AIzaSyD_UlRxu4BsQMT6M6PXu51-BqnFWvLGKjI'

