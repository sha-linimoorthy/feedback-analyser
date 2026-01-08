# API tests

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from unittest.mock import Mock, patch
from uuid import uuid4
from app.main import app
from app.database import Base, get_db

"""
Using sqlite file based database for testing as it is simple, faster and zero dependency unlike postgres used in production
Creating a db session and overriding the get_db dependency so the original db remains untouched
"""
# Test database setup
SQLALCHEMY_TEST_DATABASE_URL = "sqlite:///./test.db"
engine = create_engine(SQLALCHEMY_TEST_DATABASE_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def override_get_db():
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()

app.dependency_overrides[get_db] = override_get_db

"""
Creating all the tables and dropping them when the test ends
"""
@pytest.fixture(scope="function")
def test_db():
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)

@pytest.fixture
def client(test_db):
    return TestClient(app)


# ==================== API Tests ====================

"""
Event organizers Form:
    Tests
        - Create form
        - Create form with only event name (PK)
        - Create form with no data
        - Update the created form
        - Update the form with nonexisting events
        - Delete the created form
        - Delete the non existing foem
"""

class TestFeedbackFormAPI:
    
    def test_create_form_success(self, client):
        """Test successful form creation"""
        payload = {
            "event_name": "Tech Conference 2026",
            "event_date": "2026-06-15",
            "description": "Annual tech event"
        }
        
        response = client.post("/api/v1/forms", json = payload)
        
        assert response.status_code == 201
        data = response.json()
        assert data["event_name"] == "Tech Conference 2026"
        assert "id" in data
        assert "created_at" in data
    
    def test_create_form_minimal(self, client):
        """Test form creation with minimal data"""
        payload = {"event_name": "Minimal Event"}
        
        response = client.post("/api/v1/forms", json = payload)
        
        assert response.status_code == 201
        data = response.json()
        assert data["event_name"] == "Minimal Event"
        assert data["event_date"] is None
    
    def test_create_form_validation_error(self, client):
        """Test form creation with invalid data"""
        payload = {"event_name": ""}  # Empty name
        
        response = client.post("/api/v1/forms", json=payload)
        
        assert response.status_code == 422
    
    def test_update_form_success(self, client):
        """Test successful form update"""
        # Create form first
        create_payload = {"event_name": "Original Event"}
        create_response = client.post("/api/v1/forms", json = create_payload)
        form_id = create_response.json()["id"]
        
        # Update form
        update_payload = {
            "event_name": "Updated Event",
            "description": "New description"
        }
        response = client.put(f"/api/v1/forms/{form_id}", json=update_payload)
        
        assert response.status_code == 200
        data = response.json()
        assert data["event_name"] == "Updated Event"
        assert data["description"] == "New description"
    
    def test_update_nonexistent_form(self, client):
        """Test updating a form that doesn't exist"""
        fake_id = str(uuid4())
        update_payload = {"event_name": "Updated"}
        
        response = client.put(f"/api/v1/forms/{fake_id}", json = update_payload)
        
        assert response.status_code == 404
    
    def test_delete_form_success(self, client):
        """Test successful form deletion"""
        # Create form
        create_payload = {"event_name": "Event to Delete"}
        create_response = client.post("/api/v1/forms", json = create_payload)
        form_id = create_response.json()["id"]
        
        # Delete form
        response = client.delete(f"/api/v1/forms/{form_id}")
        
        assert response.status_code == 204
        
        # Verify deletion
        get_response = client.get(f"/api/v1/forms/{form_id}/analysis")
        assert get_response.status_code == 404
    
    def test_delete_nonexistent_form(self, client):
        """Test deleting a form that doesn't exist"""
        fake_id = str(uuid4())
        
        response = client.delete(f"/api/v1/forms/{fake_id}")
        
        assert response.status_code == 404


"""
Feedbacks submitted by the attendees
    Tests
        - Submit form
        - Submit form only with the required fields
        - Submit form with invalid ratings
        - Submit response for non existing form
"""

class TestFeedbackResponseAPI:
    
    def test_submit_response_success(self, client):
        """Test successful response submission"""
        # Create form
        form_payload = {"event_name": "Test Event"}
        form_response = client.post("/api/v1/forms", json = form_payload)
        form_id = form_response.json()["id"]
        
        # Submit response
        response_payload = {
            "attendee_name": "John Doe",
            "rating": 5,
            "comment": "Excellent event!"
        }
        response = client.post(f"/api/v1/forms/{form_id}/responses", json = response_payload)
        
        assert response.status_code == 201
        data = response.json()
        assert data["rating"] == 5
        assert data["comment"] == "Excellent event!"
        assert data["form_id"] == form_id
    
    def test_submit_response_minimal(self, client):
        """Test response submission with only required fields"""
        # Create form
        form_payload = {"event_name": "Test Event"}
        form_response = client.post("/api/v1/forms", json=form_payload)
        form_id = form_response.json()["id"]
        
        # Submit minimal response
        response_payload = {"rating": 3}
        response = client.post(f"/api/v1/forms/{form_id}/responses", json=response_payload)
        
        assert response.status_code == 201
        data = response.json()
        assert data["rating"] == 3
        assert data["attendee_name"] is None
    
    def test_submit_response_invalid_rating(self, client):
        """Test response with invalid rating"""
        # Create form
        form_payload = {"event_name": "Test Event"}
        form_response = client.post("/api/v1/forms", json=form_payload)
        form_id = form_response.json()["id"]
        
        # Invalid rating (out of range)
        response_payload = {"rating": 6}
        response = client.post(f"/api/v1/forms/{form_id}/responses", json=response_payload)
        
        assert response.status_code == 422
    
    def test_submit_response_nonexistent_form(self, client):
        """Test submitting response to non-existent form"""
        fake_id = str(uuid4())
        response_payload = {"rating": 4, "comment": "Great!"}
        
        response = client.post(f"/api/v1/forms/{fake_id}/responses", json=response_payload)
        
        assert response.status_code == 404

