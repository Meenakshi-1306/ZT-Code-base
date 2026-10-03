from fastapi import Depends, HTTPException, status

from sqlalchemy.orm import Session

from app.database.database import get_db
from app.models.user import User
from app.core.security import decode_access_token
from app.services.rbac_service import RBACService


from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

security = HTTPBearer()


from fastapi import Depends, HTTPException
from sqlalchemy.orm import Session
import jwt

from app.database.database import get_db
from app.models.user import User
from app.core.security import decode_access_token

from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials


security = HTTPBearer()


def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db)
):
    token = credentials.credentials

    try:
        payload = decode_access_token(token)

    except jwt.ExpiredSignatureError:
        raise HTTPException(
            status_code=401,
            detail="Token has expired"
        )

    except jwt.InvalidTokenError:
        raise HTTPException(
            status_code=401,
            detail="Invalid authentication token"
        )

    user_id = payload.get("sub")

    if not user_id:
        raise HTTPException(
            status_code=401,
            detail="Invalid authentication token"
        )

    user = (
        db.query(User)
        .filter(
            User.id == user_id,
            User.status == "active"
        )
        .first()
    )

    if not user:
        raise HTTPException(
            status_code=401,
            detail="User not found or inactive"
        )

    return user


def require_permission(permission_name: str):

    def permission_dependency(
        current_user: User = Depends(get_current_user),
        db: Session = Depends(get_db)
    ) -> User:

        organization_id = getattr(
            current_user,
            "current_organization_id",
            None
        )

        if not organization_id and current_user.organization_members:
            organization_id = current_user.organization_members[0].organization_id

        if not organization_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="User is not associated with an organization"
            )

        has_permission = RBACService.user_has_permission(
            db=db,
            user_id=current_user.id,
            organization_id=organization_id,
            permission_name=permission_name
        )

        if not has_permission:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Permission required: {permission_name}"
            )

        return current_user

    return permission_dependency