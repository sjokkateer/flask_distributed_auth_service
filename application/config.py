import os

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'beep-boop-you-will-never-get-this'
    SESSION_TYPE = 'filesystem'
