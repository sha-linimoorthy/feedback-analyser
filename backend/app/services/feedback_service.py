# Business logic
from sqlalchemy.orm import Session
from typing import List, Optional
from uuid import UUID
from datetime import datetime
from app.models import FeedbackForm, FeedbackResponse, SentimentAnalysis
from app.schemas import (
    FeedbackFormCreate, FeedbackFormUpdate,
    FeedbackResponseCreate
)
from app.utils.exceptions import (
    FormNotFoundException, AnalysisNotFoundException,
    NoResponsesException, AIServiceException
)
from app.services.ai_service import GeminiAIService

"""
Abstraction layer between the API routes and the database & AI services.
- Creating, retrieving, updating, and deleting feedback forms
- Validating form existence before operations
- Storing attendee feedback responses
- Performing AI sentiment analysis using Gemini
- DB Level Caching:
    - Sentiment analysis results are cached in the SentimentAnalysis table.
"""
class FeedbackService:
    def __init__(self, db: Session):
        self.db = db
        self.ai_service = GeminiAIService()
    
    def create_form(self, form_data: FeedbackFormCreate) -> FeedbackForm:
        """Create a new feedback form"""
        db_form = FeedbackForm(
            event_name=form_data.event_name,
            event_date=form_data.event_date,
            description=form_data.description
        )
        self.db.add(db_form)
        self.db.commit()
        self.db.refresh(db_form)
        return db_form
    
    def get_form(self, form_id: UUID) -> FeedbackForm:
        """Get feedback form by ID"""
        form = self.db.query(FeedbackForm).filter(FeedbackForm.id == form_id).first()
        if not form:
            raise FormNotFoundException(str(form_id))
        return form
    
    def update_form(self, form_id: UUID, form_data: FeedbackFormUpdate) -> FeedbackForm:
        """Update feedback form"""
        form = self.get_form(form_id)
        
        update_data = form_data.dict(exclude_unset=True)
        for field, value in update_data.items():
            setattr(form, field, value)
        
        form.updated_at = datetime.utcnow()
        self.db.commit()
        self.db.refresh(form)
        return form
    
    def delete_form(self, form_id: UUID) -> bool:
        """Delete feedback form and all associated data"""
        form = self.get_form(form_id)
        self.db.delete(form)
        self.db.commit()
        return True
    
    def create_response(self, form_id: UUID, response_data: FeedbackResponseCreate) -> FeedbackResponse:
        """Submit a feedback response"""
        # Verify form exists
        self.get_form(form_id)
        
        db_response = FeedbackResponse(
            form_id=form_id,
            attendee_name=response_data.attendee_name,
            rating=response_data.rating,
            comment=response_data.comment
        )
        self.db.add(db_response)
        self.db.commit()
        self.db.refresh(db_response)
        return db_response
    
    def analyze_form(self, form_id: UUID) -> SentimentAnalysis:
        """Analyze feedback using AI (Gemini API)"""
        # Check if form exists
        form = self.get_form(form_id)
        
        # Check if analysis already exists (cache)
        existing_analysis = self.db.query(SentimentAnalysis).filter(
            SentimentAnalysis.form_id == form_id
        ).first()
        
        if existing_analysis:
            return existing_analysis
        
        # Get all responses
        responses = self.db.query(FeedbackResponse).filter(
            FeedbackResponse.form_id == form_id
        ).all()
        
        if not responses:
            raise NoResponsesException(str(form_id))
        
        # Prepare data for AI
        feedback_data = [
            {
                "rating": r.rating,
                "comment": r.comment or ""
            }
            for r in responses
        ]
        
        # Call AI service
        try:
            analysis_result = self.ai_service.analyze_feedback(feedback_data)
        except Exception as e:
            raise AIServiceException(f"Failed to analyze feedback: {str(e)}")
        
        # Store analysis
        db_analysis = SentimentAnalysis(
            form_id=form_id,
            overall_sentiment=analysis_result["overall_sentiment"],
            positive_highlights=analysis_result["positive_highlights"],
            common_complaints=analysis_result["common_complaints"],
            executive_summary=analysis_result["executive_summary"]
        )
        self.db.add(db_analysis)
        self.db.commit()
        self.db.refresh(db_analysis)
        return db_analysis
    
    def get_analysis(self, form_id: UUID) -> SentimentAnalysis:
        """Get existing analysis for a form"""
        # Verify form exists
        self.get_form(form_id)
        
        analysis = self.db.query(SentimentAnalysis).filter(
            SentimentAnalysis.form_id == form_id
        ).first()
        
        if not analysis:
            raise AnalysisNotFoundException(str(form_id))
        
        return analysis