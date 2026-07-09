# Vortex Shedding — Strouhal Number Validation

Validation of laminar vortex shedding frequency against the Williamson (1988) correlation at Re = 100.

## Physics

Flow past a circular cylinder at Re = 100 (laminar, 2-D) produces a periodic von Kármán vortex street. The shedding frequency is characterised by the Strouhal number:

St = f D / U∞

where *f* is the shedding frequency, *D* = 1 m is the cylinder diameter, and *U∞* = 1 m/s is the freestream velocity. The Williamson (1988) correlation gives:

St = 0.2663 − 1.0166 / √Re → **St ≈ 0.165 at Re = 100**

## Setup

| Parameter | Value |
|-----------|-------|
| Solver | `pimpleFoam` (transient incompressible) |
| Mesh | 4-block O-mesh (blockMesh), 12,000 cells |
| Domain | Circular, R_out = 20D (40 radii) |
| Re | 100 (U = 1 m/s, D = 1 m, ν = 0.01 m²/s) |
| End time | 80 s (~13 shedding periods) |
| Time stepping | Adaptive, max Co = 0.5 |
| Turbulence | Laminar |
| IC | Uniform (1, 0.001, 0) m/s — 0.1% cross-flow perturbation to trigger shedding |

Frequency extracted via FFT of the lift coefficient C_L(t), using only t > 36 s (latter 55% of run) to exclude transient startup.

## Results

![Strouhal validation](strouhal_validation.png)

The simulation reproduces the Williamson (1988) Strouhal number to within measurement uncertainty, confirming that the O-mesh topology and PIMPLE time integration correctly capture laminar cylinder shedding physics.

## References

- Williamson, C. H. K. (1988). Defining a universal and continuous Strouhal–Reynolds number relationship for the laminar vortex shedding of a circular cylinder. *Physics of Fluids*, **31**(10), 2742–2744.
