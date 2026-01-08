import pytest
from unittest.mock import Mock, patch, MagicMock
from sqlalchemy.orm import Session
from uuid import uuid4

from app.services.feedback_service import FeedbackService
from app.services.ai_service import GeminiAIService
from app.schemas import FeedbackFormCreate, FeedbackResponseCreate
from app.models import FeedbackForm, FeedbackResponse, SentimentAnalysis
from app.utils.exceptions import FormNotFoundException, NoResponsesException


class TestFeedbackService:
    
    @pytest.fixture
    def mock_db(self):
        return Mock(spec=Session)
    
    @pytest.fixture
    def service(self, mock_db):
        return FeedbackService(mock_db)
    
    def test_create_form(self, service, mock_db):
        """Test form creation logic"""
        form_data = FeedbackFormCreate(
            event_name="Test Event",
            event_date="2026-06-15",
            description="Test description"
        )
        
        result = service.create_form(form_data)
        
        assert mock_db.add.called
        assert mock_db.commit.called
        assert mock_db.refresh.called
    
    def test_get_form_not_found(self, service, mock_db):
        """Test getting non-existent form"""
        mock_db.query().filter().first.return_value = None
        
        with pytest.raises(FormNotFoundException):
            service.get_form(uuid4())
    
    def test_create_response(self, service, mock_db):
        """Test response creation"""
        # Mock form exists
        mock_form = FeedbackForm(id=uuid4(), event_name="Test")
        mock_db.query().filter().first.return_value = mock_form
        
        response_data = FeedbackResponseCreate(
            rating=5,
            comment="Great event!"
        )
        
        result = service.create_response(mock_form.id, response_data)
        
        assert mock_db.add.called
        assert mock_db.commit.called
    
    @patch('app.services.feedback_service.GeminiAIService')
    def test_analyze_form_no_responses(self, mock_ai, service, mock_db):
        """Test analysis with no responses"""
        # Mock form exists
        mock_form = FeedbackForm(id=uuid4(), event_name="Test")
        
        # Create separate query mocks for different queries
        mock_form_query = MagicMock()
        mock_analysis_query = MagicMock()
        mock_response_query = MagicMock()
        
        # Configure return values
        mock_form_query.filter().first.return_value = mock_form
        mock_analysis_query.filter().first.return_value = None  # No existing analysis
        mock_response_query.filter().all.return_value = []  # No responses
        
        # Set up query() to return different mocks in order
        mock_db.query.side_effect = [
            mock_form_query,      # First call: get_form
            mock_analysis_query,  # Second call: check existing analysis
            mock_response_query   # Third call: get responses
        ]
        
        with pytest.raises(NoResponsesException):
            service.analyze_form(mock_form.id)


class TestGeminiAIService:
    
    def test_build_analysis_prompt(self):
        """Test prompt construction"""
        service = GeminiAIService()
        
        feedback_data = [
            {"rating": 5, "comment": "Excellent!"},
            {"rating": 4, "comment": "Good but crowded"}
        ]
        
        prompt = service._build_analysis_prompt(feedback_data)
        
        assert "Total Responses: 2" in prompt
        assert "Average Rating: 4.50" in prompt
        assert "Excellent!" in prompt
        assert "OVERALL_SENTIMENT" in prompt
    
    def test_parse_ai_response(self):
        """Test AI response parsing"""
        service = GeminiAIService()
        
        mock_response = """
        OVERALL_SENTIMENT: Positive
        
        POSITIVE_HIGHLIGHTS:
        Great speakers and excellent networking opportunities
        
        COMMON_COMPLAINTS:
        Limited parking and long registration lines
        
        EXECUTIVE_SUMMARY:
        The event received overwhelmingly positive feedback with attendees 
        praising the quality of speakers and networking opportunities.
        """
        
        result = service._parse_ai_response(mock_response)
        
        assert result["overall_sentiment"] == "Positive"
        assert "speakers" in result["positive_highlights"].lower()
        assert "parking" in result["common_complaints"].lower()
        assert len(result["executive_summary"]) > 0
    
    def test_parse_ai_response_with_invalid_sentiment(self):
        """Test parsing with invalid sentiment defaults to Neutral"""
        service = GeminiAIService()
        
        mock_response = "OVERALL_SENTIMENT: InvalidSentiment"
        result = service._parse_ai_response(mock_response)
        
        assert result["overall_sentiment"] == "Neutral"
