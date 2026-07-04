"""
Plot CFD friction factor vs Re and overlay Moody chart analytical curves.

Laminar:    f = 64/Re   (Hagen-Poiseuille, exact)
Turbulent:  f = 0.316*Re^-0.25  (Blasius smooth pipe, Re < 1e5)
            f = (0.790*ln(Re) - 1.64)^-2  (Petukhov, Re 3e3-5e6)
"""

import os
import csv
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

SIMS = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RESULTS_DIR = os.path.join(SIMS, "results")
PLOTS_DIR   = os.path.join(SIMS, "plots")
os.makedirs(PLOTS_DIR, exist_ok=True)

# --- analytical curves ---
Re_lam  = np.logspace(1.5, 3.36, 200)   # Re 30 → 2300 (xlim starts at 30)
Re_turb = np.logspace(3.5,  5.5,  200)  # Re 3e3 → 3e5

f_lam     = 64.0 / Re_lam
f_blasius = 0.316 * Re_turb**-0.25
f_petukhov = (0.790 * np.log(Re_turb) - 1.64)**-2

# --- load CFD results ---
csv_path = os.path.join(RESULTS_DIR, "friction_factors.csv")
laminar_pts = []
turb_pts    = []

if os.path.exists(csv_path):
    with open(csv_path) as f:
        reader = csv.DictReader(f)
        for row in reader:
            Re    = float(row["Re"])
            f_cfd = float(row["f_cfd"])
            model = row["model"]
            if model == "laminar":
                laminar_pts.append((Re, f_cfd))
            else:
                turb_pts.append((Re, f_cfd))

laminar_pts.sort()
turb_pts.sort()

# --- plot ---
fig, ax = plt.subplots(figsize=(9, 6))

ax.loglog(Re_lam,  f_lam,     "k-",  linewidth=2,   label="Laminar: $f = 64/Re$ (Hagen-Poiseuille)")
ax.loglog(Re_turb, f_blasius, "b--", linewidth=1.5,  label="Blasius: $f = 0.316\\,Re^{-1/4}$  ($Re < 10^5$)")
ax.loglog(Re_turb, f_petukhov,"b:",  linewidth=1.5,  label="Petukhov: $(0.790\\ln Re - 1.64)^{-2}$")

if laminar_pts:
    Re_l, f_l = zip(*laminar_pts)
    ax.loglog(Re_l, f_l, "ro", markersize=9, zorder=5,
              markerfacecolor="none", markeredgewidth=2,
              label="Laminar CFD (present)")

if turb_pts:
    Re_t, f_t = zip(*turb_pts)
    ax.loglog(Re_t, f_t, "g^", markersize=8, zorder=5,
              label="k-ω SST CFD (present)")

# Transition band
ax.axvspan(2300, 4000, alpha=0.08, color="orange", label="Transition zone (2300 < Re < 4000)")

ax.set_xlabel("Reynolds number  $Re = U_{bulk} D / \\nu$", fontsize=12)
ax.set_ylabel("Darcy friction factor  $f$", fontsize=12)
ax.set_title("Pipe Flow — Friction Factor Validation (Moody Chart)\n"
             "D = 50 mm, periodic domain, simpleFoam", fontsize=11)
ax.legend(fontsize=9, loc="upper right")
ax.grid(True, which="both", alpha=0.3)
ax.set_xlim(30, 3e5)
ax.set_ylim(0.005, 2.0)

plt.tight_layout()
out = os.path.join(PLOTS_DIR, "moody_validation.png")
fig.savefig(out, dpi=150, bbox_inches="tight")
print(f"Saved: {out}")

# --- error table ---
print("\nFriction factor error vs theory:")
if os.path.exists(csv_path):
    with open(csv_path) as f:
        reader = csv.DictReader(f)
        print(f"{'Model':>12} {'Re':>8} {'f_CFD':>8} {'f_theory':>10} {'err%':>7}")
        for row in reader:
            print(f"{row['model']:>12} {float(row['Re']):>8.0f} "
                  f"{float(row['f_cfd']):>8.4f} {float(row['f_theory']):>10.4f} "
                  f"{float(row['err_pct']):>+7.1f}%")
