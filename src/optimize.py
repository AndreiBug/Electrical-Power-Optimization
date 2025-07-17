# optimize.py
import copy
from typing import Callable, Dict, Tuple, Optional

from indicators import Indicators  # importa clasa ta (SS/SC/NPV/NEEG)

def make_objective(
    ind: Indicators,
    Pm: float = 575.0,
    f: float = 0.80,
    GTSTC: float = 1000.0,
    w_sc: float = 0.5,
    w_ss: float = 0.5,
) -> Callable[[int], float]:
    """
    Creeaza si returneaza o functie obiectiv(param: n_panels) -> scor_de_maximizat.

    Parametri
    ---------
    ind : Indicators
        Obiect deja creat pentru o casa; trebuie sa aiba
        ind.consumption (kWh/ora) si ind.solar_radiation (W/m^2 sau echiv.)
        deja populate (apeleaza inainte get_consumption(), get_solar_radiation()).
    Pm : float
        Puterea nominala a UNUI panou la 1000 W/m2 [W].
    f : float
        Factor de derating total (0..1).
    GTSTC : float
        Irradiance la STC [W/m2], tipic 1000.
    w_sc, w_ss : float
        Ponderi pentru combinatia SC/SS. Nu trebuie sa insumeze 1, se scaleaza intern.

    Return
    ------
    objective(n_panels: int) -> float
        Intoarce scor (mai mare = mai bine). Daca vrei sa folosesti
        un optimizer care *minimizeaza*, foloseste -objective().
    """

    # copie shallow; vom suprascrie campurile production temporar
    # (nu vrem sa alteram obiectul original in timpul cautarii)
    base_ind = ind

    def objective(n_panels: int) -> float:
        if n_panels <= 0:
            return -1e9  # scor foarte mic pentru valori invalide

        # facem o copie ca sa nu stricam productia persistata
        ind_local = copy.deepcopy(base_ind)

        # calculeaza productie pentru n_panels
        prod = {}
        for t, G in ind_local.solar_radiation.items():
            power_W = Pm * n_panels * f * G / GTSTC
            energy_kWh = power_W / 1000.0  # energie pe ora (G e medie pe ora)
            prod[t] = energy_kWh
        ind_local.production = prod

        # calculeaza SC + SS folosind functiile din Indicators
        sc_val = ind_local.self_consumption()
        ss_val = ind_local.self_sufficiency()

        # daca nu se poate calcula, penalizeaza
        if sc_val is None or ss_val is None:
            return -1e9

        # scor combinat
        score = (w_sc * sc_val) + (w_ss * ss_val)
        return score

    return objective


def grid_search_n_panels(
    ind: Indicators,
    n_min: int = 1,
    n_max: int = 20,
    **objective_kwargs,
) -> Tuple[int, float]:
    """
    Grid-search simplu peste n_panels in [n_min, n_max].
    Returneaza (best_n, best_score).
    """
    obj = make_objective(ind, **objective_kwargs)
    best_n = None
    best_score = float("-inf")

    for n in range(n_min, n_max + 1):
        score = obj(n)
        if score > best_score:
            best_score = score
            best_n = n

    print(f"Cea mai buna configuratie: n={best_n}, scor={best_score:.4f}")
    return best_n, best_score


def suggest_pv_size(
    ind: Indicators,
    n_min: int = 1,
    n_max: int = 20,
    w_sc: float = 0.5,
    w_ss: float = 0.5,
    Pm: float = 575.0,
    f: float = 0.80,
    GTSTC: float = 1000.0,
) -> int:
    """
    Wrapper convenabil: ruleaza grid-search si actualizeaza obiectul
    Indicators cu productia pentru n optim.
    Intoarce n optim.
    """
    best_n, _ = grid_search_n_panels(
        ind,
        n_min=n_min,
        n_max=n_max,
        w_sc=w_sc,
        w_ss=w_ss,
        Pm=Pm,
        f=f,
        GTSTC=GTSTC,
    )

    # regenereaza productia finala in obiectul real
    prod_final = {}
    for t, G in ind.solar_radiation.items():
        power_W = Pm * best_n * f * G / GTSTC
        prod_final[t] = power_W / 1000.0  # kWh/ora
    ind.production = prod_final

    # recalculeaza SC/SS finale
    ind.self_consumption()
    ind.self_sufficiency()

    return best_n
