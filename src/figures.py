"""Построение графиков отчёта (PNG, 200 dpi) по таблицам results/tables.

Запуск: python3 src/figures.py (после src/analysis.py)
"""
import json
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from matplotlib.colors import LinearSegmentedColormap, TwoSlopeNorm
from matplotlib.patches import FancyBboxPatch
from matplotlib.ticker import FuncFormatter

from models import CRITERIA, slip_curve, B_NOM
from params import P

ROOT = Path(__file__).resolve().parents[1]
T = ROOT / "results" / "tables"
F = ROOT / "results" / "fig"
CAN = ROOT / "data" / "can"
S = json.loads((ROOT / "results" / "summary.json").read_text())

# --- палитра (эталонная палитра навыка dataviz) и стиль
C_ET, C_D, C_3 = "#2a78d6", "#eb6834", "#1baf7a"
BLUES = ["#86b6ef", "#2a78d6", "#104281"]      # порядковая шкала (глубина)
ORANGES = ["#f4a582", "#eb6834", "#a8401a"]
GRID, INK, INK2 = "#d9d8d4", "#0b0b0b", "#52514e"
DIV = LinearSegmentedColormap.from_list("div", ["#c0392b", "#e88e7f", "#f0efec", "#86b6ef", "#1c5cab"])
CM = 1 / 2.54
W = 16.5 * CM

plt.rcParams.update({
    "font.family": "Liberation Serif", "font.size": 10, "axes.titlesize": 10, "axes.labelsize": 10,
    "legend.fontsize": 9, "xtick.labelsize": 9, "ytick.labelsize": 9, "axes.edgecolor": INK2,
    "axes.linewidth": 0.6, "axes.grid": True, "grid.color": GRID, "grid.linewidth": 0.5,
    "axes.spines.top": False, "axes.spines.right": False, "lines.linewidth": 1.6,
    "legend.frameon": False, "mathtext.fontset": "stix", "savefig.dpi": 200, "savefig.bbox": "tight", "axes.axisbelow": True,
})
comma = FuncFormatter(lambda x, _: (f"{x:g}").replace(".", ","))


def fmt(ax):
    ax.xaxis.set_major_formatter(comma)
    ax.yaxis.set_major_formatter(comma)


def save(fig, name):
    F.mkdir(parents=True, exist_ok=True)
    fig.savefig(F / f"{name}.png")
    plt.close(fig)


def num(x, d=2):
    return f"{x:.{d}f}".replace(".", ",")


def log(stem):
    return pd.read_csv(CAN / f"YL254ET_{stem}_log_1Hz.csv")


# ============================================================ схемы методики
def box(ax, x, y, w, h, text, fc="#f0efec", ec=INK2, fs=9, bold=False):
    ax.add_patch(FancyBboxPatch((x, y), w, h, boxstyle="round,pad=0.01,rounding_size=0.015",
                                fc=fc, ec=ec, lw=0.8))
    ax.text(x + w / 2, y + h / 2, text, ha="center", va="center", fontsize=fs, wrap=True,
            fontweight="bold" if bold else "normal")


def arrow(ax, x1, y1, x2, y2):
    ax.annotate("", (x2, y2), (x1, y1), arrowprops=dict(arrowstyle="-|>", color=INK2, lw=0.8))


def fig_method():
    fig, ax = plt.subplots(figsize=(W, 13 * CM))
    ax.set_xlim(0, 1); ax.set_ylim(0, 1); ax.axis("off")
    rows = [
        (0.88, ["Полевой опыт ЭТ\n(CAN 1 Гц, журнал событий,\nполевой журнал)", "Условия испытаний\n(твёрдость, влажность\nпочвы, погода)", "Паспортные данные\nЭТ и дизельного аналога"]),
        (0.70, ["Первичная обработка:\nзачётные участки, P, E,\nv, δ, W, e", "Статистика опыта:\nдисперсионный анализ,\nрегрессия, неопределённость", "Физические модели:\nR(a,v), δ(φн), A(a,v),\nтепловая модель"]),
        (0.52, ["Перенос нагрузки\nна дизельный аналог:\nмасса, буксование, расход\nтоплива ASABE D497.7", "Эксплуатационная модель\nсмены: развороты, зарядка,\nпереезды, автономность", "Экономическая модель\n(ГОСТ 34393-2018):\nпрямые и совокупные затраты"]),
        (0.34, ["Система из 10 показателей\nв 5 группах", "Нормирование:\nсимметричное относительное\nпреимущество $d_i \\in [-1;\\,1]$", "Весовые коэффициенты:\nМАИ (Саати) + энтропийный\nметод, α = 0,5"]),
        (0.16, ["Интегральный индекс\nI = Σ wᵢ·dᵢ;\nконтроль методом TOPSIS", "Анализ устойчивости:\nМонте-Карло (параметры\nи веса), P(I > 0)", "Зоны оптимального\nиспользования: технологическая,\nорганизационная, экономическая"]),
    ]
    xs = [0.02, 0.355, 0.69]
    for y, texts in rows:
        for x, t in zip(xs, texts):
            box(ax, x, y - 0.065, 0.29, 0.13, t, fs=8)
    for (y1, _), (y2, _) in zip(rows[:-1], rows[1:]):
        for x in xs:
            arrow(ax, x + 0.145, y1 - 0.066, x + 0.145, y2 + 0.066)
    ax.text(0.5, 0.02, "Результат: вывод о преимуществе ЭТ или Д для каждого сочетания «операция — режим — организация работ — экономические условия»",
            ha="center", fontsize=8.5, color=INK2)
    save(fig, "f01_method")


