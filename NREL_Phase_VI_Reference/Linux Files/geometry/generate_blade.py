"""
NREL Phase VI blade STL generator.

Geometry source:
  Giguere & Selig, NREL/SR-500-26173, 1999 (Appendix A)
  S809 airfoil: Somers, NREL/SR-440-6918, 1997

Coordinate convention (OpenFOAM):
  x = streamwise (flow direction, rotor axis)
  y = horizontal (rotor plane)
  z = vertical   (rotor plane)

Rotor axis = x-axis. Blade spans in the +z direction from hub outward.
Hub centre at origin. Inflow along +x.
"""

import numpy as np
import struct
import os

# ---------------------------------------------------------------------------
# S809 airfoil coordinates (normalized, x/c from 0 to 1, closed trailing edge)
# Upper surface first (LE to TE), then lower surface (LE to TE)
# Source: Somers 1997 / UIUC Airfoil Database
# ---------------------------------------------------------------------------
S809_UPPER = np.array([
    [0.00000,  0.00000],
    [0.00250,  0.01710],
    [0.00500,  0.02380],
    [0.01250,  0.03740],
    [0.02500,  0.05240],
    [0.05000,  0.07320],
    [0.07500,  0.08840],
    [0.10000,  0.10100],
    [0.15000,  0.12020],
    [0.20000,  0.13470],
    [0.25000,  0.14560],
    [0.30000,  0.15280],
    [0.35000,  0.15610],
    [0.40000,  0.15620],
    [0.45000,  0.15340],
    [0.50000,  0.14810],
    [0.55000,  0.14060],
    [0.60000,  0.13090],
    [0.65000,  0.11930],
    [0.70000,  0.10600],
    [0.75000,  0.09160],
    [0.80000,  0.07610],
    [0.85000,  0.05980],
    [0.90000,  0.04280],
    [0.95000,  0.02540],
    [1.00000,  0.00120],
])

S809_LOWER = np.array([
    [0.00000,  0.00000],
    [0.00250, -0.01230],
    [0.00500, -0.01680],
    [0.01250, -0.02490],
    [0.02500, -0.03310],
    [0.05000, -0.04380],
    [0.07500, -0.05010],
    [0.10000, -0.05430],
    [0.15000, -0.05920],
    [0.20000, -0.06140],
    [0.25000, -0.06150],
    [0.30000, -0.05980],
    [0.35000, -0.05720],
    [0.40000, -0.05420],
    [0.45000, -0.05130],
    [0.50000, -0.04820],
    [0.55000, -0.04520],
    [0.60000, -0.04200],
    [0.65000, -0.03870],
    [0.70000, -0.03520],
    [0.75000, -0.03140],
    [0.80000, -0.02720],
    [0.85000, -0.02280],
    [0.90000, -0.01820],
    [0.95000, -0.01340],
    [1.00000,  0.00120],
])

# ---------------------------------------------------------------------------
# Blade geometry (Appendix A of SR-500-26173)
# Columns: r [m], chord [m], twist [deg]
# Pitch axis at 30% chord. Pitch reference at 75% span = 0 deg twist here.
# Tip pitch = 3 deg (test configuration from TP-500-29494).
# ---------------------------------------------------------------------------
TIP_PITCH_DEG = 3.0   # NASA-Ames test configuration

# Hub diameter assumed = 0.43 m radius = 0.86 m dia (typical for Phase VI)
HUB_RADIUS = 0.432   # m  (hub extends to ~28.5 in = 0.724 m, radius ~0.432)

BLADE_STATIONS = np.array([
    # r [m],  chord [m],  twist_geometric [deg]
    [0.660,   0.218,      29.00],   # hub transition start (computed)
    [0.883,   0.183,      28.00],   # transition
    [1.008,   0.349,      28.00],   # transition end / S809 start
    [1.258,   0.737,      20.05],
    [1.522,   0.710,      14.04],
    [1.798,   0.682,       9.67],
    [2.075,   0.654,       6.75],
    [2.352,   0.626,       4.84],
    [2.628,   0.598,       3.48],
    [2.905,   0.570,       2.40],
    [3.181,   0.542,       1.51],
    [3.458,   0.514,       0.76],
    [3.735,   0.486,       0.09],
    [3.772,   0.483,       0.00],   # 75% span — pitch reference
    [4.011,   0.459,      -0.55],
    [4.288,   0.431,      -1.11],
    [4.565,   0.403,      -1.55],
    [4.841,   0.375,      -1.84],
    [5.030,   0.356,      -2.00],   # tip
])

def get_airfoil_section(chord, twist_total_deg, pitch_axis_xc=0.30):
    """
    Return 2D airfoil points in the rotor plane (y-z plane),
    scaled to chord, rotated by twist, with pitch axis at 30% chord.
    pitch_axis_xc: fraction of chord where rotation axis sits
    Returns: upper (N,2), lower (N,2) arrays of (y, z) coordinates.
    """
    twist_rad = np.radians(twist_total_deg)

    def transform(pts_xc):
        # Scale to chord, shift so pitch axis is at origin
        x = (pts_xc[:, 0] - pitch_axis_xc) * chord
        z = pts_xc[:, 1] * chord
        # Rotate by twist (positive twist = nose up)
        y_rot =  x * np.cos(twist_rad) + z * np.sin(twist_rad)
        z_rot = -x * np.sin(twist_rad) + z * np.cos(twist_rad)
        return np.column_stack([y_rot, z_rot])

    upper = transform(S809_UPPER)
    lower = transform(S809_LOWER)
    return upper, lower

