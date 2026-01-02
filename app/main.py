import sys
from pathlib import Path
# Add parent directory to path when running as script
if __name__ == "__main__":
    sys.path.insert(0, str(Path(__file__).parent.parent))

from contextlib import asynccontextmanager
from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse
from fastapi.middleware.cors import CORSMiddleware
from app.config import settings
from app.database import engine, Base
from app.routers import auth, customers, inventory, barbershop, cafe, invoices, reports
from app.init import auto_setup


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifespan context manager for startup and shutdown events"""
    # Startup: Auto-initialize the application
    print("\n" + "=" * 60)
    print("🚀 در حال راه‌اندازی Kagan ERP...")
    print("=" * 60)
    auto_setup()
    print("=" * 60)
    print(f"🚀 سرور در حال اجرا در http://localhost:8000")
    print(f"📚 مستندات API: http://localhost:8000/docs")
    print("=" * 60 + "\n")
    yield
    # Shutdown: cleanup if needed
    pass


# Create FastAPI app
app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description="سیستم ERP جامع برای مدیریت آرایشگاه و کافه",
    lifespan=lifespan,
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount static files
app.mount("/static", StaticFiles(directory="static"), name="static")

# Templates
templates = Jinja2Templates(directory="app/templates")

# Include routers
app.include_router(auth.router)
app.include_router(customers.router)
app.include_router(inventory.router)
app.include_router(barbershop.router)
app.include_router(cafe.router)
app.include_router(invoices.router)
app.include_router(reports.router)


@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    return templates.TemplateResponse("index.html", {"request": request, "app_name": settings.APP_NAME})


@app.get("/health")
async def health_check():
    return {"status": "healthy", "app": settings.APP_NAME, "version": settings.APP_VERSION}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)
