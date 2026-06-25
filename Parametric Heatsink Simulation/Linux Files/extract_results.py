#!/usr/bin/env python3
"""
Post-process all parametric heatsink cases.
Extracts max solid temperature and computes thermal resistance R = (T_max - T_in) / Q.
Reads from fieldMinMax function object output.
"""

import os
import glob
import re

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
Q = 150.0       # W
T_IN = 300.0    # K

results = []

for case_dir in sorted(glob.glob(os.path.join(SCRIPT_DIR, "pitch_*"))):
    name = os.path.basename(case_dir)

    # Read case summary for fin_pitch
    summary_path = os.path.join(case_dir, "case_summary.txt")
    fin_pitch_mm = None
    n_fins = None
    if os.path.exists(summary_path):
        with open(summary_path) as f:
            for line in f:
                m = re.search(r"fin_pitch=(\S+)mm", line)
                if m:
                    fin_pitch_mm = float(m.group(1))
                m = re.search(r"n_fins=(\d+)", line)
                if m:
                    n_fins = int(m.group(1))

    # Find latest time directory in solid region
    solid_dirs = sorted(glob.glob(os.path.join(case_dir, "solid", "[0-9]*")))
    if not solid_dirs:
        print(f"  {name}: no solid time directories found — skipping")
        continue
    latest_solid = solid_dirs[-1]
    t_latest = os.path.basename(latest_solid)

    # Read T field max from fieldMinMax log
    # fieldMinMax writes to postProcessing/fieldMinMax/<time>/fieldMinMax.dat
    minmax_files = glob.glob(os.path.join(case_dir, "postProcessing", "fieldMinMax", "*", "fieldMinMax.dat"))
    T_max = None
    if minmax_files:
        with open(minmax_files[0]) as f:
            lines = [l for l in f if not l.startswith("#") and l.strip()]
        if lines:
            # columns: Time  field  min  minLocation  max  maxLocation
            # We want the last entry for T in the solid region
            last_T_line = None
            for line in lines:
                if "T" in line:
                    last_T_line = line
            if last_T_line:
                parts = last_T_line.split()
                try:
                    T_max = float(parts[4])  # max column
                except (IndexError, ValueError):
                    pass

    if T_max is None:
        # Fallback: parse solver log for last T residual line won't give T_max
        print(f"  {name}: could not extract T_max from fieldMinMax — check postProcessing/")
        continue

    R_th = (T_max - T_IN) / Q
    results.append({
        "name": name,
        "fin_pitch_mm": fin_pitch_mm,
        "n_fins": n_fins,
        "T_max_K": T_max,
        "T_max_C": T_max - 273.15,
        "R_th": R_th,
        "t_latest": t_latest,
    })

if not results:
    print("No results found. Have all cases converged?")
else:
    print(f"\n{'Case':<30} {'Pitch(mm)':<12} {'N_fins':<8} {'T_max(K)':<12} {'T_max(C)':<12} {'R_th(K/W)':<12}")
    print("-" * 86)
    for r in results:
        print(f"{r['name']:<30} {r['fin_pitch_mm']:<12.1f} {r['n_fins']:<8} "
              f"{r['T_max_K']:<12.2f} {r['T_max_C']:<12.2f} {r['R_th']:<12.4f}")
    print()

    # Find optimal
    best = min(results, key=lambda x: x["R_th"])
    print(f"Lowest thermal resistance: {best['name']}  R_th = {best['R_th']:.4f} K/W")
