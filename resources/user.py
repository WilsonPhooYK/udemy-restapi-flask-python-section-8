from typing import Any, Union
from werkzeug.security import safe_str_cmp
from flask_jwt_extended import (
    create_access_token,
    create_refresh_token,
    get_jwt_identity,
    jwt_required,
    get_jwt
)
from flask_restful import Resource, reqparse
from blacklist import BLACKLIST

from models.user import UserModel, UserModelType

JSONResponseType = tuple[dict[str, Any], int]

_user_parser = reqparse.RequestParser()
_user_parser.add_argument(
    "username",
    type=str,
    required=True,
    help="This field cannot be left blank!",
)
_user_parser.add_argument(
    "password",
    type=str,
    required=True,
    help="This field cannot be left blank!",
)
    
class UserRegister(Resource):
    def post(self) -> JSONResponseType:
        data: dict[str, str] = _user_parser.parse_args()
        
        if UserModel.find_by_username(data["username"]):
            return {"error_message": "User exists"}, 400

        user = UserModel(**data)
        user.save_to_db()

        return {"success": True}, 201

class User(Resource):
    @classmethod
    def get(cls, user_id: int) -> Union[JSONResponseType, UserModelType]:
        user = UserModel.find_by_id(user_id)
        if not user:
            return {"error_message": "User not found"}, 404
        return user.json()
    
    @classmethod
    def delete(cls, user_id: int) -> JSONResponseType:
        user = UserModel.find_by_id(user_id)
        if not user:
            return {"error_message": "User not found"}, 404
        user.delete_from_db()
        return {"message": "User deleted"}, 200
    
class UserLogin(Resource):
    @classmethod
    def post(cls) -> JSONResponseType:
        # get data from parser
        data: dict[str, str] = _user_parser.parse_args()
    
        # find user in database
        user = UserModel.find_by_username(data["username"])

        # This is what the authenticate() dunction used to 
        if user and safe_str_cmp(user.password, data['password']):
            # create access token
            access_token = create_access_token(identity=user.id, fresh=True)
            # create refresh token
            refresh_token = create_refresh_token(user.id)
            return {
                'access_token': access_token,
                'refresh_token': refresh_token
            }, 200
            
            
        return {"message": "Invalid credentials"}, 401
    
class UserLogout(Resource):
    @jwt_required()
    def post(self):
        jti = get_jwt()['jti'] # jti is 'JWT ID', a unique identifier for a jwt
        BLACKLIST.add(jti)
        return {'message': 'Successfully logged out.'}, 200
    
class TokenRefresh(Resource):
    @jwt_required(refresh=True)
    def post(self):
        current_user = get_jwt_identity()
        new_token = create_access_token(identity=current_user, fresh=False)
        return {'access_token': new_token}, 200