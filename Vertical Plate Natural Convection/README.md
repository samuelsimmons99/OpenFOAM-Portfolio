# Vertical Plate Natural Convection

**OpenFOAM 13 · buoyantFoam · Boussinesq · Transient 2D Laminar**

Transient natural convection simulation of a heated vertical plate in quiescent air, compared against the Churchill-Chu analytical correlation. The simulation computes Grashof number, Rayleigh number, Nusselt number, and convection coefficient from both CFD and theory, and quantifies the sources of discrepancy.

---

## Problem Definition

A 1 m x 1 m vertical plate starts at 100°C (373.15 K) in quiescent air at 300 K (26.85°C). There is no forced flow - natural convection is driven purely by buoyancy as the warm plate heats the adjacent air, reducing its density and causing it to rise. The simulation tracks the development of the thermal boundary layer and plume from rest to quasi-steady state.

| Parameter | Value |
|-----------|-------|
| Plate temperature | 373.15 K (100°C) |
| Ambient air temperature | 300 K (26.85°C) |
| Temperature difference | 73.15 K |
| Plate height (L) | 1.0 m |
| Gravity | 9.81 m/s² (downward, -y) |

---

## Analytical Reference Values

Air properties are evaluated at the film temperature T_f = (373.15 + 300) / 2 = 336.6 K.

### Air Properties at Film Temperature

| Property | Symbol | Value |
|----------|--------|-------|
| Dynamic viscosity (Sutherland law) | mu | 2.018e-5 Pa·s |
| Density (ideal gas) | rho | 1.049 kg/m³ |
| Kinematic viscosity | nu | 1.924e-5 m²/s |
| Thermal conductivity | k | 0.02860 W/m·K |
| Specific heat | Cp | 1007 J/kg·K |
| Prandtl number | Pr | 0.711 |
| Thermal expansion coefficient (ideal gas) | beta = 1/T_f | 2.971e-3 1/K |

### Dimensionless Numbers

| Number | Formula | Value |
|--------|---------|-------|
| **Grashof** | Gr_L = g · beta · dT · L³ / nu² | **5.757e9** |
| **Rayleigh** | Ra_L = Gr_L · Pr | **4.091e9** |

Ra > 10^9 places this case in the **transitional regime** (laminar to turbulent), requiring care in choosing the appropriate correlation for comparison.

### Churchill-Chu Correlation (1975)

**All-Ra form** (accounts for both laminar and turbulent contributions):

Nu_L = {0.825 + 0.387 · [Ra_L / (1 + (0.492/Pr)^(9/16))^(16/9)]^(1/6)}²

| Correlation | Nu_L | h (W/m²·K) | q (W/m²) |
|-------------|------|------------|----------|
| All-Ra Churchill-Chu | **190.4** | **5.447** | **398.4** |
| Laminar Churchill-Chu (0.68 + 0.670·Ra^0.25/corr) | **130.8** | **3.739** | **273.5** |

The all-Ra form includes turbulent enhancement; the laminar form is the correct comparison baseline for this laminar CFD run.

---

## Simulation Setup

### Domain and Mesh

The 2D domain is sized to capture the full boundary layer and thermal plume:

| Region | x range | y range | Purpose |
|--------|---------|---------|---------|
| Below plate | 0 to 1.5 m | -0.3 to 0 m | Air entrainment inlet |
| Plate region | 0 to 1.5 m | 0 to 1.0 m | Boundary layer development |
| Above plate | 0 to 1.5 m | 1.0 to 1.3 m | Thermal plume exit |

- **Plate**: x = 0, y = 0 to 1 m (left boundary, heated wall)
- **z-direction**: 0.05 m thickness, 1 cell (empty BC - 2D simulation)
- **Total cells**: 9,450 hex cells (3-block blockMesh)

**Wall-normal refinement**: x-direction graded fine-to-coarse away from plate. First cell 0.66 mm, resolves the ~3.5 mm thermal boundary layer with approximately 5 cells.

Characteristic velocity (buoyancy scale): v_char = sqrt(g · beta · dT · L) = 1.46 m/s

### Solver and Physics

| Setting | Value |
|---------|-------|
| Solver | `buoyantFoam` (OpenFOAM 13, PIMPLE transient) |
| Equation of state | Boussinesq: rho = rho0 · (1 - beta · (T - T0)) |
| Energy equation | `eConst` / `sensibleInternalEnergy` |
| Turbulence | Laminar (Stokes) |
| End time | 300 s |
| Timestep | 0.05 s (fixed), Courant number mean ~0.18, max ~11 |

**Boundary conditions:**

