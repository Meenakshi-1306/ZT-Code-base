from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from app.database.database import get_db
from app.models.user import User
from app.core.security import verify_password, create_access_token
from app.schemas.auth import LoginResponse
from app.schemas.common import APIResponse

router = APIRouter(
    prefix="/api/auth",
    tags=["Authentication"]
)


@router.post("/login", response_model=APIResponse[LoginResponse])
def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db)
):

    user = (
        db.query(User)
        .filter(
            User.email == form_data.username,
            User.status == "active"
        )
        .first()
    )

    if not user:
        raise HTTPException(
            status_code=401,
            detail="Invalid email or password"
        )

    if not verify_password(
        form_data.password,
        user.password_hash
    ):
        raise HTTPException(
            status_code=401,
            detail="Invalid email or password"
        )

    if not user.organization_members:
        raise HTTPException(
            status_code=403,
            detail="User is not associated with an organization"
        )

    organization_id = user.organization_members[0].organization_id

    access_token = create_access_token(
        user_id=user.id,
        organization_id=organization_id
    )

    return {
        "success": True,
        "data": {
            "access_token": access_token,
            "token_type": "bearer"
        },
        "message": "Login successful"
    }
