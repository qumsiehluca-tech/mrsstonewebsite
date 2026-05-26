#!/usr/bin/env python3
"""Generate abstract industrial SVG art for Stone Cold Loans (Theme 3).

These are design-forward duotone compositions (diagonal geometry, halftone
fields, blueprint grids, grain) meant to read as art-directed imagery rather
than literal drawings. The client can swap any file for real business
photography by replacing it at the same path with the same dimensions.
"""
import os, random, math

OUT = os.path.join(os.path.dirname(__file__), "assets")
os.makedirs(OUT, exist_ok=True)

# Theme 3 palette
STEEL_D  = "#1c2126"
STEEL_M  = "#2b333a"
STEEL_L  = "#3d4853"
GREEN_D  = "#1d2b24"
GREEN_M  = "#2f4438"
AMBER    = "#e8a13a"
AMBER_D  = "#b87a1f"
HAZE     = "#0d0f12"

def grain(w, h, n=None, seed=1):
    random.seed(seed)
    n = n or int(w*h/9000)
    out = []
    for _ in range(n):
        x = random.uniform(0, w); y = random.uniform(0, h)
        r = random.uniform(.35, 1.3); o = random.uniform(.015, .07)
        out.append(f'<circle cx="{x:.0f}" cy="{y:.0f}" r="{r:.1f}" fill="#fff" opacity="{o:.2f}"/>')
    return "".join(out)

_HT_IDS = []
def halftone_def(w, h, gap, base_r, seed=2, color="#000", maxo=.5):
    """Return (defs, body) for a halftone dot pattern that fades top->bottom.
    Uses an SVG <pattern> + gradient mask so the file stays tiny."""
    pid = f"ht{seed}"
    mid = f"htm{seed}"
    defs = (
        f'<pattern id="{pid}" width="{gap}" height="{gap}" patternUnits="userSpaceOnUse">'
        f'<circle cx="{gap/2:.1f}" cy="{gap/2:.1f}" r="{base_r:.2f}" fill="{color}"/></pattern>'
        f'<linearGradient id="{mid}" x1="0" y1="0" x2="0" y2="1">'
        f'<stop offset="0" stop-color="#fff" stop-opacity="0"/>'
        f'<stop offset="1" stop-color="#fff" stop-opacity="{maxo}"/></linearGradient>'
    )
    body = (
        f'<g style="mix-blend-mode:multiply">'
        f'<rect width="{w}" height="{h}" fill="url(#{pid})" mask="url(#{mid}mask)"/></g>'
    )
    # mask wrapper
    mask = f'<mask id="{mid}mask"><rect width="{w}" height="{h}" fill="url(#{mid})"/></mask>'
    return defs + mask, body

def halftone(w, h, gap, base_r, fade=True, seed=2, color="#000", maxo=.5):
    """Backwards-compatible: returns just the body; defs registered globally."""
    d, body = halftone_def(w, h, gap, base_r, seed, color, maxo)
    _HT_IDS.append(d)
    return body

def diag_field(w, h, count, color, op, seed=3, slant=0.55):
    """Parallel diagonal bars — industrial striping."""
    random.seed(seed)
    out = []
    span = w + h
    step = span/count
    for i in range(count):
        x = i*step - h*slant
        bw = step*random.uniform(.18, .42)
        out.append(f'<path d="M{x:.0f} 0 L{x+bw:.0f} 0 L{x+bw+h*slant:.0f} {h} L{x+h*slant:.0f} {h}Z" '
                   f'fill="{color}" opacity="{op*random.uniform(.5,1):.3f}"/>')
    return "".join(out)

def wrap(w, h, defs, body, seed=1, vignette=True):
    vg = (f'<rect width="{w}" height="{h}" fill="url(#vg)"/>' if vignette else '')
    ht_defs = "".join(_HT_IDS)
    _HT_IDS.clear()
    return f'''<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" viewBox="0 0 {w} {h}">
<defs>
<linearGradient id="vg" x1="0" y1="0" x2="0" y2="1">
<stop offset="0" stop-color="#000" stop-opacity="0"/>
<stop offset="0.55" stop-color="#000" stop-opacity="0"/>
<stop offset="1" stop-color="{HAZE}" stop-opacity="0.78"/>
</linearGradient>
{defs}
{ht_defs}
</defs>
{body}
{vg}
{grain(w,h,seed=seed)}
</svg>'''