def fig_hierarchy():
    w = pd.read_csv(T / "weights.csv")
    fig, ax = plt.subplots(figsize=(W, 12 * CM))
    ax.set_xlim(0, 1); ax.set_ylim(0, 1); ax.axis("off")
    box(ax, 0.0, 0.38, 0.17, 0.24, "Цель:\nсравнительная\nоценка ЭТ и\nдизельного\nтрактора того\nже класса", fc="#cde2fb", bold=True, fs=8.5)
    groups = list(dict.fromkeys(w["group"]))
    ahp = S["ahp"]["groups"]
    n_tot = len(w)
    hrow = 0.94 / n_tot
    y = 0.97
    for g in groups:
        sub = w[w["group"] == g]
        hg = hrow * len(sub)
        yg = y - hg
        box(ax, 0.22, yg + 0.006, 0.2, hg - 0.012, f"{g}\nw = {num(ahp[g], 3)}", fc="#e8e7e3", fs=8.5)
        arrow(ax, 0.17, 0.5, 0.22, yg + hg / 2)
        for j, (_, r) in enumerate(sub.iterrows()):
            yi = y - (j + 1) * hrow
            box(ax, 0.46, yi + 0.008, 0.54, hrow - 0.016, f"{r['code']}. {r['name']}, {r['unit']}", fc="#fcfcfb", fs=7.6)
            arrow(ax, 0.42, yg + hg / 2, 0.46, yi + hrow / 2)
        y = yg
    save(fig, "f02_hierarchy")


# ============================================================ опытные данные
def shade_phases(ax, d):
    cols = {"рабочий ход": "#cde2fb", "разворот": "#fde2d3", "переезд": "#e8e7e3", "ВОМ": "#d4f1e6"}
    st = d["stype"].values
    t = d["t_s"].values
    i = 0
    while i < len(st):
        j = i
        while j < len(st) and st[j] == st[i]:
            j += 1
        if st[i] in cols:
            ax.axvspan(t[i] / 60, t[j - 1] / 60, color=cols[st[i]], lw=0)
        i = j


def fig_session():
    d = log("cultivator_2026-09-15")
    fig, (a1, a2) = plt.subplots(2, 1, figsize=(W, 11 * CM), sharex=True, gridspec_kw={"height_ratios": [2, 1]})
    shade_phases(a1, d)
    a1.plot(d["t_s"] / 60, d["power_kW"], color=C_ET, lw=0.6)
    a1.set_ylabel("Мощность P, кВт")
    a2.plot(d["t_s"] / 60, d["bms_soc_pct"], color=INK, lw=1.2)
    a2.set_ylabel("SOC, %")
    a2.set_xlabel("Время от начала записи, мин")
    from matplotlib.patches import Patch
    a1.legend(handles=[Patch(color="#cde2fb", label="рабочий ход"), Patch(color="#fde2d3", label="разворот"),
                       Patch(color="#e8e7e3", label="переезд")], loc="upper right", ncol=3)
    for a in (a1, a2):
        fmt(a)
    save(fig, "f03_session_cult")


def pass_window(stem, n):
    d = log(stem)
    m = d["phase"].str.match(rf"проход {n}:") | d["phase"].str.contains(rf"проход {n}: ")
    idx = d.index[m]
    return d.loc[idx.min() - 5: idx.max() + 5]


def fig_pass(stem, n, name, pto=False):
    d = pass_window(stem, n)
    d = d[d["phase"].str.contains(f"проход {n}:")]
    t = d["t_s"] - d["t_s"].iloc[0]
    fig, axs = plt.subplots(3, 1, figsize=(W, 13 * CM), sharex=True)
    for a in axs:
        for z, c in (("РУ", "#f0efec"), ("ЗД", "#cde2fb"), ("УВ", "#f0efec")):
            tz = t[d["zone"] == z]
            if len(tz):
                a.axvspan(tz.min(), tz.max(), color=c, lw=0)
    axs[0].plot(t, d["power_kW"], color=C_ET)
    axs[0].set_ylabel("P, кВт")
    axs[1].plot(t, d["m2_current_A"], color=C_ET)
    axs[1].set_ylabel("Ток двигателя\nхода, А")
    if pto:
        axs[2].plot(t, d["pto_rpm"], color=C_3)
        axs[2].set_ylabel("Частота ВОМ,\nмин$^{-1}$")
    else:
        axs[2].plot(t, d["v_wheel_kmh"], color=C_3)
        axs[2].set_ylabel("Теоретическая\nскорость, км/ч")
    axs[2].set_xlabel("Время от начала этапа, с")
    ph = d["phase"].values
    for a in axs:
        fmt(a)
    zd = t[d["zone"] == "ЗД"]
    axs[0].text(zd.mean(), axs[0].get_ylim()[1] * 0.95, "зачётная делянка (ЗД)", ha="center", va="top", fontsize=8.5, color=INK2)
    save(fig, name)


