#!/usr/bin/env python

###
### This file is generated automatically by SALOME v9.15.0 with dump python functionality
###

import sys
import salome

salome.salome_init()
import salome_notebook
notebook = salome_notebook.NoteBook()
sys.path.insert(0, r'C:/Users/Samue/Documents/GitHub/OpenFOAM-Portfolio/OpenFOAM-Portfolio/Smoking Pipe Tutorial')

###
### GEOM component
###

import GEOM
from salome.geom import geomBuilder
import math
import SALOMEDS


geompy = geomBuilder.New()

O = geompy.MakeVertex(0, 0, 0)
OX = geompy.MakeVectorDXDYDZ(1, 0, 0)
OY = geompy.MakeVectorDXDYDZ(0, 1, 0)
OZ = geompy.MakeVectorDXDYDZ(0, 0, 1)
RV_Submission_rev_3_stl = geompy.ImportSTEP("C:/Users/Samue/Documents/GitHub/OpenFOAM-Portfolio/OpenFOAM-Portfolio/Smoking Pipe Tutorial/smoking_pipe.STEP", False, True)
Inlet = geompy.CreateGroup(RV_Submission_rev_3_stl, geompy.ShapeType["FACE"])
geompy.UnionIDs(Inlet, [283])
Outlet = geompy.CreateGroup(RV_Submission_rev_3_stl, geompy.ShapeType["FACE"])
geompy.UnionIDs(Outlet, [4])
Walls = geompy.CreateGroup(RV_Submission_rev_3_stl, geompy.ShapeType["FACE"])
geompy.UnionIDs(Walls, [279, 248, 208, 91, 138, 84, 49, 100, 177, 257, 260, 224, 193, 159, 135, 29, 105, 42, 268, 277, 205, 184, 154, 118, 145, 113, 200, 275, 266, 16, 254, 221, 162, 125, 22, 74, 82, 79, 271])
[Inlet, Outlet, Walls] = geompy.GetExistingSubObjects(RV_Submission_rev_3_stl, False)
geompy.DifferenceIDs(Walls, [279, 248, 208, 91, 138, 84, 49, 100, 177, 257, 260, 224, 193, 159, 135, 29, 105, 42, 268, 277, 205, 184, 154, 118, 145, 113, 200, 275, 266, 16, 254, 221, 162, 125, 22, 74, 82, 79, 271])
geompy.UnionIDs(Walls, [279, 248, 208, 91, 138, 84, 49, 100, 177, 257, 260, 224, 193, 159, 135, 29, 105, 42, 268, 277, 205, 184, 154, 145, 113, 200, 275, 266, 16, 254, 221, 162, 125, 22, 74, 82, 79, 271])
Pipe_Handle = geompy.CreateGroup(RV_Submission_rev_3_stl, geompy.ShapeType["FACE"])
geompy.UnionIDs(Pipe_Handle, [118])
SmokingPipeSurfaceTriangulation_stl_1 = geompy.ImportSTL("C:/Users/Samue/Documents/GitHub/OpenFOAM-Portfolio/OpenFOAM-Portfolio/Smoking Pipe Tutorial/SmokingPipeSurfaceTriangulation.stl" )
geomObj_1 = geompy.MakeCDG(RV_Submission_rev_3_stl)
geomObj_2 = geompy.MakeCDG(SmokingPipeSurfaceTriangulation_stl_1)
geomObj_3 = geompy.MakeCDG(RV_Submission_rev_3_stl)
Point_1 = geompy.MakeCDG(RV_Submission_rev_3_stl)
Bounding_Box_1 = geompy.MakeBoundingBox(SmokingPipeSurfaceTriangulation_stl_1, True)
Scale_1 = geompy.MakeScaleAlongAxes(Bounding_Box_1, Point_1, 1.01, 1.01, 1.005)
Sewing_1 = geompy.Sew(RV_Submission_rev_3_stl, 0.01)
Inlet_1 = geompy.CreateGroup(Sewing_1, geompy.ShapeType["FACE"])
geompy.UnionIDs(Inlet_1, [269])
Outlet_1 = geompy.CreateGroup(Sewing_1, geompy.ShapeType["FACE"])
geompy.UnionIDs(Outlet_1, [140])
PipeHandle = geompy.CreateGroup(Sewing_1, geompy.ShapeType["FACE"])
geompy.UnionIDs(PipeHandle, [104])
Walls_1 = geompy.CreateGroup(Sewing_1, geompy.ShapeType["FACE"])
geompy.UnionIDs(Walls_1, [263, 212, 267, 209, 28, 124, 86, 15, 111, 60, 259, 254, 242, 165, 248, 145, 2, 65, 8, 68, 181, 265, 245, 236, 256, 193, 35, 121, 91, 150, 188, 196, 147, 172, 131, 70, 99, 77])
[Inlet_1, Outlet_1, PipeHandle, Walls_1] = geompy.GetExistingSubObjects(Sewing_1, False)
geompy.addToStudy( O, 'O' )
geompy.addToStudy( OX, 'OX' )
geompy.addToStudy( OY, 'OY' )
geompy.addToStudy( OZ, 'OZ' )
geompy.addToStudy( RV_Submission_rev_3_stl, 'RV Submission_rev 3.stl' )
geompy.addToStudyInFather( RV_Submission_rev_3_stl, Inlet, 'Inlet' )
geompy.addToStudyInFather( RV_Submission_rev_3_stl, Outlet, 'Outlet' )
geompy.addToStudyInFather( RV_Submission_rev_3_stl, Walls, 'Walls' )
geompy.addToStudyInFather( RV_Submission_rev_3_stl, Pipe_Handle, 'Pipe Handle' )
geompy.addToStudy( SmokingPipeSurfaceTriangulation_stl_1, 'SmokingPipeSurfaceTriangulation.stl_1' )
geompy.addToStudy( Point_1, 'Point_1' )
geompy.addToStudy( Bounding_Box_1, 'Bounding Box_1' )
geompy.addToStudy( Scale_1, 'Scale_1' )
geompy.addToStudy( Sewing_1, 'Sewing_1' )
geompy.addToStudyInFather( Sewing_1, Inlet_1, 'Inlet' )
geompy.addToStudyInFather( Sewing_1, Outlet_1, 'Outlet' )
geompy.addToStudyInFather( Sewing_1, PipeHandle, 'PipeHandle' )
geompy.addToStudyInFather( Sewing_1, Walls_1, 'Walls' )

