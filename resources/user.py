from typing import Any
from flask_restful import Resource, reqparse

from models.user import UserModel

JSONResponseType = tuple[dict[str, Any], int]

class UserRegister(Resource):
    parser = reqparse.RequestParser()
    parser.add_argument(
        "username",
        type=str,
        required=True,
        help="This field cannot be left blank!",
    )
    parser.add_argument(
        "password",
        type=str,
        required=True,
        help="This field cannot be left blank!",
    )

    def post(self) -> JSONResponseType:
        data: dict[str, str] = UserRegister.parser.parse_args()
        
        if UserModel.find_by_username(data["username"]):
            return {"error_message": "User exists"}, 400

        user = UserModel(**data)
        user.save_to_db()

        return {"success": True}, 201