def fig_limit():
    fig, axs = plt.subplots(1, 2, figsize=(W, 7 * CM))
    for a, stem, n, lab, col, ylab in (
            (axs[0], "cultivator_2026-09-15", 25, "культиватор: a = 0,14 м, v = 5,4 км/ч", "v_wheel_kmh", "Теоретическая скорость, км/ч"),
            (axs[1], "tiller_2026-10-14_session1", 17, "фреза: a = 0,16 м, v = 3,6 км/ч", "pto_rpm", "Частота ВОМ, мин$^{-1}$")):
        d = log(stem)
        d = d[d["phase"].str.contains(f"проход {n}: попытка")]
        t = d["t_s"] - d["t_s"].iloc[0]
        a.plot(t, d["power_kW"], color=C_ET, label="P, кВт")
        a.axhline(P["P_el_lim"], color=INK2, ls="--", lw=0.8)
        a.text(0.5, P["P_el_lim"] + 0.3, "предел 17,5 кВт", fontsize=8, color=INK2)
        b = a.twinx() if False else None
        a.set_title(lab)
        a.set_xlabel("Время, с")
        a.set_ylabel("P, кВт")
        fmt(a)
        a.set_ylim(0, 20)
        ins = a.inset_axes([0.45, 0.08, 0.5, 0.35])
        ins.plot(t, d[col], color=C_3, lw=1)
        ins.set_title(ylab, fontsize=7)
        ins.tick_params(labelsize=7)
        ins.grid(True, lw=0.3)
        ins.xaxis.set_major_formatter(comma); ins.yaxis.set_major_formatter(comma)
    save(fig, "f06_limit")


def fig_power_vs_v():
    reg = pd.read_csv(T / "regimes_measured.csv")
    val = pd.read_csv(T / "compare_S1.csv")
    fig, axs = plt.subplots(1, 2, figsize=(W, 7.5 * CM))
    from models import power_point
    from analysis import base_params
    p, _ = base_params()
    import models
    ps = pd.read_csv(T / "passes.csv")
    m = models.fit_models(ps, p)
    for a, impl, vr in ((axs[0], "культиватор", (3.4, 5.6)), (axs[1], "фреза", (1.6, 3.8))):
        r = reg[reg["implement"] == impl]
        for i, (ad, g) in enumerate(r.groupby("a_plan")):
            a.errorbar(g["v_mean"], g["P_mean"], yerr=g["P_ci"], fmt="o", ms=5, color=BLUES[i], capsize=3,
                       label=f"a = {num(ad)} м")
            vv = np.linspace(*vr, 50)
            a.plot(vv, [power_point(impl, ad, x, p, m)["P_el"] for x in vv], color=BLUES[i], lw=1)
        a.axhline(P["P_el_lim"], color="#d03b3b", ls="--", lw=0.8)
        a.text(vr[0], P["P_el_lim"] - 0.9, "предельная мощность 17,5 кВт", fontsize=8, color="#d03b3b")
        a.set_title(impl.capitalize())
        a.set_xlabel("Фактическая скорость v, км/ч")
        a.set_ylabel("Мощность от батареи P, кВт")
        a.set_ylim(5, 19)
        a.legend(loc="upper left")
        fmt(a)
    save(fig, "f07_power_v")


def fig_energy_ha():
    reg = pd.read_csv(T / "regimes_measured.csv")
    fig, axs = plt.subplots(1, 2, figsize=(W, 7.5 * CM))
    for a, impl in zip(axs, ("культиватор", "фреза")):
        r = reg[reg["implement"] == impl]
        vs = sorted(r["v_plan"].unique())
        for i, (v, g) in enumerate(r.groupby("v_plan")):
            a.errorbar(g["a_mean"] * 100, g["e_mean"], yerr=g["e_ci"], fmt="-o", ms=5, color=ORANGES[i], capsize=3,
                       label=f"v = {num(v, 1)} км/ч")
        a.set_title(impl.capitalize())
        a.set_xlabel("Глубина обработки a, см")
        a.set_ylabel("Удельный расход энергии e, кВт·ч/га")
        a.legend()
        fmt(a)
    save(fig, "f08_energy_ha")


def fig_traction():
    c = pd.read_csv(T / "cult_traction.csv")
    m = S["models"]
    fig, axs = plt.subplots(1, 2, figsize=(W, 7.5 * CM))
    a = axs[0]
    v2 = (c["v_fact_kmh"] / 3.6) ** 2
    for i, (ad, g) in enumerate(c.groupby("a_plan_m")):
        a.plot((g["v_fact_kmh"] / 3.6) ** 2, g["k_Nm2"] / 1e3, "o", color=BLUES[i], ms=5, label=f"a = {num(ad)} м")
    xx = np.linspace(0.8, 2.4, 20)
    a.plot(xx, (m["k0"] + m["eps"] * xx) / 1e3, color=INK, lw=1, label="k = k₀ + ε·v²")
    a.set_xlabel("v², м²/с²")
    a.set_ylabel("Удельное сопротивление k, кН/м²")
    a.legend(fontsize=8)
    fmt(a)
    a = axs[1]
    a.plot(c["phi_n"], 100 * c["slip"], "o", color=C_ET, ms=5, label="опыт (ЭТ, 1300 кг)")
    ph = np.linspace(0, 0.55, 100)
    a.plot(ph, 100 * slip_curve(ph, m["phi_max"], m["k_slip"], m["d0"]), color=INK, lw=1, label="аппроксимация")
    phD = c["R_N"] / (P["m_D"] * P["g"])
    a.plot(phD, 100 * slip_curve(phD, m["phi_max"], m["k_slip"], m["d0"]), "s", mfc="none", color=C_D, ms=5,
           label="расчёт для Д (1140 кг)")
    a.axhline(100 * P["slip_max"], color="#d03b3b", ls="--", lw=0.8)
    a.text(0.01, 100 * P["slip_max"] + 0.4, "δ доп = 18 %", fontsize=8, color="#d03b3b")
    a.set_xlabel("Коэффициент использования веса φн = R/G")
    a.set_ylabel("Буксование δ, %")
    a.legend(fontsize=8, loc="upper left")
    fmt(a)
    save(fig, "f09_traction")


