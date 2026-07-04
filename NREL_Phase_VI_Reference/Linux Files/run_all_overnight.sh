#!/bin/bash
# NREL Phase VI — full sweep (parallel)
# 3 models × 7 wind speeds = 21 cases, 8-core MPI simpleFoam
# Run with:  nohup bash run_all_overnight.sh > log.overnight 2>&1 &

source /home/rinkoa/OpenFOAM-v2012/etc/bashrc

SIMS="/home/rinkoa/OpenFOAM-v2012/sims/NREL_Phase_VI"
BASE="$SIMS/base_case"
PP="$SIMS/postProcess"
RESULTS="$SIMS/results"
NPROC=8

MODELS="kOmegaSST realizableKE laminar"
WINDSPEEDS="5 7 10 13 15 18 21"

mkdir -p "$SIMS/cases" "$RESULTS"

START_TIME=$(date)
echo "=============================="
echo " NREL Phase VI — parallel sweep"
echo " $NPROC cores  |  Started: $START_TIME"
echo "=============================="

TOTAL=0; DONE=0
for M in $MODELS; do for V in $WINDSPEEDS; do TOTAL=$((TOTAL+1)); done; done

for MODEL in $MODELS; do
    for VWIND in $WINDSPEEDS; do
        CASE="$SIMS/cases/${MODEL}_V${VWIND}"
        CSV="$RESULTS/torque_${MODEL}.csv"

        if grep -q "^${MODEL},${VWIND}" "$CSV" 2>/dev/null; then
            echo "[SKIP] ${MODEL} V=${VWIND} already done"
            DONE=$((DONE+1))
            continue
        fi

        DONE=$((DONE+1))
        echo ""
        echo "--------------------------------------"
        echo " Case $DONE/$TOTAL: ${MODEL}  V=${VWIND} m/s  $(date)"
        echo "--------------------------------------"

        rm -rf "$CASE"
        cp -r "$BASE" "$CASE"

        cp "$CASE/constant/turbulenceProperties.${MODEL}" \
           "$CASE/constant/turbulenceProperties"

        K=$(python3   -c "I=0.005; V=$VWIND; print(f'{1.5*(V*I)**2:.4e}')")
        OM=$(python3  -c "import math; k=1.5*($VWIND*0.005)**2; L=0.3; print(f'{math.sqrt(k)/(0.5477*L):.4f}')")
        EPS=$(python3 -c "import math; k=1.5*($VWIND*0.005)**2; L=0.3; print(f'{0.1644*k**1.5/L:.4e}')")

        sed -i "s|uniform (7 0 0)|uniform ($VWIND 0 0)|g"            "$CASE/0/U"
        sed -i "s|uniform 1.84e-3|uniform $K|g"                       "$CASE/0/k"
        sed -i "s|inletValue uniform 1.84e-3|inletValue uniform $K|g" "$CASE/0/k"
        sed -i "s|uniform 0.261|uniform $OM|g"                        "$CASE/0/omega"
        sed -i "s|uniform 4.33e-5|uniform $EPS|g"                     "$CASE/0/epsilon"
        sed -i "s|inletValue uniform 4.33e-5|inletValue uniform $EPS|g" "$CASE/0/epsilon"

        if [ "$MODEL" = "laminar" ]; then
            rm -f "$CASE/0/k" "$CASE/0/omega" "$CASE/0/epsilon" "$CASE/0/nut"
        fi

        cd "$CASE"
        decomposePar  > log.decomposePar  2>&1
        mpirun -np $NPROC simpleFoam -parallel > log.simpleFoam 2>&1
        SF_EXIT=$?
        reconstructPar > log.reconstructPar 2>&1
        cd "$SIMS"

        if [ $SF_EXIT -ne 0 ]; then
            echo "[ERROR] simpleFoam failed for ${MODEL} V=${VWIND} — check $CASE/log.simpleFoam"
            continue
        fi

        python3 "$PP/extract_torque.py" \
            --case "$CASE" \
            --model "$MODEL" \
            --vwind "$VWIND" \
            --output "$CSV"
    done
done

echo ""
echo "=============================="
echo " All cases complete!"
echo " Started:  $START_TIME"
echo " Finished: $(date)"
echo "=============================="
echo ""
python3 "$PP/plot_validation.py"
echo "Plot: $SIMS/plots/turbulence_model_validation.png"
