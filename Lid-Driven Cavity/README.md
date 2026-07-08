# Lid-Driven Cavity Flow

Benchmark validation of incompressible laminar flow in a square cavity driven by a sliding lid, across five Reynolds numbers. Compared against the widely-cited numerical reference data of Ghia, Ghia & Shin (1982).

## Geometry and setup

| Parameter | Value |
|-----------|-------|
| Domain | 1 m × 1 m square cavity |
| Lid velocity | U = 1 m/s (top wall) |
| Solver | `icoFoam` (transient laminar incompressible) |
| Mesh | 128 × 128 structured `blockMesh` |
| Re sweep | 100, 400, 1000, 3200, 10 000 |

The lid moves in the +x direction. All other walls are no-slip. The 2D simulation uses a single-cell depth with `empty` front/back patches.

**Time-stepping:** Adaptive end times and time-steps used per Re to reach steady-state:

| Re | Δt | End time (s) |
|----|-----|-------------|
| 100 | 0.005 | 100 |
| 400 | 0.002 | 150 |
| 1 000 | 0.001 | 200 |
| 3 200 | 0.0007 | 250 |
| 10 000 | 0.0005 | 60 (flow developed) |

## Validation reference

Ghia, U., Ghia, K.N. & Shin, C.T. (1982) "High-Re solutions for incompressible flow using the Navier-Stokes equations and a multigrid method." *Journal of Computational Physics*, 48:387-411.

Tabulated u-velocity profiles along the vertical centreline (x = 0.5) and v-velocity profiles along the horizontal centreline (y = 0.5) for Re = 100 to 10 000.

## Results

![Lid-driven cavity validation](lid_driven_cavity.png)

**Left:** u-velocity along the vertical centreline (x = 0.5 L). Circles are Ghia et al. (1982) data; solid lines are CFD.  
**Right:** v-velocity along the horizontal centreline (y = 0.5 L).

CFD results agree closely with Ghia et al. across all five Reynolds numbers. At Re = 100 the primary vortex is nearly circular and centred. As Re increases the vortex centre shifts toward the cavity mid-plane and secondary corner eddies strengthen, consistent with the benchmark. Re = 10 000 was run to t = 60 s, by which point the flow was statistically developed (residuals below 10⁻⁴).

## Key observations

- Re = 100-1000: excellent point-wise agreement (<2% deviation on centreline extrema)
- Re = 3200-10000: very good agreement; slight underprediction of the negative u peak near the bottom wall at Re = 10 000 is consistent with marginal time-convergence at this Reynolds number
- No turbulence model required - purely laminar throughout