def fig_tiller_A():
    t = pd.read_csv(T / "till_rotor.csv")
    m = S["models"]
    fig, ax = plt.subplots(figsize=(W * 0.62, 7.5 * CM))
    for i, (ad, g) in enumerate(t.groupby("a_plan_m")):
        ax.plot(g["v_fact_kmh"], g["A_kJm3"], "o", color=BLUES[i], ms=5, label=f"a = {num(ad)} м")
        vv = np.linspace(1.7, 3.7, 10)
        ax.plot(vv, m["A0"] + m["A1"] * vv + m["A2"] * ad, color=BLUES[i], lw=1)
    ax.set_xlabel("Скорость v, км/ч")
    ax.set_ylabel("Удельная энергия фрезерования\nA, кДж/м³ (от батареи)")
    ax.legend()
    fmt(ax)
    save(fig, "f10_tiller_A")


def fig_validation():
    v = pd.read_csv(T / "model_validation.csv")
    fig, ax = plt.subplots(figsize=(W * 0.55, 7.5 * CM))
    for impl, c, mk in (("культиватор", C_ET, "o"), ("фреза", C_3, "s")):
        g = v[v["implement"] == impl]
        ax.plot(g["P_meas"], g["P_model"], mk, color=c, ms=6, label=impl)
    ax.plot([6, 18], [6, 18], color=INK2, lw=0.8)
    ax.set_xlabel("Измеренная мощность, кВт")
    ax.set_ylabel("Расчётная мощность, кВт")
    ax.legend()
    fmt(ax)
    save(fig, "f11_validation")


def fig_balance():
    b = pd.read_csv(T / "session_balance.csv")
    order = ["рабочий ход", "разворот", "переезд", "гидропривод", "ВОМ", "замеры", "стоянка"]
    cols = [C_ET, C_D, "#8a8984", C_3, "#eda100", "#c3c2b7", "#e8e7e3"]
    fig, axs = plt.subplots(1, 2, figsize=(W, 7 * CM))
    names = {"C": "Культиватор\n15.09", "T1": "Фреза\n14.10", "T2": "Фреза\n15.10"}
    for a, col, lab in ((axs[0], "E_kWh", "Энергия, кВт·ч"), (axs[1], "t_s", "Время, ч")):
        bottom = np.zeros(3)
        for st, c in zip(order, cols):
            vals = np.array([b[(b.session == s) & (b.stype == st)][col].sum() for s in names])
            if col == "t_s":
                vals = vals / 3600
            a.bar(list(names.values()), vals, bottom=bottom, color=c, label=st, width=0.55, edgecolor="white", lw=1)
            bottom += vals
        a.set_ylabel(lab)
        fmt(a)
        a.xaxis.set_major_formatter(plt.NullFormatter()) if False else None
    axs[1].legend(bbox_to_anchor=(1.02, 1), loc="upper left", fontsize=8)
    save(fig, "f12_balance")


def fig_soc_capacity():
    fig, ax = plt.subplots(figsize=(W * 0.6, 7.5 * CM))
    for (stem, lab), c in zip((("cultivator_2026-09-15", "15.09"), ("tiller_2026-10-14_session1", "14.10"),
                               ("tiller_2026-10-15_session2", "15.10")), (C_ET, C_D, C_3)):
        d = log(stem)
        d = d[d["bms_soc_pct"].notna()]
        ah = d["bms_current_A"].cumsum() / 3600
        ax.plot(ah, d["bms_soc_pct"], color=c, lw=1.2, label=lab)
    xx = np.linspace(0, 170, 10)
    ax.plot(xx, 98 - xx / P["C_bat_Ah"] * 100, color=INK, ls="--", lw=0.8, label="расчёт при C = 304 А·ч")
    ax.set_xlabel("Отданный заряд Q, А·ч")
    ax.set_ylabel("SOC по данным BMS, %")
    ax.legend()
    fmt(ax)
    save(fig, "f13_soc_capacity")


