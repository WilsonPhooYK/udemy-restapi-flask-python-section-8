from typing import Union
from flask_jwt import jwt_required
from flask_restful import Resource

from models.store import StoreModel, StoreModelType

JSONResponseType = tuple[dict[str, str], int]

class Store(Resource):
    # Authorization - JWT {token}
    @jwt_required()
    def get(self, name: str) -> Union[StoreModelType, JSONResponseType]:
        # Returns the current user row
        item = StoreModel.find_by_name(name)
        if item:
            return item.json()

        return {"error_message": "Store not found"}, 404
    
    @jwt_required()
    def post(self, name: str) -> Union[tuple[StoreModelType, int], JSONResponseType]:
        if StoreModel.find_by_name(name):
            return {"message": f"An store with name '{name}' already exists."}, 400

        store = StoreModel(name)

        try:
            store.save_to_db()
        except:
            return {
                "error_message": "An error occured inseting the item"
            }, 500  # Internal Server Error

        return store.json(), 201
    
    @jwt_required()
    def delete(self, name: str) -> JSONResponseType:
        store = StoreModel.find_by_name(name)
        if not store:
            return {"message": f"A store with name '{name}' does not exists."}, 400

        store.delete_from_db()

        return {"message": "Store deleted"}, 200
    
class StoreList(Resource):
    def get(self) -> tuple[list[StoreModelType], int]:
        return [store.json() for store in StoreModel.query.all()], 200