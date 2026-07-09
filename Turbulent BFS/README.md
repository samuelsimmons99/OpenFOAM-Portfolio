# Turbulent Backward-Facing Step: RANS Model Comparison

Comparison of three RANS turbulence models against the Le, Moin & Kim (1997) DNS benchmark at Re_h = 5100.

## Physics

Turbulent flow over a backward-facing step (ER = 2) produces a separated shear layer and a downstream recirculation bubble. The reattachment length x_r/h is the canonical metric for separated-flow turbulence modelling. Because all three RANS models use different closure assumptions for the Reynolds stress tensor, they predict different bubble lengths — making this a decisive test of model behaviour in adverse pressure gradient, separated-flow conditions.

## Setup

| Parameter | Value |
|-----------|-------|
| Solver | `simpleFoam` (steady RANS) |
| Mesh | 3-block blockMesh, 8,500 cells (Δx = 1 mm, Δy = 1 mm) |
| Expansion ratio | ER = 2 (step height h = inlet channel height = 0.01 m) |
| Reynolds number | Re_h = U h / ν = 5100 |
| Inlet | Uniform U = 1 m/s, I = 5%, L = 0.0014 m |
| y+ (near wall) | ~32 (wall-function regime) |
| Turbulence models | k-ε (standard), k-ω SST, Spalart-Allmaras |

Wall-function boundary conditions (kqRWallFunction, epsilonWallFunction, omegaWallFunction, nutkWallFunction) are applied at all solid surfaces. The k-ω SST uses the automatic near-wall blending formulation; Spalart-Allmaras uses zero nuTilda at walls (equivalent to low-Re treatment).

## Results

![Turbulent BFS validation](turbulent_bfs_validation.png)

### Reattachment length

| Model | x_r/h | Error vs DNS |
|-------|-------|-------------|
| k-ε (standard) | 6.01 | -4.3% |
| k-ω SST | 7.07 | +12.5% |
| Spalart-Allmaras | 6.65 | +5.9% |
| Le et al. (1997) DNS | 6.28 | reference |

### Physical interpretation

**k-ε (standard):** Under-predicts reattachment (-4.3%). The standard k-ε model over-estimates turbulent diffusion in the shear layer separating from the step corner. Excessive mixing energises the recirculating flow prematurely, shortening the bubble. This is the well-known limitation of isotropic eddy-viscosity models in separated flows with strong streamline curvature.

**Spalart-Allmaras:** +5.9% over-prediction. SA uses a single transported quantity (modified viscosity nuTilda) and is calibrated for attached boundary layer flows. It performs better than standard k-ε here because it avoids the stiff two-equation coupling near the reattachment point, but still over-diffuses slightly without explicit shear-stress limitation.

**k-ω SST:** +12.5% over-prediction. Somewhat counter-intuitively, SST produces the longest bubble. The SST limiter suppresses the turbulent viscosity in the free shear layer (where the stress-intensity ratio exceeds the SST bound), which reduces mixing and allows the recirculation to persist further downstream. This known behaviour was reported by Menter et al. (2003): SST can over-predict x_r in strong separations when the inlet has not developed a full turbulent boundary layer before the step.

**Key takeaway:** For this geometry, all three models are within 13% of the DNS — acceptable engineering accuracy — but each errs in opposite directions. k-ε is the most computationally robust but least accurate; SST gives the longest bubble, consistent with its shear-stress limiting; SA is intermediate. For flows where the exact reattachment location is design-critical, LES or hybrid RANS/LES is required.

## References

- Le, H., Moin, P., & Kim, J. (1997). Direct numerical simulation of turbulent flow over a backward-facing step. *Journal of Fluid Mechanics*, **330**, 349-374.
- Menter, F. R., Kuntz, M., & Langtry, R. (2003). Ten years of industrial experience with the SST turbulence model. *Turbulence, Heat and Mass Transfer*, **4**, 625-632.
- Celik, I. B., Ghia, U., Roache, P. J., et al. (2008). Procedure for estimation and reporting of uncertainty due to discretisation in CFD applications. *Journal of Fluids Engineering*, **130**(7), 078001.