def fig_cells():
    d = pd.concat([log(s) for s in ("cultivator_2026-09-15", "tiller_2026-10-14_session1", "tiller_2026-10-15_session2")])
    d = d[d["bms_current_A"].notna()]
    fig, axs = plt.subplots(1, 2, figsize=(W, 7.5 * CM))
    a = axs[0]
    a.plot(d["bms_current_A"], d["cell_delta_mV"], ".", ms=1.5, color=C_ET, alpha=0.3)
    a.set_xlabel("Ток батареи I, А")
    a.set_ylabel("Разбаланс ячеек ΔU, мВ")
    fmt(a)
    a = axs[1]
    a.plot(d["bms_soc_pct"], d["bms_cell_min_mV"], ".", ms=1.5, color=C_D, alpha=0.3)
    a.set_xlabel("SOC, %")
    a.set_ylabel("Минимальное напряжение ячейки, мВ")
    fmt(a)
    save(fig, "f14_cells")


def fig_thermal():
    fig, axs = plt.subplots(1, 2, figsize=(W, 7.5 * CM), gridspec_kw={"width_ratios": [1.6, 1]})
    d = pd.read_csv(T / "thermal_T1.csv")
    a = axs[0]
    a.plot(d["t_s"] / 60, d["T_meas"], color=C_ET, lw=1.2, label="измерение")
    a.plot(d["t_s"] / 60, d["T_model"], color=INK, ls="--", lw=1, label="модель")
    a.set_xlabel("Время, мин")
    a.set_ylabel("Температура двигателя хода, °C")
    a.legend()
    fmt(a)
    th = pd.read_csv(T / "thermal_fit.csv")
    R = th["R_K_per_kW"].mean()
    a = axs[1]
    Pp = np.linspace(0, 17.5, 50)
    for Ta, c in ((10, BLUES[0]), (25, BLUES[1]), (40, BLUES[2])):
        a.plot(Pp, Ta + R * Pp, color=c, label=f"Tокр = {Ta} °C")
    a.axvline(P["P_mot_1h"] / P["eta_ep"] + P["P_aux"], color="#d03b3b", ls="--", lw=0.8)
    a.set_xlabel("Длительная мощность P, кВт")
    a.set_ylabel("Установившаяся\nтемпература, °C")
    a.legend(fontsize=8)
    fmt(a)
    save(fig, "f15_thermal")


def fig_depth():
    ps = pd.read_csv(T / "passes.csv")
    w = ps[(ps["kind"] == "рабочий") & ps["a_meas_mean_m"].notna() & (~ps["limit_attempt"])]
    fig, axs = plt.subplots(1, 2, figsize=(W, 7 * CM))
    for a, impl in zip(axs, ("культиватор", "фреза")):
        g = w[w["implement"] == impl]
        a.errorbar(g["a_plan_m"] * 100 + (g["v_plan_kmh"] - g["v_plan_kmh"].mean()) * 0.3, g["a_meas_mean_m"] * 100,
                   yerr=g["a_meas_sd_m"] * 100, fmt="o", ms=4, color=C_ET, capsize=2)
        lim = [6, 18]
        a.plot(lim, lim, color=INK2, lw=0.8)
        a.fill_between(lim, [x - 1 for x in lim], [x + 1 for x in lim], color="#cde2fb", lw=0, label="допуск ±1 см")
        a.set_title(impl.capitalize())
        a.set_xlabel("Заданная глубина, см")
        a.set_ylabel("Фактическая глубина, см")
        a.legend(loc="upper left")
        fmt(a)
    save(fig, "f16_depth")


# ============================================================ сравнение
def fig_diesel_model():
    c = pd.read_csv(T / "compare_S1.csv")
    Pn = P["k_pto_D"] * P["P_e_nom_D"]
    X = np.linspace(0.1, 1.0, 100)
    fig, axs = plt.subplots(1, 2, figsize=(W, 7.5 * CM))
    a = axs[0]
    a.plot(X * Pn, P["sfc_a"] * X * Pn + P["sfc_b"] * Pn, color=C_D, label="Q = 0,22·P + 0,096·Pном")
    for impl, mk in (("культиватор", "o"), ("фреза", "s")):
        g = c[c["implement"] == impl]
        a.plot(g["P_shaft_D"], g["Q_Lh"], mk, color=INK, mfc="none", ms=6, label=f"режимы: {impl}")
    a.set_xlabel("Мощность на входе трансмиссии P, кВт")
    a.set_ylabel("Часовой расход топлива Q, л/ч")
    a.legend(fontsize=8)
    fmt(a)
    a = axs[1]
    a.plot(X, 1000 * P["rho_D"] * (P["sfc_a"] + P["sfc_b"] / X), color=C_D)
    a.plot(c["X_D"], 1000 * P["rho_D"] * (P["sfc_a"] + P["sfc_b"] / c["X_D"]), "o", color=INK, mfc="none", ms=6)
    a.set_ylim(200, 800)
    a.set_xlabel("Загрузка X = P/Pном")
    a.set_ylabel("Удельный расход, г/(кВт·ч)")
    fmt(a)
    save(fig, "f17_diesel")


def lab_reg(r):
    return f"{num(r['a'])}×{num(r['v'], 1)}"


