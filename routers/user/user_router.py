import logging

from fastapi import APIRouter, status, HTTPException, Response
from data import db_session
from fastapi.responses import JSONResponse
from tools.error_book import *
from tools.settings import *
from routers.responses import *
import routers.user.schemas as schemas
from data.user import User
from jose import jwt
from tools.tools import check_password


user_router = APIRouter()


@user_router.put("/user",
                 summary='Add user',
                 status_code=status.HTTP_201_CREATED,
                 responses={201: {"model": CreatedResponse, "description": "User added"},
                            400: {"model": BadRequest}})
def user_put(body: schemas.User):
    """
        Add new user, all parameters are required:

        - **login**: unique user login
        - **password**: user password
        - **email**: user email
    """
    try:
        db_sess = db_session.create_session()
        user = db_sess.query(User).filter(User.login == body.login).first()

        if not (user is None):
            raise UserExistError(login=body.login)

        hashed_password = jwt.encode({'password': body.password}, SECRET_KEY, algorithm=ALGORITHM)
        db_sess.add(User(
            email=body.email,
            login=body.login,
            hashed_password=hashed_password
        ))
        db_sess.commit()
        return JSONResponse(**CreatedResponse(content='User created').dict())
    except UserExistError as error:
        logging.warning(error)
        return JSONResponse(**BadRequest(content=str(error)).dict())


@user_router.get("/user/{login}",
                 summary='Get user',
                 status_code=status.HTTP_200_OK,
                 responses={200: {"model": schemas.UserGet},
                            404: {"model": NotFound}})
def user_get(login: str):
    """
        Get information about user:

        - **login**: user login, required
    """
    try:
        db_sess = db_session.create_session()
        user = db_sess.query(User).filter(User.login == login).first()

        if user is None:
            raise UserNotFountError(login=login)

        response = schemas.UserGet(info=user.info, login=user.login, email=user.email)
        return JSONResponse(content=response.dict(), status_code=status.HTTP_200_OK)
    except UserNotFountError as error:
        logging.warning(error)
        return JSONResponse(**NotFound(content=str(error)).dict())


@user_router.patch("/user/{login}",
                   summary='Patch user',
                   status_code=status.HTTP_200_OK,
                   responses={200: {"model": SuccessfulResponse},
                              404: {"model": NotFound}})
def user_patch(login: str, body: schemas.UserPatch):
    """
        Patch user:

        - **login**: user login, required
    """
    try:
        db_sess = db_session.create_session()
        user = db_sess.query(User).filter(User.login == login).first()

        if user is None:
            raise UserNotFountError(login=login)

        if not check_password(body.old_password, user):
            raise WrongPasswordError(login=login)



        db_sess.commit()
        return JSONResponse(**SuccessfulResponse(content='User changed').dict())
    except UserNotFountError as error:
        logging.warning(error)
        return JSONResponse(**NotFound(content=str(error)).dict())
    except WrongPasswordError as error:
        logging.warning(error)
        return JSONResponse(**BadRequest(content=str(error)).dict())
