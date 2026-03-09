# FastAPI Backend

A simple FastAPI backend application.

## Getting Started

### Prerequisites
- Python 3.8+
- Virtual environment (recommended)

### Installation

1. **Clone the repository:**
   ```bash
   git clone https://github.com/apucsd/fastapi-backend.git
   cd fastapi-backend
   ```

2. **Create and activate a virtual environment:**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

### Running Locally

- **Development mode (with auto-reload):**
  ```bash
  make dev
  ```
  Or directly:
  ```bash
  uvicorn app.main:app --reload --host 0.0.0.0
  ```

- **Production mode:**
  ```bash
  make start
  ```
  Or directly:
  ```bash
  uvicorn app.main:app --host 0.0.0.0
  ```

The API will be available at `http://127.0.0.1:8000` or your local IP if using `--host 0.0.0.0`.

### API Documentation
Once running, visit `http://127.0.0.1:8000/docs` for interactive API docs (Swagger UI).