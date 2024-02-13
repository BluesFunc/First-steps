from typing import Union, List, Any
from typing_extensions import Annotated

from fastapi import (FastAPI, Query, Request,
                     Response, status, Form,
                     UploadFile, File, HTTPException,
                     Depends, Header)
from fastapi.responses import RedirectResponse, JSONResponse, HTMLResponse, PlainTextResponse
from fastapi.exceptions import RequestValidationError
from fastapi.security import OAuth2PasswordBearer

from models import BaseUser, UserIn, UserInDB, UserOut, Item

app = FastAPI()
items = {"foo": "Pretender"}


@app.get("/")
async def main():
    content = """
<body>
<form action="/files/" enctype="multipart/form-data" method="post">
<input name="files" type="file" multiple>
<input type="submit">
</form>
<form action="/uploadfiles/" enctype="multipart/form-data" method="post">
<input name="files" type="file" multiple>
<input type="submit">
</form>
</body>
    """
    return HTMLResponse(content=content)


@app.post("/login")  # Forms
async def login(username: Annotated[str, Form()], password: Annotated[str, Form()]):
    return {"username": username}


@app.post("/user/", status_code=status.HTTP_201_CREATED)  # Change status code
async def create_user(user: UserIn) -> BaseUser:
    return user


@app.get("/items", response_model=List[Item])  # Define response type
async def read_items() -> Any:
    return [
        {"name": "Alex", "price": 12.3},
        {"name": "John", "price": 78.1}
    ]


# File path
@app.get("/data")
async def get_some_string(q: Annotated[Union[str, None], Query(max_length=10)] = None):
    if q:
        return {q}
    return {"NOTING"}


@app.get("/files/{file_path:path}")
async def read_item(file_path: str):
    file_name = file_path.split("/")[-1]
    return {"file_name": file_name}


# Set query parameters

@app.get("/set_query_parameters_length_with_annotated")
async def new_set_query_parameters_length(
        q: Annotated[
            Union[None, str],
            Query(
                alias="param",
                max_length=5,
                deprecated=True,
                description="Nothing specials with that parameters",
                include_in_schema=False
            )
        ] = None
):
    if q:
        return {"q": q}
    return "None"


@app.get("/set_query_parameters_length_without_annotated")
async def old_set_query_parameters_length(q: Union[None, str] = Query(default=None, max_length=50)):
    if q:
        return {"q": q}
    return "None"


# Return responses

@app.get("/portal")
async def get_portal(teleport: bool = False) -> Response:
    if teleport:
        return RedirectResponse(url="https://www.youtube.com/watch?v=dQw4w9WgXcQ")
    return JSONResponse(content={"message": "Cake is a lie"})


# Extra models
def fake_password_hasher(raw_password: str):
    return "superhash" + raw_password


def fake_save_user(user_in: UserIn):
    hashed_password = fake_password_hasher(user_in.password)
    user_in_db = UserInDB(**user_in.model_dump(), hash_password=hashed_password)
    return user_in_db


@app.post("/user/", response_model=UserOut)
async def creat_user(user_in: UserIn):
    user_saved = fake_save_user(user_in)
    return user_saved


# Upload files

@app.post("/files/")
async def create_files(
        files: Annotated[List[bytes], File(description="Multiple files as bytes")],
):
    return {"file_sizes": [len(file) for file in files]}


@app.post("/uploadfiles/")
async def create_upload_files(
        files: Annotated[
            List[UploadFile], File(description="Multiple files as UploadFile")
        ],
):
    return {"filenames": [file.filename for file in files]}


# Exceptions
@app.get("/items/{item_id}", tags=["items"])
async def read_item(item_id: str):
    if item_id not in items:
        raise HTTPException(
            status_code=404,
            detail="Item not found",
            headers={"X-Error": "There goes my error"}  # custom header
        )
    return {"item": items[item_id]}


class UnicornExceptions(Exception):  # This class and decorated function below is a custom exception
    def __init__(self, name: str):
        self.name = name


@app.exception_handler(UnicornExceptions)
async def unicorn_exceptions_handler(request: Request, exc: UnicornExceptions):
    return JSONResponse(
        status_code=status.HTTP_418_IM_A_TEAPOT,
        content={"message": f"Wow, {exc.name} is doing total bullshit right now"}
    )


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request, exc):
    return PlainTextResponse(str(exc), status_code=400)


@app.get("/unicorns/{name}")
async def read_unicorn(name: int, server: Annotated[str, Header()]):
    return {"message": f"{name} is a good boy {server}"}


# Dependencies

async def common_parameters(
        q: Union[str, None] = None, skip: int = 0, limit: int = 100
):
    return {"q": q, "skip": skip, "limit": limit + 12}


@app.get("/users/")
async def read_users(common: Annotated[dict, Depends(common_parameters)]):
    return common


# Помимо добавления в агрументы функции, зависимости можно включать в декораторы пути.
# В этом случае значения, возвращаемые вызываемым объектом, не используються
# Их можно глобално кастить к приложению. ТАк они подействую на все декораторы пути
# Также можно использовать yield вместо return.
# Например, в случае если нужно выполнить операции после возвращения значения

# Security

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")


@app.get("/person/", tags=["security"])
async def read_person(token: Annotated[str, Depends(oauth2_scheme)]):
    return {"token": token}


# def fake_decode_token(token):
#     return User(
#         username=token+"BLABLA", email="alex@mail.ru", full_name="Alex"
#     )


# async def get_current_user(token: Annotated[str, Depends(oauth2_scheme)]):
#     user = fake_decode_token(token)
#     return user


# @app.get("/users/me", tags=["security"])
# async def read_users_me(current_user: Annotated[User, Depends(get_current_user)]):
#     return current_user
