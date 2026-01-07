# SQLAlchemy ORM models

from sqlalchemy import Column, String, Integer, Text, DateTime, Date, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from datetime import datetime
import uuid
from app.database import Base

"""
Defines SQLAlchemy ORM models
    - FeedbackForm
        - event feedback form
        - parent table
        - one form many responses
        - one form one sentiment analysis
    - FeedbackResponse
        - stores individual attendee feedback
        - linked to feedback form via foreign key
    - SentimentAnalysis
        - stores AI insights
        - one analysis per event

"""


class FeedbackForm(Base):
    __tablename__ = "feedback_forms"
    
    id = Column(UUID(as_uuid = True), primary_key =True, default =  uuid.uuid4)
    event_name = Column(String(255), nullable =False)
    event_date = Column(Date, nullable = True)
    description = Column(Text, nullable = True)
    created_at = Column(DateTime, default = datetime.utcnow)
    updated_at = Column(DateTime, default = datetime.utcnow, onupdate = datetime.utcnow)
    
    # Relationships
    # one-to-Many
    responses = relationship("FeedbackResponse", back_populates="form", cascade="all, delete-orphan")
    # one-to-one
    analysis = relationship("SentimentAnalysis", back_populates="form", cascade="all, delete-orphan", uselist=False)


class FeedbackResponse(Base):
    __tablename__ = "feedback_responses"
    
    id = Column(UUID(as_uuid = True), primary_key = True, default = uuid.uuid4)
    form_id = Column(UUID(as_uuid = True), ForeignKey("feedback_forms.id", ondelete = "CASCADE"), nullable = False)
    attendee_name = Column(String(255), nullable = True)
    rating = Column(Integer, nullable = False)
    comment = Column(Text, nullable = True)
    submitted_at = Column(DateTime, default = datetime.utcnow)
    
    # Relationship
    # many-to-one
    form = relationship("FeedbackForm", back_populates = "responses")


class SentimentAnalysis(Base):
    __tablename__ = "sentiment_analysis"
    
    id = Column(UUID(as_uuid = True), primary_key = True, default = uuid.uuid4)
    form_id = Column(UUID(as_uuid = True), ForeignKey("feedback_forms.id", ondelete = "CASCADE"), unique = True, nullable = False)
    overall_sentiment = Column(String(50), nullable = False)
    positive_highlights = Column(Text, nullable = True)
    common_complaints = Column(Text, nullable = True)
    executive_summary = Column(Text, nullable = False)
    analyzed_at = Column(DateTime, default = datetime.utcnow)
    
    # Relationship
    # one-to-one
    form = relationship("FeedbackForm", back_populates = "analysis")
