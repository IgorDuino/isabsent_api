from data import db_session
from data.user import User
from tools.tools import create_access_token, check_password
from fastapi import APIRouter, status, HTTPException, Depends
from fastapi.security import OAuth2PasswordRequestForm


auth_router = APIRouter()


@auth_router.post("/token")
async def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends()):
    """
        Generate JWT token for user
    """
    db_sess = db_session.create_session()
    user = db_sess.query(User).filter(User.login == form_data.username).first()

    if not (user and check_password(form_data.password, user.hashed_password)):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    user.token_id += 1
    db_sess.commit()
    access_token = create_access_token(user.login, user.token_id)
    return {"access_token": access_token, "token_type": "bearer"}
