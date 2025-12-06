from typing import Optional, List
import uuid
from datetime import datetime
from sqlalchemy import String, Integer, DateTime, Table, Column, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from config.config import Base
from sqlalchemy import UniqueConstraint


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

    code: Mapped[str] = mapped_column(
        String(4),
        nullable=False,
        unique=True,
        index=True,
    )

    county_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("counties.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )

    county: Mapped[Optional["County"]] = relationship(
        "County",
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

    county_office_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("county_offices.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )

    county_office: Mapped[Optional["CountyOffice"]] = relationship(
        "CountyOffice",
        lazy="joined",
    )

    registry_number: Mapped[Optional[str]] = mapped_column(
        String(32),
        nullable=True,
        unique=True,
        index=True,
    )

class RegistryCounter(Base):
    __tablename__ = "registry_counters"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    county_office_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("county_offices.id", ondelete="CASCADE"),
        nullable=False,
    )
    year: Mapped[int] = mapped_column(Integer, nullable=False)
    value: Mapped[int] = mapped_column(Integer, nullable=False, default=0)

    __table_args__ = (
        UniqueConstraint("county_office_id", "year", name="uq_registry_counter_office_year"),
    )

class Voivodeship(Base):
    __tablename__ = "voivodeships"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4
    )

    name: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
        unique=True
    )

    # krótki kod do numeracji/identyfikacji, np. "MA", "MZ"
    code: Mapped[str] = mapped_column(
        String(4),
        nullable=False,
        unique=True,
        index=True
    )

    counties: Mapped[List["County"]] = relationship(
        "County",
        back_populates="voivodeship",
        cascade="all, delete-orphan",
        passive_deletes=True,
    )


class County(Base):
    __tablename__ = "counties"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4
    )

    name: Mapped[str] = mapped_column(
        String(120),
        nullable=False
    )

    # kod powiatu (Twój wewnętrzny), np. "KR", "WA", itd.
    code: Mapped[str] = mapped_column(
        String(6),
        nullable=False,
        index=True
    )

    voivodeship_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("voivodeships.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )

    voivodeship: Mapped["Voivodeship"] = relationship(
        "Voivodeship",
        back_populates="counties",
    )

    county_offices: Mapped[List["CountyOffice"]] = relationship(
        "CountyOffice",
        back_populates="county",
        cascade="all",
        passive_deletes=True,
    )

    __table_args__ = (
        UniqueConstraint("voivodeship_id", "code", name="uq_county_voiv_code"),
    )