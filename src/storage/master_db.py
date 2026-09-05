import sqlite3

MASTER_DB_PATH = "data/master.db"


def initialize_master_db():
    conn = sqlite3.connect(MASTER_DB_PATH)
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS readings_master (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            city TEXT,
            station_name TEXT,
            location_id INTEGER,
            sensor_id INTEGER,
            parameter TEXT,
            value REAL,
            timestamp TEXT
        )
    """)

    conn.commit()
    conn.close()


def insert_master_reading(reading):
    """Bulk-load a historical reading into master.db."""
    conn = sqlite3.connect(MASTER_DB_PATH)
    cursor = conn.cursor()

    cursor.execute("""
        INSERT INTO readings_master
            (city, station_name, location_id, sensor_id, parameter, value, timestamp)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    """, (
        reading["city"],
        reading["station_name"],
        reading["location_id"],
        reading["sensor_id"],
        reading["parameter"],
        reading["value"],
        reading["timestamp"],
    ))

    conn.commit()
    conn.close()


def get_distinct_cities():
    conn = sqlite3.connect(MASTER_DB_PATH)
    cursor = conn.cursor()

    cursor.execute("SELECT DISTINCT city FROM readings_master")
    cities = [row[0] for row in cursor.fetchall()]

    conn.close()
    return cities


def get_next_reading_for_city(city, after_id):
    """Get the next chronological reading for a city after a given master id."""
    conn = sqlite3.connect(MASTER_DB_PATH)
    cursor = conn.cursor()

    cursor.execute("""
        SELECT id, city, station_name, location_id, sensor_id, parameter, value, timestamp
        FROM readings_master
        WHERE city = ? AND id > ?
        ORDER BY id ASC
        LIMIT 1
    """, (city, after_id))

    row = cursor.fetchone()
    conn.close()

    if row is None:
        return None

    return {
        "master_id": row[0],
        "city": row[1],
        "station_name": row[2],
        "location_id": row[3],
        "sensor_id": row[4],
        "parameter": row[5],
        "value": row[6],
        "timestamp": row[7],
    }


def get_earliest_master_id(city):
    """Used to loop back to the start once a city runs out of new data."""
    conn = sqlite3.connect(MASTER_DB_PATH)
    cursor = conn.cursor()

    cursor.execute("""
        SELECT MIN(id) FROM readings_master WHERE city = ?
    """, (city,))

    row = cursor.fetchone()
    conn.close()

    return row[0] - 1 if row and row[0] is not None else 0