from datetime import datetime, timedelta
from typing import Any, Union
import jwt
import bcrypt
from app.core.config import settings

SECRET_KEY = getattr(settings, "SECRET_KEY", "b336ef10bd65a9dbfa4f5f5e2270940cc2bf6cd5d781b2bf1d1cc6d013ac2441")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60 * 24 * 7 # 7 days token

def verify_password(plain_password: str, hashed_password: str) -> bool:
    if len(plain_password) > 71:
        plain_password = plain_password[:71]
    return bcrypt.checkpw(plain_password.encode('utf-8'), hashed_password.encode('utf-8'))

def get_password_hash(password: str) -> str:
    if len(password) > 71:
        password = password[:71]
    salt = bcrypt.gensalt()
    return bcrypt.hashpw(password.encode('utf-8'), salt).decode('utf-8')

def create_access_token(subject: Union[str, Any], expires_delta: timedelta = None) -> str:
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode = {"exp": expire, "sub": str(subject)}
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt
