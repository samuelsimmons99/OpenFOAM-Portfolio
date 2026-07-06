#!/usr/bin/env python3
"""
Potato cooling post-processor.
Reads probe data from postProcessing/ and compares to Churchill-Bernstein analytical.
"""

import os
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

CASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PORTFOLIO = '/mnt/c/Users/Samue/Documents/GitHub/OpenFOAM-Portfolio/Potato Cooling'

# ── Physical properties ───────────────────────────────────────────────────────
T_air   = 25.0 + 273.15
T_init  = 180.0 + 273.15
R       = 0.040
D       = 2 * R
rho_p   = 1050.0
cp_p    = 3600.0
k_p     = 0.56
V       = (4/3) * np.pi * R**3
A       = 4 * np.pi * R**2
m       = rho_p * V

# Air at ~100°C film temperature
k_air  = 0.0313
nu_air = 2.31e-5
alpha  = 4.49e-5
Pr     = 0.713
beta   = 1.0 / ((T_init + T_air) / 2.0)
g      = 9.81

delta_T = T_init - T_air
Ra = g * beta * delta_T * D**3 / (nu_air * alpha)
Nu_CB = 2 + 0.589 * Ra**0.25 / (1 + (0.469/Pr)**(9/16))**(4/9)
h_CB = Nu_CB * k_air / D
Bi = h_CB * R / k_p
tau = m * cp_p / (h_CB * A)

print(f"Ra = {Ra:.3e},  Nu_CB = {Nu_CB:.2f},  h_CB = {h_CB:.2f} W/(m²K)")
print(f"Bi = {Bi:.3f},  τ_lumped = {tau:.0f} s")

t_ana = np.linspace(0, 600, 3000)
T_lump = T_air + (T_init - T_air) * np.exp(-t_ana / tau)

# ── Read probe files ──────────────────────────────────────────────────────────
def read_probe_file(probe_dir, field='T'):
    pfile = os.path.join(probe_dir, field)
    times, vals = [], []
    with open(pfile) as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith('#'):
                continue
            parts = line.split()
            try:
                times.append(float(parts[0]))
                vals.append([float(x) for x in parts[1:]])
            except ValueError:
                continue
    return np.array(times), np.array(vals)

t_sol, T_sol = read_probe_file(os.path.join(CASE, 'postProcessing/probes_solid/potato/0'))
t_flu, T_flu = read_probe_file(os.path.join(CASE, 'postProcessing/probes_fluid/domain0/0'))

T_sol_C = T_sol - 273.15
T_flu_C = T_flu - 273.15

# ── Plot ─────────────────────────────────────────────────────────────────────
fig, axes = plt.subplots(1, 2, figsize=(13, 5))
fig.suptitle(
    f'Potato Cooling — Natural Convection  (Ra={Ra:.2e}, Nu={Nu_CB:.1f}, Bi={Bi:.2f})',
    fontsize=12
)

# Left: temperature vs time
ax = axes[0]
ax.plot(t_ana, T_lump - 273.15, 'k--', lw=1.5,
        label=f'Lumped-C analytical (τ={tau:.0f} s, uniform T)')
ax.plot(t_sol, T_sol_C[:, 0], 'b-',  lw=2,   label='CFD: potato centre')
ax.plot(t_sol, T_sol_C[:, 1], 'r-',  lw=2,   label='CFD: surface equator (+x)')
ax.plot(t_sol, T_sol_C[:, 2], 'm--', lw=1.5, label='CFD: surface top (+z)')
ax.axhline(25, color='gray', lw=0.8, ls=':')
ax.text(580, 26, 'T_air', va='bottom', ha='right', fontsize=8, color='gray')
ax.set_xlabel('Time (s)')
ax.set_ylabel('Temperature (°C)')
ax.set_title('Cooling Curve — Potato (Bi=0.53 → CHT required)')
ax.legend(fontsize=8, loc='upper right')
ax.set_xlim(0, 600)
ax.set_ylim(140, 185)
ax.grid(True, alpha=0.3)

# Right: air plume + potato centre
ax2 = axes[1]
ax2.plot(t_sol, T_sol_C[:, 0], 'b-',  lw=2,   label='CFD: potato centre')
ax2.plot(t_flu, T_flu_C[:, 0], 'r-',  lw=1.5, label='CFD: air 20mm above (plume)')
ax2.plot(t_flu, T_flu_C[:, 1], 'g-',  lw=1.5, label='CFD: air 110mm above')
ax2.axhline(25, color='gray', lw=0.8, ls=':')
ax2.set_xlabel('Time (s)')
ax2.set_ylabel('Temperature (°C)')
ax2.set_title('Rising Hot Plume — Natural Convection')
ax2.legend(fontsize=8)
ax2.set_xlim(0, 600)
ax2.grid(True, alpha=0.3)

plt.tight_layout()

outfile = os.path.join(CASE, 'postProcess', 'potato_cooling.png')
os.makedirs(os.path.dirname(outfile), exist_ok=True)
plt.savefig(outfile, dpi=150, bbox_inches='tight')
print(f"Saved: {outfile}")

# Copy to portfolio
os.makedirs(PORTFOLIO, exist_ok=True)
import shutil
shutil.copy(outfile, os.path.join(PORTFOLIO, 'potato_cooling.png'))
print(f"Copied to portfolio.")

# ── Results table ─────────────────────────────────────────────────────────────
print("\n=== CFD results at key times ===")
print(f"{'t (s)':>7}  {'T_centre':>10}  {'T_surf_eq':>10}  {'T_surf_top':>11}  {'ΔT_spatial':>11}  {'T_lump':>8}")
for t_tgt in [0, 60, 120, 300, 600]:
    idx = np.argmin(np.abs(t_sol - t_tgt))
    Tc = T_sol_C[idx, 0]
    Ts_eq = T_sol_C[idx, 1]
    Ts_top = T_sol_C[idx, 2]
    Tl = (T_air + (T_init - T_air) * np.exp(-t_tgt / tau)) - 273.15
    print(f"{t_tgt:>7.0f}  {Tc:>10.2f}  {Ts_eq:>10.2f}  {Ts_top:>11.2f}  {Tc-Ts_eq:>11.2f}  {Tl:>8.2f}")
