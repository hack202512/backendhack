import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

DB_URL = os.getenv(
    "DATABASE_URL",
    #"postgresql://postgres:tCZqteJQyDRWSOJuCLPlANDKDNXKbppa@postgres.railway.internal:5432/railway"
     "postgresql+psycopg2://admin:admin@localhost:9337/postgres",
)

engine = create_engine(DB_URL, echo=True, future=True)

SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine,
)

Base = declarative_base()
