# GameVault Server

FastAPI backend for GameVault private cloud game management platform.

## Features

- Game library management with automatic metadata scraping
- Incremental update system with manifest-based file tracking
- User authentication and authorization with JWT
- Game save synchronization and versioning
- RESTful API with automatic OpenAPI documentation

## Setup

1. Create a virtual environment:
```bash
python -m venv venv
venv\Scripts\activate  # On Windows
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Configure environment:
```bash
copy .env.example .env
# Edit .env with your configuration
```

4. Run the server:
```bash
uvicorn app.main:app --reload
```

**Note**: Database will be automatically initialized and migrated on first startup. No manual migration needed!

5. Access the API documentation:
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## Project Structure

```
server/
├── app/
│   ├── api/          # API endpoints
│   ├── core/         # Core configuration
│   ├── crud/         # Database operations
│   ├── models/       # SQLAlchemy models
│   ├── schemas/      # Pydantic schemas
│   ├── services/     # Business logic
│   └── main.py       # Application entry
├── storage/          # Data storage
└── requirements.txt  # Python dependencies
```

## Development

Run with auto-reload:
```bash
uvicorn app.main:app --reload --port 8000
```

Run tests:
```bash
pytest
```

Format code:
```bash
black app/
```

Lint code:
```bash
flake8 app/
```
