from passlib.context import CryptContext
from jose import JWTError, jwt
from datetime import datetime, timedelta
from fastapi import Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session

from database import get_db
import models


# =========================
# PASSWORD HASHING
# =========================
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def hash_password(password: str):
    return pwd_context.hash(password[:72])


def verify_password(plain_password: str, hashed_password: str):
    return pwd_context.verify(plain_password[:72], hashed_password)


# =========================
# JWT CONFIG
# =========================
SECRET_KEY = "REPLACE_WITH_RANDOM_64_CHAR_SECRET"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60


# =========================
# CREATE TOKEN
# =========================
def create_access_token(data: dict):
    to_encode = data.copy()

    expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})

    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)


# =========================
# AUTH SCHEME (FIXED)
# =========================
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/login")


# =========================
# GET CURRENT USER (FIXED)
# =========================
def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db)
):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])

        user_data = payload.get("sub")

        # ✅ HANDLE BOTH TOKEN FORMATS
        if isinstance(user_data, dict):
            user_id = user_data.get("sub")
        else:
            user_id = user_data

        if user_id is None:
            raise HTTPException(status_code=401, detail="Invalid token")

    except JWTError:
        raise HTTPException(status_code=401, detail="Token expired or invalid")

    user = db.query(models.User).filter(models.User.id == int(user_id)).first()

    if not user:
        raise HTTPException(status_code=401, detail="User not found")

    return user


# =========================
# ROLE-BASED ACCESS CONTROL
# =========================
def super_admin_only(user: models.User = Depends(get_current_user)):
    if user.role != "super_admin":
        raise HTTPException(status_code=403, detail="Super Admin only")
    return user


def admin_only(user: models.User = Depends(get_current_user)):
    if user.role not in ["admin", "super_admin"]:
        raise HTTPException(status_code=403, detail="Admin only")
    return user


def user_only(user: models.User = Depends(get_current_user)):
    return user