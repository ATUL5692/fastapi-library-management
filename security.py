from passlib.context import CryptContext
from jose import JWTError, jwt
from datetime import datetime, timedelta
from fastapi import Depends, HTTPException
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
import hashlib
import os

from database import get_db
import models


# =========================
# PASSWORD HASHING
# =========================
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def hash_password(password: str):
    # Step 1: Normalize password length (fix bcrypt limit)
    hashed_input = hashlib.sha256(password.encode("utf-8")).hexdigest()

    # Step 2: bcrypt hash
    return pwd_context.hash(hashed_input)


def verify_password(plain_password: str, hashed_password: str):
    hashed_input = hashlib.sha256(plain_password.encode("utf-8")).hexdigest()
    return pwd_context.verify(hashed_input, hashed_password)


# =========================
# JWT CONFIG
# =========================
SECRET_KEY = os.getenv("SECRET_KEY", "dev-secret-key")
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
# AUTH SCHEME (CLEAN)
# =========================
security = HTTPBearer()


# =========================
# GET CURRENT USER
# =========================
def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db)
):
    token = credentials.credentials

    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])

        user_id = payload.get("sub")

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