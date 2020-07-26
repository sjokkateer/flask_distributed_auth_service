from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import rsa
from pathlib import Path


path_to_keys = Path(__file__).parent / 'keys'
path_to_private_keys = path_to_keys / 'private'
path_to_public_keys = path_to_keys / 'public'


def create_key() -> int:
    from app import db
    from models import Key
    
    key = Key()
    db.session.add(key)
    db.session.commit()
    
    return key.id

# Insert anything into DB which will return an id and w/e timestamp such that we can use
# the id for the file name of the private and public keys
key_id = create_key()

# Gen private key
private_key = rsa.generate_private_key(
    public_exponent=65537,
    key_size=4096,
    backend=default_backend()
)

# Convert to bytes
pem = private_key.private_bytes(
    encoding=serialization.Encoding.PEM,
    format=serialization.PrivateFormat.PKCS8,
    encryption_algorithm=serialization.NoEncryption()
)

# Write private key to file
with open(path_to_private_keys / str(key_id), 'wb') as f:
    f.write(pem)

# Same for public key
public_key = private_key.public_key()

pem = public_key.public_bytes(
    encoding=serialization.Encoding.PEM,
    format=serialization.PublicFormat.SubjectPublicKeyInfo
)

with open(path_to_public_keys / str(key_id), 'wb') as f:
    f.write(pem)
