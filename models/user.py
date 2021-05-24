from dataclasses import dataclass
from typing import TypedDict
from db import db

Model = db.Model

UserModelType = TypedDict('UserModelType', {
    'id': int,
    'username': str,
})

@dataclass
class UserModel(Model):
    __tablename__ = 'users'
    # Must have id to authenticate
    id: int = db.Column(db.Integer, primary_key=True)
    username: str = db.Column(db.String(80))
    password: str = db.Column(db.String(80))

    def __init__(self, username: str, password: str) -> None:
        # Must have id to authenticate
        self.username = username
        self.password = password
        
    def json(self) -> UserModelType:
        return {
            'id': self.id,
            'username': self.username
        }

    @classmethod
    def find_by_username(cls, username: str) -> "UserModel":
        # SELECT * FROM items WHERE username=username LIMIT 1
        return cls.query.filter_by(username=username).first()

    @classmethod
    def find_by_id(cls, _id: int) -> "UserModel":
        # SELECT * FROM items WHERE id=_id LIMIT 1
        return cls.query.filter_by(id=_id).first()
    
    def save_to_db(self):
        db.session.add(self)
        db.session.commit()
        
    def delete_from_db(self):
        db.session.delete(self)
        db.session.commit()