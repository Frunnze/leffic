from fastapi import APIRouter, Depends, status, Response, HTTPException, Request
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
import traceback
import jwt

from ..schemas import (
    UserCreate, UserLogin
)
from ..models import User
from ..database import get_db
from ..tools.access import (
    create_access_token, create_refresh_token,
    hash_password, verify_password, SECRET_KEY, ALGORITHM
)


auth = APIRouter()

@auth.post("/sign-up")
def register_user(user: UserCreate, response: Response, db: Session = Depends(get_db)):
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
        db_user = User(
            username=user.username, 
            email=user.email, 
            hashed_password=hashed_password
        )
        db.add(db_user)
        db.commit()
        db.refresh(db_user)

        # Generate JWT tokens
        access_token = create_access_token(data={"user_id": str(db_user.id), "iss": "my-issuer"})
        refresh_token = create_refresh_token(data={"user_id": str(db_user.id), "iss": "my-issuer"})

        # Set the refresh token in the HTTP-only cookie
        response.set_cookie(
            key="refresh_token",
            value=refresh_token,
            httponly=True,  # Prevent JavaScript access
            secure=False,    # Set to True in production (only for HTTPS)
            samesite="Strict",  # Adjust depending on your needs (Lax, Strict, None)
        )

        # Return response with tokens and user
        return {
            "user_id": str(db_user.id),
            "username": db_user.username,
            "email": db_user.email,
            "access_token": access_token
        }
    except Exception as e:
        traceback.print_exc()
        db.rollback()
        return JSONResponse(
            status_code=500,
            content={"error": str(e)},
        )


@auth.post("/login")
def login_user(user_login: UserLogin, response: Response, db: Session = Depends(get_db)):
    try:
        # Find user by email
        user = db.query(User).filter(User.email == user_login.email).first()

        if not user:
            return JSONResponse(
                status_code=status.HTTP_404_NOT_FOUND,
                content={"detail": "Incorrect email"}
            )
        
        # Verify password
        if not verify_password(user_login.password, user.hashed_password):
            return JSONResponse(
                status_code=status.HTTP_404_NOT_FOUND,
                content={"detail": "Incorrect password"}
            )

        # Generate tokens
        access_token = create_access_token(data={"user_id": str(user.id), "iss": "my-issuer" })
        refresh_token = create_refresh_token(data={"user_id": str(user.id), "iss": "my-issuer" })

        # Set the refresh token in the HTTP-only cookie
        response.set_cookie(
            key="refresh_token",
            value=refresh_token,
            httponly=True,
            secure=False,
            samesite="Strict",
        )

        return {
            "user_id": str(user.id),
            "username": user.username,
            "email": user.email,
            "access_token": access_token
        }
    except Exception as e:
        traceback.print_exc()
        return JSONResponse(
            status_code=500,
            content={"error": str(e)},
        )


@auth.post("/refresh-token")
def refresh_token(request: Request):
    token = request.cookies.get("refresh_token")
    if not token:
        raise HTTPException(status_code=401, detail="Missing refresh token")

    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id = payload.get("user_id")
        if not user_id:
            raise HTTPException(status_code=401, detail="Invalid token")
    except Exception as e:
        raise HTTPException(status_code=401, detail="Invalid token")

    access_token = create_access_token({"user_id": user_id, "iss": "my-issuer"})

    return {"access_token": access_token, "user_id": user_id}


@auth.post("/logout")
def logout_user(response: Response):
    response.delete_cookie(
        key="refresh_token",
        httponly=True,
        secure=False,  # use True in production
        samesite="Strict",
        path="/"
    )
    response.status_code = status.HTTP_200_OK
    return {"message": "Successfully logged out"}