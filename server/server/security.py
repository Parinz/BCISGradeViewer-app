from datetime import datetime, timedelta

from fastapi import Depends
from fastapi.security import OAuth2PasswordBearer
from jose import jwt, JWTError
from pydantic import BaseModel
from cryptography.fernet import Fernet

from .config import ACCESS_TOKEN_EXPIRE_DAYS, ALGORITHM, SECRET_KEY, FERNET_KEY
from .exceptions import CredentialsException

# Depends on the oauth scheme
oauthScheme = OAuth2PasswordBearer(tokenUrl="token")

# Create Fernet class used in server/sql/crud.py
encryptor = Fernet(FERNET_KEY)

# Create a user class for oauth
class OauthUser(BaseModel):
    username: str


# Oauth, gets current user by jwt decoding.
async def get_current_user(token: str = Depends(oauthScheme)):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
    except JWTError:
        raise CredentialsException
    username: str = payload.get("sub")
    student: bool = payload.get("student")
    return {"username": username, "student": student}


# Create access JWT
def create_access_token(data: dict):
    # Create shallow copy of data
    toEncode = data.copy()

    # Set expiry date, if not none.
    if ACCESS_TOKEN_EXPIRE_DAYS:
        expire = datetime.utcnow() + timedelta(days=ACCESS_TOKEN_EXPIRE_DAYS)
        toEncode.update({"exp": expire})
    encodedJWT = jwt.encode(toEncode, SECRET_KEY, algorithm=ALGORITHM)
    return encodedJWT
