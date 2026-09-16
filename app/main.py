import os
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse

from app.config import settings
from app.api.webhook import router as webhook_router
from app.api.chat_router import router as chat_router
from app.api.crm_router import router as crm_router
from app.api.solevault_router import router as solevault_router
from app.db.models import Base
from app.db.solevault_models import Base as SolevaultBase
from app.db.session import engine, AsyncSessionLocal
from app.db.seed_solevault import seed_solevault_database
from app.services.firebase_service import firebase_service


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Initialize relational tables for both CRM and SOLEVAULT E-Commerce
    try:
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
            await conn.run_sync(SolevaultBase.metadata.create_all)
    except Exception as e:
        print(f"[Warning] Database table creation note: {e}")

    # Seed SOLEVAULT relational database
    try:
        async with AsyncSessionLocal() as db_session:
            await seed_solevault_database(db_session)
    except Exception as e:
        print(f"[Warning] SOLEVAULT relational seed note: {e}")

    # Ensure StrideHub initial data is seeded into Firestore
    try:
        firebase_service.seed_stridehub_shoe_data("stridehub-shoes")
    except Exception as e:
        print(f"[Warning] Firebase seed note: {e}")

    yield


app = FastAPI(
    title="SOLEVAULT & StrideHub - AI Footwear E-Commerce & WhatsApp CRM",
    description="Modern, production-ready shoe brand e-commerce platform and executive dashboard called SOLEVAULT with 45+ tables and 100+ entity fields, combined with real-time AI WhatsApp Sales Agent.",
    version="2.1.0",
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

# Register API Routers
app.include_router(solevault_router)
app.include_router(chat_router)
app.include_router(crm_router)
app.include_router(webhook_router)


@app.get("/health", tags=["Health"])
async def health_check():
    return {
        "status": "healthy",
        "service": "stridehub-ai-sales-agent",
        "environment": settings.ENVIRONMENT,
        "ai_provider": settings.AI_PROVIDER,
        "gemini_model": settings.GEMINI_MODEL,
        "firebase_project": "ai-sales-agent---shoe",
        "firebase_firestore": "connected" if firebase_service.is_healthy() else "mock_store",
        "database": "PostgreSQL (RLS Enabled)" if "postgres" in settings.DATABASE_URL else "SQLite (Local Dev)"
    }


# Serve static web frontend if static folder exists
static_dir = os.path.join(os.path.dirname(__file__), "static")
if os.path.exists(static_dir):
    app.mount("/static", StaticFiles(directory=static_dir), name="static")

    @app.get("/")
    async def serve_index():
        return FileResponse(os.path.join(static_dir, "index.html"))
