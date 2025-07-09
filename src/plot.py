import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime

########## Plotarea graficelor ##########

def plot_10min_consumption_for_day(house, target_date):  # Plotare pe zi la interval de 10 minute pentru o casa
    
    input_csv = "Consumption.csv"
    df = pd.read_csv(input_csv)
    df = df[df['HouseIDREF'] == house.house_id]  # Pastreaza doar randurile care apartin casei curente

    if df.empty:
        print(f"Nu exista date pentru casa {house.house_id}.")
        return

    # Converteste EpochTime in data-ora si extrage doar data
    df['Datetime'] = pd.to_datetime(df['EpochTime'], unit='s')
    df['Date'] = df['Datetime'].dt.date

    # Verifica daca data introdusa este valida
    target_day = pd.to_datetime(target_date).date()

    # Cauta ziua ceruta
    df = df[df['Date'] == target_day]

    if df.empty:
        print(f"Nu exista consum în ziua {target_date} pentru casa {house.house_id}.")
        return

    # Grupare pe intervale de 10 minute
    df['Interval'] = df['Datetime'].dt.floor('10min')
    interval_total = df.groupby('Interval')['Value'].sum().reset_index()

    # interval_total['Value'] /= 1000  # Transformare în kWh

    fig = px.line(
        interval_total,
        x='Interval',
        y='Value',
        title=f'Consum total la 10 minute în ziua {target_date} pentru casa {house.house_id}',
        labels={'Interval': 'Ora (10 minute)', 'Value': 'Consum (W)'},
        markers=True
    )
    fig.update_layout(xaxis_tickformat='%H:%M')
    fig.write_html(f"consum_pe_10min_in_zi.html", auto_open=True)
    fig.show()

def plot_hourly_consumption_for_day(house, target_date):  # Plotare pe zi la interval de o ora pentru o casa
    input_csv = "Consumption.csv"  # Fisierul cu datele de consum

    df = pd.read_csv(input_csv)
    df = df[df['HouseIDREF'] == house.house_id]  # Filtrare dupa house_id

    if df.empty:
        print(f"Nu exista date pentru casa {house.house_id}.")
        return

    # Conversie EpochTime -> Datetime + extragere zi
    df['Datetime'] = pd.to_datetime(df['EpochTime'], unit='s')
    df['Date'] = df['Datetime'].dt.date

    try:
        target_day = pd.to_datetime(target_date).date()
    except Exception as e:
        print(f"Data introdusa este invalida: {e}")
        return

    df = df[df['Date'] == target_day]

    if df.empty:
        print(f"Nu exista consum in ziua {target_date} pentru casa {house.house_id}.")
        return

    # Grupare pe ore
    df['Hour'] = df['Datetime'].dt.floor('h')
    hourly_total = df.groupby('Hour')['Value'].sum().reset_index()
    hourly_total['Value'] /= 1000  # Transformare in kWh

    fig = px.line(
        hourly_total,
        x='Hour',
        y='Value',
        title=f'Consum total orar in ziua {target_date} pentru casa {house.house_id}',
        labels={'Hour': 'Ora', 'Value': 'Consum (kWh)'},
        markers=True
    )
    fig.update_layout(xaxis_tickformat='%H:%M')
    fig.write_html(f"consum_pe_ora_in_zi.html", auto_open=True)
    fig.show()

def plot_daily_consumption_in_a_year(house):  # Plotare pe an la interval de o zi pentru o casa
    input_csv = "Consumption.csv"

    df = pd.read_csv(input_csv)
    df = df[df['HouseIDREF'] == house.house_id]  # Filtrare dupa ID-ul casei

    if df.empty:
        print(f"Nu exista date pentru casa {house.house_id}.")
        return

    # Conversie EpochTime -> Datetime + extragere data
    df['Datetime'] = pd.to_datetime(df['EpochTime'], unit='s')
    df['Date'] = df['Datetime'].dt.date

    # Grupare pe zi si transformare in kWh
    daily_total = df.groupby('Date')['Value'].sum().reset_index()
    daily_total['Value'] /= 1000

    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=daily_total['Date'],
        y=daily_total['Value'],
        mode='lines+markers',
        name='Consum zilnic',
        marker=dict(size=6, color='royalblue'),
        line=dict(color='royalblue'),
        hovertemplate='Data: %{x}<br>Consum: %{y:.2f} kWh<extra></extra>'
    ))

    fig.update_layout(
        title=f'Consum total pe zi pentru casa {house.house_id}',
        xaxis_title='Data',
        yaxis_title='Consum (kWh)',
        xaxis_tickformat='%Y-%m-%d',
        hovermode='x unified'
    )

    fig.write_html(f"consum_pe_zi_in_an.html", auto_open=True)
    fig.show()

