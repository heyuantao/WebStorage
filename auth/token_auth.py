#-*- coding=utf-8 -*-
from flask import Flask
from flask_httpauth import HTTPBasicAuth, HTTPDigestAuth, HTTPTokenAuth
from config import config

token_list = config.App.AUTH_TOKEN

class TokenAuth:
    auth = None

    def init_app(self, app=None):
        auth = HTTPTokenAuth(scheme='Token')
        self.auth = auth

        @auth.verify_token
        def verify_token(token):
            if token in token_list:
                return True
            return False

    def get_auth(self):
        return self.auth
