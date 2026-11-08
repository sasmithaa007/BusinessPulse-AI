"""
app/database/base.py
--------------------
Declarative base shared by all SQLAlchemy models.
"""

from sqlalchemy.orm import declarative_base

Base = declarative_base()