def plot_appliance_hourly_consumption_for_day(house, appliance_name, date_str):  # Plotare pe ora pentru un aparat intr-o zi specifica
    consumption_csv = "Consumption.csv"
    appliance_csv = "Appliance.csv"

    df_consumption = pd.read_csv(consumption_csv)
    df_appliance = pd.read_csv(appliance_csv)

    # Obtine ID-ul aparatului dupa nume si casa
    filtered_appliances = df_appliance[
        (df_appliance['HouseIDREF'] == house.house_id) &
        (df_appliance['Name'] == appliance_name)
    ]

    if filtered_appliances.empty:
        print(f"Appliance-ul '{appliance_name}' nu a fost gasit pentru casa {house.house_id}.")
        return

    appliance_id = filtered_appliances.iloc[0]['ID']

    # Filtrare consum pentru acel aparat
    df = df_consumption[
        (df_consumption['HouseIDREF'] == house.house_id) &
        (df_consumption['ApplianceIDREF'] == appliance_id)
    ].copy()

    if df.empty:
        print(f"Nu exista date de consum pentru appliance-ul '{appliance_name}' in casa {house.house_id}.")
        return

    # Conversie si filtrare dupa data
    df['Datetime'] = pd.to_datetime(df['EpochTime'], unit='s')
    df['Date'] = df['Datetime'].dt.date
    df['Hour'] = df['Datetime'].dt.hour

    target_date = pd.to_datetime(date_str).date()
    df = df[df['Date'] == target_date]

    if df.empty:
        print(f"Nu exista date pentru appliance-ul '{appliance_name}' in data {date_str}.")
        return

    # Agregare pe ora
    hourly = df.groupby('Hour')['Value'].sum().reset_index()

    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=hourly['Hour'],
        y=hourly['Value'],
        mode='lines+markers',
        marker=dict(size=6, color='royalblue'),
        line=dict(color='royalblue'),
        name='Consum',
        hovertemplate='Ora: %{x}<br>Consum: %{y:.2f} Wh<extra></extra>'
    ))

    fig.update_layout(
        title=f'Consum orar pentru {appliance_name} in casa {house.house_id} ({date_str})',
        xaxis_title='Ora',
        yaxis_title='Consum (Wh)',
        xaxis=dict(dtick=1),
        hovermode='x unified'
    )

    fig.write_html(f"appliance.html", auto_open=True)
    fig.show()

def plot_hourly_production_for_day(house, day=None):  # Plotare energie produsa pe ora intr-o zi
    if not hasattr(house, 'production') or not house.production:
        print("Datele de productie nu sunt disponibile.")
        return

    # Conversie epochtime -> datetime
    data = {datetime.fromtimestamp(int(k)): v for k, v in house.production.items()}

    # Determinam ziua ceruta
    if day is None:
        day = next(iter(data)).date()
    elif isinstance(day, str):
        day = datetime.fromisoformat(day).date()

    # Filtrare pe zi
    daily_data = {t: v for t, v in data.items() if t.date() == day}

    if not daily_data:
        print(f"Nu există date pentru ziua {day}.")
        return
    
    times = sorted(daily_data)
    values = [daily_data[t] for t in times]

    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=times,
        y=values,
        mode='lines+markers',
        name='Productie estimata',
        line=dict(color='orange'),
        marker=dict(size=6),
        hovertemplate='Ora: %{x|%H:%M}<br>Productie: %{y:.2f} kWh<extra></extra>'
    ))

    fig.update_layout(
        title=f'Productia estimata de energie pentru ziua {day}',
        xaxis_title='Ora',
        yaxis_title='Energie produsa (kWh)',
        xaxis=dict(
            tickformat='%H:%M',
            tickangle=45,
            title_standoff=10
        ),
        hovermode='x unified',
        template='plotly_white'
    )

    fig.write_html("productie_zi.html", auto_open=True)
    fig.show()
