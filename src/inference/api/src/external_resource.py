import mysql.connector
import openmeteo_requests
from retry_requests import retry
import requests_cache
import pandas as pd


def retrieve_meteo_data(mode, features, lat, lon, start_dt="", end_dt=""):
    cache_session = requests_cache.CachedSession(".cache", expire_after=3600)
    retry_session = retry(cache_session, retries=5, backoff_factor=0.2)
    openmeteo = openmeteo_requests.Client(session=retry_session)

    # features = [
    #     "temperature_2m",
    #     "relative_humidity_2m",
    #     "cloud_cover",
    #     "wind_speed_10m",
    #     "wind_direction_100m",
    #     "soil_temperature_0_to_7cm",
    #     "soil_temperature_7_to_28cm",
    #     "soil_temperature_28_to_100cm",
    #     "rain",
    #     "precipitation",
    #     "evapotranspiration",
    # ]

    # Make sure all required weather variables are listed here
    # The order of variables in hourly or daily is important to assign them correctly below

    if mode == "historical":
        url = "https://archive-api.open-meteo.com/v1/archive"
        params = {
            "latitude": lat,  # 52.52,
            "longitude": lon,  # 13.41,
            "start_date": start_dt,
            "end_date": end_dt,
            "hourly": features,
        }

    if mode == "forecast":
        url = "https://api.open-meteo.com/v1/forecast"
        params = {
            "latitude": lat,  # 52.52,
            "longitude": lon,  # 13.41,
            "hourly": features,
            # "forecast_days": 3,
        }

    responses = openmeteo.weather_api(url, params=params)

    # Process first location. Add a for-loop for multiple locations or weather models
    response = responses[0]

    # Process hourly data. The order of variables needs to be the same as requested.
    hourly = response.Hourly()

    hourly_data = {
        "date": pd.date_range(
            start=pd.to_datetime(hourly.Time(), unit="s", utc=True),
            end=pd.to_datetime(hourly.TimeEnd(), unit="s", utc=True),
            freq=pd.Timedelta(seconds=hourly.Interval()),
            inclusive="left",
        )
    }

    for i, p in enumerate(features):
        hourly_data[p] = hourly.Variables(i).ValuesAsNumpy()

    return pd.DataFrame(data=hourly_data)


def retrive_sensor_data_old(host, user, password, database, features, start_dt, end_dt):

    conn = mysql.connector.connect(
        host=host, user=user, password=password, database=database
    )

    cursor = conn.cursor(dictionary=True)

    features_to_retrieve = [item for item in features]
    # s_a, s_b, irr, LAI
    if "datetime" not in features_to_retrieve:
        features_to_retrieve.append("datetime")
    features_to_retrieve = ", ".join(features_to_retrieve)

    query = f"""
    SELECT {features_to_retrieve}
    FROM sensor_data
    WHERE datetime BETWEEN %s AND %s
    ORDER BY datetime ASC;
    """

    cursor.execute(query, (start_dt, end_dt))
    rows = cursor.fetchall()

    cursor.close()
    conn.close()

    return rows


def retrive_sensor_data(host, user, password, database, features, start_dt, end_dt, sensor_id):
    
    conn = mysql.connector.connect(
        host="localhost",
        user="root",
        password="password",
        database="irrigation_db"
    )

    cursor = conn.cursor(dictionary=True)

    query = f"""
    SELECT ts, lai
    FROM lai
    WHERE ts < CURDATE() AND field_id = 2
    ORDER BY ts ASC;
    """

    cursor.execute(query)
    rows = cursor.fetchall()

    df = pd.DataFrame(rows, columns=['ts','lai'])
    df["ts"] = pd.to_datetime(df["ts"])
    full_index = pd.date_range(start=df['ts'][0], end=end_dt, freq="h")
    df = df.set_index("ts")
    df = df.reindex(full_index)
    df = df.interpolate()
    filtered_df = df.loc[start_dt: end_dt]
    lai = filtered_df['lai'].to_list()

    zones = {'s_b', 's_w'}

    outSensor = {}
    for zone in zones:
        query = f"""
        SELECT ts, water_content
        FROM soil_moisture
        WHERE sensor_zone = '{zone}' and ts BETWEEN %s AND %s AND field_id = 2;
        """

        cursor.execute(query, (start_dt, end_dt))
        rows = cursor.fetchall()

        df = pd.DataFrame(rows, columns=['ts','water_content'])
        df["ts"] = pd.to_datetime(df["ts"])
        df["ts"] = df["ts"].dt.round('h')
        df = df.groupby('ts').mean()
        
        outSensor[zone] = df['water_content']

    query = f"""
    SELECT ts, water_volume
    FROM irrigation
    WHERE ts BETWEEN %s AND %s AND field_id = 2;
    """

    cursor.execute(query)#, (start_dt, end_dt))
    rows = cursor.fetchall()
    rows

    if len(rows)==0:
        irr = len(full_index) * [0.0]
    else:
        df = pd.DataFrame(rows, columns=['ts', 'water_volume'])
        df["ts"] = pd.to_datetime(df["ts"])
        full_index = pd.date_range(start=start_dt, end=end_dt, freq="h")
        df = df.set_index('ts')
        df = df.reindex(full_index)
        df.fillna(0.0, inplace=True)
        print(df)


