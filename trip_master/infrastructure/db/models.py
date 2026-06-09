from datetime import datetime

from sqlalchemy import BigInteger, Boolean, DateTime, Enum, ForeignKey, Integer, String, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship

from trip_master.domain.enums import Category, TripStatus


class Base(DeclarativeBase):
    pass


class TripModel(Base):
    __tablename__ = "trips"

    id: Mapped[str] = mapped_column(UUID(as_uuid=False), primary_key=True)
    chat_id: Mapped[int] = mapped_column(BigInteger, index=True, nullable=False)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    status: Mapped[TripStatus] = mapped_column(
        Enum(TripStatus, name="trip_status"), default=TripStatus.active, nullable=False
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False
    )

    items: Mapped[list["ItemModel"]] = relationship(back_populates="trip", cascade="all, delete-orphan")


class ItemModel(Base):
    __tablename__ = "items"

    id: Mapped[str] = mapped_column(UUID(as_uuid=False), primary_key=True)
    trip_id: Mapped[str] = mapped_column(
        UUID(as_uuid=False), ForeignKey("trips.id", ondelete="CASCADE"), nullable=False, index=True
    )
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    category: Mapped[Category] = mapped_column(
        Enum(Category, name="item_category"), nullable=False
    )
    amount: Mapped[str] = mapped_column(String(100), default="", nullable=False)
    is_bought: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    buyer_id: Mapped[int | None] = mapped_column(BigInteger, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False
    )

    trip: Mapped[TripModel] = relationship(back_populates="items")
