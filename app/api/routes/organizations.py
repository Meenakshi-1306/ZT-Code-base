from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
    status,
    File,
    Form,
    UploadFile,
)

from sqlalchemy.orm import Session

from app.database.database import get_db
from app.core.dependencies import require_permission

from app.controllers.organization_controller import OrganizationController

from app.schemas.common import APIResponse

from app.schemas.organization import (
    OrganizationDetailsResponse,
    OrganizationSettingsResponse,
    OrganizationUpdateRequest,
    OrganizationVerificationResponse,
)

from app.schemas.organization_registration import (
    OrganizationRegistrationRequest,
    OrganizationRegistrationResponse,
    OTPVerifyRequest,
    OTPVerifyResponse,
    OTPResendRequest,
    OTPResendResponse,
)

from app.schemas.organization_verification import (
    OrganizationVerificationRequest,
)


router = APIRouter(
    prefix="/api/organizations",
    tags=["Organizations"],
)


@router.get("", summary="List organizations")
def list_organizations(db: Session = Depends(get_db)):
    from app.models.organization import Organization
    orgs = db.query(Organization).all()
    return {
        "success": True,
        "organizations": [
            {
                "id": org.id,
                "name": org.name,
                "slug": org.slug,
                "domain": org.domain,
                "status": org.status
            }
            for org in orgs
        ]
    }


@router.post("", summary="Create organization")
def create_organization(request: dict, db: Session = Depends(get_db)):
    from app.models.organization import Organization
    import uuid
    org_id = f"ORG_{uuid.uuid4().hex[:6].upper()}"
    org = Organization(
        id=org_id,
        name=request.get("name", "New Organization"),
        slug=request.get("name", "new-org").lower().replace(" ", "-"),
        domain=request.get("domain", "example.com"),
        status="active"
    )
    db.add(org)
    db.commit()
    db.refresh(org)
    return {
        "success": True,
        "id": org.id,
        "name": org.name,
        "domain": org.domain,
        "message": "Organization created successfully"
    }


@router.get("/{organization_id}/teams", summary="List organization teams")
def list_org_teams(organization_id: str, db: Session = Depends(get_db)):
    from app.models.team import Team
    teams = db.query(Team).filter(Team.organization_id == organization_id).all()
    return {
        "success": True,
        "teams": [
            {
                "id": t.id,
                "name": t.name,
                "description": t.description,
                "status": t.status
            }
            for t in teams
        ]
    }


@router.post("/{organization_id}/teams", summary="Create organization team")
def create_org_team(organization_id: str, request: dict, db: Session = Depends(get_db)):
    from app.models.team import Team
    import uuid
    team_id = f"TEAM_{uuid.uuid4().hex[:6].upper()}"
    team = Team(
        id=team_id,
        organization_id=organization_id,
        name=request.get("name", "New Team"),
        description=request.get("description", "Team Description"),
        status="active"
    )
    db.add(team)
    db.commit()
    db.refresh(team)
    return {
        "success": True,
        "id": team.id,
        "name": team.name,
        "message": "Team created successfully"
    }


@router.get("/{organization_id}/projects", summary="List organization projects")
def list_org_projects(organization_id: str, db: Session = Depends(get_db)):
    return {
        "success": True,
        "projects": [
            {
                "id": "PROJ_001",
                "name": "Zero Trust Security Pipeline",
                "description": "Real-time threat monitoring",
                "status": "ACTIVE"
            }
        ]
    }


@router.post("/{organization_id}/projects", summary="Create organization project")
def create_org_project(organization_id: str, request: dict, db: Session = Depends(get_db)):
    import uuid
    proj_id = f"PROJ_{uuid.uuid4().hex[:6].upper()}"
    return {
        "success": True,
        "id": proj_id,
        "name": request.get("name", "New Project"),
        "description": request.get("description", "Project Description"),
        "message": "Project created successfully"
    }


# ============================================================
# MODULE 1 - ORGANIZATION REGISTRATION
# ============================================================

