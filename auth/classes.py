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
        keys = Key.query.order_by(Key.id.desc()).limit(3).all()

        key_id = random.choice(keys).id

        secret_key_file = Path(__file__).parent / 'keys' / 'private' / str(key_id)
        secret_key = open(secret_key_file).read()

        now = datetime.utcnow()

        access_token = jwt.encode({
            'exp': now + timedelta(minutes=15),
            'user_id': user_id,
            'key_id': key_id,
            }, 
            secret_key, 
            algorithm=cls.ALGORITHM
        ).decode('utf-8')
        
        refresh_token = jwt.encode({
            'exp': now + timedelta(days=30),
            'user_id': user_id,
            'key_id': key_id,
            }, 
            secret_key, 
            algorithm=cls.ALGORITHM
        ).decode('utf-8')

        return {
            'access_token': access_token,
            'refresh_token': refresh_token
        }
