#!/usr/bin/env python3
"""
Heatsink parametric study — full domain with plenums, bypass, and fan curves.

Domain (Z = flow direction, Y = vertical, X = width):

  Z=0                         Z=290mm
  fan1_face                   fan2_face
  |  inlet plenum  | heatsink |  outlet plenum  |
  |    105 mm      |  80 mm   |     105 mm      |

X: 0 to FAN_D (80mm) — set by fan diameter
Y: 0 to FAN_D (80mm) — base bottom to fan top
   Y=0            : heatsink base bottom (zeroGradient — insulated)
   Y=0  to BT     : heatsink base (solid Al)
   Y=BT to BT+FH  : fin region — solid fins + fluid channels
   Y=BT+FH to FAN_D: bypass region (fluid, full width)

Fin array is centered in X; side gaps between fin array edge and domain wall are fluid.
Fin tips (Y = BT+FH) are coupled solid/fluid interfaces (not adiabatic).

Fans:
  Fan 1: fanPressureJump cyclic patch pair at Z=0
  Fan 2: fanPressureJump cyclic patch pair at Z=290mm
  Both fans use the Delta FFB0812VH P-Q curve (12V):
    dP(phi) = 73.99 - 1164.25*phi - 34615.0*phi^2   [Pa, phi in kg/s]
"""

import os, shutil, math

# =============================================================================
# PARAMETER SWEEP
# =============================================================================
SWEEP = [
    {"fin_pitch": 4e-3, "n_fins": 18},
    {"fin_pitch": 5e-3, "n_fins": 15},
    {"fin_pitch": 6e-3, "n_fins": 12},
    {"fin_pitch": 7e-3, "n_fins": 10},
    {"fin_pitch": 8e-3, "n_fins":  9},
]

# =============================================================================
# FIXED GEOMETRY & PHYSICS
# =============================================================================
FAN_D  = 80e-3    # m  fan diameter = domain width and height
FT     = 1.5e-3   # m  fin thickness
FH     = 35e-3    # m  fin height above base
FL     = 80e-3    # m  heatsink length (flow direction)
BT     = 5e-3     # m  base thickness
LP     = 105e-3   # m  plenum length each side
Q_TOT  = 150.0    # W
T_IN   = 300.0    # K
RHO    = 1.177    # kg/m3 air at 300K (for fan curve phi conversion)

# Fan curve polynomial coefficients (dP vs phi = rho*Q)
# dP = C0 + C1*phi + C2*phi^2
FAN_C0 =  73.99
FAN_C1 = -1164.25
FAN_C2 = -34615.0

# Cell counts
NZ_PLENUM = 25   # cells in each plenum (Z)
NZ_FIN    = 40   # cells through heatsink (Z)
NY_BASE   =  4   # cells in base thickness
NY_FIN    = 18   # cells in fin height
NY_BYPASS = 12   # cells in bypass region
NX_FIN    =  4   # cells across fin thickness
NX_CHAN   =  8   # cells across channel width
NX_SIDE   =  4   # cells in side gap

def chan_w(p):   return p["fin_pitch"] - FT
def fin_arr_w(p):
    # n_fins fins + (n_fins-1) channels
    return p["n_fins"]*FT + (p["n_fins"]-1)*chan_w(p)
def side_gap(p): return (FAN_D - fin_arr_w(p)) / 2.0
def base_area(p): return FAN_D * FL   # heat flux over full base width
def solid_vol(p):
    v_base = FAN_D * BT * FL
    v_fins = p["n_fins"] * FT * FH * FL
    return v_base + v_fins
def heat_src(p):  return Q_TOT / solid_vol(p)

