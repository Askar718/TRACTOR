"""Физические модели агрегатов, восстановленные по результатам опытов, и расчёт
сравнительных показателей электротрактора (ЭТ) и дизельного аналога (Д).

Принцип сопоставления: обе машины выполняют одну и ту же операцию тем же орудием
на той же почве с той же скоростью. Тяговое сопротивление орудия, мощность на привод
ротора фрезы и сопротивление качению определены по измерениям на ЭТ и перенесены на Д
с учётом различия масс (сопротивление качению, буксование) и различия силовых установок.
"""
import math

import numpy as np
import pandas as pd
from scipy.optimize import curve_fit

B_NOM = {"культиватор": 1.20, "фреза": 1.25}  # м, конструкционная ширина захвата


# ---------------------------------------------------------------- подбор моделей
def slip_curve(phi, phi_max, k, d0=0.0):
    """Кривая буксования по коэффициенту использования сцепного веса φ = R/G:
    φ = φ_max·(1 − exp(−k·δ))  ⇒  δ = −ln(1 − φ/φ_max)/k.
    Буксование отсчитывается от холостого прохода (ГОСТ 7057), поэтому δ(0) = 0."""
    return d0 - np.log(1.0 - np.clip(phi / phi_max, 0, 0.999999)) / k


def fit_models(passes, p):
    """Коэффициенты моделей по данным проходов при заданных КПД (η_эп, η_тр)."""
    m = {}
    g, eta_ep, eta_tr = p["g"], p["eta_ep"], p["eta_tr"]
    ok = passes[~passes["limit_attempt"]].copy()

    # --- культиватор: сопротивление передвижению и тяговое сопротивление
    c = ok[ok["implement"] == "культиватор"].copy()
    c0 = c[c["kind"] == "холостой"]
    c1 = c[c["kind"] == "рабочий"].copy()
    Fk0 = eta_ep * eta_tr * (c0["power_kW"] - p["P_aux"]) * 1e3 / (c0["v_fact_kmh"] / 3.6)
    f_roll = (Fk0 / (p["m_ET"] * g)).mean()
    m["f_roll"] = f_roll
    Ff = f_roll * p["m_ET"] * g
    # касательная сила тяги: F_к = η_эп·η_тр·(P − P_всп)·(1 − δ)/v
    c1["Fk_N"] = eta_ep * eta_tr * (c1["power_kW"] - p["P_aux"]) * 1e3 * (1 - c1["slip"]) / (c1["v_fact_kmh"] / 3.6)
    c1["R_N"] = c1["Fk_N"] - Ff
    c1["k_Nm2"] = c1["R_N"] / (c1["B_meas_m"] * c1["a_meas_mean_m"])
    X = np.column_stack([np.ones(len(c1)), (c1["v_fact_kmh"] / 3.6) ** 2])
    coef, *_ = np.linalg.lstsq(X, c1["k_Nm2"].values, rcond=None)
    m["k0"], m["eps"] = coef
    pred = X @ coef
    ss = ((c1["k_Nm2"] - c1["k_Nm2"].mean()) ** 2).sum()
    m["k_R2"] = 1 - ((c1["k_Nm2"] - pred) ** 2).sum() / ss
    # кривая буксования δ(φ), φ = R/G
    c1["phi_n"] = c1["R_N"] / (p["m_ET"] * g)
    phi, dl = c1["phi_n"].values, c1["slip"].values
    f = lambda d, a, b: a * (1 - np.exp(-b * d))
    (phi_max, k), _ = curve_fit(f, dl, phi, p0=(0.8, 5.0), bounds=([0.4, 0.1], [1.0, 200.0]), maxfev=20000)
    m["phi_max"], m["k_slip"], m["d0"] = phi_max, k, 0.0
    ph_pred = f(dl, phi_max, k)
    m["slip_R2"] = 1 - ((phi - ph_pred) ** 2).sum() / ((phi - phi.mean()) ** 2).sum()
    dl_pred = slip_curve(phi, phi_max, k)
    m["slip_rmse"] = float(np.sqrt(((dl - dl_pred) ** 2).mean()))
    m["cult_points"] = c1

    # --- фреза: P = P_всп + c_дв·v + P_р0 + A·B·a·v, A = A0 + A1·v + A2·a
    t = ok[ok["implement"] == "фреза"]
    t0 = t[t["kind"] == "холостой"]
    t1 = t[t["kind"] == "рабочий"].copy()
    c_v = ((t0["power_kW"] - p["P_aux"]) / (t0["v_fact_kmh"] / 3.6)).mean()  # кВт/(м/с)
    m["c_move"] = c_v
    m["P_rot0"] = p.get("P_rot0_el", 0.98)
    v = t1["v_fact_kmh"] / 3.6
    q = t1["B_meas_m"] * t1["a_meas_mean_m"] * v
    t1["P_till_kW"] = t1["power_kW"] - p["P_aux"] - c_v * v - m["P_rot0"]
    t1["A_kJm3"] = t1["P_till_kW"] / q
    X = np.column_stack([np.ones(len(t1)), t1["v_fact_kmh"], t1["a_meas_mean_m"]])
    coef, *_ = np.linalg.lstsq(X, t1["A_kJm3"].values, rcond=None)
    m["A0"], m["A1"], m["A2"] = coef
    pred = X @ coef
    m["A_R2"] = 1 - ((t1["A_kJm3"] - pred) ** 2).sum() / ((t1["A_kJm3"] - t1["A_kJm3"].mean()) ** 2).sum()
    m["till_points"] = t1
    # буксование с фрезой относительно холостого прохода (определено на передаче П2)
    m["slip_till_meas"] = float(t1["slip"].mean())
    m["slip_till"] = 0.0

    # --- пульсации мощности: коэффициент вариации в зачётной зоне
    w = ok[ok["kind"] == "рабочий"]
    m["cv_P"] = (w["power_sd_kW"] / w["power_kW"]).median()
    return m


