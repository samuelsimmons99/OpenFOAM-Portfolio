"""
Extract Nusselt number from PipeHeatTransfer cases.

Reads OpenFOAM ASCII field files directly (no sampledSets needed).
Mesh: 25 radial × 1 azimuthal × 250 axial = 6250 cells
Cell ordering: radial (i) fastest, then axial (k): global = k*25 + i
Radial cell centres: x_i = R * (i+0.5)/25 (uniform grading = 0.1, so non-uniform)

For Nu:
  - Read T field at axial slice k=240 (z ≈ 2.4 m)
  - Read U field at same slice → U_z profile
  - Compute T_bulk = Σ(Uz*T*r*dr) / Σ(Uz*r*dr)  [velocity-weighted, axisymmetric]
  - q_w_local = min wallHeatFlux at last iteration (from log) — this is at outlet
  - Nu = q_w * D / (k_air * (T_wall - T_bulk))
"""

import os, math, json, re
import numpy as np

CASES_DIR = "/home/rinkoa/OpenFOAM-v2012/sims/PipeHeatTransfer/cases"
RESULTS_DIR = "/home/rinkoa/OpenFOAM-v2012/sims/PipeHeatTransfer/results"
os.makedirs(RESULTS_DIR, exist_ok=True)

D = 0.05
R = D / 2
k_air = 0.0262   # [W/(m·K)]
T_wall = 350.0
T_in = 300.0
nu_air = 1.5e-5
Cp = 1005.0
Pr = 0.71
N_RAD = 25       # radial cells
N_AX = 250       # axial cells
N_CELLS = N_RAD * N_AX

case_list = [
    ("lam_Re500",    500,   "laminar"),
    ("lam_Re1000",   1000,  "laminar"),
    ("lam_Re2000",   2000,  "laminar"),
    ("turb_Re5000",  5000,  "turbulent"),
    ("turb_Re10000", 10000, "turbulent"),
    ("turb_Re20000", 20000, "turbulent"),
    ("turb_Re50000", 50000, "turbulent"),
]


def read_of_scalar_field(path):
    """Parse OpenFOAM ASCII scalar internalField into numpy array."""
    with open(path) as f:
        txt = f.read()
    # Find internalField block
    m = re.search(r'internalField\s+nonuniform\s+List<scalar>\s*\n\s*(\d+)\s*\n\s*\(\s*\n(.*?)\n\s*\)', txt, re.DOTALL)
    if not m:
        # Try uniform value
        m2 = re.search(r'internalField\s+uniform\s+([\d.e+-]+)', txt)
        if m2:
            return np.full(N_CELLS, float(m2.group(1)))
        return None
    n = int(m.group(1))
    vals = list(map(float, m.group(2).split()))
    return np.array(vals[:n])


def read_of_vector_field(path):
    """Parse OpenFOAM ASCII vector internalField → Nx3 numpy array."""
    with open(path) as f:
        txt = f.read()
    m = re.search(r'internalField\s+nonuniform\s+List<vector>\s*\n\s*(\d+)\s*\n\s*\(\s*\n(.*?)\n\s*\)', txt, re.DOTALL)
    if not m:
        m2 = re.search(r'internalField\s+uniform\s+\(([\d.e+\-\s]+)\)', txt)
        if m2:
            v = list(map(float, m2.group(1).split()))
            return np.tile(v, (N_CELLS, 1))
        return None
    n = int(m.group(1))
    raw = re.findall(r'\(([\d.e+\-\s]+)\)', m.group(2))
    vals = [list(map(float, x.split())) for x in raw[:n]]
    return np.array(vals)


def read_cell_centres(case_path):
    """Read cell centre x and z coordinates from constant/polyMesh/cellCentres if written,
    otherwise compute from known blockMesh grading (0.1 grading in x, uniform in z)."""
    # Try reading from postProcessing/cellCentres if available
    # Otherwise compute analytically from blockMesh
    # blockMesh grading: simpleGrading (0.1 1 1)
    # Radial grading ratio = 0.1 → geometric series from axis to wall
    # Wall spacing / axis spacing = 0.1
    # Sum of n terms: S = R, ratio r per cell: a*(r^n - 1)/(r-1) = R
    # Expansion ratio 0.1 means last/first = 0.1
    n = N_RAD
    er = 0.1  # last cell / first cell width
    # geometric series: r^(n-1) = er → r = er^(1/(n-1))
    r = er ** (1.0 / (n - 1))
    # cell widths: w_i = w_0 * r^i
    # sum w_i = R → w_0 * (r^n - 1) / (r - 1) = R
    w0 = R * (r - 1) / (r**n - 1)
    widths = np.array([w0 * r**i for i in range(n)])
    # cell centres from axis
    edges = np.concatenate([[0.0], np.cumsum(widths)])
    x_c = 0.5 * (edges[:-1] + edges[1:])  # radial cell centres

    # axial cell centres (uniform: 250 cells over 2.5 m)
    dz = 2.5 / N_AX
    z_c = np.array([(k + 0.5) * dz for k in range(N_AX)])

    return x_c, z_c, widths


