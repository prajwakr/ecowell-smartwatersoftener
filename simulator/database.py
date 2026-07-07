import sqlite3
import threading
from datetime import datetime


class Database:

    def __init__(self):

        self.lock = threading.Lock()

        self.conn = sqlite3.connect(
            "database/ecowell.db",
            check_same_thread=False
        )

        self.create_tables()

    def create_tables(self):

        with self.lock:

            cursor = self.conn.cursor()

            cursor.execute("""
            CREATE TABLE IF NOT EXISTS sensor_logs(

                id INTEGER PRIMARY KEY AUTOINCREMENT,

                timestamp TEXT,
                flow REAL,
                pressure REAL,
                salt REAL,
                tds INTEGER,

                power TEXT,
                regeneration TEXT,

                state TEXT,
                health INTEGER

            )
            """)

            cursor.execute("""
            CREATE TABLE IF NOT EXISTS activity_logs(

                id INTEGER PRIMARY KEY AUTOINCREMENT,

                timestamp TEXT,
                message TEXT

            )
            """)

            self.conn.commit()

    def save_sensor(self, sensor):

        with self.lock:

            cursor = self.conn.cursor()

            cursor.execute("""
            INSERT INTO sensor_logs(

                timestamp,
                flow,
                pressure,
                salt,
                tds,
                power,
                regeneration,
                state,
                health

            )

            VALUES(?,?,?,?,?,?,?,?,?)

            """, (

                sensor["timestamp"],
                sensor["flow"],
                sensor["pressure"],
                sensor["salt"],
                sensor["tds"],
                str(sensor["power"]),
                str(sensor["regeneration"]),
                sensor["state"],
                sensor["health"]

            ))

            self.conn.commit()

    def save_log(self, message):

        with self.lock:

            cursor = self.conn.cursor()

            cursor.execute("""
            INSERT INTO activity_logs(

                timestamp,
                message

            )

            VALUES(?,?)

            """, (

                datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                message

            ))

            self.conn.commit()

    def get_recent_sensor_logs(self, limit=50):

        with self.lock:

            cursor = self.conn.cursor()

            cursor.execute("""
            SELECT
                id,
                timestamp,
                flow,
                pressure,
                salt,
                tds,
                power,
                regeneration,
                state,
                health
            FROM sensor_logs
            ORDER BY id DESC
            LIMIT ?
            """, (limit,))

            rows = cursor.fetchall()

        history = []

        for row in rows:

            history.append({

                "id": row[0],
                "timestamp": row[1],
                "flow": row[2],
                "pressure": row[3],
                "salt": row[4],
                "tds": row[5],
                "power": row[6],
                "regeneration": row[7],
                "state": row[8],
                "health": row[9]

            })

        return history

    def get_activity_logs(self, limit=30):

        with self.lock:

            cursor = self.conn.cursor()

            cursor.execute("""
            SELECT
                id,
                timestamp,
                message
            FROM activity_logs
            ORDER BY id DESC
            LIMIT ?
            """, (limit,))

            rows = cursor.fetchall()

        logs = []

        for row in rows:

            logs.append({

                "id": row[0],
                "timestamp": row[1],
                "message": row[2]

            })

        return logs

    def clear_sensor_logs(self):

        with self.lock:

            cursor = self.conn.cursor()

            cursor.execute("DELETE FROM sensor_logs")

            self.conn.commit()

    def clear_activity_logs(self):

        with self.lock:

            cursor = self.conn.cursor()

            cursor.execute("DELETE FROM activity_logs")

            self.conn.commit()

    def get_dashboard_stats(self):

        with self.lock:

            cursor = self.conn.cursor()

            cursor.execute("SELECT COUNT(*) FROM sensor_logs")
            total_readings = cursor.fetchone()[0]

            cursor.execute("SELECT COUNT(*) FROM activity_logs")
            total_logs = cursor.fetchone()[0]

            cursor.execute("""
            SELECT COUNT(*)
            FROM activity_logs
            WHERE message LIKE '%Regeneration Completed%'
            """)
            total_regenerations = cursor.fetchone()[0]

            cursor.execute("""
            SELECT AVG(health)
            FROM sensor_logs
            """)
            avg_health = cursor.fetchone()[0]

        if avg_health is None:
            avg_health = 100

        return {

            "total_readings": total_readings,
            "total_logs": total_logs,
            "total_regenerations": total_regenerations,
            "average_health": round(avg_health, 1)

        }

    def close(self):

        with self.lock:

            self.conn.close()