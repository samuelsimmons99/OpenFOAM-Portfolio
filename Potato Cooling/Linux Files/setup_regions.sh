#!/bin/bash
# Write all region-level files after splitMeshRegions
source /home/rinkoa/OpenFOAM-v2012/etc/bashrc
CASE=/home/rinkoa/OpenFOAM-v2012/sims/PotatoCooling

# ── AIR REGION ─────────────────────────────────────────────────────────────────

mkdir -p $CASE/air/{0,system,constant}

# constant/thermophysicalProperties (air, perfectGas)
cat > $CASE/air/constant/thermophysicalProperties << 'EOF'
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

# constant/turbulenceProperties (laminar — Ra ~ 3e6, laminar convection)
cat > $CASE/air/constant/turbulenceProperties << 'EOF'
FoamFile { version 2.0; format ascii; class dictionary; object turbulenceProperties; }
simulationType laminar;
EOF

# constant/g
cp $CASE/constant/g $CASE/air/constant/g

# 0/T (air)
cat > $CASE/air/0/T << 'EOF'
FoamFile { version 2.0; format ascii; class volScalarField; object T; }
dimensions      [0 0 0 1 0 0 0];
internalField   uniform 298.15;
boundaryField
{
    sides           { type fixedValue; value uniform 298.15; }
    ".*_to_air"     { type compressible::turbulentTemperatureCoupledBaffleMixed;
                      Tnbr T; kappa fluidThermo; kappaName none;
                      value uniform 398.15; }
}
EOF

# 0/p_rgh
cat > $CASE/air/0/p_rgh << 'EOF'
FoamFile { version 2.0; format ascii; class volScalarField; object p_rgh; }
dimensions      [1 -1 -2 0 0 0 0];
internalField   uniform 101325;
boundaryField
{
    sides       { type fixedFluxPressure; value uniform 101325; }
    ".*_to_air" { type fixedFluxPressure; value uniform 101325; }
}
EOF

# 0/p
cat > $CASE/air/0/p << 'EOF'
FoamFile { version 2.0; format ascii; class volScalarField; object p; }
dimensions      [1 -1 -2 0 0 0 0];
internalField   uniform 101325;
boundaryField
{
    sides       { type calculated; value uniform 101325; }
    ".*_to_air" { type calculated; value uniform 101325; }
}
EOF

# 0/U
cat > $CASE/air/0/U << 'EOF'
FoamFile { version 2.0; format ascii; class volVectorField; object U; }
dimensions      [0 1 -1 0 0 0 0];
internalField   uniform (0 0 0);
boundaryField
{
    sides       { type noSlip; }
    ".*_to_air" { type noSlip; }
}
EOF

# 0/alphat
cat > $CASE/air/0/alphat << 'EOF'
FoamFile { version 2.0; format ascii; class volScalarField; object alphat; }
dimensions      [1 -1 -1 0 0 0 0];
internalField   uniform 0;
boundaryField
{
    sides       { type calculated; value uniform 0; }
    ".*_to_air" { type calculated; value uniform 0; }
}
EOF

# system/fvSchemes (air)
cat > $CASE/air/system/fvSchemes << 'EOF'
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

# system/fvSolution (air)
cat > $CASE/air/system/fvSolution << 'EOF'
FoamFile { version 2.0; format ascii; class dictionary; object fvSolution; }
solvers
{
    rho
    {
        solver          PCG;
        preconditioner  DIC;
        tolerance       1e-7;
        relTol          0;
    }
    p_rgh
    {
        solver          GAMG;
        smoother        GaussSeidel;
        tolerance       1e-7;
        relTol          0.01;
    }
    p_rghFinal
    {
        $p_rgh;
        relTol          0;
    }
    "(U|h|e)"
    {
        solver          smoothSolver;
        smoother        symGaussSeidel;
        tolerance       1e-8;
        relTol          0.1;
    }
    "(U|h|e)Final"
    {
        $U;
        relTol          0;
    }
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
relaxationFactors
{
    equations
    {
        U       0.9;
        h       0.9;
    }
}
EOF

# system/controlDict (region — inherits top-level but region needs its own)
cat > $CASE/air/system/controlDict << 'EOF'
FoamFile { version 2.0; format ascii; class dictionary; object controlDict; }
libs ();
EOF

# ── POTATO REGION ──────────────────────────────────────────────────────────────

mkdir -p $CASE/potato/{0,system,constant}

# constant/thermophysicalProperties (potato solid)
cat > $CASE/potato/constant/thermophysicalProperties << 'EOF'
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

# constant/radiationProperties (no radiation)
cat > $CASE/potato/constant/radiationProperties << 'EOF'
FoamFile { version 2.0; format ascii; class dictionary; object radiationProperties; }
radiationModel  none;
EOF

# 0/T (potato — hot at start)
cat > $CASE/potato/0/T << 'EOF'
FoamFile { version 2.0; format ascii; class volScalarField; object T; }
dimensions      [0 0 0 1 0 0 0];
internalField   uniform 453.15;
boundaryField
{
    ".*_to_potato"  { type compressible::turbulentTemperatureCoupledBaffleMixed;
                      Tnbr T; kappa solidThermo; kappaName none;
                      value uniform 453.15; }
}
EOF

# system/fvSchemes (potato)
cat > $CASE/potato/system/fvSchemes << 'EOF'
FoamFile { version 2.0; format ascii; class dictionary; object fvSchemes; }
ddtSchemes      { default Euler; }
gradSchemes     { default Gauss linear; }
divSchemes      { default none; }
laplacianSchemes { default Gauss linear corrected; }
interpolationSchemes { default linear; }
snGradSchemes   { default corrected; }
EOF

# system/fvSolution (potato)
cat > $CASE/potato/system/fvSolution << 'EOF'
FoamFile { version 2.0; format ascii; class dictionary; object fvSolution; }
solvers
{
    h
    {
        solver          smoothSolver;
        smoother        symGaussSeidel;
        tolerance       1e-8;
        relTol          0.1;
    }
    hFinal
    {
        $h;
        relTol          0;
    }
}
PIMPLE { nNonOrthogonalCorrectors 0; }
EOF

# system/controlDict (region stub)
cat > $CASE/potato/system/controlDict << 'EOF'
FoamFile { version 2.0; format ascii; class dictionary; object controlDict; }
libs ();
EOF

echo "=== Region files written ==="
echo "Air:    $(ls $CASE/air/0/) $(ls $CASE/air/system/) $(ls $CASE/air/constant/)"
echo "Potato: $(ls $CASE/potato/0/) $(ls $CASE/potato/system/) $(ls $CASE/potato/constant/)"