def find_latest_time(case_path):
    times = []
    for d in os.listdir(case_path):
        try:
            t = float(d)
            if t > 0:
                times.append(t)
        except ValueError:
            pass
    return str(int(max(times))) if times else None


def read_last_wallheatflux(log_path):
    """Get q_w min/max at last outer iteration from solver log."""
    q_min = q_max = q_integ = None
    with open(log_path) as f:
        for line in f:
            if 'min/max/integ' in line:
                parts = line.split('=')[-1].strip().split(',')
                try:
                    q_min = float(parts[0].strip())
                    q_max = float(parts[1].strip())
                    q_integ = float(parts[2].strip())
                except:
                    pass
    return q_min, q_max, q_integ


def compute_nu(case_name, Re, model):
    case_path = os.path.join(CASES_DIR, case_name)
    if not os.path.isdir(case_path):
        print(f"  {case_name}: not found")
        return None

    Ubulk = Re * nu_air / D

    # Get latest time
    t_str = find_latest_time(case_path)
    if not t_str:
        print(f"  {case_name}: no time directories")
        return None

    # Read T and U fields
    T_path = os.path.join(case_path, t_str, "T")
    U_path = os.path.join(case_path, t_str, "U")
    if not os.path.exists(T_path):
        print(f"  {case_name}: T field not found at t={t_str}")
        return None

    T_field = read_of_scalar_field(T_path)
    U_field = read_of_vector_field(U_path)
    if T_field is None or U_field is None:
        print(f"  {case_name}: failed to read fields")
        return None

    # Get cell geometry
    x_c, z_c, widths = read_cell_centres(case_path)

    # Extract radial profile at axial slice k=249 (z≈2.495m, outlet — consistent with q_min location)
    k_sample = 249
    cell_indices = np.array([k_sample * N_RAD + i for i in range(N_RAD)])

    T_rad = T_field[cell_indices]
    Uz_rad = U_field[cell_indices, 2]   # z-component (axial velocity)
    r_rad = x_c                          # radial positions

    # Velocity-weighted bulk temperature (axisymmetric): ∫Uz*T*r*dr / ∫Uz*r*dr
    dr = widths
    num = np.sum(Uz_rad * T_rad * r_rad * dr)
    den = np.sum(Uz_rad * r_rad * dr)
    T_bulk = num / den if den > 0 else T_in

    # Wall heat flux from log (local value at outlet = q_min)
    log_path = None
    for name in ["log.solver", "log.simpleFoam", "log.buoyantSimpleFoam"]:
        p = os.path.join(case_path, name)
        if os.path.exists(p):
            log_path = p
            break
    if not log_path:
        print(f"  {case_name}: solver log not found")
        return None

    q_min, q_max, q_integ_wedge = read_last_wallheatflux(log_path)
    if q_min is None:
        print(f"  {case_name}: wallHeatFlux not in log")
        return None

    # q_min is the local wall flux at the coolest part (outlet, fully-developed)
    q_w = q_min  # [W/m²]
    dT = T_wall - T_bulk
    if dT <= 0:
        print(f"  {case_name}: T_bulk={T_bulk:.2f} >= T_wall — check setup")
        return None

    Nu_CFD = q_w * D / (k_air * dT)

    # Theoretical (Gnielinski for turbulent — more accurate than Dittus-Boelter at lower Re)
    if model == "laminar":
        Nu_theory = 3.658
    else:
        f_p = (0.790 * math.log(Re) - 1.64) ** (-2)
        Nu_theory = (f_p/8) * (Re - 1000) * Pr / (1 + 12.7 * math.sqrt(f_p/8) * (Pr**(2/3) - 1))
    err = (Nu_CFD - Nu_theory) / Nu_theory * 100

    return {
        "case": case_name, "Re": Re, "model": model,
        "Nu_CFD": Nu_CFD, "Nu_theory": Nu_theory,
        "T_bulk_z2p4": T_bulk, "q_w_outlet": q_w,
        "err_pct": err
    }


results = []
print(f"\n{'Case':<22} {'Re':>7}  {'T_bulk':>7}  {'q_w':>8}  {'Nu_CFD':>8}  {'Nu_theory':>10}  {'error':>7}")
print("-" * 80)
for case_name, Re, model in case_list:
    r = compute_nu(case_name, Re, model)
    if r:
        results.append(r)
        print(f"  {case_name:<20} {Re:>7}  {r['T_bulk_z2p4']:>7.2f}  {r['q_w_outlet']:>8.2f}  {r['Nu_CFD']:>8.3f}  {r['Nu_theory']:>10.3f}  {r['err_pct']:>+6.1f}%")
    else:
        print(f"  {case_name:<20} {Re:>7}  [skipped]")

out_path = os.path.join(RESULTS_DIR, "nu_results.json")
with open(out_path, "w") as f:
    json.dump(results, f, indent=2)
print(f"\nSaved {len(results)} results to {out_path}")
