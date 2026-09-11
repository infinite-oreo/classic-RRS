from flask import Flask

from . import config, db, scheduler
from .routes import register_blueprints


def create_app():
    app = Flask(__name__)
    app.config["SECRET_KEY"] = config.SECRET_KEY

    db.init_app(app)
    db.init_db()

    register_blueprints(app)
    scheduler.start()

    return app
