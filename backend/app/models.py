"""
SQLAlchemy ORM models for BusinessPulse AI.
"""
from sqlalchemy import (
    Column, Integer, String, Float, Boolean, DateTime, Text, ForeignKey, Enum
)
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import enum
from app.database import Base


class UserRole(str, enum.Enum):
    admin = "admin"
    analyst = "analyst"
    viewer = "viewer"


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    full_name = Column(String, nullable=False)
    hashed_password = Column(String, nullable=False)
    role = Column(String, default="analyst")
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())


class Customer(Base):
    __tablename__ = "customers"

    id = Column(Integer, primary_key=True, index=True)
    scenario = Column(String, index=True, nullable=False, default="fintech")
    name = Column(String, nullable=False)
    email = Column(String, index=True)
    segment = Column(String, index=True)  # enterprise, smb, startup, individual
    status = Column(String, index=True)   # active, inactive, churned
    subscription_plan = Column(String)
    lifetime_value = Column(Float, default=0.0)
    churn_risk_score = Column(Float, default=0.0)  # 0-100
    signup_date = Column(DateTime(timezone=True))
    last_activity_date = Column(DateTime(timezone=True))
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    transactions = relationship("Transaction", back_populates="customer")
    usage_events = relationship("UsageEvent", back_populates="customer")


class Transaction(Base):
    __tablename__ = "transactions"

    id = Column(Integer, primary_key=True, index=True)
    scenario = Column(String, index=True, nullable=False, default="fintech")
    customer_id = Column(Integer, ForeignKey("customers.id"), index=True)
    amount = Column(Float, nullable=False)
    status = Column(String, index=True)        # success, failed, pending
    payment_method = Column(String, index=True)  # card, bank_transfer, wallet
    failure_reason = Column(String, nullable=True)
    transaction_date = Column(DateTime(timezone=True), index=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    customer = relationship("Customer", back_populates="transactions")


class UsageEvent(Base):
    __tablename__ = "usage_events"

    id = Column(Integer, primary_key=True, index=True)
    scenario = Column(String, index=True, nullable=False, default="fintech")
    customer_id = Column(Integer, ForeignKey("customers.id"), index=True)
    feature_name = Column(String, index=True)
    event_count = Column(Integer, default=1)
    event_date = Column(DateTime(timezone=True), index=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    customer = relationship("Customer", back_populates="usage_events")


class PerformanceLog(Base):
    __tablename__ = "performance_logs"

    id = Column(Integer, primary_key=True, index=True)
    scenario = Column(String, index=True, nullable=False, default="fintech")
    endpoint = Column(String, index=True)
    method = Column(String)
    response_time_ms = Column(Float)
    status_code = Column(Integer, index=True)
    error_message = Column(Text, nullable=True)
    logged_at = Column(DateTime(timezone=True), index=True, server_default=func.now())


class OperationalProcess(Base):
    __tablename__ = "operational_processes"

    id = Column(Integer, primary_key=True, index=True)
    scenario = Column(String, index=True, nullable=False, default="fintech")
    process_name = Column(String, index=True)
    status = Column(String, index=True)  # success, failed, running
    processing_time_ms = Column(Float)
    cost = Column(Float, default=0.0)
    error_message = Column(Text, nullable=True)
    executed_at = Column(DateTime(timezone=True), index=True, server_default=func.now())
