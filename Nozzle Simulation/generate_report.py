"""
Generate Nozzle_Simulation_Report.pdf from the portfolio images and data.
Run from the 'Nozzle Simulation' directory:
    python generate_report.py
"""

import os
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import cm
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_JUSTIFY
from reportlab.lib import colors
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Image, Table, TableStyle,
    PageBreak, HRFlowable, KeepTogether
)
from reportlab.platypus.flowables import BalancedColumns

W, H = A4
MARGIN = 2.2 * cm
IMG_DIR = os.path.join(os.path.dirname(__file__), "Linux Files")
OUT     = os.path.join(os.path.dirname(__file__), "Nozzle_Simulation_Report.pdf")

styles = getSampleStyleSheet()

def S(name, **kw):
    base = styles[name]
    return ParagraphStyle(name + "_custom", parent=base, **kw)

title_style   = S("Title",   fontSize=20, spaceAfter=6, textColor=colors.HexColor("#1a2a4a"))
h1_style      = S("Heading1", fontSize=14, spaceBefore=14, spaceAfter=4,
                  textColor=colors.HexColor("#1a2a4a"))
h2_style      = S("Heading2", fontSize=11, spaceBefore=10, spaceAfter=3,
                  textColor=colors.HexColor("#2c4a7a"))
body_style    = S("Normal",  fontSize=9,  spaceAfter=4,  leading=14,
                  alignment=TA_JUSTIFY)
mono_style    = S("Code",    fontSize=8,  fontName="Courier", spaceAfter=4,
                  backColor=colors.HexColor("#f4f4f4"), leading=12)
caption_style = S("Normal",  fontSize=8,  textColor=colors.grey,
                  alignment=TA_CENTER, spaceAfter=6)
small_style   = S("Normal",  fontSize=8,  spaceAfter=3, leading=12)

ACCENT = colors.HexColor("#2c4a7a")

def hr():
    return HRFlowable(width="100%", thickness=0.5, color=ACCENT, spaceAfter=6)

def h1(text):  return Paragraph(text, h1_style)
def h2(text):  return Paragraph(text, h2_style)
def p(text):   return Paragraph(text, body_style)
def sp(h=6):   return Spacer(1, h)

def img(fname, width=None, caption=None):
    fpath = os.path.join(IMG_DIR, fname)
    if not os.path.exists(fpath):
        return [p(f"<i>[Image not found: {fname}]</i>")]
    w = width or (W - 2*MARGIN)
    from PIL import Image as PILImage
    with PILImage.open(fpath) as im:
        iw, ih = im.size
    h = w * ih / iw
    items = [Image(fpath, width=w, height=h)]
    if caption:
        items.append(Paragraph(caption, caption_style))
    return items

def table(headers, rows, col_widths=None):
    data = [headers] + rows
    cw = col_widths or [((W - 2*MARGIN) / len(headers))] * len(headers)
    t = Table(data, colWidths=cw)
    t.setStyle(TableStyle([
        ("BACKGROUND",  (0,0), (-1,0),  ACCENT),
        ("TEXTCOLOR",   (0,0), (-1,0),  colors.white),
        ("FONTNAME",    (0,0), (-1,0),  "Helvetica-Bold"),
        ("FONTSIZE",    (0,0), (-1,-1), 8),
        ("ROWBACKGROUNDS", (0,1), (-1,-1), [colors.white, colors.HexColor("#edf2f8")]),
        ("GRID",        (0,0), (-1,-1), 0.3, colors.HexColor("#c0c8d8")),
        ("VALIGN",      (0,0), (-1,-1), "MIDDLE"),
        ("TOPPADDING",  (0,0), (-1,-1), 3),
        ("BOTTOMPADDING",(0,0),(-1,-1), 3),
        ("LEFTPADDING", (0,0), (-1,-1), 5),
    ]))
    return t

# ── content ────────────────────────────────────────────────────────────────────

story = []