# ------------------------------------------------------------- энергетика режима
def power_point(impl, a, v_kmh, p, m):
    """Мощности ЭТ и Д в режиме (a, v). Возвращает словарь; для невыполнимых режимов — NaN."""
    g = p["g"]
    v = v_kmh / 3.6
    B = B_NOM[impl]
    r = {"impl": impl, "a": a, "v": v_kmh, "B": B}
    if impl == "культиватор":
        R = B * a * (m["k0"] + m["eps"] * v ** 2)
        out = {}
        for mach, mass in (("ET", p["m_ET"]), ("D", p["m_D"])):
            Fk = R + m["f_roll"] * mass * g
            phi = R / (mass * g)
            if phi >= 0.995 * m["phi_max"]:
                out[mach] = (np.nan, np.nan, np.nan)
                continue
            d = float(slip_curve(phi, m["phi_max"], m["k_slip"]))
            P_shaft = Fk * v / (1 - d) / p["eta_tr"] / 1e3
            out[mach] = (P_shaft, d, phi)
        r["R_kN"] = R / 1e3
        r["P_shaft_ET"], r["slip_ET"], r["phi_ET"] = out["ET"]
        r["P_shaft_D"], r["slip_D"], r["phi_D"] = out["D"]
        r["P_shaft_D"] = r["P_shaft_D"] + p["P_hyd_idle_D"]
        r["P_el"] = p["P_aux"] + r["P_shaft_ET"] / p["eta_ep"]
    else:
        d = m["slip_till"]
        vt = v
        A = m["A0"] + m["A1"] * v_kmh + m["A2"] * a
        P_till = A * B * a * v
        P_move = m["c_move"] * vt
        r["P_el"] = p["P_aux"] + P_move + m["P_rot0"] + P_till
        r["P_shaft_ET"] = p["eta_ep"] * (r["P_el"] - p["P_aux"])
        r["P_shaft_D"] = p["eta_ep"] * (P_move * p["m_D"] / p["m_ET"] + m["P_rot0"] + P_till) + p["P_hyd_idle_D"]
        r["slip_ET"] = r["slip_D"] = d
        r["R_kN"] = np.nan
    P_pto_nom = p["k_pto_D"] * p["P_e_nom_D"]
    k_peak = 1 + 2 * m["cv_P"]
    r["reserve_ET"] = 1 - r["P_el"] * k_peak / p["P_el_lim"]
    r["reserve_D"] = 1 - r["P_shaft_D"] * k_peak / P_pto_nom
    r["feas_ET"] = bool(np.isfinite(r["P_el"]) and r["reserve_ET"] >= 0 and r["slip_ET"] <= p["slip_max"])
    r["feas_D"] = bool(np.isfinite(r["P_shaft_D"]) and r["reserve_D"] >= 0 and r["slip_D"] <= p["slip_max"])
    r["cont_ET"] = bool(r["feas_ET"] and r["P_shaft_ET"] <= p["P_mot_1h"])
    # часовой расход топлива Д на регуляторной ветви (ASABE D497.7, линейная форма)
    r["Q_Lh"] = p["k_D"] * (p["sfc_a"] * r["P_shaft_D"] + p["sfc_b"] * P_pto_nom)
    r["X_D"] = r["P_shaft_D"] / P_pto_nom
    return r


