import jwt
import random
from datetime import datetime, timedelta
from pathlib import Path

# Should facilitate a way for us to upload new private and public key pairs
# Could do that with a shell script, even though this would ofcourse not work for windows
class JWT:
    ALGORITHM = 'RS256'

    @classmethod
    def create_tokens(cls, user_id):
        from models import Key

        keys = Key.get_n_most_recent_keys(3) # Number of rotation keys could be set dynamically through env
        key_id = random.choice(keys).id

        private_key_file = KeyFolder.get_private_key_folder() / str(key_id)
        private_key = open(private_key_file).read()

        now = datetime.utcnow()

        access_token = jwt.encode({
            'exp': now + timedelta(minutes=15),
            'user_id': user_id,
            'key_id': key_id,
            }, 
            private_key, 
            algorithm=cls.ALGORITHM
        ).decode('utf-8')
        
        refresh_token = jwt.encode({
            'exp': now + timedelta(days=30),
            'user_id': user_id,
            'key_id': key_id,
            }, 
            private_key, 
            algorithm=cls.ALGORITHM
        ).decode('utf-8')

        return {
            'access_token': access_token,
            'refresh_token': refresh_token
        }


class KeyFolder:
    # Could be dynamically set if required
    KEY_FOLDER = 'keys'
    PRIVATE_KEY_FOLDER = 'private'
    PUBLIC_KEY_FOLDER = 'public'

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