def fig_compare_energy():
    c = pd.read_csv(T / "compare_S1.csv")
    fig, axs = plt.subplots(2, 1, figsize=(W, 12 * CM))
    for a, (code, ylab) in zip(axs, (("I1", "Внешняя энергия, МДж/га"), ("I8", "Эмиссия CO₂, кг/га"))):
        x = np.arange(len(c))
        a.bar(x - 0.2, c[f"ET_{code}"], 0.38, color=C_ET, label="ЭТ YL254ET")
        a.bar(x + 0.2, c[f"D_{code}"], 0.38, color=C_D, label="Д JM-254 (расчёт)")
        if code == "I1":
            a.plot(x - 0.2, c["ET_I2"], "_", color=INK, ms=12, mew=1.5, label="первичная энергия ЭТ")
            a.plot(x + 0.2, c["D_I2"], "_", color=INK2, ms=12, mew=1.5, label="первичная энергия Д")
        a.set_xticks(x)
        a.set_xticklabels([("К " if r["implement"] == "культиватор" else "Ф ") + lab_reg(r) for r in c.to_dict("records")],
                          rotation=60, fontsize=7.5)
        a.set_ylabel(ylab)
        a.legend(ncol=4 if code == "I1" else 2, fontsize=7.5, loc="upper left")
        a.yaxis.set_major_formatter(comma)
    axs[1].set_xlabel("Режим: орудие (К — культиватор, Ф — фреза), глубина a, м × скорость v, км/ч")
    save(fig, "f18_cmp_energy")


def fig_costs():
    c = pd.read_csv(T / "compare_S1.csv")
    sel = [("культиватор", 0.08, 3.6), ("культиватор", 0.11, 4.5), ("фреза", 0.08, 2.7), ("фреза", 0.12, 2.7)]
    fig, ax = plt.subplots(figsize=(W, 8 * CM))
    parts = [("c_lab", "оплата труда", "#8a8984"), ("c_en", "энергия / топливо", C_3),
             ("c_rm", "ремонт и ТО", "#eda100"), ("c_cap", "капитальные затраты", "#6250d6")]
    xt, xl = [], []
    for i, (impl, a_, v_) in enumerate(sel):
        r = c[(c.implement == impl) & (c.a == a_) & (c.v == v_)].iloc[0]
        for j, mach in enumerate(("ET", "D")):
            x = i * 3 + j
            b = 0
            for k, (key, lab, col) in enumerate(parts):
                val = r[f"e_{key}_{mach}"] / 1000
                ax.bar(x, val, 0.8, bottom=b, color=col, label=lab if (i == 0 and j == 0) else None, edgecolor="white", lw=1)
                b += val
            ax.text(x, b + 0.2, num(b, 1), ha="center", fontsize=8)
            xt.append(x)
            xl.append(f"{'ЭТ' if mach == 'ET' else 'Д'}\n{'К' if impl == 'культиватор' else 'Ф'} {num(a_)}×{num(v_, 1)}")
    ax.set_xticks(xt)
    ax.set_xticklabels(xl, fontsize=8)
    ax.set_ylabel("Удельные совокупные затраты, тыс. тг/га")
    ax.legend(ncol=4, fontsize=8, loc="upper left")
    ax.yaxis.set_major_formatter(comma)
    save(fig, "f19_costs")


def fig_radar():
    fig = plt.figure(figsize=(W, 8.5 * CM))
    codes = [c[0] for c in CRITERIA]
    ang = np.linspace(0, 2 * np.pi, len(codes), endpoint=False).tolist()
    for k, sc in enumerate(("S1", "S2")):
        c = pd.read_csv(T / f"compare_{sc}.csv")
        ax = fig.add_subplot(1, 2, k + 1, projection="polar")
        for (impl, a_, v_), col in ((("культиватор", 0.11, 4.5), C_ET), (("фреза", 0.12, 2.7), C_D)):
            r = c[(c.implement == impl) & (c.a == a_) & (c.v == v_)].iloc[0]
            vals = [r[f"d_{x}"] for x in codes]
            ax.plot(ang + ang[:1], vals + vals[:1], color=col, lw=1.4, label=f"{impl} {num(a_)}×{num(v_, 1)}")
            ax.fill(ang + ang[:1], vals + vals[:1], color=col, alpha=0.08)
        ax.plot(np.linspace(0, 2 * np.pi, 100), np.zeros(100), color=INK, lw=0.8)
        ax.set_xticks(ang)
        ax.set_xticklabels(codes, fontsize=8)
        ax.set_ylim(-1, 1)
        ax.set_yticks([-1, -0.5, 0, 0.5, 1])
        ax.set_yticklabels(["−1", "−0,5", "0", "0,5", "1"], fontsize=7)
        ax.set_title("Сценарий 1: полная смена" if sc == "S1" else "Сценарий 2: задание 0,5 га/смену", fontsize=9, pad=14)
        if k == 1:
            ax.legend(loc="lower center", bbox_to_anchor=(-0.15, -0.28), ncol=2, fontsize=8)
    save(fig, "f20_radar")


def fig_weights():
    w = pd.read_csv(T / "weights.csv")
    x = np.arange(len(w))
    fig, ax = plt.subplots(figsize=(W, 7 * CM))
    ax.bar(x - 0.27, w["w_ahp"], 0.26, color=C_ET, label="МАИ (экспертные)")
    ax.bar(x, w["w_entropy"], 0.26, color=C_3, label="энтропийные")
    ax.bar(x + 0.27, w["w"], 0.26, color=INK2, label="итоговые (α = 0,5)")
    ax.set_xticks(x)
    ax.set_xticklabels(w["code"])
    ax.set_ylabel("Весовой коэффициент")
    ax.legend()
    fmt(ax)
    ax.xaxis.set_major_formatter(plt.FixedFormatter(w["code"].tolist()))
    save(fig, "f21_weights")


