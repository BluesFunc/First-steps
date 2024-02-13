from typing import Union

from pydantic import BaseModel, Field


class Image(BaseModel):
    url: str
    name: str

    class Config:
        json_schema_extra = {
            "examples": [
                {
                    "name": "Student",
                    "url": "http//doiki.com"
                }
            ]
        }


class Item(BaseModel):
    name: str
    description: Union[str, None] = Field(
        default=None, title="The description of the item", max_length=100
    )
    price: float = Field(gt=0, description="price must be greater than zero")
    tax: Union[float, None] = None

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "name": "Foo",
                    "description": "A very nice Item",
                    "price": 35.4,
                    "tax": 3.2,
                }
            ]
        }
    }


class BaseUser(BaseModel):
    username: str
    email: Union[str, None] = None
    full_name: Union[str, None] = None
    disabled: Union[bool, None] = None


class UserIn(BaseUser):
    password: str


class UserInDB(BaseUser):
    hashed_password: str


class UserOut(BaseUser):
    pass
