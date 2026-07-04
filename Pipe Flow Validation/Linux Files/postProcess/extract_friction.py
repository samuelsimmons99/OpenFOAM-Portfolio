"""
Extract friction factor from a converged PipeFlow case.

Method: read wallShearStress field on the wall patch, area-average
the magnitude, then compute:
    f = 8 * tau_w / (rho * Ubulk^2)   [Darcy friction factor]

Analytical checks:
    Laminar:    f = 64/Re  (Hagen-Poiseuille)
    Turbulent:  f = 0.316 * Re^-0.25  (Blasius, Re < 1e5)
"""

import argparse
import csv
import math
import os
import struct


def latest_time(case_dir):
    times = []
    for name in os.listdir(case_dir):
        try:
            t = float(name)
            if t > 0:
                times.append(t)
        except ValueError:
            pass
    return max(times) if times else None


def read_wss_from_log(log_path):
    """
    Parse wallShearStress area-average from the surfaceFieldValue log output
    embedded in log.simpleFoam. Returns (wss_x, wss_y, wss_z) or None.
    """
    if not os.path.exists(log_path):
        return None
    wss = None
    with open(log_path) as f:
        for line in f:
            # surfaceFieldValue prints: areaAverage(wall) of wallShearStress = (x y z)
            if "areaAverage" in line and "wallShearStress" in line and "=" in line:
                after_eq = line.split("=")[-1].strip()
                vals = after_eq.strip("()\n").split()
                if len(vals) == 3:
                    wss = tuple(float(v) for v in vals)
    return wss


def read_wss_from_field(case_dir):
    """
    Fallback: read wallShearStress OpenFOAM field file at latest time,
    parse the wall patch internal values, compute area-weighted mean magnitude.
    Uses postProcessing/wallShearStress if present.
    """
    pp_dir = os.path.join(case_dir, "postProcessing", "wallShearStress")
    if not os.path.isdir(pp_dir):
        return None

    times = []
    for d in os.listdir(pp_dir):
        try:
            times.append(float(d))
        except ValueError:
            pass
    if not times:
        return None

    t_dir = os.path.join(pp_dir, str(int(max(times))) if max(times).is_integer() else str(max(times)))
    # try both integer and float string
    for name in os.listdir(pp_dir):
        candidate = os.path.join(pp_dir, name, "wallShearStress_wall.dat")
        if os.path.exists(candidate):
            wss_file = candidate
            break
    else:
        return None

    vals = []
    with open(wss_file) as f:
        for line in f:
            line = line.strip()
            if line.startswith("#") or not line:
                continue
            parts = line.split()
            if len(parts) >= 4:
                # x y z columns
                vals.append((float(parts[1]), float(parts[2]), float(parts[3])))

    if not vals:
        return None
    mean = [sum(v[i] for v in vals) / len(vals) for i in range(3)]
    return tuple(mean)


def f_theory(Re, model):
    if model == "laminar":
        return 64.0 / Re
    else:
        # Blasius (Re < 1e5)
        return 0.316 * Re**-0.25


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--case",   required=True)
    p.add_argument("--model",  required=True)
    p.add_argument("--Re",     type=float, required=True)
    p.add_argument("--Ubulk",  type=float, required=True)
    p.add_argument("--nu",     type=float, required=True)
    p.add_argument("--rho",    type=float, required=True)
    p.add_argument("--D",      type=float, required=True)
    p.add_argument("--output", required=True)
    args = p.parse_args()

    log_path = os.path.join(args.case, "log.simpleFoam")

    wss = read_wss_from_log(log_path)
    if wss is None:
        wss = read_wss_from_field(args.case)
    if wss is None:
        print(f"  [WARN] Could not extract WSS for Re={args.Re} — skipping")
        return

    # wallShearStress in OF incompressible = kinematic stress = tau_Pa/rho [m^2/s^2]
    tau_mag = math.sqrt(sum(v**2 for v in wss))
    f_cfd = 8.0 * tau_mag / (args.Ubulk**2)
    f_th  = f_theory(args.Re, args.model)
    err   = (f_cfd - f_th) / f_th * 100

    print(f"  Re={args.Re:.0f}  tau_w(kinematic)={tau_mag:.4e} m2/s2  "
          f"f_cfd={f_cfd:.4f}  f_theory={f_th:.4f}  err={err:+.1f}%")

    write_header = not os.path.exists(args.output)
    with open(args.output, "a", newline="") as f:
        w = csv.writer(f)
        if write_header:
            w.writerow(["model", "Re", "Ubulk", "f_cfd", "f_theory", "err_pct"])
        w.writerow([args.model, args.Re, args.Ubulk,
                    round(f_cfd, 6), round(f_th, 6), round(err, 2)])


if __name__ == "__main__":
    main()
