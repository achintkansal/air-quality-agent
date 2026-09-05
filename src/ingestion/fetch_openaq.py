import os

import requests
import yaml
from dotenv import load_dotenv

from src.storage.db import initialize_database, save_reading


load_dotenv()

API_KEY = os.getenv("OPENAQ_API_KEY")
BASE_URL = "https://api.openaq.org/v3"
CONFIG_PATH = "config/hourly_india_stations.yaml"


def load_stations():
    """Load monitored stations from YAML."""
    with open(CONFIG_PATH, "r") as file:
        config = yaml.safe_load(file)

    return config["stations"]


def get_latest_readings(location_id):
    """Fetch latest readings from OpenAQ."""
    url = f"{BASE_URL}/locations/{location_id}/latest"

    headers = {
        "X-API-Key": API_KEY
    }

    response = requests.get(
        url,
        headers=headers,
        timeout=30
    )

    response.raise_for_status()

    return response.json()


def get_pm25_reading(location_id, sensor_id):
    """Find the latest PM2.5 reading for a sensor."""
    data = get_latest_readings(location_id)

    for reading in data.get("results", []):
        if reading.get("sensorsId") == sensor_id:
            return {
                "location_id": location_id,
                "sensor_id": sensor_id,
                "parameter": "pm25",
                "value": reading["value"],
                "timestamp": reading["datetime"]["utc"],
            }

    return None


def fetch_all_pm25_readings():
    """Fetch PM2.5 readings for all configured stations."""
    stations = load_stations()
    readings = []

    print(f"Found {len(stations)} configured stations.")

    for station in stations:
        city = station["city"]
        location_id = station["location_id"]
        sensor_id = station["sensor_id"]

        print(f"\nFetching {city}...")
        print(f"Location ID: {location_id}")
        print(f"Sensor ID: {sensor_id}")

        try:
            reading = get_pm25_reading(
                location_id=location_id,
                sensor_id=sensor_id,
            )

            if reading is None:
                print("  No PM2.5 reading found.")
                continue

            reading["city"] = city
            reading["station_name"] = station["name"]

            readings.append(reading)

            print(
                f"  PM2.5: {reading['value']}"
            )

            print(
                f"  Timestamp: {reading['timestamp']}"
            )

        except requests.RequestException as error:
            print(f"  OpenAQ request failed: {error}")

        except Exception as error:
            print(f"  Unexpected error: {error}")

    return readings


def save_all_readings(readings):
    """Save fetched readings into SQLite."""
    print(f"\nReadings ready to save: {len(readings)}")

    for reading in readings:
        try:
            save_reading(reading)

            print(
                f"  Saved {reading['city']} "
                f"reading to database."
            )

        except Exception as error:
            print(
                f"  Failed to save "
                f"{reading['city']}: {error}"
            )


if __name__ == "__main__":
    print("Starting air quality ingestion...")

    initialize_database()

    readings = fetch_all_pm25_readings()

    print("\nSaving readings...")

    save_all_readings(readings)

    print("\nDone.")