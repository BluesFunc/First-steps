from typing import Annotated, Union, List
from datetime import datetime

from pydantic import BaseModel, EmailStr, Field


class Token(BaseModel):
    access_token: str
    token_type: str


class Ticket(BaseModel):
    price: float
    origin: str
    destination: str
    departure_time: datetime
    arrival_time: datetime


class User(BaseModel):
    username: str
    name: Union[str, None] = None
    surname: Union[str, None] = None
    passport_series: str = Field(max_length=8, min_length=8)
    EmailStr: Union[EmailStr, None] = None
    tickets: Union[List[Ticket], None] = None


class UserInDB(User):
    hashed_password: str