# ------------------------------------------------------- эксплуатационная модель
def shift_model(r, p, turn):
    """Сменная производительность, расход энергии и затраты на 1 га для ЭТ и Д.

    turn — средние длительность (с) и электрическая мощность (кВт) разворота (изм.).
    """
    B, v = r["B"], r["v"]
    W0 = 0.1 * B * v                                    # га/ч основного времени
    n_turn = 1e4 / (B * p["L_run_m"])                   # разворотов на 1 га
    t_ha = 1 / W0 + n_turn * turn["t_s"] / 3600         # ч работы в поле на 1 га
    T_av = p["T_shift_h"] * p["tau_svc"]
    t_tr = p["l_charge_km"] / p["v_transp_kmh"]         # ч, переезд в одну сторону
    E_tr = p["P_transp_kW"] * t_tr                      # кВт·ч, переезд ЭТ в одну сторону
    res = {"W0": W0, "t_ha": t_ha, "n_turn": n_turn}

    # --- электротрактор
    e_bat_ha = r["P_el"] * (1 / W0) + n_turn * turn["P_kW"] * turn["t_s"] / 3600  # кВт·ч/га из батареи
    E_use = p["E_bat_kWh"] * (p["SOC_max"] - p["SOC_min"]) / 100
    t_auton = E_use / (e_bat_ha / t_ha)                 # ч непрерывной работы на одной зарядке
    t_charge_full = E_use / (p["eta_ch"] * p["eta_bat"]) / p["P_ch_ac"]
    # имитация смены: переезд к полю, работа до SOC_min, переезд на зарядку, зарядка, возврат
    t, area, E_bat_tr, n_ch = t_tr, 0.0, E_tr, 0
    E_avail = E_use - E_tr
    while True:
        need_back = E_tr
        t_work = min((E_avail - need_back) / (e_bat_ha / t_ha), T_av - t - t_tr)
        if t_work <= 0:
            break
        area += t_work / t_ha
        t += t_work
        E_avail -= t_work * e_bat_ha / t_ha
        if T_av - t - t_tr <= 1e-6:
            break
        # зарядка в течение смены целесообразна, если после неё остаётся время на работу
        t_left = T_av - t - 2 * t_tr
        t_ch = (E_use - E_avail + E_tr) / (p["eta_ch"] * p["eta_bat"]) / p["P_ch_ac"]
        if t_left - t_ch < 0.25:
            break
        t += 2 * t_tr + t_ch
        E_bat_tr += 2 * E_tr
        n_ch += 1
        E_avail = E_use - E_tr
    E_bat_tr += E_tr
    res["S_shift_ET"] = area
    res["t_auton_ET"] = t_auton
    res["n_charge_shift"] = n_ch
    e_bat_total = e_bat_ha + (E_bat_tr / area if area > 0 else np.nan)
    res["e_bat_ha"] = e_bat_ha
    res["e_grid_ha"] = e_bat_total / (p["eta_ch"] * p["eta_bat"])
    res["t_rec_ET"] = res["e_grid_ha"] / p["P_ch_ac"]   # ч восполнения энергии на 1 га

    # --- дизельный аналог
    P_turn_D = p["eta_ep"] * (turn["P_kW"] - p["P_aux"]) + p["P_hyd_idle_D"]
    P_pto_nom = p["k_pto_D"] * p["P_e_nom_D"]
    Q_turn = p["k_D"] * (p["sfc_a"] * P_turn_D + p["sfc_b"] * P_pto_nom)
    P_tr_D = p["eta_ep"] * (p["P_transp_kW"] - p["P_aux"]) * p["m_D"] / p["m_ET"] + p["P_hyd_idle_D"]
    Q_tr = p["k_D"] * (p["sfc_a"] * P_tr_D + p["sfc_b"] * P_pto_nom)
    q_ha = r["Q_Lh"] / W0 + n_turn * turn["t_s"] / 3600 * Q_turn  # л/га
    Q_avg = q_ha / t_ha
    t_auton_D = p["tank_D"] / Q_avg
    t_work_D = T_av - 2 * t_tr
    n_ref = max(0.0, (t_work_D * Q_avg + 2 * t_tr * Q_tr) / p["tank_D"] - 1)  # дозаправок в смену
    t_work_D -= n_ref * p["t_refuel_h"]
    res["S_shift_D"] = t_work_D / t_ha
    res["q_ha"] = q_ha + 2 * t_tr * Q_tr / res["S_shift_D"]
    res["t_auton_D"] = t_auton_D
    res["t_rec_D"] = res["q_ha"] / p["tank_D"] * p["t_refuel_h"]
    res["Q_avg_Lh"] = Q_avg
    return res


