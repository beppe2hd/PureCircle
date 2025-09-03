import pandas as pd

dfMeteoStation = pd.read_excel('../data/WeatherStation_Slimania_Season1.xlsx', usecols=[1,2,3,4,5,6,7,8,9])
dfMeteoStation["datetime"] = dfMeteoStation["datetime"].dt.round('h')
dfMeteoStation_rev = dfMeteoStation.groupby('datetime').mean()

dfMeteoStation_rev = dfMeteoStation_rev.set_index("datetime")
dfMeteoStation_rev = dfMeteoStation_rev.reindex(full_index)
values = {
    "Temp": 0,
    "Hum": 0,
    "Int": 0,
    "UVI": 0,
    "WS": 0,
    "WD": 0,
    "RG": 0,
    "BP": 0
}
dfMeteoStation_rev.loc["2024-12-12 12:00:00"] = values
dfMeteoStation_rev[['Temp', 'Hum', 'Int', 'UVI', 'WS', 'WD', 'RG', 'BP']] = dfMeteoStation_rev[['Temp', 'Hum', 'Int', 'UVI', 'WS', 'WD', 'RG', 'BP']].interpolate()

print("Hello")

