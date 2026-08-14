from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.config import settings
from app.api.webhook import router as webhook_router
from app.db.models import Base
from app.db.session import engine


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Initialize tables if not existing
    try:
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
    except Exception as e:
        print(f"[Warning] Database initialization note: {e}")
    yield


app = FastAPI(
    title="WhatsApp Sales-Qualification Backend",
    description="Multi-tenant WhatsApp sales qualification backend with PostgreSQL RLS, LangGraph, and Claude API.",
    version="1.0.0",
    lifespan=lifespan
)

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register routers
app.include_router(webhook_router)


@app.get("/health", tags=["Health"])
@app.get("/", tags=["Health"])
async def health_check():
    return {
        "status": "healthy",
        "service": "whatsapp-sales-backend",
        "environment": settings.ENVIRONMENT,
        "database": "PostgreSQL (RLS Enabled)" if "postgres" in settings.DATABASE_URL else "SQLite (Local Dev)",
        "claude_model": settings.CLAUDE_MODEL
    }
