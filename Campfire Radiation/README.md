# Campfire Radiation Simulation

**OpenFOAM 13 - buoyantFoam - P1 Radiation - perfectGas - Laminar 2D - Mesh Independence (GCI)**

Simulation of thermal radiation from a campfire (modelled as a 1200 K hot-gas zone) in quiescent ambient air. Demonstrates P1 participating-medium radiation transport, buoyancy-driven plume development, and a formal three-level Grid Convergence Index (GCI) mesh independence study.

---

## Problem Description

A campfire is approximated as a rectangular hot-gas zone (0.21 m x 0.81 m, 1200 K) at the axis of a half-domain. The ambient air is at 300 K. The flame emits thermal radiation into the surrounding medium (absorption coefficient kappa = 0.3 m-1, representing lightly smoky air) and heats the ground via convection and radiation.

The simulation answers two questions:

1. **Radiation field**: How does incident radiation G (W/m2) decay with distance from the flame axis, and how does the P1 approximation compare to the Stefan-Boltzmann prediction?
2. **Mesh independence**: Is the medium (nx=60) mesh sufficiently refined, and what is the GCI?

---

## Domain and Geometry

Half-domain (symmetry at x=0, flame at axis):

```
     top  (outlet BC)
  +--------+
  |        |  y=3 m
  |  plume |
  |        |
  +--------+  y=0.8 m
  |flame   |  (T=1200K in box x=[0,0.21], y=[0,0.81])
  |  zone  |
  +--------+  y=0 m
axis    outlet (x=4 m)
         ground (z=0, wall)
```

| Dimension | Value |
|-----------|-------|
| Domain width (half) | 4 m |
| Domain height | 3 m |
| Domain depth (2D) | 0.05 m |
| Flame zone width | 0.21 m |
| Flame zone height | 0.81 m |
| Flame temperature | 1200 K |
| Ambient temperature | 300 K |

---

## Physics

### Radiation Model: P1

The P1 model solves a diffusion equation for incident radiation G (W/m2):

```
div(Gamma * grad(G)) - kappa*G + 4*kappa*sigma*T^4 = 0
```

where Gamma = 1/(3*(kappa + sigma_s)) = 1/(3*kappa) (no scattering), sigma = 5.67e-8 W/m2/K4.

The P1 model is valid when the optical thickness tau = kappa*L >> 1. Here tau = 0.3*4 = 1.2, meaning the domain is borderline optically thick. P1 is approximate but acceptable for demonstration.

**Boundary conditions for G:**

- Ground: `MarshakRadiation`, emissivity = 0.9 (absorbing ground)
- Outlet and top: `MarshakRadiation`, emissivity = 1.0 (black body surroundings)
- Axis: `symmetryPlane`

### Flame Temperature Constraint

The flame zone temperature is maintained at 1200 K using the `fixedTemperature` constraint in `fvConstraints` applied to the `flameZone` cellZone (created via `topoSet`). This represents the thermal output of combustion without modelling combustion chemistry.

### Equation of State: perfectGas

With a 4:1 temperature ratio (1200 K / 300 K), Boussinesq linearisation fails (it predicts negative density at the flame). The `perfectGas` EOS is used:

```
rho = p / (Rspecific * T)    where Rspecific = R/M = 8314/28.9 = 287.7 J/(kg*K)
```

At T=300 K: rho = 1.174 kg/m3. At T=1200 K: rho = 0.294 kg/m3 (4x lower). This density difference drives the buoyant plume.

### Air Properties

| Property | Value |
|----------|-------|
| Molecular weight | 28.9 g/mol |
| Cp | 1005 J/(kg*K) |
| mu (constant) | 1.8e-5 Pa*s |
| Pr | 0.71 |
| kappa (absorption) | 0.30 m-1 |

Note: constant transport properties are used (no temperature-dependent viscosity). The 1.8e-5 Pa*s value is appropriate for ambient air; at 1200 K the actual mu would be roughly 4x higher. This approximation is acceptable for a portfolio demonstration focused on radiation.

---

## Mesh Convergence Study (GCI)

Three mesh levels with refinement ratio r = 2 in each direction:

| Level | nx | ny_low | ny_high | Total cells | h (relative) |
|-------|----|--------|---------|-------------|--------------|
| Coarse | 30 | 10 | 20 | 900 | 1/30 |
| Medium | 60 | 20 | 40 | 3,600 | 1/60 |
| Fine | 120 | 40 | 80 | 14,400 | 1/120 |

All three meshes use the same geometric grading: strong refinement near the flame axis (x=0) with a 30:1 expansion ratio over the first 5% of the domain width.

The **Grid Convergence Index (GCI)** method (Roache 1994) with safety factor Fs=1.25 gives a conservative error band:

```
GCI_fine = Fs * |f_medium - f_fine| / (r^p - 1) / |f_fine|  * 100 %
```

where p is the observed order of convergence from Richardson extrapolation.

**Quantity of interest**: time-averaged G (W/m2) at probe point (x=2.0 m, y=0.4 m) - 2 m from the flame axis at head height.

### Results

*[GCI analysis pending - runs in progress]*

---

## Simulation Setup

### Solver

| Setting | Value |
|---------|-------|
| Solver | `buoyantFoam` (OF13, `foamRun -solver fluid`) |
| Mode | Transient, laminar |
| End time | 30 s |
| Timestep | 0.005 s fixed |
| Radiation | P1, solved every timestep |
| Temperature constraint | `fvConstraints` `fixedTemperature` on `flameZone` cellZone |

### Boundary Conditions

| Patch | U | T | p_rgh | G |
|-------|---|---|-------|---|
| Axis | symmetryPlane | symmetryPlane | symmetryPlane | symmetryPlane |
| Ground (wall) | noSlip | zeroGradient | fixedFluxPressure | MarshakRadiation (eps=0.9) |
| Outlet (right wall) | pressureInletOutletVelocity | inletOutlet 300 K | fixedValue 101325 | MarshakRadiation (eps=1.0) |
| Top | pressureInletOutletVelocity | inletOutlet 300 K | fixedValue 101325 | MarshakRadiation (eps=1.0) |

---

## Workflow

```
blockMesh (2-block graded 2D mesh, three resolutions)
    |
topoSet (create flameZone cellZone from box selection)
    |
setFields (pre-initialize T=1200K in flameZone to avoid cold-start shock)
    |
buoyantFoam (perfectGas, P1 radiation, fixedTemperature constraint)
    |
Python GCI script (Richardson extrapolation on G probe at 2 m from flame)
```

---

## Status

| Task | Status |
|------|--------|
| Medium mesh (nx=60, 3600 cells) | Done - 30 s run complete |
| Coarse mesh (nx=30, 900 cells) | Running |
| Fine mesh (nx=120, 14400 cells) | Running |
| GCI analysis | Pending |
| Visualisation (G, T fields) | Pending |
| Portfolio images | Pending |

---

## Software Stack

| Tool | Version | Purpose |
|------|---------|---------|
| OpenFOAM | 13 | CFD + radiation solver |
| Python | 3.x | GCI analysis script |
| Ubuntu (WSL2) | 24.04 | OS |