# ── cover ─────────────────────────────────────────────────────────────────────
story += [
    sp(40),
    Paragraph("Rocket Nozzle CFD Simulation", title_style),
    Paragraph("Three-case study: hot gas · premixed combustion · separate injection",
              S("Normal", fontSize=12, textColor=colors.grey, alignment=TA_CENTER)),
    sp(10),
    Paragraph("OpenFOAM v2012 · Axisymmetric wedge · 14 400 cells",
              S("Normal", fontSize=10, textColor=ACCENT, alignment=TA_CENTER)),
    sp(6),
    hr(),
    sp(6),
    Paragraph("Samuel Simmons", S("Normal", fontSize=9, alignment=TA_CENTER)),
]

# ── Section 1: Overview ───────────────────────────────────────────────────────
story += [PageBreak(), h1("1. Overview"), hr()]
story += [p(
    "Three OpenFOAM simulations of a De Laval (converging-diverging) rocket nozzle are "
    "presented on an identical extended 5-block axisymmetric mesh. The domain extends from "
    "the chamber head (x = −0.30 m) through the nozzle throat and diverging section to a "
    "downstream plume region (x = 1.50 m), allowing the supersonic jet and its interaction "
    "with the ambient far-field to be captured."
)]
story += [sp(4), table(
    ["Case", "Solver", "Description"],
    [
        ["Hot gas (frozen)", "rhoCentralFoam",
         "Single-species perfect gas (M=22 g/mol, γ=1.2). Density-based explicit solver."],
        ["Premixed combustion", "rhoReactingFoam",
         "C₁₂H₂₆/O₂ pre-mixed at inlet. Single-step Arrhenius. JANAF thermodynamics."],
        ["Separate injection", "rhoReactingFoam",
         "Fuel and LOX through dedicated inlets; mixing and reaction downstream."],
    ],
    col_widths=[3.5*cm, 3.5*cm, 10*cm]
)]

# ── Section 2: Mesh ───────────────────────────────────────────────────────────
story += [sp(8), h1("2. Mesh"), hr()]
story += [p(
    "The mesh is a 5-degree wedge (one cell in the azimuthal direction) generated with "
    "<b>blockMesh</b>. Five blocks cover the chamber, converging section, diverging section, "
    "plume core (x = 0.50–1.50 m, r = 0–0.14 m), and plume ambient "
    "(x = 0.50–1.50 m, r = 0.14–0.50 m)."
), sp(4)]

story += [table(
    ["Parameter", "Value"],
    [
        ["Chamber radius", "0.150 m"],
        ["Throat radius", "0.050 m"],
        ["Exit radius", "0.1414 m"],
        ["Throat position", "x = 0.150 m"],
        ["Domain x range", "−0.30 m → 1.50 m"],
        ["Domain r range", "0 → 0.50 m"],
        ["Total cells", "14 400"],
    ],
    col_widths=[6*cm, 11*cm]
), sp(6)]

story += img("Nozzle_mesh.png", caption="Fig. 1 — Axisymmetric wedge mesh (hot-gas case, x–r plane).")
story += img("Nozzle_combustion_mesh.png", caption="Fig. 2 — Same mesh used for combustion cases.")

# ── Section 3: Hot gas ────────────────────────────────────────────────────────
story += [PageBreak(), h1("3. Case 1 — Hot Gas (rhoCentralFoam)"), hr()]
story += [p(
    "Combustion products are approximated as a single-species perfect gas representative "
    "of an LOX/kerosene flame (M = 22 g/mol, γ = 1.2, Cp = 2 267 J/kg K). The density-based "
    "explicit solver <b>rhoCentralFoam</b> (Kurganov–Tadmor flux, vanLeer MUSCL, CFL = 0.1) "
    "captures the transonic throat, supersonic expansion fan, and plume development."
), sp(4)]

story += [table(
    ["Property", "Value", "Notes"],
    [
        ["Molecular weight", "22 g/mol", "CO₂/H₂O/CO/H₂ mixture"],
        ["γ", "1.2", "Triatomic-dominated"],
        ["Chamber pressure p₀", "3 MPa", "Total pressure at inlet"],
        ["Chamber temperature T₀", "3 000 K", "Approximate adiabatic flame T"],
        ["Back pressure", "101 325 Pa", "Sea level — over-expanded nozzle"],
        ["Exit Mach (design)", "3.20", "Isentropic 1-D theory"],
    ],
    col_widths=[5*cm, 3*cm, 9*cm]
), sp(6)]

