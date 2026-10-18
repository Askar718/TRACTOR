"""Статистическая обработка опытов, сравнительная оценка ЭТ и дизельного аналога,
анализ чувствительности и построение зон оптимального использования.

Запуск: python3 src/analysis.py (после src/process.py)
Выход:  results/tables/*.csv, results/summary.json
"""
import json
from pathlib import Path

import numpy as np
import pandas as pd
import statsmodels.formula.api as smf
from scipy import stats
from statsmodels.stats.anova import anova_lm

from models import (CRITERIA, GROUPS, ahp_weights, entropy_weights, evaluate, fit_models,
                    power_point, rel_advantage, topsis, B_NOM)
from params import P, RANGES

ROOT = Path(__file__).resolve().parents[1]
T = ROOT / "results" / "tables"
CODES = [c[0] for c in CRITERIA]
RNG = np.random.default_rng(20261018)
SCEN = {"S1": None, "S2": 0.5}  # сменное задание: S1 — полная смена; S2 — 0,5 га/смену


def ci95(x):
    x = np.asarray(x, float)
    x = x[np.isfinite(x)]
    if len(x) < 2:
        return np.nan
    return stats.t.ppf(0.975, len(x) - 1) * x.std(ddof=1) / np.sqrt(len(x))


def base_params():
    bg = pd.read_csv(T / "background.csv")
    p = dict(P)
    rot = bg[bg["regime"].str.startswith("холостое вращение")]["P_mean_kW"].mean()
    p["P_rot0_el"] = rot - p["P_aux"]
    tr = pd.read_csv(T / "turns.csv")
    turn = {"t_s": tr["t_s"].mean(), "P_kW": tr["E_kWh"].sum() * 3600 / tr["t_s"].sum()}
    return p, turn


# --------------------------------------------------------------- опытные данные
def regime_table(ps):
    w = ps[(ps["kind"] == "рабочий") & (~ps["limit_attempt"])]
    rows = []
    for (impl, a, v), g in w.groupby(["implement", "a_plan_m", "v_plan_kmh"]):
        r = {"implement": impl, "a_plan": a, "v_plan": v, "n": len(g), "gear": g["gear"].iloc[0]}
        for col, name in [("power_kW", "P"), ("e_kWh_ha", "e"), ("W_ha_h", "W"), ("slip", "slip"),
                          ("v_fact_kmh", "v"), ("a_meas_mean_m", "a"), ("B_meas_m", "B"),
                          ("e_kJ_m3", "eV"), ("m2_current_A", "Im"), ("cell_delta_max_mV", "dU"),
                          ("pto_rpm", "pto"), ("cv_depth_pct", "cvA"), ("power_max_kW", "Pmax")]:
            r[f"{name}_mean"] = g[col].mean()
            r[f"{name}_sd"] = g[col].std(ddof=1)
            r[f"{name}_ci"] = ci95(g[col])
        r["pto_min"] = g["pto_rpm_min"].min()
        rows.append(r)
    return pd.DataFrame(rows)


