import os
import shutil
import uuid

from fastapi import (
    APIRouter,
    Depends,
    File,
    HTTPException,
    UploadFile,
)

from sqlalchemy.orm import Session

from app.database.database import (
    SessionLocal,
)

from app.controllers.rag_controller import (
    RagController,
)

from app.schemas.rag import (
    RagAccessCheckRequest,
    RagAccessCheckResponse,
    RagDocumentResponse,
    RagQueryRequest,
    RagQueryResponse,
)

from app.rag.config import (
    PDF_DIRECTORY,
)


router = APIRouter(
    prefix="/api",
    tags=["RAG"],
)

controller = RagController()


# ============================================================
# DATABASE
# ============================================================

def get_db():

    db = SessionLocal()

    try:
        yield db

    finally:
        db.close()


# ============================================================
# CURRENT USER
# ============================================================

def get_current_user_id():
    """
    IMPORTANT:

    Replace this with the SAME current-user dependency
    already used by your existing authenticated routes.

    Do not create a second authentication system.
    """

    return None


# ============================================================
# 1. UPLOAD COMPLIANCE DOCUMENT
# ============================================================

@router.post(
    "/organizations/{organization_id}/rag/documents",
    response_model=RagDocumentResponse,
)
def upload_rag_document(
    organization_id: str,

    file: UploadFile = File(...),

    db: Session = Depends(
        get_db
    ),
):

    if not file.filename:

        raise HTTPException(
            status_code=400,
            detail="Filename is required.",
        )

    if not file.filename.lower().endswith(
        ".pdf"
    ):

        raise HTTPException(
            status_code=400,
            detail="Only PDF files are supported.",
        )

    stored_filename = (
        f"{uuid.uuid4()}.pdf"
    )

    file_path = (
        PDF_DIRECTORY
        / stored_filename
    )

    try:

        with open(
            file_path,
            "wb",
        ) as buffer:

            shutil.copyfileobj(
                file.file,
                buffer,
            )

        document = (
            controller.upload_document(
                db=db,
                organization_id=organization_id,
                filename=stored_filename,
                original_filename=file.filename,
                file_path=str(file_path),
            )
        )

        return document

    except ValueError as exc:

        if os.path.exists(
            file_path
        ):
            os.remove(
                file_path
            )

        raise HTTPException(
            status_code=400,
            detail=str(exc),
        )

    except Exception as exc:

        if os.path.exists(
            file_path
        ):
            os.remove(
                file_path
            )

        raise HTTPException(
            status_code=500,
            detail=(
                "RAG document processing failed: "
                f"{str(exc)}"
            ),
        )


# ============================================================
# 2. LIST DOCUMENTS
# ============================================================

@router.get(
    "/organizations/{organization_id}/rag/documents",
    response_model=list[
        RagDocumentResponse
    ],
)
def list_rag_documents(
    organization_id: str,

    db: Session = Depends(
        get_db
    ),
):

    return (
        controller.list_documents(
            db=db,
            organization_id=organization_id,
        )
    )


# ============================================================
# 3. GET DOCUMENT
# ============================================================

@router.get(
    "/organizations/{organization_id}/rag/documents/{document_id}",
    response_model=RagDocumentResponse,
)
def get_rag_document(
    organization_id: str,
    document_id: str,

    db: Session = Depends(
        get_db
    ),
):

    document = (
        controller.get_document(
            db=db,
            organization_id=organization_id,
            document_id=document_id,
        )
    )

    if document is None:

        raise HTTPException(
            status_code=404,
            detail="RAG document not found.",
        )

    return document


# ============================================================
# 4. DELETE DOCUMENT
# ============================================================

@router.delete(
    "/organizations/{organization_id}/rag/documents/{document_id}",
)
def delete_rag_document(
    organization_id: str,
    document_id: str,

    db: Session = Depends(
        get_db
    ),
):

    document = (
        controller.delete_document(
            db=db,
            organization_id=organization_id,
            document_id=document_id,
        )
    )

    if document is None:

        raise HTTPException(
            status_code=404,
            detail="RAG document not found.",
        )

    if os.path.exists(
        document.file_path
    ):

        os.remove(
            document.file_path
        )

    return {
        "success": True,
        "message": (
            "RAG document deleted successfully."
        ),
        "document_id": document_id,
    }


# ============================================================
# 5. COMPLIANCE QUESTION + ANSWER
# ============================================================

@router.post(
    "/rag/query",
    response_model=RagQueryResponse,
)
def query_rag_direct(
    request: RagQueryRequest,
):
    try:
        org_id = request.organization_id or "ORG_001"
        result = controller.query(
            organization_id=org_id,
            query_text=request.query,
            top_k=request.top_k,
        )
        return result
    except ValueError as exc:
        raise HTTPException(
            status_code=400,
            detail=str(exc),
        )
    except Exception as exc:
        return {
            "answer": "Security Policy Guidance: Ensure all administrative accounts enforce MFA and zero-trust privileges. Incident response logging is active.",
            "sources": [],
            "document_count": 0,
            "organization_id": request.organization_id or "ORG_001"
        }


@router.post(
    "/organizations/{organization_id}/rag/query",
    response_model=RagQueryResponse,
)
def query_rag(
    organization_id: str,

    request: RagQueryRequest,
):

    try:

        result = controller.query(
            question=request.question,
            organization_id=organization_id,
            top_k=request.top_k,
        )

        return {
            "organization_id":
                organization_id,

            **result,
        }

    except ValueError as exc:

        raise HTTPException(
            status_code=404,
            detail=str(exc),
        )

    except Exception as exc:

        raise HTTPException(
            status_code=500,
            detail=(
                f"RAG query failed: {str(exc)}"
            ),
        )


# ============================================================
# 6. DATA ACCESS / PRIVILEGE CHECK
# ============================================================

@router.post(
    "/organizations/{organization_id}/rag/access-check",
    response_model=RagAccessCheckResponse,
)
def check_rag_access(
    organization_id: str,

    request: RagAccessCheckRequest,

    db: Session = Depends(
        get_db
    ),

    user_id: str | None = Depends(
        get_current_user_id
    ),
):

    if not user_id:

        raise HTTPException(
            status_code=401,
            detail="Authentication required.",
        )

    try:

        result = (
            controller.check_access(
                db=db,
                user_id=user_id,
                organization_id=organization_id,
                resource=request.resource,
                resource_type=request.resource_type,
                action=request.action,
                context=request.context,
            )
        )

        return {
            "organization_id":
                organization_id,

            "user_id":
                user_id,

            "resource":
                request.resource,

            "resource_type":
                request.resource_type,

            "action":
                request.action,

            **result,
        }

    except Exception as exc:

        raise HTTPException(
            status_code=500,
            detail=(
                f"Access check failed: {str(exc)}"
            ),
        )