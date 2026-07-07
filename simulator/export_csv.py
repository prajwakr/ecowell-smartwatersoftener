import csv
import os


class CSVExporter:

    def __init__(self, database):

        self.database = database

    def export_sensor_logs(self):

        logs = self.database.get_recent_sensor_logs(1000)

        os.makedirs("exports", exist_ok=True)

        filename = "exports/sensor_history.csv"

        with open(filename, "w", newline="") as file:

            writer = csv.writer(file)

            writer.writerow([
                "ID",
                "Timestamp",
                "Flow",
                "Pressure",
                "Salt",
                "TDS",
                "Power",
                "Regeneration",
                "State",
                "Health"
            ])

            for log in logs:

                writer.writerow([
                    log["id"],
                    log["timestamp"],
                    log["flow"],
                    log["pressure"],
                    log["salt"],
                    log["tds"],
                    log["power"],
                    log["regeneration"],
                    log["state"],
                    log["health"]
                ])

        return filename