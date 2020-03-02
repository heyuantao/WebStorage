#-*- coding=utf-8 -*-
from flask import Flask
from flask_cors import CORS
from config import config


def create_app():
    app = Flask(__name__,static_folder=config.App.STATIC_FOLDER, template_folder=config.App.TEMPLATE_FOLDER)
    app.config.from_object(config)
    CORS(app)
    app.secret_key = 'A0Zr98j/3yX R~XHH!jmN]LWX/,?RT'

    from auth import Auth
    auth_instance = Auth()
    auth_instance.init_app(app)


    from routes import Route
    route_instance = Route()
    route_instance.init_app(app, auth_instance.get_auth())

    from database import RedisClient
    redis_instance = RedisClient()
    redis_instance.init_app(app)

    return app


if __name__ == '__main__':
    app = create_app()
    app.run(port=34567,host="0.0.0.0")