def base_grad(wid, w, h, c1, c2, ang="v"):
    if ang == "v":
        coords = 'x1="0" y1="0" x2="0" y2="1"'
    else:
        coords = 'x1="0" y1="0" x2="1" y2="1"'
    return (f'<linearGradient id="{wid}" {coords}>'
            f'<stop offset="0" stop-color="{c1}"/><stop offset="1" stop-color="{c2}"/></linearGradient>')

# ---------------------------------------------------------------- HERO
def hero():
    w, h = 1600, 900
    defs = base_grad("bg", w, h, "#283139", "#13171b", "d")
    b = [f'<rect width="{w}" height="{h}" fill="url(#bg)"/>']
    # large amber sun-disc behind, low and right
    b.append(f'<circle cx="1180" cy="540" r="360" fill="{AMBER}" opacity="0.10"/>')
    b.append(f'<circle cx="1180" cy="540" r="220" fill="{AMBER}" opacity="0.12"/>')
    # stacked horizon planes (abstract land)
    b.append(f'<path d="M0 600 L1600 540 L1600 900 L0 900Z" fill="{GREEN_D}" opacity="0.9"/>')
    b.append(f'<path d="M0 720 L1600 690 L1600 900 L0 900Z" fill="{STEEL_D}"/>')
    # bold converging diagonals (a road / direction, but abstract)
    b.append(f'<path d="M740 560 L860 560 L1140 900 L420 900Z" fill="#0c0e10" opacity="0.85"/>')
    b.append(f'<path d="M792 560 L808 560 L900 900 L690 900Z" fill="{AMBER}" opacity="0.22"/>')
    # halftone fade lower-left for printed-photo feel
    b.append(f'<g>{halftone(w,h,26,7,seed=11,maxo=.20)}</g>')
    # thin amber survey lines
    for yy in (560, 690):
        b.append(f'<line x1="0" y1="{yy}" x2="1600" y2="{yy-(yy-540)*0+ (0 if yy==560 else 0)}" '
                 f'stroke="{AMBER}" stroke-width="1.5" opacity="0.25"/>')
    return wrap(w, h, defs, "".join(b), seed=1)

# ---------------------------------------------------------------- INDUSTRY TILE
def tile(name, motif, seed, accent=AMBER):
    """Square-ish industry tile: duotone field + a bold geometric motif + halftone."""
    w, h = 800, 600
    defs = base_grad(f"bg{seed}", w, h, STEEL_M, STEEL_D, "d")
    b = [f'<rect width="{w}" height="{h}" fill="url(#bg{seed})"/>']
    b.append(f'<g>{diag_field(w,h,7,"#000",0.18,seed=seed)}</g>')
    b.append(motif)
    b.append(f'<g>{halftone(w,h,30,8,seed=seed+40,maxo=.22)}</g>')
    return wrap(w, h, defs, "".join(b), seed=seed, vignette=True)

def m_trucking():
    # abstract: long horizontal container bands + wheel circles
    b = []
    b.append('<rect x="120" y="300" width="520" height="150" rx="6" fill="#0d0f11" opacity="0.92"/>')
    b.append(f'<rect x="120" y="300" width="520" height="150" rx="6" fill="none" stroke="{AMBER}" stroke-width="2" opacity="0.4"/>')
    for i in range(5):
        x = 150 + i*100
        b.append(f'<line x1="{x}" y1="300" x2="{x}" y2="450" stroke="#000" stroke-width="6" opacity="0.5"/>')
    b.append(f'<rect x="560" y="250" width="120" height="120" rx="6" fill="{GREEN_M}"/>')
    for cx in (210, 330, 600):
        b.append(f'<circle cx="{cx}" cy="470" r="34" fill="#0a0b0c"/>')
        b.append(f'<circle cx="{cx}" cy="470" r="14" fill="{STEEL_L}"/>')
    b.append(f'<rect x="120" y="496" width="560" height="10" fill="{AMBER}" opacity="0.5"/>')
    return "".join(b)

def m_construction():
    # crane boom + scaffold grid
    b = []
    # scaffold grid
    for i in range(5):
        x = 120 + i*90
        b.append(f'<line x1="{x}" y1="180" x2="{x}" y2="500" stroke="#0d0f11" stroke-width="9" opacity="0.85"/>')
    for j in range(4):
        y = 200 + j*95
        b.append(f'<line x1="120" y1="{y}" x2="480" y2="{y}" stroke="#0d0f11" stroke-width="9" opacity="0.85"/>')
    # crane mast + boom
    b.append(f'<rect x="560" y="120" width="22" height="380" fill="{AMBER}"/>')
    b.append(f'<path d="M571 120 L760 120 L760 150 L571 165Z" fill="{AMBER}"/>')
    b.append(f'<line x1="640" y1="150" x2="640" y2="260" stroke="#0d0f11" stroke-width="6"/>')
    b.append(f'<rect x="624" y="260" width="32" height="30" fill="{STEEL_L}"/>')
    b.append(f'<rect x="120" y="500" width="640" height="14" fill="#0a0b0c"/>')
    return "".join(b)

