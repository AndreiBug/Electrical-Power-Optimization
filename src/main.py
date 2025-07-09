from house import House
from weather_station import WeatherStation
import clean
import plot
from energy_processing import EnergyProcessing
from indicators import Indicators

# Case eliminate cu 30 zile consecutive cu 0 consum: {2000925}
# Case eliminate cu mai putin de un an de date: [2000902, 2000981, 2000993]
# 62 case eliminate care nu au valori pentru radiatie la statia meteo.
# 634 randuri eliminate din Appliance.csv (case invalide).
# 33676139 randuri eliminate din Consumption.csv (case invalide).
# 32 statii meteo eliminate din WeatherStation.csv (fara case asignate).
# 3855724 randuri eliminate din WeatherData.csv (statii neasignate).
# 160 randuri eliminate din Record.csv (statii neasignate).
# Spike-urile au fost normalizate.
# Numar total de spike-uri normalizate: 375794
# Au fost corectate 16308 valori negative din WeatherData.

h = House(2000937)

# Curatare date
# clean.clean_files()

# Plotari
# plot.plot_10min_consumption_for_day(h, "1998-02-22")
# plot.plot_hourly_consumption_for_day(h, "1998-02-06")
# plot.plot_daily_consumption_in_a_year(h)
# plot.plot_appliance_hourly_consumption_for_day(h, "Fridge (Kitchen, 180l)", "1998-02-22")

indicator = Indicators(h.house_id)

# Obtinerea inndicatorilor
indicator.get_consumption()
indicator.get_solar_radiation()
indicator.get_power_estimated()

indicator.print_consumption()
indicator.print_solar_radiation()
indicator.print_power_estimated()

indicator.calculate_indicator("SS")
indicator.calculate_indicator("SC")
indicator.calculate_NEEG()
indicator.calculate_NPV()