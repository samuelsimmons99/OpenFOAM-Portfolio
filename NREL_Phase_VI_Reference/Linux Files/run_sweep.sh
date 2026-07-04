#!/bin/bash
# Run one turbulence model across all 7 wind speeds.
# Usage: ./run_sweep.sh kOmegaSST
#        ./run_sweep.sh kEpsilon
#        ./run_sweep.sh laminar

set -e
source /home/rinkoa/OpenFOAM-v2012/etc/bashrc

MODEL="${1:-kOmegaSST}"
WINDSPEEDS="5 7 10 13 15 18 21"
BASE="/home/rinkoa/OpenFOAM-v2012/sims/NREL_Phase_VI/base_case"
CASES="/home/rinkoa/OpenFOAM-v2012/sims/NREL_Phase_VI/cases"
RESULTS="/home/rinkoa/OpenFOAM-v2012/sims/NREL_Phase_VI/results"
PP="/home/rinkoa/OpenFOAM-v2012/sims/NREL_Phase_VI/postProcess"

mkdir -p "$CASES" "$RESULTS"

for VWIND in $WINDSPEEDS; do
    # Skip if we already have a result for this case
    if grep -q "^${MODEL},${VWIND}," "$RESULTS/torque_${MODEL}.csv" 2>/dev/null; then
        echo "=== SKIP: ${MODEL} V=${VWIND} (already in CSV) ==="
        continue
    fi

    CASE="${CASES}/${MODEL}_V${VWIND}"
    echo ""
    echo "=== ${MODEL}  V=${VWIND} m/s ==="

    # Copy mesh from base_case
    rm -rf "$CASE"
    cp -r "$BASE" "$CASE"

    # Set turbulence model
    cp "$CASE/constant/turbulenceProperties.${MODEL}" \
       "$CASE/constant/turbulenceProperties"

    # Scale turbulence BCs for this wind speed (I=0.5%)
    K=$(python3 -c "I=0.005; V=$VWIND; print(f'{1.5*(V*I)**2:.4e}')")
    OM=$(python3 -c "import math; k=1.5*($VWIND*0.005)**2; L=0.3; print(f'{math.sqrt(k)/(0.5477*L):.4f}')")
    EPS=$(python3 -c "import math; k=1.5*($VWIND*0.005)**2; L=0.3; print(f'{0.1644*k**1.5/L:.4e}')")

    sed -i "s|uniform (7 0 0)|uniform ($VWIND 0 0)|g" "$CASE/0/U"
    sed -i "s|uniform 1.84e-3|uniform $K|g"             "$CASE/0/k"
    sed -i "s|inletValue uniform 1.84e-3|inletValue uniform $K|g" "$CASE/0/k"
    sed -i "s|uniform 0.261|uniform $OM|g"              "$CASE/0/omega"
    sed -i "s|uniform 4.33e-5|uniform $EPS|g"           "$CASE/0/epsilon"
    sed -i "s|inletValue uniform 4.33e-5|inletValue uniform $EPS|g" "$CASE/0/epsilon"

    # For laminar: remove turbulence fields
    if [ "$MODEL" = "laminar" ]; then
        rm -f "$CASE/0/k" "$CASE/0/omega" "$CASE/0/epsilon" "$CASE/0/nut"
    fi

    # Run
    cd "$CASE"
    simpleFoam > log.simpleFoam 2>&1
    cd -

    # Extract torque
    python3 "$PP/extract_torque.py" \
        --case "$CASE" \
        --model "$MODEL" \
        --vwind "$VWIND" \
        --output "$RESULTS/torque_${MODEL}.csv"

    echo "  Done."
done

echo ""
echo "=== ${MODEL} sweep complete. ==="
echo "Results: $RESULTS/torque_${MODEL}.csv"