def m_autorepair():
    # big gear + lift arms
    b = []
    cx, cy, R = 400, 300, 150
    teeth = 12
    pts = []
    for i in range(teeth*2):
        ang = math.pi*i/teeth
        rr = R if i % 2 == 0 else R*0.78
        pts.append(f'{cx+rr*math.cos(ang):.0f},{cy+rr*math.sin(ang):.0f}')
    b.append(f'<polygon points="{" ".join(pts)}" fill="#0d0f11" opacity="0.9"/>')
    b.append(f'<circle cx="{cx}" cy="{cy}" r="58" fill="{STEEL_D}"/>')
    b.append(f'<circle cx="{cx}" cy="{cy}" r="58" fill="none" stroke="{AMBER}" stroke-width="4" opacity="0.6"/>')
    b.append(f'<circle cx="{cx}" cy="{cy}" r="20" fill="{AMBER}" opacity="0.55"/>')
    # lift arm
    b.append(f'<rect x="120" y="470" width="560" height="16" fill="{AMBER}" opacity="0.5"/>')
    b.append(f'<rect x="150" y="430" width="120" height="40" fill="{GREEN_M}"/>')
    b.append(f'<rect x="530" y="430" width="120" height="40" fill="{GREEN_M}"/>')
    return "".join(b)

def m_restaurant():
    # abstract storefront + signage + steam arcs
    b = []
    b.append('<rect x="140" y="200" width="520" height="300" fill="#0d0f11" opacity="0.9"/>')
    b.append(f'<rect x="140" y="200" width="520" height="60" fill="{AMBER}" opacity="0.55"/>')
    b.append(f'<rect x="170" y="300" width="200" height="200" fill="{STEEL_M}"/>')
    b.append(f'<rect x="170" y="300" width="200" height="200" fill="none" stroke="{AMBER}" stroke-width="2" opacity="0.4"/>')
    for i in range(3):
        x = 420 + i*70
        b.append(f'<rect x="{x}" y="320" width="44" height="180" fill="{GREEN_M}"/>')
    # steam arcs
    for i in range(3):
        x = 250 + i*70
        b.append(f'<path d="M{x} 300 q -18 -40 0 -80 q 18 -40 0 -80" fill="none" '
                 f'stroke="{AMBER}" stroke-width="3" opacity="0.3"/>')
    b.append(f'<rect x="140" y="500" width="520" height="12" fill="#0a0b0c"/>')
    return "".join(b)

def m_logistics():
    # stacked container blocks + route line
    b = []
    cols = [(160, GREEN_M), (260, STEEL_L), (360, "#0d0f11"), (460, GREEN_M), (560, STEEL_L)]
    random.seed(7)
    for x, col in cols:
        stack = random.randint(2, 4)
        for s in range(stack):
            y = 470 - s*70
            b.append(f'<rect x="{x}" y="{y}" width="84" height="62" rx="3" fill="{col}" opacity="0.95"/>')
            b.append(f'<rect x="{x}" y="{y}" width="84" height="62" rx="3" fill="none" stroke="#000" stroke-width="2" opacity="0.4"/>')
            b.append(f'<line x1="{x+42}" y1="{y}" x2="{x+42}" y2="{y+62}" stroke="#000" stroke-width="2" opacity="0.3"/>')
    # route arc with nodes
    b.append(f'<path d="M120 180 Q 400 90 680 200" fill="none" stroke="{AMBER}" stroke-width="3" opacity="0.55" stroke-dasharray="2 10" stroke-linecap="round"/>')
    for px, py in [(120,180),(400,128),(680,200)]:
        b.append(f'<circle cx="{px}" cy="{py}" r="9" fill="{AMBER}" opacity="0.8"/>')
    b.append(f'<rect x="120" y="498" width="560" height="12" fill="#0a0b0c"/>')
    return "".join(b)

