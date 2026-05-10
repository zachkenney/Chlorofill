import sqlite3
from datetime import date

DB_PATH = "plants.db"

def get_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_connection()
    cur = conn.cursor()

    cur.executescript("""
        CREATE TABLE IF NOT EXISTS plants (
            id                      INTEGER PRIMARY KEY AUTOINCREMENT,
            name                    TEXT NOT NULL,
            species                 TEXT,
            watering_interval_days  INTEGER NOT NULL
        );

        CREATE TABLE IF NOT EXISTS watering_log (
            id                INTEGER PRIMARY KEY AUTOINCREMENT,
            plant_id          INTEGER NOT NULL,
            watered_on        TEXT NOT NULL,
            FOREIGN KEY (plant_id) REFERENCES plants(id)
        );
    """)

    conn.commit()
    conn.close()

def add(name, species, watering_interval_days, last_watered):
    conn = get_connection()
    cur = conn.cursor()

    cur.execute(
        'INSERT INTO plants (name, species, watering_interval_days) VALUES (?, ?, ?) RETURNING id',
        (name, species, watering_interval_days)
    )
    plant_id = cur.fetchone()[0]
    cur.execute(
        'INSERT INTO watering_log (plant_id, watered_on) VALUES (?, ?)',
        (plant_id, last_watered)
    )
    conn.commit()
    conn.close()

def addlog():
    pass

def find():
    conn = get_connection()
    cur = conn.cursor()

    plants = cur.execute('select * from plants').fetchall()
    conn.close()
    return plants

def log():
    conn = get_connection()
    cur = conn.cursor()

    log = cur.execute('select * from watering_log').fetchall()
    conn.close()
    return log
