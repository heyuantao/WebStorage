import os

class Config:
    TMP_UPLOAD_PATH ="./data/tmp"                               #before merge
    UPLOAD_PATH = "./data/merged"                               #not end with slash
    STATIC_FOLDER = "./templates/mystorageapp/build/static"     #not end with slash
    TEMPLATE_FOLDER = "./templates/mystorageapp/build"          #not end with slash


config = Config()