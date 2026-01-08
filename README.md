# AI Attendee Feedback & Sentiment Analyzer

AI driven backend service that collects attendee feedback for events and generates actionable sentiment insights using **Gemini AI**, **FastAPI**, and **PostgreSQL**.

---

## Overview

Event organizers often struggle to extract meaningful insights from large volumes of textual feedback.  
This project automates that process by:

- Collecting structured attendee feedback
- Analyzing sentiments using AI
- Generating summarized insights for decision-making

The service exposes REST APIs for feedback management and sentiment analysis.

---

## Key Features

- Create and manage event feedback forms
- Collect attendee feedback (ratings & comments)
- AI-powered sentiment analysis (Positive / Neutral / Negative)
- Cached analysis results to reduce AI API usage
- Fully containerized PostgreSQL setup using Docker
- Interactive API documentation with Swagger

---

## Tech Stack

- **Backend**: FastAPI  
- **Database**: PostgreSQL  
- **ORM**: SQLAlchemy  
- **AI Integration**: Gemini API  
- **Validation**: Pydantic  
- **Testing**: Pytest  
- **Containerization**: Docker  

---

## Project Structure

```

feedback-analyzer/
├── app/
│   ├── main.py              # FastAPI entry point
│   ├── database.py          # DB connection & session
│   ├── models.py            # ORM models
│   ├── schemas.py           # Pydantic schemas
│   ├── routers/
│   │   └── feedback.py      # API routes
│   ├── services/
│   │   ├── feedback_service.py
│   │   └── ai_service.py    # Gemini integration
│   └── utils/
│       └── exceptions.py
├── tests/
│   ├── test_api.py
│   └── test_services.py
├── docker-compose.yml
├── Dockerfile
├── requirements.txt
├── .env.example
└── README.md

````

---

## Prerequisites

- Python 3.10+
- Docker & Docker Compose
- Gemini API Key

---

## Setup & Running the Application

### Clone the Repository

```bash
git clone https://github.com/sha-linimoorthy/feedback-analyzer.git
cd feedback-analyzer
````

---

### Environment Configuration

Create a `.env` file from the example:

```bash
cp .env.example .env
```

Update values as needed:

```env
DATABASE_URL=postgresql://user_name:user_password@postgres:5432/db_name
GEMINI_API_KEY=api_key
```

---

### Start PostgreSQL (Docker)

```bash
docker-compose up -d
```

Verify:

```bash
docker-compose ps
```

---

### Install Dependencies

```bash
python -m venv venv
source venv/bin/activate   # Linux/Mac
# venv\Scripts\activate    # Windows

pip install -r requirements.txt
```

---

### Run the FastAPI Server

```bash
uvicorn app.main:app --reload
```

---

## API Documentation

Once the server is running:

* **Swagger UI**: [http://localhost:8000/docs](http://localhost:8000/docs)

---

## API Endpoints 

| Method | Endpoint                       | Description               |
| ------ | ------------------------------ | ------------------------- |
| POST   | `/api/v1/forms`                | Create feedback form      |
| POST   | `/api/v1/forms/{id}/responses` | Submit feedback           |
| POST   | `/api/v1/forms/{id}/analyze`   | Analyze feedback using AI |
| GET    | `/api/v1/forms/{id}/analysis`  | Get cached analysis       |
| PUT    | `/api/v1/forms/{id}`           | Update form               |
| DELETE | `/api/v1/forms/{id}`           | Delete form & data        |

---

## Running Tests

```bash
pytest
```

With coverage:

```bash
pytest --cov=app tests/
```

---

## Notes

* Sentiment analysis results are **cached** to avoid repeated AI calls
* Analysis is **manually triggered**
* External AI API availability may vary
* Authentication & authorization are intentionally out of scope

---

## Troubleshooting

**Database not connecting?**

```bash
docker-compose logs postgres
```

**Port already in use?**

```bash
uvicorn app.main:app --reload --port 8001
```

---

## License

This project is for **demonstration purposes**.

---