@router.post(
    "/register",
    response_model=OrganizationRegistrationResponse,
    summary="Register a new organization",
)
def register_organization(
    request: OrganizationRegistrationRequest,
    db: Session = Depends(get_db),
):
    try:
        result = OrganizationController.create_organization(
            db=db,
            organization_data=request.model_dump(),
        )

        organization = result["organization"]

        return {
            "organization_id": organization.id,
            "organization_name": organization.name,
            "email": organization.contact_email,
            "email_domain": organization.email_domain,
            "verification_status": organization.verification_status,
            "email_verified": organization.email_verified,
            "message": (
                "Organization registered successfully. "
                "Please verify your email using the OTP."
            ),
            "development_otp": result["otp"],
        }

    except ValueError as exc:
        raise HTTPException(
            status_code=400,
            detail=str(exc),
        )


# ============================================================
# MODULE 1 - EMAIL OTP VERIFICATION
# ============================================================

@router.post(
    "/verify-email",
    response_model=OTPVerifyResponse,
    summary="Verify organization email using OTP",
)
def verify_organization_email(
    request: OTPVerifyRequest,
    db: Session = Depends(get_db),
):
    try:
        return OrganizationController.verify_organization_email(
            db=db,
            organization_id=request.organization_id,
            otp=request.otp,
        )

    except ValueError as exc:
        message = str(exc)

        if message == "Organization not found":
            status_code = 404

        elif "expired" in message.lower():
            status_code = 400

        elif "maximum" in message.lower():
            status_code = 429

        else:
            status_code = 400

        raise HTTPException(
            status_code=status_code,
            detail=message,
        )


# ============================================================
# MODULE 1 - RESEND OTP
# ============================================================

@router.post(
    "/resend-otp",
    response_model=OTPResendResponse,
    summary="Resend organization email OTP",
)
def resend_organization_otp(
    request: OTPResendRequest,
    db: Session = Depends(get_db),
):
    try:
        return OrganizationController.resend_organization_otp(
            db=db,
            organization_id=request.organization_id,
        )

    except ValueError as exc:
        message = str(exc)

        if message == "Organization not found":
            status_code = 404

        elif "wait" in message.lower():
            status_code = 429

        elif "already verified" in message.lower():
            status_code = 400

        else:
            status_code = 400

        raise HTTPException(
            status_code=status_code,
            detail=message,
        )


# ============================================================
# MODULE 1 - SUBMIT ORGANIZATION VERIFICATION
# ============================================================

@router.post(
    "/{organization_id}/verification",
    response_model=OrganizationVerificationResponse,
    summary="Submit organization verification",
)
def submit_organization_verification(
    organization_id: str,
    request: OrganizationVerificationRequest,
    db: Session = Depends(get_db),
):
    try:
        result = OrganizationController.submit_verification(
            db=db,
            organization_id=organization_id,
            verification_data=request.model_dump(),
        )

        return result

    except ValueError as exc:
        message = str(exc)

        if message == "Organization not found":
            status_code = 404

        elif "Email must be verified" in message:
            status_code = 400

        else:
            status_code = 400

        raise HTTPException(
            status_code=status_code,
            detail=message,
        )


# ============================================================
# MODULE 1 - UPLOAD VERIFICATION DOCUMENT
# ============================================================

@router.post(
    "/verification/document",
    summary="Upload organization verification document",
)
async def upload_verification_document(
    organization_id: str = Form(...),
    document_type: str = Form(...),
    document: UploadFile = File(...),
    db: Session = Depends(get_db),
):
    try:
        result = await OrganizationController.upload_verification_document(
            db=db,
            organization_id=organization_id,
            document_type=document_type,
            document=document,
        )

        return {
            "success": True,
            "data": result,
            "message": "Verification document uploaded successfully",
        }

    except ValueError as exc:
        raise HTTPException(
            status_code=400,
            detail=str(exc),
        )


# ============================================================
# ORGANIZATION DETAILS
# ============================================================

