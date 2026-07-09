# Magnus Effect - Rotating Cylinder Aerodynamics

Validation of the Magnus effect on a 2D rotating cylinder across two Reynolds number regimes: laminar (Re = 200) and turbulent (Re = 1x10^5). Results compared against published DNS/experimental benchmarks.

## Physical setup

A cylinder of diameter D = 1 m rotates at angular velocity omega in a uniform free-stream of velocity U_inf. The spin ratio alpha = omega*D/(2*U_inf) is swept from 0 to 5 to capture the full range of Magnus lift behaviour.

| Parameter | Laminar | Turbulent |
|-----------|---------|-----------|
| Re = U_inf*D/nu | 200 | 1x10^5 |
| Solver | `simpleFoam` | `simpleFoam` |
| Turbulence | Laminar | k-omega SST |
| alpha range | 0 - 5 | 0 - 4 |
| Domain | 40D x 40D | 40D x 40D |
| Mesh | 16k/24k cells (coarse/fine O-mesh) | 16k cells (O-mesh) |

The rotating wall boundary condition uses `rotatingWallVelocity` with the cylinder axis along y. Lift and drag are extracted via `forceCoeffs`. All simulations were run to statistical steady state (t = 200 s for laminar, t = 100 s for turbulent).

## Validation references

**Laminar Re = 200:** Mittal, R. & Kumar, B. (2003) "Flow past a rotating cylinder", *Journal of Fluid Mechanics*, 476:303-334.

**Turbulent Re = 1x10^5:** Tokumaru, P.T. & Dimotakis, P.E. (1993) "The lift of a cylinder executing rotary motions in a uniform flow", *Journal of Fluid Mechanics*, 255:1-10.

## Results

![Magnus polar curves](magnus_polar.png)

**Left (Re = 200):** Lift coefficient vs spin ratio compared with Mittal & Kumar (2003). CFD reproduces the linear Cl increase for alpha ≤ 2 well (errors < 10%). At alpha ≥ 3, the steady solver (simpleFoam) significantly overpredicts Cl because vortex shedding from the cylinder wake (captured in M&K's DNS) is inherently unsteady. A transient solver would require resolving quasi-periodic shedding cycles (T~25 s at Re=200) at dt~1e-4 s, making the computation impractical on available hardware.

**Right (Re = 1x10^5):** Lift coefficient vs spin ratio compared with Tokumaru & Dimotakis (1993). k-omega SST captures the qualitative Magnus lift trend; quantitative agreement degrades at high alpha where vortex shedding interacts with the rotation-induced asymmetric flow.

## Key observations

- Alpha ≤ 2 (Re=200): Cl within 5–10% of Mittal & Kumar (2003) DNS; good for 24k-cell 2D mesh
- Alpha ≥ 3 (Re=200): steady solver overpredicts because flow is unsteady (quasi-periodic vortex shedding). Mesh refinement from dr1=9mm→0.3mm reduces error (alpha=5: Cl=27.2→20.8) but cannot fix the fundamental physics limitation of a steady solver
- Magnus lift is strongly nonlinear at high spin ratios (alpha > 3) in both regimes
- Turbulent (Re=1e5, k-ω SST): good qualitative trend; absolute agreement with Tokumaru & Dimotakis limited by 2D assumption (experiment is 3D)
- At alpha = 0, Cd ≈ 1.35 agrees with expected stationary cylinder value at Re = 200

## Boundary conditions

| Patch | Condition |
|-------|-----------|
| Cylinder wall | `rotatingWallVelocity` (omega set per alpha) |
| Inlet | `fixedValue` uniform free-stream |
| Outlet | `inletOutlet` / zero-gradient p |
| Top/Bottom | `slip` |

## Running the case

```bash
# Set spin ratio in 0/U (rotatingWallVelocity omega value) and run:
pimpleFoam
postProcess -func forceCoeffs
```
