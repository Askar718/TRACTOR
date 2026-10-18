"""Первичная обработка журналов CAN (1 Гц) полевых опытов электротрактора JINMA YL254ET.

Для каждого зачётного прохода (зона ЗД, 100 м) и каждого холостого (самопередвижение)
вычисляются средние значения каналов, энергия и производные показатели; результаты
объединяются с полевым журналом (фактическая скорость, глубина, ширина захвата).
Дополнительно формируются баланс времени и энергии по видам работ для каждой сессии.

Запуск: python3 src/process.py  (из корня репозитория)
Выход:  results/tables/passes.csv, results/tables/session_balance.csv,
        results/tables/background.csv, results/tables/sessions.csv
"""
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
CAN = ROOT / "data" / "can"
OUT = ROOT / "results" / "tables"

SESSIONS = {
    "C": ("cultivator_2026-09-15", "культиватор", "2026-09-15"),
    "T1": ("tiller_2026-10-14_session1", "фреза", "2026-10-14"),
    "T2": ("tiller_2026-10-15_session2", "фреза", "2026-10-15"),
}
L_ZD = 100.0  # длина зачётной делянки, м
DT = 1.0      # шаг журнала, с

MEAN_COLS = [
    "power_kW", "bms_current_A", "bms_voltage_V", "m1_current_A", "m2_current_A",
    "m2_rpm", "m1_rpm", "v_wheel_kmh", "pto_rpm", "cell_delta_mV",
    "m2_motor_temp_C", "m2_ctrl_temp_C", "bms_temp_max_C", "bms_cell_min_mV",
]


def load(key):
    stem = SESSIONS[key][0]
    log = pd.read_csv(CAN / f"YL254ET_{stem}_log_1Hz.csv")
    field = pd.read_csv(CAN / f"YL254ET_{stem}_field.csv")
    events = pd.read_csv(CAN / f"YL254ET_{stem}_events.csv")
    return log, field, events


def run_name(phase):
    """Название заезда без указания этапа: «проход 7», «самопередвижение 2»."""
    return str(phase).split(":")[0].strip()


def pass_stats(log, key):
    rows = []
    zd = log[(log["zone"] == "ЗД")]
    for phase, g in zd.groupby("phase", sort=False):
        if not ("рабочий ход" in phase or "зачётный ход" in phase or "попытка" in phase):
            continue
        r = {"session": key, "implement": SESSIONS[key][1], "date": SESSIONS[key][2],
             "run_key": run_name(phase), "phase": phase,
             "limit_attempt": "попытка" in phase, "n_s": len(g)}
        for c in MEAN_COLS:
            r[c] = g[c].mean()
        r["power_max_kW"] = g["power_kW"].max()
        r["power_sd_kW"] = g["power_kW"].std()
        r["m2_current_max_A"] = g["m2_current_A"].max()
        r["bms_current_max_A"] = g["bms_current_A"].max()
        r["cell_delta_max_mV"] = g["cell_delta_mV"].max()
        r["pto_rpm_min"] = g["pto_rpm"].min()
        r["E_ZD_kWh"] = g["power_kW"].sum() * DT / 3600.0
        r["Ah_ZD"] = g["bms_current_A"].sum() * DT / 3600.0
        rows.append(r)
    return pd.DataFrame(rows)


def merge_field(st, field):
    f = field.copy()
    f["run_key"] = f["run"].map(run_name)
    f = f.drop(columns=["run"])
    m = st.merge(f, on="run_key", how="left")
    m["kind"] = np.where(m["run_key"].str.startswith("самопередвижение"), "холостой", "рабочий")
    return m


def derived(df):
    d = df.copy()
    # фактическая скорость по времени прохождения делянки (для прерванных проходов — по журналу)
    # прерванные (предельные) проходы делянку не завершили: скорость и производные не определяются
    d.loc[d["limit_attempt"], ["v_fact_kmh", "B_meas_m"]] = np.nan
    d["v_ms"] = d["v_fact_kmh"] / 3.6
    # буксование: отношение пути, пройденного колесом, к фактическому пути
    d["slip"] = 1.0 - d["v_fact_kmh"] / d["v_wheel_kmh"]
    # производительность за час основного времени, га/ч: W = 0,1·B·v
    B = d["B_meas_m"].fillna(np.nan)
    d["W_ha_h"] = 0.1 * B * d["v_fact_kmh"]
    # удельный расход энергии из батареи, кВт·ч/га
    d["e_kWh_ha"] = d["power_kW"] / d["W_ha_h"]
    # удельный расход на единицу объёма обработанной почвы, кДж/м³ (= кВт / (м³/с))
    d["q_m3_s"] = B * d["a_meas_mean_m"] * d["v_ms"]
    d["e_kJ_m3"] = d["power_kW"] / d["q_m3_s"]
    d["cv_depth_pct"] = 100 * d["a_meas_sd_m"] / d["a_meas_mean_m"]
    return d


