import numpy as np
from scipy.optimize import differential_evolution

# Vom folosi formula din EnergyProcessing.get_power_estimated,
# dar fara a modifica permanent obiectul pana nu stim n_opt.
def _pv_production_for_n(indicator_obj, n_panels, Pm=575, f=0.8, GTSTC=1000.0):

    # radiatia solara trebuie sa o avem deja
    if not indicator_obj.solar_radiation:
        raise ValueError("solar_radiation nu este incarcat in obiect; apeleaza get_solar_radiation() inainte de optimizare.")
    
    prod = {}
    # Pm [W] per panou; G [W/m^2]; f factor pierderi; GTSTC=1000 W/m^2
    # energie ora [kWh] = (Pm * n * f * G / GTSTC) / 1000
    for t, G in indicator_obj.solar_radiation.items():
        power_W = Pm * n_panels * f * (G / GTSTC)
        energy_kWh = power_W / 1000.0
        prod[t] = energy_kWh
    return prod


def _objective_max_sc_ss(x, indicator_obj, w_sc=0.5, w_ss=0.5,
                         Pm=575, f=0.8, GTSTC=1000.0, round_panels=True):
    """
    Functia obiectiv pentru DE.
    x: vector numpy (diferential evolution trimite array). Noi luam x[0] = n_panels.
    Returnam o valoare de *minimizat*, deci folosim -score (pentru maximizare).
    """
    # extragem n_panels
    n_panels = x[0]
    if round_panels:
        n_panels = max(1, int(round(n_panels)))

    # calculeaza productie temporara
    temp_prod = _pv_production_for_n(indicator_obj, n_panels, Pm=Pm, f=f, GTSTC=GTSTC)

    # salvam productie curenta reala si repunem dupa
    prod_backup = indicator_obj.production

    indicator_obj.production = temp_prod  # incarcam pentru apel SC/SS

    # calculeaza SC si SS
    sc_val = indicator_obj.calculate_indicator("SC")
    ss_val = indicator_obj.calculate_indicator("SS")

    # revine la productie initiala (nu vrem efect cumulativ)
    indicator_obj.production = prod_backup

    # daca unul din indicatori nu a fost calculat (None), penalizam
    if sc_val is None or ss_val is None:
        return 1e9  # penalizare mare => evitam configuratia

    # calculare scor
    score = (w_sc * sc_val) + (w_ss * ss_val)

    # minimizeaza -> intoarcem negativul pentru maximizare
    return -score


def optimize_panels_de(indicator_obj,
                       n_min=1,
                       n_max=40,
                       w_sc=0.5,
                       w_ss=0.5,
                       Pm=575,
                       f=0.8,
                       GTSTC=1000.0,
                       maxiter=40,
                       popsize=15,
                       seed=None,
                       disp=True):
    """
    Optimizeaza numarul de panouri PV folosind Differential Evolution
    pentru a maximiza o combinatie ponderata a SC si SS.

    Parameters
    ----------
    indicator_obj : Indicators
        Obiect deja initializat cu house_id si cu date incarcate:
        indicator_obj.get_consumption(); indicator_obj.get_solar_radiation().
    n_min, n_max : int
        Interval permis pentru numarul de panouri.
    w_sc, w_ss : float
        Ponderi pentru SC si SS in functia obiectiv. w_sc + w_ss != obligatoriu 1, se scaleaza natural.
    Pm : float
        Putere unui panou [W].
    f : float
        Factor pierderi (eficienta BOS, cabluri etc.).
    GTSTC : float
        Irradianta de referinta STC [W/m^2].
    maxiter, popsize, seed, disp : parametri SciPy DE.

    """
    # verificari
    if not indicator_obj.consumption:
        raise ValueError("indicator_obj.consumption este gol. Apeleaza indicator_obj.get_consumption() inainte.")
    if not indicator_obj.solar_radiation:
        raise ValueError("indicator_obj.solar_radiation este gol. Apeleaza indicator_obj.get_solar_radiation() inainte.")

    # definim bounds pentru SciPy DE (liste de tuple)
    # DE lucreaza in float; noi vom rotunji in obiectiv
    bounds = [(n_min, n_max)]

    # rulam DE
    result = differential_evolution(
        _objective_max_sc_ss,
        bounds=bounds,
        args=(indicator_obj, w_sc, w_ss, Pm, f, GTSTC, True),
        maxiter=maxiter,
        popsize=popsize,
        seed=seed,
        disp=disp
    )

    # extragem n optim
    n_opt = int(round(result.x[0]))
    n_opt = max(n_min, min(n_opt, n_max))

    # calculam productie finala pt n_opt si setam in obiect
    indicator_obj.production = _pv_production_for_n(indicator_obj, n_opt, Pm=Pm, f=f, GTSTC=GTSTC)

    # recalc SC/SS finale
    sc_opt = indicator_obj.calculate_indicator("SC")
    ss_opt = indicator_obj.calculate_indicator("SS")

    best_score = (w_sc * sc_opt) + (w_ss * ss_opt)

    if disp:
        print("\n=== Rezultate Differential Evolution ===")
        print(f"n_panels optim: {n_opt}")
        print(f"SC: {sc_opt:.3f}")
        print(f"SS: {ss_opt:.3f}")
        print(f"Scor combinat (w_sc={w_sc}, w_ss={w_ss}): {best_score:.3f}")
        print(f"SciPy DE raw fun eval: {result.fun:.6f} (negativul scorului)")
        print("========================================\n")

    return {
        'best_n': n_opt,
        'best_score': best_score,
        'best_SC': sc_opt,
        'best_SS': ss_opt,
        'scipy_result': result 
    }
