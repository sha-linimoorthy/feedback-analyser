# Pydantic validation schemas

from pydantic import BaseModel, Field, validator
from datetime import datetime, date
from typing import Optional
from uuid import UUID

"""
Pydantic models used to validate and structure request and responses respectively

- FeedbackForm Schema
    - FeedbackFormCreate
        Event organizers creates new form, contains meta data event name, date, about event

    _ FeedbackformUpdate
        Updating the existing form 
    
    - FeedbackFormResponse
        Used when returning data to the client

- FeedbackResponse Schema
    - FeedbackResponseCreate
        Attendee submits feedback
    
    - FeedbackResponseResponse
        Used when returning the stored responses, sent to the external AI

- SentimentAnalysis Schema
    - SentimentAnalysisResponse
        Used to return AI- generated sentiment insights
"""

# Feedback Form Schemas
class FeedbackFormCreate(BaseModel):
    event_name: str = Field(..., min_length = 1, max_length = 255, description = "Name of the event")
    event_date: Optional[date] = Field(None, description = "Date of the event")
    description: Optional[str] = Field(None, max_length = 2000, description = "Event description")

class FeedbackFormUpdate(BaseModel):
    event_name: Optional[str] = Field(None, min_length = 1, max_length = 255)
    event_date: Optional[date] = None
    description: Optional[str] = Field(None, max_length = 2000)

class FeedbackFormResponse(BaseModel):
    id: UUID
    event_name: str
    event_date: Optional[date]
    description: Optional[str]
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


# Feedback Response Schemas
class FeedbackResponseCreate(BaseModel):
    attendee_name: Optional[str] = Field(None, max_length = 255)
    rating: int = Field(..., ge = 1, le = 5, description = "Rating from 1 to 5")
    comment: Optional[str] = Field(None, max_length = 2000, description = "Feedback comment")
    
    @validator('comment')
    def validate_comment(cls, v):
        if v is not None and len(v.strip()) == 0:
            return None
        return v

class FeedbackResponseResponse(BaseModel):
    id: UUID
    form_id: UUID
    attendee_name: Optional[str]
    rating: int
    comment: Optional[str]
    submitted_at: datetime
    
    class Config:
        from_attributes = True


# Sentiment Analysis Schemas
class SentimentAnalysisResponse(BaseModel):
    id: UUID
    form_id: UUID
    overall_sentiment: str
    positive_highlights: Optional[str]
    common_complaints: Optional[str]
    executive_summary: str
    analyzed_at: datetime
    
    class Config:
        from_attributes = True