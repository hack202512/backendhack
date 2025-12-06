import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

# Pobierz DATABASE_URL z zmiennych środowiskowych (Railway automatycznie ustawia to)
raw_db_url = os.getenv("DATABASE_URL")

if raw_db_url:
    # Railway zwykle dostarcza postgresql://, ale SQLAlchemy z psycopg2 potrzebuje postgresql+psycopg2://
    if raw_db_url.startswith("postgresql://"):
        DB_URL = raw_db_url.replace("postgresql://", "postgresql+psycopg2://", 1)
    elif raw_db_url.startswith("postgres://"):
        DB_URL = raw_db_url.replace("postgres://", "postgresql+psycopg2://", 1)
    else:
        DB_URL = raw_db_url
else:
    # Fallback tylko dla lokalnego developmentu
    DB_URL = "postgresql+psycopg2://admin:admin@localhost:9337/postgres"

engine = create_engine(DB_URL, echo=True, future=True)

SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine,
)

Base = declarative_base()
