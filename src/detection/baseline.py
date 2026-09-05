from dataclasses import dataclass

from sqlalchemy import select
from sqlalchemy.orm import Session

from src.storage.models import Reading


@dataclass
class Baseline:
    mean: float
    stddev: float
    sample_size: int


def get_baseline(
    session: Session,
    city: str,
    hours: int = 24,
    exclude_reading_id: int | None = None,
) -> Baseline | None:
    """
    Calculate the recent PM2.5 baseline for a city.

    The current reading can be excluded so that the baseline
    is calculated only from previous readings.
    """

    query = (
        select(Reading.value)
        .where(
            Reading.city == city,
            Reading.parameter == "pm25",
        )
    )

    # Do not allow the current reading to influence its own baseline.
    if exclude_reading_id is not None:
        query = query.where(
            Reading.id != exclude_reading_id
        )

    result = session.execute(
        query
        .order_by(Reading.id.desc())
        .limit(hours * 12)
    )

    values = [
        value
        for (value,) in result.all()
        if value is not None
    ]

    if not values:
        return None

    mean = sum(values) / len(values)

    if len(values) > 1:
        variance = sum(
            (value - mean) ** 2
            for value in values
        ) / (len(values) - 1)

        stddev = variance ** 0.5
    else:
        stddev = 0.0

    return Baseline(
        mean=mean,
        stddev=stddev,
        sample_size=len(values),
    )