###
### SMESH component
###

import  SMESH, SALOMEDS
from salome.smesh import smeshBuilder

smesh = smeshBuilder.New()
#smesh.SetEnablePublish( False ) # Set to False to avoid publish in study if not needed or in some particular situations:
                                 # multiples meshes built in parallel, complex and numerous mesh edition (performance)

SmokingPipeSurfaceTriangulation = smesh.Mesh(RV_Submission_rev_3_stl,'SmokingPipeSurfaceTriangulation')
Regular_1D = SmokingPipeSurfaceTriangulation.Segment()
Adaptive_1 = Regular_1D.Adaptive(0.001,0.02,0.0001)
NETGEN_2D = SmokingPipeSurfaceTriangulation.Triangle(algo=smeshBuilder.NETGEN_2D)
Adaptive_1.SetMinSize( 0.001 )
Adaptive_1.SetMaxSize( 0.005 )
Adaptive_1.SetDeflection( 0.0001 )
status = SmokingPipeSurfaceTriangulation.RemoveHypothesis(Adaptive_1)
Local_Length_1 = Regular_1D.LocalLength(0.001,None,1e-07)
Regular_1D_1 = SmokingPipeSurfaceTriangulation.Segment(geom=Outlet)
Local_Length_2 = Regular_1D_1.LocalLength(0.00025,None,1e-07)
NETGEN_2D_1 = SmokingPipeSurfaceTriangulation.Triangle(algo=smeshBuilder.NETGEN_2D,geom=Outlet)
NETGEN_2D_Parameters_1 = NETGEN_2D.Parameters()
NETGEN_2D_Parameters_1.SetOptimize( 1 )
NETGEN_2D_Parameters_1.SetChordalError( -1 )
NETGEN_2D_Parameters_1.SetChordalErrorEnabled( 0 )
NETGEN_2D_Parameters_1.SetUseDelauney( 0 )
NETGEN_2D_Parameters_1.SetQuadAllowed( 0 )
Length_From_Edges_1 = smesh.CreateHypothesis('LengthFromEdges')
Local_Length_1.SetLength( 0.0001 )
Local_Length_1.SetPrecision( 1e-07 )
status = SmokingPipeSurfaceTriangulation.RemoveHypothesis(Local_Length_1)
Adaptive_1.SetMinSize( 5e-05 )
Adaptive_1.SetMaxSize( 0.01 )
Adaptive_1.SetDeflection( 0.0001 )
NETGEN_2D_Parameters_1.SetUseSurfaceCurvature( 1 )
NETGEN_2D_Parameters_1.SetMinSize( 1e-08 )
NETGEN_2D_Parameters_1.SetFineness( 3 )
NETGEN_2D_Parameters_1.SetMaxSize( 0.00025 )
NETGEN_2D_Parameters_1.SetWorstElemMeasure( 43 )
NETGEN_2D_Parameters_1.SetCheckChartBoundary( 48 )
status = SmokingPipeSurfaceTriangulation.RemoveHypothesis(Regular_1D)
status = SmokingPipeSurfaceTriangulation.RemoveHypothesis(NETGEN_2D)
MG_CADSurf = SmokingPipeSurfaceTriangulation.Triangle(algo=smeshBuilder.MG_CADSurf)
status = SmokingPipeSurfaceTriangulation.RemoveHypothesis(NETGEN_2D_Parameters_1)
status = SmokingPipeSurfaceTriangulation.RemoveHypothesis(MG_CADSurf)
NETGEN_1D_2D = SmokingPipeSurfaceTriangulation.Triangle(algo=smeshBuilder.NETGEN_1D2D)
NETGEN_2D_Parameters_1_1 = NETGEN_1D_2D.Parameters()
NETGEN_2D_Parameters_1_1.SetUseDelauney( 0 )
NETGEN_2D_Parameters_1_1.SetMaxSize( 0.00025 )
NETGEN_2D_Parameters_1_1.SetMinSize( 1e-06 )
NETGEN_2D_Parameters_1_1.SetSecondOrder( 0 )
NETGEN_2D_Parameters_1_1.SetOptimize( 1 )
NETGEN_2D_Parameters_1_1.SetFineness( 3 )
NETGEN_2D_Parameters_1_1.SetChordalError( 0 )
NETGEN_2D_Parameters_1_1.SetChordalErrorEnabled( 0 )
NETGEN_2D_Parameters_1_1.SetUseSurfaceCurvature( 1 )
NETGEN_2D_Parameters_1_1.SetFuseEdges( 1 )
NETGEN_2D_Parameters_1_1.SetQuadAllowed( 0 )
NETGEN_2D_Parameters_1_1.SetWorstElemMeasure( 60 )
NETGEN_2D_Parameters_1_1.SetCheckChartBoundary( 144 )
status = SmokingPipeSurfaceTriangulation.RemoveHypothesis(NETGEN_2D_Parameters_1_1)
NETGEN_2D_Simple_Parameters_1 = NETGEN_1D_2D.Parameters(smeshBuilder.SIMPLE)
NETGEN_2D_Simple_Parameters_1.SetLocalLength( 0.0001 )
NETGEN_2D_Simple_Parameters_1.LengthFromEdges()
NETGEN_2D_Simple_Parameters_1.SetAllowQuadrangles( 0 )
status = SmokingPipeSurfaceTriangulation.RemoveHypothesis(NETGEN_1D_2D)
NETGEN_2D_2 = SmokingPipeSurfaceTriangulation.Triangle(algo=smeshBuilder.NETGEN_2D)
status = SmokingPipeSurfaceTriangulation.RemoveHypothesis(NETGEN_2D_Simple_Parameters_1)
status = SmokingPipeSurfaceTriangulation.AddHypothesis(NETGEN_2D_Parameters_1)
Regular_1D_2 = SmokingPipeSurfaceTriangulation.Segment()
status = SmokingPipeSurfaceTriangulation.AddHypothesis(Adaptive_1)
Regular_1D_3 = SmokingPipeSurfaceTriangulation.Segment(geom=Pipe_Handle)
Adaptive_1.SetMinSize( 5e-05 )
Adaptive_1.SetMaxSize( 0.0002 )
Adaptive_1.SetDeflection( 0.0001 )
status = SmokingPipeSurfaceTriangulation.RemoveHypothesis(Regular_1D,Pipe_Handle)
NETGEN_1D_2D_1 = SmokingPipeSurfaceTriangulation.Triangle(algo=smeshBuilder.NETGEN_1D2D,geom=Pipe_Handle)
status = SmokingPipeSurfaceTriangulation.AddHypothesis(NETGEN_2D_Parameters_1_1,Pipe_Handle)
try:
  SmokingPipeSurfaceTriangulation.ExportSTL( r'C:/Users/Samue/Documents/GitHub/OpenFOAM-Portfolio/OpenFOAM-Portfolio/Smoking Pipe Tutorial/SmokingPipeSurfaceTriangulation.stl', 1 )
  pass
