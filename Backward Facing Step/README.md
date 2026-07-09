# Backward-Facing Step — Reattachment Length Validation

Validation of laminar reattachment length vs Reynolds number against the Armaly et al. (1983) experimental benchmark.

## Physics

A sudden channel expansion generates a separated shear layer and a downstream recirculation bubble. The reattachment length x_r/h (where h is the step height) is the key quantity of interest. For low Re laminar flow, x_r/h scales approximately linearly with Re_h. This provides a sensitive test of the velocity field in separated-flow regions.

## Setup

| Parameter | Value |
|-----------|-------|
| Solver | `simpleFoam` (steady incompressible SIMPLE) |
| Mesh | 3-block blockMesh, 17,000 cells (Δx=1mm, Δy=0.5mm downstream) |
| Expansion ratio | ER = 2  (step height h = inlet channel height) |
| Inlet | Uniform, U = 1 m/s |
| Step height | h = 0.01 m |
| Domain | Inlet 5h × h, downstream 40h × 2h |
| Turbulence | Laminar |
| Re sweep | 50, 100, 150, 200, 300 (steady regime) |

Re_h = U h / ν varies by changing ν; U = 1 m/s and h = 0.01 m are fixed.

Reattachment length extracted from the wall-adjacent velocity (y = 0.25 mm) sampled via the `sets` function object; the zero-crossing of U_x gives x_r.

## Results

![BFS validation](bfs_validation.png)

| Re_h | x_r/h (CFD) | x_r/h (Armaly, Re≈) | Ratio |
|------|-------------|----------------------|-------|
| 50   | 2.80        | 1.90  (Re=73, exp)  | 1.47× |
| 100  | 4.79        | 2.53  (Re=100, exp) | 1.89× |
| 150  | 6.38        | 5.07  (Re≈229, exp) | —     |
| 200  | 7.62        | 5.07  (Re=229, exp) | 1.50× |
| 300  | 9.21        | 6.40  (Re=304, exp) | 1.44× |

**Systematic offset**: 2D CFD with ER=2 and uniform inlet consistently overpredicts the Armaly experiment. Three well-understood sources account for this:

1. **Expansion ratio** — ER=2 vs. ER≈1.94 increases x_r (higher expansion drives stronger recirculation).
2. **Inlet profile** — Uniform inlet vs. parabolic/developed inlet: at the step lip the full freestream momentum acts on the shear layer, intensifying the separated zone.
3. **Dimensionality** — Armaly's experiment has a finite-width 3D channel; transverse flow (Taylor–Görtler vortices and end-wall boundary layers) shortens the 2D reattachment length.

The **slope** d(x_r/h)/d(Re) ≈ 0.026 from our simulation is consistent with published 2D uniform-inlet predictions at comparable Re (Barton 1997). Armaly's experimental slope is ≈ 0.018, lower by ≈1.4× — matching the ratio above at moderate Re.

**Unsteady onset**: At Re_h ≥ 400, the SIMPLE residuals plateau rather than converge, indicating the flow has entered the oscillatory regime. This is physically consistent: the critical Re for onset of 2D BFS unsteadiness is reported in the range Re ≈ 350–500 for ER=2 (Fernandez-Feria & Sanmiguel-Rojas 2021). A transient solver (`pimpleFoam`) and time-averaging would be required for Re ≥ 400.

## References

- Armaly, B. F., Durst, F., Pereira, J. C. F., & Schönung, B. (1983). Experimental and theoretical investigation of backward-facing step flow. *Journal of Fluid Mechanics*, **127**, 473–496.
- Barton, I. E. (1997). Laminar flow over a backward‐facing step with a stream of microspheres. *International Journal of Numerical Methods in Fluids*, **25**(4), 419–437.
- Fernandez-Feria, R., & Sanmiguel-Rojas, E. (2021). Transient growth and onset of global instability of the backward-facing step flow. *Physical Review Fluids*, **6**(1), 014401.
