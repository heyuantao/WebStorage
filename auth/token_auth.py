#-*- coding=utf-8 -*-
from flask import Flask
from flask_httpauth import HTTPBasicAuth, HTTPDigestAuth, HTTPTokenAuth

tokens = {
    "secret-token-1": "john",
    "secret-token-2": "susan"
}

class TokenAuth:
    auth = None

    def init_app(self, app=None):
        auth = HTTPTokenAuth(scheme='Token')
        self.auth = auth

        @auth.verify_token
        def verify_token(token):
            if token in tokens:
                return True
            return False

    def get_auth(self):
        return self.auth
