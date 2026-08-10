from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from contextlib import asynccontextmanager
import os
from dotenv import load_dotenv

# Load .env configuration from root and backend
root_env = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), ".env")
backend_env = os.path.join(os.path.dirname(os.path.dirname(__file__)), ".env")
if os.path.exists(root_env):
    load_dotenv(root_env)
if os.path.exists(backend_env):
    load_dotenv(backend_env)

from app.routes.articles import router as articles_router
from app.routes.pdf_routes import router as pdf_router
from app.routes.analytics_routes import router as analytics_router
from app.routes.collector_routes import router as collector_router
from app.scheduler.jobs import start_scheduler, stop_scheduler
from app.services.storage import db_storage

# Ensure pdfs directory exists
PDF_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "pdfs")
os.makedirs(PDF_DIR, exist_ok=True)

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup actions
    print("Initializing WildTN-News FastAPI Backend...")
    try:
        start_scheduler()
    except Exception as e:
        print(f"Scheduler start warning: {e}")
    yield
    # Shutdown actions
    stop_scheduler()

app = FastAPI(
    title="WildTN-News API",
    description="Wildlife & Conservation Intelligence Platform for Tamil Nadu",
    version="1.0.0",
    lifespan=lifespan
)

# CORS Configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Static mounting for PDF downloads
app.mount("/pdfs", StaticFiles(directory=PDF_DIR), name="pdfs")

# API Routers
app.include_router(articles_router)
app.include_router(pdf_router)
app.include_router(analytics_router)
app.include_router(collector_router)

@app.get("/")
def root():
    return {
        "status": "Online",
        "system": "WildTN-News Platform API",
        "docs": "/docs",
        "total_articles": len(db_storage.articles)
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)
