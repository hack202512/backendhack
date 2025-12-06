import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

# Pobierz DATABASE_URL z zmiennych środowiskowych (Railway automatycznie ustawia to)
# SQLAlchemy 2.x z psycopg2-binary automatycznie wykryje driver z postgresql://
DB_URL = os.getenv(
    "DATABASE_URL",
    "postgresql+psycopg2://admin:admin@localhost:9337/postgres"  # Fallback dla lokalnego dev
)

engine = create_engine(DB_URL, echo=True, future=True)

SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine,
)

Base = declarative_base()