def anova(ps):
    """Последовательный дисперсионный анализ (тип I) для неполного факторного плана в блоках.
    Степени свободы определяются рангом матриц вложенных моделей:
    блоки → +a → +v → +a×v (средние ячеек)."""
    out = {}
    w = ps[(ps["kind"] == "рабочий") & (~ps["limit_attempt"])].copy()
    for impl, g in w.groupby("implement"):
        g = g.reset_index(drop=True)
        blk = pd.get_dummies(g["block"].astype(int), drop_first=True, dtype=float)
        A = pd.get_dummies(g["a_plan_m"], drop_first=True, dtype=float)
        V = pd.get_dummies(g["v_plan_kmh"], drop_first=True, dtype=float)
        cell = pd.get_dummies(g["a_plan_m"].astype(str) + "_" + g["v_plan_kmh"].astype(str), drop_first=True, dtype=float)
        one = np.ones((len(g), 1))
        X = [np.hstack([one, blk]), np.hstack([one, blk, A]), np.hstack([one, blk, A, V]), np.hstack([one, blk, cell])]
        for y in ("e_kWh_ha", "power_kW"):
            yy = g[y].values
            rss, rk = [], []
            for Xi in X:
                beta, *_ = np.linalg.lstsq(Xi, yy, rcond=None)
                rss.append(((yy - Xi @ beta) ** 2).sum())
                rk.append(np.linalg.matrix_rank(Xi))
            sst = ((yy - yy.mean()) ** 2).sum()
            rows = [("Блоки", sst - rss[0], rk[0] - 1), ("Глубина a", rss[0] - rss[1], rk[1] - rk[0]),
                    ("Скорость v", rss[1] - rss[2], rk[2] - rk[1]), ("Взаимодействие a×v", rss[2] - rss[3], rk[3] - rk[2])]
            df_e = len(yy) - rk[3]
            ms_e = rss[3] / df_e
            tab = pd.DataFrame([{"source": n, "df": d, "SS": ss, "MS": ss / d, "F": ss / d / ms_e,
                                 "p": stats.f.sf(ss / d / ms_e, d, df_e), "eta2": ss / sst} for n, ss, d in rows]
                               + [{"source": "Остаток", "df": df_e, "SS": rss[3], "MS": ms_e, "F": np.nan, "p": np.nan, "eta2": rss[3] / sst},
                                  {"source": "Итого", "df": len(yy) - 1, "SS": sst, "MS": np.nan, "F": np.nan, "p": np.nan, "eta2": 1.0}])
            out[(impl, y)] = tab
            tab.to_csv(T / f"anova_{'cult' if impl == 'культиватор' else 'till'}_{y}.csv", index=False, encoding="utf-8-sig")
    return out


def regressions(m):
    res = {}
    c = m["cult_points"].copy()
    c["v2"] = (c["v_fact_kmh"] / 3.6) ** 2
    c["k_kNm2"] = c["k_Nm2"] / 1e3
    f1 = smf.ols("k_kNm2 ~ v2", data=c).fit()
    t = m["till_points"].copy()
    f2 = smf.ols("A_kJm3 ~ v_fact_kmh + a_meas_mean_m", data=t).fit()
    for name, f in (("cult_k", f1), ("till_A", f2)):
        res[name] = {"params": f.params.to_dict(), "bse": f.bse.to_dict(), "pvalues": f.pvalues.to_dict(),
                     "R2": f.rsquared, "R2adj": f.rsquared_adj, "F": f.fvalue, "F_p": f.f_pvalue,
                     "s": float(np.sqrt(f.scale)), "n": int(f.nobs)}
    # эмпирическая поверхность отклика P(a, v) — для контроля
    w = pd.concat([m["cult_points"], m["till_points"]])
    for impl, g in w.groupby("implement"):
        f = smf.ols("power_kW ~ a_meas_mean_m * v_fact_kmh + I(a_meas_mean_m**2) + I(v_fact_kmh**2)", data=g).fit()
        res[f"rs_{impl}"] = {"params": f.params.to_dict(), "pvalues": f.pvalues.to_dict(),
                             "R2": f.rsquared, "R2adj": f.rsquared_adj, "F": f.fvalue, "F_p": f.f_pvalue,
                             "s": float(np.sqrt(f.scale)), "n": int(f.nobs)}
    return res


def uncertainty(reg):
    """Бюджет неопределённости удельного расхода энергии e = P/(0,1·B·v) по ГОСТ 34100.3."""
    uB_P = np.sqrt((0.01 / np.sqrt(3)) ** 2 + (0.005 / np.sqrt(3)) ** 2)   # ток ±1 %, напряжение ±0,5 % (равномерн.)
    uB_v = np.sqrt((0.1 / 100 / np.sqrt(3)) ** 2 + (0.1 / 100 / np.sqrt(3)) ** 2)  # путь ±0,1 м; время ±0,1 с на ≥66 с
    uB_B = 0.01 / 1.2 / np.sqrt(3)
    uB = np.sqrt(uB_P ** 2 + uB_v ** 2 + uB_B ** 2)
    rows = []
    for _, r in reg.iterrows():
        uA = r["e_sd"] / np.sqrt(r["n"]) / r["e_mean"]
        uc = np.sqrt(uA ** 2 + uB ** 2)
        rows.append({"implement": r["implement"], "a": r["a_plan"], "v": r["v_plan"], "e": r["e_mean"],
                     "uA_pct": 100 * uA, "uB_pct": 100 * uB, "uc_pct": 100 * uc, "U95_pct": 200 * uc,
                     "U95_abs": 2 * uc * r["e_mean"]})
    return pd.DataFrame(rows), {"uB_P": uB_P, "uB_v": uB_v, "uB_B": uB_B, "uB": uB}


