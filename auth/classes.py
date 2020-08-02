from abc import ABC, abstractmethod
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import rsa
from datetime import datetime, timedelta
from enum import Enum
from models import Key
from pathlib import Path

import jwt
import random


class Token(Enum):
    ACCESS = 0
    REFRESH = 1


# Should be refactored into two pieces, one a refresh token
# and one an access token class where refresh token is the base class
# since it requires similar functionality but less extensive than
# the access token
class JWT:
    ALGORITHM = 'RS256'
    NUMBER_OF_RANDOM_KEYS = 3
    
    @classmethod
    def create_tokens(cls, user_id):
        key_id = Key.get_random_key_out_of_n(cls.NUMBER_OF_RANDOM_KEYS).id
        private_key = cls.get_private_key(key_id)

        now = datetime.utcnow()
        payload = {
            'user_id': user_id,
            'key_id': key_id
        }
        access_token = cls.create_token(Token.ACCESS, now, payload, private_key)

        # Similarly get a key id from the recent refresh token key ids
        key_id = Key.get_random_key_out_of_n(cls.NUMBER_OF_RANDOM_KEYS, is_refresh_token_key=True).id
        payload['key_id'] = key_id
        private_key = cls.get_private_key(key_id)
        refresh_token = cls.create_token(Token.REFRESH, now, payload, private_key)

        return {
            'access_token': access_token,
            'refresh_token': refresh_token
        }

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
            raise InvalidTokenTypeException(f'{token_type!r} is not a valid token type!')

        return ttl

    @classmethod
    def create_token_from_existing_payload(cls, token_type, payload):
        key_id = Key.get_random_key_out_of_n(cls.NUMBER_OF_RANDOM_KEYS).id
        payload['key_id'] = key_id
        private_key = cls.get_private_key(key_id)

        now = datetime.now()
        
        return cls.create_token(token_type, now, payload, private_key)

    @classmethod
    def decode(cls, token):
        # Could result in a decode error when something random was given as token
        payload = jwt.decode(token, verify=False)

        # Key_id could not be present in case token was decoded but for ex was made
        # by something else then our server
        key_id = payload['key_id']
        public_key = open(KeyFolder.get_public_key_folder() / str(key_id)).read()

        return jwt.decode(token, public_key, algorithms=cls.ALGORITHM)


class InvalidTokenTypeException(Exception):
    pass


class NoTokenException(Exception):
    pass


class TokenExtractor:
    @staticmethod
    def extract(request):
        auth_header = request.headers
        bearer_token = auth_header.get('Authorization')

        if not bearer_token: raise NoTokenException('No token provided!')

        return bearer_token.split()[-1]


class KeyFolder:
    '''
    Class is responsible for returning the paths to the key folders.
    '''
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
    def get_key_folder(cls) -> Path:
        key_folder = Path(__file__).parent / cls.KEY_FOLDER
        cls.create_if_not_exists(key_folder)
        
        return key_folder

    @classmethod
    def create_if_not_exists(cls, dir):
        if not dir.exists():
            dir.mkdir()

    @classmethod
    def get_private_key_folder(cls) -> Path:
        return cls.create_and_get_key_folder(cls.PRIVATE_KEY_FOLDER)

    @classmethod
    def create_and_get_key_folder(cls, folder) -> Path:
        path_to_key_folder = cls.get_key_folder() / folder
        cls.create_if_not_exists(path_to_key_folder)

        return path_to_key_folder

    @classmethod
    def get_public_key_folder(cls) -> Path:
        return cls.create_and_get_key_folder(cls.PUBLIC_KEY_FOLDER)


class KeyGenerator:
    '''
    Class is responsible for generating a private and public
    key pair on instantiation (RSA).
    '''
    def __init__(self):
        self.private_key = None
        self.public_key = None

        self.generate_key_pair()

    def generate_key_pair(self):
        self.private_key = self.generate_private_key()
        self.public_key = self.private_key.public_key()

    def generate_private_key(self):
        return rsa.generate_private_key(
            public_exponent=65537,
            key_size=4096,
            backend=default_backend()
        )


class KeyFileWriter:
    '''
    Class is responsible for writing the generated keys to
    their respective folders.
    '''
    def __init__(self, key_generator: KeyGenerator):
        self.key_generator = key_generator
        self.key_file_write_strategy = None

    def write_keys_to_file(self, key_file_name: str):
        self.write_private_key_to_file(key_file_name)
        self.write_public_key_to_file(key_file_name)

    def write_private_key_to_file(self, key_file_name: str):
        self.key_file_write_strategy = PrivateKeyFileWriteStrategy(self.key_generator.private_key)
        self.write_key_to_file(key_file_name)

    def write_key_to_file(self, key_file_name: str):
        with open(self.key_file_write_strategy.get_path_to_key_folder() / key_file_name, 'wb') as f:
            f.write(self.key_file_write_strategy.get_pem())

    def write_public_key_to_file(self, key_file_name: str):
        self.key_file_write_strategy = PublicKeyFileWriteStrategy(self.key_generator.public_key)
        self.write_key_to_file(key_file_name)


class KeyFileWriteStrategy(ABC):
    '''
    Class serves as a base for the key file writing strategy.
    '''
    def __init__(self, key):
        self.key = key

    @abstractmethod
    def get_pem(self):
        pass

    @abstractmethod
    def get_path_to_key_folder(self) -> str:
        pass


class PrivateKeyFileWriteStrategy(KeyFileWriteStrategy):
    '''
    Class is responsible for converting the private key into bytes
    and providing the right private key folder.
    '''
    def __init__(self, key):
        super().__init__(key)

    def get_pem(self):
        return self.key.private_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PrivateFormat.PKCS8,
            encryption_algorithm=serialization.NoEncryption()
        )

    def get_path_to_key_folder(self) -> Path:
        return KeyFolder.get_private_key_folder()


class PublicKeyFileWriteStrategy(KeyFileWriteStrategy):
    '''
    Class is responsible for converting the public key into bytes
    and providing the right public key folder.
    '''
    def __init__(self, key):
        super().__init__(key)

    def get_pem(self):
        return self.key.public_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PublicFormat.SubjectPublicKeyInfo
        )

    def get_path_to_key_folder(self) -> Path:
        return KeyFolder.get_public_key_folder()
