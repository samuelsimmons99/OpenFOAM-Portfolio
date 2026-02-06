#!/bin/bash

foamCleanTutorials
blockMesh | tee log.blockMesh
modifyMesh -overwrite 
checkMesh | tee log.checkMesh
icoFoam | tee log.icoFoam

