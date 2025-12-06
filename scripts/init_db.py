import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

from config.config import Base, engine

from models.models import User, CountyOffice, FoundItem

def init_db():
    print("creating tables")
    Base.metadata.create_all(bind=engine)
    print("finished")


if __name__ == "__main__":
    init_db()
