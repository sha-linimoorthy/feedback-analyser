# API endpoints

from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session
from uuid import UUID

"""
Defined REST API endpoints 
- Create, update, and delete feedback forms for events
- Submit attendee feedback responses for a form
- Perform AI-based sentiment analysis on collected feedback
- Retrieve cached sentiment analysis results
"""

from app.database import get_db
from app.schemas import (
    FeedbackFormCreate, FeedbackFormUpdate, FeedbackFormResponse,
    FeedbackResponseCreate, FeedbackResponseResponse,
    SentimentAnalysisResponse
)
from app.services.feedback_service import FeedbackService

router = APIRouter(prefix="/api/v1", tags=["Feedback Management"])

@router.post("/forms", response_model=FeedbackFormResponse, status_code=status.HTTP_201_CREATED)
def create_feedback_form(
    form_data: FeedbackFormCreate,
    db: Session = Depends(get_db)
):
    """
    Create a new feedback form for an event.
    
    - **event_name**: Name of the event (required)
    - **event_date**: Date of the event (optional)
    - **description**: Event description (optional)
    """
    service = FeedbackService(db)
    return service.create_form(form_data)


@router.post("/forms/{form_id}/responses", response_model=FeedbackResponseResponse, status_code=status.HTTP_201_CREATED)
def submit_feedback_response(
    form_id: UUID,
    response_data: FeedbackResponseCreate,
    db: Session = Depends(get_db)
):
    """
    Submit attendee feedback for a specific form.
    
    - **rating**: Rating from 1-5 (required)
    - **comment**: Free-text feedback (optional, max 2000 chars)
    - **attendee_name**: Name of attendee (optional)
    """
    service = FeedbackService(db)
    return service.create_response(form_id, response_data)


@router.post("/forms/{form_id}/analyze", response_model=SentimentAnalysisResponse, status_code=status.HTTP_200_OK)
def analyze_feedback(
    form_id: UUID,
    db: Session = Depends(get_db)
):
    """
    Analyze feedback using Gemini AI.
    
    This endpoint:
    1. Fetches all responses for the form
    2. Calls Gemini API for sentiment analysis
    3. Caches the result in the database
    4. Returns structured insights
    
    Subsequent calls return cached results.
    """
    service = FeedbackService(db)
    return service.analyze_form(form_id)

@router.get("/forms/{form_id}/analysis", response_model=SentimentAnalysisResponse, status_code=status.HTTP_200_OK)
def get_analysis(
    form_id: UUID,
    db: Session = Depends(get_db)
):
    """
    Retrieve existing analysis results for a form.
    
    Returns 404 if analysis hasn't been performed yet.
    """
    service = FeedbackService(db)
    return service.get_analysis(form_id)

@router.put("/forms/{form_id}", response_model=FeedbackFormResponse, status_code=status.HTTP_200_OK)
def update_feedback_form(
    form_id: UUID,
    form_data: FeedbackFormUpdate,
    db: Session = Depends(get_db)
):
    """
    Update feedback form metadata.
    
    All fields are optional - only provided fields will be updated.
    """
    service = FeedbackService(db)
    return service.update_form(form_id, form_data)


@router.delete("/forms/{form_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_feedback_form(
    form_id: UUID,
    db: Session = Depends(get_db)
):
    """
    Delete a feedback form and all associated data.
    
    This will cascade delete:
    - All feedback responses
    - Sentiment analysis results
    """
    service = FeedbackService(db)
    service.delete_form(form_id)
    return None