def crf(r, n):
    return 1 / n if r == 0 else r * (1 + r) ** n / ((1 + r) ** n - 1)


def sff(r, n):
    """Коэффициент фонда возмещения (для учёта остаточной стоимости)."""
    return 1 / n if r == 0 else r / ((1 + r) ** n - 1)


def economics(r, s, p):
    """Удельные затраты, тг/га (ГОСТ 34393-2018: прямые эксплуатационные + приведённые)."""
    out = {}
    wage_h = p["wage_month"] / p["h_month"] * p["k_soc"]
    price = {"ET": p["price_ET_usd"] * p["usd_kzt"] * p["k_landed"],
             "D": p["price_D_usd"] * p["usd_kzt"] * p["k_landed"]}
    T_life = p["T_year_h"] * p["life_y"]
    # ремонт и ТО: накопленные затраты RF1·Ц·(h/1000)^RF2, средние на 1 ч; база — дизельный трактор
    rm_h_D = p["RF1"] * price["D"] * (T_life / 1000) ** p["RF2"] / T_life
    rm_h = {"D": rm_h_D, "ET": p["k_RM_ET"] * rm_h_D}
    for mach in ("ET", "D"):
        S = s[f"S_shift_{mach}"]
        h_ha = s["t_ha"]                     # моточасов (часов работы машины) на 1 га
        # оплата труда — за время работы машины (поле + переезды); простой на зарядке
        # учитывается показателем сменной производительности, а не затратами
        t_tr_ha = 2 * p["l_charge_km"] / p["v_transp_kmh"] * (1 + s.get("n_charge_shift", 0) if mach == "ET" else 1) / S
        lab = wage_h * (h_ha + t_tr_ha)
        if mach == "ET":
            en = s["e_grid_ha"] * p["c_el"]
        else:
            en = s["q_ha"] * p["c_D"]
        rm = rm_h[mach] * h_ha
        A_year = p["T_year_h"] / h_ha        # га/год
        cap = price[mach] * (crf(p["r_disc"], p["life_y"]) - p["salvage"] * sff(p["r_disc"], p["life_y"]))
        bat = 0.0
        if mach == "ET":
            cyc_y = A_year * s["e_bat_ha"] / p["E_bat_kWh"]
            life_bat = min(p["bat_cycles"] / max(cyc_y, 1e-9), p["bat_cal_y"])
            n_rep = max(0.0, p["life_y"] / life_bat - 1)
            C_bat = p["bat_usd_kWh"] * p["E_bat_kWh"] * p["usd_kzt"]
            bat = C_bat * n_rep / (1 + p["r_disc"]) ** life_bat * crf(p["r_disc"], p["life_y"])
            out["cycles_year"] = cyc_y
            out["life_bat_y"] = life_bat
        out[f"price_{mach}"] = price[mach]
        out[f"c_lab_{mach}"] = lab
        out[f"c_en_{mach}"] = en
        out[f"c_rm_{mach}"] = rm
        out[f"c_cap_{mach}"] = (cap + bat) / A_year
        out[f"C_dir_{mach}"] = lab + en + rm
        out[f"C_tot_{mach}"] = lab + en + rm + (cap + bat) / A_year
        out[f"A_year_{mach}"] = A_year
    return out


