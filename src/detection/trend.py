from dataclasses import dataclass

from sqlalchemy import select
from sqlalchemy.orm import Session

from src.storage.models import Reading


@dataclass
class TrendResult:
    is_sustained_trend: bool
    increase: float
    reason: str


def detect_sustained_trend(
    session: Session,
    city: str,
    readings_count: int = 12,
    min_increasing_points: int = 8,
) -> TrendResult:
    """
    Detect whether PM2.5 has been consistently increasing.

    readings_count=12 means approximately the last hour
    when readings arrive every 5 minutes.
    """

    result = session.execute(
        select(Reading.value)
        .where(
            Reading.city == city,
            Reading.parameter == "pm25",
            Reading.value.is_not(None),
        )
        .order_by(Reading.id.desc())
        .limit(readings_count)
    )

    values = [value for (value,) in result.all()]
    values.reverse()

    if len(values) < min_increasing_points:
        return TrendResult(
            is_sustained_trend=False,
            increase=0.0,
            reason="Not enough recent readings to detect a sustained trend",
        )

    increasing_points = sum(
        current > previous
        for previous, current in zip(values, values[1:])
    )

    increase = values[-1] - values[0]

    is_sustained_trend = (
        increasing_points >= min_increasing_points
        and increase > 0
    )

    if is_sustained_trend:
        reason = (
            f"PM2.5 increased from {values[0]:.2f} to "
            f"{values[-1]:.2f} across the recent readings"
        )
    else:
        reason = "No sustained upward PM2.5 trend detected"

    return TrendResult(
        is_sustained_trend=is_sustained_trend,
        increase=increase,
        reason=reason,
    )