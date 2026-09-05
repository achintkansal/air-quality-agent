import sqlite3

LIVE_DB_PATH = "data/live.db"


def initialize_live_db():
    conn = sqlite3.connect(LIVE_DB_PATH)
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS readings (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            city TEXT,
            station_name TEXT,
            location_id INTEGER,
            sensor_id INTEGER,
            parameter TEXT,
            value REAL,
            timestamp TEXT,
            pushed_at TEXT DEFAULT CURRENT_TIMESTAMP
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS push_cursor (
            city TEXT PRIMARY KEY,
            last_pushed_master_id INTEGER DEFAULT 0
        )
    """)

    conn.commit()
    conn.close()


def get_cursor(city):
    conn = sqlite3.connect(LIVE_DB_PATH)
    cursor = conn.cursor()

    cursor.execute("SELECT last_pushed_master_id FROM push_cursor WHERE city = ?", (city,))
    row = cursor.fetchone()
    conn.close()

    return row[0] if row else 0


def update_cursor(city, master_id):
    conn = sqlite3.connect(LIVE_DB_PATH)
    cursor = conn.cursor()

    cursor.execute("""
        INSERT INTO push_cursor (city, last_pushed_master_id)
        VALUES (?, ?)
        ON CONFLICT(city) DO UPDATE SET last_pushed_master_id = excluded.last_pushed_master_id
    """, (city, master_id))

    conn.commit()
    conn.close()


def insert_live_reading(reading):
    conn = sqlite3.connect(LIVE_DB_PATH)
    cursor = conn.cursor()

    cursor.execute("""
        INSERT INTO readings
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