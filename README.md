# Book Price Drop Watcher

A production-lean MVP pipeline that monitors a CSV file for Packt book prices, syncs changes to a database, validates books via free APIs (Google Books, Open Library), and compares prices to send notifications when third-party sources are cheaper by a configurable threshold.

## Architecture

The system consists of three main components:

1. **Backend Pipeline** (`src/`): Scheduled Python service that monitors CSV and syncs to database
2. **API Service** (`api/`): FastAPI REST API that exposes data to the frontend
3. **Frontend Dashboard** (`frontend/`): React + TypeScript web application for the sales team

## Setup

### 1. Backend Pipeline

1. Install Python dependencies:
```bash
pip install -r requirements.txt
```

2. Copy `.env.example` to `.env` and configure if needed:
```bash
cp .env.example .env
```

3. Create the data directory and add your CSV file:
```bash
mkdir -p data
# Add your packt_books.csv file to the data/ directory
```

4. Run the pipeline:
```bash
python -m src.main
```

### 2. API Service

1. Install API dependencies:
```bash
pip install -r requirements-api.txt
```

2. Run the API server:
```bash
python -m api.main
```

The API will be available at `http://localhost:8000`
- API Documentation: `http://localhost:8000/docs`
- Health Check: `http://localhost:8000/health`

### 3. Frontend Dashboard

1. Navigate to the frontend directory:
```bash
cd frontend
```

2. Install Node.js dependencies:
```bash
npm install
```

3. Start the development server:
```bash
npm run dev
```

The frontend will be available at `http://localhost:3000`

## Running All Services

For development, you'll need to run three services:

1. **Terminal 1 - Pipeline**:
```bash
python -m src.main
```

2. **Terminal 2 - API**:
```bash
python -m api.main
```

3. **Terminal 3 - Frontend**:
```bash
cd frontend && npm run dev
```

## Production Build

### Frontend Build

```bash
cd frontend
npm run build
```

This creates a `dist/` directory with static files that can be served by any web server.

### API Deployment

The API can be deployed using:
- Docker
- Cloud platforms (AWS, GCP, Azure)
- Serverless functions
- Traditional web servers with uvicorn/gunicorn

## CSV Format

Expected CSV format:
```csv
ISBN,Title,Author,Packt_Price,Packt_URL,Last_Updated
9780134685991,Effective Python,Item Brett Slatkin,29.99,https://packtpub.com/...,2024-01-15
9781492056355,Python Tricks,Dan Bader,24.99,https://packtpub.com/...,2024-01-15
```

## Configuration

Edit `config/config.yaml` to adjust:
- CSV check interval
- Price comparison thresholds
- Price check interval
- Notification cooldown period

## Architecture

The system uses:
- **CSV Watcher**: Detects changes in CSV file using hash comparison
- **CSV Parser**: Validates and parses CSV data
- **Database Sync**: Syncs CSV data to SQLite database
- **API Fetchers**: Fetches book metadata from Google Books and Open Library APIs
- **Price Comparator**: Compares prices and checks thresholds
- **Notifications**: Sends console notifications when price drops are detected

## Limitations

Google Books and Open Library APIs don't provide prices. The system is architected to support price comparison when price sources become available.

