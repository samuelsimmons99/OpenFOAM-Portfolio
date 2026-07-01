# Rocket Nozzle Simulation

**OpenFOAM v2012 · Axisymmetric wedge · Compressible reacting flow**

Three coupled simulations of a De Laval (converging-diverging) rocket nozzle on an identical extended mesh that captures the supersonic core flow, the diverging plume, and the ambient far-field. The study progresses from a frozen-composition hot-gas model through premixed combustion to separate LOX/kerosene injection, isolating the effect of each modelling assumption on the exit flow and species distribution.

---

## Cases

| # | Case | Solver | Description |
|---|------|--------|-------------|
| 1 | **Hot gas** | `rhoCentralFoam` | Combustion products as a single-species perfect gas (M = 22 g/mol, γ = 1.2). Density-based explicit solver captures the transonic throat and supersonic plume. |
| 2 | **Premixed combustion** | `rhoReactingFoam` | C₁₂H₂₆/O₂ mixture (kerosene surrogate) enters pre-mixed at stoichiometry. Single-step global Arrhenius reaction; JANAF thermodynamics; Sutherland transport. |
| 3 | **Separate injection** | `rhoReactingFoam` | Kerosene (fuel_inlet) and LOX (lox_inlet) are injected separately at O/F ≈ 2.7. Mixing and reaction develop downstream. |

---

## Mesh

All three cases share the same 5-block axisymmetric wedge mesh (5° wedge angle) built with `blockMesh`.

### Domain layout

```
x = -0.30          x = 0.00     x = 0.15     x = 0.50     x = 1.50
   |  Chamber     |  Converging |  Diverging  |  Plume      |  Far field
   |  (r = 0.15)  |  section    |  section    |  core       |  ambient
```

| Parameter | Value |
|-----------|-------|
| Chamber radius | 0.150 m |
| Throat radius | 0.050 m |
| Exit radius | 0.1414 m |
| Throat position | x = 0.150 m |
| Domain: x range | −0.30 m → 1.50 m |
| Domain: r range | 0 → 0.50 m |
| Total cells | 14 400 |
| Cell distribution | 40 radial × 360 axial (5 blocks) |

**Patches:** `inlet`, `outlet`, `outer_boundary` (far-field annulus + radial), `nozzle_wall`, `axis` (empty), `front`/`back` (wedge).

### Mesh visualisation

#### Hot gas / no-reaction case
![Nozzle mesh](Linux%20Files/Nozzle_mesh.png)

#### Premixed combustion
![Combustion mesh](Linux%20Files/Nozzle_combustion_mesh.png)

#### Separate injection
![Injected mesh](Linux%20Files/Nozzle_injected_mesh.png)

---

## Case 1 - Hot Gas (rhoCentralFoam)

### Physics

| Property | Value | Notes |
|----------|-------|-------|
| Molecular weight | 22 g/mol | CO₂/H₂O/CO/H₂ mixture |
| γ | 1.2 | Triatomic-dominated |
| Cp | 2 267 J/(kg K) | From γ, M |
| μ | 1×10⁻⁴ Pa s | At 3 000 K |
| Chamber pressure | 3 MPa | Total |
| Chamber temperature | 3 000 K | Total - LOX/kerosene adiabatic flame |
| Back pressure | 101 325 Pa | Sea level |

### Boundary conditions

| Patch | p | T | U | ρ |
|-------|---|---|---|---|
| inlet | `totalPressure` 3 MPa | `fixedValue` 3 000 K | `pressureInletOutletVelocity` | `fixedValue` 2.646 kg/m³ |
| outlet | `waveTransmissive` | `inletOutlet` 300 K | `zeroGradient` | `zeroGradient` |
| outer_boundary | `zeroGradient` | `inletOutlet` 300 K | `inletOutlet` (0 0 0) | `zeroGradient` |
| nozzle_wall | `zeroGradient` | `zeroGradient` | `noSlip` | `zeroGradient` |

### Mach number result (nozzle-only domain — validated design point)

![Mach number contour](Linux%20Files/nozzle_Mach_contour.png)

Throat Mach = 1.0 confirmed; exit Mach ≈ 3.22, matching the isentropic design value of 3.20 to within 1%.

| Quantity | Simulated | Isentropic theory |
|----------|-----------|-------------------|
| Exit Mach | 3.22 | 3.20 |
| Exit static T | 1 488 K | 1 482 K |
| Peak exit velocity | 2 667 m/s | 2 637 m/s |

### Extended plume domain — early transient (t = 0.0005 s)

The hot-gas case on the extended 5-block domain captures the inlet shock propagating from chamber conditions into the initially-atmospheric plume region. At t = 0.5 ms the compression front is visible mid-domain; the long-time steady-state field is represented by the validated nozzle-only result above.

![Hot gas overview](Linux%20Files/Nozzle_overview.png)

![Hot gas axis profiles](Linux%20Files/Nozzle_axis_profiles.png)

---

## Case 2 - Premixed Combustion (rhoReactingFoam)

### Physics

Pre-mixed C₁₂H₂₆/O₂ (Y_fuel = 0.2, Y_O₂ = 0.8) enters at 500 K and 3 MPa. A single-step global Arrhenius reaction consumes the reactants:

