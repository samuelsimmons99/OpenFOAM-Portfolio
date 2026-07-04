#!/bin/bash
# PipeFlow — laminar + turbulent Re sweep
# Axisymmetric wedge, periodic BC, meanVelocityForce driving
# Validation against Moody chart (Hagen-Poiseuille + Blasius/Colebrook)
#
# Usage: nohup bash run_sweep.sh > log.sweep 2>&1 &

source /home/rinkoa/OpenFOAM-v2012/etc/bashrc

SIMS="/home/rinkoa/OpenFOAM-v2012/sims/PipeFlow"
BASE="$SIMS/base_case"
PP="$SIMS/postProcess"
RESULTS="$SIMS/results"

D=0.05          # pipe diameter [m]
NU=1.5e-5       # kinematic viscosity [m²/s]
RHO=1.2         # density [kg/m³] (for shear stress → friction factor)

mkdir -p "$SIMS/cases" "$RESULTS"

# Re cases: laminar (100-2000) + turbulent (5000-50000)
# Skip 2300-4000: transitional — RANS cannot capture intermittency
LAMINAR_RE="100 500 1000 2000"
TURB_RE="5000 10000 20000 50000"

CSV="$RESULTS/friction_factors.csv"
echo "model,Re,Ubulk,f_cfd,f_theory" > "$CSV"

START_TIME=$(date)
echo "=============================="
echo " PipeFlow sweep — started $START_TIME"
echo "=============================="

run_case() {
    local MODEL=$1
    local RE=$2
    local CASE="$SIMS/cases/${MODEL}_Re${RE}"

    # Ubulk = Re * nu / D
    local UBULK=$(python3 -c "print(f'{$RE * $NU / $D:.6f}')")

    echo ""
    echo "--- ${MODEL}  Re=${RE}  Ubulk=${UBULK} m/s  $(date) ---"

    rm -rf "$CASE"
    cp -r "$BASE" "$CASE"

    # Set turbulence model
    cp "$CASE/constant/turbulenceProperties.${MODEL}" \
       "$CASE/constant/turbulenceProperties"

    # Set target bulk velocity in fvOptions and initial U
    sed -i "s|Ubar.*$|Ubar            (0 0 ${UBULK});|" "$CASE/system/fvOptions"
    sed -i "s|internalField.*uniform.*$|internalField   uniform (0 0 ${UBULK});|" "$CASE/0/U"

    if [ "$MODEL" = "laminar" ]; then
        rm -f "$CASE/0/k" "$CASE/0/omega" "$CASE/0/nut"
    else
        # Turbulence ICs: I=5%, l = 0.07*R
        local K=$(python3 -c "U=$UBULK; print(f'{1.5*(U*0.05)**2:.4e}')")
        local OM=$(python3 -c "import math; k=1.5*($UBULK*0.05)**2; l=0.07*$D/2; print(f'{math.sqrt(k)/(0.5477*l):.4f}')")
        sed -i "s|internalField.*uniform.*$|internalField   uniform $K;|" "$CASE/0/k"
        sed -i "s|value.*uniform.*$|value           uniform $K;|"          "$CASE/0/k"
        sed -i "s|internalField.*uniform.*$|internalField   uniform $OM;|" "$CASE/0/omega"
        sed -i "s|value.*uniform.*$|value           uniform $OM;|"         "$CASE/0/omega"
    fi

    # Build mesh (only needed once — reuse if already built)
    if [ ! -d "$CASE/constant/polyMesh" ]; then
        cd "$CASE"
        blockMesh > log.blockMesh 2>&1
        cd "$SIMS"
    fi

    cd "$CASE"
    simpleFoam > log.simpleFoam 2>&1
    SF_EXIT=$?
    cd "$SIMS"

    if [ $SF_EXIT -ne 0 ]; then
        echo "  [ERROR] simpleFoam failed — Re=${RE} ${MODEL}"
        return
    fi

    python3 "$PP/extract_friction.py" \
        --case "$CASE" \
        --model "$MODEL" \
        --Re "$RE" \
        --Ubulk "$UBULK" \
        --nu "$NU" \
        --rho "$RHO" \
        --D "$D" \
        --output "$CSV"
}

for RE in $LAMINAR_RE; do
    run_case laminar $RE
done

for RE in $TURB_RE; do
    run_case kOmegaSST $RE
done

echo ""
echo "=============================="
echo " All cases done — $START_TIME → $(date)"
echo "=============================="

python3 "$PP/plot_moody.py"
echo "Plot: $SIMS/plots/moody_validation.png"
