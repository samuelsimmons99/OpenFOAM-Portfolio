# Rocket Nozzle Simulation

**OpenFOAM v2012 · rhoCentralFoam · Axisymmetric wedge · Compressible supersonic flow**

A parametric study of flow through a De Laval (converging-diverging) rocket nozzle, comparing an idealised hot-gas model against a reacting LOX/kerosene combustion case. Both cases use the same axisymmetric wedge geometry and are run with density-based compressible solvers capable of capturing the transonic throat, supersonic expansion, and shock structure at the nozzle exit.

---

## Cases

| Case | Solver | Inlet model | Status |
|---|---|---|---|
| [Hot gas (frozen composition)](#hot-gas-case) | `rhoCentralFoam` | Combustion products approximated as a perfect gas (M=22 g/mol, gamma=1.2) | Complete |
| [LOX/kerosene reacting flow](#lox-kerosene-case) | TBD | Full combustion chemistry with species transport | In progress |

---

## Nozzle Geometry

All cases share the same axisymmetric conical De Laval profile:

| Parameter | Value |
|---|---|
| Inlet radius | 0.150 m |
| Throat radius | 0.050 m |
| Exit radius | 0.1414 m |
| Throat position | x = 0.15 m |
| Total nozzle length | 0.50 m |
| Converging area ratio | 9:1 |
| Diverging area ratio | 8:1 |
| Design exit Mach (gamma=1.2) | ~3.2 |

The mesh is a 5-degree wedge (axisymmetric) built with `blockMesh`, 40 radial cells x 150 axial cells = 6,000 cells total. The two-block structure (converging + diverging) uses `wedge` boundary patches on the front and back faces and an `empty` patch on the degenerate axis line.

---

## Hot Gas Case

### Setup

Combustion products of LOX/kerosene are approximated as a single-species perfect gas with properties representative of the chamber exit composition:

| Property | Value | Notes |
|---|---|---|
| Molecular weight | 22 g/mol | Mix of CO2, H2O, CO, H2 |
| gamma | 1.2 | Tri-atomic dominated at high T |
| Cp | 2267 J/(kg K) | Derived from gamma, M |
| Dynamic viscosity | 1e-4 Pa s | Approximate at 3000 K |
| Chamber total pressure | 3 MPa | |
| Chamber total temperature | 3000 K | Approximate LOX/kerosene adiabatic flame temperature |
| Ambient back pressure | 101,325 Pa | Sea level — nozzle is over-expanded at design |

Boundary conditions: `totalPressure` and `totalTemperature` at the inlet, `waveTransmissive` at the outlet. The case is run laminar (viscous effects are secondary for this geometry and Reynolds number).

Solver: `rhoCentralFoam` with Kurganov-Tadmor flux scheme, MUSCL reconstruction (`vanLeer` for rho and T, `vanLeerV` for U), CFL = 0.1. Initialised with an isentropic pressure and temperature ramp along x to avoid the numerical temperature inversion that occurs when starting from uniform chamber conditions against a near-vacuum outlet.

### Results

**Mach number contour**

![Mach number contour](Linux%20Files/nozzle_Mach_contour.png)

The flow accelerates from rest at the inlet, reaches sonic conditions (Mach 1) at the throat (x = 0.15 m), then expands supersonically through the diverging section to a peak exit Mach of **3.22**, matching the isentropic design prediction of 3.2 to within 1%.

| Quantity | Simulated | Isentropic theory |
|---|---|---|
| Exit Mach | 3.22 | 3.20 |
| Exit static T | 1488 K | 1482 K |
| Peak exit velocity | 2667 m/s | 2637 m/s |

The oblique feature visible near x = 0.2 m is an expansion fan originating from the sharp throat corner — a real compressible flow effect, not a numerical artefact. The nozzle is over-expanded at sea level (design exit pressure ~43.5 kPa vs 101.3 kPa ambient), which would produce oblique shocks outside the nozzle exit in a full domain; those are outside the current computational domain.

---

## LOX/Kerosene Case

*(In progress)* — Full reacting flow with species transport and combustion chemistry, replacing the frozen-composition inlet condition with actual LOX/kerosene combustion. Same nozzle geometry.

---

## Workflow

```
blockMesh (5-degree wedge, 6000 cells)
        |
rhoCentralFoam (density-based, explicit, CFL=0.1)
        |
Post-processing: Mach = |U| / sqrt(gamma * R_spec * T)
```

**Key solver notes:**

- `rhoCentralFoam` requires `fluxScheme Kurganov` and `vanLeer` interpolation schemes — these are not inherited from `fvSchemes` defaults and must be set explicitly.
- `totalTemperature` BC in v2012 requires a `gamma` entry in the field file, not just in `thermophysicalProperties`.
- Initialising with uniform chamber conditions causes temperature inversion in the first timestep due to the large pressure gradient across the domain. An isentropic ramp initialisation resolves this.
- The wedge block vertex ordering must ensure direction 3 (the extrusion direction, v0 to v4) is a non-degenerate edge — starting both groups with a wall vertex rather than an axis vertex avoids the "inward-pointing faces" error from the degenerate zero-length axis edge.

---

## Limitations

- Conical nozzle profile — a bell or Rao-optimised profile would reduce exit flow divergence angle and improve specific impulse.
- Adiabatic wall assumption — no heat transfer to the nozzle wall.
- Laminar — boundary layer transition and turbulent mixing near the wall are not modelled.
- 2D axisymmetric — no three-dimensional instabilities or asymmetric shock structures captured.
- The over-expanded exit shock structure forms outside the domain.

---

## Software Stack

| Tool | Version | Purpose |
|---|---|---------|
| OpenFOAM | v2012 | CFD solver |
| ParaView | 5.11 | Post-processing |
| Python / matplotlib | 3.x | Mach contour plot |
| Ubuntu (WSL2) | 24.04 | OS |

---

## Repository

Part of the [OpenFOAM Portfolio](https://github.com/samuelsimmons99/OpenFOAM-Portfolio), a collection of CFD simulations demonstrating thermal and fluid simulation skills relevant to thermal engineering roles.
