"""FastAPI dependencies."""

from src.storage.database import db


def get_database():
    """Get database instance."""
    return db

