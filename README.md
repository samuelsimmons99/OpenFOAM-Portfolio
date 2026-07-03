# OpenFOAM CFD Portfolio
**Samuel Simmons · Thermal Engineer**

Six simulation projects spanning compressible aerothermodynamics, conjugate heat transfer, reacting flow, radiation, and external aerodynamics — each taken from geometry through mesh, solver setup, and quantitative validation or parametric study.

[LinkedIn](https://www.linkedin.com/in/samuelsimmons99) · [GitHub](https://github.com/samuelsimmons99)

---

## Skills at a glance

| Domain | Methods demonstrated |
|--------|----------------------|
| **Compressible flow** | Density-based explicit (rhoCentralFoam), supersonic nozzle, Mach 3+ expansion fan, shock structure |
| **Reacting flow** | rhoReactingFoam, JANAF thermodynamics, single-step Arrhenius, species transport (C₁₂H₂₆ / O₂ / CO₂ / H₂O) |
| **Conjugate heat transfer** | chtMultiRegionSimpleFoam, foamMultiRun, solid–fluid coupling, CPU junction temperature prediction |
| **Radiation** | P1 / discrete-ordinates radiation model, view factors, mesh convergence study |
| **Natural convection** | buoyantFoam, Boussinesq approximation, validated against Churchill–Chu correlation |
| **External aerodynamics** | pimpleFoam, Re sweep (3 → 8×10⁵), kOmegaSST, Cd/Cl time-averaged |
| **Turbulence modelling** | k-ε, k-ω SST, laminar — applied and compared across cases |
| **Mesh generation** | blockMesh, snappyHexMesh, parametric Python meshing, axisymmetric wedge, multi-region |
| **Parallel & HPC** | OpenMPI, up to 16 cores, decomposePar, serial/parallel cross-verification |
| **Post-processing** | ParaView, Python/matplotlib, forceCoeffs, probes, mesh convergence plots |
| **Validation** | Isentropic nozzle theory, Churchill–Chu Nu correlation, fan curve comparison, serial vs parallel agreement |

---

## Projects

### [Rocket Nozzle — Compressible & Reacting Flow](./Nozzle%20Simulation/)
**Solvers:** `rhoCentralFoam` · `rhoReactingFoam` &nbsp;|&nbsp; **Mesh:** 5-block axisymmetric wedge, 14 400 cells &nbsp;|&nbsp; **Domain:** chamber + plume (x = −0.30 → 1.50 m)

<img src="Nozzle Simulation/Linux Files/nozzle_Mach_contour.png" width="700">

Three coupled simulations on a conical De Laval nozzle (area ratio 8:1, design Mach 3.2) at LOX/kerosene chamber conditions (T₀ = 3 000 K, p₀ = 3 MPa):

- **Hot gas** — frozen-composition perfect gas (M = 22 g/mol, γ = 1.2); exit Mach 3.22 vs isentropic theory 3.20 (< 1% error)
- **Premixed combustion** — C₁₂H₂₆/O₂ pre-mixed inlet, single-step Arrhenius, JANAF thermodynamics; species tracked through nozzle and plume
- **Separate injection** — fuel and LOX through dedicated annular inlets at O/F ≈ 2.7; mixing and reaction develop downstream

---

### [2U Server Conjugate Heat Transfer](./2U%20Server%20Simulation/)
**Solver:** `chtMultiRegionSimpleFoam` &nbsp;|&nbsp; **Mesh:** 1.1 M cells, 16 MPI cores &nbsp;|&nbsp; **Regions:** air · CPU silicon · aluminium heatsink · steel chassis

<img src="2U Server Simulation/Linux Files/heatsink_thermal_plume.png" width="700">

Steady-state CHT of a rack-mount server under 150 W CPU dissipation. Couples turbulent forced convection (k-ω SST) in the air domain with solid conduction through three material regions. Predicts **96°C CPU junction temperature** — within the thermal design power envelope. Full parallel workflow: geometry from Ansys SpaceClaim, snappyHexMesh for air domain, blockMesh for solid regions.

---

### [Parametric Heatsink CHT — Fin Pitch Sweep](./Parametric%20Heatsink%20Simulation/)
**Solver:** `foamMultiRun` &nbsp;|&nbsp; **Mesh:** Python-parametric blockMesh, 3 regions (air · Al · Si) &nbsp;|&nbsp; **Study:** 3 mm / 4 mm / 5 mm fin pitch

<img src="Parametric Heatsink Simulation/fan_curve_operating_points.png" width="700">

CPU + fin-array heatsink in a fan-driven duct. Mesh is generated parametrically so fin count and pitch are swept without manual geometry rebuilding. Peak CPU temperature drops from **343.9 K → 337.0 K** (−6.9 K) as pitch decreases from 5 mm to 3 mm. Fan operating points extracted from converged flow fields and overlaid on the published fan curve. Serial/parallel cross-verification to 0.001 K.

---

### [Radiation Heat Transfer — Mesh Convergence Study](./Radiation%20Simulation/)
**Study:** systematic mesh refinement, GCI error estimation

Radiative heat transfer simulation with a structured mesh convergence study. Grid Convergence Index (GCI) methodology applied across refinement levels to quantify discretisation error and demonstrate solution independence. Complements the convection-only heatsink cases by adding the radiation exchange mechanism relevant to high-temperature or vacuum environments.

*(In progress — images coming soon)*

---

### [Cylinder Flow — Reynolds Number Sweep](./Cylinder%20Flow/)
**Solver:** `pimpleFoam` &nbsp;|&nbsp; **Mesh:** background box + snappyHexMesh cylinder &nbsp;|&nbsp; **Re:** 3 · 40 · 30 000 · 800 000 · 5 000 000

<img src="Cylinder Flow/Linux Files/Re_30000_U_contour.png" width="700">

Five-case parametric study from creeping Stokes flow through laminar vortex shedding to turbulent supercritical shedding (k-ω SST). Drag and lift coefficients extracted via `forceCoeffs` and compared against published data across all regimes. Demonstrates solver and turbulence model selection as a function of flow physics, not just case setup.

---

### [Vertical Plate Natural Convection — Rayleigh Sweep](./Vertical%20Plate%20Natural%20Convection/)
**Solver:** `buoyantFoam` (Boussinesq, transient 2D) &nbsp;|&nbsp; **Ra:** 4.56×10⁸ · 4.09×10⁹ · 3.27×10¹⁰

<img src="Vertical Plate Natural Convection/images/base_T.png" width="700">

Three-case sweep from laminar to turbulent natural convection on a heated vertical plate. CFD Nusselt numbers benchmarked against the Churchill–Chu (1975) all-Ra correlation: laminar case within **2%**, turbulent k-ε case 15% below (expected under-prediction for k-ε in buoyant flows). Demonstrates both the capability and the quantified limits of the chosen turbulence closure.

---

### [Internal Pipe Flow](./Smoking%20Pipe%20Tutorial/)
**Solvers:** `simpleFoam` (steady) · `pimpleFoam` (transient) &nbsp;|&nbsp; **Mesh:** snappyHexMesh from STL

<img src="Smoking Pipe Tutorial/smoking_pipe_steady_state/streamlines_U.png" width="700">

Full workflow demonstration on a smoking pipe geometry: STL import → snappyHexMesh → boundary condition setup → steady and transient solve → ParaView post-processing. Foundational case establishing the mesh-to-result pipeline used in all subsequent projects.

---

## What's next

| Gap | Why it matters |
|-----|---------------|
| Turbulence model comparison study | Show model selection judgement (k-ε vs k-ω SST vs LES) on a single geometry with quantified differences |
| CHT with radiation coupling | Combine conduction, convection, and radiation in one domain — directly applicable to high-temperature electronics and spacecraft thermal control |

---

## Repository structure

```
OpenFOAM-Portfolio/
├── 2U Server Simulation/          # CHT, turbulent forced convection, parallel
├── Cylinder Flow/                 # Re sweep, external aero, drag/lift
├── Nozzle Simulation/             # Compressible + reacting, 3 cases
├── Parametric Heatsink Simulation/# Parametric CHT, fin sweep
├── Radiation Simulation/          # Radiation + mesh convergence  (in progress)
├── Smoking Pipe Tutorial/         # Internal flow, full pipeline walkthrough
├── Vertical Plate Natural Convection/ # Ra sweep, Nu validation
└── README.md                      # This file
```

**Software stack:** OpenFOAM v2012 / OF13 · Python 3 / matplotlib · ParaView · Ansys SpaceClaim · OpenMPI · Ubuntu WSL2