except:
  print('ExportSTL() failed. Invalid file name?')
Inlet_2 = SmokingPipeSurfaceTriangulation.GroupOnGeom(Inlet,'Inlet',SMESH.FACE)
Outlet_2 = SmokingPipeSurfaceTriangulation.GroupOnGeom(Outlet,'Outlet',SMESH.FACE)
Walls_2 = SmokingPipeSurfaceTriangulation.GroupOnGeom(Walls,'Walls',SMESH.FACE)
Pipe_Handle_1 = SmokingPipeSurfaceTriangulation.GroupOnGeom(Pipe_Handle,'Pipe Handle',SMESH.FACE)
[ Inlet_2, Outlet_2, Walls_2, Pipe_Handle_1 ] = SmokingPipeSurfaceTriangulation.GetGroups()
try:
  SmokingPipeSurfaceTriangulation.ExportSTL( r'C:/Users/Samue/Documents/GitHub/OpenFOAM-Portfolio/OpenFOAM-Portfolio/Smoking Pipe Tutorial/STL File/Inlet.stl', 1, Inlet_2)
  pass
except:
  print('ExportPartToSTL() failed. Invalid file name?')
try:
  SmokingPipeSurfaceTriangulation.ExportSTL( r'C:/Users/Samue/Documents/GitHub/OpenFOAM-Portfolio/OpenFOAM-Portfolio/Smoking Pipe Tutorial/STL File/Outlet.stl', 1, Outlet_2)
  pass
