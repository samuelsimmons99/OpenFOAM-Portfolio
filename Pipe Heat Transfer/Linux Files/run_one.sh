#!/bin/bash
# Run a single PipeHeatTransfer case
# Usage: bash run_one.sh <case_name> <Re> <model:laminar|turbulent>
source /home/rinkoa/OpenFOAM-v2012/etc/bashrc

NAME=$1; RE=$2; MODEL=$3
BASE=/home/rinkoa/OpenFOAM-v2012/sims/PipeHeatTransfer/base_case
CASES=/home/rinkoa/OpenFOAM-v2012/sims/PipeHeatTransfer/cases
D=0.05; NU=1.5e-5

UBULK=$(python3 -c "print($RE * $NU / $D)")
DEST="$CASES/$NAME"
echo "=== $NAME  Re=$RE  Ubulk=$UBULK m/s  model=$MODEL ==="

rm -rf "$DEST"
cp -r "$BASE" "$DEST"

if [ "$MODEL" = "laminar" ]; then
    cp "$DEST/constant/turbulenceProperties.laminar" "$DEST/constant/turbulenceProperties"
else
    cp "$DEST/constant/turbulenceProperties.kOmegaSST" "$DEST/constant/turbulenceProperties"
fi

# Set velocity
U_STR="(0 0 $UBULK)"
sed -i "s|uniform (0 0 0.15)|uniform $U_STR|g" "$DEST/0/U"

if [ "$MODEL" = "turbulent" ]; then
    TI=0.05
    K=$(python3 -c "print($TI * $TI * $UBULK * $UBULK * 1.5)")
    L=$(python3 -c "print(0.07 * $D / 2)")
    OMEGA=$(python3 -c "import math; k=$K; L=$L; print(0.09**0.25 * math.sqrt(k) / L)")
    sed -i "s|uniform 1.69e-4|uniform $K|g" "$DEST/0/k"
    sed -i "s|uniform 3.0|uniform $OMEGA|g" "$DEST/0/omega"
fi

cd "$DEST"
echo "  blockMesh..."
blockMesh > log.blockMesh 2>&1
echo "  buoyantSimpleFoam..."
buoyantSimpleFoam > log.solver 2>&1
EXIT=$?
echo "  Exit: $EXIT"
tail -3 log.solver
echo "=== Done: $NAME ==="
