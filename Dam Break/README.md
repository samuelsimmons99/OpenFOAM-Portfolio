# Dam Break: Free Surface Flow Validation

Validation of OpenFOAM's VOF (Volume of Fluid) free-surface solver against the classical Martin & Moyce (1952) dam break experiment.

## Physics

A square water column (0.292 m × 0.292 m) collapses under gravity in a 1.2 m × 0.6 m tank. The simulation captures the surge front propagation and column height decay, non-dimensionalised as:

- τ = t √(2g/a), non-dimensional time
- X = x_front / (2a), non-dimensional surge front position  
- Z = z_col / H, non-dimensional column height

where *a* = 0.146 m (half column width), *H* = 0.292 m (initial column height).

## Setup

| Parameter | Value |
|-----------|-------|
| Solver | `interFoam` (VOF, two-phase) |
| Mesh | 480 × 240 × 1 uniform Cartesian (115,200 cells, Δx = Δy = 2.5 mm) |
| Water | ρ = 1000 kg/m³, ν = 1×10⁻⁶ m²/s |
| Air | ρ = 1 kg/m³, ν = 1.48×10⁻⁵ m²/s |
| Surface tension | σ = 0.07 N/m |
| End time | 0.45 s (τ_max ≈ 5.2) |
| Time stepping | Adaptive, max Co = 0.4, max α·Co = 0.4 |
| Turbulence | Laminar |

Initial condition set with `setFields`: α_water = 1 inside the column, 0 elsewhere.

## Results

![Dam break validation](dambreak_validation.png)

**Surge front** tracks M&M closely through τ ≈ 3, with a small lead consistent with published VOF results, commonly attributed to the finite gate removal time in the physical experiment (Koshizuka & Oka 1995; Colagrossi & Landrini 2003). The plateau at τ ≈ 4.5 is the surge reaching the right wall.

**Column height** matches well at early times (τ < 1.5) but overpredicts the late-collapse phase (τ > 2). This is a known VOF limitation: the rapid thinning and detachment of the column near τ ≈ 2.5–3 requires sub-millimetre resolution to resolve the interface geometry accurately (Hu & Adams 2009). Meshes of Δ < 1 mm or particle-based methods (SPH) are typically required for full column-height agreement at τ > 2.5. The correct qualitative behaviour is reproduced: monotonic column collapse, correct time scale, and volume conservation.

## References

- Martin, J. C., & Moyce, W. J. (1952). Part IV. An experimental study of the collapse of liquid columns on a rigid horizontal plane. *Philosophical Transactions of the Royal Society of London. Series A*, **244**(882), 312–324.
- Koshizuka, S., & Oka, Y. (1995). Moving-particle semi-implicit method for fragmentation of incompressible fluid. *Nuclear Science and Engineering*, **123**(3), 421–434.