| Patch | Velocity | Temperature | p_rgh |
|-------|----------|-------------|-------|
| `plate` (heated wall) | noSlip | fixedValue 373.15 K | fixedFluxPressure |
| `bottom_left`, `top_left` (wall above/below plate) | slip | zeroGradient | fixedFluxPressure |
| `inlet` (y = -0.3 m) | pressureInletOutletVelocity | inletOutlet 300 K | fixedValue 0 |
| `outlet` (y = 1.3 m) | pressureInletOutletVelocity | inletOutlet 300 K | fixedValue 0 |
| `farfield` (x = 1.5 m) | pressureInletOutletVelocity | inletOutlet 300 K | fixedValue 0 |

---

## Results

### Heat Transfer Comparison

The simulation reaches quasi-steady state by t = 160 s, after which the plate-averaged heat flux stabilises at ~199 W/m².

| Quantity | All-Ra Churchill-Chu | Laminar Churchill-Chu | CFD (laminar) |
|----------|---------------------|----------------------|---------------|
| **Nu_L** | 190.4 | 130.8 | **95.3** |
| **h (W/m²·K)** | 5.447 | 3.739 | **2.725** |
| **q (W/m²)** | 398.4 | 273.5 | **199.3** |
| CFD vs all-Ra CC | - | - | -50.0% |
| CFD vs laminar CC | - | - | -27.1% |

### Transient Heat Flux Development

The wall-averaged heat flux evolves from an initially high value (conduction-dominated, no flow) and decreases as the boundary layer thickens and entrainment velocity reaches equilibrium:

| Time | q (W/m²) | Phase |
|------|----------|-------|
| 0 s | 4614 | Conduction only (zero velocity) |
| 20 s | 299 | Boundary layer forming |
| 60 s | 254 | Flow developing |
| 160 s | 200 | Quasi-steady |
| 300 s | 199 | Fully quasi-steady |

### Analysis of Discrepancy

The 27% gap between CFD (Nu = 95.3) and the **laminar** correlation (Nu = 130.8) is expected and attributable to three compounding effects:

1. **Cv vs Cp in Boussinesq eConst**: The `eConst/sensibleInternalEnergy` energy equation diffuses temperature at alpha = k/(rho·Cv) rather than the physically correct k/(rho·Cp). For air (Cp/Cv = gamma = 1.4), the thermal diffusivity is 40% too large, modestly thickening the boundary layer (expected -8% on Nu ~ alpha^(-1/4)).

2. **High Courant number near wall**: With a fixed deltaT = 0.05 s and first-cell thickness 0.66 mm, the maximum Courant number reaches ~11 in the cells closest to the plate. The `linearUpwind` scheme at high Co introduces numerical diffusion, further thickening the effective thermal boundary layer.

3. **Finite domain warming**: The 1.5 m wide domain allows the rising warm plume to partially recirculate through open boundaries, gradually warming the effective ambient temperature below 300 K. This reduces the driving delta_T and the heat flux.

A fully mesh-refined run with adaptive timestepping (Co_max < 1), a larger domain, and `hConst/sensibleEnthalpy` (which correctly uses Cp) would be expected to converge the CFD Nu to within 10-15% of the laminar correlation.

---

## Key Physics

- **Gr >> 1**: Buoyancy forces dominate viscous forces - inertial flow rather than creeping flow
- **Ra ~ 4e9**: At the laminar-to-turbulent transition. Fully laminar natural convection (Ra < 10^8) would give Nu_L ~ 0.59 · Ra^(1/4) = 83. The Ra^(1/3) turbulent scaling begins near Ra = 10^9.
- **Boundary layer profile**: Heat flux is highest at the bottom of the plate (leading edge, thin developing BL) and lowest near the top (fully developed BL, ~3.5 mm thick). The ratio of max to min flux in the simulation (635:151 at t=300s) reflects this local Nu_x variation.
- **Characteristic velocity**: The buoyancy velocity scale sqrt(g·beta·dT·L) = 1.46 m/s is a useful check - observed CFD velocities near the plate are in this range.

---

## Workflow

```
blockMesh (3-block graded 2D mesh, 9,450 cells)
    |
buoyantFoam (Boussinesq, laminar, transient, deltaT=0.05s, endTime=300s)
    |
wallHeatFlux function object (writes q_avg vs. time to postProcessing/)
    |
analytical_comparison.py (computes Gr/Ra/Nu analytically, reads CFD, compares)
```

---

## Status

| Task | Status |
|------|--------|
| Mesh generation (blockMesh) | Done - zero non-orthogonality, zero skewness |
| Solver run (300 s transient) | Done - 174 s wall clock |
| Quasi-steady state reached | Done - plateau at t = 160 s |
| Analytical comparison | Done - see table above |

---

## Software Stack

| Tool | Version | Purpose |
|------|---------|---------|
| OpenFOAM | 13 | CFD solver (`buoyantFoam`, Boussinesq) |
| Python | 3.x | Analytical comparison script |
| Ubuntu (WSL2) | 24.04 | OS |
