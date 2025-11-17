from externalAPI.Weather import weather_request
from datetime import datetime, timedelta
import pandas as pd

w = weather_request('2025-11-14', '2025-11-16', 34.90, 2.4)

#
h = w.meteo_request_histor()
#h = w.meteo_request_forecast()
print(h["date"])

# Current time
now = datetime.now()
# Round down to the hour
current_hour = now.replace(minute=0, second=0, microsecond=0)
past_hours = current_hour - timedelta(hours=24)

index_of_interest = pd.date_range(past_hours, current_hour, freq="h")

print(h.shape)
print(type(h["date"][0]))

h.set_index("date", inplace=True)
h2 = h[h.index.isin(index_of_interest)]


print(h2)
print(h2.shape)


