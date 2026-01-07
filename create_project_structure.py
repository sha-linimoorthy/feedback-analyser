import os

PROJECT_STRUCTURE = {
    "backend": {
        "app": {
            "__init__.py": "",
            "main.py": "# FastAPI app entry point\n",
            "database.py": "# Database connection & session\n",
            "models.py": "# SQLAlchemy ORM models\n",
            "schemas.py": "# Pydantic validation schemas\n",
            "routers": {
                "__init__.py": "",
                "feedback.py": "# API endpoints\n",
            },
            "services": {
                "__init__.py": "",
                "feedback_service.py": "# Business logic\n",
                "ai_service.py": "# Gemini API integration\n",
            },
            "utils": {
                "__init__.py": "",
                "exceptions.py": "# Custom exceptions\n",
            },
        },
        "tests": {
            "__init__.py": "",
            "test_api.py": "# API tests\n",
            "test_services.py": "# Service tests\n",
        },
        "docker-compose.yml": "",
        "Dockerfile": "",
        "requirements.txt": "",
        ".env.example": "",
        "README.md": "# Feedback Analyzer\n",
    }
}


def create_structure(base_path, structure):
    for name, content in structure.items():
        path = os.path.join(base_path, name)
        if isinstance(content, dict):
            os.makedirs(path, exist_ok=True)
            create_structure(path, content)
        else:
            with open(path, "w") as f:
                f.write(content)


if __name__ == "__main__":
    create_structure(".", PROJECT_STRUCTURE)
    print("Project structure created successfully!")