def thermal_fit():
    """Тепловая модель первого порядка двигателя хода: τ·dT/dt = T_окр + R_т·P − T."""
    from scipy.optimize import least_squares
    rows = []
    for key, stem in (("C", "cultivator_2026-09-15"), ("T1", "tiller_2026-10-14_session1"),
                      ("T2", "tiller_2026-10-15_session2")):
        d = pd.read_csv(ROOT / "data" / "can" / f"YL254ET_{stem}_log_1Hz.csv")
        d = d[d["m2_motor_temp_C"].notna()]
        Tm = d["m2_motor_temp_C"].values
        Pw = (d["power_kW"] - P["P_aux"]).clip(lower=0).values
        T0 = Tm[0]

        def sim(x):
            tau, R = x
            y = np.empty_like(Tm)
            y[0] = T0
            for k in range(1, len(Tm)):
                y[k] = y[k - 1] + (T0 + R * Pw[k - 1] - y[k - 1]) / tau
            return y

        sol = least_squares(lambda x: sim(x) - Tm, x0=(600, 2.0), bounds=([30, 0.01], [20000, 20]))
        y = sim(sol.x)
        rows.append({"session": key, "T_amb_C": T0, "tau_s": sol.x[0], "R_K_per_kW": sol.x[1],
                     "rmse_K": float(np.sqrt(((y - Tm) ** 2).mean())), "T_max_C": Tm.max()})
        pd.DataFrame({"t_s": d["t_s"].values, "T_meas": Tm, "T_model": y, "P_kW": Pw}).to_csv(
            T / f"thermal_{key}.csv", index=False)
    return pd.DataFrame(rows)


# --------------------------------------------------------------- сравнение
def regimes_list(ps):
    w = ps[(ps["kind"] == "рабочий") & (~ps["limit_attempt"])]
    return sorted({(r.implement, r.a_plan_m, r.v_plan_kmh) for r in w.itertuples()})


def compare(regs, p, m, turn, S_task):
    rows = []
    for impl, a, v in regs:
        q = dict(p, S_task=S_task)
        r, s, e, ET, D = evaluate(impl, a, v, q, m, turn)
        row = {"implement": impl, "a": a, "v": v, **{k: r[k] for k in r if k not in ("impl",)}}
        if s is not None:
            row.update({f"s_{k}": val for k, val in s.items()})
            row.update({f"e_{k}": val for k, val in e.items()})
            row.update({f"ET_{k}": ET[k] for k in CODES})
            row.update({f"D_{k}": D[k] for k in CODES})
            d = rel_advantage(ET, D)
            row.update({f"d_{k}": d[k] for k in CODES})
        rows.append(row)
    return pd.DataFrame(rows)


def integral(df, w):
    return sum(w[c] * df[f"d_{c}"] for c in CODES)


def weights(cmp_S1):
    ah = ahp_weights()
    feas = cmp_S1[cmp_S1["feas_ET"] & cmp_S1["feas_D"]]
    tab = pd.concat([feas[[f"ET_{c}" for c in CODES]].set_axis(CODES, axis=1),
                     feas[[f"D_{c}" for c in CODES]].set_axis(CODES, axis=1)], ignore_index=True)
    we = entropy_weights(tab)
    wc = {c: 0.5 * ah["w"][c] + 0.5 * we[c] for c in CODES}
    sw = sum(wc.values())
    wc = {c: x / sw for c, x in wc.items()}
    return ah, we, wc, tab


def topsis_check(cmp, w):
    f = cmp[cmp["feas_ET"] & cmp["feas_D"]].reset_index(drop=True)
    tab = pd.concat([f[[f"ET_{c}" for c in CODES]].set_axis(CODES, axis=1),
                     f[[f"D_{c}" for c in CODES]].set_axis(CODES, axis=1)], ignore_index=True)
    cl = topsis(tab, w)
    n = len(f)
    f["C_ET"], f["C_D"] = cl[:n], cl[n:]
    return f[["implement", "a", "v", "C_ET", "C_D"]]