except:
  print('ExportPartToSTL() failed. Invalid file name?')
try:
  SmokingPipeSurfaceTriangulation.ExportSTL( r'C:/Users/Samue/Documents/GitHub/OpenFOAM-Portfolio/OpenFOAM-Portfolio/Smoking Pipe Tutorial/STL File/Walls.stl', 1, Walls_2)
  pass
except:
  print('ExportPartToSTL() failed. Invalid file name?')
try:
  SmokingPipeSurfaceTriangulation.ExportSTL( r'C:/Users/Samue/Documents/GitHub/OpenFOAM-Portfolio/OpenFOAM-Portfolio/Smoking Pipe Tutorial/STL File/Pipe Handle.stl', 1, Pipe_Handle_1)
  pass
except:
  print('ExportPartToSTL() failed. Invalid file name?')
NETGEN_2D_Parameters_1.SetMaxSize( 0.0005 )
NETGEN_2D_Parameters_1.SetOptimize( 1 )
NETGEN_2D_Parameters_1.SetFineness( 5 )
NETGEN_2D_Parameters_1.SetGrowthRate( 0.1 )
NETGEN_2D_Parameters_1.SetChordalError( 0 )
NETGEN_2D_Parameters_1.SetChordalErrorEnabled( 0 )
NETGEN_2D_Parameters_1.SetUseSurfaceCurvature( 1 )
NETGEN_2D_Parameters_1.SetQuadAllowed( 0 )
[ Inlet_2, Outlet_2, Walls_2, Pipe_Handle_1 ] = SmokingPipeSurfaceTriangulation.GetGroups()
NETGEN_2D_Parameters_1_1.SetSecondOrder( 0 )
NETGEN_2D_Parameters_1_1.SetOptimize( 1 )
NETGEN_2D_Parameters_1_1.SetFineness( 3 )
NETGEN_2D_Parameters_1_1.SetChordalError( 0 )
NETGEN_2D_Parameters_1_1.SetChordalErrorEnabled( 0 )
NETGEN_2D_Parameters_1_1.SetUseSurfaceCurvature( 1 )
NETGEN_2D_Parameters_1_1.SetFuseEdges( 1 )
NETGEN_2D_Parameters_1_1.SetQuadAllowed( 0 )
[ Inlet_2, Outlet_2, Walls_2, Pipe_Handle_1 ] = SmokingPipeSurfaceTriangulation.GetGroups()
NETGEN_2D_Parameters_1_1.SetMaxSize( 0.0005 )
NETGEN_2D_Parameters_1_1.SetMinSize( 5e-05 )
NETGEN_2D_Parameters_1_1.SetWorstElemMeasure( 218 )
NETGEN_2D_Parameters_1_1.SetCheckChartBoundary( 192 )
[ Inlet_2, Outlet_2, Walls_2, Pipe_Handle_1 ] = SmokingPipeSurfaceTriangulation.GetGroups()
NETGEN_2D_Parameters_1.SetMinSize( 0.00025 )
NETGEN_2D_Parameters_1.SetWorstElemMeasure( 218 )
NETGEN_2D_Parameters_1.SetCheckChartBoundary( 192 )
[ Inlet_2, Outlet_2, Walls_2, Pipe_Handle_1 ] = SmokingPipeSurfaceTriangulation.GetGroups()
Adaptive_1.SetMinSize( 0.00025 )
Adaptive_1.SetMaxSize( 0.0005 )
Adaptive_1.SetDeflection( 0.0001 )
[ Inlet_2, Outlet_2, Walls_2, Pipe_Handle_1 ] = SmokingPipeSurfaceTriangulation.GetGroups()
try:
  SmokingPipeSurfaceTriangulation.ExportSTL( r'C:/Users/Samue/Documents/GitHub/OpenFOAM-Portfolio/OpenFOAM-Portfolio/Smoking Pipe Tutorial/STL File/Inlet.stl', 1, Inlet_2)
  pass
