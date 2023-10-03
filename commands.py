import click
from flask.cli import with_appcontext

import app


@click.command(name='create_tables')
@with_appcontext
def create_tables():
    app.db.create_all()