# =============================================================================
# blockMeshDict generator
# =============================================================================
def gen_bmd(p):
    """
    Build blockMeshDict for the full domain.

    X strips (left to right):
      [side_gap(fluid)] [fin(solid)] [chan(fluid)] ... [fin(solid)] [side_gap(fluid)]

    Y layers (bottom to top):
      [base: solid, 0..BT]
      [fin/chan: solid fins + fluid channels, BT..BT+FH]
      [bypass: fluid full width, BT+FH..FAN_D]

    Z slabs (front to back):
      [inlet plenum: fluid, 0..LP]
      [heatsink zone: mixed, LP..LP+FL]
      [outlet plenum: fluid, LP+FL..LP+FL+LP]

    In the plenum slabs, ALL X strips are fluid regardless of fin/chan type.
    In the heatsink slab, X strips follow fin/chan assignment.
    Base Y layer is always solid across all X strips in heatsink slab.
    Bypass Y layer is always fluid across all X strips in all slabs.
    """
    cw  = chan_w(p)
    sg  = side_gap(p)
    nf  = p["n_fins"]

    # ------------------------------------------------------------------
    # X coordinate layout
    # ------------------------------------------------------------------
    # strips: list of (x_start, x_end, type) where type='fin'|'chan'|'side'
    strips = []
    x = 0.0
    strips.append((x, x+sg, 'side'))
    x += sg
    for i in range(nf):
        strips.append((x, x+FT, 'fin'))
        x += FT
        if i < nf-1:
            strips.append((x, x+cw, 'chan'))
            x += cw
    strips.append((x, x+sg, 'side'))
    x += sg
    assert abs(x - FAN_D) < 1e-9, f"Width mismatch: {x} vs {FAN_D}"

    # unique X coords
    x_coords = []
    for (xs, xe, _) in strips:
        if not x_coords or abs(x_coords[-1]-xs) > 1e-12:
            x_coords.append(xs)
    x_coords.append(strips[-1][1])

    # Y layers: (y_start, y_end, label)
    y_layers = [
        (0.0,      BT,      'base'),
        (BT,       BT+FH,   'finzone'),
        (BT+FH,    FAN_D,   'bypass'),
    ]
    y_coords = [0.0, BT, BT+FH, FAN_D]

    z_slabs = [
        (0.0,      LP,       'inlet_plenum'),
        (LP,       LP+FL,    'heatsink'),
        (LP+FL,    LP+FL+LP, 'outlet_plenum'),
    ]
    z_coords = [0.0, LP, LP+FL, LP+FL+LP]

    # ------------------------------------------------------------------
    # Vertex grid [ix][iy][iz]
    # ------------------------------------------------------------------
    vertices = []
    grid = {}
    for iz,zv in enumerate(z_coords):
        for iy,yv in enumerate(y_coords):
            for ix,xv in enumerate(x_coords):
                grid[(ix,iy,iz)] = len(vertices)
                vertices.append((xv,yv,zv))

    def v(ix,iy,iz): return grid[(ix,iy,iz)]

    # ------------------------------------------------------------------
    # Block zone assignment
    # strip_type: 'fin'|'chan'|'side'
    # y_label:    'base'|'finzone'|'bypass'
    # z_label:    'inlet_plenum'|'heatsink'|'outlet_plenum'
    # ------------------------------------------------------------------
    def zone(strip_type, y_label, z_label):
        if z_label != 'heatsink':
            return 'fluid'
        # heatsink slab
        if y_label == 'base':
            return 'solid'   # entire base is Al
        if y_label == 'bypass':
            return 'fluid'
        # finzone
        if strip_type == 'fin':
            return 'solid'
        return 'fluid'       # chan or side in finzone

    # ------------------------------------------------------------------
    # NX per strip type
    # ------------------------------------------------------------------
    def nx(strip_type):
        if strip_type == 'fin':  return NX_FIN
        if strip_type == 'chan': return NX_CHAN
        return NX_SIDE

    def ny(y_label):
        if y_label == 'base':    return NY_BASE
        if y_label == 'finzone': return NY_FIN
        return NY_BYPASS

    def nz(z_label):
        if z_label == 'heatsink': return NZ_FIN
        return NZ_PLENUM

    # ------------------------------------------------------------------
    # Build blocks
    # ------------------------------------------------------------------
    blocks = []
    for iz,(zs,ze,zl) in enumerate(z_slabs):
        for iy,(ys,ye,yl) in enumerate(y_layers):
            for ix,(xs,xe,st) in enumerate(strips):
                z = zone(st, yl, zl)
                # hex vertices: (x0y0z0 x1y0z0 x1y1z0 x0y1z0
                #                x0y0z1 x1y0z1 x1y1z1 x0y1z1)
                bv = [
                    v(ix,   iy,   iz  ), v(ix+1, iy,   iz  ),
                    v(ix+1, iy+1, iz  ), v(ix,   iy+1, iz  ),
                    v(ix,   iy,   iz+1), v(ix+1, iy,   iz+1),
                    v(ix+1, iy+1, iz+1), v(ix,   iy+1, iz+1),
                ]
                blocks.append({
                    'v': bv,
                    'n': (nx(st), ny(yl), nz(zl)),
                    'zone': z,
                })

    # ------------------------------------------------------------------
    # Boundary faces
    # ------------------------------------------------------------------
    # We need to identify external boundary faces.
    # For each block, check each of its 6 faces against domain extents.

    n_ix = len(strips)
    n_iy = len(y_layers)
    n_iz = len(z_slabs)

    # fan patch faces: cyclic pairs at z=z_coords[0] and z=z_coords[-1]
    # Only FLUID blocks at those Z faces
    fan1_half0 = []   # outer (upstream) face of fan1 slab
    fan1_half1 = []   # inner (downstream) face of fan1 slab
    fan2_half0 = []   # outer (downstream) face of fan2 slab
    fan2_half1 = []   # inner (upstream) face of fan2 slab

    # Other boundaries
    base_bottom  = []  # y=0
    top_wall     = []  # y=FAN_D
    side_walls   = []  # x=0 and x=FAN_D

    bidx = 0
    for iz,(zs,ze,zl) in enumerate(z_slabs):
        for iy,(ys,ye,yl) in enumerate(y_layers):
            for ix,(xs,xe,st) in enumerate(strips):
                b = blocks[bidx]; bidx += 1
                bv = b['v']
                z = b['zone']

                if iz == 0 and z == 'fluid':
                    fan1_half0.append((bv[0], bv[3], bv[2], bv[1]))
                if iz == n_iz-1 and z == 'fluid':
                    fan2_half0.append((bv[4], bv[5], bv[6], bv[7]))
                # y=0 (base bottom) — all blocks at iy==0
                if iy == 0:
                    base_bottom.append((bv[0], bv[1], bv[5], bv[4]))
                # y=FAN_D (top)
                if iy == n_iy-1:
                    top_wall.append((bv[3], bv[7], bv[6], bv[2]))
                # x=0
                if ix == 0:
                    side_walls.append((bv[0], bv[4], bv[7], bv[3]))
                # x=FAN_D
                if ix == n_ix-1:
                    side_walls.append((bv[1], bv[2], bv[6], bv[5]))

    # fan patch pairs: half0/half1 same faces, opposite winding (required by blockMesh cyclic)

    # ------------------------------------------------------------------
    # Write file
    # ------------------------------------------------------------------
    def face_str(faces):
        return "\n".join(f"        ({' '.join(str(vi) for vi in f)})" for f in faces)

    L = []
    L += ["FoamFile", "{",
          "    version 2.0; format ascii;",
          "    class dictionary; object blockMeshDict;", "}", "",
          "scale 1;", ""]

    L += ["vertices", "("]
    for (xv,yv,zv) in vertices:
        L.append(f"    ({xv:.7e} {yv:.7e} {zv:.7e})")
    L += [");", ""]

    L += ["blocks", "("]
    for b in blocks:
        vs = " ".join(str(vi) for vi in b['v'])
        nx_,ny_,nz_ = b['n']
        L.append(f"    hex ({vs}) {b['zone']} ({nx_} {ny_} {nz_}) simpleGrading (1 1 1)")
    L += [");", ""]

    L += ["edges", "(", ");", ""]

    def patch(name, ptype, faces):
        return [f"    {name}", "    {", f"        type {ptype};",
                "        faces", "        (", face_str(faces), "        );", "    }"]

    L += ["boundary", "("]
    # Fan cyclic pairs
    L += patch("fan1_half0", "patch", fan1_half0)
    L += patch("fan2_half0", "patch", fan2_half0)
    L += patch("base_bottom", "wall", base_bottom)
    L += patch("top_wall",    "wall", top_wall)
    L += patch("side_walls",  "wall", side_walls)
    L += [");", "", "mergePatchPairs", "(", ");"]

    return "\n".join(L)

