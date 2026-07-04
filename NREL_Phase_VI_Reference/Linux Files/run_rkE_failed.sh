#!/bin/bash
# Re-run the 4 realizableKE cases that crashed with FPE.
# Fixes applied:
#   1. epsilon relaxation reduced to 0.3
#   2. IC copied from converged kOmegaSST solution (same wind speed)

source /home/rinkoa/OpenFOAM-v2012/etc/bashrc

SIMS="/home/rinkoa/OpenFOAM-v2012/sims/NREL_Phase_VI"
BASE="$SIMS/base_case"
PP="$SIMS/postProcess"
RESULTS="$SIMS/results"
CSV="$RESULTS/torque_realizableKE.csv"
NPROC=8

WINDSPEEDS="5 13 18 21"

echo "=============================="
echo " realizableKE — failed cases retry"
echo " $(date)"
echo "=============================="

for VWIND in $WINDSPEEDS; do
    CASE="$SIMS/cases/realizableKE_V${VWIND}"
    DONOR="$SIMS/cases/kOmegaSST_V${VWIND}"

    echo ""
    echo "--- realizableKE V=${VWIND} m/s  $(date) ---"

    rm -rf "$CASE"
    cp -r "$BASE" "$CASE"

    # Use turbulenceProperties for realizableKE
    cp "$CASE/constant/turbulenceProperties.realizableKE" \
       "$CASE/constant/turbulenceProperties"

    # Tighten epsilon relaxation to 0.3 to prevent FPE
    sed -i 's/epsilon         0.7/epsilon         0.3/' "$CASE/system/fvSolution"

    # Compute turbulence ICs for this wind speed
    K=$(python3   -c "I=0.005; V=$VWIND; print(f'{1.5*(V*I)**2:.4e}')")
    OM=$(python3  -c "import math; k=1.5*($VWIND*0.005)**2; L=0.3; print(f'{math.sqrt(k)/(0.5477*L):.4f}')")
    EPS=$(python3 -c "import math; k=1.5*($VWIND*0.005)**2; L=0.3; print(f'{0.1644*k**1.5/L:.4e}')")

    sed -i "s|uniform (7 0 0)|uniform ($VWIND 0 0)|g"            "$CASE/0/U"
    sed -i "s|uniform 1.84e-3|uniform $K|g"                       "$CASE/0/k"
    sed -i "s|inletValue uniform 1.84e-3|inletValue uniform $K|g" "$CASE/0/k"
    sed -i "s|uniform 0.261|uniform $OM|g"                        "$CASE/0/omega"
    sed -i "s|uniform 4.33e-5|uniform $EPS|g"                     "$CASE/0/epsilon"
    sed -i "s|inletValue uniform 4.33e-5|inletValue uniform $EPS|g" "$CASE/0/epsilon"

    # Warm-start: overwrite 0/U and 0/p from converged kOmegaSST solution
    DONOR_T=$(ls "$DONOR" 2>/dev/null | grep -E '^[0-9]+$' | sort -n | tail -1)
    if [ -n "$DONOR_T" ] && [ -f "$DONOR/$DONOR_T/U" ]; then
        echo "  Using kOmegaSST V=${VWIND} t=${DONOR_T} as IC"
        cp "$DONOR/$DONOR_T/U" "$CASE/0/U"
        cp "$DONOR/$DONOR_T/p" "$CASE/0/p"
        sed -i "s|uniform ($VWIND 0 0)|uniform ($VWIND 0 0)|g" "$CASE/0/U"
    else
        echo "  No donor solution found — using cold start"
    fi

    cd "$CASE"
    decomposePar  > log.decomposePar  2>&1
    mpirun -np $NPROC simpleFoam -parallel > log.simpleFoam 2>&1
    SF_EXIT=$?
    reconstructPar > log.reconstructPar 2>&1
    cd "$SIMS"

    if [ $SF_EXIT -ne 0 ]; then
        echo "  [ERROR] simpleFoam failed — check $CASE/log.simpleFoam"
        continue
    fi

    python3 "$PP/extract_torque.py" \
        --case "$CASE" \
        --model "realizableKE" \
        --vwind "$VWIND" \
        --output "$CSV"
done

echo ""
echo "Done. Regenerating plot..."
python3 "$PP/plot_validation.py"
echo "Plot: $SIMS/plots/turbulence_model_validation.png"
