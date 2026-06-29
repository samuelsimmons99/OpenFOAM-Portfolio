# Flow Past a Circular Cylinder — Reynolds Number Sweep

A parametric study of 2D flow over a circular cylinder (diameter = 1 m) across six Reynolds numbers spanning creeping flow through to the turbulent regime, using `pimpleFoam` (laminar) and `pimpleFoam` + `kOmegaSST` (turbulent).

| Case | Re | Inlet U (m/s) | Model | Cd | Cl | Regime |
|---|---|---|---|---|---|---|
| Re_3 | 3 | 4.5e-05 | laminar | 47.4 | ~0 | Creeping (Stokes) flow |
| Re_40 | 40 | 6.0e-04 | laminar | 3.64 | ~0 | Steady, attached recirculation bubble |
| Re_100 | 100 | 1.5e-03 | laminar | 1.63 | ~0 | Unsteady (von Kármán shedding onset) |
| Re_30000 | 3.0e4 | 0.45 | kOmegaSST | 1.20 | ~0.2 (oscillating) | Subcritical turbulent shedding |
| Re_800000 | 8.0e5 | 12 | kOmegaSST | — | — | Supercritical turbulent |
| Re_5000000 | 5.0e6 | 75 | kOmegaSST | — | — | Transcritical turbulent |

Cd/Cl are taken from the final logged `forceCoeffs` sample of each run; see `logs/log.pimpleFoam` in each case for the full time history. Re_800000/Re_5000000 take substantially longer to solve due to the smaller Courant-limited timestep at higher inlet velocity — drop in final results once available.

## Domain & mesh

All cases share the same geometry and mesh recipe:
- Domain: a `[-10,20] x [-10,10] x [0,1]` m box, cylinder of radius 0.5 m centred at the origin.
- `blockMesh` generates a uniform background mesh.
- `snappyHexMesh` cuts the cylinder out of the background mesh using a built-in `searchableCylinder` (no STL needed) with surface + distance-based refinement near the wall and wake.
- `top`/`bottom` are `symmetryPlane`, `inlet`/`outlet` are `patch`, `front`/`back` are `empty` (2D case), `cylinder` is `wall`.

This mesh approach was chosen after an earlier hand-built O-grid `blockMeshDict` (multiple blocks stitched directly with explicit vertices) turned out to produce a **topologically disconnected mesh** — `checkMesh` reported 3 separate, unconnected cell regions due to non-conformal seams between the inner O-grid blocks and the far-field blocks. Rebuilding around `snappyHexMesh` removed that whole class of bug.

## Running a case yourself

Each `Re_*` folder is a self-contained OpenFOAM case with everything needed to regenerate the mesh and resolve the flow from scratch — only the generated mesh (`constant/polyMesh`), the parallel decomposition (`processor*`), and intermediate time directories have been omitted to keep the repo lightweight (the final time directory is kept as a sample result).

```bash
cd "Re_100"
./Allrun
# equivalent to:
#   blockMesh
#   snappyHexMesh -overwrite
#   checkMesh
#   decomposePar
#   mpirun -np 4 pimpleFoam -parallel
#   reconstructPar
```

Turbulent cases (`Re_30000`, `Re_800000`, `Re_5000000`) use `kOmegaSST` and require a `wallDist` entry in `system/fvSchemes` (included) — this is a common gotcha when adapting `fvSchemes` from a laminar case.

**Tools:** OpenFOAM v2012 · snappyHexMesh · ParaView · OpenMPI
