from data import db_session
from data.school import School
from data.teacher import Teacher
from data.student import Student
from fastapi import APIRouter, status, HTTPException, Depends
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from jose import JWTError, jwt
from passlib.context import CryptContext

from data.user import User

auth_router = APIRouter()
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
SECRET_KEY = "1627403a671b12805a499e7e061d1c8d82ed380ba607895565b2b59c62458a54"
ALGORITHM = "HS256"


def create_access_token(login: str):
    to_encode = {
       'login': login
    }
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


async def token_check(token: str = Depends(oauth2_scheme)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        login: str = payload.get("login")
        if login is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception
    db_sess = db_session.create_session()
    user = db_sess.query(User).filter(User.login == login).first()
    if user is None:
        raise credentials_exception
    return user.enabled


@auth_router.post("/token")
async def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends()):
    db_sess = db_session.create_session()
    user = db_sess.query(User).filter(User.login == form_data.username).first()
    if not user or form_data.password != user.hashed_password:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token = create_access_token(user.login)
    return {"access_token": access_token, "token_type": "bearer"}