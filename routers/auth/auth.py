from jose import JWTError, jwt
from fastapi import status, HTTPException, Depends
from passlib.context import CryptContext
from fastapi.security import OAuth2PasswordBearer
from data import db_session
from data.user import User
from tools.settings import *

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/v1/token")
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


async def token_check(token: str = Depends(oauth2_scheme)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        login: str = payload.get("login")
        token_id: int = payload.get("token_id")

        if login is None or token_id is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception

    db_sess = db_session.create_session()
    user = db_sess.query(User).filter(User.login == login).first()
    if user is None or not user.enabled:
        raise credentials_exception

    if user.token_id != token_id:
        raise credentials_exception
