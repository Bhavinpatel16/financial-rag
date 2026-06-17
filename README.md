# Financial Document Management API with RAG

A FastAPI application for managing financial documents with AI-powered semantic search using LangChain, Qdrant, and HuggingFace embeddings.

---

## Project Structure

```
financial_rag/
├── app/
│   ├── api/routes/
│   │   ├── auth.py          # /auth/register, /auth/login
│   │   ├── documents.py     # /documents CRUD
│   │   ├── roles.py         # /roles, /users/assign-role
│   │   └── rag.py           # /rag/index, /rag/search, /rag/context
│   ├── core/
│   │   ├── config.py        # Settings from .env
│   │   └── security.py      # JWT + RBAC helpers
│   ├── db/
│   │   ├── database.py      # SQLAlchemy engine + session
│   │   └── seed.py          # Seed default roles & admin user
│   ├── models/
│   │   ├── user.py          # User, Role, Permission ORM models
│   │   └── document.py      # Document ORM model
│   ├── schemas/
│   │   ├── user.py          # Pydantic schemas for auth/users/roles
│   │   └── document.py      # Pydantic schemas for docs + RAG
│   ├── services/
│   │   ├── file_service.py  # PDF upload + text extraction
│   │   └── rag_service.py   # Chunking, embeddings, Qdrant, reranking
│   └── main.py              # FastAPI app entry point
├── tests/
│   └── test_api.py
├── docker-compose.yml       # PostgreSQL + Qdrant
├── requirements.txt
└── .env.example
```

---

## Step-by-Step Setup Guide

### Step 1 — Prerequisites

Make sure you have installed:
- Python 3.11+
- Docker + Docker Compose
- Git (optional)

```bash
python --version    # Should be 3.11+
docker --version
```

---

### Step 2 — Clone / Create Project

```bash
# If downloading, unzip the project. Then:
cd financial_rag
```

---

### Step 3 — Create Virtual Environment

```bash
python -m venv venv

# Activate it:
# On Windows:
venv\Scripts\activate
# On Mac/Linux:
source venv/bin/activate
```

---

### Step 4 — Install Dependencies

```bash
pip install -r requirements.txt
```

This installs FastAPI, SQLAlchemy, LangChain, Qdrant client, sentence-transformers (for free local embeddings), pypdf, and more.

---

### Step 5 — Configure Environment Variables

```bash
cp .env.example .env
```

Edit `.env` — the defaults work for local Docker setup. Key settings:

```env
DATABASE_URL=postgresql://postgres:password@localhost:5432/financial_rag
SECRET_KEY=your-super-secret-key-change-this-in-production-min-32-chars
USE_LOCAL_EMBEDDINGS=true
EMBEDDING_MODEL=sentence-transformers/all-MiniLM-L6-v2
```

> **Note:** `USE_LOCAL_EMBEDDINGS=true` uses HuggingFace models locally — no API key needed!  
> To use OpenAI embeddings instead, set `USE_LOCAL_EMBEDDINGS=false` and add `OPENAI_API_KEY=sk-...`

---

### Step 6 — Start Databases with Docker

```bash
docker-compose up -d
```

This starts:
- **PostgreSQL** on port 5432
- **Qdrant** (vector database) on port 6333

Verify they're running:
```bash
docker-compose ps
```

---

### Step 7 — Seed the Database

```bash
python -m app.db.seed
```

This creates:
- Default **permissions** (documents:upload, documents:read, etc.)
- Default **roles**: Admin, Analyst, Auditor, Client
- Default **admin user**: `admin` / `Admin@1234`

---

### Step 8 — Run the Application

```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

The API is now running at: **http://localhost:8000**

---

### Step 9 — Explore the API Docs

Open in browser:
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

---

## API Usage Walkthrough

### 1. Register a User

```bash
curl -X POST http://localhost:8000/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "email": "analyst@company.com",
    "username": "analyst1",
    "password": "Analyst@1234",
    "full_name": "John Analyst"
  }'
```

### 2. Login and Get Token

```bash
curl -X POST http://localhost:8000/auth/login \
  -F "username=admin" \
  -F "password=Admin@1234"
```

Copy the `access_token` from the response.

### 3. Assign a Role (Admin only)

```bash
curl -X POST http://localhost:8000/users/assign-role \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"user_id": 2, "role_id": 2}'
```

### 4. Upload a PDF Document

```bash
curl -X POST http://localhost:8000/documents/upload \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -F "title=Q4 Financial Report" \
  -F "company_name=Acme Corp" \
  -F "document_type=report" \
  -F "file=@/path/to/report.pdf"
```

### 5. Index Document for Semantic Search

```bash
curl -X POST http://localhost:8000/rag/index-document/1 \
  -H "Authorization: Bearer YOUR_TOKEN"
```

### 6. Semantic Search

```bash
curl -X POST http://localhost:8000/rag/search \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"query": "financial risk related to high debt ratio", "top_k": 5}'
```

### 7. Get Document Context

```bash
curl -X GET http://localhost:8000/rag/context/1 \
  -H "Authorization: Bearer YOUR_TOKEN"
```

---

## RBAC Permission Table

| Role     | Permissions                                           |
|----------|-------------------------------------------------------|
| Admin    | Full access (all operations)                          |
| Analyst  | Upload, read, edit documents; index & search RAG      |
| Auditor  | Read and review documents; search RAG                 |
| Client   | View own documents only                               |

---

## RAG Pipeline

```
PDF Upload
    ↓
Text Extraction (pypdf)
    ↓
Semantic Chunking (LangChain, 800 chars, 150 overlap)
    ↓
Embeddings (sentence-transformers/all-MiniLM-L6-v2)
    ↓
Vector Storage (Qdrant)
    
--- At Query Time ---

User Query
    ↓
Query Embedding
    ↓
Vector Search → Top 20 Results
    ↓
Financial Keyword Reranker
    ↓
Top 5 Most Relevant Chunks
```

---

## Running Tests

```bash
pytest tests/ -v
```

---

## Troubleshooting

| Problem | Solution |
|---------|----------|
| `Connection refused` on port 5432 | Run `docker-compose up -d` |
| `Connection refused` on port 6333 | Qdrant not running, check Docker |
| `ModuleNotFoundError` | Activate venv and run `pip install -r requirements.txt` |
| Slow first search | sentence-transformers downloads model on first run (~90MB), wait |
| `403 Forbidden` | User doesn't have required role — assign via `/users/assign-role` |

---

## Production Checklist

- [ ] Change `SECRET_KEY` in `.env` to a random 64-char string
- [ ] Set `DEBUG=false`
- [ ] Use environment variables instead of `.env` file
- [ ] Add HTTPS (nginx + certbot)
- [ ] Set `allow_origins` in CORS to your actual frontend domain
- [ ] Use a managed PostgreSQL (e.g., AWS RDS)
- [ ] Use managed Qdrant Cloud instead of local Docker
