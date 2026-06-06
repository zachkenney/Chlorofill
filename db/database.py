import sqlite3
from datetime import datetime, date, timedelta

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
            next_date         TEXT NOT NULL,
            FOREIGN KEY (plant_id) REFERENCES plants(id) ON DELETE CASCADE
        );
    """)

    conn.commit()
    conn.close()

def _parse_date(s):
    for fmt in ('%Y-%m-%d', '%m/%d/%Y'):
        try:
            return datetime.strptime(s,fmt).date()
        except ValueError:
            continue
    raise ValueError(f'Unrecognized date format: {s}. Use YYYY-MM-DD.')

def add(name, species, watering_interval_days, watered_on):
    next_date = _parse_date(watered_on) + timedelta(days=watering_interval_days)   
    
    conn = get_connection()
    cur = conn.cursor()

    cur.execute(
        'INSERT INTO plants (name, species, watering_interval_days) VALUES (?, ?, ?) RETURNING id',
        (name, species, watering_interval_days)
    )
    plant_id = cur.fetchone()[0]
    

    cur.execute(
        'INSERT INTO watering_log (plant_id, watered_on, next_date) VALUES (?, ?, ?)',
        (plant_id, watered_on, next_date)
    )
    conn.commit()
    conn.close()

def addlog(name):
    conn = get_connection()
    cur = conn.cursor()

    plant = cur.execute(
        'SELECT id, watering_interval_days FROM plants WHERE name = ?', (name,)
    ).fetchone()

    today = date.today()
    next_date = today + timedelta(days=plant['watering_interval_days'])

    cur.execute(
        'INSERT INTO watering_log (plant_id, watered_on, next_date) VALUES (?,?,?)',
        (plant['id'], today.isoformat(), next_date.isoformat())
    )
    conn.commit()
    conn.close()

def find():
    conn = get_connection()
    cur = conn.cursor()

    plants = cur.execute('''
    SELECT plants.*, wl.next_date 
    FROM plants 
    INNER JOIN watering_log wl ON wl.plant_id = plants.id 
    WHERE wl.id = (
        SELECT MAX(id) FROM watering_log WHERE plant_id = plants.id
    )
    ''').fetchall()
    #date = cur.execute('select next_date from watering_log').fetchall()
    conn.close()
    return plants

def checkdate(today):
    conn = get_connection()
    cur = conn.cursor()

    log = cur.execute(f'select * from watering_log inner join plants on plants.id = watering_log.plant_id where next_date = ?', (today, )).fetchall()
    conn.close()
    return log

def delete(name):
    conn = get_connection()
    cur = conn.cursor()

    plant_delete = cur.execute(f'DELETE FROM plants WHERE name = ?', (name,))
    conn.commit()
    conn.close()

