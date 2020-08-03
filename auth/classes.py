from abc import ABC, abstractmethod
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import rsa
from datetime import datetime, timedelta
from models import Key
from pathlib import Path

import jwt


class TokenService:
    selected_token = None

    @classmethod
    def create_tokens(cls, initial_payload):
        '''
        Creates an access token and refresh token with given initial payload.
        '''
        tokens = [
            ('access_token', AccessToken),
            ('refresh_token', RefreshToken),
        ]

        token_response = {}
        for token in tokens:
            token_type = token[1]
            cls.selected_token = token_type
            
            name = token[0]
            token_response[name] = cls.create_token(initial_payload.copy())

        return token_response

    @classmethod
    def create_token(cls, initial_payload):
        return cls.selected_token.create_token(initial_payload)

    @classmethod
    def decode(cls, token):
        return cls.selected_token.decode(token)


class TokenBase(ABC):
    '''
    Base class for the different token types.
    
    Class is responsible for providing a set of functionalities
    shared by the specific token types.
    '''
    ALGORITHM = 'RS256'
    NUMBER_OF_RANDOM_KEYS = 3

    @classmethod
    def create_token(cls, initial_payload):
        payload = cls.create_payload(initial_payload)
        return jwt.encode(payload, KeyFileReader.get_private_key(str(payload['key_id'])), algorithm=cls.ALGORITHM).decode('utf-8')

    @classmethod
    def create_payload(cls, initial_payload: dict) -> dict:
        initial_payload['key_id'] = cls.get_random_key().id
        initial_payload['exp'] += cls.get_time_to_live()
        
        return initial_payload

    @classmethod
    @abstractmethod
    def get_time_to_live(cls) -> timedelta:
        pass

    @classmethod
    @abstractmethod
    def get_random_key(cls) -> Key:
        pass

    @classmethod
    def decode(cls, token):
        # Could result in a decode error when something random was given as token
        payload = jwt.decode(token, verify=False)
        # Key_id could not be present in case token was decoded but for ex was made
        # by something else then our server
        public_key = KeyFileReader.get_public_key(str(payload['key_id']))
        return jwt.decode(token, public_key, algorithms=cls.ALGORITHM)


class AccessToken(TokenBase):
    '''
    Class resembling an access token, is responsible for 
    providing access token specific ttl and key.
    '''
    @classmethod
    def get_time_to_live(cls) -> timedelta:
        return timedelta(minutes=15)

    @classmethod
    def get_random_key(cls) -> Key:
        return Key.get_random_key_out_of_n(cls.NUMBER_OF_RANDOM_KEYS)


class RefreshToken(TokenBase):
    '''
    Class resembling a refresh token, is responsible for 
    providing refresh token specific ttl and key.
    '''
    @classmethod
    def get_time_to_live(cls) -> timedelta:
        return timedelta(days=30)

    @classmethod
    def get_random_key(cls) -> Key:
        return Key.get_random_key_out_of_n(cls.NUMBER_OF_RANDOM_KEYS, is_refresh_token_key=True)


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


class KeyFileReader:
    '''
    Class is responsible for reading the contents from key files.
    '''
    @classmethod
    def get_private_key(cls, key_file_name: str):
        return open(KeyFolder.get_private_key_folder() / key_file_name).read()

    @classmethod
    def get_public_key(cls, key_file_name: str):
        return open(KeyFolder.get_public_key_folder() / key_file_name).read()


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
