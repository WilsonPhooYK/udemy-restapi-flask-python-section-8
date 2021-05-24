from dataclasses import dataclass
from db import db
from typing import Any, TypedDict, Optional
from models.item import ItemModelType
from typings.sql_alchemy import QueryModel

StoreModelType = TypedDict(
    "StoreModelType",
    {
        "id": int,
        "name": str,
        "items": list[ItemModelType],
    },
)

Model = db.Model

@dataclass
class StoreModel(Model):
    __tablename__ = 'stores'

    id: int = db.Column(db.Integer, primary_key=True)
    name: str = db.Column(db.String(80))
    
    # SELECT * FROM items WHERE store_id = id
    # lazy = dynamic makes items become a query builder, so as not
    # to create all the items from the start, but we need to call it everytime in
    # the json method
    items: QueryModel = db.relationship('ItemModel', lazy='dynamic')
    
    def __init__(self, name: str) -> None:
        self.name = name

    def json(self) -> StoreModelType:
        return {'name': self.name, 'items': [item.json() for item in self.items.all()], 'id': self.id}
    
    @classmethod
    def find_by_name(cls, name: str) -> Optional['StoreModel']:
        # SELECT * FROM items WHERE name=name LIMIT 1
        return cls.query.filter_by(name=name).first()
    
    @classmethod
    def find_all(cls) -> Any:
        return cls.query.all()

    def save_to_db(self):
        db.session.add(self)
        db.session.commit()

    def delete_from_db(self):
        db.session.delete(self)
        db.session.commit()