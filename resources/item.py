from flask_restful import Resource, reqparse
from flask_jwt_extended import jwt_required, get_jwt, get_jwt_identity
from typing import Any, Union
from models.item import ItemModel, ItemModelType


JSONResponseType = tuple[dict[str, str], int]
# JWT - JSON Web Token

# 400 - bad request
# 404 - item not found
# 201 - create success
# 202 - accepted, but will create success only after a long time
class Item(Resource):
    parser = reqparse.RequestParser()
    parser.add_argument(
        "price", type=float, required=True, help="This field cannot be left blank!"
    )
    parser.add_argument(
        "store_id", type=int, required=True, help="Every item needs a store id."
    )

    # Authorization - JWT {token}
    @jwt_required()
    def get(self, name: str) -> Union[ItemModelType, JSONResponseType]:
        item = ItemModel.find_by_name(name)
        if item:
            return item.json()

        return {"error_message": "Item not found"}, 404

    # except StopIteration:
    # return {"error_message": "Item not found"}, 404
    @jwt_required(fresh=True)
    def post(self, name: str) -> Union[tuple[ItemModelType, int], JSONResponseType]:
        if ItemModel.find_by_name(name):
            return {"message": f"An item with name '{name}' already exists."}, 400

        # Only parse for price
        data: ItemModelType = Item.parser.parse_args()
        item = ItemModel(name, data["price"], data["store_id"])

        try:
            item.save_to_db()
        except:
            return {
                "error_message": "An error occured inseting the item"
            }, 500  # Internal Server Error

        return item.json(), 201

    @jwt_required()
    def delete(self, name: str) -> JSONResponseType:
        # Get claims from jwt
        claims = get_jwt()
        if not claims.get('is_admin'):
            return {'message': 'Admin privilege required.'}, 401

        item = ItemModel.find_by_name(name)
        if not item:
            return {"message": f"An item with name '{name}' does not exists."}, 400

        item.delete_from_db()

        return {"message": "Item deleted"}, 200

    def put(self, name: str) -> Union[tuple[ItemModelType, int], JSONResponseType]:
        # Only parse for price
        data: ItemModelType = Item.parser.parse_args()
        item = ItemModel(name, data["price"], data["store_id"])

        if ItemModel.find_by_name(name):
            item = ItemModel(name, data["price"], data["store_id"])
        else:
            item.price = data["price"]
            
        item.save_to_db()

        return item.json(), 200

class ItemList(Resource):
    @jwt_required(optional=True)
    def get(self) -> tuple[Any, int]:
        user_id = get_jwt_identity()
        items = [item.json() for item in ItemModel.find_all()]
        
        if user_id:
            return items, 200
        
        return {
            'items': [item['name'] for item in items],
            'messsage': 'More data available if you login',
        }, 200
        # return list(map(lambda item: item.json(), ItemModel.query.all())), 200
        # return [item.json() for item in ItemModel.find_all()], 200
