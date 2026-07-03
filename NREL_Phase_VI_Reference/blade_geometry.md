# NREL Phase VI — Blade Geometry & Reference Data

Source: Giguère & Selig, NREL/SR-500-26173, April 1999
"Design of a Tapered and Twisted Blade for the NREL Combined Experiment Rotor"

---

## Rotor specification

| Parameter | Value |
|-----------|-------|
| Rotor diameter | 10.058 m (R = 5.03 m baseline) |
| Number of blades | 3 (baseline) / 2 (extended) |
| Rated power | 20 kW |
| Rotational speed | 72 rpm (baseline) |
| Cone angle | 3.4° |
| Configuration | Stall-regulated, downwind HAWT |
| Airfoil | NREL S809 (root to tip) |
| Pitch reference | 75% span station, pitch axis at 30% chord |
| Recommended pitch | 5° (both 2- and 3-bladed) |

---

## Chord and twist distribution (Appendix A)

Baseline blade (R = 5.03 m). Pitch defined at 75% span.

| r (m)  | r/R   | chord (m) | twist (deg) | notes |
|--------|-------|-----------|-------------|-------|
| 0.000  | 0.000 | hub dia.  | 0.00        | hub   |
| 0.724  | 0.144 | hub dia.  | 0.00        | hub ends here |
| 0.838  | 0.167 | computed¹ | 30.00       | transition start |
| 0.968  | 0.192 | computed¹ | 27.59       | |
| 1.258  | 0.250 | 0.737     | 20.05       | max chord |
| 1.522  | 0.302 | 0.710     | 14.04       | |
| 1.798  | 0.357 | 0.682     | 9.67        | |
| 2.075  | 0.412 | 0.654     | 6.75        | |
| 2.352  | 0.468 | 0.626     | 4.84        | |
| 2.628  | 0.522 | 0.598     | 3.48        | |
| 2.905  | 0.578 | 0.570     | 2.40        | |
| 3.181  | 0.633 | 0.542     | 1.51        | |
| 3.458  | 0.688 | 0.514     | 0.76        | |
| 3.735  | 0.743 | 0.486     | 0.09        | |
| 3.772  | 0.750 | 0.483     | 0.00        | **pitch reference (75% span)** |
| 4.011  | 0.798 | 0.459     | -0.55       | **457 mm chord at 80% span** |
| 4.288  | 0.853 | 0.431     | -1.11       | |
| 4.565  | 0.908 | 0.403     | -1.55       | |
| 4.841  | 0.963 | 0.375     | -1.84       | |
| 5.030  | 1.000 | 0.356     | -2.00       | **tip** |

¹ Chord in transition zone (28.5–49.5 in. from hub):
`c [in] = [(29 − HD)/21] × r + 2.357 × HD − 39.357`
where HD = hub diameter in inches, r = radial position in inches.

Extended blade tip (for 2-bladed rotor, span 5.533 m):

| r (m)  | r/R   | chord (m) | twist (deg) |
|--------|-------|-----------|-------------|
| 5.118  | 1.018 | 0.347     | -2.08       |
| 5.395  | 1.073 | 0.319     | -2.36       |
| 5.533  | 1.100 | 0.305     | -2.50       |

---

## CFD simulation targets

The standard Phase VI validation conditions (from Hand et al. NREL/TP-500-29494):

| Wind speed (m/s) | Operating regime |
|-----------------|-----------------|
| 5               | Attached flow, pre-stall |
| 7               | Moderate AoA |
| 10              | Near stall |
| 13              | Post stall (most challenging for RANS) |
| 15              | Deep stall |
| 18              | Deep stall |
| 21              | Deep stall |

Rotor speed: 72 rpm (tip speed ratio λ = ω R / V∞)

| V∞ (m/s) | λ = ωR/V∞ |
|----------|-----------|
| 5        | 7.54      |
| 7        | 5.39      |
| 10       | 3.77      |
| 13       | 2.90      |
| 15       | 2.52      |
| 18       | 2.10      |
| 21       | 1.80      |

ω = 72 rpm × 2π/60 = 7.54 rad/s

---

## BEM performance predictions (Appendix B — 3-bladed, 72 rpm, 5° pitch)

