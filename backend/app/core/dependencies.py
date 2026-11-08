"""
app/core/dependencies.py
------------------------
FastAPI dependencies shared across routers, including JWT-based auth.
"""

from __future__ import annotations

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.orm import Session

from app.core.security import decode_access_token
from app.database.connection import get_db
from app.models.user import User

_bearer_scheme = HTTPBearer(auto_error=True)


def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(_bearer_scheme),
    db: Session = Depends(get_db),
) -> User:
    """Extract the JWT from the ``Authorization: Bearer <token>`` header,
    validate it, and return the corresponding :class:`~app.models.user.User`.

    Raises
    ------
    HTTPException
        401 if the token is missing, malformed, expired, or the user does not
        exist / is inactive.
    """
    _credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    token = credentials.credentials
    payload = decode_access_token(token)
    if payload is None:
        raise _credentials_exception

    email: str | None = payload.get("sub")
    if not email:
        raise _credentials_exception

    user: User | None = db.query(User).filter(User.email == email).first()
    if user is None:
        raise _credentials_exception

    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Inactive user account",
        )

    return user


def get_current_admin(current_user: User = Depends(get_current_user)) -> User:
    """Like :func:`get_current_user` but additionally requires the ``admin`` role."""
    if current_user.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Administrator privileges required",
        )
    return current_user
