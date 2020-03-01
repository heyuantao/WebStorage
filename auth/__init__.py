#-*- coding=utf-8 -*-
from . import token_auth

def init_app(app):
    token_auth.init_app(app)

def get_auth():
    token_auth.get_auth()
