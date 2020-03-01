import os

class FileStorageConfig:
    TMP_UPLOAD_PATH ="./data/tmp"                               #before merge
    UPLOAD_PATH = "./data/merged"                               #not end with slash


class AppConfig:
    STATIC_FOLDER = "./templates/mystorageapp/build/static"  # not end with slash
    TEMPLATE_FOLDER = "./templates/mystorageapp/build"  # not end with slash
    AUTH_TOKEN = ["1234567890","abcdefghi"]


class Config:
    FileStorage = FileStorageConfig()
    App = AppConfig()

config = Config()