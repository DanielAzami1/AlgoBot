from flask import Flask
import os


def create_app():
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_mapping(
        SECRET_KEY='dev'
    )
    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass

    return app