# =============================================================================
# 0/ boundary conditions
# =============================================================================
def write_fluid_T(case_dir):
    txt = '''FoamFile
{
    version 2.0; format ascii;
    class volScalarField; location "0/fluid"; object T;
}
dimensions [0 0 0 1 0 0 0];
internalField uniform 300;
boundaryField
{
    fan1_half0 { type fanPressureJump; patchType cyclic; jump uniform 0; value uniform 300; }
    fan1_half1 { type fanPressureJump; patchType cyclic; jump uniform 0; value uniform 300; }
    fan2_half0 { type fanPressureJump; patchType cyclic; jump uniform 0; value uniform 300; }
    fan2_half1 { type fanPressureJump; patchType cyclic; jump uniform 0; value uniform 300; }
    base_bottom { type zeroGradient; }
    top_wall    { type zeroGradient; }
    side_walls  { type zeroGradient; }
    fluid_to_solid { type turbulentTemperatureCoupledBaffleMixed; Tnbr T; kappaMethod fluidThermo; value uniform 300; }
}'''
    with open(os.path.join(case_dir,"0","fluid","T"),"w") as f: f.write(txt)

def write_fluid_U(case_dir):
    txt = '''FoamFile
{
    version 2.0; format ascii;
    class volVectorField; location "0/fluid"; object U;
}
dimensions [0 1 -1 0 0 0 0];
internalField uniform (0 0 -1.0);
boundaryField
{
    fan1_half0 { type cyclic; }
    fan1_half1 { type cyclic; }
    fan2_half0 { type cyclic; }
    fan2_half1 { type cyclic; }
    base_bottom { type noSlip; }
    top_wall    { type noSlip; }
    side_walls  { type noSlip; }
    fluid_to_solid { type noSlip; }
}'''
    with open(os.path.join(case_dir,"0","fluid","U"),"w") as f: f.write(txt)

