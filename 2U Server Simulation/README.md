# 2U Server Conjugate Heat Transfer Simulation

**OpenFOAM v2012 · chtMultiRegionSimpleFoam · 16-Core Parallel · 20,000 Iterations**

A steady-state Conjugate Heat Transfer (CHT) simulation of a 2U rack-mount server chassis, coupling turbulent forced convection in the air domain with conductive heat transfer through solid components. Developed as part of an OpenFOAM CFD portfolio demonstrating industrial thermal simulation methodology.

---

## Key Results

| Parameter | Value |
|-----------|-------|
| Solver | `chtMultiRegionSimpleFoam` |
| Total mesh cells | ~1.1 million |
| Parallel cores | 16 |
| Total iterations | 20,000 |
| CPU heat dissipation | 150 W |
| Fan inlet velocity | 2.86 m/s (Delta FFB0812VH) |
| **Max CPU temperature** | **96°C** |
| Inlet air temperature | 27°C (300 K) |
| Estimated heatsink thermal resistance | 0.46 C/W |

---

## Simulation Overview

### Geometry
Built in **Ansys SpaceClaim** using the Python scripting API (V261). Multi-body STL export with `FilePerBody` granularity. Components modelled:
- CPU die: 45×45×4 mm (silicon, 150 W heat source)
- Thermal Interface Material: 0.1 mm (k = 6 W/m·K, modelled as contact resistance)
- Heatsink: 120×80×40 mm aluminium with 15 fins
- Steel front panel with fan cutouts
- Motherboard, PCBs, and expansion cards

### Mesh
Generated using OpenFOAM's `snappyHexMesh` with `locationsInMesh` for multi-region detection. Split into 4 regions using `splitMeshRegions -cellZones`.

| Region | Material | Approx. Cells |
|--------|----------|---------------|
| `domain0` | Air (perfectGas) | ~900,000 |
| `CPU` | Silicon (k=130 W/m·K) | ~5,200 |
| `Heatsink` | Aluminium (k=202 W/m·K) | ~150,000 |
| `FRONT_PANEL` | Steel (k=16 W/m·K) | ~50,000 |

### Solver Setup
- **Thermophysical model**: `heRhoThermo` + `perfectGas` equation of state
- **Turbulence**: k-epsilon RAS model
- **Coupling**: `turbulentTemperatureCoupledBaffleMixed` at all solid-fluid interfaces
- **Heat source**: `scalarSemiImplicitSource` (1.863×10⁷ W/m³ in CPU region)
- **Fan BC**: `fixedValue` velocity inlet `(0 0 -2.86)` m/s
- **Pressure-velocity**: SIMPLE algorithm with relaxation factors 0.7 (U), 0.5 (h), 1.0 (rho)

---

## Results

### Geometry
![SpaceClaim Geometry](Linux%20Files/SpaceClaim_Geometry.png)

Server geometry built in Ansys SpaceClaim showing the chassis (orange), motherboard and PCBs (green), aluminium heatsink fin array (brown), and fan assemblies (blue). The simulation domain encompasses the full server interior.

### Convergence History
![CPU Temperature Convergence](Linux%20Files/cpu_convergence_final.png)

CPU maximum temperature vs. iteration across all 20,000 steady-state iterations. Step changes in the curve correspond to solver restarts. The curve shows asymptotic behaviour approaching 96°C.

### Temperature Distribution
![Temperature Contour](Linux%20Files/temperature_contour_plot_overall.png)

Mid-plane temperature contour showing the thermal plume rising from the heatsink through the server interior. Inlet air at 27°C is heated as it passes through the fin array.

### Heatsink Thermal Plume
![Heatsink Thermal Plume](Linux%20Files/heatsink_thermal_plume.png)

Side-view cross-section through the heatsink showing the thermal plume structure. The CPU hot spot is visible at the base (~96°C) with heat conducted through the fins and convected downstream.

### Solid Region Temperatures
![Solid Temperatures](Linux%20Files/combined_solid_regions_temperature.png)

Temperature distribution across all solid regions showing the heat flow path from CPU → TIM → heatsink base → fins.

### Velocity Distribution
![Velocity Contour](Linux%20Files/U_contour_plot.png)

Velocity magnitude contour showing peak velocities of ~11 m/s within the heatsink fin channels and fan inlet jets impinging on board-mounted components.

### Pressure Distribution
![Pressure Contour](Linux%20Files/pressure_contours.png)

Static pressure field showing the dominant pressure drop across the heatsink fin array.

---

## Workflow

```
SpaceClaim (Python API)
        ↓
STL export (FilePerBody)
        ↓
surfaceTransformPoints (mm → m)
        ↓
blockMesh (background hex mesh)
        ↓
snappyHexMesh (castellated + snap + layers)
        ↓
splitMeshRegions -cellZones
        ↓
Isothermal run (establish flow field)
        ↓
chtMultiRegionSimpleFoam -parallel (16 cores, 20,000 iterations)
        ↓
reconstructPar → ParaView post-processing
```

---

## Future Lessons

Key debugging discoveries made during this project (full notes at `openfoam_CHT_debugging_notes.md`):

1. Use `perfectGas` not `incompressiblePerfectGas` - incompressible causes diagonal solver crash with `steadyState`
2. Delete global `system/fvOptions` - it silently overrides region-specific `fvOptions`
3. Heat source: `scalarSemiImplicitSource`, `volumeMode specific`, value `1.863e7 W/m³`
4. Both sides of coupled interfaces must use `turbulentTemperatureCoupledBaffleMixed`
5. Checkpoints overwrite coupled BCs with `fixedValue` - must manually fix after restart
6. Run isothermal first to establish flow, then switch to coupled BCs
7. `chtMultiRegionSimpleFoam` requires `SIMPLE` block in all region `fvSolution` files
8. Use `chtMultiRegionSimpleFoam` (not `chtMultiRegionFoam`) for steady-state runs

---

## Limitations

- TIM layer too thin to mesh directly → modelled as contact resistance BC
- Outer domain boundaries use `slip` condition rather than true open-atmosphere
- Three heatsink fins show lower-than-expected temperatures due to local mesh quality
- Fan modelled as uniform velocity inlet (not full fan curve pressure-flow relationship)
- Full convergence not achieved at 20,000 iterations (~0.001°C/iteration drift remaining)

---

## Software Stack

| Tool | Version | Purpose |
|------|---------|---------|
| OpenFOAM | v2012 | CFD solver |
| Ansys SpaceClaim | 2023 | CAD geometry |
| ParaView | 5.x | Post-processing |
| Python / matplotlib | 3.x | Convergence plots |
| Ubuntu (WSL2) | 24.04 | OS |
| OpenMPI | 4.0.3 | Parallel communication |

---

## Repository

Part of the [OpenFOAM Portfolio](https://github.com/samuelsimmons99/OpenFOAM-Portfolio) - a collection of CFD simulations demonstrating thermal and fluid simulation skills relevant to thermal engineering roles.
