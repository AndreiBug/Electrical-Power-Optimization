from house import House
from weather_station import WeatherStation
import clean
import plot
from energy_processing import EnergyProcessing
from indicators import Indicators
import optimize

h = House(2000933)

# Curatare date
# clean.clean_files()

indicator = Indicators(h.house_id)

# Obtinerea inndicatorilor
indicator.get_consumption()
indicator.get_solar_radiation()
indicator.get_power_estimated()
# indicator.print_consumption()
# indicator.print_solar_radiation()
# indicator.print_power_estimated()

indicator.calculate_indicator("SS")
indicator.calculate_indicator("SC")
indicator.calculate_NEEG()
indicator.calculate_NPV()

# Plotari
# plot.plot_10min_consumption_for_day(h, "1999-03-04")
# plot.plot_hourly_consumption_for_day(h, "1999-03-04")
# plot.plot_daily_consumption_in_a_year(h)
# plot.plot_appliance_hourly_consumption_for_day(h, "TV ()", "1999-03-04")
# plot.plot_hourly_production_for_day(indicator, "1999-03-04")

# Optimizare
# res = optimize.optimize_panels_de(
#     indicator_obj=indicator,
#     n_min=1,
#     n_max=40,
#     w_sc=0.5,
#     w_ss=0.5,
#     Pm=575,
#     f=0.8,
#     GTSTC=1000.0,
#     maxiter=40,
#     popsize=10,
#     seed=42,
#     disp=True
# )

# print("Rezultat final:", res)