story += img("nozzle_Mach_contour.png",
             caption="Fig. 3 — Mach number contour (nozzle-only domain, validated design point). "
                     "Exit Mach ≈ 3.22 matches isentropic theory (3.20) to within 1%.")

story += [h2("3.2 Extended plume domain — early transient (t = 0.0005 s)"), p(
    "The hot-gas case on the extended 5-block plume domain is shown at t = 0.5 ms. "
    "The inlet shock is propagating into the initially-atmospheric plume region. "
    "Long-time steady state is represented by the validated nozzle-only result above."
)]
story += img("Nozzle_overview.png",
             caption="Fig. 4 — T, p, |U| at t = 0.5 ms (extended plume domain, startup transient).")
story += img("Nozzle_axis_profiles.png",
             caption="Fig. 5 — Axis profiles of T, p, |U| at t = 0.5 ms.")

# ── Section 4: Premixed combustion ───────────────────────────────────────────
story += [PageBreak(), h1("4. Case 2 — Premixed Combustion (rhoReactingFoam)"), hr()]
story += [p(
    "Pre-mixed C₁₂H₂₆/O₂ (kerosene surrogate; Y_fuel = 0.20, Y_O₂ = 0.80) enters at "
    "T = 500 K, p = 3 MPa. A single-step global Arrhenius reaction releases heat as the "
    "reactants mix and ignite. Species thermodynamics use NASA-7 JANAF polynomials; "
    "viscosity follows Sutherland's law. Simulation time: 0 → 0.003 s."
), sp(4)]

story += [Paragraph("<b>Reaction:</b>", body_style),
          Paragraph(
              "2 C₁₂H₂₆ + 37 O₂ → 24 CO₂ + 26 H₂O&nbsp;&nbsp;"
              "(A = 5.1×10¹¹ m³/kmol·s, Tₐ = 15 034 K)",
              mono_style
          ), sp(4)]

story += [h2("4.1 Flow fields — t = 0.003 s")]
story += img("Nozzle_combustion_overview.png",
             caption="Fig. 4 — Temperature, pressure, velocity magnitude, and C₁₂H₂₆ mass "
                     "fraction at t = 0.003 s (premixed case).")

story += [h2("4.2 Axis profiles")]
story += img("Nozzle_combustion_axis_profiles.png",
             caption="Fig. 5 — Temperature, pressure, and velocity magnitude along the "
                     "nozzle axis (premixed case).")

story += [h2("4.3 Species distributions")]
story += img("Nozzle_combustion_species.png",
             caption="Fig. 6 — Mass fraction fields (C₁₂H₂₆, O₂, CO₂, H₂O) at t = 0.003 s.")
story += img("Nozzle_combustion_species_profiles.png",
             caption="Fig. 7 — Species mass fractions along the nozzle axis.")

# ── Section 5: Separate injection ────────────────────────────────────────────
story += [PageBreak(), h1("5. Case 3 — Separate Injection (rhoReactingFoam)"), hr()]
story += [p(
    "Kerosene (fuel_inlet) and liquid oxygen (lox_inlet) are injected through separate "
    "concentric annular inlets at the chamber head. The chamber is pre-filled with "
    "combustion equilibrium products (CO₂ = 0.693, H₂O = 0.307 by mass) at T = 3 000 K "
    "and p = 3 MPa. Reaction occurs downstream where mixing brings reactants to the "
    "ignition threshold. Simulation time: 0 → 0.005 s."
), sp(4)]

story += [table(
    ["Parameter", "Value"],
    [
        ["Fuel inlet species", "C₁₂H₂₆ (kerosene surrogate)"],
        ["Oxidiser inlet species", "O₂"],
        ["Inlet total pressure", "3 MPa (both)"],
        ["Design O/F ratio", "≈ 2.7 (stoichiometric C₁₂H₂₆/O₂)"],
        ["Initial chamber fill", "CO₂ + H₂O (equilibrium products)"],
    ],
    col_widths=[6*cm, 11*cm]
), sp(6)]

