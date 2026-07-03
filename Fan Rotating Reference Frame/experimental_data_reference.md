# NREL Phase VI — Experimental Validation Data Reference

---

## Source documents in this folder

| File | Reference |
|------|-----------|
| `NREL Unsteady Aerodynamics.pdf` | Simms, Schreck, Hand, Fingersh — NREL/TP-500-29494, June 2001. "NREL Unsteady Aerodynamics Experiment in the NASA-Ames Wind Tunnel: A Comparison of Predictions to Measurements." The primary source of measured torque, thrust, and spanwise force data. |
| `NREL_Paper.pdf` | Song & Perot — Wind Engineering, Vol. 39, No. 3, 2015, pp. 299–310. "CFD Simulation of the NREL Phase VI Rotor." OpenFOAM pimpleDyMFoam (Spalart-Allmaras) vs. experiment. Good reference for mesh strategy and solver setup. |

---

## Test configuration (from TP-500-29494 and Song & Perot 2015)

| Parameter | Value |
|-----------|-------|
| Rotor diameter | 10.058 m (2-bladed) |
| Rotation rate | 72 rpm = 7.540 rad/s |
| Tip pitch angle | 3° (from feather) |
| Yaw | 0° (upwind, zero yaw — S sequence) |
| Wind tunnel | NASA-Ames 24.4 m × 36.6 m (80' × 120') |
| Flow speed uniformity | ±0.25%, turbulence intensity ≤ 0.5% |
| Blockage | < 1% (negligible) |
| Instrumented span stations | r/R = 0.30, 0.47, 0.63, 0.80, 0.95 |
| Measurements | Shaft torque, root flap bending moment, Cn, Ct, Cm, Cp at 5 span stations |

---

## Key experimental result: Low-speed shaft torque vs wind speed

From Figure 11 of Song & Perot (2015) and Figure 8 of TP-500-29494.
Configuration: upwind, 0° yaw, 3° tip pitch, 72 rpm.

| V∞ (m/s) | Experimental LSST (N·m) | Power = τ×ω (kW) | Flow regime |
|----------|------------------------|------------------|-------------|
| 5        | ~130                   | ~0.98            | Attached, pre-stall |
| 7        | ~420                   | ~3.17            | Mild separation near root |
| 10       | ~1 490                 | ~11.2            | Stall onset (root stalling) |
| 13       | ~1 620                 | ~12.2            | Partial stall |
| 15       | ~1 490                 | ~11.2            | Deep stall — torque plateaus |
| 18       | ~1 400                 | ~10.6            | Deep stall |
| 21       | ~1 370                 | ~10.3            | Deep stall (entire blade separated) |

ω = 7.540 rad/s. Values above are read from published figures; use the PDF directly for precise numbers.

**Stall onset:** blades begin separating near root (r/R ≈ 0.30) at V∞ ≈ 10 m/s.
At V∞ ≥ 13 m/s the entire blade is substantially stalled.

---

## What to compare in CFD

### Integral (global) quantities
1. **Low-speed shaft torque** vs V∞ — primary validation metric
2. **Root flap bending moment** vs V∞

### Distributed quantities (pressure taps at 5 stations)
3. **Cn (normal force coefficient)** vs V∞ at r/R = 0.30, 0.47, 0.63, 0.80, 0.95
4. **Ct (tangential force coefficient)** — directly proportional to local torque contribution
5. **Pressure coefficient Cp** distribution around chord at each span station

### Turbulence model sensitivity
- 5 m/s: all models should agree — attached flow, easy case
- 10 m/s: models diverge near root where separation starts
- 13–21 m/s: models significantly underpredict torque (deep stall) — k-ω SST does best of the RANS family

---

## Song & Perot (2015) OpenFOAM setup summary

| Item | Value |
|------|-------|
| Solver | `pimpleDyMFoam` (OpenFOAM-1.6-ext) |
| Interface | GGI (Generalised Grid Interface) — equivalent to AMI in modern OF |
| Turbulence model | Spalart-Allmaras (no wall functions, integrated to wall) |
| Mesh | Unstructured, 10 million cells |
| y⁺ target | y⁺ ≤ 5 (first cell in laminar sublayer) |
| First prism layer height | 5 × 10⁻⁵ m |
| Prism growth rate | 15% per layer |
| Wind tunnel walls | Slip BC (tunnel BL not resolved) |
| Inlet BC | fixedValue velocity, zeroGradient pressure |
| Outlet BC | zeroGradient velocity, fixedValue pressure (0) |
| Blade BC | movingWallVelocity (no-slip in rotating frame) |
| ν̃ (SA variable) inlet | 1.85 × 10⁻⁴ m²/s |
| Compute time | ~48 h/revolution on 128 cores (10M cell mesh) |

**Conclusions from Song & Perot:**
- Good agreement at V∞ ≤ 7 m/s (attached flow)
- Agreement degrades above 10 m/s — Spalart-Allmaras overpredicts stall severity → underpredicts post-stall torque
- 3D effects (spanwise flow under stall) are significant and not captured by 2D models

---

## Turbulence model comparison expectations for your study

| Model | Expected behaviour on Phase VI |
|-------|-------------------------------|
| Laminar | Good at 5 m/s, fails above ~8 m/s (physically wrong) |
| k-ε (standard) | Overdiffusive, delays separation onset, overpredicts torque in stall |
| k-ω SST | Best RANS for this case — handles adverse pressure gradient, predicts stall onset most accurately |
| Spalart-Allmaras | Good for attached flow, underpredicts torque post-stall (too much stall) |

**Portfolio message:** k-ω SST is recommended for rotating blade flows. This is the quantitative justification.

---

## Spanwise instrumentation locations

| r/R | r (m) | Used for |
|-----|-------|---------|
| 0.30 | 1.509 | Root — stalls first, highest 3D effects |
| 0.47 | 2.365 | Mid-inboard |
| 0.63 | 3.172 | Mid-span |
| 0.80 | 4.027 | **80% chord fixed at 0.457 m** — key design constraint |
| 0.95 | 4.782 | Near tip |

---

## Blind comparison findings (TP-500-29494)

The original 2001 blind comparison (30 experts, 19 codes) showed:
- At no-yaw, no-stall: power predictions ranged **25% to 175%** of measured
- At high wind (stall): power predictions ranged **30% to 275%** of measured
- Blade bending force: **85–150%** of measured (pre-stall), **60–125%** (stall)

This scatter is why Phase VI is such a strong benchmark — it reveals the limits of every model.
