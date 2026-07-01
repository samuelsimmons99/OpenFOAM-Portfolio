# OpenFOAM CFD Portfolio
**Samuel Simmons · Thermal Simulation Engineer**

A collection of CFD simulations built with OpenFOAM, demonstrating thermal-fluid simulation capability across the full workflow from CAD geometry and mesh generation through parallel computation and post-processing.

---

## Projects

### [2U Server Conjugate Heat Transfer Simulation](./2U%20Server%20Simulation/)
Steady-state conjugate heat transfer simulation of a 2U rack-mount server chassis using `chtMultiRegionSimpleFoam`. Couples turbulent forced convection in the air domain with heat conduction through CPU silicon, aluminium heatsink, and steel front panel. Predicts 96°C CPU junction temperature under 150 W dissipation across a 1.1-million-cell multi-region mesh run on 16 MPI cores.

**Tools:** OpenFOAM v2012 · Ansys SpaceClaim · snappyHexMesh · ParaView · Python · OpenMPI

---

### [Smoking Pipe Tutorial](./Smoking%20Pipe%20Tutorial/)
Internal pipe flow simulation of a smoking pipe geometry using `simpleFoam` (steady-state) and `pimpleFoam` (transient). Covers the full workflow from STL geometry preparation through snappyHexMesh meshing, solver configuration, and ParaView post-processing.

**Tools:** OpenFOAM · snappyHexMesh · ParaView · Salome

---

### [Cylinder Flow Reynolds Number Sweep](./Cylinder%20Flow/)
Parametric study of 2D flow past a circular cylinder across five Reynolds numbers (Re = 3 to 8×10⁵), from creeping Stokes flow through laminar vortex shedding to turbulent (`kOmegaSST`) supercritical shedding. Background mesh + `snappyHexMesh` with a built-in cylinder geometry, run with `pimpleFoam` and post-processed via `forceCoeffs` for drag/lift coefficients across all regimes.

**Tools:** OpenFOAM v2012 · snappyHexMesh · ParaView · OpenMPI

---

### [Rocket Nozzle Simulation](./Nozzle%20Simulation/)
Compressible flow through a conical De Laval nozzle (area ratio 8:1), modelling LOX/kerosene combustion products as a perfect gas at T0=3000 K and p0=3 MPa. `rhoCentralFoam` density-based solver on a 5-degree axisymmetric wedge mesh captures the transonic throat, supersonic expansion to Mach 3.22, and the exit expansion fan. A reacting LOX/kerosene case with full combustion chemistry is in progress.

**Tools:** OpenFOAM v2012 · rhoCentralFoam · blockMesh · ParaView · Python

---

### [Parametric Heatsink CHT Simulation](./Parametric%20Heatsink%20Simulation/)
Steady-state conjugate heat transfer simulation of a CPU + fin-array heatsink inside a fan-driven duct using `foamMultiRun` (3-region: air, aluminium heatsink, silicon CPU). The mesh is generated parametrically from a Python script so fin pitch can be swept without rebuilding geometry. A 3-point pitch sweep (3 mm / 4 mm / 5 mm) was completed, reducing peak CPU temperature from 343.90 K (5 mm, 15 fins) to 336.96 K (3 mm, 24 fins) - a 6.94 K improvement. Fan operating points extracted from converged flow fields and plotted against the published Delta FFB0812VH fan curve. Baseline 5 mm case cross-verified between serial and 8-core parallel runs (agreement to 0.001 K).

**Tools:** OpenFOAM 13 · foamMultiRun · blockMesh · Python · OpenMPI · Ubuntu WSL2

---

## References
The `3 Weeks Series` folder contains study materials and reference cases used to learn OpenFOAM.

---

## Contact
[LinkedIn](https://www.linkedin.com/in/samuelsimmons99) · [GitHub](https://github.com/samuelsimmons99)