def write_fluid_p_rgh(case_dir):
    # Fan curve polynomial in terms of phi (mass flux kg/s)
    txt = f'''FoamFile
{{
    version 2.0; format ascii;
    class volScalarField; location "0/fluid"; object p_rgh;
}}
dimensions [1 -1 -2 0 0 0 0];
internalField uniform 0;
boundaryField
{{
    // Fan 1 — pushing flow in +Z direction into domain
    fan1_half0
    {{
        type            fanPressureJump;
        patchType       cyclic;
        jump            uniform 0;
        value           uniform 0;
        jumpTable       polynomial
        (
            ({FAN_C0:.4f}  0)
            ({FAN_C1:.4f}  1)
            ({FAN_C2:.4f}  2)
        );
    }}
    fan1_half1
    {{
        type            fanPressureJump;
        patchType       cyclic;
        jump            uniform 0;
        value           uniform 0;
        jumpTable       polynomial
        (
            ({FAN_C0:.4f}  0)
            ({FAN_C1:.4f}  1)
            ({FAN_C2:.4f}  2)
        );
    }}
    // Fan 2 — pulling flow out in +Z direction
    fan2_half0
    {{
        type            fanPressureJump;
        patchType       cyclic;
        jump            uniform 0;
        value           uniform 0;
        jumpTable       polynomial
        (
            ({FAN_C0:.4f}  0)
            ({FAN_C1:.4f}  1)
            ({FAN_C2:.4f}  2)
        );
    }}
    fan2_half1
    {{
        type            fanPressureJump;
        patchType       cyclic;
        jump            uniform 0;
        value           uniform 0;
        jumpTable       polynomial
        (
            ({FAN_C0:.4f}  0)
            ({FAN_C1:.4f}  1)
            ({FAN_C2:.4f}  2)
        );
    }}
    base_bottom  {{ type fixedFluxPressure; value uniform 0; }}
    top_wall     {{ type fixedFluxPressure; value uniform 0; }}
    side_walls   {{ type fixedFluxPressure; value uniform 0; }}
    fluid_to_solid {{ type fixedFluxPressure; value uniform 0; }}
}}'''
    with open(os.path.join(case_dir,"0","fluid","p_rgh"),"w") as f: f.write(txt)

