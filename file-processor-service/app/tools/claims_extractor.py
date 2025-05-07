import jwt
from typing import Optional
from fastapi import Header, HTTPException


def get_user_id_from_jwt(
    authorization: Optional[str] = Header(None)
) -> str:
    try:
        scheme, token = authorization.split()
        if scheme.lower() != "bearer":
            raise ValueError("Invalid auth scheme")

        payload = jwt.decode(token, options={"verify_signature": False})
        return payload.get("user_id")
    except Exception as e:
        raise HTTPException(status_code=401, detail=f"Invalid token: {str(e)}")