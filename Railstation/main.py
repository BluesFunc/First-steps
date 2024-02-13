from datetime import timedelta, timezone, datetime
from typing import Annotated, Union

from fastapi import FastAPI, HTTPException, status, Depends
from fastapi.security import OAuth2PasswordRequestForm, OAuth2PasswordBearer
from jose import jwt, JWTError
from passlib.context import CryptContext

from models import User, UserInDB, Token

SECURITY_KEY = "04589309efc8c8130f0a5c5ae977464ed390a81be38ac21aa9fcbbe958d8bb64"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

user_db = {
    "Alex": {
        "username": "Alex",
        "passport_series": "MK456709",
        "email": "LEAXA@gmail.com",
        "tickets": []
    },
}

tickets_db = {
    1: {
        "price": 12.1,
        "origin": "Minsk",
        "destination": "Saratov",
        "departure_time": "12/12/24 22:56",
        "arrival_time": "13/12/24 12:44"
    },
    2: {
        "price": 5.2,
        "origin": "Minsk",
        "destination": "Borisov",
        "departure_time": "12/12/23 22:56",
        "arrival_time": "13/12/23 12:44"
    },
    3: {
        "price": 5.2,
        "origin": "Moscow",
        "destination": "Kazan",
        "departure_time": "30/01/24 12:32",
        "arrival_time": "30/01/24 20:44"
    }
}

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

authentication = OAuth2PasswordBearer(tokenUrl="token")

app = FastAPI()


def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password):
    return pwd_context.hash(password)


def get_user(db, username: str) -> User:
    if username in db:
        user_dict = db[username]
        return UserInDB(**user_dict)


def authenticate_user(db, user: str, password: str):
    user = get_user(db, user)
    if not user:
        return False
    if not verify_password(password, user.hashed_password):
        return False
    return user


def create_access_token(data: dict, expires_delta: timedelta):
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + expires_delta
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECURITY_KEY, algorithm=ALGORITHM)
    return encoded_jwt


@app.post("/token")
async def login(form_data: Annotated[OAuth2PasswordRequestForm, Depends()]) -> Token:
    user = authenticate_user(user_db, form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.username}, expires_delta=access_token_expires
    )
    return Token(access_token=access_token, token_type="bearer")


async def get_current_user(token: Annotated[str, Depends(authentication)]):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECURITY_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception
    user = get_user(user_db, username=username)
    if user is None:
        raise credentials_exception
    return user


@app.post("/register")
def register(
        form_data: Annotated[OAuth2PasswordRequestForm, Depends()]
):
    if form_data.username in user_db:
        raise HTTPException(detail="User already exist", status_code=400)
    hashed_password = get_password_hash(form_data.password)
    new_user = UserInDB(
        username=form_data.username, hashed_password=hashed_password, passport_series="MR123456"
    )
    user_db.update({form_data.username: {**new_user.model_dump()}})
    return {"new_user": {**new_user.model_dump()}}


@app.post("/me/username")
def get_username(user: Annotated[User, Depends(get_current_user)]):
    return {"username": {**user.model_dump()}}
