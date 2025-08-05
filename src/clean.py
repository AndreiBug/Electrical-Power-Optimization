import pandas as pd

########## Corectii ale anomaliilor ##########

def delete_house_less_than_a_year():  # Stergerea caselor cu mai putin de un an de date
    house_csv = "Database/House.csv"

    df_house = pd.read_csv(house_csv)

    one_year_seconds = 365 * 24 * 3600  # Durata in secunde pentru un an
    df_house['Duration'] = df_house['EndingEpochTime'] - df_house['StartingEpochTime']

    # Selecteaza casele cu durata mai mica de un an
    houses_to_remove = df_house[df_house['Duration'] < one_year_seconds]['ID'].tolist()

    if not houses_to_remove:
        print("Nu s-au gasit case cu mai putin de un an de date.")
        return

    # Filtreaza doar casele care raman si elimina coloana temporara
    df_house_cleaned = df_house[df_house['Duration'] >= one_year_seconds].drop(columns=['Duration'])
    df_house_cleaned.to_csv(house_csv, index = False)

    print("Case eliminate cu mai putin de un an de date: " + str(houses_to_remove))

def normalize_spikes(): # Normalizarea spike-urilor din 10 in 10 minute
    csv = "Database/Consumption.csv"
    threshold = 3

    df = pd.read_csv(csv)
    df = df.sort_values(by=['HouseIDREF', 'ApplianceIDREF', 'EpochTime']).reset_index(drop=True)  # Sorteaza pentru a avea valorile in ordine cronologica

    spike_count = 0  # Contor global

    # Grupare pe casa, aparat
    def fix_spikes(group):
        nonlocal spike_count
        values = group['Value'].to_numpy(dtype = float)
        new_values = values.copy()

        for i in range(1, len(values) - 1):
            left = values[i - 1]
            right = values[i + 1]
            local_avg = (left + right) / 2

            if values[i] > local_avg * threshold:
                new_values[i] = local_avg
                spike_count += 1

        group['Value'] = new_values
        return group

    df_cleaned = df.groupby(['HouseIDREF', 'ApplianceIDREF'], group_keys=False).apply(fix_spikes)
    df_cleaned.to_csv(csv, index=False)

    print("Numar total de spike-uri normalizate: " + str(spike_count))

def delete_houses_with_30_days_zero_consumption(): # Stergerea caselor cu 30 de zile consecutive cu 0 consum
    consumption_file = "Database/Consumption.csv"
    house_file = "Database/House.csv"
    threshold = 30

    df_consumption = pd.read_csv(consumption_file)
    df_house = pd.read_csv(house_file)

    # Convertim EpochTime in datetime si extragem doar data
    df_consumption['Datetime'] = pd.to_datetime(df_consumption['EpochTime'], unit='s')
    df_consumption['Date'] = df_consumption['Datetime'].dt.date

    # Calculam consumul total zilnic per casa
    daily = df_consumption.groupby(['HouseIDREF', 'Date'])['Value'].sum().reset_index()
    daily = daily.sort_values(by=['HouseIDREF', 'Date']).reset_index(drop=True)

    houses_to_remove = set()

    # Verificam pentru fiecare casa daca are 30 zile consecutive cu 0 consum
    for house_id, group in daily.groupby('HouseIDREF'):
        zero_streak = 0
        last_day = None

        for _, row in group.iterrows():
            day = row['Date']
            consumption = row['Value']

            if consumption == 0.0:
                if last_day is None or (day - last_day).days == 1:
                    zero_streak += 1
                else:
                    zero_streak = 1

                if zero_streak >= threshold:
                    houses_to_remove.add(house_id)
                    break
            else:
                zero_streak = 0

            last_day = day

    df_house_cleaned = df_house[~df_house['ID'].isin(houses_to_remove)]
    df_house_cleaned.to_csv(house_file, index=False)

    print("Case eliminate cu " + str(threshold) + " zile consecutive cu 0 consum: " + str(houses_to_remove))

