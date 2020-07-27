from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import rsa
from datetime import datetime, timedelta
from enum import Enum
from pathlib import Path

import jwt
import random


class Token(Enum):
    ACCESS = 0
    REFRESH = 1


# Should facilitate a way for us to upload new private and public key pairs
# Could do that with a shell script, even though this would ofcourse not work for windows
class JWT:
    ALGORITHM = 'RS256'

    @classmethod
    def create_tokens(cls, user_id):
        key_id = cls.get_random_key_id()
        private_key = cls.get_private_key(key_id)

        now = datetime.utcnow()
        payload = {
            'user_id': user_id,
            'key_id': key_id
        }
        access_token = cls.create_token(Token.ACCESS, now, payload, private_key)
        refresh_token = cls.create_token(Token.REFRESH, now, payload, private_key)

        return {
            'access_token': access_token,
            'refresh_token': refresh_token
        }

    @classmethod
    def get_random_key_id(cls):
        from models import Key

        keys = Key.get_n_most_recent_keys(3) # Number of rotation keys could be set dynamically through env
        return random.choice(keys).id

    @classmethod
    def get_private_key(cls, id):
        private_key_file = KeyFolder.get_private_key_folder() / str(id)
        return open(private_key_file).read()

    @classmethod
    def create_token(cls, token_type, current_time, payload, private_key):
        ttl = cls.get_ttl(token_type)

        payload['exp'] = current_time + ttl

        return jwt.encode(payload, private_key, algorithm=cls.ALGORITHM).decode('utf-8')

    @classmethod
    def get_ttl(cls, token_type):
        if token_type == Token.ACCESS:
            ttl = timedelta(minutes=15)
        elif token_type == Token.REFRESH:
            ttl = timedelta(days=30)
        else:
            raise TypeError(f'{token_type!r} is not a valid token type!')

        return ttl

    @classmethod
    def create_token_from_existing_payload(cls, token_type, payload):
        key_id = cls.get_random_key_id()
        private_key = cls.get_private_key(key_id)

        now = datetime.now()
        
        return cls.create_token(token_type, now, payload, private_key)

    @classmethod
    def decode(cls, refresh_token):
        payload = jwt.decode(refresh_token, verify=False)

        key_id = payload['key_id']
        public_key = open(KeyFolder.get_public_key_folder() / str(key_id)).read()

        return jwt.decode(refresh_token, public_key, algorithms=cls.ALGORITHM)


class KeyFolder:
    # Could be dynamically set if required
    KEY_FOLDER = 'keys'
    PRIVATE_KEY_FOLDER = 'private'
    PUBLIC_KEY_FOLDER = 'public'

    # All the create_if_not_exists would prefferably
    # be called once when the server is set up of course.
    # Otherwise (as it is right now) these additional calls
    # will be made on each login call and when the key generation
    # script is run 
    @classmethod
    def get_key_folder(cls):
        key_folder = Path(__file__).parent / cls.KEY_FOLDER
        cls.create_if_not_exists(key_folder)
        
        return key_folder

    @classmethod
    def create_if_not_exists(cls, dir):
        if not dir.exists():
            dir.mkdir()

    @classmethod
    def get_private_key_folder(cls):
        return cls.create_and_get_key_folder(cls.PRIVATE_KEY_FOLDER)

    @classmethod
    def create_and_get_key_folder(cls, folder):
        path_to_key_folder = cls.get_key_folder() / folder
        cls.create_if_not_exists(path_to_key_folder)

        return path_to_key_folder

    @classmethod
    def get_public_key_folder(cls):
        return cls.create_and_get_key_folder(cls.PUBLIC_KEY_FOLDER)


class KeyGenerator:
    @staticmethod
    def generate_key_pair():
        key_id = KeyGenerator.generate_key_id()
        private_key = KeyGenerator.generate_private_key(key_id)
        KeyGenerator.generate_public_key(private_key, key_id)

    @staticmethod
    def generate_key_id() -> int:
        from app import db
        from models import Key
        
        key = Key()
        db.session.add(key)
        db.session.commit()
        
        return key.id

    @staticmethod
    def generate_private_key(key_id):
        private_key = rsa.generate_private_key(
            public_exponent=65537,
            key_size=4096,
            backend=default_backend()
        )

        pem = private_key.private_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PrivateFormat.PKCS8,
            encryption_algorithm=serialization.NoEncryption()
        )

        KeyGenerator.write_key_to_file(KeyFolder.get_private_key_folder() / str(key_id), pem)

        return private_key

    @staticmethod
    def write_key_to_file(file_name, pem):
        with open(file_name, 'wb') as f:
            f.write(pem)

    @staticmethod
    def generate_public_key(private_key, key_id):
        public_key = private_key.public_key()

        pem = public_key.public_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PublicFormat.SubjectPublicKeyInfo
        )

        KeyGenerator.write_key_to_file(KeyFolder.get_public_key_folder() / str(key_id), pem)