def monte_carlo(ps, regs, turn, wc, n=1000):
    keys = list(RANGES)
    samples, out = [], []
    conc = 50.0
    wv = np.array([wc[c] for c in CODES])
    for i in range(n):
        x = {k: RNG.uniform(*RANGES[k]) for k in keys}
        p = dict(P, **x)
        p["P_rot0_el"] = turn["P_rot0_el"]
        m = fit_models(ps, p)
        ww = dict(zip(CODES, RNG.dirichlet(conc * wv)))
        for sc, St in SCEN.items():
            for impl, a, v in regs:
                q = dict(p, S_task=St)
                r, s, e, ET, D = evaluate(impl, a, v, q, m, turn)
                if s is None:
                    continue
                d = rel_advantage(ET, D)
                I = sum(ww[c] * d[c] for c in CODES)
                out.append({"it": i, "scen": sc, "implement": impl, "a": a, "v": v, "I": I,
                            "dC_tot": e["C_tot_ET"] - e["C_tot_D"], "feas_ET": r["feas_ET"], "feas_D": r["feas_D"]})
        samples.append(x)
    return pd.DataFrame(out), pd.DataFrame(samples)


def src_sensitivity(mc, smp, scen="S2"):
    """Стандартизованные коэффициенты регрессии индекса I по параметрам (усреднение по режимам)."""
    g = mc[mc["scen"] == scen].groupby("it")["I"].mean()
    X = smp.loc[g.index]
    Z = (X - X.mean()) / X.std()
    y = (g - g.mean()) / g.std()
    beta, *_ = np.linalg.lstsq(np.column_stack([np.ones(len(Z)), Z.values]), y.values, rcond=None)
    r2 = 1 - ((y.values - np.column_stack([np.ones(len(Z)), Z.values]) @ beta) ** 2).sum() / (y.values ** 2).sum()
    return pd.Series(beta[1:], index=X.columns).sort_values(key=np.abs, ascending=False), r2


# --------------------------------------------------------------- зоны
def zone_tech(p, m, turn, wc):
    grids = {"культиватор": (np.linspace(0.06, 0.16, 41), np.linspace(3.0, 6.0, 41)),
             "фреза": (np.linspace(0.06, 0.18, 41), np.linspace(1.5, 4.0, 41))}
    rows = []
    for impl, (A, V) in grids.items():
        for a in A:
            for v in V:
                r = power_point(impl, a, v, p, m)
                row = {"implement": impl, "a": a, "v": v, "P_el": r["P_el"], "P_shaft_D": r["P_shaft_D"],
                       "slip_ET": r["slip_ET"], "slip_D": r["slip_D"], "feas_ET": r["feas_ET"],
                       "feas_D": r["feas_D"], "cont_ET": r["cont_ET"]}
                for sc, St in SCEN.items():
                    q = dict(p, S_task=St)
                    rr, s, e, ET, D = evaluate(impl, a, v, q, m, turn)
                    if s is None:
                        row[f"I_{sc}"] = np.nan
                        continue
                    d = rel_advantage(ET, D)
                    row[f"I_{sc}"] = sum(wc[c] * d[c] for c in CODES)
                    if sc == "S1":
                        row["e_bat_ha"] = s["e_bat_ha"]
                        row["q_ha"] = s["q_ha"]
                        row["dC_tot"] = e["C_tot_ET"] - e["C_tot_D"]
                rows.append(row)
    return pd.DataFrame(rows)


REP = {"культиватор": (0.11, 4.5), "фреза": (0.12, 2.7)}


def zone_org(p, m, turn, wc):
    rows = []
    for impl, (a, v) in REP.items():
        for St in np.linspace(0.1, 4.0, 40):
            for l in np.linspace(0.0, 5.0, 26):
                q = dict(p, S_task=St, l_charge_km=l)
                r, s, e, ET, D = evaluate(impl, a, v, q, m, turn)
                d = rel_advantage(ET, D)
                rows.append({"implement": impl, "S_task": St, "l_km": l, "I": sum(wc[c] * d[c] for c in CODES),
                             "S_shift_ET": s["S_shift_ET"], "S_shift_D": s["S_shift_D"],
                             "A_charge": s["t_auton_ET"] / s["t_ha"], "n_charge": s["n_charge_shift"]})
    return pd.DataFrame(rows)


