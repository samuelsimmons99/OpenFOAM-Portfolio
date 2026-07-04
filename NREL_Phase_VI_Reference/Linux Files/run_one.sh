#!/bin/bash
# Run a single case: MODEL VWIND
# Usage: ./run_one.sh kOmegaSST 7
MODEL="$1"
VWIND="$2"
SIMS="/home/rinkoa/OpenFOAM-v2012/sims/NREL_Phase_VI"
BASE="$SIMS/base_case"
CASE="$SIMS/cases/${MODEL}_V${VWIND}"
PP="$SIMS/postProcess"
RESULTS="$SIMS/results"

source /home/rinkoa/OpenFOAM-v2012/etc/bashrc

echo "=== $MODEL V=${VWIND} m/s ==="
echo "BASE=$BASE"
echo "CASE=$CASE"

mkdir -p "$SIMS/cases" "$RESULTS"

rm -rf "$CASE"
cp -r "$BASE" "$CASE"
echo "Copied base_case to $CASE"

# Set turbulence model
cp "$CASE/constant/turbulenceProperties.${MODEL}" \
   "$CASE/constant/turbulenceProperties"

# Compute turbulence BCs
K=$(python3 -c "I=0.005; V=$VWIND; print(f'{1.5*(V*I)**2:.4e}')")
OM=$(python3 -c "import math; k=1.5*($VWIND*0.005)**2; L=0.3; print(f'{math.sqrt(k)/(0.5477*L):.4f}')")
EPS=$(python3 -c "import math; k=1.5*($VWIND*0.005)**2; L=0.3; print(f'{0.1644*k**1.5/L:.4e}')")

echo "K=$K  OM=$OM  EPS=$EPS"

sed -i "s|uniform (7 0 0)|uniform ($VWIND 0 0)|g"    "$CASE/0/U"
sed -i "s|uniform 1.84e-3|uniform $K|g"               "$CASE/0/k"
sed -i "s|inletValue uniform 1.84e-3|inletValue uniform $K|g" "$CASE/0/k"
sed -i "s|uniform 0.261|uniform $OM|g"                "$CASE/0/omega"
sed -i "s|uniform 4.33e-5|uniform $EPS|g"             "$CASE/0/epsilon"
sed -i "s|inletValue uniform 4.33e-5|inletValue uniform $EPS|g" "$CASE/0/epsilon"

if [ "$MODEL" = "laminar" ]; then
    rm -f "$CASE/0/k" "$CASE/0/omega" "$CASE/0/epsilon" "$CASE/0/nut"
fi

cd "$CASE"
echo "Running simpleFoam..."
simpleFoam > log.simpleFoam 2>&1
echo "Exit: $?"
tail -3 log.simpleFoam

python3 "$PP/extract_torque.py" \
    --case "$CASE" \
    --model "$MODEL" \
    --vwind "$VWIND" \
    --output "$RESULTS/torque_${MODEL}.csv"
