import pandas as pd

# print("hello")
# elements = []
sensors = {}
for i in range(1, 36):
    dfSensor = pd.read_excel('../data/DraginoSoilMositure_Morocco_Season1.xlsx', sheet_name=f'Sensor {i}',
                             usecols=[0, 1])
    dfSensor.rename(columns={"Row Labels": "datetime", "Average of water_SOIL": "sm_value"}, inplace=True)
    dfSensor = dfSensor.set_index("datetime")
    full_index = pd.date_range(dfSensor.index.min(), dfSensor.index.max(), freq="h")
    dfSensor = dfSensor.reindex(full_index)
    dfSensor.reset_index(inplace=True, names='datetime')
    dfSensor["sm_value"] = dfSensor["sm_value"].interpolate()
    sensors[i] = dfSensor

dfMeteo = pd.read_csv('../data/open-meteo.csv')
dfMeteo["datetime"] = pd.to_datetime(dfMeteo["datetime"])
dfMeteo = dfMeteo.set_index("datetime")
dfMeteo = dfMeteo.reindex(full_index)
dfMeteo.reset_index(inplace=True, names='datetime')

dfIrrigation = pd.read_excel('../data/IrrigationEvents_Morocco_Season1.xlsx', sheet_name='Irrigation')
dfIrrigation.rename(columns={"Date": "datetime", "Irrigation Duration": "duration", "Irrigation Volume": "volume"},
                    inplace=True)
dfIrrigation["datetime"] = pd.to_datetime(dfIrrigation["datetime"]) + pd.to_timedelta("12:00:00")
dfIrrigation.sort_values("datetime", ascending=True, inplace=True)
CW = [1, 2, 5, 6, 15, 16, 23, 24, 31, 32, 33, 34]
F = [3, 4, 7, 8, 19, 20, 21, 22, 25, 26, 35, 36]
# dfIrrigation.loc[dfIrrigation['Plot'] == 'CROPWAT', 'Plot'] = 0
dfIrrigation["Plot"] = dfIrrigation["Plot"].apply(
    lambda x: CW if x == "CROPWAT" else [x] if isinstance(x, int) else F
)

# dfLAI = pd.read_excel('../data/LAI_Morocco_Season1.xlsx', usecols=[0, 1, 3, 5, 7, 9, 11, 13, 15, 17, 19])
# dfLAI = dfLAI.transpose()
# dfLAI.columns = dfLAI.iloc[0]
# dfLAI = dfLAI.drop('Treatment', axis=0)
# dfLAI.reset_index(inplace=True)
# dfLAI.rename(columns={"index": "datetime"}, inplace=True)
# dfLAI["datetime"] = pd.to_datetime(dfLAI["datetime"]) + pd.to_timedelta("12:00:00")
# dfLAI = dfLAI.set_index("datetime")
# dfLAI.index.names = ['datetime']

# dfLAI = dfLAI.reindex(full_index)

dfLAI = pd.read_excel('../data/LAI_Morocco_Season1.xlsx', sheet_name=f'Sheet1')
dfLAI["datetime"] = pd.to_datetime(dfLAI["datetime"]) + pd.to_timedelta("12:00:00")
dfLAI = dfLAI.set_index("datetime")
# full_index1 = pd.date_range(dfLAI.index.min(), dfLAI.index.max(), freq="h")
full_index2 = pd.date_range(start='2024-12-12  12:00:00', end='2025-05-15 13:00:00', freq="h")
dfLAI = dfLAI.reindex(full_index)

values = {
    "Tititcaca-CROP": 0,
    "Tititcaca-Sensor": 0,
    "Tititcaca-Farmer": 0,
    "ICBA-CROP": 0,
    "ICBA-Sensor": 0,
    "ICBA-Farmer": 0
}
dfLAI.loc["2024-12-12 12:00:00"] = values

dfLAI[['Tititcaca-CROP', 'Tititcaca-Sensor', 'Tititcaca-Farmer', 'ICBA-CROP',
       'ICBA-Sensor', 'ICBA-Farmer']] = dfLAI[['Tititcaca-CROP', 'Tititcaca-Sensor', 'Tititcaca-Farmer', 'ICBA-CROP',
                                               'ICBA-Sensor', 'ICBA-Farmer']].interpolate()

mapToSensor = {'Tititcaca-CROP': [5, 6, 23, 24, 31, 32],
               'Tititcaca-Sensor': [3, 4, 19, 20, 35, 36],
               'Tititcaca-Farmer': [9, 10, 13, 14, 29, 30],
               'ICBA-CROP': [1, 2, 15, 16, 33, 34],
               'ICBA-Sensor': [7, 8, 21, 22, 25, 26],
               'ICBA-Farmer': [11, 12, 17, 18, 27, 28]}

for i in range(1, 37):
    for k, v in mapToSensor.items():
        if i in v:
            dfLAI[f'{i}'] = dfLAI[k]

dfLAI.drop(['Tititcaca-CROP', 'Tititcaca-Sensor', 'Tititcaca-Farmer', 'ICBA-CROP',
            'ICBA-Sensor', 'ICBA-Farmer'], axis=1)
dfLAI.reset_index(inplace=True, names='datetime')


dfMeteoStation = pd.read_excel('../data/WeatherStation_Slimania_Season1.xlsx', usecols=[1,2,3,4,5,6,7,8,9])
dfMeteoStation["datetime"] = dfMeteoStation["datetime"].dt.round('h')
dfMeteoStation_rev = dfMeteoStation.groupby('datetime').mean()

#dfMeteoStation_rev = dfMeteoStation_rev.set_index("datetime")
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
dfMeteoStation_rev.reset_index(inplace=True, names='datetime')

import plotly.graph_objects as go
import pandas as pd

# Create an empty figure
fig = go.Figure()

# Iteratively add traces
for i, df in sensors.items():
    fig.add_trace(go.Scatter(
        x=df["datetime"],
        y=df["sm_value"],
        mode='lines',
        name=f"Trace {i}",
        visible='legendonly'
    ))
    mask = dfIrrigation["Plot"].apply(lambda x: i in x)
    dfIrrigationFiltered = dfIrrigation[mask]
    fig.add_trace(go.Scatter(
        x=dfIrrigationFiltered["datetime"],
        y=dfIrrigationFiltered["volume"],
        mode='markers',
        marker=dict(
            size=13,
        ),
        name=f"Trace Irr {i}",
        visible='legendonly'
    ))
    fig.add_trace(go.Scatter(
        x=dfLAI["datetime"],
        y=dfLAI[f"{i}"]*10,
        mode='lines',
        name=f"LAI {i}",
        visible='legendonly'
    ))

dfMeteoFiltered = dfMeteo[dfMeteo["rain"] > 0]
fig.add_trace(go.Scatter(
    x=dfMeteoFiltered["datetime"],
    y=dfMeteoFiltered["rain"] * 10,
    mode='markers',
    marker=dict(
        size=10,
    ),
    name=f"rain"
))

dfMeteoStation_rev2 = dfMeteoStation_rev[dfMeteoStation_rev["RG"] > 0]
fig.add_trace(go.Scatter(
        x=dfMeteoStation_rev2["datetime"],
        y=dfMeteoStation_rev2[f"RG"],
        mode='markers',
        name=f"MS_rain"
))

# Show plot
fig.show()
