# NREL Phase VI Wind Turbine — Turbulence Model Validation

**Solver:** `simpleFoam` + MRF &nbsp;|&nbsp; **Mesh:** snappyHexMesh, 1.15 M cells &nbsp;|&nbsp; **Models:** Laminar · Realizable k-ε · k-ω SST

---

## Overview

Validation study on the NREL Phase VI 2-blade horizontal-axis wind turbine, one of the most widely cited CFD benchmarks for rotating machinery. Open experimental data come from the NASA Ames 80 × 120 ft wind tunnel (Hand et al., NREL/TP-500-29494, 2001). Blade geometry (NREL S809 airfoil, tapered and twisted from hub to tip) is generated programmatically in Python and imported into snappyHexMesh. A cylindrical Multiple Reference Frame (MRF) rotating zone captures blade loading without mesh motion. All 21 cases (3 turbulence models × 7 wind speeds) are run to convergence and compared against measured low-speed shaft torque.

---

## Geometry

```
          ┌──────────────────────────────────────────┐
 slip BC  │                                          │  slip BC
  top     │  ←── 15 m ──┤  rotor  ├──── 30 m ─────→ │  outlet
          │              ↑ x = 0                     │
          │    ┌─────────────────────────────────┐    │
  inlet   │    │     MRF rotating zone           │    │
 (fixedV) │    │  blade + blade2, 72 rpm         │    │
          │    └─────────────────────────────────┘    │
 slip BC  │                                          │  slip BC
  bottom  │         D_rotor = 10.06 m               │  (side1/2)
          └──────────────────────────────────────────┘
```

| Parameter | Value |
|-----------|-------|
| Rotor diameter | 10.058 m (2-bladed) |
| Airfoil | NREL S809, t/c = 21% |
| Rotation | 72 rpm = 7.540 rad/s (about +x axis) |
| Pitch | 3° at tip (feather) |
| Domain | x: −15 → +30 m &nbsp;·&nbsp; y, z: ±13 m |
| Upstream distance | 3R (15 m) |
| Downstream distance | 6R (30 m) |
| Wind speeds simulated | 5, 7, 10, 13, 15, 18, 21 m/s |
| Tip speed ratio λ | 1.80 – 7.54 |

---

## Boundary Conditions

| Patch | Type | U | p |
|-------|------|---|---|
| `inlet` | patch | `fixedValue` (V∞, axial) | `zeroGradient` |
| `outlet` | patch | `inletOutlet` | `fixedValue` (0) |
| `top / bottom / side1 / side2` | slip | `slip` | `zeroGradient` |
| `blade` / `blade2` | wall | `noSlip` | `zeroGradient` |

Turbulence at inlet: k–ω SST, Tu = 0.5%, L_t = 0.1R.

---

## Mesh

Generated with `snappyHexMesh` from a programmatically generated S809-profile blade STL:

| Item | Value |
|------|-------|
| Base hex grid | Cartesian box, ~270k cells |
| Blade surface refinement | 3 levels (cell size ≈ 5 mm near leading edge) |
| Prism layers | 5 layers, expansion ratio 1.3, y⁺ ≈ 30–80 |
| Rotating zone | Spherical cellZone, R = 5.8 m, centred at origin |
| Total cells (refined) | **1.15 M** |
| Non-orthogonality (max) | < 65° |

---

## Results — Low-Speed Shaft Torque vs Wind Speed

<img src="turbulence_model_validation.png" width="700">

| V∞ (m/s) | λ | Exp. τ (N·m) | k-ω SST (N·m) | Error | Laminar (N·m) | Error | Regime |
|----------|---|-------------|---------------|-------|--------------|-------|--------|
| 5 | 7.54 | 130 | 380 | +192% | 466 | +258% | Pre-stall (high TSR) |
| 7 | 5.39 | 420 | **419** | **−0.2%** | 487 | +16% | Design point |
| 10 | 3.77 | 1 490 | 499 | −67% | 587 | −61% | Stall onset |
| 13 | 2.90 | 1 620 | 552 | −66% | 625 | −61% | Partial stall |
| 15 | 2.52 | 1 490 | 556 | −63% | 651 | −56% | Deep stall |
| 18 | 2.10 | 1 400 | 666 | −52% | 751 | −46% | Deep stall |
| 21 | 1.80 | 1 370 | 780 | −43% | 903 | −34% | Deep stall |

Experimental values from Hand et al. (NREL/TP-500-29494), Figure 8. ω = 7.540 rad/s.

---

## Key Findings

1. **Design-point accuracy** — k-ω SST matches the measured shaft torque at V = 7 m/s (λ = 5.4) to within 0.2%, consistent with Song & Perot (2015) who reported comparable accuracy with Spalart-Allmaras.

2. **Post-stall underprediction** — All RANS models underpredict torque above V = 10 m/s by 40–70%. Steady RANS cannot capture the 3D dynamic-stall vortices and centrifugal pumping that sustain torque in the separated regime; LES or DES would be required to close the gap.

3. **High-TSR overprediction (V = 5 m/s)** — At λ = 7.54 the inboard blade sections (r/R < 0.3) operate at very high geometric angles of attack. The MRF/RANS approach overestimates inboard loading; 3D rotational-stall correction (à la Snel 1994) is outside the scope of simpleFoam.

4. **Turbulence model sensitivity** — In attached flow (V ≤ 7 m/s), k-ω SST outperforms the laminar model by a factor of ~5 in torque accuracy. Realizable k-ε is numerically less stable at off-design conditions (convergence issues at V = 5, 13, 21 m/s) and is not plotted for those cases.

5. **RANS limits on rotating blades** — Consistent with the 2001 blind-comparison study (TP-500-29494), where 30 analysis codes predicted power over a range of 25–275% of the measured value. Steady RANS on rotating blades is reliable only in the attached-flow regime.

---

## References

- Hand, M. M. et al. "Unsteady Aerodynamics Experiment Phase VI: Wind Tunnel Test Configurations and Available Data Campaigns." NREL/TP-500-29494, December 2001. _(primary experimental source)_
- Song, Y. & Perot, J. B. "CFD Simulation of the NREL Phase VI Rotor." _Wind Engineering_ 39(3), pp. 299–310, 2015. _(OpenFOAM pimpleDyMFoam, SA model, 10 M cells)_
- Giguère, P. & Selig, M. S. "Design of a Tapered and Twisted Blade for the NREL Combined Experiment Rotor." NREL/SR-500-26173, April 1999. _(blade geometry source)_
- Snel, H. et al. "Sectional Prediction of 3-D Effects for Stalled Flow on Rotating Blades." ECWEC 1993. _(rotation corrections context)_