"""
Sentiment analysis from the AI response
Mocking the AI response because it is cost efficient operation
    TESTS
        - Analyze the feedback 
        - Analyze without the response
        - Test analyses caching 
"""

class TestSentimentAnalysisAPI:
    
    @patch('app.services.ai_service.GeminiAIService.analyze_feedback')
    def test_analyze_feedback_success(self, mock_analyze, client):
        """Test successful sentiment analysis"""
        # Mock AI response
        mock_analyze.return_value = {
            "overall_sentiment": "Positive",
            "positive_highlights": "Great speakers and venue",
            "common_complaints": "Limited parking",
            "executive_summary": "Overall positive feedback with minor logistics issues"
        }
        
        # Create form
        form_payload = {"event_name": "Test Conference"}
        form_response = client.post("/api/v1/forms", json=form_payload)
        form_id = form_response.json()["id"]
        
        # Submit responses
        responses = [
            {"rating": 5, "comment": "Great speakers!"},
            {"rating": 4, "comment": "Good but parking was difficult"},
            {"rating": 5, "comment": "Excellent venue"}
        ]
        for resp in responses:
            client.post(f"/api/v1/forms/{form_id}/responses", json=resp)
        
        # Analyze
        response = client.post(f"/api/v1/forms/{form_id}/analyze")
        
        assert response.status_code == 200
        data = response.json()
        assert data["overall_sentiment"] == "Positive"
        assert "Great speakers" in data["positive_highlights"]
        assert mock_analyze.called
    
    def test_analyze_without_responses(self, client):
        """Test analysis with no responses"""
        # Create form without responses
        form_payload = {"event_name": "Empty Event"}
        form_response = client.post("/api/v1/forms", json=form_payload)
        form_id = form_response.json()["id"]
        
        # Try to analyze
        response = client.post(f"/api/v1/forms/{form_id}/analyze")
        
        assert response.status_code == 422
        assert "No feedback responses" in response.json()["detail"]
    
    @patch('app.services.ai_service.GeminiAIService.analyze_feedback')
    def test_get_analysis_success(self, mock_analyze, client):
        """Test retrieving existing analysis"""
        # Mock AI response
        mock_analyze.return_value = {
            "overall_sentiment": "Neutral",
            "positive_highlights": "Good content",
            "common_complaints": "Room temperature",
            "executive_summary": "Mixed feedback overall"
        }
        
        # Create form and responses
        form_payload = {"event_name": "Test Event"}
        form_response = client.post("/api/v1/forms", json=form_payload)
        form_id = form_response.json()["id"]
        
        client.post(f"/api/v1/forms/{form_id}/responses", json={"rating": 3, "comment": "Okay"})
        
        # Generate analysis
        client.post(f"/api/v1/forms/{form_id}/analyze")
        
        # Retrieve analysis
        response = client.get(f"/api/v1/forms/{form_id}/analysis")
        
        assert response.status_code == 200
        data = response.json()
        assert data["overall_sentiment"] == "Neutral"
    
    def test_get_analysis_not_found(self, client):
        """Test retrieving analysis that doesn't exist"""
        # Create form but don't analyze
        form_payload = {"event_name": "Test Event"}
        form_response = client.post("/api/v1/forms", json=form_payload)
        form_id = form_response.json()["id"]
        
        response = client.get(f"/api/v1/forms/{form_id}/analysis")
        
        assert response.status_code == 404
        assert "No analysis found" in response.json()["detail"]
    
    @patch('app.services.ai_service.GeminiAIService.analyze_feedback')
    def test_analysis_caching(self, mock_analyze, client):
        """Test that analysis results are cached"""
        mock_analyze.return_value = {
            "overall_sentiment": "Positive",
            "positive_highlights": "Test",
            "common_complaints": "None",
            "executive_summary": "Good event"
        }
        
        # Create form and response
        form_payload = {"event_name": "Cache Test"}
        form_response = client.post("/api/v1/forms", json=form_payload)
        form_id = form_response.json()["id"]
        
        client.post(f"/api/v1/forms/{form_id}/responses", json={"rating": 5})
        
        # First analysis
        client.post(f"/api/v1/forms/{form_id}/analyze")
        
        # Second analysis (should return cached)
        response = client.post(f"/api/v1/forms/{form_id}/analyze")
        
        assert response.status_code == 200
        # AI should only be called once (cached second time)
        assert mock_analyze.call_count == 1
