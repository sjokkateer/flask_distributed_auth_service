from app import db
from pathlib import Path
from werkzeug.security import generate_password_hash, check_password_hash

import datetime


class User(db.Model):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(254), unique=True, nullable=False)
    password = db.Column(db.String(94))
    joined_at = db.Column(db.DateTime, default=datetime.datetime.now)

    def __init__(self, email, password):
        self.email = email
        self.password = self.hash(password)

    def hash(self, password):
        return generate_password_hash(password)

    def is_valid(self, password):
        return check_password_hash(self.password, password)

    def __repr__(self):
        return f'<User {self.email}>'


class Key(db.Model):
    __tablename__ = 'keys'

    id = db.Column(db.Integer, primary_key=True)

    @classmethod
    def get_n_most_recent_keys(cls, n):
        return cls.query.order_by(cls.id.desc()).limit(n).all()
