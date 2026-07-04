"""
Extract shaft torque from OpenFOAM forces postProcessing output.
OpenFOAM v2012 splits forces into force.dat and moment.dat.

With two blades (blade + blade2) the forces function writes a single
moment.dat that sums both patches — total 2-blade rotor torque.

moment.dat columns:
  Time  (Mp_x Mp_y Mp_z)  (Mv_x Mv_y Mv_z)  (Mporous_x ...)
  Total moment x (parts[1]) = shaft torque about rotor axis.
"""

import argparse
import csv
import os
import numpy as np

OMEGA = 7.5398   # rad/s = 72 rpm


def find_moment_file(case_dir):
    pp = os.path.join(case_dir, "postProcessing", "forces")
    if not os.path.isdir(pp):
        raise FileNotFoundError(f"No postProcessing/forces in {case_dir}")
    times = sorted(os.listdir(pp), key=float)
    latest = times[-1]
    for fname in ("moment.dat", "moment_0.dat"):
        fpath = os.path.join(pp, latest, fname)
        if os.path.exists(fpath):
            return fpath
    raise FileNotFoundError(f"No moment.dat in {os.path.join(pp, latest)}")


def parse_moments(filepath):
    times, Mx_total = [], []
    with open(filepath) as f:
        for line in f:
            if line.startswith("#") or not line.strip():
                continue
            parts = line.replace("(", " ").replace(")", " ").split()
            if len(parts) < 4:
                continue
            try:
                t = float(parts[0])
                mx_total = float(parts[1])
            except ValueError:
                continue
            times.append(t)
            Mx_total.append(mx_total)
    return np.array(times), np.array(Mx_total)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--case", required=True)
    parser.add_argument("--model", required=True)
    parser.add_argument("--vwind", required=True, type=float)
    parser.add_argument("--output", required=True)
    args = parser.parse_args()

    fpath = find_moment_file(args.case)
    times, Mx = parse_moments(fpath)

    # Average last 500 iterations of a 3000-iter run
    n_avg = min(500, len(times))
    mean_torque = np.mean(Mx[-n_avg:])
    shaft_torque = abs(mean_torque)   # 2-blade total (both patches summed by OF)
    mean_power_kW = shaft_torque * OMEGA / 1000.0

    print(f"  {args.model}  V={args.vwind} m/s  |torque|={shaft_torque:.1f} N·m  "
          f"P={mean_power_kW:.2f} kW")

    os.makedirs(os.path.dirname(args.output), exist_ok=True)
    write_header = not os.path.exists(args.output)
    with open(args.output, "a", newline="") as f:
        writer = csv.writer(f)
        if write_header:
            writer.writerow(["model", "V_inf_ms", "torque_Nm", "power_kW"])
        writer.writerow([args.model, args.vwind,
                         f"{shaft_torque:.1f}", f"{mean_power_kW:.3f}"])


if __name__ == "__main__":
    main()