def section_3d(r, chord, twist_total_deg):
    """
    Return 3D points for one blade cross-section at span r.
    Blade spans along +z. Airfoil section lies in the x-y plane.
    x = streamwise (into wind, +x): mapped from 2D thickness direction (z_rot)
    y = tangential (rotor plane, +y): mapped from 2D chord direction (y_rot)
    z = spanwise (blade span)

    y_rot from get_airfoil_section is the chord-tangential component.
    z_rot is the thickness-streamwise component.
    Swap: x_3d = z_rot (thickness → streamwise), y_3d = y_rot (chord → tangential).
    Triangle winding is reversed below to compensate for the reflection.
    """
    upper_2d, lower_2d = get_airfoil_section(chord, twist_total_deg)
    n = len(upper_2d)
    pts_upper = np.column_stack([upper_2d[:, 1],   # x = z_rot = thickness/streamwise
                                  upper_2d[:, 0],   # y = y_rot = chord/tangential
                                  np.full(n, r)])
    pts_lower = np.column_stack([lower_2d[:, 1],
                                  lower_2d[:, 0],
                                  np.full(n, r)])
    return pts_upper, pts_lower

def write_ascii_stl(filename, triangles, name="blade"):
    """Write list of triangles [(v0,v1,v2), ...] as ASCII STL."""
    with open(filename, 'w') as f:
        f.write(f"solid {name}\n")
        for v0, v1, v2 in triangles:
            n = np.cross(v1 - v0, v2 - v0)
            norm = np.linalg.norm(n)
            if norm > 0:
                n /= norm
            f.write(f"  facet normal {n[0]:.6e} {n[1]:.6e} {n[2]:.6e}\n")
            f.write(f"    outer loop\n")
            f.write(f"      vertex {v0[0]:.6e} {v0[1]:.6e} {v0[2]:.6e}\n")
            f.write(f"      vertex {v1[0]:.6e} {v1[1]:.6e} {v1[2]:.6e}\n")
            f.write(f"      vertex {v2[0]:.6e} {v2[1]:.6e} {v2[2]:.6e}\n")
            f.write(f"    endloop\n")
            f.write(f"  endfacet\n")
        f.write(f"endsolid {name}\n")

def triangulate_strip(upper_a, lower_a, upper_b, lower_b):
    """
    Triangulate between two airfoil cross-sections.
    upper_a, lower_a: points at station a (N points each)
    upper_b, lower_b: points at station b (N points each)
    Returns list of triangles.
    """
    triangles = []
    n = len(upper_a)

    # Upper surface: reversed winding (x↔y swap in section_3d is a reflection)
    for i in range(n - 1):
        triangles.append((upper_a[i], upper_a[i+1], upper_b[i]))
        triangles.append((upper_b[i], upper_a[i+1], upper_b[i+1]))

    # Lower surface: reversed winding
    for i in range(n - 1):
        triangles.append((lower_a[i], lower_b[i], lower_a[i+1]))
        triangles.append((lower_b[i], lower_b[i+1], lower_a[i+1]))

    # Leading edge cap (first points of upper and lower)
    # Trailing edge cap (last points, nearly same location)

    return triangles

def cap_section(upper, lower):
    """Triangulate the end cap of a section (tip or root)."""
    triangles = []
    n = len(upper)
    # Fan triangulation from centroid
    pts = np.vstack([upper, lower[::-1]])
    centroid = pts.mean(axis=0)
    for i in range(len(pts) - 1):
        triangles.append((centroid, pts[i+1], pts[i]))   # reversed for reflection fix
    triangles.append((centroid, pts[0], pts[-1]))
    return triangles

def main():
    # Total twist = geometric twist + tip pitch setting
    # Geometric twist is zero at 75% span by definition.
    # Tip pitch adds a constant offset to all stations.
    stations = BLADE_STATIONS.copy()
    stations[:, 2] += TIP_PITCH_DEG   # add tip pitch to all geometric twists

    # Build cross-sections
    sections = []
    for r, chord, twist in stations:
        u3d, l3d = section_3d(r, chord, twist)
        sections.append((r, u3d, l3d))

    # Generate triangles for blade surface
    triangles = []
    for i in range(len(sections) - 1):
        _, ua, la = sections[i]
        _, ub, lb = sections[i+1]
        triangles.extend(triangulate_strip(ua, la, ub, lb))

    # Root cap
    _, u0, l0 = sections[0]
    triangles.extend(cap_section(u0, l0))

    # Tip cap
    _, ut, lt = sections[-1]
    triangles.extend(cap_section(ut, lt))

    out = os.path.join(os.path.dirname(__file__), "blade.stl")
    write_ascii_stl(out, triangles, "blade")
    print(f"Written {len(triangles)} triangles to {out}")

    # Also write a quick sanity check: chord and twist at each station
    print("\nBlade stations (with tip pitch applied):")
    print(f"{'r [m]':>8} {'chord [m]':>10} {'total twist [deg]':>18}")
    for r, chord, twist in stations:
        print(f"{r:8.3f} {chord:10.4f} {twist:18.3f}")

if __name__ == "__main__":
    main()
