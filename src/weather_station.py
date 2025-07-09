import pandas as pd

class WeatherStation:
    def __init__(self, station_id):
        self.station_id = station_id

        df = pd.read_csv("WeatherStation.csv")

        station_data = df[df['ID'] == station_id]

        row = station_data.iloc[0]
        self.location = row['Location']
        self.longitude = row['Longitude']
        self.latitude = row['Latitude']
        self.starting_epoch = row['StartingEpochTime']
        self.ending_epoch = row['EndingEpochTime']