@router.get(
    "/{organization_id}",
    response_model=APIResponse[OrganizationDetailsResponse],
    summary="Get organization details",
)
def get_organization(
    organization_id: str,
    db: Session = Depends(get_db),
    current_user=Depends(require_permission("ORG_VIEW")),
):
    try:
        data = OrganizationController.get_organization(
            db=db,
            organization_id=organization_id,
            current_user=current_user,
        )

        return {
            "success": True,
            "data": data,
            "message": "Organization retrieved successfully",
        }

    except ValueError as exc:
        status_code = (
            404
            if str(exc) == "Organization not found"
            else 403
        )

        raise HTTPException(
            status_code=status_code,
            detail=str(exc),
        )


# ============================================================
# UPDATE ORGANIZATION
# ============================================================

@router.patch(
    "/{organization_id}",
    response_model=APIResponse[OrganizationDetailsResponse],
    summary="Update organization profile",
)
def update_organization(
    organization_id: str,
    request: OrganizationUpdateRequest,
    db: Session = Depends(get_db),
    current_user=Depends(require_permission("ORG_UPDATE")),
):
    try:
        data = OrganizationController.update_organization(
            db=db,
            organization_id=organization_id,
            request=request,
            current_user=current_user,
        )

        return {
            "success": True,
            "data": data,
            "message": "Organization updated successfully",
        }

    except ValueError as exc:
        status_code = (
            404
            if str(exc) == "Organization not found"
            else 403
        )

        raise HTTPException(
            status_code=status_code,
            detail=str(exc),
        )


# ============================================================
# ORGANIZATION SETTINGS - GET
# ============================================================

@router.get(
    "/{organization_id}/settings",
    response_model=APIResponse[OrganizationSettingsResponse],
    summary="Get organization settings",
)
def get_organization_settings(
    organization_id: str,
    db: Session = Depends(get_db),
    current_user=Depends(require_permission("ORG_SETTINGS_VIEW")),
):
    try:
        data = OrganizationController.get_settings(
            db=db,
            organization_id=organization_id,
            current_user=current_user,
        )

        return {
            "success": True,
            "data": data,
            "message": "Organization settings retrieved successfully",
        }

    except ValueError as exc:
        status_code = (
            404
            if str(exc) == "Organization not found"
            else 403
        )

        raise HTTPException(
            status_code=status_code,
            detail=str(exc),
        )


# ============================================================
# ORGANIZATION SETTINGS - UPDATE
# ============================================================

@router.put(
    "/{organization_id}/settings",
    summary="Update organization settings",
)
def update_organization_settings(
    organization_id: str,
    request: dict,
    db: Session = Depends(get_db),
    current_user=Depends(require_permission("ORG_UPDATE")),
):
    try:
        data = OrganizationController.update_settings(
            db=db,
            organization_id=organization_id,
            request=request,
            current_user=current_user,
        )

        return {
            "success": True,
            "data": data,
            "message": "Organization settings updated successfully",
        }

    except ValueError as exc:
        status_code = (
            404
            if str(exc) == "Organization not found"
            else 403
        )

        raise HTTPException(
            status_code=status_code,
            detail=str(exc),
        )


# ============================================================
# ORGANIZATION VERIFICATION STATUS
# ============================================================

@router.get(
    "/{organization_id}/verification",
    response_model=APIResponse[OrganizationVerificationResponse],
    summary="Get organization verification status",
)
def get_organization_verification(
    organization_id: str,
    db: Session = Depends(get_db),
    current_user=Depends(
        require_permission("ORG_VERIFICATION_VIEW")
    ),
):
    try:
        data = OrganizationController.get_verification(
            db=db,
            organization_id=organization_id,
            current_user=current_user,
        )

        return {
            "success": True,
            "data": data,
            "message": "Organization verification retrieved successfully",
        }

    except ValueError as exc:
        status_code = (
            404
            if str(exc) == "Organization not found"
            else 403
        )

        raise HTTPException(
            status_code=status_code,
            detail=str(exc),
        )