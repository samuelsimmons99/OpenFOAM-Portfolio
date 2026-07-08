# Magnus Effect - Rotating Cylinder Aerodynamics

Validation of the Magnus effect on a 2D rotating cylinder across two Reynolds number regimes: laminar (Re = 200) and turbulent (Re = 1x10^5). Results compared against published DNS/experimental benchmarks.

## Physical setup

A cylinder of diameter D = 1 m rotates at angular velocity omega in a uniform free-stream of velocity U_inf. The spin ratio alpha = omega*D/(2*U_inf) is swept from 0 to 5 to capture the full range of Magnus lift behaviour.

| Parameter | Laminar | Turbulent |
|-----------|---------|-----------|
| Re = U_inf*D/nu | 200 | 1x10^5 |
| Solver | `pimpleFoam` | `pimpleFoam` |
| Turbulence | Laminar | k-omega SST |
| alpha range | 0 - 5 | 0 - 4 |
| Domain | 40D x 40D | 40D x 40D |
| Mesh | ~18 000 cells | ~18 000 cells |

The rotating wall boundary condition uses `rotatingWallVelocity` with the cylinder axis along y. Lift and drag are extracted via `forceCoeffs`. All simulations were run to statistical steady state (t = 200 s for laminar, t = 100 s for turbulent).

## Validation references

**Laminar Re = 200:** Mittal, R. & Kumar, B. (2003) "Flow past a rotating cylinder", *Journal of Fluid Mechanics*, 476:303-334.

**Turbulent Re = 1x10^5:** Tokumaru, P.T. & Dimotakis, P.E. (1993) "The lift of a cylinder executing rotary motions in a uniform flow", *Journal of Fluid Mechanics*, 255:1-10.

## Results

![Magnus polar curves](magnus_polar.png)

**Left (Re = 200):** Lift coefficient vs spin ratio compared with Mittal & Kumar (2003). CFD reproduces the linear Cl increase for alpha < 2 and the progressive steepening at higher spin ratios. Drag shows a non-monotonic response with a local minimum near alpha = 2, consistent with the DNS data.

**Right (Re = 1x10^5):** Lift coefficient vs spin ratio compared with Tokumaru & Dimotakis (1993). k-omega SST captures the qualitative Magnus lift trend; quantitative agreement degrades at high alpha where vortex shedding interacts with the rotation-induced asymmetric flow.

## Key observations

- Laminar regime shows excellent agreement with Mittal & Kumar across all spin ratios
- Magnus lift is strongly nonlinear at high spin ratios (alpha > 3) in both regimes
- Turbulent boundary layer delays separation, producing lower Cl for the same alpha compared with laminar
- At alpha = 0, Cd agrees with the expected values for a stationary cylinder (Cd ~ 1.0 at Re = 200)

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
