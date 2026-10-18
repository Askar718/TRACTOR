"""Выгрузка числовых данных для построения рисунков в MATLAB (matlab/data/*.csv).

Все файлы — числовые CSV с одной строкой заголовка (латиница), разделитель — запятая.
Коды: машина 1 — культиватор, 2 — фреза.
Запуск: python3 src/export_matlab.py (после analysis.py)
"""
import json
from pathlib import Path

import numpy as np
import pandas as pd

from models import CRITERIA, fit_models, power_point, slip_curve
from params import P

ROOT = Path(__file__).resolve().parents[1]
T = ROOT / "results" / "tables"
CAN = ROOT / "data" / "can"
OUT = ROOT / "matlab" / "data"
CODES = [c[0] for c in CRITERIA]
IMPL = {"культиватор": 1, "фреза": 2}


def w(name, df):
    df.to_csv(OUT / f"{name}.csv", index=False, float_format="%.6g")


def wmat(name, M):
    np.savetxt(OUT / f"{name}.csv", np.asarray(M, float), delimiter=",", fmt="%.6g")


def log(stem):
    return pd.read_csv(CAN / f"YL254ET_{stem}_log_1Hz.csv")


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    S = json.loads((ROOT / "results" / "summary.json").read_text())
    M = S["models"]
    p = dict(P, P_rot0_el=S["P_rot0_el"])
    ps = pd.read_csv(T / "passes.csv")
    m = fit_models(ps, p)

    # 1. запись сессии с культиватором
    d = log("cultivator_2026-09-15")
    code = d["stype"].map({"рабочий ход": 1, "разворот": 2, "переезд": 3}).fillna(4)
    w("session_C", pd.DataFrame({"t_min": d.t_s / 60, "P": d.power_kW, "SOC": d.bms_soc_pct, "code": code}).dropna())

    # 2. баланс энергии и времени
    b = pd.read_csv(T / "session_balance.csv")
    order = ["рабочий ход", "разворот", "переезд", "гидропривод", "ВОМ", "замеры", "стоянка"]
    rows = []
    for s in ("C", "T1", "T2"):
        e = [b[(b.session == s) & (b.stype == st)].E_kWh.sum() for st in order]
        t = [b[(b.session == s) & (b.stype == st)].t_s.sum() / 60 for st in order]
        rows.append(e + t)
    w("balance", pd.DataFrame(rows, columns=[f"E{i}" for i in range(7)] + [f"t{i}" for i in range(7)]))
    wmat("balance_noh", rows)

    # 3. записи проходов
    zc = {"РУ": 1, "ЗД": 2, "УВ": 3}
    for stem, n, name in (("cultivator_2026-09-15", 4, "pass_cult"), ("tiller_2026-10-14_session1", 1, "pass_till")):
        d = log(stem)
        d = d[d["phase"].str.contains(f"проход {n}:")]
        w(name, pd.DataFrame({"t": d.t_s - d.t_s.iloc[0], "P": d.power_kW, "I": d.m2_current_A, "n": d.m2_rpm,
                              "pto": d.pto_rpm, "zone": d.zone.map(zc).fillna(0), "stage": d.phase.str.contains("рабочий ход").astype(int)}))
    for stem, n, name in (("cultivator_2026-09-15", 25, "limit_cult"), ("tiller_2026-10-14_session1", 17, "limit_till")):
        d = log(stem)
        d = d[d["phase"].str.contains(f"проход {n}: попытка")]
        w(name, pd.DataFrame({"t": d.t_s - d.t_s.iloc[0], "P": d.power_kW, "n": d.m2_rpm, "pto": d.pto_rpm, "I": d.m2_current_A}))

    # 4. режимы (средние по повторностям)
    r = pd.read_csv(T / "regimes_measured.csv")
    w("regimes", pd.DataFrame({"impl": r.implement.map(IMPL), "a": r.a_plan, "v": r.v_plan, "a_mean": r.a_mean,
                               "a_sd": r.a_sd, "v_mean": r.v_mean, "P": r.P_mean, "P_ci": r.P_ci, "e": r.e_mean,
                               "e_ci": r.e_ci, "slip": r.slip_mean, "eV": r.eV_mean, "pto_min": r.pto_min}))
    rows = []
    for impl, A, vr in (("культиватор", (0.08, 0.11, 0.14), (3.3, 5.7)), ("фреза", (0.08, 0.12, 0.16), (1.6, 3.8))):
        for a in A:
            for v in np.linspace(*vr, 45):
                rows.append((IMPL[impl], a, v, power_point(impl, a, v, p, m)["P_el"]))
    w("curves_power", pd.DataFrame(rows, columns=["impl", "a", "v", "P"]))

    # 5. проходы: глубина, тяга, фреза
    pw = ps[(ps.kind == "рабочий") & (~ps.limit_attempt)]
    w("depth", pd.DataFrame({"impl": pw.implement.map(IMPL), "a_plan": pw.a_plan_m, "v_plan": pw.v_plan_kmh,
                             "a_cm": pw.a_meas_mean_m * 100, "sd_cm": pw.a_meas_sd_m * 100}))
    c = m["cult_points"]
    w("cult_points", pd.DataFrame({"a": c.a_plan_m, "v2": (c.v_fact_kmh / 3.6) ** 2, "k": c.k_Nm2 / 1e3,
                                   "phi": c.phi_n, "slip": 100 * c.slip, "R": c.R_N / 1e3,
                                   "phiD": c.R_N / (P["m_D"] * P["g"]),
                                   "slipD": 100 * slip_curve(c.R_N / (P["m_D"] * P["g"]), m["phi_max"], m["k_slip"])}))
    ph = np.linspace(0, 0.6, 121)
    w("slip_curve", pd.DataFrame({"phi": ph, "slip": 100 * slip_curve(ph, m["phi_max"], m["k_slip"])}))
    t = m["till_points"]
    w("till_points", pd.DataFrame({"a": t.a_plan_m, "v": t.v_fact_kmh, "A": t.A_kJm3}))
    w("models", pd.DataFrame([{"f_roll": m["f_roll"], "k0": m["k0"] / 1e3, "eps": m["eps"] / 1e3, "phi_max": m["phi_max"],
                               "k_slip": m["k_slip"], "A0": m["A0"], "A1": m["A1"], "A2": m["A2"], "P_lim": P["P_el_lim"],
                               "slip_max": 100 * P["slip_max"], "C_Ah": P["C_bat_Ah"], "P_mot_1h": P["P_mot_1h"],
                               "eta_ep": P["eta_ep"], "P_aux": P["P_aux"], "P_pto_nom": P["k_pto_D"] * P["P_e_nom_D"],
                               "sfc_a": P["sfc_a"], "sfc_b": P["sfc_b"], "rho_D": P["rho_D"]}]))

    # 6. батарея и тепловой режим
    for k, stem in (("C", "cultivator_2026-09-15"), ("T1", "tiller_2026-10-14_session1"), ("T2", "tiller_2026-10-15_session2")):
        d = log(stem)
        d = d[d.bms_soc_pct.notna()]
        w(f"soc_{k}", pd.DataFrame({"Ah": d.bms_current_A.cumsum() / 3600, "SOC": d.bms_soc_pct}).iloc[::5])
    d = pd.concat([log(s) for s in ("cultivator_2026-09-15", "tiller_2026-10-14_session1", "tiller_2026-10-15_session2")])
    d = d[d.bms_current_A.notna()].iloc[::3]
    w("cells", pd.DataFrame({"I": d.bms_current_A, "dU": d.cell_delta_mV, "SOC": d.bms_soc_pct, "Umin": d.bms_cell_min_mV}))
    th = pd.read_csv(T / "thermal_T1.csv")
    w("thermal_T1", pd.DataFrame({"t_min": th.t_s / 60, "T": th.T_meas, "Tm": th.T_model}).iloc[::5])
    tf = pd.read_csv(T / "thermal_fit.csv")
    w("thermal_fit", tf[["T_amb_C", "tau_s", "R_K_per_kW", "rmse_K", "T_max_C"]])
    v = pd.read_csv(T / "model_validation.csv")
    w("validation", pd.DataFrame({"impl": v.implement.map(IMPL), "Pm": v.P_meas, "Pc": v.P_model}))

    # 7. сравнение
    for sc in ("S1", "S2"):
        cc = pd.read_csv(T / f"compare_{sc}.csv")
        out = {"impl": cc.implement.map(IMPL), "a": cc.a, "v": cc.v, "feasET": cc.feas_ET.astype(int),
               "feasD": cc.feas_D.astype(int), "I": cc.I, "PD": cc.P_shaft_D, "Q": cc.Q_Lh, "X": cc.X_D,
               "Acharge": cc.s_t_auton_ET / cc.s_t_ha, "SET": cc.s_S_shift_ET, "SD": cc.s_S_shift_D,
               "tautET": cc.s_t_auton_ET, "tautD": cc.s_t_auton_D}
        for k in CODES:
            out[f"ET_{k}"] = cc[f"ET_{k}"]
            out[f"D_{k}"] = cc[f"D_{k}"]
            out[f"d_{k}"] = cc[f"d_{k}"]
        for part in ("lab", "en", "rm", "cap"):
            for mach in ("ET", "D"):
                out[f"{part}_{mach}"] = cc[f"e_c_{part}_{mach}"]
        w(f"compare_{sc}", pd.DataFrame(out))
    wt = pd.read_csv(T / "weights.csv")
    w("weights", wt[["w_ahp", "w_entropy", "w"]])
    mc = pd.read_csv(T / "mc_raw.csv")
    c1 = pd.read_csv(T / "compare_S1.csv")
    for sc in ("S1", "S2"):
        g = mc[mc.scen == sc]
        cols = []
        for x in c1.itertuples():
            cols.append(g[(g.implement == x.implement) & np.isclose(g.a, x.a) & np.isclose(g.v, x.v)].sort_values("it").I.values)
        wmat(f"mc_{sc}", np.column_stack(cols))
    src = pd.read_csv(T / "sensitivity_src.csv", index_col=0)
    order = ["k_D", "EF_grid", "eta_ch", "eta_ep", "T_year_h", "PEF_el", "r_disc", "c_D", "eta_bat", "eta_tr",
             "c_el", "k_RM_ET", "k_landed", "k_pto_D", "bat_usd_kWh"]
    w("src", src.loc[order, ["S1", "S2"]].reset_index(drop=True))

    # 8. зоны
    zt = pd.read_csv(T / "zone_tech.csv")
    for impl, key in (("культиватор", "cult"), ("фреза", "till")):
        g = zt[zt.implement == impl]
        A = np.sort(g.a.unique()); V = np.sort(g.v.unique())
        wmat(f"zt_{key}_A", A); wmat(f"zt_{key}_V", V)
        for col in ("I_S1", "I_S2", "feas_ET", "feas_D", "cont_ET", "mrg_ET", "mrg_D", "mrg_cont"):
            wmat(f"zt_{key}_{col}", g.pivot(index="a", columns="v", values=col).reindex(index=A, columns=V).astype(float).values)
    zo = pd.read_csv(T / "zone_org.csv")
    for impl, key in (("культиватор", "cult"), ("фреза", "till")):
        g = zo[zo.implement == impl]
        Sx = np.sort(g.S_task.unique()); L = np.sort(g.l_km.unique())
        wmat(f"zo_{key}_S", Sx); wmat(f"zo_{key}_L", L)
        wmat(f"zo_{key}_I", g.pivot(index="l_km", columns="S_task", values="I").reindex(index=L, columns=Sx).values)
        wmat(f"zo_{key}_Ach", g.groupby("l_km").A_one.mean().reindex(L).values)
    ze = pd.read_csv(T / "zone_econ.csv")
    for impl, key in (("культиватор", "cult"), ("фреза", "till")):
        g = ze[ze.implement == impl]
        X = np.sort(g.T_year.unique()); Y = np.sort(g.c_D.unique())
        wmat(f"ze_{key}_T", X); wmat(f"ze_{key}_c", Y)
        wmat(f"ze_{key}_dC", g.pivot(index="c_D", columns="T_year", values="dC_tot").reindex(index=Y, columns=X).values / 1000)
    w("econ_point", pd.DataFrame([{"T_year": P["T_year_h"], "c_D": P["c_D"]}]))
    print("экспортировано файлов:", len(list(OUT.glob("*.csv"))))


if __name__ == "__main__":
    main()
