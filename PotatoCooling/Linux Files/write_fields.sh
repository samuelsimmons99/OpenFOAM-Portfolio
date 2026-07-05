#!/bin/bash
# Write all region fields and properties in the correct v2012 multi-region layout
CASE=/home/rinkoa/OpenFOAM-v2012/sims/PotatoCooling

# ── DOMAIN0 (AIR) — Initial fields ───────────────────────────────────────────

mkdir -p $CASE/0/domain0

cat > $CASE/0/domain0/T << 'EOF'
FoamFile { version 2.0; format ascii; class volScalarField; object T; }
dimensions      [0 0 0 1 0 0 0];
internalField   uniform 298.15;
boundaryField
{
    sides
    {
        type            fixedValue;
        value           uniform 298.15;
    }
    domain0_to_potato
    {
        type            compressible::turbulentTemperatureCoupledBaffleMixed;
        Tnbr            T;
        kappa           fluidThermo;
        kappaName       none;
        value           uniform 370.0;
    }
}
EOF

cat > $CASE/0/domain0/p_rgh << 'EOF'
FoamFile { version 2.0; format ascii; class volScalarField; object p_rgh; }
dimensions      [1 -1 -2 0 0 0 0];
internalField   uniform 101325;
boundaryField
{
    sides               { type fixedFluxPressure; value uniform 101325; }
    domain0_to_potato   { type fixedFluxPressure; value uniform 101325; }
}
EOF

cat > $CASE/0/domain0/p << 'EOF'
FoamFile { version 2.0; format ascii; class volScalarField; object p; }
dimensions      [1 -1 -2 0 0 0 0];
internalField   uniform 101325;
boundaryField
{
    sides               { type calculated; value uniform 101325; }
    domain0_to_potato   { type calculated; value uniform 101325; }
}
EOF

cat > $CASE/0/domain0/U << 'EOF'
FoamFile { version 2.0; format ascii; class volVectorField; object U; }
dimensions      [0 1 -1 0 0 0 0];
internalField   uniform (0 0 0);
boundaryField
{
    sides               { type noSlip; }
    domain0_to_potato   { type noSlip; }
}
EOF

cat > $CASE/0/domain0/alphat << 'EOF'
FoamFile { version 2.0; format ascii; class volScalarField; object alphat; }
dimensions      [1 -1 -1 0 0 0 0];
internalField   uniform 0;
boundaryField
{
    sides               { type calculated; value uniform 0; }
    domain0_to_potato   { type calculated; value uniform 0; }
}
EOF

# ── POTATO (SOLID) — Initial fields ─────────────────────────────────────────

mkdir -p $CASE/0/potato

cat > $CASE/0/potato/T << 'EOF'
FoamFile { version 2.0; format ascii; class volScalarField; object T; }
dimensions      [0 0 0 1 0 0 0];
internalField   uniform 453.15;
boundaryField
{
    potato_to_domain0
    {
        type            compressible::turbulentTemperatureCoupledBaffleMixed;
        Tnbr            T;
        kappa           solidThermo;
        kappaName       none;
        value           uniform 453.15;
    }
}
EOF

# ── DOMAIN0 (AIR) — system ────────────────────────────────────────────────────

cat > $CASE/system/domain0/fvSchemes << 'EOF'
FoamFile { version 2.0; format ascii; class dictionary; object fvSchemes; }
ddtSchemes      { default Euler; }
gradSchemes     { default Gauss linear; }
divSchemes
{
    default             none;
    div(phi,U)          Gauss linearUpwind grad(U);
    div(phi,h)          Gauss linearUpwind grad(h);
    div(phi,K)          Gauss linearUpwind grad(K);
    div(((rho*nuEff)*dev2(T(grad(U))))) Gauss linear;
}
laplacianSchemes { default Gauss linear corrected; }
interpolationSchemes { default linear; }
snGradSchemes   { default corrected; }
EOF

cat > $CASE/system/domain0/fvSolution << 'EOF'
FoamFile { version 2.0; format ascii; class dictionary; object fvSolution; }
solvers
{
    rho             { solver PCG; preconditioner DIC; tolerance 1e-7; relTol 0; }
    p_rgh           { solver GAMG; smoother GaussSeidel; tolerance 1e-7; relTol 0.01; }
    p_rghFinal      { $p_rgh; relTol 0; }
    "(U|h|e)"       { solver smoothSolver; smoother symGaussSeidel; tolerance 1e-8; relTol 0.1; }
    "(U|h|e)Final"  { $U; relTol 0; }
}
PIMPLE
{
    nOuterCorrectors    3;
    nCorrectors         2;
    nNonOrthogonalCorrectors 0;
    momentumPredictor   true;
    pRefPoint           (0.15 0.15 0.30);
    pRefValue           101325;
}
relaxationFactors { equations { U 0.9; h 0.9; } }
EOF

# ── POTATO — system ───────────────────────────────────────────────────────────

cat > $CASE/system/potato/fvSchemes << 'EOF'
FoamFile { version 2.0; format ascii; class dictionary; object fvSchemes; }
ddtSchemes      { default Euler; }
gradSchemes     { default Gauss linear; }
divSchemes      { default none; }
laplacianSchemes { default Gauss linear corrected; }
interpolationSchemes { default linear; }
snGradSchemes   { default corrected; }
EOF

cat > $CASE/system/potato/fvSolution << 'EOF'
FoamFile { version 2.0; format ascii; class dictionary; object fvSolution; }
solvers
{
    h           { solver smoothSolver; smoother symGaussSeidel; tolerance 1e-8; relTol 0.1; }
    hFinal      { $h; relTol 0; }
}
PIMPLE { nNonOrthogonalCorrectors 0; }
EOF

# ── constant/ — thermophysical properties ────────────────────────────────────

cat > $CASE/constant/domain0/thermophysicalProperties << 'EOF'
FoamFile { version 2.0; format ascii; class dictionary; object thermophysicalProperties; }
thermoType
{
    type            heRhoThermo;
    mixture         pureMixture;
    transport       const;
    thermo          hConst;
    equationOfState perfectGas;
    specie          specie;
    energy          sensibleEnthalpy;
}
mixture
{
    specie          { molWeight 28.97; }
    thermodynamics  { Cp 1007; Hf 0; }
    transport       { mu 1.85e-5; Pr 0.713; }
}
EOF

cat > $CASE/constant/domain0/turbulenceProperties << 'EOF'
FoamFile { version 2.0; format ascii; class dictionary; object turbulenceProperties; }
simulationType laminar;
EOF

cat > $CASE/constant/domain0/g << 'EOF'
FoamFile { version 2.0; format ascii; class uniformDimensionedVectorField; object g; }
dimensions  [0 1 -2 0 0 0 0];
value       (0 0 -9.81);
EOF

cat > $CASE/constant/potato/thermophysicalProperties << 'EOF'
FoamFile { version 2.0; format ascii; class dictionary; object thermophysicalProperties; }
thermoType
{
    type            heSolidThermo;
    mixture         pureMixture;
    transport       constIso;
    thermo          hConst;
    equationOfState rhoConst;
    specie          specie;
    energy          sensibleEnthalpy;
}
mixture
{
    specie          { molWeight 18; nMoles 1; }
    transport       { kappa 0.56; }
    thermodynamics  { Cp 3600; Hf 0; }
    equationOfState { rho 1050; }
}
EOF

cat > $CASE/constant/potato/radiationProperties << 'EOF'
FoamFile { version 2.0; format ascii; class dictionary; object radiationProperties; }
radiationModel  none;
EOF

echo "=== Done writing fields ==="
ls $CASE/0/domain0/
ls $CASE/0/potato/
