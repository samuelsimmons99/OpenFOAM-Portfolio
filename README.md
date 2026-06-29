# OpenFOAM CFD Portfolio
**Samuel Simmons · Thermal Simulation Engineer**

A collection of CFD simulations built with OpenFOAM, demonstrating thermal-fluid simulation capability across the full workflow — from CAD geometry and mesh generation through parallel computation and post-processing.

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
Parametric study of 2D flow past a circular cylinder across six Reynolds numbers (3 to 5×10⁶), from creeping Stokes flow through laminar vortex shedding to turbulent (`kOmegaSST`) regimes. Background mesh + `snappyHexMesh` with a built-in cylinder geometry, run with `pimpleFoam` and post-processed via `forceCoeffs` for drag/lift coefficients.

**Tools:** OpenFOAM v2012 · snappyHexMesh · ParaView · OpenMPI

---

### Heatsink Parametric Study *(in progress)*
Parametric study of fin array heatsink geometries with fan curve modelling. Coming soon.

---

## References
The `3 Weeks Series` folder contains study materials and reference cases used to learn OpenFOAM.

---

## Contact
[LinkedIn](https://www.linkedin.com/in/samuelsimmons99) · [GitHub](https://github.com/samuelsimmons99)
