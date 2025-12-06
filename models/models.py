from typing import Optional, List
import uuid
from datetime import datetime
from sqlalchemy import String, Integer, DateTime, Table, Column, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from config.config import Base


starostwo_users = Table(
    "starostwo_users",
    Base.metadata,
    Column(
        "county_office_id",
        UUID(as_uuid=True),
        ForeignKey("county_offices.id", ondelete="CASCADE"),
        primary_key=True,
    ),
    Column(
        "user_id",
        Integer,
        ForeignKey("users.id", ondelete="CASCADE"),
        primary_key=True,
    ),
)


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        index=True
    )

    first_name: Mapped[str] = mapped_column(
        String(100),
        nullable=False
    )

    last_name: Mapped[str] = mapped_column(
        String(100),
        nullable=False
    )

    email: Mapped[str] = mapped_column(
        String(255),
        unique=True,
        index=True,
        nullable=False
    )

    hashed_password: Mapped[str] = mapped_column(
        String(255),
        nullable=False
    )

    county_offices: Mapped[List["CountyOffice"]] = relationship(
        "CountyOffice",
        secondary=starostwo_users,
        back_populates="users",
    )

    fulfilled_forms: Mapped[List["FoundItem"]] = relationship(
        "FoundItem",
        back_populates="user",
        cascade="all, delete-orphan",
        passive_deletes=True,
    )


class CountyOffice(Base):
    __tablename__ = "county_offices"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4
    )

    county_name: Mapped[str] = mapped_column(
        String(100),
        nullable=False
    )

    users: Mapped[List[User]] = relationship(
        "User",
        secondary=starostwo_users,
        back_populates="county_offices",
    )


class FoundItem(Base):
    __tablename__ = "found_items"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4
    )

    item_name: Mapped[str] = mapped_column(
        String(500),
        nullable=False
    )

    item_color: Mapped[Optional[str]] = mapped_column(
        String(100),
        nullable=True
    )

    item_brand: Mapped[Optional[str]] = mapped_column(
        String(100),
        nullable=True
    )

    found_location: Mapped[Optional[str]] = mapped_column(
        String(255),
        nullable=True
    )

    found_date: Mapped[Optional[datetime]] = mapped_column(
        DateTime,
        default=datetime.utcnow,
        nullable=True
    )

    found_time: Mapped[Optional[str]] = mapped_column(
        String(5),
        nullable=True
    )

    circumstances: Mapped[Optional[str]] = mapped_column(
        String(500),
        nullable=True
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=datetime.utcnow,
        nullable=False,
    )

    found_by_firstname: Mapped[Optional[str]] = mapped_column(
        String(100),
        nullable=True
    )

    found_by_lastname: Mapped[Optional[str]] = mapped_column(
        String(100),
        nullable=True
    )

    found_by_phonenumber: Mapped[Optional[str]] = mapped_column(
        String(22),
        nullable=True
    )

    user_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
    )

    user: Mapped["User"] = relationship(
        "User",
        back_populates="fulfilled_forms",
    )
