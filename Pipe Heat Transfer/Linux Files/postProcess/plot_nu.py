"""Plot Nu vs Re: CFD vs Dittus-Boelter and Nu=3.658 (laminar)."""
import json, os
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.ticker as ticker

RESULTS = "/home/rinkoa/OpenFOAM-v2012/sims/PipeHeatTransfer/results/nu_results.json"
OUT_PLOT = "/home/rinkoa/OpenFOAM-v2012/sims/PipeHeatTransfer/results/nu_validation.png"
PORTFOLIO = "/mnt/c/Users/Samue/Documents/GitHub/OpenFOAM-Portfolio/Pipe Heat Transfer/nu_validation.png"

with open(RESULTS) as f:
    data = json.load(f)

lam_Re   = [d["Re"] for d in data if d["model"] == "laminar"]
lam_Nu   = [d["Nu_CFD"] for d in data if d["model"] == "laminar"]
turb_Re  = [d["Re"] for d in data if d["model"] == "turbulent"]
turb_Nu  = [d["Nu_CFD"] for d in data if d["model"] == "turbulent"]

# Theory lines
Re_turb = np.logspace(np.log10(3000), np.log10(1e6), 200)
Pr = 0.71
Nu_DB = 0.023 * Re_turb**0.8 * Pr**0.4   # Dittus-Boelter (Re > 10k)

# Gnielinski correlation (3000 < Re < 5e6) — more accurate at lower Re
def petukhov_f(Re):
    return (0.790 * np.log(Re) - 1.64) ** (-2)
f_turb = petukhov_f(Re_turb)
Nu_Gni = (f_turb / 8) * (Re_turb - 1000) * Pr / (1 + 12.7 * np.sqrt(f_turb / 8) * (Pr**(2/3) - 1))

fig, ax = plt.subplots(figsize=(8, 5.5))

# Theory
ax.axhline(3.658, color="royalblue", linewidth=1.5, linestyle="--", label="Nu = 3.658 (laminar, const $T_w$)")
ax.plot(Re_turb, Nu_DB, color="orangered", linewidth=1.5, linestyle="--", label="Dittus–Boelter (turbulent)")
ax.plot(Re_turb, Nu_Gni, color="darkorange", linewidth=1.5, linestyle=":", label="Gnielinski (turbulent)")

# CFD
ax.scatter(lam_Re, lam_Nu, marker="o", s=80, facecolors="none",
           edgecolors="royalblue", linewidths=2, zorder=5, label="CFD — laminar")
ax.scatter(turb_Re, turb_Nu, marker="^", s=80, color="orangered",
           zorder=5, label="CFD — turbulent (k–ω SST)")

# Transition band
ax.axvspan(2300, 4000, alpha=0.08, color="grey", label="Transition zone")

ax.set_xscale("log")
ax.set_yscale("log")
ax.set_xlabel("Reynolds number  Re", fontsize=12)
ax.set_ylabel("Nusselt number  Nu", fontsize=12)
ax.set_title("Pipe Flow Heat Transfer — CFD vs Analytical Correlations", fontsize=13)
ax.legend(fontsize=10, loc="upper left")
ax.grid(True, which="both", ls=":", alpha=0.5)
ax.xaxis.set_major_formatter(ticker.LogFormatter(labelOnlyBase=False, minor_thresholds=(4, 0.5)))
ax.set_xlim(300, 1.5e5)

plt.tight_layout()
plt.savefig(OUT_PLOT, dpi=150, bbox_inches="tight")
print(f"Saved: {OUT_PLOT}")

# Copy to portfolio
os.makedirs(os.path.dirname(PORTFOLIO), exist_ok=True)
import shutil
shutil.copy(OUT_PLOT, PORTFOLIO)
print(f"Copied to portfolio: {PORTFOLIO}")
plt.show()