def zone_econ(p, m, turn, wc):
    rows = []
    for impl, (a, v) in REP.items():
        for Ty in np.linspace(100, 1500, 29):
            for cD in np.linspace(200, 600, 21):
                q = dict(p, S_task=SCEN["S2"], T_year_h=Ty, c_D=cD)
                r, s, e, ET, D = evaluate(impl, a, v, q, m, turn)
                d = rel_advantage(ET, D)
                rows.append({"implement": impl, "T_year": Ty, "c_D": cD,
                             "ratio": cD / p["c_el"], "dC_tot": e["C_tot_ET"] - e["C_tot_D"],
                             "dC_dir": e["C_dir_ET"] - e["C_dir_D"], "I": sum(wc[c] * d[c] for c in CODES)})
    return pd.DataFrame(rows)


def breakeven(p, m, turn):
    """Годовая загрузка, при которой совокупные удельные затраты ЭТ и Д равны."""
    out = {}
    for impl, (a, v) in REP.items():
        f = lambda Ty: (lambda e: e["C_tot_ET"] - e["C_tot_D"])(
            evaluate(impl, a, v, dict(p, S_task=SCEN["S2"], T_year_h=Ty), m, turn)[2])
        grid = np.linspace(50, 6000, 600)
        vals = np.array([f(x) for x in grid])
        idx = np.where(np.sign(vals[:-1]) != np.sign(vals[1:]))[0]
        out[impl] = float(grid[idx[0]] + (grid[idx[0] + 1] - grid[idx[0]]) * vals[idx[0]] / (vals[idx[0]] - vals[idx[0] + 1])) if len(idx) else None
    return out


def measures(p, m, turn, wc):
    """Влияние организационно-технических мер на показатели ЭТ (представительные режимы)."""
    E2 = 2 * P["E_bat_kWh"]
    var = [
        ("Базовый вариант", {}),
        ("Зарядное устройство 7 кВт", {"P_ch_ac": 7.0}),
        ("Батарея 46,7 кВт·ч (×2)", {"E_bat_kWh": E2, "price_ET_usd": P["price_ET_usd"] + P["E_bat_kWh"] * P["bat_usd_kWh"]}),
        ("Годовая загрузка 1500 ч", {"T_year_h": 1500.0}),
        ("Цена ДТ 450 тг/л", {"c_D": 450.0}),
        ("Зарядка 7 кВт + загрузка 1500 ч", {"P_ch_ac": 7.0, "T_year_h": 1500.0}),
    ]
    rows = []
    for name, kw in var:
        for impl, (a, v) in REP.items():
            q0 = dict(p, **kw)
            out = {"variant": name, "implement": impl}
            for sc, St in SCEN.items():
                q = dict(q0, S_task=St)
                r, s, e, ET, D = evaluate(impl, a, v, q, m, turn)
                d = rel_advantage(ET, D)
                out[f"I_{sc}"] = sum(wc[c] * d[c] for c in CODES)
            out.update({"S_shift_ET": s["S_shift_ET"], "S_shift_D": s["S_shift_D"],
                        "A_charge": s["t_auton_ET"] / s["t_ha"], "C_tot_ET": e["C_tot_ET"], "C_tot_D": e["C_tot_D"]})
            rows.append(out)
    return pd.DataFrame(rows)