story += [h2("5.1 Flow fields — t = 0.005 s")]
story += img("Nozzle_injected_overview.png",
             caption="Fig. 8 — Temperature, pressure, velocity magnitude, and C₁₂H₂₆ mass "
                     "fraction at t = 0.005 s (separate injection case).")

story += [h2("5.2 Axis profiles")]
story += img("Nozzle_injected_axis_profiles.png",
             caption="Fig. 9 — Temperature, pressure, and velocity magnitude along the "
                     "nozzle axis (separate injection case).")

story += [h2("5.3 Species distributions")]
story += img("Nozzle_injected_species.png",
             caption="Fig. 10 — Mass fraction fields (C₁₂H₂₆, O₂, CO₂, H₂O) at t = 0.005 s.")
story += img("Nozzle_injected_species_profiles.png",
             caption="Fig. 11 — Species axis profiles showing fuel/oxidiser mixing and "
                     "product formation.")

# ── Section 6: Technical notes ────────────────────────────────────────────────
story += [PageBreak(), h1("6. Implementation Notes"), hr()]
notes = [
    ("<b>Thermodynamic consistency (rhoCentralFoam):</b> The initial density must satisfy "
     "ρ = p / (R_spec · T) uniformly. Mismatching the far-field ρ against the interior "
     "pressure causes Newton iteration in hePsiThermo::correct() to diverge to T → 10¹² K. "
     "Outer boundary: zeroGradient on both p and ρ ensures consistency at startup."),
    ("<b>foamChemistryReader elements block:</b> readSpeciesComposition() looks for an "
     "'elements {}' sub-dictionary directly inside each species' top-level block in "
     "constant/thermo — NOT inside the nested 'specie {}' block. A top-level "
     "'elements (C H O);' list also triggers a HashPtrTable parsing error."),
    ("<b>Species mass fraction initialisation:</b> All Y_i must sum to 1 at every patch "
     "face at t = 0 (including inletOutlet 'value' fields at the outlet). A zero-sum "
     "causes division-by-zero in multiComponentMixture::patchFaceVolMixture()."),
    ("<b>Far-field pressure BC:</b> waveTransmissive at the outer_boundary amplifies the "
     "startup pressure wave from the high-pressure interior into the atmospheric far-field. "
     "zeroGradient for p at that boundary is more stable during the initial transient."),
    ("<b>C12H26 JANAF coefficients:</b> Tcommon is set to 300 K with identical low/high "
     "coefficient arrays to avoid discontinuity artefacts; Tlow = 200 K, Thigh = 5 000 K. "
     "The JANAF limit() function clips T to [Tlow, Thigh] — out-of-range warnings are "
     "expected in regions exceeding 5 000 K and do not indicate solver failure."),
]
for note in notes:
    story += [p(f"• {note}"), sp(2)]

# ── Section 7: Limitations ────────────────────────────────────────────────────
story += [h1("7. Limitations"), hr()]
lims = [
    "Conical nozzle — a bell or Rao-optimised profile reduces divergence loss.",
    "Single-step global Arrhenius — no intermediate species (CO, OH, H) or dissociation.",
    "Adiabatic walls — no regenerative cooling or conjugate heat transfer.",
    "Laminar — turbulent mixing of the fuel/oxidiser shear layer not modelled (Case 3).",
    "2-D axisymmetric — no azimuthal instabilities, swirl, or injector pattern effects.",
    "Short simulation times — steady-state plume not yet established in Cases 2 and 3.",
]
for lim in lims:
    story += [p(f"• {lim}")]

# ── build ──────────────────────────────────────────────────────────────────────

doc = SimpleDocTemplate(
    OUT, pagesize=A4,
    leftMargin=MARGIN, rightMargin=MARGIN,
    topMargin=MARGIN, bottomMargin=MARGIN,
)

def add_footer(canvas, doc):
    canvas.saveState()
    canvas.setFont("Helvetica", 7)
    canvas.setFillColor(colors.grey)
    canvas.drawCentredString(W/2, 1.2*cm,
        f"Rocket Nozzle CFD Simulation — Samuel Simmons — Page {doc.page}")
    canvas.restoreState()

doc.build(story, onFirstPage=add_footer, onLaterPages=add_footer)
print(f"PDF written to {OUT}")
