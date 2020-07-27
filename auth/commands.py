from app import app
from flask.cli import AppGroup

import click


auth_cli = AppGroup('auth')

@auth_cli.command('gen-keys')
@click.argument('number')
def generate_keys(number):
    for _ in number:
        import script

app.cli.add_command(auth_cli)
