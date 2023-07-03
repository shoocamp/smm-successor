from datetime import timedelta, datetime
from typing import Optional, Annotated

from fastapi import Depends
from fastapi import HTTPException
from fastapi.security import OAuth2PasswordBearer
from jose import jwt, JWTError
from passlib.context import CryptContext
from starlette import status

from smm_successor.config import CONFIG
from smm_successor.db import Storage
from smm_successor.models.user import BaseUser, TokenData

PWD_CONTEXT = CryptContext(schemes=["bcrypt"], deprecated="auto")
SECRET_KEY = CONFIG['auth']['secret_key']
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_DAYS = 30

storage = Storage(connection_uri=CONFIG["database"]["uri"])
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/users/signin")


def get_current_user(token: Annotated[str, Depends(oauth2_scheme)]) -> BaseUser:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
        token_data = TokenData(username=username)
    except JWTError:
        raise credentials_exception
    user = storage.get_user_by_name(token_data.username)
    if user is None:
        raise credentials_exception
    return user


def verify_password(plain_password, hashed_password) -> bool:
    return PWD_CONTEXT.verify(plain_password, hashed_password)


def get_password_hash(password) -> str:
    return PWD_CONTEXT.hash(password)


def authenticate_user(username: str, password: str) -> Optional[BaseUser]:
    hashed_password = storage.get_user_hashed_password(username)
    if not hashed_password:
        return None
    if not verify_password(password, hashed_password):
        return None
    user = storage.get_user_by_name(username)
    return user


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt
