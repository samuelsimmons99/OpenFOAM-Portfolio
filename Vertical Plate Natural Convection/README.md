# Vertical Plate Natural Convection

**OpenFOAM 13 · buoyantFoam · Boussinesq · Transient 2D · Three-Case Ra Sweep**

Parametric study of natural convection on a heated vertical plate across three Rayleigh number regimes: fully laminar, transitional, and fully turbulent. Each case computes Grashof number, Rayleigh number, Nusselt number, and convection coefficient from both CFD and the Churchill-Chu (1975) analytical correlation.

---

## Problem Definition

A vertical plate in quiescent air at 300 K is held at a fixed temperature. Buoyancy drives air upward along the plate, forming a thermal boundary layer. Three cases vary plate temperature and height to sweep Ra across three orders of magnitude.

| Case | T_plate | T_inf | dT | L | Ra | Regime |
|------|---------|-------|----|---|----|--------|
| Laminar | 305 K (32°C) | 300 K | 5 K | 1 m | 4.56e8 | Laminar (Ra < 1e9) |
| Transitional | 373.15 K (100°C) | 300 K | 73.15 K | 1 m | 4.09e9 | Transitional (1e9 < Ra < 1e10) |
| Turbulent | 373.15 K (100°C) | 300 K | 73.15 K | 2 m | 3.27e10 | Turbulent (Ra > 1e10) |

All cases use the same solver setup - the Ra regime is set by geometry and boundary conditions alone.

---

## Analytical Reference: Churchill-Chu (1975)

Air properties are evaluated at the film temperature T_f = (T_plate + T_inf) / 2.

**All-Ra form** (valid for the full Ra range, accounts for turbulent augmentation):

Nu_L = {0.825 + 0.387 · [Ra_L / (1 + (0.492/Pr)^(9/16))^(16/9)]^(1/6)}^2

**Laminar form** (Ra < 1e9 only):

Nu_L = 0.68 + 0.670 · Ra_L^(1/4) / (1 + (0.492/Pr)^(9/16))^(4/9)

### Air Properties at Film Temperature

| Property | Laminar (T_f=302.5 K) | Transitional (T_f=336.6 K) | Turbulent (T_f=336.6 K) |
|----------|-----------------------|---------------------------|-------------------------|
| mu (Pa·s) | 1.860e-5 | 2.018e-5 | 2.018e-5 |
| rho (kg/m³) | 1.167 | 1.049 | 1.049 |
| nu (m²/s) | 1.594e-5 | 1.924e-5 | 1.924e-5 |
| k (W/m·K) | 0.02620 | 0.02860 | 0.02860 |
| Pr | 0.715 | 0.711 | 0.711 |
| beta (1/K) | 3.306e-3 | 2.971e-3 | 2.971e-3 |

### Analytical Nusselt Numbers

| Case | Ra | All-Ra CC Nu | Laminar CC Nu |
|------|----|-------------|---------------|
| Laminar | 4.56e8 | 96.6 | 75.9 |
| Transitional | 4.09e9 | 190.4 | 130.8 |
| Turbulent | 3.27e10 | 367.7 | 219.4 (not valid) |

---

## Simulation Setup

### Domain and Mesh

Three-block 2D blockMesh, graded fine-to-coarse away from the plate wall.

| Case | Domain (x x y) | Cells | First cell dx |
|------|----------------|-------|---------------|
| Laminar / Transitional | 1.5 m x 1.6 m | 9,450 | 0.66 mm |
| Turbulent | 2.5 m x 2.8 m | 16,400 | 0.83 mm |

- **Plate**: left boundary (x = 0), fixed temperature
- **z-direction**: 0.05 m, 1 cell, empty BC (2D simulation)
- **Open boundaries** (inlet, outlet, farfield): `inletOutlet` at 300 K, `pressureInletOutletVelocity`

### Solver and Physics

| Setting | Laminar / Transitional | Turbulent |
|---------|----------------------|-----------|
| Solver | `buoyantFoam` (PIMPLE transient) | same |
| Equation of state | Boussinesq | same |
| Energy equation | `eConst` / `sensibleInternalEnergy` | same |
| Turbulence model | Laminar (Stokes) | `kEpsilon` |
| End time | 600 s / 300 s | 300 s |
| Timestep | 0.05 s fixed | 0.05 s fixed |

**Boundary conditions (all cases):**

| Patch | Velocity | Temperature | p_rgh |
|-------|----------|-------------|-------|
| `plate` | noSlip | fixedValue T_plate | fixedFluxPressure |
| `bottom_left`, `top_left` | slip | zeroGradient | fixedFluxPressure |
| `inlet`, `outlet`, `farfield` | pressureInletOutletVelocity | inletOutlet 300 K | fixedValue 0 |

---

## Results

### Heat Transfer Comparison