def m_trades():
    # crossed tools abstracted: wrench bar + hammer bar + bolt grid
    b = []
    # bolt grid backdrop
    for r in range(3):
        for c in range(6):
            x = 170 + c*80; y = 200 + r*90
            b.append(f'<circle cx="{x}" cy="{y}" r="7" fill="#000" opacity="0.4"/>')
    # diagonal tool bars
    b.append(f'<g transform="rotate(38 400 300)">'
             f'<rect x="180" y="285" width="440" height="34" rx="17" fill="#0d0f11" opacity="0.92"/>'
             f'<circle cx="180" cy="302" r="34" fill="none" stroke="#0d0f11" stroke-width="20"/></g>')
    b.append(f'<g transform="rotate(-38 400 300)">'
             f'<rect x="180" y="285" width="420" height="30" rx="6" fill="{AMBER}" opacity="0.85"/>'
             f'<rect x="560" y="262" width="70" height="76" rx="6" fill="{AMBER}" opacity="0.85"/></g>')
    b.append(f'<circle cx="400" cy="300" r="26" fill="{STEEL_L}"/>')
    b.append(f'<rect x="120" y="498" width="560" height="12" fill="#0a0b0c"/>')
    return "".join(b)

# ---------------------------------------------------------------- ABOUT
def about():
    w, h = 900, 1000
    defs = base_grad("abg", w, h, "#2c343c", "#15191d", "d")
    b = [f'<rect width="{w}" height="{h}" fill="url(#abg)"/>']
    b.append(f'<g>{diag_field(w,h,8,"#000",0.16,seed=21)}</g>')
    # blueprint frame
    b.append(f'<rect x="90" y="120" width="720" height="760" fill="none" stroke="{AMBER}" stroke-width="2" opacity="0.35"/>')
    # abstract building blocks rising — growth motif
    base_y = 760
    random.seed(5)
    for i in range(6):
        x = 150 + i*110
        bh = 120 + i*80
        col = GREEN_M if i % 2 else STEEL_L
        b.append(f'<rect x="{x}" y="{base_y-bh}" width="86" height="{bh}" fill="{col}" opacity="0.95"/>')
        b.append(f'<rect x="{x}" y="{base_y-bh}" width="86" height="{bh}" fill="none" stroke="#000" stroke-width="2" opacity="0.35"/>')
    b.append(f'<rect x="90" y="{base_y}" width="720" height="16" fill="#0a0b0c"/>')
    # ascending amber trend line
    pts = "150,720 260,650 370,560 480,500 590,420 700,330"
    b.append(f'<polyline points="{pts}" fill="none" stroke="{AMBER}" stroke-width="4" opacity="0.8"/>')
    for p in pts.split():
        px, py = p.split(",")
        b.append(f'<circle cx="{px}" cy="{py}" r="7" fill="{AMBER}"/>')
    b.append(f'<g>{halftone(w,h,32,9,seed=60,maxo=.20)}</g>')
    return wrap(w, h, defs, "".join(b), seed=9)

# ---------------------------------------------------------------- CTA
def cta():
    w, h = 1600, 600
    defs = base_grad("cbg", w, h, "#22292f", "#101316", "d")
    b = [f'<rect width="{w}" height="{h}" fill="url(#cbg)"/>']
    # bold amber chevrons sweeping right — momentum
    for i in range(5):
        x = -200 + i*420
        b.append(f'<path d="M{x} 0 L{x+160} 0 L{x+160+300} 300 L{x+160} 600 L{x} 600 L{x+300} 300Z" '
                 f'fill="{AMBER}" opacity="{0.05+i*0.015:.3f}"/>')
    # horizon strip
    b.append(f'<path d="M0 430 L1600 400 L1600 600 L0 600Z" fill="{GREEN_D}" opacity="0.9"/>')
    b.append(f'<rect x="0" y="486" width="1600" height="6" fill="{AMBER}" opacity="0.4"/>')
    b.append(f'<g>{halftone(w,h,28,7,seed=70,maxo=.16)}</g>')
    return wrap(w, h, defs, "".join(b), seed=7)

# ---------------------------------------------------------------- WRITE
def write(name, svg):
    p = os.path.join(OUT, name)
    with open(p, "w") as f:
        f.write(svg)
    print(f"  wrote {name} ({len(svg)} bytes)")

if __name__ == "__main__":
    write("hero.svg", hero())
    write("trucking.svg",     tile("trucking", m_trucking(), 101))
    write("construction.svg", tile("construction", m_construction(), 102))
    write("autorepair.svg",   tile("autorepair", m_autorepair(), 103))
    write("restaurant.svg",   tile("restaurant", m_restaurant(), 104))
    write("logistics.svg",    tile("logistics", m_logistics(), 105))
    write("trades.svg",       tile("trades", m_trades(), 106))
    write("about.svg", about())
    write("cta.svg", cta())
    print(f"Done. 9 assets in {OUT}")
