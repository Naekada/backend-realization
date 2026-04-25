from datetime import datetime, timezone, timedelta
from core.settings import settings
from jose import jwt, JWTError
from passlib.context import CryptContext
import bcrypt


pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# ==================== Хэширование паролей - Start =================== #
def hash_password(password: str) -> str:
    password_bytes = password.encode("utf-8")
    salt = bcrypt.gensalt()
    hashed = bcrypt.hashpw(password_bytes, salt)
    return hashed.decode("utf-8")



def verify_password(plain_password: str, hashed_password: str) -> bool:
    plain_bytes = plain_password.encode("utf-8")
    hashed_bytes = hashed_password.encode("utf-8")

    try:
        return bcrypt.checkpw(plain_bytes, hashed_bytes)
    except ValueError:
        return False
# ==================== Хэширование паролей - End ==================== # 


# ==================== Токены - Start =================== #
def create_access_token(
        data: dict, 
        expire_time: timedelta | None = None
) -> str:
    if expire_time:
        expire = datetime.now(timezone.utc) + expire_time
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=settings.jwt_access_token_expire_minutes)

    to_encode = data.copy()
    to_encode.update({"exp": expire, "type": "access"})
    encoded_jwt = jwt.encode(to_encode, settings.jwt_secret_key, settings.jwt_algorithm)

    return encoded_jwt


def create_refresh_token(
        data: dict
):
    expire = datetime.now(timezone.utc) + timedelta(days=settings.jwt_access_token_expire_days)
    to_encode = data.copy()
    to_encode.update({"exp": expire, "type": "refresh"})
    encoded_refresh_jwt = jwt.encode(to_encode, settings.jwt_secret_key, settings.jwt_algorithm)
    return encoded_refresh_jwt


def decode_access_token(token: str) -> dict | None:
    try: 
        payload = jwt.decode(token, settings.jwt_secret_key, settings.jwt_algorithm)
        if payload.get("type") == "refresh":
            return None
        return payload
    except JWTError:
        return None
    

def decode_refresh_token(token: str) -> dict | None:
    try:
        payload = jwt.decode(token, settings.jwt_secret_key, settings.jwt_algorithm)
        if payload.get("type") != "refresh":
            return None
        return payload
    except JWTError:
        return None
# ==================== Токены - End =================== #

