# PopeBeats2Tube

PopeBeats2Tube is a web application that allows users to upload, schedule, and manage audio and image files. It also integrates with Google authentication and the YouTube API to sync media content. This application is designed for personal use, with a simple and intuitive interface for handling various media management tasks.

## Features

- **Upload Management**:
  - Upload single or multiple files (images and audio).
  - Schedule uploads for single and multiple files.
  - View upload history.

- **Backend Capabilities**:
  - Google authentication for secure login.
  - Image and audio processing.
  - YouTube API integration to sync media content.

## Tech Stack

- **Frontend**: React (or any preferred modern JavaScript framework)
- **Backend**: FastAPI (Python)
- **Database**: SQLite (development) / PostgreSQL (production)
- **Authentication**: Google OAuth 2.0
- **Hosting**: Self-hosted on Dell OptiPlex Micro

## Requirements

- Python 3.9+
- Node.js 16+
- SQLite (for local development)
- PostgreSQL (for production deployment)
- Google Cloud Platform account for OAuth and YouTube API integration

## Setup Instructions

### Backend

1. Clone the repository:
   ```bash
   git clone https://github.com/username/soundframe.git
   cd soundframe/backend
   ```
2. Create a virtual environment and install dependencies:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   pip install -r requirements.txt
   ```
3. Configure Google OAuth credentials and YouTube API:
   - Set up a project in Google Cloud Console.
   - Enable the OAuth 2.0 and YouTube Data API v3.
   - Download the credentials JSON file and place it in the `backend/config` directory.
4. Start the development server:
   ```bash
   uvicorn main:app --reload
   ```

### Frontend

1. Navigate to the `frontend` directory:
   ```bash
   cd ../frontend
   ```
2. Install dependencies:
   ```bash
   npm install
   ```
3. Start the development server:
   ```bash
   npm start
   ```

## Project Structure

```
Soundframe/
|
├── backend/
│   ├── app/
│   │   ├── services/          # Core service logic (e.g., upload handling, scheduling)
│   │   ├── models/            # Data models and schemas
│   │   ├── routes/            # API routes
│   │   └── utils/             # Utility functions
│   ├── config/                # Configuration files (e.g., Google OAuth, logging)
│   ├── tests/                 # Unit and integration tests
│   └── main.py                # Entry point for FastAPI application
│
├── frontend/
│   ├── public/                # Static assets
│   ├── src/
│   │   ├── components/        # React components
│   │   ├── pages/             # Application pages
│   │   └── services/          # API service calls
│   ├── package.json           # Frontend dependencies and scripts
│   └── index.html             # HTML template
│
├── docs/                      # Project documentation
└── README.md                  # Project introduction
```

## Contributing

This is a personal project, but contributions are welcome. If you'd like to contribute:

1. Fork the repository.
2. Create a feature branch.
3. Commit your changes.
4. Open a pull request.

## License

This project is licensed under the MIT License. See the `LICENSE` file for details.

## Contact

For any questions or feedback, feel free to reach out to pavle.curcic678@gmail.com.

## Made as a birthday present, with love.

This is considered as an open source project, feel free to selfhost it!
