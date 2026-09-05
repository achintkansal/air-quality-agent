import time

from src.detection.model import detect
from src.messaging.generate_message import generate_message
from src.storage.db import get_session, initialize_database
from src.storage.models import AgentCursor, Reading
from src.dedup.state_manager import should_notify


POLLUTANT = "pm25"
UNIT = "µg/m³"

CITIES = ["Mumbai", "Delhi", "Pune"]

# Check the database frequently for newly inserted readings.
POLL_INTERVAL_SECONDS = 1


def get_last_processed_id(session, city: str) -> int:
    cursor = session.get(AgentCursor, city)

    if cursor is None:
        cursor = AgentCursor(
            city=city,
            last_processed_reading_id=0,
        )
        session.add(cursor)
        session.commit()

    return cursor.last_processed_reading_id


def update_last_processed_id(
    session,
    city: str,
    reading_id: int,
) -> None:
    cursor = session.get(AgentCursor, city)

    if cursor is None:
        cursor = AgentCursor(
            city=city,
            last_processed_reading_id=reading_id,
        )
        session.add(cursor)
    else:
        cursor.last_processed_reading_id = reading_id

    session.commit()


def process_reading(reading: Reading) -> None:
    session = get_session()

    try:
        result = detect(
            session=session,
            city=reading.city,
            current_value=reading.value,
            current_reading_id=reading.id,
        )

        station_id = reading.station_name or str(reading.location_id)

        decision = should_notify(
            session=session,
            station_id=station_id,
            pollutant=POLLUTANT,
            current_state=result.verdict,
            current_value=reading.value,
        )

        print(
            f"{reading.city} | "
            f"{reading.value:.2f} {UNIT} | "
            f"{result.verdict} | "
            f"{decision.decision}"
        )

        if decision.should_notify:
            notification = generate_message(
                city=reading.city,
                station_id=station_id,
                pollutant=POLLUTANT,
                value=reading.value,
                unit=UNIT,
                verdict=decision.verdict,
                reason=decision.reason,
            )

            print(f"Subject: {notification.subject}")
            print(notification.message)
            print()

    finally:
        session.close()


def process_new_readings() -> None:
    session = get_session()

    try:
        for city in CITIES:
            last_id = get_last_processed_id(session, city)

            readings = (
                session.query(Reading)
                .filter(
                    Reading.city == city,
                    Reading.parameter == POLLUTANT,
                    Reading.id > last_id,
                )
                .order_by(Reading.id.asc())
                .all()
            )

            for reading in readings:
                process_reading(reading)

                update_last_processed_id(
                    session,
                    city,
                    reading.id,
                )
            # print("*" * 60)

    finally:
        session.close()


def run_agent() -> None:
    initialize_database()

    print("Air Quality Agent started.")
    print("Watching data/live.db for new readings...")

    while True:
        try:
            process_new_readings()
        except Exception as e:
            print(f"Agent error: {e}")

        time.sleep(POLL_INTERVAL_SECONDS)


if __name__ == "__main__":
    run_agent()