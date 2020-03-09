#-*- coding=utf-8 -*-
from flask import Flask
from flask_cors import CORS
from werkzeug.serving import WSGIRequestHandler
from config import config
import logging

logger = logging.getLogger(__name__)


def create_app():
    app = Flask(__name__,static_folder=config.App.STATIC_FOLDER, template_folder=config.App.TEMPLATE_FOLDER)
    app.config.from_object(config)
    CORS(app)
    app.secret_key = 'A0Zr98j/3yX R~XHH!jmN]LWX/,?RR'

    from routes import FileServer_Router
    route_instance = FileServer_Router()
    route_instance.init_app(app)

    from storage import Storage
    storage_instance = Storage()
    storage_instance.init_app(app)

    from db import Database
    redis_instance = Database()
    redis_instance.init_app(app)

    #从gunicorn获得loglevel等级，并将其设置到app中
    gunicorn_logger = logging.getLogger("gunicorn.error")
    app.logger.handlers = gunicorn_logger.handlers
    app.logger.setLevel(gunicorn_logger.level)

    #if logger.getEffectiveLevel()==logging.DEBUG:
    #    logger.critical("The app is in debug mode, the merge process will execute slowly !")

    return app

WSGIRequestHandler.protocol_version = "HTTP/1.1"
application = create_app()

if __name__ == '__main__':
    #logging.basicConfig(level=logging.DEBUG)
    application.run(port=5001,host="0.0.0.0")
