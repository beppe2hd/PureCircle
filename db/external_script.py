import mysql.connector
import requests
import decimal
from datetime import datetime

# --- CONFIG ---
DB_CONFIG = {
    "host": "127.0.0.1",
    "port": 3306,
    "user": "morocco",
    "password": "moroccopw",
    "database": "sensors",
}

API_URL = "http://api-purecircle.ngrok.app/sensor-data/"

SENSOR_LIST = ["sensor_014", "sensor_015", "sensor_032", "sensor_033",
"sensor_089", "sensor_090", "sensor166", "sensor_174",
"sensor_172", "sensor_156", "sensor_161", "sensor_162"]

#--- FETCH DATA FROM DB ---
def fetch_last_24h_data():
    conn = mysql.connector.connect(**DB_CONFIG)
    cursor = conn.cursor(dictionary=True)  # rows as dicts

    query = """
    SELECT id, time, sensor, water_SOIL
    FROM sensor_data
    WHERE time >= NOW() - INTERVAL 1 HOUR
      AND sensor IN ("sensor_014", "sensor_015", "sensor_032", "sensor_033", "sensor_089", "sensor_090", "sensor_166", "sensor_174","sensor_172", "sensor_156", "sensor_161", "sensor_162")
    ORDER BY time DESC
    LIMIT 2000;
    """

    cursor.execute(query)
    rows = cursor.fetchall()
    conn.close()

    # Convert datetime to string for JSON
    for row in rows:
        if isinstance(row["time"], datetime):
            row["time"] = row["time"].isoformat()
        if isinstance(row["water_SOIL"], (decimal.Decimal, float)):
            row["water_SOIL"] = float(row["water_SOIL"])
    return rows


# --- SEND TO FASTAPI ---
def send_to_api(data):
    headers = {"Content-Type": "application/json"}
    response = requests.post(API_URL, json=data, headers=headers)
    if response.status_code == 200:
        print("Data sent successfully:", response.json())
    else:
        print(" Error:", response.status_code, response.text)

# --- MAIN ---
if __name__ == "__main__":
    data = fetch_last_24h_data()
    print(f"📨 Sending {len(data)} records...")
    send_to_api(data)