def write_fluid_p(case_dir):
    txt = '''FoamFile
{
    version 2.0; format ascii;
    class volScalarField; location "0/fluid"; object p;
}
dimensions [1 -1 -2 0 0 0 0];
internalField uniform 101325;
boundaryField
{
    fan1_half0   { type calculated; value uniform 101325; }
    fan1_half1   { type calculated; value uniform 101325; }
    fan2_half0   { type calculated; value uniform 101325; }
    fan2_half1   { type calculated; value uniform 101325; }
    base_bottom  { type calculated; value uniform 101325; }
    top_wall     { type calculated; value uniform 101325; }
    side_walls   { type calculated; value uniform 101325; }
    fluid_to_solid { type calculated; value uniform 101325; }
}'''
    with open(os.path.join(case_dir,"0","fluid","p"),"w") as f: f.write(txt)

def write_fluid_k(case_dir):
    txt = '''FoamFile
{
    version 2.0; format ascii;
    class volScalarField; location "0/fluid"; object k;
}
// k = 1.5*(U*I)^2, I=5%, U~2.86 m/s => k~0.0154 m2/s2
dimensions [0 2 -2 0 0 0 0];
internalField uniform 0.0154;
boundaryField
{
    fan1_half0   { type cyclic; }
    fan1_half1   { type cyclic; }
    fan2_half0   { type cyclic; }
    fan2_half1   { type cyclic; }
    base_bottom  { type kqRWallFunction; value uniform 0.0154; }
    top_wall     { type kqRWallFunction; value uniform 0.0154; }
    side_walls   { type kqRWallFunction; value uniform 0.0154; }
    fluid_to_solid { type kqRWallFunction; value uniform 0.0154; }
}'''
    with open(os.path.join(case_dir,"0","fluid","k"),"w") as f: f.write(txt)

def write_fluid_epsilon(case_dir):
    txt = '''FoamFile
{
    version 2.0; format ascii;
    class volScalarField; location "0/fluid"; object epsilon;
}
dimensions [0 2 -3 0 0 0 0];
internalField uniform 0.026;
boundaryField
{
    fan1_half0   { type cyclic; }
    fan1_half1   { type cyclic; }
    fan2_half0   { type cyclic; }
    fan2_half1   { type cyclic; }
    base_bottom  { type epsilonWallFunction; value uniform 0.026; }
    top_wall     { type epsilonWallFunction; value uniform 0.026; }
    side_walls   { type epsilonWallFunction; value uniform 0.026; }
    fluid_to_solid { type epsilonWallFunction; value uniform 0.026; }
}'''
    with open(os.path.join(case_dir,"0","fluid","epsilon"),"w") as f: f.write(txt)

def write_fluid_alphat(case_dir):
    txt = '''FoamFile
{
    version 2.0; format ascii;
    class volScalarField; location "0/fluid"; object alphat;
}
dimensions [1 -1 -1 0 0 0 0];
internalField uniform 0;
boundaryField
{
    fan1_half0   { type cyclic; }
    fan1_half1   { type cyclic; }
    fan2_half0   { type cyclic; }
    fan2_half1   { type cyclic; }
    base_bottom  { type compressible::alphatWallFunction; Prt 0.85; value uniform 0; }
    top_wall     { type compressible::alphatWallFunction; Prt 0.85; value uniform 0; }
    side_walls   { type compressible::alphatWallFunction; Prt 0.85; value uniform 0; }
    fluid_to_solid { type compressible::alphatWallFunction; Prt 0.85; value uniform 0; }
}'''
    with open(os.path.join(case_dir,"0","fluid","alphat"),"w") as f: f.write(txt)

