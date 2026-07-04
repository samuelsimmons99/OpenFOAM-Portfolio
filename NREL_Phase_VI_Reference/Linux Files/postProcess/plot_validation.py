"""
Plot CFD shaft torque vs experimental data (NREL Phase VI).

Experimental data: Hand et al., NREL/TP-500-29494, 2001 (S-sequence, 3° pitch).
Published CFD reference: Song & Perot (2015), Figure 11.
"""

import os
import csv
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

# ---------------------------------------------------------------------------
# Hand et al. NREL/TP-500-29494 — S-sequence (0° yaw, 3° tip pitch, 72 rpm)
# ---------------------------------------------------------------------------
EXP_V = np.array([5,    7,    10,   13,   15,   18,   21])
EXP_T = np.array([130,  420,  1490, 1620, 1490, 1400, 1370])
EXP_P = EXP_T * 7.5398 / 1000

# ---------------------------------------------------------------------------
# Song & Perot (2015) Figure 11 — digitised from published figure
# Note: different pitch/sequence than Hand et al., hence different EXP baseline
# ---------------------------------------------------------------------------
SP_V   = np.array([5,   7,   10,   13,   15,   18,   21])
SP_EXP = np.array([300, 800, 1290, 1300, 1270, 1180, 1250])   # N·m
SP_CFD = np.array([200, 610, 1130,  950,  840,  840,  950])   # N·m
SP_EXP_P = SP_EXP * 7.5398 / 1000
SP_CFD_P = SP_CFD * 7.5398 / 1000

RESULTS_DIR = os.path.join(os.path.dirname(__file__), "..", "results")
PLOT_DIR    = os.path.join(os.path.dirname(__file__), "..", "plots")
os.makedirs(PLOT_DIR, exist_ok=True)

MODEL_COLORS = {
    "laminar":      "#2196F3",
    "realizableKE": "#FF9800",
    "kOmegaSST":   "#4CAF50",
}
MODEL_LABELS = {
    "laminar":      "Laminar (present)",
    "realizableKE": "Realizable k-ε (present)",
    "kOmegaSST":   "k-ω SST (present)",
}


def load_csv(path):
    rows = []
    if not os.path.exists(path):
        return rows
    with open(path) as f:
        reader = csv.DictReader(f)
        for row in reader:
            rows.append({
                "model":  row["model"],
                "V":      float(row["V_inf_ms"]),
                "torque": float(row["torque_Nm"]),
                "power":  float(row["power_kW"]),
            })
    return rows


def make_torque_plot(ax, all_data):
    # Hand et al. experiment
    ax.errorbar(EXP_V, EXP_T, yerr=EXP_T * 0.05,
                fmt="ko-", capsize=4, linewidth=2, markersize=6,
                label="Experiment — Hand et al. (NREL/TP-500-29494)")

    # Song & Perot experiment and CFD
    ax.plot(SP_V, SP_EXP, "s--", color="#555555", linewidth=1.5, markersize=5,
            label="Experiment — Song & Perot (2015)")
    ax.plot(SP_V, SP_CFD, "^--", color="#9C27B0", linewidth=1.5, markersize=5,
            label="CFD — Song & Perot (2015)")

    # Present CFD results
    for model, color in MODEL_COLORS.items():
        rows = [r for r in all_data if r["model"] == model]
        if not rows:
            continue
        V = sorted(set(r["V"] for r in rows))
        T = [np.mean([r["torque"] for r in rows if r["V"] == v]) for v in V]
        ax.plot(V, T, "o-", color=color,
                label=MODEL_LABELS[model], linewidth=1.5, markersize=5)

    ax.set_xlabel("Wind speed V∞ (m/s)", fontsize=12)
    ax.set_ylabel("Shaft torque (N·m)", fontsize=12)
    ax.set_title("NREL Phase VI — Shaft Torque vs Wind Speed\n"
                 "2-blade, 72 rpm, MRF simpleFoam", fontsize=11)
    ax.legend(fontsize=8.5, loc="upper left")
    ax.grid(True, alpha=0.3)
    ax.set_xlim(4, 22)
    ax.set_ylim(0, 2200)

    ax.axvspan(4,  8,  alpha=0.05, color="green")
    ax.axvspan(8,  12, alpha=0.05, color="yellow")
    ax.axvspan(12, 22, alpha=0.05, color="red")
    ax.text(5.5, 2100, "Attached",    ha="center", fontsize=8, color="green")
    ax.text(10,  2100, "Onset stall", ha="center", fontsize=8, color="goldenrod")
    ax.text(17,  2100, "Deep stall",  ha="center", fontsize=8, color="red")


def main():
    all_data = []
    for model in MODEL_COLORS:
        csv_path = os.path.join(RESULTS_DIR, f"torque_{model}.csv")
        all_data.extend(load_csv(csv_path))

    if not all_data:
        print("No result CSV files found. Run sweep first.")
        return

    fig, axes = plt.subplots(1, 2, figsize=(14, 5))

    make_torque_plot(axes[0], all_data)

    # Power plot
    axes[1].errorbar(EXP_V, EXP_P, yerr=EXP_P * 0.05,
                     fmt="ko-", capsize=4, linewidth=2, markersize=6,
                     label="Experiment — Hand et al.")
    axes[1].plot(SP_V, SP_EXP_P, "s--", color="#555555", linewidth=1.5,
                 markersize=5, label="Experiment — Song & Perot (2015)")
    axes[1].plot(SP_V, SP_CFD_P, "^--", color="#9C27B0", linewidth=1.5,
                 markersize=5, label="CFD — Song & Perot (2015)")

    for model, color in MODEL_COLORS.items():
        rows = [r for r in all_data if r["model"] == model]
        if not rows:
            continue
        V = sorted(set(r["V"] for r in rows))
        P = [np.mean([r["power"] for r in rows if r["V"] == v]) for v in V]
        axes[1].plot(V, P, "o-", color=color,
                     label=MODEL_LABELS[model], linewidth=1.5, markersize=5)

    axes[1].set_xlabel("Wind speed V∞ (m/s)", fontsize=12)
    axes[1].set_ylabel("Shaft power (kW)", fontsize=12)
    axes[1].set_title("NREL Phase VI — Shaft Power vs Wind Speed", fontsize=11)
    axes[1].legend(fontsize=8.5, loc="upper left")
    axes[1].grid(True, alpha=0.3)
    axes[1].set_xlim(4, 22)
    axes[1].set_ylim(0, 17)

    plt.tight_layout()
    outpath = os.path.join(PLOT_DIR, "turbulence_model_validation.png")
    fig.savefig(outpath, dpi=150, bbox_inches="tight")
    print(f"Saved: {outpath}")

    # Error table vs Hand et al.
    print("\nTorque error vs Hand et al. experiment:")
    print(f"{'V∞':>6} {'Exp [N·m]':>12}", end="")
    for m in MODEL_COLORS:
        print(f"  {MODEL_LABELS[m]:>22}", end="")
    print()
    for v_exp, t_exp in zip(EXP_V, EXP_T):
        print(f"{v_exp:>6.0f} {t_exp:>12.0f}", end="")
        for model in MODEL_COLORS:
            rows = [r for r in all_data if r["model"] == model and r["V"] == v_exp]
            if rows:
                t_cfd = np.mean([r["torque"] for r in rows])
                err = (t_cfd - t_exp) / t_exp * 100
                print(f"  {err:>+21.1f}%", end="")
            else:
                print(f"  {'N/A':>22}", end="")
        print()


if __name__ == "__main__":
    main()
