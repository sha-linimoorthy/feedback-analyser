# FastAPI app entry point

from fastapi import FastAPI, Request, status
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from sqlalchemy.exc import SQLAlchemyError

from app.database import init_db
from app.routers import feedback

"""
Main entry point for the FastAPI app.
- Initialize database tables at application startup
- Create and configure the FastAPI application instance
- Register versioned API routers
- Handle global validation and database errors in a consistent format
- Expose health check endpoints for monitoring and availability checks
"""

app = FastAPI(
    title="AI Attendee Feedback Analyzer",
    description="REST API for collecting and analyzing event feedback using Gemini AI"
)

# Include routers
app.include_router(feedback.router)

# Initialize database tables
@app.on_event("startup")
def on_startup():
    init_db()

# Global exception handlers
@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    """Handle Pydantic validation errors"""
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={"detail": exc.errors()}
    )

@app.exception_handler(SQLAlchemyError)
async def database_exception_handler(request: Request, exc: SQLAlchemyError):
    """Handle database errors"""
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={"detail": "Database error occurred"}
    )

@app.get("/")
async def root():
    """Health check endpoint"""
    return {
        "message": "AI-Powered Attendee Feedback Analyzer API",
        "status": "running",
        "docs": "/docs"
    }


@app.get("/health")
async def health_check():
    """Detailed health check"""
    return {
        "status": "healthy",
        "database": "connected"
    }