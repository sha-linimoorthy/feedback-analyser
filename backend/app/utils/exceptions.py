# Custom exceptions

from fastapi import HTTPException, status

"""
Custom HTTP exceptions by extendin HTTPException class
- FormNotFoundException 
    - Raised when feedback form does not exists

- AnalysisNotFoundException
    - Raised when sentiment analysis is not generated for this form

-NoResponsesException
    - RAised when analysis is requested but no attendee feedback is available

- AIServiceException
    - Raised when AI service is unavailable or fails 
"""

class FormNotFoundException(HTTPException):
    def __init__(self, form_id: str):
        super().__init__(
            status_code = status.HTTP_404_NOT_FOUND,
            detail =f"Feedback form with id {form_id} not found"
        )

class AnalysisNotFoundException(HTTPException):
    def __init__(self, form_id: str):
        super().__init__(
            status_code = status.HTTP_404_NOT_FOUND,
            detail = f"No analysis found for form {form_id}. Please run analysis first."
        )

class NoResponsesException(HTTPException):
    def __init__(self, form_id: str):
        super().__init__(
            status_code = status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail = f"Cannot analyze form {form_id}: No feedback responses submitted yet"
        )

class AIServiceException(HTTPException):
    def __init__(self, message: str = "External AI service unavailable"):
        super().__init__(
            status_code = status.HTTP_503_SERVICE_UNAVAILABLE,
            detail = message
        )