def fig_index():
    fig, axs = plt.subplots(1, 2, figsize=(W, 8 * CM), sharey=True)
    mc = pd.read_csv(T / "mc_raw.csv")
    for a, sc in zip(axs, ("S1", "S2")):
        g = mc[mc.scen == sc]
        keys = list(dict.fromkeys(zip(g.implement, g.a, g.v)))
        data = [g[(g.implement == k[0]) & (g.a == k[1]) & (g.v == k[2])]["I"].values for k in keys]
        bp = a.boxplot(data, orientation="horizontal", widths=0.6, patch_artist=True, showfliers=False,
                       medianprops=dict(color=INK))
        for patch, k in zip(bp["boxes"], keys):
            patch.set_facecolor(C_ET if k[0] == "культиватор" else C_3)
            patch.set_alpha(0.6)
        a.axvline(0, color="#d03b3b", lw=0.8)
        a.set_yticks(range(1, len(keys) + 1))
        a.set_yticklabels([f"{'К' if k[0] == 'культиватор' else 'Ф'} {num(k[1])}×{num(k[2], 1)}" for k in keys], fontsize=8)
        a.set_xlabel("Интегральный индекс I")
        a.set_title("Сценарий 1 (полная смена)" if sc == "S1" else "Сценарий 2 (0,5 га/смену)")
        a.xaxis.set_major_formatter(comma)
    save(fig, "f22_index_mc")


def fig_tornado():
    s = pd.read_csv(T / "sensitivity_src.csv", index_col=0)
    names = {"EF_grid": "коэффициент эмиссии сети", "PEF_el": "коэфф. первичной энергии эл.", "T_year_h": "годовая загрузка",
             "bat_usd_kWh": "стоимость батареи", "c_D": "цена ДТ", "c_el": "тариф на электроэнергию",
             "eta_bat": "КПД батареи", "eta_ch": "КПД зарядного устройства", "eta_ep": "КПД электропривода",
             "eta_tr": "КПД трансмиссии", "k_D": "поправка расхода топлива", "k_RM_ET": "доля затрат на ремонт ЭТ",
             "k_landed": "коэфф. цены поставки", "k_pto_D": "отношение Pвом/Pе", "r_disc": "ставка дисконтирования"}
    s = s.reindex(s["S2"].abs().sort_values().index)
    fig, ax = plt.subplots(figsize=(W, 9 * CM))
    y = np.arange(len(s))
    ax.barh(y - 0.2, s["S1"], 0.38, color=C_ET, label="сценарий 1")
    ax.barh(y + 0.2, s["S2"], 0.38, color=C_D, label="сценарий 2")
    ax.set_yticks(y)
    ax.set_yticklabels([names.get(i, i) for i in s.index], fontsize=8.5)
    ax.axvline(0, color=INK, lw=0.6)
    ax.set_xlabel("Стандартизованный коэффициент регрессии индекса I")
    ax.legend()
    ax.xaxis.set_major_formatter(comma)
    save(fig, "f23_tornado")


def fig_zone_tech(sc):
    z = pd.read_csv(T / "zone_tech.csv")
    reg = pd.read_csv(T / "regimes_measured.csv")
    fig, axs = plt.subplots(1, 2, figsize=(W, 8 * CM))
    for a, impl in zip(axs, ("культиватор", "фреза")):
        g = z[z.implement == impl]
        A = np.sort(g.a.unique()); V = np.sort(g.v.unique())
        piv = lambda col: g.pivot(index="a", columns="v", values=col).reindex(index=A, columns=V).values.astype(float)
        I = piv(f"I_{sc}")
        fE = piv("feas_ET"); fD = piv("feas_D"); cE = piv("cont_ET")
        Im = np.where(fE > 0.5, I, np.nan)
        lim = 0.3
        cs = a.contourf(V, A * 100, Im, levels=np.linspace(-lim, lim, 13), cmap=DIV, extend="both")
        a.contour(V, A * 100, fE, levels=[0.5], colors=[C_ET], linewidths=1.6)
        a.contour(V, A * 100, fD, levels=[0.5], colors=[C_D], linewidths=1.6, linestyles="--")
        a.contour(V, A * 100, cE, levels=[0.5], colors=[INK], linewidths=0.9, linestyles=":")
        a.contour(V, A * 100, Im, levels=[0], colors=[INK], linewidths=1.2)
        r = reg[reg.implement == impl]
        a.plot(r["v_plan"], r["a_plan"] * 100, "k+", ms=7)
        a.set_title(impl.capitalize())
        a.set_xlabel("Скорость v, км/ч")
        a.set_ylabel("Глубина a, см")
        fmt(a)
        a.grid(False)
    cb = fig.colorbar(cs, ax=axs, shrink=0.9, pad=0.02)
    cb.set_label("Индекс I (> 0 — преимущество ЭТ)")
    cb.formatter = comma; cb.update_ticks()
    from matplotlib.lines import Line2D
    fig.legend(handles=[Line2D([], [], color=C_ET, lw=1.6, label="граница области ЭТ"),
                           Line2D([], [], color=C_D, lw=1.6, ls="--", label="граница области Д"),
                           Line2D([], [], color=INK, lw=0.9, ls=":", label="длительный режим ЭТ"),
                           Line2D([], [], color=INK, lw=1.2, label="I = 0"),
                           Line2D([], [], color="k", marker="+", lw=0, label="опытные режимы")],
               loc="lower center", bbox_to_anchor=(0.45, -0.1), ncol=3, fontsize=8)
    save(fig, f"f24_zone_tech_{sc}")


