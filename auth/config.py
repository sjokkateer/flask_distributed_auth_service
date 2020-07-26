import os


class Config:
    SECRET_KEY = 'blabla-refactor-later-to-private-key'
    SQLALCHEMY_DATABASE_URI = f"{os.getenv('DB_VENDOR')}://{os.getenv('DB_USER')}:{os.getenv('DB_PASSWORD')}@{os.getenv('DB_HOST')}:{os.getenv('DB_PORT')}/{os.getenv('DB_NAME')}"
    SQLALCHEMY_TRACK_MODIFICATIONS = False
