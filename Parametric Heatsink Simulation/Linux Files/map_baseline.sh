#!/usr/bin/env bash
# Seed a new fin-pitch case from the converged p5_cpu (5mm) baseline instead of
# starting from a flat 300K initial field. Cuts iterations needed to converge
# since the new pitch's flow/thermal field is close to the baseline's.
#
# Run AFTER blockMesh + splitMeshRegions -cellZones have built the new case's
# mesh, and BEFORE starting foamMultiRun on it.
#
# Usage: ./map_baseline.sh <new_case_dir>   (e.g. ./map_baseline.sh p4_cpu)

set -euo pipefail
SRC="p5_cpu"
DST="${1:?Usage: map_baseline.sh <new_case_dir>}"

if [ ! -d "$SRC" ] || [ ! -d "$DST" ]; then
    echo "Expected both $SRC and $DST to exist as case directories in $(pwd)" >&2
    exit 1
fi

for region in fluid heatsink cpu; do
    echo "Mapping region '$region': $SRC -> $DST"
    mapFields "$SRC" -case "$DST" -region "$region" -sourceTime latestTime -consistent
done

echo "Done. $DST/0/* now seeded from $SRC's converged fields (mesh-interpolated)."
echo "Review $DST/0/<region>/T and U before launching foamMultiRun."
