# Financial RAG - Document Management API

![Python](https://img.shields.io/badge/Python-3.11+-blue?style=flat-square)
![FastAPI](https://img.shields.io/badge/FastAPI-Latest-green?style=flat-square)
![License](https://img.shields.io/badge/License-MIT-yellow?style=flat-square)
![Status](https://img.shields.io/badge/Status-Active-brightgreen?style=flat-square)

A production-ready **FastAPI application** for managing financial documents with AI-powered semantic search using **LangChain**, **Qdrant**, and **HuggingFace embeddings**. Features role-based access control (RBAC), JWT authentication, and advanced document retrieval.

**GitHub Repository:** https://github.com/Bhavinpatel16/financial-rag

---

## Features

✨ **Core Features:**
- 📄 **PDF Document Upload & Management** — Upload, store, and organize financial documents
- 🔍 **AI-Powered Semantic Search** — Find relevant documents using natural language queries
- 🤖 **RAG Pipeline** — Retrieval-Augmented Generation with LangChain and Qdrant
- 🔐 **JWT Authentication** — Secure token-based authentication
- 👥 **Role-Based Access Control (RBAC)** — Admin, Analyst, Auditor, Client roles
- ⚡ **Vector Database** — Qdrant for fast semantic similarity search
- 📊 **Document Embeddings** — Local HuggingFace embeddings (no API keys required)
- 🏗️ **RESTful API** — Fully documented with Swagger UI & ReDoc
- 🐳 **Docker Support** — Easy deployment with Docker Compose

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

## Quick Start (30 seconds)

```bash
# 1. Clone repo
git clone https://github.com/Bhavinpatel16/financial-rag.git
cd financial-rag

# 2. Setup virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Start databases
docker-compose up -d

# 5. Configure & seed database
cp .env.example .env
python -m app.db.seed

# 6. Run the app
uvicorn app.main:app --reload --port 8000

# 7. Open browser
# API Docs: http://localhost:8000/docs
# ReDoc: http://localhost:8000/redoc
```

Default login credentials:
- **Username:** `admin`
- **Password:** `Admin@1234`

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

## Tech Stack

| Component | Technology |
|-----------|-----------|
| **Backend Framework** | FastAPI |
| **Authentication** | JWT + RBAC |
| **Database** | PostgreSQL |
| **Vector DB** | Qdrant |
| **Embeddings** | HuggingFace (sentence-transformers) |
| **RAG Framework** | LangChain |
| **ORM** | SQLAlchemy |
| **PDF Processing** | PyPDF |
| **API Docs** | Swagger UI + ReDoc |
| **Containerization** | Docker & Docker Compose |

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

---

## Environment Variables

Key environment variables in `.env`:

```env
# Database
DATABASE_URL=postgresql://postgres:password@localhost:5432/financial_rag

# Security
SECRET_KEY=your-super-secret-key-change-this-in-production-min-32-chars
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=60

# Embeddings (Local)
USE_LOCAL_EMBEDDINGS=true
EMBEDDING_MODEL=sentence-transformers/all-MiniLM-L6-v2

# Vector DB
QDRANT_URL=http://localhost:6333
QDRANT_COLLECTION_NAME=financial_documents

# CORS
CORS_ORIGINS=["http://localhost:3000","http://localhost:8000"]
```

---

## API Endpoints

### Authentication
- `POST /auth/register` — Register new user
- `POST /auth/login` — Login and get JWT token

### Documents
- `GET /documents/` — List all documents
- `POST /documents/upload` — Upload PDF document
- `GET /documents/{id}` — Get document details
- `PUT /documents/{id}` — Update document
- `DELETE /documents/{id}` — Delete document

### RAG Search
- `POST /rag/index-document/{id}` — Index document for semantic search
- `POST /rag/search` — Semantic search across indexed documents
- `GET /rag/context/{id}` — Get document context/summary

### User & Roles (Admin only)
- `GET /roles/` — List all roles
- `POST /users/assign-role` — Assign role to user
- `GET /users/` — List all users

Full API documentation available at `/docs` (Swagger UI) or `/redoc` (ReDoc) after running the server.

---

## Performance Tips

1. **First Search is Slow** — HuggingFace embeddings download (~90MB) on first use. Subsequent searches are fast.
2. **Batch Indexing** — Index multiple documents in parallel for better performance.
3. **Vector DB Optimization** — Increase `vector_size` in Qdrant config for better accuracy (trade-off with speed).
4. **Database Indexing** — PostgreSQL automatically indexes common queries.

---

## Contributing

Contributions are welcome! Please follow these steps:

1. **Fork** the repository
2. **Create** a feature branch (`git checkout -b feature/amazing-feature`)
3. **Commit** your changes (`git commit -m 'Add amazing feature'`)
4. **Push** to the branch (`git push origin feature/amazing-feature`)
5. **Open** a Pull Request

### Development Setup

```bash
git clone https://github.com/Bhavinpatel16/financial-rag.git
cd financial-rag
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
docker-compose up -d
python -m app.db.seed
uvicorn app.main:app --reload
```

---

## Support & Issues

Found a bug? Have a feature request?

- **GitHub Issues:** https://github.com/Bhavinpatel16/financial-rag/issues
- **Discussions:** https://github.com/Bhavinpatel16/financial-rag/discussions

---

## License

This project is licensed under the **MIT License** — see [LICENSE](LICENSE) file for details.

---

## Authors

- **Bhavin Patel** — Initial development

---

## Acknowledgments

- [FastAPI](https://fastapi.tiangolo.com/) - Modern web framework
- [LangChain](https://www.langchain.com/) - LLM orchestration
- [Qdrant](https://qdrant.tech/) - Vector database
- [HuggingFace](https://huggingface.co/) - Open-source ML models

---

**Happy coding! 🚀**
