from fastapi import FastAPI
from contextlib import asynccontextmanager
import sys, os
from dotenv import load_dotenv
import torch

load_dotenv()
sys.path.append(os.getenv("PYTHONPATH"))
print(os.getenv("PYTHONPATH"))
from src.commons.architectures.model_handler import create_model, inference
from src.inference.api.src.external_resource import (
    retrive_sensor_data,
    retrieve_meteo_data,
)
from src.commons.utils import (
    get_config_file,
    get_start_end_date,
    reset_df_start_end_hours,
)

config = get_config_file(os.getenv("configFile"))
model = create_model(config)
model.eval()


start_dt_historical, end_dt_historical = get_start_end_date(
    config["features"]["input_seq_len"], "past"
)
start_dt_forecast, end_dt_forecast = get_start_end_date(
    config["features"]["output_seq_len"], "future"
)

fields_feaures = config["features"]["input"]["fiedls"]
meteo_features_historical = config["features"]["input"]["meteo_historical"]
meteo_features_forecast = config["features"]["input"]["meteo_forecast"]
meteo_features_forecast = [item[:-2] for item in meteo_features_forecast]
lat = config["features"]["geo_coordinate"]["lat"]
lon = config["features"]["geo_coordinate"]["lon"]

historical_sensor_data = retrive_sensor_data(
    host=os.getenv("host"),
    user=os.getenv("user"),
    password=os.getenv("password"),
    database=os.getenv("database"),
    features=fields_feaures,
    start_dt=start_dt_historical,
    end_dt=end_dt_historical,
)

meteo_data_historical = retrieve_meteo_data(
    mode="historical",
    features=meteo_features_historical,
    lat=lat,
    lon=lon,
    start_dt=start_dt_historical.split(" ")[
        0
    ],  # meteo service do not need seconds information
    end_dt=end_dt_historical.split(" ")[0],
)
meteo_data_forecast = retrieve_meteo_data(
    mode="forecast", features=meteo_features_forecast, lat=lat, lon=lon
)

meteo_data_historical = reset_df_start_end_hours(
    meteo_data_historical, start_dt_historical, end_dt_historical
)
meteo_data_forecast = reset_df_start_end_hours(
    meteo_data_forecast, start_dt_forecast, end_dt_forecast
)

x = []
x_f = []


for i in range(0, config["features"]["output_seq_len"]):
    r = historical_sensor_data[i]
    a = [r[item] for item in fields_feaures]
    hmd = meteo_data_historical.iloc[i][meteo_features_historical].to_list()
    fmd = meteo_data_forecast.iloc[i][meteo_features_forecast].to_list()
    a.extend(hmd)
    x.append(a)
    x_f.append(fmd)
# Convert to NumPy array for convenience
x = torch.tensor(x)
x_f = torch.tensor(x_f)
y = inference(model, x, x_f)
