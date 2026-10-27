import sqlite3
from config import Config


def get_db():
    """Return a new database connection."""
    conn = sqlite3.connect(Config.DATABASE_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    """Create tables if they don't already exist."""
    conn = get_db()
    cursor = conn.cursor()
    cursor.executescript("""
        CREATE TABLE IF NOT EXISTS users (
            id          INTEGER PRIMARY KEY AUTOINCREMENT,
            name        TEXT    NOT NULL,
            age_group   TEXT    NOT NULL,
            occupation  TEXT    NOT NULL,
            lifestyle   TEXT    NOT NULL,
            created_at  DATETIME DEFAULT CURRENT_TIMESTAMP
        );

        CREATE TABLE IF NOT EXISTS health_sensitivities (
            id      INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
            name    TEXT    NOT NULL
        );

        CREATE TABLE IF NOT EXISTS assessments (
            id              INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id         INTEGER REFERENCES users(id) ON DELETE SET NULL,
            location        TEXT,
            temperature     REAL,
            humidity        REAL,
            uv_index        REAL,
            wind_speed      REAL,
            aqi             REAL,
            pm25            REAL,
            pm10            REAL,
            climate_score   REAL,
            risk_category   TEXT,
            ai_response     TEXT,
            created_at      DATETIME DEFAULT CURRENT_TIMESTAMP
        );
    """)
    conn.commit()
    conn.close()


# ---------------------------------------------------------------------------
# User CRUD
# ---------------------------------------------------------------------------

def create_user(name, age_group, occupation, lifestyle, sensitivities):
    """Insert a new user and their sensitivities. Returns the new user id."""
    conn = get_db()
    try:
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO users (name, age_group, occupation, lifestyle) VALUES (?, ?, ?, ?)",
            (name, age_group, occupation, lifestyle),
        )
        user_id = cursor.lastrowid
        for s in sensitivities:
            if s:
                cursor.execute(
                    "INSERT INTO health_sensitivities (user_id, name) VALUES (?, ?)",
                    (user_id, s),
                )
        conn.commit()
        return user_id
    finally:
        conn.close()


def get_user(user_id):
    """Return a user row plus their sensitivities list."""
    conn = get_db()
    try:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM users WHERE id = ?", (user_id,))
        user = cursor.fetchone()
        if not user:
            return None
        cursor.execute(
            "SELECT name FROM health_sensitivities WHERE user_id = ?", (user_id,)
        )
        sensitivities = [row["name"] for row in cursor.fetchall()]
        result = dict(user)
        result["sensitivities"] = sensitivities
        return result
    finally:
        conn.close()


def save_assessment(user_id, location, weather, aqi_data, score, risk_category, ai_response):
    """Persist an assessment record."""
    conn = get_db()
    try:
        conn.execute(
            """INSERT INTO assessments
               (user_id, location, temperature, humidity, uv_index, wind_speed,
                aqi, pm25, pm10, climate_score, risk_category, ai_response)
               VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
            (
                user_id,
                location,
                weather.get("temperature"),
                weather.get("humidity"),
                weather.get("uv_index"),
                weather.get("wind_speed"),
                aqi_data.get("aqi"),
                aqi_data.get("pm25"),
                aqi_data.get("pm10"),
                score,
                risk_category,
                ai_response,
            ),
        )
        conn.commit()
    finally:
        conn.close()
