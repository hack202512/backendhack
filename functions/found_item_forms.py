from typing import List
from io import BytesIO
from datetime import datetime, time

from fastapi import APIRouter, Depends, HTTPException, Query, status
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session

from context.db import get_db
from functions.auth import get_current_user_token
from models.models import FoundItem, User
from schemas.found_item_form import FoundItemFormRequest, FoundItemFormResponse

try:
    import openpyxl
except ImportError:  # pragma: no cover
    openpyxl = None


router = APIRouter(prefix="/found-item-forms", tags=["found-item-forms"])


def require_user(
    token_data: dict = Depends(get_current_user_token),
    db: Session = Depends(get_db),
) -> User:
    user_id = token_data.get("user_id")
    if not user_id:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token payload")

    user = db.query(User).filter(User.id == int(user_id)).first()
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="User not found")
    return user


def to_form_response(i: FoundItem) -> FoundItemFormResponse:
    created_at = getattr(i, "created_at", None)
    if not created_at:
        from datetime import timezone
        created_at = datetime.now(timezone.utc)

    found_date = getattr(i, "found_date", None)
    found_date_date = found_date.date() if found_date else None

    return FoundItemFormResponse(
        id=str(getattr(i, "id")),
        item_name=getattr(i, "item_name", "") or getattr(i, "name", "") or "",
        item_color=getattr(i, "item_color", None),
        item_brand=getattr(i, "item_brand", None),
        found_location=getattr(i, "found_location", None),
        found_date=found_date_date,
        found_time=getattr(i, "found_time", None),
        circumstances=getattr(i, "circumstances", None),
        found_by_firstname=getattr(i, "found_by_firstname", None),
        found_by_lastname=getattr(i, "found_by_lastname", None),
        found_by_phonenumber=getattr(i, "found_by_phonenumber", None),
        created_at=created_at,
    )


@router.post("/", response_model=FoundItemFormResponse, status_code=201)
def add_found_item(
    payload: FoundItemFormRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_user),
):
    item = FoundItem()

    item.item_name = payload.item_name.strip()
    item.item_color = payload.item_color.strip() if payload.item_color else None
    item.item_brand = payload.item_brand.strip() if payload.item_brand else None
    item.found_location = payload.found_location.strip()

    if payload.found_time:
        try:
            time_obj = datetime.strptime(payload.found_time, "%H:%M").time()
            item.found_date = datetime.combine(payload.found_date, time_obj)
        except ValueError:
            item.found_date = datetime.combine(payload.found_date, time.min)
    else:
        item.found_date = datetime.combine(payload.found_date, time.min)

    item.found_time = payload.found_time.strip() if payload.found_time else None
    item.circumstances = payload.circumstances.strip() if payload.circumstances else None
    item.found_by_firstname = payload.found_by_firstname.strip() if payload.found_by_firstname else None
    item.found_by_lastname = payload.found_by_lastname.strip() if payload.found_by_lastname else None
    item.found_by_phonenumber = payload.found_by_phonenumber.strip() if payload.found_by_phonenumber else None
    item.user_id = current_user.id

    db.add(item)
    db.commit()
    db.refresh(item)

    return to_form_response(item)


@router.get("/my", response_model=List[FoundItemFormResponse])
def list_my_found_items(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_user),
):
    if not hasattr(FoundItem, "user_id"):
        raise HTTPException(500, detail="Model FoundItem missing user_id field")

    order_col = getattr(FoundItem, "created_at", None) or getattr(FoundItem, "id")
    items = (
        db.query(FoundItem)
        .filter(FoundItem.user_id == current_user.id)
        .order_by(order_col.desc())
        .all()
    )
    return [to_form_response(i) for i in items]


@router.get("/export")
def export_my_forms(
    format: str = Query("excel", pattern="^(excel|json|csv)$"),
    db: Session = Depends(get_db),
    current_user: User = Depends(require_user),
):
    order_col = getattr(FoundItem, "created_at", None) or getattr(FoundItem, "id")
    items = (
        db.query(FoundItem)
        .filter(FoundItem.user_id == current_user.id)
        .order_by(order_col.desc())
        .all()
    )
    mapped = [to_form_response(i) for i in items]


    if format == "csv":
        import csv
        from io import StringIO

        output = StringIO()
        writer = csv.writer(output)

        writer.writerow([
            "id",
            "item_name",
            "found_location",
            "found_date",
            "created_at",
        ])

        for m in mapped:
            writer.writerow([
                m.id,
                m.item_name,
                m.found_location or "",
                m.found_date.isoformat() if m.found_date else "",
                m.created_at.isoformat() if m.created_at else "",
            ])

        csv_bytes = output.getvalue().encode("utf-8")
        output.close()

        headers = {"Content-Disposition": "attachment; filename=found_items.csv"}
        return StreamingResponse(
            BytesIO(csv_bytes),
            media_type="text/csv; charset=utf-8",
            headers=headers,
        )

    elif format == "json":
        import json

        data = []
        for m in mapped:
            data.append({
                "id": m.id,
                "item_name": m.item_name,
                "item_color": m.item_color,
                "item_brand": m.item_brand,
                "found_location": m.found_location,
                "found_date": m.found_date.isoformat() if m.found_date else None,
                "created_at": m.created_at.isoformat() if m.created_at else None,
            })

        buf = BytesIO(json.dumps(data, ensure_ascii=False, indent=2).encode("utf-8"))
        headers = {"Content-Disposition": "attachment; filename=found_items.json"}
        return StreamingResponse(buf, media_type="application/json", headers=headers)

    if openpyxl is None:
        raise HTTPException(500, detail="openpyxl not installed. Add it to requirements.")

    wb = openpyxl.Workbook()
    ws = wb.active
    ws.title = "Found items"

    ws.append([
        "ID",
        "Item name",
        "Color",
        "Brand",
        "Found location",
        "Found date",
        "Created at",
    ])

    for m in mapped:
        ws.append([
            m.id,
            m.item_name,
            m.item_color,
            m.item_brand,
            m.found_location,
            m.found_date.isoformat() if m.found_date else None,
            m.created_at.isoformat() if m.created_at else None,
        ])

    stream = BytesIO()
    wb.save(stream)
    stream.seek(0)

    headers = {"Content-Disposition": "attachment; filename=found_items.xlsx"}
    return StreamingResponse(
        stream,
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        headers=headers,
    )


@router.get("/{item_id}", response_model=FoundItemFormResponse)
def get_found_item(
    item_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_user),
):
    item = (
        db.query(FoundItem)
        .filter(FoundItem.id == item_id, FoundItem.user_id == current_user.id)
        .first()
    )
    if not item:
        raise HTTPException(404, detail="Form not found")
    return to_form_response(item)