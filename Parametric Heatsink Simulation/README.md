# Parametric Heatsink Conjugate Heat Transfer Study

**OpenFOAM 13 · foamMultiRun (buoyant, multi-region) · Parallel/Serial Verified · 20,000 Iterations**

A steady-state Conjugate Heat Transfer (CHT) simulation of a CPU + fin-array heatsink inside a fan-driven duct, built with a fully parametric Python mesh generator so fin pitch can be swept without rebuilding geometry by hand. Developed as part of an OpenFOAM CFD portfolio demonstrating industrial thermal simulation methodology.

---

## Key Results

| Parameter | Value |
|-----------|-------|
| Solver | `foamMultiRun` (buoyant, 3-region CHT) |
| Regions | `fluid` (air) + `solid` → `heatsink` (Al) + `cpu` (Si) cell zones |
| Total mesh cells | 649,200 (577,200 fluid + 72,000 solid) |
| Total iterations | 20,000 (steady-state) |
| CPU heat dissipation | 150 W |
| Fan | Delta FFB0812VH (quadratic curve, `fanPressure` BC) |
| Fan outlet velocity (converged) | 3.87 m/s |
| Fin pitch / fin count (baseline) | 5 mm / 15 fins |
| **Max CPU temperature** | **343.90 K (70.9°C)** |
| Inlet air temperature | 300 K (27°C) |
| Verification | Serial run vs. 8-core parallel run agree to 0.001 K |

---

## Simulation Overview

### Geometry — parametric, not hand-built
Geometry is generated directly as a `blockMeshDict` by [`gen_cases_v2.py`](Linux%20Files/gen_cases_v2.py): given a fin pitch and fin count, the script lays out alternating fin/channel/side-gap strips across the duct width, splits them against the CPU footprint, and emits a full hex-block mesh with fan, wall, and region-zone tagging baked in. This means a new pitch is a one-line parameter change, not a CAD rebuild — the point of the study being a *parametric* sweep rather than a single fixed design.

Fixed geometry (from `gen_cases_v2.py`):
- Fan/duct cross-section: 80 × 80 mm
- Fin thickness: 1.5 mm · Fin height: 35 mm · Base thickness: 5 mm
- CPU die: 40 × 40 × 4.5 mm, centered under the fin array
- Inlet/outlet plenum length: 105 mm each · Heatsink length: 80 mm (total duct length 290 mm)
- Baseline case: 5 mm pitch → 3.5 mm channel width, 15 fins, 4.25 mm side gaps

### Mesh
Block-structured hex mesh from `blockMesh`, split into regions with `splitMeshRegions -cellZones`.

| Region | Material | Cells |
|--------|----------|-------|
| `fluid` | Air (buoyant, k-ε) | 577,200 |
| `heatsink` | Aluminium (k = 205 W/m·K, ρ = 2700) | ~70,800 |
| `cpu` | Silicon (k = 150 W/m·K, ρ = 2329) | 1,200 |

### Solver Setup
- **Driver**: `foamMultiRun`, coupling one `fluid` region (buoyant, `p_rgh`/k-ε) to a `solid` super-region containing the `heatsink` and `cpu` cell zones
- **Region coupling**: `coupledTemperature` boundary condition at every `*_to_*` interface (fluid↔heatsink, fluid↔cpu, heatsink↔cpu)
- **Heat source**: `heatSource` fvModel, `cellZone allCpuCells`, `Q 150` (W), applied directly to the CPU silicon zone
- **Fan BC**: `fanPressure` at `fan1_half0`, driven by a tabulated `pressureVsQ.csv` curve fit from the Delta FFB0812VH fan curve `dP = 73.99 − 1164.25·Q − 34615·Q²` [Pa, Q in m³/s]
- **Turbulence**: k-ε
- **Run length**: 20,000 iterations to steady state, monitored via `cpuTmax`/`solidTmax` `volFieldValue`/`surfaceFieldValue` function objects

### Verification
The baseline 5 mm case was run twice — once serial, once decomposed across 8 MPI ranks — to confirm the parallel decomposition doesn't change the converged solution. Both runs land on **T_max = 343.900 K**, agreeing to within 0.001 K, which is a standard (and reassuring) parallel-vs-serial cross-check before trusting a decomposed run for larger sweeps.

---

## Results

### Convergence
CPU max temperature settles to 343.90 K by ~15,000 iterations in both runs (see `postProcessing/cpu/cpuTmax/*/volFieldValue.dat`); residuals for U, h, e, and p_rgh are all below 1e-6 at iteration 20,000.

### Thermal performance
At 150 W dissipation and a 5 mm/15-fin array, the duct reaches a converged fan exit velocity of 3.87 m/s and holds the CPU die at 70.9°C above a 27°C inlet — a CPU-to-ambient temperature rise of ~44 K under fan-curve-driven (not fixed-velocity) airflow.

---

## Workflow

```
gen_cases_v2.py (parametric blockMeshDict generator)
        ↓
blockMesh (hex mesh, fin/channel/side-gap strips + fan/wall patches)
        ↓
splitMeshRegions -cellZones (fluid | heatsink | cpu)
        ↓
foamMultiRun (buoyant fluid + conductive solid, coupled, 20,000 iterations)
        ↓
postProcessing (cpuTmax, solidTmax, fan patch flow/velocity)
```

---

## Status & Future Work

This is the **baseline case** of an intended 3-point fin-pitch sweep (4 mm / 5 mm / 6 mm). Current state in the `sims` directory:

| Case folder | Status | Result |
|-------------|--------|--------|
| 5 mm pitch, 15 fins (serial) | ✅ Converged, 20,000 it. | T_max = 343.90 K |
| 5 mm pitch, 15 fins (8-core parallel) | ✅ Converged, 20,000 it. | T_max = 343.90 K |
| 4 mm pitch (18 fins) | 🔲 Planned — regenerate mesh via `gen_cases_v2.py` with `fin_pitch=4e-3` | — |
| 6 mm pitch (12 fins) | 🔲 Planned — regenerate mesh via `gen_cases_v2.py` with `fin_pitch=6e-3` | — |

Next step: parameterize `gen_cases_v2.py`'s `fin_pitch`/`n_fins` per case folder, rerun, and compare T_max across pitches to find the thermal optimum for this fan/duct combination (tighter fins → more flow resistance; wider fins → less surface area — the expected result is a minimum CPU temperature at an intermediate pitch).

---

## Software Stack

| Tool | Version | Purpose |
|------|---------|---------|
| OpenFOAM | 13 | CFD solver (`foamMultiRun`, buoyant multi-region CHT) |
| Python | 3.x | Parametric `blockMeshDict` generation |
| Ubuntu (WSL2) | 24.04 | OS |
| OpenMPI | — | 8-core parallel verification run |

---

## Repository

Part of the [OpenFOAM Portfolio](https://github.com/samuelsimmons99/OpenFOAM-Portfolio) — a collection of CFD simulations demonstrating thermal and fluid simulation skills relevant to thermal engineering roles.
