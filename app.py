from blacklist import BLACKLIST
import os
from typing import Any, cast

from flask import Flask, jsonify
from flask_restful import Api
from flask_jwt_extended import JWTManager

from db import db

from resources.user import UserRegister, User, UserLogin, TokenRefresh
from resources.item import Item, ItemList
from resources.store import Store, StoreList

app = Flask(__name__)
# db at root foler
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URI', 'sqlite:///data.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
# Will raise 400 instead of 500 for flask errors
app.config['PROPAGATE_EXCEPTIONS'] = True
app.config['JWT_BLACKLIST_ENABLED'] = True
app.config['JWT_BLACKLIST_TOKEN_CHECKS'] = ['access', 'refresh']
app.secret_key = "jose"
api = Api(app)

# app.config['JWT_AUTH_URL_RULE'] = '/login'
# app.config['JWT_EXPIRATION_DELTA'] = timedelta(seconds=1800)
# app.config['JWT_AUTH_USERNAME_KEY'] = 'email'
jwt = JWTManager(app)  # not creating /auth

# Run this whenever a new JWT is created
@jwt.additional_claims_loader
def add_claims_to_jwt(identity: int) -> Any:
    return {'is_admin': True if identity == 1 else False}

@jwt.token_in_blocklist_loader
def check_if_token_in_blocklist(_decrypted_header: Any, decrypted_body: Any):
    return decrypted_body.get('jti') in BLACKLIST

# The following callbacks are used for customizing jwt response/error messages.
# The original ones may not be in a very pretty format (opinionated)
@jwt.expired_token_loader
def expired_token_callback():
    return cast(Any, jsonify({
        'description': 'The token has expired.',
        'error': 'token_expired'
    })), 401


@jwt.invalid_token_loader
def invalid_token_callback(error: Any):  # we have to keep the argument here, since it's passed in by the caller internally
    return cast(Any, jsonify({
        'description': 'Signature verification failed.',
        'error': 'invalid_token'
    })), 401


@jwt.unauthorized_loader
def missing_token_callback(error: Any):
    return cast(Any, jsonify({
        'description': 'Request does not contain an access token.',
        'error': 'authorization_required'
    })), 401


@jwt.needs_fresh_token_loader
def token_not_fresh_callback():
    return cast(Any, jsonify({
        'description': 'The token is not fresh.',
        'error': 'fresh_token_required'
    })), 401


@jwt.revoked_token_loader
def revoked_token_callback(_decrypted_header: Any, _decrypted_body: Any):
    return cast(Any, jsonify({
        'description': 'The token has been revoked.',
        'error': 'token_revoked'
    })), 401

# from security import authenticate, identity as identity_function
# jwt = JWT(app, authenticate, identity_function)

# @jwt.auth_response_handler
# def customized_response_handler(access_token, identity):
#     return jsonify({
#                         'access_token': access_token.decode('utf-8'),
#                         'user_id': identity.id
#                    })

# @jwt.error_handler
# def customized_error_handler(error):
#     return jsonify({
#                        'message': error.description,
#                        'code': error.status_code
#                    }), error.status_code

api.add_resource(Item, "/item/<string:name>")
api.add_resource(ItemList, "/items")
api.add_resource(UserRegister, '/register')
api.add_resource(Store, '/store/<string:name>')
api.add_resource(StoreList, '/stores')
api.add_resource(User, '/user/<int:user_id>')
api.add_resource(UserLogin, '/login')
api.add_resource(TokenRefresh, '/refresh')

if __name__ == "__main__":
    # Run method before first request into app
    # NEED TO IMPORT ALL MODELS SO DB CAN CREATE TABLE
    @app.before_first_request
    def create_tables():
        db.create_all()
        
    db.init_app(app)
    app.run(port=5000, debug=True)
