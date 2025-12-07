from sqlalchemy.orm import Session
import inspect
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

from models.models import User, CountyOffice
from context.db import get_db


def add_bydgoszcz_county_office_and_assign_user(db: Session) -> CountyOffice:


    user_email = "jankowalski@gmail.com"


    user = db.query(User).filter(User.email == user_email).one_or_none()
    if user is None:
        raise ValueError(f"Nie znaleziono użytkownika o emailu: {user_email}")


    bydgoszcz_office = (
        db.query(CountyOffice)
        .filter(CountyOffice.code == "0403")
        .one_or_none()
    )

    if bydgoszcz_office is None:

        bydgoszcz_office = CountyOffice(
            county_name="Starostwo Powiatowe w Bydgoszczy",
            code="0403",
            voivodeship_name="kujawsko-pomorskie",
            voivodeship_code="04",
            county_code="0403",
        )
        db.add(bydgoszcz_office)
        db.flush()


    if bydgoszcz_office not in user.county_offices:
        user.county_offices.append(bydgoszcz_office)

    db.commit()
    db.refresh(bydgoszcz_office)

    return bydgoszcz_office


def acquire_db():
    db_obj = get_db()
    if inspect.isgenerator(db_obj):
        db_gen = db_obj
        db = next(db_gen)
        return db, db_gen
    return db_obj, None

def main():
    db, db_gen = acquire_db()
    try:
        office = add_bydgoszcz_county_office_and_assign_user(db)
        print("Zwrócony obiekt:", office)
    finally:
        if db_gen is not None:
            try:
                db_gen.close()
            except Exception:
                pass
        else:
            try:
                db.close()
            except Exception:
                pass

if __name__ == "__main__":
    main()
