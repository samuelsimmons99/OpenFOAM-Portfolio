#!/bin/bash
source /home/rinkoa/OpenFOAM-v2012/etc/bashrc
CASE=/home/rinkoa/OpenFOAM-v2012/sims/PipeHeatTransfer/cases/test_laminar_Re500

if [ ! -d "$CASE" ]; then
    echo "Test case not found"
    ls /home/rinkoa/OpenFOAM-v2012/sims/PipeHeatTransfer/cases/
    exit 1
fi

cat > "$CASE/system/sets" << 'EOF'
FoamFile
{
    version     2.0;
    format      ascii;
    class       dictionary;
    object      sampleDict;
}

type            sets;
libs            ("libsampling.so");
interpolationScheme cellPoint;
setFormat       raw;
fields          (T U);

sets
(
    radialProfile_z2p4
    {
        type    uniform;
        axis    x;
        start   (0.0001  0  2.4);
        end     (0.025   0  2.4);
        nPoints 50;
    }
);
EOF

cd "$CASE"
echo "Running postProcess sets..."
postProcess -func sets -latestTime 2>&1 | tail -5
echo "---"
find "$CASE/postProcessing" -name "*.xy" 2>/dev/null | head -5
