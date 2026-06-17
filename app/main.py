from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse

from app.core.config import settings
from app.db.database import create_tables
from app.api.routes import auth, documents, roles, rag

import app.models.user  
import app.models.document  

app = FastAPI(
    title=settings.APP_NAME,
    description="Financial Document Management with RAG-powered Semantic Search",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
def on_startup():
    create_tables()


# ── Routers 
app.include_router(auth.router)
app.include_router(documents.router)
app.include_router(roles.router)
app.include_router(rag.router)


@app.get("/", tags=["UI"])
def root():
    return FileResponse("app/static/index.html")


@app.get("/health", tags=["Health"])
def health():
    return {"status": "healthy"}