def correct_negative_weather_values(): # Corectarea valorilor din statiile meteo cu valori sub 0
    csv_file = "Database/WeatherData.csv"
    df = pd.read_csv(csv_file)

    negative_count = (df['Value'] < 0).sum()

    if negative_count == 0:
        print("Nu au fost gasite valori negative in fisier.")
        return

    df.loc[df['Value'] < 0, 'Value'] = 0
    df.to_csv(csv_file, index=False)

    print("Au fost corectate " + str(negative_count) + " valori negative din WeatherData.")

def remove_houses_with_no_radiation_data(): # Sterge casele care nu au asociata o statie meteo cu radiatia inregistrata
    house_file = 'Database/House.csv'
    weather_file = 'Database/WeatherData.csv'

    df_house = pd.read_csv(house_file)
    df_weather = pd.read_csv(weather_file)

    radiation_data = df_weather[df_weather['WeatherVariableIDREF'] == 4]
    stations_with_radiation = set(radiation_data['WeatherStationIDREF'])

    df_house_filtered = df_house[df_house['WeatherStationIDREF'].isin(stations_with_radiation)]

    df_house_filtered.to_csv(house_file, index=False)

    print(str(len(df_house) - len(df_house_filtered)) + " case eliminate care nu au valori pentru radiatie la statia meteo.")
    return df_house_filtered   

def clean_all_tables():  # Filtrare in toate csv-urile dupa casele care au ramas in House.csv
    house_file = "Database/House.csv"
    appliance_file = "Database/Appliance.csv"
    consumption_file = "Database/Consumption.csv"
    weather_station_file = "Database/WeatherStation.csv"
    weather_data_file = "Database/WeatherData.csv"
    record_file = "Database/Record.csv"

    # Citire House.csv si extragere ID-uri valide
    df_house = pd.read_csv(house_file)
    valid_house_ids = set(df_house['ID'])
    valid_station_ids = set(df_house['WeatherStationIDREF'].dropna().astype(int))

    # Appliance.csv
    df_appliance = pd.read_csv(appliance_file)
    initial_appliance_rows = len(df_appliance)
    df_appliance = df_appliance[df_appliance['HouseIDREF'].isin(valid_house_ids)]
    df_appliance.to_csv(appliance_file, index=False)
    print(str(initial_appliance_rows - len(df_appliance)) + " randuri eliminate din " + appliance_file)

    # Consumption.csv
    df_consumption = pd.read_csv(consumption_file)
    initial_consumption_rows = len(df_consumption)
    df_consumption = df_consumption[df_consumption['HouseIDREF'].isin(valid_house_ids)]
    df_consumption.to_csv(consumption_file, index=False)
    print(str(initial_consumption_rows - len(df_consumption)) + " randuri eliminate din " + consumption_file)

    # WeatherStation.csv
    df_station = pd.read_csv(weather_station_file)
    initial_station_count = len(df_station)
    df_station = df_station[df_station['ID'].isin(valid_station_ids)]
    df_station.to_csv(weather_station_file, index=False)
    print(str(initial_station_count - len(df_station)) + " statii meteo eliminate din " + weather_station_file)

    # WeatherData.csv
    df_weather_data = pd.read_csv(weather_data_file)
    initial_weather_data_rows = len(df_weather_data)
    df_weather_data = df_weather_data[df_weather_data['WeatherStationIDREF'].isin(valid_station_ids)]
    df_weather_data.to_csv(weather_data_file, index=False)
    print(str(initial_weather_data_rows - len(df_weather_data)) + " randuri eliminate din " + weather_data_file)

    # Record.csv
    df_record = pd.read_csv(record_file)
    initial_record_rows = len(df_record)
    df_record = df_record[df_record['WeatherStationIDREF'].isin(valid_station_ids)]
    df_record.to_csv(record_file, index=False)
    print(str(initial_record_rows - len(df_record)) + " randuri eliminate din " + record_file)

def clean_files(): # Apelez toate functiile de filtrare
    # Functii de stergere
    delete_houses_with_30_days_zero_consumption()
    delete_house_less_than_a_year()
    remove_houses_with_no_radiation_data()
    clean_all_tables()
    
    # Functii de corectare valori
    normalize_spikes()
    correct_negative_weather_values()
