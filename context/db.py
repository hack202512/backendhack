from fastapi import FastAPI, Depends
from sqlalchemy.orm import Session
from config.config import SessionLocal, Base, engine

Base.metadata.create_all(bind=engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
