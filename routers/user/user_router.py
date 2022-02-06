import logging
import routers.user.schemas as schemas

from tools.error_book import *
from tools.settings import *
from routers.responses import *
from fastapi import APIRouter, status, Depends
from fastapi.responses import JSONResponse
from data import db_session
from data.user import User
from jose import jwt
from routers.auth.auth import token_check


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
            hashed_password=hashed_password,
            info=body.info
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
        Get information about user with given login:

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


@user_router.get("/user/",
                 summary='Get user list',
                 status_code=status.HTTP_200_OK,
                 responses={200: {"model": schemas.UserGetList},
                            404: {"model": NotFound}})
def user_get():
    """Get information about users"""
    try:
        db_sess = db_session.create_session()
        users = db_sess.query(User).all()

        response = schemas.UserGetList(users=[])
        for user in users:
            response.users.append(schemas.UserGet(email=user.email,
                                                  login=user.login,
                                                  info=user.info))

        return JSONResponse(content=response.dict(), status_code=status.HTTP_200_OK)
    except UserNotFountError as error:
        logging.warning(error)
        return JSONResponse(**NotFound(content=str(error)).dict())


@user_router.patch("/user/{login}",
                   summary='Patch user',
                   status_code=status.HTTP_200_OK,
                   dependencies=[Depends(token_check)],
                   responses={200: {"model": SuccessfulResponse},
                              404: {"model": NotFound},
                              400: {"model": BadRequest}})
def user_patch(login: str, body: schemas.UserPatch):
    """
        Patch user with given login:

        - **login**: user login, required
        - **new_password**: new password for user, not required
        - **new_email**: new email for user, not required
        - **new_login**: new login for user, not required
        - **new_info**: new info for user, not required
    """
    try:
        db_sess = db_session.create_session()
        user = db_sess.query(User).filter(User.login == login).first()

        if user is None:
            raise UserNotFountError(login=login)

        if not (body.new_login is None):
            user.login = body.new_login
        if not (body.new_email is None):
            user.email = body.new_email
        if not (body.new_password is None):
            user.hashed_password = jwt.encode({'password': body.new_password}, SECRET_KEY, ALGORITHM)
        if not (body.new_info is None):
            user.info = body.new_info

        db_sess.commit()
        return JSONResponse(**SuccessfulResponse(content='User changed').dict())
    except UserNotFountError as error:
        logging.warning(error)
        return JSONResponse(**NotFound(content=str(error)).dict())


@user_router.delete("/user/{login}",
                    summary='Delete user',
                    status_code=status.HTTP_200_OK,
                    dependencies=[Depends(token_check)],
                    responses={200: {"model": SuccessfulResponse},
                               404: {"model": NotFound}})
def user_delete(login: str):
    """
        Delete user with given login:

        - **login**: user login, required
    """
    try:
        db_sess = db_session.create_session()
        user = db_sess.query(User).filter(User.login == login).first()

        if user is None:
            raise UserNotFountError(login=login)

        db_sess.delete(user)
        db_sess.commit()

        return JSONResponse(**SuccessfulResponse(content='User deleted').dict())
    except UserNotFountError as error:
        logging.warning(error)
        return JSONResponse(**NotFound(content=str(error)).dict())
