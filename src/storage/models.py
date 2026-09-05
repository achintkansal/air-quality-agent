from datetime import datetime

from sqlalchemy import DateTime, Float, Integer, String, Text, UniqueConstraint
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


class Base(DeclarativeBase):
    pass


class Reading(Base):
    """
    Existing readings table used by the live ingestion process.
    """

    __tablename__ = "readings"

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        autoincrement=True,
    )

    city: Mapped[str | None] = mapped_column(
        String(100),
        nullable=True,
    )

    station_name: Mapped[str | None] = mapped_column(
        String(255),
        nullable=True,
    )

    location_id: Mapped[int | None] = mapped_column(
        Integer,
        nullable=True,
    )

    sensor_id: Mapped[int | None] = mapped_column(
        Integer,
        nullable=True,
    )

    parameter: Mapped[str | None] = mapped_column(
        String(50),
        nullable=True,
    )

    value: Mapped[float | None] = mapped_column(
        Float,
        nullable=True,
    )

    timestamp: Mapped[str | None] = mapped_column(
        String(50),
        nullable=True,
    )

    pushed_at: Mapped[str | None] = mapped_column(
        String(50),
        nullable=True,
    )


class NotificationState(Base):
    """
    Stores the last notification state for each city/station + pollutant.
    """

    __tablename__ = "notification_state"

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        autoincrement=True,
    )

    station_id: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
    )

    pollutant: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
    )

    last_notified_state: Mapped[str | None] = mapped_column(
        String(30),
        nullable=True,
    )

    last_notified_at: Mapped[datetime | None] = mapped_column(
        DateTime,
        nullable=True,
    )

    last_value: Mapped[float | None] = mapped_column(
        Float,
        nullable=True,
    )

    __table_args__ = (
        UniqueConstraint(
            "station_id",
            "pollutant",
            name="uq_notification_state_station_pollutant",
        ),
    )


class EventLog(Base):
    """
    Records every notification decision made by the agent.
    """

    __tablename__ = "event_log"

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        autoincrement=True,
    )

    station_id: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
    )

    pollutant: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
    )

    timestamp: Mapped[datetime] = mapped_column(
        DateTime,
        nullable=False,
    )

    decision: Mapped[str] = mapped_column(
        String(20),
        nullable=False,
    )

    reason: Mapped[str] = mapped_column(
        Text,
        nullable=False,
    )

    verdict: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
    )

class AgentCursor(Base):
    """
    Stores the last reading ID processed by the detection agent
    for each city.
    """

    __tablename__ = "agent_cursor"

    city: Mapped[str] = mapped_column(
        String(100),
        primary_key=True,
    )

    last_processed_reading_id: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        default=0,
    )