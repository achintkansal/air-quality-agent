from src.storage.master_db import (
    get_distinct_cities,
    get_next_reading_for_city,
    get_earliest_master_id,
)
from src.storage.live_db import (
    initialize_live_db,
    get_cursor,
    update_cursor,
    insert_live_reading,
)


def push_next_reading_for_city(city):
    last_id = get_cursor(city)
    reading = get_next_reading_for_city(city, after_id=last_id)

    if reading is None:
        # Ran out of new data — loop back to the start of this city's history
        print(f"  {city}: reached end of history, looping back to start.")
        last_id = get_earliest_master_id(city)
        reading = get_next_reading_for_city(city, after_id=last_id)

        if reading is None:
            print(f"  {city}: no data available at all, skipping.")
            return

    insert_live_reading(reading)
    update_cursor(city, reading["master_id"])

    print(f"  {city}: pushed value={reading['value']} timestamp={reading['timestamp']}")


def run():
    initialize_live_db()
    cities = get_distinct_cities()

    print(f"Simulating hourly push for {len(cities)} cities...")

    for city in cities:
        push_next_reading_for_city(city)

    print("Done.")


if __name__ == "__main__":
    run()