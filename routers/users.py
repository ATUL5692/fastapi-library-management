# This file is for handling users part.

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

import crud
import schemas
import models
from database import get_db
from security import (
    get_current_user,
    admin_only,
    super_admin_only,
    verify_password,
    hash_password
)

router = APIRouter(prefix="/user", tags=["Users"])


# =========================
# GET CURRENT USER (ME)
# =========================
@router.get("/me", response_model=schemas.UserResponse)
def get_me(
    current_user: models.User = Depends(get_current_user)
):
    return current_user


# =========================
# GET USERS (ROLE-BASED) ✅ FIXED
# =========================
@router.get("/", response_model=List[schemas.UserResponse])
def get_users(
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    # 🔥 normalize role (critical fix)
    role = (current_user.role or "").lower().strip()

    if role in ["admin", "super_admin"]:
        return crud.get_users(db)

    return [current_user]


# =========================
# GET USER BY ID
# =========================
@router.get("/{user_id}", response_model=schemas.UserResponse)
def get_user(
    user_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    user = crud.get_user(db, user_id)

    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    return user


# =========================
# UPDATE NAME
# =========================
@router.put("/me/name")
def update_name(
    data: schemas.UpdateName,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    current_user.name = data.name
    db.commit()
    return {"message": "Name updated successfully"}


# =========================
# UPDATE EMAIL
# =========================
@router.put("/me/email")
def update_email(
    data: schemas.UpdateEmail,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    existing = db.query(models.User).filter(
        models.User.email == data.email,
        models.User.id != current_user.id
    ).first()

    if existing:
        raise HTTPException(status_code=400, detail="Email already exists")

    current_user.email = data.email
    db.commit()

    return {"message": "Email updated successfully"}


# =========================
# UPDATE PHONE
# =========================
@router.put("/me/phone")
def update_phone(
    data: schemas.UpdatePhone,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    existing = db.query(models.User).filter(
        models.User.phone == data.phone,
        models.User.id != current_user.id
    ).first()

    if existing:
        raise HTTPException(status_code=400, detail="Phone already exists")

    current_user.country_code = data.country_code
    current_user.phone = data.phone

    db.commit()

    return {"message": "Phone updated successfully"}


# =========================
# CHANGE PASSWORD
# =========================
@router.put("/me/password")
def change_password(
    data: schemas.ChangePassword,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    if not verify_password(data.old_password, current_user.password):
        raise HTTPException(status_code=400, detail="Incorrect old password")

    current_user.password = hash_password(data.new_password)
    db.commit()

    return {"message": "Password updated successfully"}


# =========================
# DELETE USER (ADMIN ONLY)
# =========================
@router.delete("/{user_id}")
def delete_user(
    user_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(admin_only)
):
    user = db.query(models.User).filter(
        models.User.id == user_id
    ).first()

    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    if (user.role or "").lower() == "super_admin":
        raise HTTPException(status_code=400, detail="Cannot delete super admin")

    if current_user.id == user_id:
        raise HTTPException(status_code=400, detail="Admin cannot delete themselves")

    active_transaction = db.query(models.Transaction).filter(
        models.Transaction.user_id == user_id,
        models.Transaction.status == "issued"
    ).first()

    if active_transaction:
        raise HTTPException(
            status_code=400,
            detail="User has active borrowed books"
        )

    db.delete(user)
    db.commit()

    return {
        "message": "User deleted successfully",
        "user_id": user_id
    }


# =========================
# PROMOTE TO ADMIN (SUPER ADMIN ONLY)
# =========================
@router.put("/make-admin/{user_id}")
def make_admin(
    user_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(super_admin_only)
):
    user = db.query(models.User).filter(models.User.id == user_id).first()

    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    if (user.role or "").lower() == "super_admin":
        raise HTTPException(status_code=400, detail="Already super admin")

    user.role = "admin"
    db.commit()

    return {"message": f"User {user_id} promoted to admin"}


# =========================
# TRANSFER SUPER ADMIN
# =========================
@router.put("/transfer-super-admin/{user_id}")
def transfer_super_admin(
    user_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(super_admin_only)
):
    new_admin = db.query(models.User).filter(models.User.id == user_id).first()

    if not new_admin:
        raise HTTPException(status_code=404, detail="User not found")

    if new_admin.id == current_user.id:
        raise HTTPException(status_code=400, detail="Already super admin")

    current_user.role = "admin"
    new_admin.role = "super_admin"

    db.commit()

    return {"message": f"Super admin transferred to user {user_id}"}