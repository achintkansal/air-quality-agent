from dataclasses import dataclass

@dataclass
class NotificationMessage:
    subject: str
    message: str


def generate_message(
    city: str,
    station_id: str,
    pollutant: str,
    value: float,
    unit: str,
    verdict: str,
    reason: str,
) -> NotificationMessage:
    """
    Generate a concise notification based on the detection verdict.
    """

    if verdict == "SPIKE":
        subject = f"Air Quality Alert - {city}"

        message = (
            f"PM2.5 has suddenly increased at {station_id} in {city}. "
            f"The latest reading is {value:.2f} {unit}. "
            f"This is an unusual change compared with recent conditions. "
            f"{reason}."
        )

    elif verdict == "SUSTAINED_TREND":
        subject = f"Air Quality Trend - {city}"

        message = (
            f"PM2.5 has been steadily increasing at {station_id} in {city}. "
            f"The latest reading is {value:.2f} {unit}. "
            f"This indicates a sustained upward trend. "
            f"{reason}."
        )

    elif verdict == "RECOVERED":
        subject = f"Air Quality Improving - {city}"

        message = (
            f"PM2.5 levels at {station_id} in {city} have returned "
            f"toward normal conditions. "
            f"The latest reading is {value:.2f} {unit}. "
            f"{reason}."
        )

    else:
        subject = f"Air Quality Update - {city}"

        message = (
            f"PM2.5 at {station_id} in {city} is currently "
            f"{value:.2f} {unit}. "
            f"No significant anomaly was detected."
        )

    return NotificationMessage(
        subject=subject,
        message=message,
    )