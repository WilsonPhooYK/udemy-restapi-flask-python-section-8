from dataclasses import dataclass
from db import db
from typing import TypedDict, Optional

ItemModelType = TypedDict(
    "ItemModelType",
    {
        "name": str,
        "price": float,
        "store_id": int,
    },
)

Model = db.Model

@dataclass
class ItemModel(Model):
    __tablename__ = 'items'

    id: int = db.Column(db.Integer, primary_key=True)
    name: str = db.Column(db.String(80))
    price: float = db.Column(db.Float(precision=2))
    
    store_id = db.Column(db.Integer, db.ForeignKey('stores.id'))
    # Matches store_id to Store
    store = db.relationship('StoreModel')
    
    def __init__(self, name: str, price: float, store_id: int) -> None:
        # Must have id to authenticate
        self.name = name
        self.price = price
        self.store_id = store_id

    def json(self) -> ItemModelType:
        return {'name': self.name, 'price': self.price, 'store_id': self.store_id}
    
    @classmethod
    def find_by_name(cls, name: str) -> Optional['ItemModel']:
        # SELECT * FROM items WHERE name=name LIMIT 1
        return cls.query.filter_by(name=name).first()

    def save_to_db(self):
        db.session.add(self)
        db.session.commit()

    def delete_from_db(self):
        db.session.delete(self)
        db.session.commit()