def write_solid_T(case_dir):
    txt = '''FoamFile
{
    version 2.0; format ascii;
    class volScalarField; location "0/solid"; object T;
}
dimensions [0 0 0 1 0 0 0];
internalField uniform 300;
boundaryField
{
    base_bottom  { type zeroGradient; }
    solid_to_fluid { type turbulentTemperatureCoupledBaffleMixed; Tnbr T; kappaMethod solidThermo; value uniform 300; }
}'''
    with open(os.path.join(case_dir,"0","solid","T"),"w") as f: f.write(txt)

# =============================================================================
# fvOptions — volumetric heat source in solid
# =============================================================================
def write_solid_fvoptions(case_dir, p):
    hs = heat_src(p)
    txt = f'''FoamFile
{{
    version 2.0; format ascii;
    class dictionary; location "system/solid"; object fvOptions;
}}
heatSource
{{
    type            scalarSemiImplicitSource;
    active          true;
    selectionMode   all;
    scalarSemiImplicitSourceCoeffs
    {{
        volumeMode  specific;
        injectionRateSuSp
        {{
            h   ({hs:.4e} 0);
        }}
    }}
}}'''
    with open(os.path.join(case_dir,"system","solid","fvOptions"),"w") as f: f.write(txt)

# =============================================================================
# Case generator
# =============================================================================
def generate_case(p, case_dir, base_case_dir):
    print(f"Generating: {os.path.basename(case_dir)}")
    if os.path.exists(case_dir): shutil.rmtree(case_dir)
    shutil.copytree(base_case_dir, case_dir)

    os.makedirs(os.path.join(case_dir,"0","fluid"),  exist_ok=True)
    os.makedirs(os.path.join(case_dir,"0","solid"),  exist_ok=True)
    os.makedirs(os.path.join(case_dir,"system","fluid"), exist_ok=True)
    os.makedirs(os.path.join(case_dir,"system","solid"), exist_ok=True)

    # blockMeshDict
    bmd_path = os.path.join(case_dir,"system","blockMeshDict")
    with open(bmd_path,"w") as f: f.write(gen_bmd(p))

    # BCs
    write_fluid_T(case_dir)
    write_fluid_U(case_dir)
    write_fluid_p_rgh(case_dir)
    write_fluid_p(case_dir)
    write_fluid_k(case_dir)
    write_fluid_epsilon(case_dir)
    write_fluid_alphat(case_dir)
    write_solid_T(case_dir)
    write_solid_fvoptions(case_dir, p)

    sg  = side_gap(p)
    cw  = chan_w(p)
    hs  = heat_src(p)
    sv  = solid_vol(p)
    summary = (
        f"# fin_pitch={p['fin_pitch']*1e3:.1f}mm  n_fins={p['n_fins']}\n"
        f"# channel_width  = {cw*1e3:.2f} mm\n"
        f"# side_gap       = {sg*1e3:.2f} mm\n"
        f"# fin_array_w    = {fin_arr_w(p)*1e3:.1f} mm\n"
        f"# domain W x H   = {FAN_D*1e3:.0f} x {FAN_D*1e3:.0f} mm\n"
        f"# total Z length = {(2*LP+FL)*1e3:.0f} mm\n"
        f"# solid_volume   = {sv*1e9:.1f} mm3\n"
        f"# heat_src_vol   = {hs:.4e} W/m3\n"
        f"# Fan curve: dP = {FAN_C0:.2f} + {FAN_C1:.2f}*phi + {FAN_C2:.1f}*phi^2 [Pa]\n"
    )
    with open(os.path.join(case_dir,"case_summary.txt"),"w") as f: f.write(summary)
    print(summary)

# =============================================================================
if __name__ == "__main__":
    script_dir = os.path.dirname(os.path.abspath(__file__))
    base_case  = os.path.join(script_dir, "base_case")
    for p in SWEEP:
        name = f"pitch_{int(p['fin_pitch']*1e3)}mm_nfins_{p['n_fins']}"
        generate_case(p, os.path.join(script_dir, name), base_case)
    print("Done. Run run_all.sh to execute.")
