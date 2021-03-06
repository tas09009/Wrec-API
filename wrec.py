# from flask import Flask, render_template
# from flask_bootstrap import Bootstrap

# app = Flask(__name__)
# bootstrap = Bootstrap(app)

import os
from app import create_app, db
from app.models import User, Book, TenCategories, HundredCategories, ThousandCategories
from flask_migrate import Migrate, upgrade

app = create_app(os.getenv("FLASK_CONFIG") or "default")
migrate = Migrate(app, db)


"""To avoid importing database instances and models into a shell session"""


@app.shell_context_processor
def make_shell_context():
    return dict(
        db=db,
        User=User,
        Book=Book,
        TenCategories=TenCategories,
        HundredCategories=HundredCategories,
        ThousandCategories=ThousandCategories,
    )


@app.cli.command()
def test():
    """Run the unit tests"""
    import unittest

    tests = unittest.TestLoader().discover("tests")
    unittest.TextTestRunner(verbosity=2).run(tests)


@app.cli.command()
def deploy():
    """Run deployment tasks"""
    # migrate database to latest revision
    upgrade()
