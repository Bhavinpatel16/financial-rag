# Financial RAG - Document Management API

![Python](https://img.shields.io/badge/Python-3.11+-blue?style=flat-square)
![FastAPI](https://img.shields.io/badge/FastAPI-Latest-green?style=flat-square)
![License](https://img.shields.io/badge/License-MIT-yellow?style=flat-square)
![Status](https://img.shields.io/badge/Status-Active-brightgreen?style=flat-square)

Financial RAG is a FastAPI application for managing financial documents with AI-powered semantic search. It includes JWT authentication, role-based access control, PDF upload and extraction, and a Retrieval-Augmented Generation pipeline using LangChain, Qdrant, and HuggingFace embeddings.

GitHub Repository: https://github.com/Bhavinpatel16/financial-rag

---

## Features

- PDF document upload, storage, and management
- AI-powered semantic search with natural language queries
- RAG pipeline with LangChain and Qdrant
- JWT authentication
- Role-based access control for Admin, Analyst, Auditor, and Client users
- Local HuggingFace embeddings with no API key required
- PostgreSQL database with SQLAlchemy ORM
- Interactive API documentation through Swagger UI and ReDoc
- Docker Compose setup for PostgreSQL and Qdrant

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
|-----------|------------|
| Backend Framework | FastAPI |
| Authentication | JWT + RBAC |
| Database | PostgreSQL |
| Vector Database | Qdrant |
| Embeddings | HuggingFace sentence-transformers |
| RAG Framework | LangChain |
| ORM | SQLAlchemy |
| PDF Processing | PyPDF |
| API Docs | Swagger UI + ReDoc |
| Containerization | Docker Compose |

---

## Quick Start

### 1. Clone the repository

```bash
git clone https://github.com/Bhavinpatel16/financial-rag.git
cd financial-rag
```

### 2. Create and activate a virtual environment

```bash
python -m venv venv
```

On Windows:

```bash
venv\Scripts\activate
```

On macOS/Linux:

```bash
source venv/bin/activate
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure environment variables

```bash
cp .env.example .env
```

The default values are intended for the local Docker setup.

### 5. Start PostgreSQL and Qdrant

```bash
docker-compose up -d
```

### 6. Seed the database

```bash
python -m app.db.seed
```

This creates default permissions, roles, and the admin user.

Default admin credentials:

- Username: `admin`
- Password: `Admin@1234`

### 7. Run the API

```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

Open:

- API: http://localhost:8000
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

---

## Environment Variables

Key settings from `.env.example`:

```env
DATABASE_URL=postgresql://postgres:password@localhost:5432/financial_rag
SECRET_KEY=your-super-secret-key-change-this-in-production-min-32-chars
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=60
USE_LOCAL_EMBEDDINGS=true
EMBEDDING_MODEL=sentence-transformers/all-MiniLM-L6-v2
QDRANT_URL=http://localhost:6333
QDRANT_COLLECTION_NAME=financial_documents
CORS_ORIGINS=["http://localhost:3000","http://localhost:8000"]
```

With `USE_LOCAL_EMBEDDINGS=true`, the project uses HuggingFace embeddings locally. To use OpenAI embeddings instead, set `USE_LOCAL_EMBEDDINGS=false` and provide `OPENAI_API_KEY`.

---

## API Usage

### Register a user

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

### Login

```bash
curl -X POST http://localhost:8000/auth/login \
  -F "username=admin" \
  -F "password=Admin@1234"
```

Copy the `access_token` from the response and pass it as a Bearer token in protected requests.

### Assign a role

```bash
curl -X POST http://localhost:8000/users/assign-role \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"user_id": 2, "role_id": 2}'
```

### Upload a PDF document

```bash
curl -X POST http://localhost:8000/documents/upload \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -F "title=Q4 Financial Report" \
  -F "company_name=Acme Corp" \
  -F "document_type=report" \
  -F "file=@/path/to/report.pdf"
```

### Index a document for search

```bash
curl -X POST http://localhost:8000/rag/index-document/1 \
  -H "Authorization: Bearer YOUR_TOKEN"
```

### Search indexed documents

```bash
curl -X POST http://localhost:8000/rag/search \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"query": "financial risk related to high debt ratio", "top_k": 5}'
```

### Get document context

```bash
curl -X GET http://localhost:8000/rag/context/1 \
  -H "Authorization: Bearer YOUR_TOKEN"
```

---

## API Endpoints

### Authentication

- `POST /auth/register` - Register a new user
- `POST /auth/login` - Login and receive a JWT token

### Documents

- `GET /documents/` - List documents
- `POST /documents/upload` - Upload a PDF document
- `GET /documents/{id}` - Get document details
- `PUT /documents/{id}` - Update a document
- `DELETE /documents/{id}` - Delete a document

### RAG

- `POST /rag/index-document/{id}` - Index a document for semantic search
- `POST /rag/search` - Search indexed documents
- `GET /rag/context/{id}` - Get document context

### Roles and Users

- `GET /roles/` - List roles
- `POST /users/assign-role` - Assign a role to a user
- `GET /users/` - List users

---

## RBAC Permission Summary

| Role | Access |
|------|--------|
| Admin | Full access to all operations |
| Analyst | Upload, read, edit, index, and search documents |
| Auditor | Read and review documents; search RAG |
| Client | View own documents only |

---

## RAG Pipeline

```text
PDF Upload
  -> Text Extraction with PyPDF
  -> Chunking with LangChain
  -> Embeddings with sentence-transformers
  -> Vector Storage in Qdrant

Query Time
  -> User Query
  -> Query Embedding
  -> Vector Search
  -> Financial Keyword Reranking
  -> Top Relevant Chunks
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
| PostgreSQL connection refused | Run `docker-compose up -d` and confirm the database container is running |
| Qdrant connection refused | Confirm the Qdrant container is running on port `6333` |
| `ModuleNotFoundError` | Activate the virtual environment and run `pip install -r requirements.txt` |
| Slow first search | The HuggingFace model may download on first use |
| `403 Forbidden` | Assign the required role through `/users/assign-role` |

---

## Production Checklist

- Change `SECRET_KEY` to a strong random value
- Set `DEBUG=false`
- Use environment variables in production
- Configure HTTPS
- Restrict CORS origins to trusted frontend domains
- Use managed PostgreSQL for production workloads
- Use managed Qdrant or a persistent Qdrant deployment

---

## Contributing

1. Fork the repository.
2. Create a feature branch.
3. Commit your changes.
4. Push the branch.
5. Open a pull request.

---

## License

This project is licensed under the MIT License. See `LICENSE` for details.

---

## Author

Bhavin Patel

---

## Acknowledgments

- [FastAPI](https://fastapi.tiangolo.com/)
- [LangChain](https://www.langchain.com/)
- [Qdrant](https://qdrant.tech/)
- [HuggingFace](https://huggingface.co/)