# ------------------------------------------------------------- система критериев
CRITERIA = [
    # код, группа, наименование, ед., направление (+1 больше — лучше; −1 меньше — лучше)
    ("I1", "Энергетические", "Удельные затраты подведённой энергии", "МДж/га", -1),
    ("I2", "Энергетические", "Удельные затраты первичной энергии", "МДж/га", -1),
    ("I3", "Технологические", "Коэффициент выполнения сменного задания", "–", +1),
    ("I4", "Технологические", "Буксование движителей", "%", -1),
    ("I5", "Технологические", "Запас мощности", "%", +1),
    ("I6", "Экономические", "Удельные прямые эксплуатационные затраты", "тг/га", -1),
    ("I7", "Экономические", "Удельные совокупные затраты", "тг/га", -1),
    ("I8", "Экологические", "Удельные выбросы CO₂ с учётом производства энергии", "кг/га", -1),
    ("I9", "Экологические", "Удельные выбросы CO₂ в месте выполнения работ", "кг/га", -1),
    ("I10", "Автономность", "Доля сменного задания, выполняемая без восполнения энергии", "–", +1),
]
GROUPS = ["Энергетические", "Технологические", "Экономические", "Экологические", "Автономность"]


def indicators(r, s, e, p):
    """Значения показателей. Сменное задание S_task, га/смену; при S_task = None задание
    равно сменной выработке дизельного аналога (машина загружена на всю смену)."""
    S_task = p.get("S_task") or s["S_shift_D"]
    s["S_task"] = S_task
    A_aut_ET = s["t_auton_ET"] / s["t_ha"]   # га, обрабатываемые на одной зарядке
    A_aut_D = s["t_auton_D"] / s["t_ha"]     # га, обрабатываемые на одной заправке
    ET = {
        "I1": s["e_grid_ha"] * 3.6,
        "I2": s["e_grid_ha"] * 3.6 * p["PEF_el"],
        "I3": min(1.0, s["S_shift_ET"] / S_task),
        "I4": 100 * r["slip_ET"],
        "I5": 100 * r["reserve_ET"],
        "I6": e["C_dir_ET"],
        "I7": e["C_tot_ET"],
        "I8": s["e_grid_ha"] * p["EF_grid"],
        "I9": 0.0,
        "I10": min(1.0, A_aut_ET / S_task),
    }
    D = {
        "I1": s["q_ha"] * p["LHV_D"],
        "I2": s["q_ha"] * p["LHV_D"] * p["PEF_D"],
        "I3": min(1.0, s["S_shift_D"] / S_task),
        "I4": 100 * r["slip_D"],
        "I5": 100 * r["reserve_D"],
        "I6": e["C_dir_D"],
        "I7": e["C_tot_D"],
        "I8": s["q_ha"] * p["EF_D"],
        "I9": s["q_ha"] * p["EF_D"],
        "I10": min(1.0, A_aut_D / S_task),
    }
    return ET, D