def main():
    ps = pd.read_csv(T / "passes.csv")
    p, turn = base_params()
    m = fit_models(ps, p)
    turn["P_rot0_el"] = p["P_rot0_el"]

    reg = regime_table(ps)
    reg.to_csv(T / "regimes_measured.csv", index=False, encoding="utf-8-sig")
    av = anova(ps)
    rg = regressions(m)
    unc, ub = uncertainty(reg)
    unc.to_csv(T / "uncertainty.csv", index=False, encoding="utf-8-sig")
    th = thermal_fit()
    th.to_csv(T / "thermal_fit.csv", index=False, encoding="utf-8-sig")
    m["cult_points"].to_csv(T / "cult_traction.csv", index=False, encoding="utf-8-sig")
    m["till_points"].to_csv(T / "till_rotor.csv", index=False, encoding="utf-8-sig")

    regs = regimes_list(ps)
    cmp = {sc: compare(regs, p, m, turn, St) for sc, St in SCEN.items()}
    ah, we, wc, ent_tab = weights(cmp["S1"])
    for sc in SCEN:
        cmp[sc]["I"] = integral(cmp[sc], wc)
        cmp[sc]["I_ahp"] = integral(cmp[sc], ah["w"])
        cmp[sc].to_csv(T / f"compare_{sc}.csv", index=False, encoding="utf-8-sig")
    tp = {sc: topsis_check(cmp[sc], wc) for sc in SCEN}
    for sc in SCEN:
        tp[sc].to_csv(T / f"topsis_{sc}.csv", index=False, encoding="utf-8-sig")
    pd.DataFrame({"code": CODES, "group": [c[1] for c in CRITERIA], "name": [c[2] for c in CRITERIA],
                  "unit": [c[3] for c in CRITERIA], "sign": [c[4] for c in CRITERIA],
                  "w_ahp": [ah["w"][c] for c in CODES], "w_entropy": [we[c] for c in CODES],
                  "w": [wc[c] for c in CODES]}).to_csv(T / "weights.csv", index=False, encoding="utf-8-sig")

    # проверка модели по измеренной мощности
    val = []
    for _, r in reg.iterrows():
        pp = power_point(r["implement"], r["a_mean"], r["v_mean"], p, m)
        val.append({"implement": r["implement"], "a": r["a_plan"], "v": r["v_plan"], "P_meas": r["P_mean"],
                    "P_model": pp["P_el"], "err_pct": 100 * (pp["P_el"] / r["P_mean"] - 1)})
    val = pd.DataFrame(val)
    val.to_csv(T / "model_validation.csv", index=False, encoding="utf-8-sig")

    mc, smp = monte_carlo(ps, regs, turn, wc, n=1000)
    mc.to_csv(T / "mc_raw.csv", index=False)
    mcs = mc.groupby(["scen", "implement", "a", "v"]).agg(
        I_mean=("I", "mean"), I_p05=("I", lambda x: x.quantile(0.05)), I_p95=("I", lambda x: x.quantile(0.95)),
        P_pos=("I", lambda x: (x > 0).mean()), P_cost=("dC_tot", lambda x: (x < 0).mean())).reset_index()
    mcs.to_csv(T / "mc_summary.csv", index=False, encoding="utf-8-sig")
    src = {sc: src_sensitivity(mc, smp, sc) for sc in SCEN}
    pd.DataFrame({sc: src[sc][0] for sc in SCEN}).to_csv(T / "sensitivity_src.csv", encoding="utf-8-sig")

    zt = zone_tech(p, m, turn, wc)
    zt.to_csv(T / "zone_tech.csv", index=False)
    zo = zone_org(p, m, turn, wc)
    zo.to_csv(T / "zone_org.csv", index=False)
    ze = zone_econ(p, m, turn, wc)
    ze.to_csv(T / "zone_econ.csv", index=False)
    be = breakeven(p, m, turn)
    measures(p, m, turn, wc).to_csv(T / "measures.csv", index=False, encoding="utf-8-sig")

    summary = {
        "turn": turn, "P_rot0_el": p["P_rot0_el"],
        "models": {k: float(v) for k, v in m.items() if not isinstance(v, pd.DataFrame)},
        "regressions": rg, "uncertainty_B": ub,
        "ahp": {"groups": ah["groups"], "CR_groups": ah["CR_groups"], "lam": ah["lam_groups"],
                "local": ah["local"], "CR_local": ah["CR_local"]},
        "weights_entropy": we, "weights": wc, "breakeven_T_year": be,
        "src_R2": {sc: src[sc][1] for sc in SCEN},
        "validation_mape": float(val["err_pct"].abs().mean()),
        "anova": {f"{k[0]}|{k[1]}": v.to_dict(orient="list") for k, v in av.items()},
    }
    (ROOT / "results" / "summary.json").write_text(json.dumps(summary, ensure_ascii=False, indent=1, default=float))
    print(json.dumps({k: summary[k] for k in ("models", "weights", "breakeven_T_year", "validation_mape", "src_R2")},
                     ensure_ascii=False, indent=1, default=float))
    print(th)
    for sc in SCEN:
        print(sc, cmp[sc][["implement", "a", "v", "feas_ET", "feas_D", "cont_ET", "I"]].round(3).to_string())
    print(mcs.round(3).to_string())


if __name__ == "__main__":
    main()
