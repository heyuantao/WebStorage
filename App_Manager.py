#-*- coding=utf-8 -*-
from flask import Flask
from flask_cors import CORS
from werkzeug.serving import WSGIRequestHandler
from config import config
import logging

logger = logging.getLogger(__name__)


def read_upload_file_list_to_db(db,store):
    file_list = store.get_upload_file_list()
    for file in file_list:
        db.add_to_downloadable_file_list_by_key(file)

def create_app():
    app = Flask(__name__,static_folder=config.App.STATIC_FOLDER, template_folder=config.App.TEMPLATE_FOLDER)
    app.config.from_object(config)
    CORS(app)
    app.secret_key = 'A0Zr98j/3yX R~XHH!jmN]LWX/,?RT'

    from auth import Auth
    auth_instance = Auth()
    auth_instance.init_app(app)

    from routes import Manager_Router
    route_instance = Manager_Router()
    route_instance.init_app(app, auth_instance.get_auth())

    from storage import Storage
    storage_instance = Storage()
    storage_instance.init_app(app)

    from db import Database
    redis_instance = Database()
    redis_instance.init_app(app)

    #init finished
    read_upload_file_list_to_db(redis_instance, storage_instance)
    return app

#WSGIRequestHandler.protocol_version = "HTTP/1.1"
application = create_app()

if __name__ == '__main__':
    logging.basicConfig(level=logging.DEBUG)
    application.run(port=5000,host="0.0.0.0")
