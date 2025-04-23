from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from fastapi.security import OAuth2PasswordBearer
import traceback

from ..schemas import (
    UserResponse, UserCreate, UserLogin
)
from ..models import User
from ..tools.hash import hash_password, verify_password
from ..database import get_db
from .. import oauth2_scheme


auth = APIRouter()


@auth.post("/sign-up/", response_model=UserResponse)
def register_user(user: UserCreate, db: Session = Depends(get_db)):
    try:
        # Check if username or email already exists
        if db.query(User).filter(User.username == user.username).first():
            return JSONResponse(
                status_code=status.HTTP_409_CONFLICT, 
                content="Username already registered"
            )

        if db.query(User).filter(User.email == user.email).first():
            return JSONResponse(
                status_code=status.HTTP_409_CONFLICT, 
                content="Email already registered"
            )

        # Create new user
        hashed_password = hash_password(user.password)
        db_user = User(username=user.username, email=user.email, hashed_password=hashed_password)

        db.add(db_user)
        db.commit()
        db.refresh(db_user)
        return db_user
    except Exception as e:
        traceback.print_exc()
        db.rollback()
        return JSONResponse(
            status_code=500,
            content={"error": str(e)},
        )


@auth.post("/login/")
def login_user(user_login: UserLogin, db: Session = Depends(get_db)):
    try:
        # Find user by username or email
        user = db.query(User).filter(User.email == user_login.email).first()
        
        if not user or not verify_password(user_login.password, user.hashed_password):
            return JSONResponse(
                status_code=status.HTTP_401_UNAUTHORIZED,
                content="Incorrect email or password",
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        return {"msg": "Login successful"}
    except Exception as e:
        traceback.print_exc()
        return JSONResponse(
            status_code=500,
            content={"error": str(e)},
        )
    


@auth.post("/login/")
def login_user(user_login: UserLogin, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == user_login.email).first()
    
    if not user or not verify_password(user_login.password, user.hashed_password):
        return JSONResponse(status_code=status.HTTP_401_UNAUTHORIZED,
            content="Incorrect email or password")
    
    return {"msg": "Login successful"}