except:
  print('ExportPartToSTL() failed. Invalid file name?')
try:
  SmokingPipeSurfaceTriangulation.ExportSTL( r'C:/Users/Samue/Documents/GitHub/OpenFOAM-Portfolio/OpenFOAM-Portfolio/Smoking Pipe Tutorial/STL File/Outlet.stl', 1, Outlet_2)
  pass
except:
  print('ExportPartToSTL() failed. Invalid file name?')
try:
  SmokingPipeSurfaceTriangulation.ExportSTL( r'C:/Users/Samue/Documents/GitHub/OpenFOAM-Portfolio/OpenFOAM-Portfolio/Smoking Pipe Tutorial/STL File/Walls.stl', 1, Walls_2)
  pass
except:
  print('ExportPartToSTL() failed. Invalid file name?')
try:
  SmokingPipeSurfaceTriangulation.ExportSTL( r'C:/Users/Samue/Documents/GitHub/OpenFOAM-Portfolio/OpenFOAM-Portfolio/Smoking Pipe Tutorial/STL File/Pipe Handle.stl', 1, Pipe_Handle_1)
  pass
except:
  print('ExportPartToSTL() failed. Invalid file name?')
Local_Length_1.SetLength( 0.01 )
Local_Length_1.SetPrecision( 1e-07 )
isDone = SmokingPipeSurfaceTriangulation.Compute()
SmokingPipeSurfaceTriangulation.CheckCompute()
[ Inlet_2, Outlet_2, Walls_2, Pipe_Handle_1 ] = SmokingPipeSurfaceTriangulation.GetGroups()
Mesh_1 = smesh.Mesh(Sewing_1,'Mesh_1')
Inlet_3 = Mesh_1.GroupOnGeom(Inlet_1,'Inlet',SMESH.FACE)
Outlet_3 = Mesh_1.GroupOnGeom(Outlet_1,'Outlet',SMESH.FACE)
PipeHandle_1 = Mesh_1.GroupOnGeom(PipeHandle,'PipeHandle',SMESH.FACE)
Walls_3 = Mesh_1.GroupOnGeom(Walls_1,'Walls',SMESH.FACE)
Sub_mesh_1 = Regular_1D_1.GetSubMesh()
Sub_mesh_2 = Regular_1D_3.GetSubMesh()


## Set names of Mesh objects
smesh.SetName(Pipe_Handle_1, 'Pipe Handle')
smesh.SetName(Length_From_Edges_1, 'Length From Edges_1')
smesh.SetName(NETGEN_2D_Parameters_1, 'NETGEN 2D Parameters_1')
smesh.SetName(NETGEN_1D_2D.GetAlgorithm(), 'NETGEN 1D-2D')
smesh.SetName(Adaptive_1, 'Adaptive_1')
smesh.SetName(Inlet_2, 'Inlet')
smesh.SetName(Outlet_2, 'Outlet')
smesh.SetName(SmokingPipeSurfaceTriangulation.GetMesh(), 'SmokingPipeSurfaceTriangulation')
smesh.SetName(Mesh_1.GetMesh(), 'Mesh_1')
smesh.SetName(Local_Length_1, 'Local Length_1')
smesh.SetName(PipeHandle_1, 'PipeHandle')
smesh.SetName(Walls_3, 'Walls')
smesh.SetName(Sub_mesh_1, 'Sub-mesh_1')
smesh.SetName(NETGEN_2D_Parameters_1_1, 'NETGEN 2D Parameters_1')
smesh.SetName(Outlet_3, 'Outlet')
smesh.SetName(Walls_2, 'Walls')
smesh.SetName(Inlet_3, 'Inlet')
smesh.SetName(NETGEN_2D_Simple_Parameters_1, 'NETGEN 2D Simple Parameters_1')
smesh.SetName(MG_CADSurf.GetAlgorithm(), 'MG-CADSurf')
smesh.SetName(Regular_1D.GetAlgorithm(), 'Regular_1D')
smesh.SetName(Local_Length_2, 'Local Length_2')
smesh.SetName(Sub_mesh_2, 'Sub-mesh_2')
smesh.SetName(NETGEN_2D.GetAlgorithm(), 'NETGEN 2D')


if salome.sg.hasDesktop():
  salome.sg.updateObjBrowser()
