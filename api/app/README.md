# Project Structure

This document outlines the structure of the Python project, including a simplified setup for a small-scale FastAPI application and details about its components.

## Project Structure

```
project-root/
├── app/
│   ├── __init__.py
│   ├── auth.py              # Handles Google Authentication.
│   ├── controllers.py       # Contains endpoint definitions for the API.
│   ├── db.py                # Database connection and setup logic.
│   ├── dto.py               # Data Transfer Objects (DTOs) for the API.
│   ├── services/
│   │   ├── __init__.py
│   │   ├── tune2tube_service.py  # Handles image and audio file processing.
│   ├── utils.py             # Helper methods and utility functions.
├── .gitignore               # Git ignore rules.
├── README.md                # Project documentation (this file).
├── requirements.txt         # Python dependencies.
└── main.py                  # Application entry point.
```

## File Descriptions

### **app/auth.py**
Handles Google Authentication for secure API access.

### **app/controllers.py**
Defines API endpoints, including:
- `/upload_tune/single`
- `/upload_tune/batch`
- `/tune_upload/get`
- `/tune_upload/get/{id}`
- `/tune_upload/create`
- `/tune_upload/update/{id}`
- `/tune_upload/delete/{id}`

### **app/db.py**
Sets up the SQLite database connection and provides a simple interface for queries.

### **app/dto.py**
Contains Data Transfer Object definitions:

#### `TuneDTO`
```python
from pydantic import BaseModel
from typing import Optional

class TuneDTO(BaseModel):
    id: int
    title: str
    description: str
    audio_file: str  # File path
    image_file: str  # File path
```

#### `tuneDTO`
```python
class tuneDTO(BaseModel):
    id: int
    date_created: str  # ISO 8601 format
    upload_date: Optional[str]  # ISO 8601 format or None
    executed: bool
    video_title: str
    image_location: str
    audio_location: str
```

### **app/services/tune2tube_service.py**
Handles processing of image and audio files, including validation and preparation for upload.

### **app/utils.py**
Contains reusable utility functions, such as date validation and file handling.

### **main.py**
Entry point for the FastAPI application. Configures the app, initializes routes, and runs the server.

### **.gitignore**
Ensures only the `app/` directory, `README.md`, and excludes unnecessary files like `venv/` and `__pycache__/`:
```
# Ignore everything
*

# Allow the app/ directory and its contents
!app/
!app/**

# Allow README.md
!README.md

# Exclude virtual environment and cache files
app/venv/
app/__pycache__/
```

### **requirements.txt**
Lists Python dependencies, such as:
```
fastapi
uvicorn
pydantic
sqlite
```

## Getting Started

1. **Install Dependencies**
   ```bash
   pip install -r requirements.txt
   ```

2. **Run the Application**
   ```bash
   python main.py
   ```

3. **Access the API**
   Visit `http://127.0.0.1:8000/docs` to interact with the API Swagger UI.

## Notes
- The project structure is designed to be minimalistic and pragmatic for a small-scale application.
- `tune2tube_service.py` processes files, while `auth.py` ensures secure access using Google Authentication.

