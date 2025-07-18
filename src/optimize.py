import numpy as np
from scipy.optimize import differential_evolution

def _pv_production_for_n(indicator_obj, n_panels, Pm=575, f=0.8, GTSTC=1000.0):
    if not indicator_obj.solar_radiation:
        raise ValueError("solar_radiation nu este incarcata; apeleaza get_solar_radiation() inainte de optimizare.")
    prod = {}
    for t, G in indicator_obj.solar_radiation.items():
        power_W = Pm * n_panels * f * (G / GTSTC)
        prod[t] = power_W / 1000.0  # kWh intr-o ora
    return prod

def _objective_max_sc_ss(x, indicator_obj, w_sc=0.5, w_ss=0.5,
                         Pm=575, f=0.8, GTSTC=1000.0, round_panels=True, quiet=True):
    n_panels = x[0]
    if round_panels:
        n_panels = max(1, int(round(n_panels)))

    prod_backup = indicator_obj.production
    indicator_obj.production = _pv_production_for_n(indicator_obj, n_panels, Pm=Pm, f=f, GTSTC=GTSTC)

    # calc indicatori (suprimă print)
    if quiet:
        old_print = indicator_obj.calculate_indicator
        def silent_calc(kind):
            # apelam originalul dar nu printam -> scrie rapid varianta ta silent
            return old_print(kind)  # TODO: adaptează dacă vrei liniște completă
        sc_val = indicator_obj.calculate_indicator("SC")
        ss_val = indicator_obj.calculate_indicator("SS")
    else:
        sc_val = indicator_obj.calculate_indicator("SC")
        ss_val = indicator_obj.calculate_indicator("SS")

    indicator_obj.production = prod_backup

    if sc_val is None or ss_val is None:
        return 1e9

    score = (w_sc * sc_val) + (w_ss * ss_val)
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
    if not indicator_obj.consumption:
        raise ValueError("indicator_obj.consumption gol.")
    if not indicator_obj.solar_radiation:
        raise ValueError("indicator_obj.solar_radiation gol.")

    bounds = [(n_min, n_max)]

    result = differential_evolution(
        _objective_max_sc_ss,
        bounds=bounds,
        args=(indicator_obj, w_sc, w_ss, Pm, f, GTSTC, True, True),
        maxiter=maxiter,
        popsize=popsize,
        seed=seed,
        disp=disp,
    )

    n_opt = int(round(result.x[0]))
    n_opt = max(n_min, min(n_opt, n_max))

    indicator_obj.production = _pv_production_for_n(indicator_obj, n_opt, Pm=Pm, f=f, GTSTC=GTSTC)

    sc_opt = indicator_obj.calculate_indicator("SC")
    ss_opt = indicator_obj.calculate_indicator("SS")
    best_score = (w_sc * sc_opt) + (w_ss * ss_opt)

    if disp:
        print("\n=== Rezultate Differential Evolution ===")
        print(f"n_panels optim: {n_opt}")
        print(f"SC: {sc_opt:.3f}")
        print(f"SS: {ss_opt:.3f}")
        print(f"Scor combinat: {best_score:.3f}")
        print(f"SciPy fun raw: {result.fun:.6f} (negativ scor).")
        print("========================================\n")

    return {
        'best_n': n_opt,
        'best_score': best_score,
        'best_SC': sc_opt,
        'best_SS': ss_opt,
        'scipy_result': result,
    }
