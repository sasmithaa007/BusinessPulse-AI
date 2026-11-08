"""
backend/main.py
----------------
FastAPI entry point for the BusinessPulse AI backend application.
"""

from __future__ import annotations

import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import settings
from app.core.security import hash_password
from app.database.base import Base
from app.database.connection import SessionLocal, engine
from app.models.user import User
from app.models.customer import Customer
from app.services.data_generator import DataGenerator

# Import all routers
from app.routers import (
    auth,
    churn,
    customers,
    dashboard,
    datasets,
    insights,
    operations,
    performance,
    products,
    reports,
    retention,
    revenue,
    segmentation,
    transactions,
)

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - [%(levelname)s] - %(name)s - %(message)s",
)
logger = logging.getLogger("businesspulse")


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan context manager for startup and shutdown events."""
    logger.info("Initializing BusinessPulse AI database tables...")
    Base.metadata.create_all(bind=engine)

    # Initialize demo admin user and synthetic data if needed
    db = SessionLocal()
    try:
        admin_user = (
            db.query(User).filter(User.email == settings.DEMO_ADMIN_EMAIL).first()
        )
        if not admin_user:
            logger.info("Creating default demo admin user: %s", settings.DEMO_ADMIN_EMAIL)
            admin = User(
                name="Demo Administrator",
                email=settings.DEMO_ADMIN_EMAIL,
                password_hash=hash_password(settings.DEMO_ADMIN_PASSWORD),
                role="admin",
                is_active=True,
            )
            db.add(admin)
            db.commit()

        # Check if database has synthetic data
        customer_count = db.query(Customer).count()
        if customer_count == 0:
            logger.info("Database is empty. Seeding initial synthetic data for demo...")
            generator = DataGenerator(seed=42)
            generator.generate_all_data(db)
            logger.info("Synthetic data generation completed successfully.")
        else:
            logger.info("Database already seeded with %d customers.", customer_count)
    except Exception as exc:
        logger.error("Error during startup data initialization: %s", exc, exc_info=True)
        db.rollback()
    finally:
        db.close()

    yield
    logger.info("BusinessPulse AI backend shutting down...")


app = FastAPI(
    title="BusinessPulse AI API",
    description="Unified Customer, Revenue & Operational Intelligence Platform",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan,
)

# CORS setup
origins = [
    "http://localhost:5173",
    "http://127.0.0.1:5173",
    "http://localhost:3000",
    settings.FRONTEND_URL,
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include all API routers (specific sub-paths first to avoid /{id} capture)
app.include_router(auth.router)
app.include_router(dashboard.router)
app.include_router(churn.router)
app.include_router(retention.router)
app.include_router(segmentation.router)
app.include_router(customers.router)
app.include_router(revenue.router)
app.include_router(transactions.router)
app.include_router(products.router)
app.include_router(performance.router)
app.include_router(operations.router)
app.include_router(insights.router)
app.include_router(datasets.router)
app.include_router(reports.router)


@app.get("/", tags=["General"])
def root():
    return {
        "name": "BusinessPulse AI API",
        "version": "1.0.0",
        "description": "Unified Customer, Revenue & Operational Intelligence Platform",
        "docs": "/docs",
        "status": "online",
        "demo_account": {
            "email": settings.DEMO_ADMIN_EMAIL,
            "password": settings.DEMO_ADMIN_PASSWORD,
        },
    }


@app.get("/health", tags=["General"])
def health_check():
    return {"status": "healthy"}
