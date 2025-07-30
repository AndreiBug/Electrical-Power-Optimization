# Functii pentru calculul energiei produse / consumate
import pandas as pd
from house import House
import plotly.graph_objects as go
from datetime import datetime, timezone
import math

class EnergyProcessing(House):
    def __init__(self, house_id):
        super().__init__(house_id)
        self.consumption = {} #Puterea consumata pe ora
        self.production = {} # Puterea produsa pe ora
        self.solar_radiation = {} # Radiatia solara pe ora
    
    def get_consumption(self):  # Calculeaza consumul total al casei per ora din csv
        consumption_file = "Database/Consumption.csv"
        df = pd.read_csv(consumption_file)

        df = df[df['HouseIDREF'] == self.house_id]

        # Convertim EpochTime la inceputul orei (rotunjire in jos la multiplu de 3600)
        def fix_hour(x):
            return x - (x % 3600)
        df['HourEpoch'] = df['EpochTime'].apply(fix_hour)
    
        df_hourly = df.groupby('HourEpoch')['Value'].sum()

        self.consumption = (df_hourly / 6000).to_dict()

        return self.consumption

    def get_solar_radiation(self): # Ia radiatia solara din WeatherData
        house_file = "Database/House.csv"
        weather_file = "Database/WeatherData.csv"

        df_house = pd.read_csv(house_file)
        df_weather = pd.read_csv(weather_file)

        station_row = df_house[df_house['ID'] == self.house_id]

        station_id = station_row.iloc[0]['WeatherStationIDREF']

        df_filtered = df_weather[
            (df_weather['WeatherStationIDREF'] == station_id) &
            (df_weather['WeatherVariableIDREF'] == 4)
        ]

        if df_filtered.empty:
            print(f"Nu s-au gasit date meteo pentru statia {station_id}.")
            return {}

        df_grouped = df_filtered.groupby('EpochTime')['Value'].sum()
        self.solar_radiation = df_grouped.to_dict()

        return self.solar_radiation

    def get_power_estimated(self, n=10, Pm=575, f=0.8, GTSTC=1000):  # Calculeaza puterea produsa estimata pentru n panouri
        if not self.solar_radiation:
            print("Radiatia solara nu este incarcata.")
            return {}

        production_data = {
            t: (Pm * n * f * G / GTSTC) / 6000  # W*10min -> kWh
            for t, G in self.solar_radiation.items()
        }

        self.production = production_data
        return self.production

    def print_consumption(self): # Printeaza consumul
        for i, (key, value) in enumerate(self.consumption.items()):
            if i >= 30:
                break
            print(f"Consum la ora {i+1}: Epoch {key} -> {value:.3f} kWh")

    def print_solar_radiation(self): # Printeaza radiatia solara
        for i, (key, value) in enumerate(self.solar_radiation.items()):
            if i >= 30:
                break
            print(f"Radiatie la ora {i+1}: Epoch {key} -> G = {value}")

    def print_power_estimated(self): # Printeaza puterea produsa
        for i, (key, value) in enumerate(self.production.items()):
            if i >= 30:
                break
            print(f"Productie la ora {i+1}: Epoch {key} -> E = {value:.3f} kWh")