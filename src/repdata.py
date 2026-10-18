"""Загрузка результатов расчётов для текста отчёта и форматирование чисел (десятичная запятая)."""
import json
from pathlib import Path

import numpy as np
import pandas as pd

from params import P, RANGES

ROOT = Path(__file__).resolve().parents[1]
T = ROOT / "results" / "tables"
FIG = ROOT / "results" / "fig"
PHOTO = ROOT / "data" / "photos"


def f(x, d=1):
    """Число с десятичной запятой и пробелом-разделителем тысяч."""
    if x is None or (isinstance(x, float) and not np.isfinite(x)):
        return "–"
    s = f"{x:,.{d}f}".replace(",", " ").replace(".", ",")
    return s.replace("-", "−")


def pc(x, d=1):
    return f(100 * x, d)


class Data:
    def __init__(self):
        rd = lambda n: pd.read_csv(T / n)
        self.S = json.loads((ROOT / "results" / "summary.json").read_text())
        self.M = self.S["models"]
        self.passes = rd("passes.csv")
        self.reg = rd("regimes_measured.csv")
        self.ses = rd("sessions.csv")
        self.bg = rd("background.csv")
        self.bal = rd("session_balance.csv")
        self.turns = rd("turns.csv")
        self.unc = rd("uncertainty.csv")
        self.th = rd("thermal_fit.csv")
        self.val = rd("model_validation.csv")
        self.w = rd("weights.csv")
        self.cmp = {s: rd(f"compare_{s}.csv") for s in ("S1", "S2")}
        self.top = {s: rd(f"topsis_{s}.csv") for s in ("S1", "S2")}
        self.mcs = rd("mc_summary.csv")
        self.src = pd.read_csv(T / "sensitivity_src.csv", index_col=0)
        self.meas = rd("measures.csv")
        self.anova = {k: rd(f"anova_{k}.csv") for k in ("cult_e_kWh_ha", "cult_power_kW", "till_e_kWh_ha", "till_power_kW")}
        self.zt = rd("zone_tech.csv")
        self.zo = rd("zone_org.csv")
        self.ze = rd("zone_econ.csv")
        self.cult = rd("cult_traction.csv")
        self.till = rd("till_rotor.csv")
        self.P = P
        self.RANGES = RANGES

    def r(self, impl, a, v):
        g = self.reg
        return g[(g.implement == impl) & np.isclose(g.a_plan, a) & np.isclose(g.v_plan, v)].iloc[0]

    def c(self, sc, impl, a, v):
        g = self.cmp[sc]
        return g[(g.implement == impl) & np.isclose(g.a, a) & np.isclose(g.v, v)].iloc[0]

    def mc(self, sc, impl, a, v):
        g = self.mcs
        return g[(g.scen == sc) & (g.implement == impl) & np.isclose(g.a, a) & np.isclose(g.v, v)].iloc[0]

    def bgv(self, key, col="P_mean_kW"):
        return self.bg[self.bg.regime.str.startswith(key)][col].mean()

    def ses_row(self, key):
        return self.ses[self.ses.session == key].iloc[0]


def rng(s, d=0, k=1.0):
    """Диапазон «мин–макс» значений s (с множителем k); одно значение, если границы совпадают."""
    v = np.asarray(list(s), float) * k
    v = v[np.isfinite(v)]
    lo, hi = f(v.min(), d), f(v.max(), d)
    if lo == hi:
        return lo
    # при отрицательной нижней границе тире неоднозначно со знаком минус – используется многоточие
    return f"{lo}…{hi}" if lo.startswith("−") else f"{lo}–{hi}"
