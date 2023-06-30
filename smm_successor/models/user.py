from typing import Optional, Dict

from pydantic import BaseModel, Field


class BaseUser(BaseModel):
    id: Optional[str]
    username: str = Field(title="Username")
    email: str = Field(title="email")

    @classmethod
    def from_db(cls, data: Dict) -> 'BaseUser':
        _id = str(data['_id'])
        del data['_id']

        return cls(
            id=_id,
            **data
        )


class UserInDB(BaseUser):
    hashed_password: str


class Token(BaseModel):
    access_token: str
    token_type: str


class TokenData(BaseModel):
    username: Optional[str] = None