```
2 C₁₂H₂₆ + 37 O₂ → 24 CO₂ + 26 H₂O
A = 5.1×10¹¹ m³/(kmol·s),  Eₐ/Rᵤ = 15 034 K
```

Thermodynamic data: JANAF NASA-7 polynomials. Transport: Sutherland viscosity.

### Boundary conditions (species)

| Patch | C₁₂H₂₆ | O₂ | CO₂ | H₂O |
|-------|---------|-----|-----|-----|
| inlet | 0.20 (fixed) | 0.80 (fixed) | 0 | 0 |
| outlet | `inletOutlet` 0 | `inletOutlet` 1.0 | `inletOutlet` 0 | `inletOutlet` 0 |
| outer_boundary | `inletOutlet` 0 | `inletOutlet` 1.0 | `inletOutlet` 0 | `inletOutlet` 0 |

### Flow fields (t = 0.003 s)

![Overview fields](Linux%20Files/Nozzle_combustion_overview.png)

![Axis profiles](Linux%20Files/Nozzle_combustion_axis_profiles.png)

### Species distributions (t = 0.003 s)

![Species 2D](Linux%20Files/Nozzle_combustion_species.png)

![Species axis profiles](Linux%20Files/Nozzle_combustion_species_profiles.png)

---

## Case 3 - Separate Injection (rhoReactingFoam)

### Physics

Kerosene and LOX enter through dedicated concentric annular inlets (`fuel_inlet` and `lox_inlet`) at the chamber head. The initial chamber fill is combustion products (CO₂ = 0.693, H₂O = 0.307 by mass). Reaction occurs where mixing brings reactants to stoichiometry and above the ignition temperature.

| Parameter | Value |
|-----------|-------|
| Fuel inlet | C₁₂H₂₆, 3 MPa total pressure |
| Oxidiser inlet | O₂, 3 MPa total pressure |
| O/F ratio (design) | ≈ 2.7 (stoichiometric for C₁₂H₂₆/O₂) |
| Chamber fill (t = 0) | CO₂ + H₂O equilibrium products |

### Flow fields (t = 0.005 s)

![Overview fields](Linux%20Files/Nozzle_injected_overview.png)

![Axis profiles](Linux%20Files/Nozzle_injected_axis_profiles.png)

### Species distributions (t = 0.005 s)

![Species 2D](Linux%20Files/Nozzle_injected_species.png)

![Species axis profiles](Linux%20Files/Nozzle_injected_species_profiles.png)

---

## Workflow

```
blockMesh  (5-block wedge, 14 400 cells, x = -0.30 → 1.50 m)
     │
     ├── rhoCentralFoam      (Case 1: hot gas, density-based explicit)
     │
     ├── rhoReactingFoam     (Case 2: premixed C₁₂H₂₆/O₂, PIMPLE)
     │
     └── rhoReactingFoam     (Case 3: separate LOX/kerosene injection)

Post-processing:
  python3 plot_nozzle_cases.py  →  mesh, T, p, |U|, species PNGs
```

### Key solver notes

- **`rhoCentralFoam`**: requires consistent `(ρ, p, T)` initial condition - mismatching the outer-boundary density against the interior pressure causes the Newton iteration for temperature to diverge in `hePsiThermo::correct()`. Fix: initialise `ρ` from `p / (R_spec · T)` uniformly and use `zeroGradient` for ρ at far-field boundaries.
- **`rhoReactingFoam` thermo reader**: `foamChemistryReader::readSpeciesComposition()` requires an `elements {}` sub-dictionary directly inside each species block in `constant/thermo` - placing it inside the nested `specie {}` block is silently ignored.
- **Species initialisation**: all species mass fractions must sum to 1 at every patch at t = 0, including at outlet `value` fields - a zero-sum triggers a floating-point exception in `multiComponentMixture::patchFaceVolMixture()`.
- **`waveTransmissive`** BC for the far-field outer boundary of a high-pressure interior domain (3 MPa vs 101 kPa) amplifies the startup transient rather than damping it. `zeroGradient` for pressure at that boundary is more stable at t = 0.
- **Wedge block ordering**: direction 3 (extrusion axis) must start from a wall vertex, not the degenerate axis vertex, to avoid "inward-pointing face" errors during `blockMesh`.

---

## Limitations

- Conical nozzle profile - a bell or Rao-optimised shape reduces divergence loss.
- Single-step global Arrhenius - does not capture intermediate species (CO, OH, H) or dissociation at high temperature.
- Adiabatic walls - no regenerative cooling or heat-transfer to the structure.
- Laminar - no turbulence model; relevant for the mixing layer between fuel and oxidiser in Case 3.
- 2D axisymmetric - no azimuthal instabilities, swirl, or injector pattern effects.
- Over-expanded exit shock structure is partially captured in the extended plume domain but requires longer physical time to reach steady state.

---

## Software Stack

| Tool | Version | Purpose |
|------|---------|---------|
| OpenFOAM | v2012 | CFD solver (rhoCentralFoam, rhoReactingFoam) |
| Python / matplotlib | 3.x | Field extraction and plotting |
| Ubuntu (WSL2) | 22.04 | Operating system |
| ParaView | 5.11 | 3-D visualisation |

---

Part of the [OpenFOAM Portfolio](https://github.com/samuelsimmons99/OpenFOAM-Portfolio).
