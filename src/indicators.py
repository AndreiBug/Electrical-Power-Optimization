# Functii pentru calculul SS, SC, NPV, NEEG
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

    def self_consumption(self): # Calculul SC
        if not self.is_production_available() or not self.is_consumption_available():
            return

        numerator = 0
        denominator = 0

        for t, prod in self.production.items():
            cons = self.consumption.get(t, 0)  # Daca nu exista consum pt acel timp, consideram 0
            numerator += min(prod, cons)
            denominator += prod

        if denominator == 0:
            print("Productia totala este zero. SC nu poate fi calculat.")
            self.SC = 0
            return 0

        self.SC = numerator / denominator

        print(f"Self-Consumption (SC): {self.SC:.3f}")
        return self.SC

    def self_sufficiency(self): # Calculul SS
        if not self.is_production_available() or not self.is_consumption_available():
            return

        numerator = 0
        denominator = 0

        for t, prod in self.production.items():
            load = self.consumption.get(t, 0)  # Daca nu exista consum pt acel timp, consideram 0
            numerator += min(prod, load)
            denominator += load

        if denominator == 0:
            print("Consumul total este zero. SS nu poate fi calculat.")
            self.SS = 0
            return 0

        self.SS = numerator / denominator

        print(f"Self-Sufficiency (SS): {self.SS:.3f}")
        return self.SS

    def calculate_NEEG(self): # Calculul NEEG
        if not self.is_production_available() or not self.is_consumption_available():
            return

        neeg = 0

        for t, prod in self.production.items():
            cons = self.consumption.get(t, 0)
            diff = abs(prod - cons)
            neeg += diff

        self.NEEG = neeg

        print(f"Net Energy Exchanged with the Grid (NEEG): {self.NEEG:.3f} kWh")
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

        # Energie consumata medie pe ora (date reale), scalata la un an
        E_cons_total = sum(self.consumption.values())  # kWh
        E_cons_an = (E_cons_total / len(self.consumption)) * 8760

        # Factura fara PV
        B_ref = E_cons_an * price_per_kWh

        # Productia anuala
        E_prod_total = sum(self.production.values())
        E_prod_an = (E_prod_total / len(self.production)) * 8760

        # Factura reala cu PV
        B_real = max(0, B_ref - E_prod_an * price_per_kWh)

        # Castig anual
        G = B_ref - B_real

        # NPV
        npv = -CapEX
        for t in range(1, Y + 1):
            npv += (G - OpEX) / ((1 + r) ** t)

        self.NPV = npv
        print(f"NPV estimat: {self.NPV:.2f} EUR")
        return self.NPV