These are BEM model predictions from SR-500-26173, NOT experimental measurements.
For CFD validation against experiment, use data from **NREL/TP-500-29494** (Hand et al. 2001).

| V∞ (m/s) | Power (kW) | Thrust (N) |
|----------|-----------|-----------|
| 4.5      | 1.26      | 544.3     |
| 5.4      | 2.63      | 817.6     |
| 6.3      | 4.47      | 1114.8    |
| 6.7      | 5.58      | 1272.1    |
| 7.2      | 6.83      | 1433.9    |
| 8.0      | 9.63      | 1750.4    |
| 8.9      | 12.20     | 1974.1    |
| 9.4      | 13.21     | 2052.3    |
| 9.8      | 14.18     | 2123.2    |
| 10.7     | 15.76     | 2252.1    |
| 11.2     | 16.48     | 2316.5    |
| 13.0     | 18.48     | 2459.7    |
| 15.2     | 19.31     | 2624.0    |
| 17.9     | 19.78     | 2895.2    |

---

## Power coefficient vs tip-speed ratio (Appendix B — 5° pitch, baseline R = 5.03 m)

Peak Cp ≈ 0.483 at λ ≈ 5.29

| λ     | Cp (5° pitch) |
|-------|--------------|
| 10.58 | 0.132        |
| 9.41  | 0.270        |
| 8.47  | 0.347        |
| 7.06  | 0.418        |
| 6.05  | 0.447        |
| 5.64  | 0.454        |
| 5.29  | 0.458        |
| 4.98  | 0.458        |
| 4.70  | 0.453        |
| 4.46  | 0.441        |
| 4.03  | 0.392        |
| 3.68  | 0.339        |
| 3.26  | 0.267        |
| 2.92  | 0.208        |
| 2.57  | 0.147        |

---

## Experimental reference (for CFD validation)

The experimental power and thrust measurements that CFD results should be compared against:

**Hand, M.M. et al., "Unsteady Aerodynamics Experiment Phase VI: Wind Tunnel Test Configurations
and Available Data Campaigns," NREL/TP-500-29494, December 2001.**

Key measured quantities at S (upwind, no yaw, full-span pitch) sequence:
- Low-speed shaft torque → mechanical power
- Rotor thrust (blade root bending moments)
- Pressure tap data at 5 spanwise stations: r/R = 0.30, 0.47, 0.63, 0.80, 0.95
- Section normal and tangential force coefficients

Blade instrumentation: one instrumented blade with pressure taps at 5 stations.

---

## S809 airfoil

Designed by Somers (NREL/SR-440-6918).
- Thickness/chord: 21%
- Design Cl: ~1.0 at Re ~1×10⁶
- Clean surface tested at Delft wind tunnel (Re = 1×10⁶ to 3×10⁶)
- Coordinates: Somers 1997, also available from UIUC Airfoil Database

Key 2D aerodynamic behaviour:
- Stall at α ≈ 14° (clean, Re = 1×10⁶) — earlier than NACA 4-digit equivalents
- Gentle stall characteristic (designed for stall-regulated turbines)
- Max Cl/Cd in attached regime at α ≈ 8°

---

## OpenFOAM case parameters

For a single-blade periodic sector simulation:

| Parameter | Value |
|-----------|-------|
| Solver | `pimpleDyMFoam` (AMI) or `pimpleFoam` (MRF) |
| Periodicity | 120° (1/3 rotor for 3-bladed) |
| Rotation | 72 rpm = 7.540 rad/s about −z axis |
| Freestream | V∞ = 7–25 m/s, axial (−x direction) |
| Reference density | 1.225 kg/m³ |
| Reference pressure | 101 325 Pa |
| Reynolds number at 75% span | Re = ρ V_rel c / μ ≈ 0.5–1.5 × 10⁶ |
| V_rel at 75% span (V=10 m/s) | √(10² + (0.75×5.03×7.54)²) ≈ 30 m/s |

Chord at 75% span = 0.483 m → Re ≈ 0.483 × 30 × 1.225 / 1.789e-5 ≈ 9.9 × 10⁵

Turbulence models to compare:
1. Laminar
2. k-ε (standard)  
3. k-ω SST ← expected best for this case (adverse pressure gradient on suction side)
