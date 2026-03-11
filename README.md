# SalesInsight AI

> **AI-powered executive summary generator for sales data.**  
> Upload CSV/Excel sales data → AI generates a professional executive summary → Delivered via email.

Built as part of the Rabbitt AI — AI Cloud DevOps Engineer assessment.

---

## Table of Contents

- [Project Overview](#project-overview)
- [Architecture](#architecture)
- [Tech Stack](#tech-stack)
- [Getting Started](#getting-started)
- [Docker Compose Usage](#docker-compose-usage)
- [Environment Variables](#environment-variables)
- [API Documentation](#api-documentation)
- [Security Measures](#security-measures)
- [Deployment](#deployment)
- [CI/CD Pipeline](#cicd-pipeline)
- [Project Structure](#project-structure)

---

## Project Overview

SalesInsight AI is a quick-response tool designed for sales teams. Team members upload a CSV or Excel file containing sales data, and the system:

1. **Parses** the data using pandas, computing revenue breakdowns, product performance, and regional insights.
2. **Generates** a professional executive summary using an LLM (Groq/Llama 3 or Google Gemini).
3. **Emails** the summary to the specified recipient via Resend or SMTP.

The entire flow completes in under 30 seconds.

---

## Architecture

```
┌─────────────────────────────────────────────────────────────────────┐
│                          Client Browser                             │
│  ┌───────────────────────────────────────────────────────────────┐  │
│  │              Next.js Frontend (Port 3000)                     │  │
│  │  ┌──────────────┐  ┌──────────────┐  ┌──────────────────┐   │  │
│  │  │ Upload Form   │  │ Email Input  │  │ Summary Display  │   │  │
│  │  └──────┬───────┘  └──────┬───────┘  └────────▲─────────┘   │  │
│  └─────────┼────────────────┼────────────────────┼──────────────┘  │
└────────────┼────────────────┼────────────────────┼──────────────────┘
             │ POST /api/upload (multipart/form-data)
             ▼                ▼                    │
┌─────────────────────────────────────────────────────────────────────┐
│                    FastAPI Backend (Port 8000)                       │
│  ┌────────────┐  ┌──────────────────┐  ┌───────────────────────┐   │
│  │ Security   │  │  File Processor  │  │    AI Engine          │   │
│  │ • Rate Lim │──│  • pandas parse  │──│  • Groq (Llama 3)    │   │
│  │ • Validate │  │  • stats compute │  │  • Gemini            │   │
│  │ • Sanitize │  │  • data prep     │  │  • Summary gen       │   │
│  └────────────┘  └──────────────────┘  └──────────┬────────────┘   │
│                                                    │                │
│                                         ┌──────────▼────────────┐  │
│                                         │   Email Service       │  │
│                                         │  • Resend API         │  │
│                                         │  • SMTP fallback      │  │
│                                         └───────────────────────┘  │
└─────────────────────────────────────────────────────────────────────┘
```

---

## Tech Stack

| Layer      | Technology                          |
|------------|-------------------------------------|
| Frontend   | Next.js 14, React 18, Tailwind CSS  |
| Backend    | FastAPI, Python 3.12, pandas        |
| AI Engine  | Groq (Llama 3) / Google Gemini      |
| Email      | Resend / SMTP                       |
| DevOps     | Docker, Docker Compose, GitHub Actions |
| Deployment | Vercel (FE) + Render (BE)           |

---

## Getting Started

### Prerequisites

- **Python 3.11+** and **pip**
- **Node.js 18+** and **npm**
- API keys for AI provider (Groq or Gemini) and email service (Resend)

### 1. Clone the Repository

```bash
git clone https://github.com/your-username/salesinsight-ai.git
cd salesinsight-ai
```

### 2. Configure Environment

```bash
cp .env.example .env
# Edit .env and fill in your API keys
```

### 3. Run Backend

```bash
cd backend
python -m venv venv
source venv/bin/activate    # Windows: venv\Scripts\activate
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000
```

Backend will be available at `http://localhost:8000`.  
Swagger docs at `http://localhost:8000/docs`.

### 4. Run Frontend

```bash
cd frontend
npm install
npm run dev
```

Frontend will be available at `http://localhost:3000`.

### 5. Test with Sample Data

Use the provided `sample_data/sales_data.csv` to test the upload flow.

---

## Docker Compose Usage

Build and run the entire stack with a single command:

```bash
# Build and start
docker compose up --build

# Run in background
docker compose up --build -d

# View logs
docker compose logs -f

# Stop
docker compose down
```

| Service   | URL                        |
|-----------|----------------------------|
| Frontend  | http://localhost:3000       |
| Backend   | http://localhost:8000       |
| API Docs  | http://localhost:8000/docs  |

---

## Environment Variables

| Variable                    | Description                        | Default                  |
|-----------------------------|------------------------------------|--------------------------|
| `AI_PROVIDER`               | AI provider (`groq` or `gemini`)  | `groq`                   |
| `GROQ_API_KEY`              | Groq API key                       | —                        |
| `GROQ_MODEL`                | Groq model name                    | `llama-3.3-70b-versatile`|
| `GEMINI_API_KEY`            | Google Gemini API key              | —                        |
| `GEMINI_MODEL`              | Gemini model name                  | `gemini-2.0-flash`       |
| `EMAIL_PROVIDER`            | Email service (`resend` or `smtp`)| `resend`                 |
| `RESEND_API_KEY`            | Resend API key                     | —                        |
| `EMAIL_FROM`                | Sender email address               | `onboarding@resend.dev`  |
| `CORS_ORIGINS`              | Allowed CORS origins (comma-sep)  | `http://localhost:3000`  |
| `MAX_FILE_SIZE_MB`          | Maximum upload file size           | `10`                     |
| `RATE_LIMIT_REQUESTS`       | Max requests per window            | `20`                     |
| `RATE_LIMIT_WINDOW_SECONDS` | Rate limit window duration         | `60`                     |
| `NEXT_PUBLIC_API_URL`       | Backend URL for frontend           | `http://localhost:8000`  |

---

## API Documentation

Interactive Swagger documentation is available at `/docs` when the backend is running.

### Endpoints

#### `GET /api/health`

Health check endpoint.

**Response:**
```json
{ "status": "healthy", "version": "1.0.0" }
```

#### `POST /api/upload`

Upload sales data and receive an AI-generated executive summary.

**Request:** `multipart/form-data`

| Field              | Type   | Description                          |
|--------------------|--------|--------------------------------------|
| `file`             | File   | Sales data file (.csv, .xlsx, .xls)  |
| `recipient_email`  | String | Email to send the summary to         |

**Success Response (200):**
```json
{
  "success": true,
  "message": "Executive summary generated and emailed to user@example.com.",
  "summary": "## Executive Summary\n\n..."
}
```

**Error Responses:**

| Code | Description                        |
|------|------------------------------------|
| 400  | Invalid file type, empty file, or invalid email |
| 413  | File exceeds size limit            |
| 429  | Rate limit exceeded                |
| 500  | AI generation or email delivery failure |

---

## Security Measures

| Measure              | Implementation                                      |
|----------------------|-----------------------------------------------------|
| File Type Validation | Only `.csv`, `.xlsx`, `.xls` accepted               |
| File Size Limit      | Configurable, default 10 MB                         |
| Rate Limiting        | Sliding window per IP (20 req/min default)          |
| Input Sanitization   | Email regex validation, HTML escaping in emails     |
| CORS                 | Strict origin allowlist                             |
| Secrets Management   | All API keys via environment variables              |
| Non-root Containers  | Docker images run as non-root user                  |
| Dependency Pinning   | All dependencies version-pinned                     |
| Structured Logging   | JSON-formatted logs with no sensitive data exposure |

---

## Deployment

### Frontend → Vercel

1. Push the repository to GitHub.
2. Import the project in [Vercel](https://vercel.com).
3. Set root directory to `frontend`.
4. Add environment variable:
   - `NEXT_PUBLIC_API_URL` = your Render backend URL (e.g., `https://salesinsight-api.onrender.com`)
5. Deploy.

### Backend → Render

1. Create a new **Web Service** on [Render](https://render.com).
2. Connect your GitHub repository.
3. Configure:
   - **Root Directory:** `backend`
   - **Build Command:** `pip install -r requirements.txt`
   - **Start Command:** `uvicorn app.main:app --host 0.0.0.0 --port $PORT`
4. Add all environment variables from `.env.example` in the Render dashboard.
5. Update `CORS_ORIGINS` to include your Vercel frontend URL.
6. Deploy.

### Post-Deployment Checklist

- [ ] Backend health check returns 200 at `/api/health`
- [ ] Frontend can reach backend API
- [ ] CORS origins updated for production URLs
- [ ] API keys set in production environment
- [ ] Test full upload → summary → email flow

---

## CI/CD Pipeline

The GitHub Actions workflow (`.github/workflows/ci.yml`) runs on every push/PR to `main`:

```
┌─────────────────────────────────────────────────────┐
│                   CI Pipeline                        │
│                                                     │
│  ┌──────────────┐        ┌──────────────┐          │
│  │  Backend CI   │        │ Frontend CI  │          │
│  │ • Install deps│        │ • npm ci     │          │
│  │ • Ruff lint   │        │ • ESLint     │          │
│  │ • pytest      │        │ • next build │          │
│  │ • Docker build│        │ • Docker     │          │
│  └──────┬───────┘        └──────┬───────┘          │
│         │                       │                   │
│         └───────────┬───────────┘                   │
│                     ▼                               │
│          ┌──────────────────┐                       │
│          │ Docker Compose   │                       │
│          │ Validation       │                       │
│          └──────────────────┘                       │
└─────────────────────────────────────────────────────┘
```

**Jobs:**
1. **Backend CI** — Python install, Ruff linting, pytest, Docker build verification.
2. **Frontend CI** — Node install, ESLint, Next.js build, Docker build verification.
3. **Docker Compose Validation** — Validates the compose file syntax.

---

## Project Structure

```
salesinsight-ai/
├── .github/
│   └── workflows/
│       └── ci.yml                 # GitHub Actions CI pipeline
├── backend/
│   ├── app/
│   │   ├── api/
│   │   │   └── routes.py          # API endpoint definitions
│   │   ├── core/
│   │   │   ├── config.py          # App configuration (env vars)
│   │   │   ├── logging_config.py  # Structured JSON logging
│   │   │   └── security.py        # Rate limiter, validation, sanitization
│   │   ├── models/
│   │   │   └── schemas.py         # Pydantic request/response models
│   │   ├── services/
│   │   │   ├── ai_engine.py       # Groq / Gemini AI integration
│   │   │   ├── email_service.py   # Resend / SMTP email delivery
│   │   │   └── file_processor.py  # pandas CSV/Excel parser
│   │   └── main.py                # FastAPI app entry point
│   ├── tests/
│   │   ├── test_api.py            # API integration tests
│   │   └── test_file_processor.py # Unit tests for data processing
│   ├── Dockerfile                 # Multi-stage production image
│   ├── requirements.txt           # Python dependencies
│   └── pyproject.toml             # Ruff & pytest config
├── frontend/
│   ├── src/
│   │   ├── app/
│   │   │   ├── globals.css        # Tailwind + global styles
│   │   │   ├── layout.tsx         # Root layout
│   │   │   └── page.tsx           # Main page
│   │   └── components/
│   │       ├── UploadForm.tsx      # File upload + email form
│   │       └── SummaryResult.tsx   # AI summary display
│   ├── Dockerfile                 # Multi-stage production image
│   ├── package.json               # Node dependencies
│   ├── tailwind.config.js         # Tailwind configuration
│   ├── tsconfig.json              # TypeScript configuration
│   └── next.config.js             # Next.js configuration
├── sample_data/
│   └── sales_data.csv             # Example dataset for testing
├── .env.example                   # Environment variable template
├── .gitignore                     # Git ignore rules
├── docker-compose.yml             # Full-stack orchestration
└── README.md                      # This file
```

---

## Running Tests

### Backend

```bash
cd backend
pip install -r requirements.txt
pytest -v
```

### Linting

```bash
# Backend
cd backend && ruff check .

# Frontend
cd frontend && npm run lint
```

---

## License

This project was built as a technical assessment for Rabbitt AI.