| Case | Ra | All-Ra CC Nu | CFD Nu | CFD h (W/m²·K) | CFD q (W/m²) | Error vs All-Ra CC |
|------|----|-------------|--------|-----------------|--------------|-------------------|
| Laminar | 4.56e8 | 96.6 | **98.5** | 2.58 | 12.9 | +1.9% |
| Transitional | 4.09e9 | 190.4 | **95.3** | 2.73 | 199.3 | -50.0% |
| Turbulent | 3.27e10 | 367.7 | **311.5** | 4.45 | 325.8 | -15.3% |

### Laminar Case (Ra = 4.56e8)

Excellent agreement with the all-Ra Churchill-Chu correlation (+1.9%). The laminar form (Nu=75.9) underestimates because Ra=4.56e8 is near the upper end of the laminar range where turbulent augmentation in the correlation begins to matter. Heat flux trend:

| Time (s) | q (W/m²) | Nu |
|----------|----------|----|
| 100 | 17.41 | 132.9 |
| 200 | 16.06 | 122.5 |
| 300 | 14.97 | 114.3 |
| 400 | 13.95 | 106.5 |
| 500 | 12.92 | 98.6 |
| 600 | 11.84 | 90.4 |

The slow monotonic decay reflects the long settling time at low driving dT (v_char = 0.40 m/s, roughly 3.6x slower than the 100°C case). The flux converges toward the all-Ra CC value (~12.7 W/m²), with the t=400-600s average giving Nu=98.5.

### Transitional Case (Ra = 4.09e9)

The laminar CFD run gives Nu=95.3, which is 27% below the laminar Churchill-Chu correlation (130.8) and 50% below the all-Ra form (190.4). Three sources of discrepancy:

1. **Turbulence missing**: Ra=4.09e9 sits at the laminar-to-turbulent transition. A laminar simulation cannot capture the turbulent augmentation that the all-Ra CC includes. This accounts for most of the gap versus all-Ra CC.
2. **Cv vs Cp error**: The Boussinesq `eConst` formulation uses Cv in the energy equation, giving thermal diffusivity k/(rho·Cv) = 1.4x too large. This thickens the thermal boundary layer, reducing Nu by roughly 8%.
3. **Numerical diffusion**: Fixed deltaT=0.05 s with 0.66 mm first cell gives Co_max ~11. The `linearUpwind` scheme at high Co adds numerical diffusion, further suppressing Nu.

### Turbulent Case (Ra = 3.27e10)

CFD with `kEpsilon` gives Nu=311.5, which is 15.3% below the all-Ra Churchill-Chu correlation (367.7). The standard `kEpsilon` model does not include the buoyancy production term in the k-equation (G_b), so it under-predicts turbulent enhancement near the heated wall. A buoyancy-augmented model (`buoyantKEpsilon`) would be expected to reduce this gap. The result nevertheless captures the correct turbulent scaling (Nu ~ Ra^(1/3)) and sits well above the laminar correlation value (219.4), confirming the turbulent regime.

### Characteristic Velocities

| Case | v_char = sqrt(g·beta·dT·L) | Observed peak CFD velocity |
|------|--------------------------|---------------------------|
| Laminar (305K, 1m) | 0.40 m/s | ~0.3 m/s |
| Transitional (100°C, 1m) | 1.46 m/s | ~1.3 m/s |
| Turbulent (100°C, 2m) | 2.06 m/s | ~2.0 m/s |

---

## Key Physics

- **Gr >> 1**: Buoyancy forces dominate viscous forces across all cases - inertial flow rather than creeping flow.
- **Ra scaling**: Nu ~ Ra^(1/4) in the laminar regime, transitioning to Nu ~ Ra^(1/3) above Ra ~1e9. The three cases are chosen to straddle this transition.
- **Boundary layer profile**: Heat flux peaks at the plate leading edge (thin developing BL) and drops toward the top (thick fully developed BL). The ratio of max to min local flux at quasi-steady state is approximately 10:1.
- **Domain warming**: At low dT (laminar case), the characteristic velocity is slow and the domain takes longer to flush. A larger domain or longer run would further converge the result.

---

## Workflow

```
blockMesh (3-block graded 2D mesh)
    |
buoyantFoam (Boussinesq, PIMPLE transient, endTime 300-600s)
    |
wallHeatFlux function object (q_avg vs. time to postProcessing/)
    |
analytical_comparison.py (Churchill-Chu, reads CFD, prints comparison)
```

---

## Status

| Task | Status |
|------|--------|
| Laminar case (305K, 1m, Ra=4.56e8) | Done - 600s run, Nu=98.5 (+1.9% vs CC) |
| Transitional case (100°C, 1m, Ra=4.09e9) | Done - 300s run, Nu=95.3 (-27% vs lam CC) |
| Turbulent case (100°C, 2m, Ra=3.27e10) | Done - 300s run, Nu=311.5 (-15% vs CC) |
| Analytical comparison (all cases) | Done - see tables above |

---

## Software Stack

| Tool | Version | Purpose |
|------|---------|---------|
| OpenFOAM | 13 | CFD solver (`buoyantFoam`, Boussinesq, `kEpsilon`) |
| Python | 3.x | Analytical comparison script |
| Ubuntu (WSL2) | 24.04 | OS |
