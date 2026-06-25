#!/bin/bash
# Run all parametric heatsink cases sequentially.
# For parallel: change the solver line to use mpirun.

set -e

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"

for CASE_DIR in "$SCRIPT_DIR"/pitch_*; do
    [ -d "$CASE_DIR" ] || continue
    CASE_NAME=$(basename "$CASE_DIR")
    echo "========================================"
    echo "Running case: $CASE_NAME"
    echo "========================================"

    cd "$CASE_DIR"

    # 1. Generate mesh
    echo "[1/3] blockMesh..."
    blockMesh > log.blockMesh 2>&1

    # 2. Split into fluid/solid regions
    echo "[2/3] splitMeshRegions..."
    splitMeshRegions -cellZones -overwrite > log.splitMeshRegions 2>&1

    # 3. Run solver
    echo "[3/3] chtMultiRegionSimpleFoam..."
    chtMultiRegionSimpleFoam > log.solver 2>&1

    echo "Done: $CASE_NAME"
    echo ""
done

echo "All cases complete."
echo ""
echo "Extract results with:"
echo "  python3 $SCRIPT_DIR/extract_results.py"