def session_balance(log, key):
    g = log.groupby("stype")
    bal = pd.DataFrame({
        "t_s": g.size() * DT,
        "E_kWh": g["power_kW"].sum() * DT / 3600.0,
        "P_mean_kW": g["power_kW"].mean(),
    })
    bal["session"] = key
    return bal.reset_index()


def background(log, key):
    """Фоновые режимы: стоянка с готовой системой, гидравлика, холостое вращение ротора, переезд, разворот."""
    pats = {
        "стоянка (готовность, насос гидравлики на холостом ходу)": log["phase"].str.contains("замеры фона|подготовка к зачётным|проверка нуля"),
        "работа гидронавески": log["phase"].str.contains("проверка гидронавески|выглубление"),
        "холостое вращение ротора фрезы (ВОМ 540)": log["phase"].str.contains("холостое вращение ротора"),
        "транспортный переезд (передача H)": log["phase"].str.contains("переезд"),
        "разворот на поворотной полосе": log["phase"].str.contains("разворот"),
    }
    rows = []
    for name, mask in pats.items():
        g = log[mask & log["power_kW"].notna()]
        if len(g) == 0:
            continue
        rows.append({"session": key, "regime": name, "t_s": len(g),
                     "P_mean_kW": g["power_kW"].mean(), "P_sd_kW": g["power_kW"].std(),
                     "m1_current_A": g["m1_current_A"].mean(), "m2_current_A": g["m2_current_A"].mean(),
                     "v_wheel_kmh": g["v_wheel_kmh"].mean(), "pto_rpm": g["pto_rpm"].mean()})
    return pd.DataFrame(rows)


def turns(log, key):
    """Длительность и энергия разворотов (этап «разворот» каждого прохода)."""
    t = log[log["phase"].str.contains("разворот", na=False)]
    g = t.groupby("phase")
    return pd.DataFrame({"session": key, "t_s": g.size() * DT,
                         "E_kWh": g["power_kW"].sum() * DT / 3600.0}).reset_index()


def session_summary(log, key):
    v = log[log["bms_soc_pct"].notna()]
    soc0, soc1 = v["bms_soc_pct"].iloc[0], v["bms_soc_pct"].iloc[-1]
    E = v["power_kW"].clip(lower=None).sum() * DT / 3600.0
    Ah = v["bms_current_A"].sum() * DT / 3600.0
    return {
        "session": key, "implement": SESSIONS[key][1], "date": SESSIONS[key][2],
        "duration_h": len(log) * DT / 3600.0,
        "soc_start": soc0, "soc_end": soc1, "dSOC": soc0 - soc1,
        "E_out_kWh": E, "Ah_out": Ah,
        "C_est_Ah": Ah / (soc0 - soc1) * 100.0,
        "E_full_est_kWh": E / (soc0 - soc1) * 100.0,
        "U_start_V": v["bms_voltage_V"].iloc[0], "U_min_V": v["bms_voltage_V"].min(),
        "cell_min_mV": v["bms_cell_min_mV"].min(),
        "cell_delta_max_mV": v["cell_delta_mV"].max(),
        "T_bat_start_C": v["bms_temp_max_C"].iloc[0], "T_bat_max_C": v["bms_temp_max_C"].max(),
        "T_m2_motor_max_C": v["m2_motor_temp_C"].max(), "T_m2_ctrl_max_C": v["m2_ctrl_temp_C"].max(),
        "T_m1_motor_max_C": v["m1_motor_temp_C"].max(),
        "I_bat_max_A": v["bms_current_A"].max(), "P_max_kW": v["power_kW"].max(),
        "I_m2_max_A": v["m2_current_A"].max(),
        "faults": int((v["bms_fault_level"] > 0).sum() + (v["m1_err"] > 0).sum() + (v["m2_err"] > 0).sum()),
    }


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    passes, bal, bg, ses, trn = [], [], [], [], []
    for key in SESSIONS:
        log, field, _ = load(key)
        st = pass_stats(log, key)
        passes.append(derived(merge_field(st, field)))
        bal.append(session_balance(log, key))
        bg.append(background(log, key))
        ses.append(session_summary(log, key))
        trn.append(turns(log, key))
    pd.concat(trn).to_csv(OUT / "turns.csv", index=False, encoding="utf-8-sig")
    passes = pd.concat(passes, ignore_index=True)
    passes.to_csv(OUT / "passes.csv", index=False, encoding="utf-8-sig")
    pd.concat(bal).to_csv(OUT / "session_balance.csv", index=False, encoding="utf-8-sig")
    pd.concat(bg).to_csv(OUT / "background.csv", index=False, encoding="utf-8-sig")
    pd.DataFrame(ses).to_csv(OUT / "sessions.csv", index=False, encoding="utf-8-sig")
    print(passes.groupby(["implement", "kind"]).size())


if __name__ == "__main__":
    main()
