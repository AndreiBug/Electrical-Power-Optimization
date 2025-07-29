from energy_processing import EnergyProcessing

class Indicators(EnergyProcessing):
    def __init__(self, house_id):
        super().__init__(house_id)
        self.SC = 0
        self.SS = 0
        self.NPV = 0
        self.NEEG = 0  

    def is_production_available(self):
        if not self.production:
            print("Productia nu este disponibila.")
            return False
        return True

    def is_consumption_available(self):
        if not self.consumption:
            print("Consumul nu este disponibil.")
            return False
        return True

    def calculate_indicator(self, indicator_type): # Calculeaza SS sau SC, se dau ca parametru in functie
        if not self.is_production_available() or not self.is_consumption_available():
            return 0

        numerator = 0
        denominator = 0

        common_times = set(self.production.keys()) & set(self.consumption.keys())

        for t in common_times:
            prod = self.production[t]
            cons = self.consumption[t]
            numerator += min(prod, cons)

            if indicator_type == "SC":
                denominator += prod
            elif indicator_type == "SS":
                denominator += cons

        if denominator == 0:
            print(f"{indicator_type}: Numitorul este 0. Nu poate fi calculat.")
            setattr(self, indicator_type, 0)
            return 0

        value = numerator / denominator
        setattr(self, indicator_type, value)
        print(f"{indicator_type}: {value:.3f}")
        return value

    def calculate_NEEG(self): # Calculul NEEG
        if not self.is_production_available() or not self.is_consumption_available():
            return
        
        imported_energy = 0
        exported_energy = 0
        
        common_times = set(self.production.keys()) & set(self.consumption.keys())

        for t in common_times:
            prod = self.production[t]
            cons = self.consumption[t]
            
            if cons > prod:
                imported_energy += (cons - prod)
            elif prod > cons:
                exported_energy += (prod - cons)

        self.NEEG = imported_energy + exported_energy

        print(f"NEEG: {self.NEEG:.3f} kWh")
        return self.NEEG

    def calculate_NPV(self):  # Calculul NPV
        Cwp = 0.11  # Pret/W
        Pm = 575    # W
        n = 1       # Nr panouri
        Y = 20      # Ani
        r = 0.05    # Rata actualizare
        price_per_kWh = 0.2  # Valoarea pentru Franta

        if not self.is_production_available() or not self.is_consumption_available():
            return

        CapEX = Cwp * Pm * n
        OpEX = 0.03 * CapEX

        common_times = set(self.production.keys()) & set(self.consumption.keys())
        
        if not common_times:
            print("Nu exista date comune pentru calculul NPV.")
            return 0
        
        # Calculam energiile pentru perioada disponibila
        total_consumption = sum(self.consumption[t] for t in common_times)
        total_self_consumption = sum(min(self.production[t], self.consumption[t]) for t in common_times)
        
        # Extindem pe un an întreg (8760 ore)
        hours_available = len(common_times)
        annual_consumption = (total_consumption / hours_available) * 8760
        annual_self_consumption = (total_self_consumption / hours_available) * 8760

        # Factura fara PV
        B_ref = annual_consumption * price_per_kWh

        # Factura cu PV
        energy_from_grid = max(0, annual_consumption - annual_self_consumption)
        B_new = energy_from_grid * price_per_kWh

        # Castig anual
        G = B_ref - B_new

        # NPV
        npv = -CapEX
        for t in range(1, Y + 1):
            npv += (G - OpEX) / ((1 + r) ** t)

        self.NPV = npv
        print(f"NPV: {self.NPV:.3f}")
        return self.NPV