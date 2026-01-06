from fastapi import APIRouter, Depends, HTTPException, status, Security
from sqlalchemy.orm import Session
from typing import List, Optional
from backend.db.session import get_db
from backend.db.models import User as UserModel, Submission as SubmissionModel
from backend.schemas.submission import SubmissionResponse
from backend.schemas.user import UserResponse
from jose import JWTError, jwt
from datetime import datetime, timedelta
from backend.core.config import settings
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials


router = APIRouter()

# Security scheme for JWT token
security = HTTPBearer()


def get_current_user_from_token(
    credentials: HTTPAuthorizationCredentials = Security(security),
    db: Session = Depends(get_db)
) -> UserResponse:
    """
    Get the current user from JWT token in Authorization header.
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    try:
        token = credentials.credentials
        payload = jwt.decode(token, settings.secret_key, algorithms=[settings.algorithm])
        email: str = payload.get("sub")
        if email is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception
    
    user = db.query(UserModel).filter(UserModel.email == email).first()
    if user is None:
        raise credentials_exception
    return UserResponse(
        id=user.id,
        email=user.email,
        is_active=user.is_active,
        created_at=user.created_at
    )


@router.get("/submissions", response_model=List[SubmissionResponse])
async def get_user_submissions(
    current_user: UserResponse = Depends(get_current_user_from_token),
    db: Session = Depends(get_db)
):
    """
    Get all submissions for the currently authenticated user.
    Returns questionnaire title, completion status, and current step.
    """
    submissions = db.query(SubmissionModel).filter(
        SubmissionModel.user_id == current_user.id
    ).order_by(SubmissionModel.updated_at.desc()).all()
    
    return submissions


@router.get("/submissions/{submission_id}", response_model=SubmissionResponse)
async def get_submission(
    submission_id: int,
    current_user: UserResponse = Depends(get_current_user_from_token),
    db: Session = Depends(get_db)
):
    """
    Get a specific submission by ID.
    """
    submission = db.query(SubmissionModel).filter(
        SubmissionModel.id == submission_id,
        SubmissionModel.user_id == current_user.id
    ).first()
    
    if not submission:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Submission not found"
        )
    
    return submission