def fig_zone_org():
    z = pd.read_csv(T / "zone_org.csv")
    fig, axs = plt.subplots(1, 2, figsize=(W, 8 * CM))
    for a, impl in zip(axs, ("культиватор", "фреза")):
        g = z[z.implement == impl]
        Sx = np.sort(g.S_task.unique()); L = np.sort(g.l_km.unique())
        I = g.pivot(index="l_km", columns="S_task", values="I").reindex(index=L, columns=Sx).values
        cs = a.contourf(Sx, L, I, levels=np.linspace(-0.3, 0.3, 13), cmap=DIV, extend="both")
        a.contour(Sx, L, I, levels=[0], colors=[INK], linewidths=1.4)
        Ac = g.groupby("l_km")["A_charge"].mean()
        a.plot(Ac.values, Ac.index, color=INK, ls=":", lw=1)
        a.set_title(impl.capitalize() + (" (0,11 м × 4,5 км/ч)" if impl == "культиватор" else " (0,12 м × 2,7 км/ч)"), fontsize=9)
        a.set_xlabel("Сменное задание S, га/смену")
        a.set_ylabel("Удалённость от места зарядки l, км")
        fmt(a)
        a.grid(False)
    cb = fig.colorbar(cs, ax=axs, shrink=0.9, pad=0.02)
    cb.set_label("Индекс I")
    cb.formatter = comma; cb.update_ticks()
    save(fig, "f25_zone_org")


def fig_zone_econ():
    z = pd.read_csv(T / "zone_econ.csv")
    fig, axs = plt.subplots(1, 2, figsize=(W, 8 * CM))
    for a, impl in zip(axs, ("культиватор", "фреза")):
        g = z[z.implement == impl]
        X = np.sort(g.T_year.unique()); Y = np.sort(g.c_D.unique())
        dC = g.pivot(index="c_D", columns="T_year", values="dC_tot").reindex(index=Y, columns=X).values / 1000
        lim = np.nanmax(np.abs(dC))
        cs = a.contourf(X, Y, -dC, levels=np.linspace(-6, 6, 13), cmap=DIV, extend="both")
        a.contour(X, Y, dC, levels=[0], colors=[INK], linewidths=1.4)
        a.plot(P["T_year_h"], P["c_D"], "k*", ms=10)
        a.annotate("октябрь 2026 г.", (P["T_year_h"], P["c_D"]), (P["T_year_h"] + 80, P["c_D"] - 40), fontsize=8)
        a.set_title(impl.capitalize())
        a.set_xlabel("Годовая загрузка, ч")
        a.set_ylabel("Цена ДТ, тг/л")
        fmt(a)
        a.grid(False)
    cb = fig.colorbar(cs, ax=axs, shrink=0.9, pad=0.02)
    cb.set_label("Экономия совокупных затрат ЭТ, тыс. тг/га")
    cb.formatter = comma; cb.update_ticks()
    save(fig, "f26_zone_econ")


def fig_autonomy():
    c = pd.read_csv(T / "compare_S1.csv")
    fig, axs = plt.subplots(1, 2, figsize=(W, 7.5 * CM))
    x = np.arange(len(c))
    labels = [f"{'К' if i == 'культиватор' else 'Ф'} {num(a_)}×{num(v_, 1)}" for i, a_, v_ in zip(c.implement, c.a, c.v)]
    A_ch = c["s_t_auton_ET"] / c["s_t_ha"]
    axs[0].bar(x, A_ch, color=C_ET)
    axs[0].set_ylabel("Площадь на одной зарядке, га")
    axs[1].bar(x - 0.2, c["s_S_shift_ET"], 0.38, color=C_ET, label="ЭТ (с подзарядкой)")
    axs[1].bar(x + 0.2, c["s_S_shift_D"], 0.38, color=C_D, label="Д")
    axs[1].set_ylabel("Сменная выработка, га")
    axs[1].legend(fontsize=8)
    for a in axs:
        a.set_xticks(x)
        a.set_xticklabels(labels, rotation=70, fontsize=7)
        a.yaxis.set_major_formatter(comma)
    save(fig, "f27_autonomy")


def main():
    for f in (fig_method, fig_hierarchy, fig_session, fig_limit, fig_power_vs_v, fig_energy_ha, fig_traction,
              fig_tiller_A, fig_validation, fig_balance, fig_soc_capacity, fig_cells, fig_thermal, fig_depth,
              fig_diesel_model, fig_compare_energy, fig_costs, fig_radar, fig_weights, fig_index, fig_tornado,
              fig_zone_org, fig_zone_econ, fig_autonomy):
        f()
    fig_pass("cultivator_2026-09-15", 4, "f04_pass_cult")
    fig_pass("tiller_2026-10-14_session1", 1, "f05_pass_till", pto=True)
    fig_zone_tech("S1")
    fig_zone_tech("S2")
    print(sorted(p.name for p in F.glob("*.png")))


if __name__ == "__main__":
    main()