def rel_advantage(ET, D):
    """Симметричное относительное преимущество ЭТ по каждому показателю, d ∈ [−1; 1]."""
    d = {}
    for code, *_rest, sign in CRITERIA:
        x, y = ET[code], D[code]
        den = max(abs(x), abs(y))
        if den == 0:
            d[code] = 0.0
            continue
        d[code] = sign * (x - y) / den
    return d


def evaluate(impl, a, v, p, m, turn):
    r = power_point(impl, a, v, p, m)
    if not (np.isfinite(r["P_el"]) and np.isfinite(r["P_shaft_D"])):
        return r, None, None, None, None
    s = shift_model(r, p, turn)
    e = economics(r, s, p)
    ET, D = indicators(r, s, e, p)
    return r, s, e, ET, D


# ------------------------------------------------------------------ веса
def ahp(M):
    """Вектор приоритетов (главный собственный вектор) и отношение согласованности."""
    M = np.asarray(M, float)
    n = len(M)
    w, V = np.linalg.eig(M)
    i = np.argmax(w.real)
    vec = np.abs(V[:, i].real)
    vec /= vec.sum()
    lam = w[i].real
    RI = {1: 0, 2: 0, 3: 0.58, 4: 0.90, 5: 1.12, 6: 1.24, 7: 1.32}[n]
    CI = (lam - n) / (n - 1) if n > 1 else 0
    CR = CI / RI if RI else 0
    return vec, lam, CI, CR


AHP_GROUPS = [
    [1, 1/2, 1/2, 2, 1],
    [2, 1, 1, 3, 2],
    [2, 1, 1, 3, 2],
    [1/2, 1/3, 1/3, 1, 1/2],
    [1, 1/2, 1/2, 2, 1],
]
AHP_LOCAL = {
    "Энергетические": [[1, 1/2], [2, 1]],
    "Технологические": [[1, 3, 2], [1/3, 1, 1/2], [1/2, 2, 1]],
    "Экономические": [[1, 1/2], [2, 1]],
    "Экологические": [[1, 2], [1/2, 1]],
    "Автономность": [[1]],
}


def ahp_weights():
    wg, lam, CI, CR = ahp(AHP_GROUPS)
    res = {"groups": dict(zip(GROUPS, wg)), "CR_groups": CR, "lam_groups": lam, "local": {}, "CR_local": {}}
    w = {}
    for gi, gname in enumerate(GROUPS):
        codes = [c[0] for c in CRITERIA if c[1] == gname]
        wl, _, _, crl = ahp(AHP_LOCAL[gname])
        res["local"][gname] = dict(zip(codes, wl))
        res["CR_local"][gname] = crl
        for c, x in zip(codes, wl):
            w[c] = wg[gi] * x
    res["w"] = w
    return res


def entropy_weights(table):
    """Энтропийные веса по матрице значений показателей (строки — альтернативы)."""
    X = table.values.astype(float)
    lo, hi = X.min(0), X.max(0)
    Z = (X - lo) / np.where(hi > lo, hi - lo, 1) + 1e-6
    Pm = Z / Z.sum(0)
    k = 1 / math.log(len(X))
    E = -k * (Pm * np.log(Pm)).sum(0)
    dv = 1 - E
    return dict(zip(table.columns, dv / dv.sum()))


def topsis(table, w):
    """Относительная близость к идеальному решению (векторная нормализация)."""
    X = table.values.astype(float)
    signs = np.array([c[4] for c in CRITERIA])
    N = X / np.sqrt((X ** 2).sum(0))
    V = N * np.array([w[c] for c in table.columns])
    best = np.where(signs > 0, V.max(0), V.min(0))
    worst = np.where(signs > 0, V.min(0), V.max(0))
    dp = np.sqrt(((V - best) ** 2).sum(1))
    dm = np.sqrt(((V - worst) ** 2).sum(1))
    return dm / (dp + dm)
