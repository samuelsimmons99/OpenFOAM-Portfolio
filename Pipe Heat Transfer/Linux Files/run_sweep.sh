#!/bin/bash
# Pipe heat transfer sweep: laminar (Re=500,1000,2000) + turbulent (Re=5000,10000,20000,50000)
source /home/rinkoa/OpenFOAM-v2012/etc/bashrc

BASE=/home/rinkoa/OpenFOAM-v2012/sims/PipeHeatTransfer/base_case
CASES=/home/rinkoa/OpenFOAM-v2012/sims/PipeHeatTransfer/cases
RESULTS=/home/rinkoa/OpenFOAM-v2012/sims/PipeHeatTransfer/results
mkdir -p "$RESULTS"

D=0.05   # [m]
NU=1.5e-5

run_case() {
    local NAME=$1
    local RE=$2
    local MODEL=$3  # laminar or turbulent

    UBULK=$(python3 -c "print($RE * $NU / $D)")
    DEST="$CASES/$NAME"
    echo "=== $NAME  Re=$RE  U=$UBULK m/s  model=$MODEL ==="

    rm -rf "$DEST"
    cp -r "$BASE" "$DEST"

    # Set turbulenceProperties
    if [ "$MODEL" = "laminar" ]; then
        cp "$DEST/constant/turbulenceProperties.laminar" "$DEST/constant/turbulenceProperties"
    else
        cp "$DEST/constant/turbulenceProperties.kOmegaSST" "$DEST/constant/turbulenceProperties"
    fi

    # Set velocity
    local U_STR="(0 0 $UBULK)"
    sed -i "s|uniform (0 0 0.15)|uniform $U_STR|g" "$DEST/0/U"

    # Estimate k and omega for turbulent cases (5% turbulence intensity)
    if [ "$MODEL" = "turbulent" ]; then
        local TI=0.05
        local K=$(python3 -c "print($TI * $TI * $UBULK * $UBULK * 1.5)")
        local L=$(python3 -c "print(0.07 * $D / 2)")
        local OMEGA=$(python3 -c "import math; k=$K; L=$L; print(0.09**0.25 * math.sqrt(k) / L)")
        sed -i "s|uniform 1.69e-4|uniform $K|g" "$DEST/0/k"
        sed -i "s|uniform 3.0|uniform $OMEGA|g" "$DEST/0/omega"
    fi

    # No sampledSets needed — extract_nu.py reads fields directly

    cd "$DEST"
    blockMesh > log.blockMesh 2>&1

    buoyantSimpleFoam > log.solver 2>&1
    echo "  Exit: $?"


    # Copy results
    mkdir -p "$RESULTS"
    cp log.solver "$RESULTS/${NAME}_log.txt" 2>/dev/null

    echo "  Done."
}

# Laminar cases
run_case "lam_Re500"   500   laminar
run_case "lam_Re1000"  1000  laminar
run_case "lam_Re2000"  2000  laminar

# Turbulent cases
run_case "turb_Re5000"  5000  turbulent
run_case "turb_Re10000" 10000 turbulent
run_case "turb_Re20000" 20000 turbulent
run_case "turb_Re50000" 50000 turbulent

echo "=== Sweep complete ==="
