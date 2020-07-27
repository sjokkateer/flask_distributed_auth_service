from app import app
from flask.cli import AppGroup


import click


auth_cli = AppGroup('auth')

@auth_cli.command('gen-keys')
@click.argument('number')
def generate_keys(number):
    '''
    Create NUMBER private and public key pairs.
    '''
    from classes import KeyGenerator
    
    for _ in number:
        KeyGenerator.generate_key_pair()

app.cli.add_command(auth_cli)
