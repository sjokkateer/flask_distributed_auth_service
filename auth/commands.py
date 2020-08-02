from app import app, db
from classes import KeyGenerator, KeyFileWriter
from flask.cli import AppGroup
from models import Key


import click


auth_cli = AppGroup('auth')

@auth_cli.command('gen-keys')
@click.argument('number')
def generate_keys(number):
    '''
    Create NUMBER private and public key pairs.
    '''
    for _ in range(int(number)):
        generate_and_store_random_key_pair()

def generate_and_store_random_key_pair(is_refresh_token_key=False):
    key_generator = KeyGenerator()
    key_file_writer = KeyFileWriter(key_generator)
    key = Key(is_refresh_token_key=is_refresh_token_key)

    try:
        db.session.add(key)
        db.session.commit()

        key_file_writer.write_keys_to_file(str(key.id))
    except:
        db.session.rollback()

@auth_cli.command('gen-refresh-keys')
@click.argument('number')
def generate_refresh_token_key(number):
    '''
    Create NUMBER private and public key pairs for refresh token
    '''
    for _ in range(int(number)):
        generate_and_store_random_key_pair(is_refresh_token_key=True)

app.cli.add_command(auth_cli)
