"""Build the SVG graphics for the github.com/ZLJLZX profile README.

    python tools/build.py        # writes assets/*-light.svg and assets/*-dark.svg

Every graphic comes in a light version (sunny sky) and a dark version (sunrise);
README.md shows the one matching the viewer's GitHub theme. Text is converted to
vector outlines (textpath.py), so the images look the same on every computer.
Change the wording in the CONTENT block and run the script again.
Fonts (SIL Open Font License) are downloaded from google/fonts on first run.
Requires: pip install fonttools uharfbuzz
"""
from __future__ import annotations

import math
import os
import random
import urllib.request

from textpath import Font, Mixed

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ASSETS = os.path.join(ROOT, "assets")
FONT_DIR = os.environ.get("FONT_DIR", os.path.join(ROOT, "tools", ".fonts"))

# ----------------------------------------------------------------------------
# CONTENT: edit here
# ----------------------------------------------------------------------------
NAME = "ZLJLZX"
GREETING = ("Hi there, I'm", "你好，我是")
TYPING = [  # the header cycles through these lines
    "AI for Science Researcher",
    "Medical Imaging × AI Systems Theory",
    "医学图像 × AI 系统理论",
    "用 AI 帮科学看得更远",
    "Stay curious. Stay sunny.",
]
HOBBIES = [  # (key, English, 中文, flavour line)
    ("basketball", "Basketball", "篮球", "Nothing but net · 空心入网"),
    ("hiking", "Hiking", "徒步", "Touch grass · 去山里充电"),
    ("music", "Music", "音乐", "On repeat · 单曲循环"),
    ("f1", "Formula 1", "F1 赛车", "Lights out! · 熄灯起步"),
    ("anime", "Anime", "动漫", "One more episode · 再看一集"),
]
FOOTER = ("Thanks for stopping by, have a sunny day!", "感谢来访，愿你今天也阳光明媚")
PROJECTS = [  # featured project cards; colours are (light theme, dark theme)
    dict(key="pair", name="PAIR", icon="molecule", color=("#6d5dfc", "#a99fff"),
         kicker="MOLECULAR DESIGN · 分子设计",
         en="Phase-aware iterative refinement for structure-based molecular generation",
         zh="基于贝叶斯流网络、无需训练的结构导向分子设计",
         tags=["Python", "PyTorch", "Drug design"]),
    dict(key="pmidfrag", name="pmidfrag", icon="paper", color=("#0b9b8f", "#5ee0d0"),
         kicker="BIOINFORMATICS · 生物信息",
         en="Which papers does your GO enrichment result stand on?",
         zh="GO 富集分析结果的文献溯源与稳健性审计",
         tags=["Python", "Gene Ontology", "Reproducibility"]),
]

# ----------------------------------------------------------------------------
# Themes
# ----------------------------------------------------------------------------
THEMES = {
    "light": dict(
        page="#ffffff",
        sky=[(0, "#bde3ff"), (0.55, "#e4f4ff"), (1, "#fff1d6")],
        greet="#4b5d78", greet_zh="#7a8aa3", name="#13315c",
        marker=("#ffd166", "#ffe08a"), marker_op=0.75, type="#f4632e",
        sun=(1032, 112, 50), sun_fill=("#fff6b8", "#ffd84a", "#ffbb2e"), ray="#ffc83d", halo="#ffe98a",
        halo_op=0.55, glow_r=330, glow="#fff4c2", glow_op=0.9,
        cloud="#ffffff", cloud_shade="#d7e9fb", cloud_op=1.0,
        waves=[("#ffe08f", 0.9), ("#a6dbff", 0.85), ("#ffffff", 1.0)],
        sparkle="#ffc93c", night=False,
        card="#ffffff", card_stroke="#e3e9f2", card_shadow=0.09, title="#1b2a44", muted="#6a7890",
        blob_op=0.16, foot_title="#13315c", foot_sub="#56657d",
        foot_waves=[("#ffe08f", 0.9), ("#bfe5ff", 0.95), ("#8fcdf7", 1.0)],
    ),
    "dark": dict(
        page="#0d1117",
        sky=[(0, "#0d1736"), (0.42, "#27286a"), (0.76, "#93487f"), (1, "#ff9357")],
        greet="#c8d0ff", greet_zh="#a5acd9", name="#ffffff",
        marker=("#ff6fa3", "#ffa24c"), marker_op=0.6, type="#ffd166",
        sun=(1010, 296, 74), sun_fill=("#fff7cf", "#ffc94d", "#ff8a3d"), ray="#ffd27a", halo="#ffa25e",
        halo_op=0.5, glow_r=420, glow="#ff9f5f", glow_op=0.55,
        cloud="#f4a3b8", cloud_shade="#7a4c93", cloud_op=0.55,
        waves=[("#ff9a62", 0.42), ("#2f2d72", 0.92), ("#0d1117", 1.0)],
        sparkle="#ffffff", night=True,
        card="#161b22", card_stroke="#30363d", card_shadow=0.0, title="#e6edf3", muted="#8b949e",
        blob_op=0.2, foot_title="#e6edf3", foot_sub="#9aa4b2",
        foot_waves=[("#e0679e", 0.6), ("#5a4cc0", 0.8), ("#2b2a6e", 1.0)],
    ),
}
HOBBY_COLORS = {"basketball": "#ff8a3d", "hiking": "#22c55e", "music": "#8b5cf6", "f1": "#ef4444", "anime": "#ec6aa8"}

# ----------------------------------------------------------------------------
# Fonts
# ----------------------------------------------------------------------------
GF = "https://raw.githubusercontent.com/google/fonts/main/ofl/"
FONT_FILES = {
    "Nunito[wght].ttf": "nunito/Nunito%5Bwght%5D.ttf",
    "NotoSansSC[wght].ttf": "notosanssc/NotoSansSC%5Bwght%5D.ttf",
}


def font_path(name: str) -> str:
    p = os.path.join(FONT_DIR, name)
    if not os.path.exists(p):
        os.makedirs(FONT_DIR, exist_ok=True)
        print(f"downloading {name} ...")
        urllib.request.urlretrieve(GF + FONT_FILES[name], p)
    return p


class Fonts:
    def __init__(self):
        nun, sc = font_path("Nunito[wght].ttf"), font_path("NotoSansSC[wght].ttf")
        self.n9 = Font(nun, wght=900)
        self.n8 = Font(nun, wght=800)
        self.n7 = Font(nun, wght=700)
        self.sc5 = Font(sc, wght=500)
        self.sc6 = Font(sc, wght=600)
        self.sc7 = Font(sc, wght=700)
        self.mix7 = Mixed(self.n8, self.sc6, cjk_scale=0.94)   # typing line
        self.mix_small = Mixed(self.n7, self.sc5, cjk_scale=0.95)


F: Fonts | None = None


# ----------------------------------------------------------------------------
# helpers
# ----------------------------------------------------------------------------
def n(v: float) -> str:
    s = f"{v:.1f}"
    s = s[:-2] if s.endswith(".0") else s
    return "0" if s == "-0" else s


def text(font, s, x, y, size, fill, tracking=0.0, anchor="start", extra=""):
    d, w = font.path(s, x, y, size, tracking, anchor)
    return f'<path d="{d}" fill="{fill}"{extra}/>', w


def svg_doc(w, h, body, title, css="", defs=""):
    return (
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" viewBox="0 0 {w} {h}" '
        f'role="img" aria-label="{title}">\n<title>{title}</title>\n'
        f"<style>{css}\n@media (prefers-reduced-motion: reduce){{*{{animation:none!important}}}}</style>\n"
        f"<defs>{defs}</defs>\n{body}\n</svg>\n"
    )


def wave_path(y0, amp, period, phase, x_from, x_to, bottom, step=8):
    pts = []
    x = x_from
    while x <= x_to:
        y = y0 + amp * math.sin(2 * math.pi * x / period + phase) + amp * 0.35 * math.sin(4 * math.pi * x / period + phase * 1.7)
        pts.append(f"{n(x)} {n(y)}")
        x += step
    return f"M{n(x_from)} {bottom}L" + "L".join(pts) + f"L{n(x_to)} {bottom}Z"


def waves(W, H, layers, bases, css, prefix):
    """Layered sine waves that drift sideways and loop seamlessly."""
    out = []
    specs = [(14, 600, 0.4, 22, 1), (11, 400, 2.1, 16, -1), (9, 300, 4.0, 12, 1)]
    for i, ((color, op), y0) in enumerate(zip(layers, bases)):
        amp, period, phase, dur, direction = specs[i]
        d = wave_path(y0, amp, period, phase, -period, W + period, H + 2)
        cls = f"{prefix}w{i}"
        start, end = (0, -period) if direction > 0 else (-period, 0)
        css.append(f".{cls}{{animation:{cls} {dur}s linear infinite}}"
                   f"@keyframes {cls}{{from{{transform:translateX({start}px)}}to{{transform:translateX({end}px)}}}}")
        out.append(f'<path class="{cls}" d="{d}" fill="{color}" fill-opacity="{op}"/>')
    return "".join(out)


def cloud(x, y, s, fill, shade, op, cls="", delay=0.0):
    """A fluffy cloud built from circles (group opacity keeps overlaps clean)."""
    blobs = [(0, 0, 26), (26, -12, 30), (56, -2, 24), (78, 8, 17), (-20, 10, 17)]
    base = f'<rect x="{n(-22 * s)}" y="{n(4 * s)}" width="{n(118 * s)}" height="{n(24 * s)}" rx="{n(12 * s)}"/>'
    circles = "".join(f'<circle cx="{n(bx * s)}" cy="{n(by * s)}" r="{n(r * s)}"/>' for bx, by, r in blobs)
    style = f' style="animation-delay:-{delay:.1f}s"' if delay else ""
    return (f'<g transform="translate({n(x)} {n(y)})"><g class="{cls}"{style} opacity="{op}">'
            f'<g fill="{shade}" transform="translate(0 {n(5 * s)})">{circles}{base}</g>'
            f'<g fill="{fill}">{circles}{base}</g></g></g>')


def sparkle(x, y, r, fill, delay, dur=2.6):
    p = (f"M{n(x)} {n(y - r)}Q{n(x + r * .18)} {n(y - r * .18)} {n(x + r)} {n(y)}"
         f"Q{n(x + r * .18)} {n(y + r * .18)} {n(x)} {n(y + r)}"
         f"Q{n(x - r * .18)} {n(y + r * .18)} {n(x - r)} {n(y)}"
         f"Q{n(x - r * .18)} {n(y - r * .18)} {n(x)} {n(y - r)}Z")
    return (f'<path d="{p}" fill="{fill}" class="twinkle" style="transform-origin:{n(x)}px {n(y)}px;'
            f'animation-duration:{dur}s;animation-delay:-{delay:.2f}s"/>')


# ----------------------------------------------------------------------------
# typing animation (SMIL; loops through all lines)
# ----------------------------------------------------------------------------
def typing_block(lines, x, y, size, color, font, id_prefix="t", type_s=0.075, hold=2.2, del_s=0.028, gap=0.35):
    # timeline
    events = []
    t = 0.6
    for s in lines:
        edges = font.boundaries(s, x, size)
        widths = [e - x + 2 for e in edges]
        seq = []
        for i, wv in enumerate(widths):
            seq.append((t + i * type_s, wv))
        t_hold = t + len(widths) * type_s
        t_del = t_hold + hold
        for i, wv in enumerate(reversed(widths[:-1])):
            seq.append((t_del + i * del_s, wv))
        t_end = t_del + (len(widths) - 1) * del_s
        seq.append((t_end, 0.0))
        events.append((t, seq, t_end))
        t = t_end + gap
    total = t

    defs, body = [], []
    cursor_pts = [(0.0, x + 2)]
    for li, (s, (t0, seq, t_end)) in enumerate(zip(lines, events)):
        d, _ = font.path(s, x, y, size)
        times = [0.0] + [ts for ts, _ in seq] + [total]
        vals = [0.0] + [wv for _, wv in seq] + [0.0]
        # merge identical times (keep last)
        kt, vv = [], []
        for ts, v in zip(times, vals):
            if kt and abs(ts - kt[-1]) < 1e-6:
                vv[-1] = v
            else:
                kt.append(ts)
                vv.append(v)
        key = ";".join(f"{ts / total:.5f}" for ts in kt)
        values = ";".join(n(v) for v in vv)
        defs.append(f'<clipPath id="{id_prefix}{li}"><rect x="{n(x - 1)}" y="{n(y - size * 1.05)}" height="{n(size * 1.45)}" width="0">'
                    f'<animate attributeName="width" values="{values}" keyTimes="{key}" dur="{total:.2f}s" '
                    f'calcMode="discrete" repeatCount="indefinite"/></rect></clipPath>')
        body.append(f'<g clip-path="url(#{id_prefix}{li})"><path d="{d}" fill="{color}"/></g>')
        cursor_pts += [(ts, x + wv + 3) for ts, wv in seq]
    cursor_pts.append((total, x + 2))
    kt, vv = [], []
    for ts, v in cursor_pts:
        if kt and abs(ts - kt[-1]) < 1e-6:
            vv[-1] = v
        else:
            kt.append(ts)
            vv.append(v)
    key = ";".join(f"{ts / total:.5f}" for ts in kt)
    values = ";".join(n(v) for v in vv)
    body.append(f'<rect x="{n(x + 2)}" y="{n(y - size * .8)}" width="3.2" height="{n(size * .98)}" rx="1.6" fill="{color}">'
                f'<animate attributeName="x" values="{values}" keyTimes="{key}" dur="{total:.2f}s" calcMode="discrete" repeatCount="indefinite"/>'
                f'<animate attributeName="opacity" values="1;0" dur="1.05s" calcMode="discrete" repeatCount="indefinite"/></rect>')
    return "".join(defs), "".join(body)


# ----------------------------------------------------------------------------
# HEADER
# ----------------------------------------------------------------------------
def build_header(theme: str):
    T = THEMES[theme]
    W, H = 1200, 360
    rng = random.Random(42)
    css, body = [], []
    sky = "".join(f'<stop offset="{o}" stop-color="{c}"/>' for o, c in T["sky"])
    sx, sy, sr = T["sun"]
    defs = f"""
<clipPath id="card"><rect width="{W}" height="{H}" rx="26"/></clipPath>
<linearGradient id="sky" x1="0" y1="0" x2="0" y2="1">{sky}</linearGradient>
<radialGradient id="glow" cx="{sx}" cy="{sy}" r="{T['glow_r']}" gradientUnits="userSpaceOnUse"><stop offset="0" stop-color="{T['glow']}" stop-opacity="{T['glow_op']}"/><stop offset="1" stop-color="{T['glow']}" stop-opacity="0"/></radialGradient>
<radialGradient id="sunfill" cx=".42" cy=".38" r=".7"><stop offset="0" stop-color="{T['sun_fill'][0]}"/><stop offset=".55" stop-color="{T['sun_fill'][1]}"/><stop offset="1" stop-color="{T['sun_fill'][2]}"/></radialGradient>
<filter id="soft" x="-50%" y="-50%" width="200%" height="200%"><feGaussianBlur stdDeviation="14"/></filter>
<linearGradient id="marker" x1="0" y1="0" x2="1" y2="0"><stop offset="0" stop-color="{T['marker'][0]}"/><stop offset="1" stop-color="{T['marker'][1]}"/></linearGradient>
"""
    body.append('<g clip-path="url(#card)">')
    body.append(f'<rect width="{W}" height="{H}" fill="url(#sky)"/>')
    body.append(f'<rect width="{W}" height="{H}" fill="url(#glow)"/>')

    # stars (night) / birds (day)
    if T["night"]:
        for _ in range(34):
            x, y = rng.uniform(20, 1180), rng.uniform(10, 170)
            if 60 < x < 700 and 60 < y < 280:
                continue
            r = rng.uniform(0.8, 1.9)
            body.append(f'<circle cx="{n(x)}" cy="{n(y)}" r="{n(r)}" fill="#fff" class="star" '
                        f'style="animation-delay:-{rng.uniform(0, 4):.2f}s;animation-duration:{rng.uniform(2.5, 5):.2f}s"/>')
        css.append(".star{animation:star 4s ease-in-out infinite}@keyframes star{0%,100%{opacity:.25}50%{opacity:.95}}")
    else:
        for i, (bx, by, s, dur) in enumerate([(760, 70, 1.0, 38), (800, 92, 0.75, 38)]):
            wing = f"M{-9 * s} 0Q{-4.5 * s} {-6 * s} 0 0Q{4.5 * s} {-6 * s} {9 * s} 0"
            body.append(f'<g transform="translate({bx} {by})"><g class="bird" style="animation-delay:-{i * 3}s">'
                        f'<path d="{wing}" fill="none" stroke="#56688a" stroke-width="2" stroke-linecap="round" class="flap" '
                        f'style="animation-delay:-{i * .2:.1f}s"/></g></g>')
        css.append(".bird{animation:bird 26s ease-in-out infinite}"
                   "@keyframes bird{0%{transform:translate(-40px,6px)}50%{transform:translate(60px,-8px)}100%{transform:translate(-40px,6px)}}"
                   ".flap{animation:flap .7s ease-in-out infinite;transform-box:fill-box;transform-origin:center}"
                   "@keyframes flap{50%{transform:scaleY(.35)}}")

    # sun: glow halo, rotating rays, disk
    rays = []
    for i in range(12):
        a = math.radians(i * 30)
        r0, r1 = sr + 18, sr + (44 if i % 2 == 0 else 34)
        rays.append(f"M{n(sx + r0 * math.cos(a))} {n(sy + r0 * math.sin(a))}L{n(sx + r1 * math.cos(a))} {n(sy + r1 * math.sin(a))}")
    body.append(f'<circle cx="{sx}" cy="{sy}" r="{sr + 34}" fill="{T["halo"]}" opacity="{T["halo_op"]}" filter="url(#soft)" class="breathe" style="transform-origin:{sx}px {sy}px"/>')
    body.append(f'<g class="spin" style="transform-origin:{sx}px {sy}px"><path d="{"".join(rays)}" stroke="{T["ray"]}" stroke-width="7" stroke-linecap="round" opacity=".9"/></g>')
    body.append(f'<circle cx="{sx}" cy="{sy}" r="{sr}" fill="url(#sunfill)"/>')
    css.append(".spin{animation:spin 50s linear infinite}@keyframes spin{to{transform:rotate(360deg)}}"
               ".breathe{animation:breathe 5s ease-in-out infinite}@keyframes breathe{50%{transform:scale(1.08)}}")

    # sparkles near the sun
    for i, (px, py, pr) in enumerate([(900, 64, 8), (1142, 196, 7), (948, 190, 5), (1150, 48, 5), (860, 150, 4)]):
        body.append(sparkle(px, py, pr, T["sparkle"], i * 0.7))
    css.append(".twinkle{animation:twinkle 2.6s ease-in-out infinite}@keyframes twinkle{0%,100%{transform:scale(.5);opacity:.3}50%{transform:scale(1.1);opacity:1}}")

    # clouds
    for i, (cx_, cy_, s, dl) in enumerate([(850, 190, 0.9, 0), (1085, 232, 0.62, 6), (610, 62, 0.5, 11)]):
        body.append(cloud(cx_, cy_, s, T["cloud"], T["cloud_shade"], T["cloud_op"], "drift", dl))
    css.append(".drift{animation:drift 22s ease-in-out infinite}@keyframes drift{50%{transform:translateX(34px)}}")

    # waves (sunrise glints on the dark version)
    body.append(waves(W, H, T["waves"], [300, 314, 330], css, "h"))
    if T["night"]:
        for i in range(9):
            gx = sx - 60 + rng.uniform(0, 120)
            gy = 322 + i * 3.5
            gw = rng.uniform(14, 40) * (1 - i * 0.06)
            body.append(f'<rect x="{n(gx - gw / 2)}" y="{n(gy)}" width="{n(gw)}" height="1.6" rx=".8" fill="#ffd18a" class="glint" '
                        f'style="animation-delay:-{rng.uniform(0, 2):.2f}s"/>')
        css.append(".glint{animation:glint 2.2s ease-in-out infinite}@keyframes glint{0%,100%{opacity:.15}50%{opacity:.8}}")

    # greeting + waving hand
    g1, w1 = text(F.n8, GREETING[0], 72, 104, 28, T["greet"])
    dot, wd = text(F.n8, "·", 72 + w1 + 12, 104, 28, T["greet_zh"])
    g2, w2 = text(F.sc6, GREETING[1], 72 + w1 + 12 + wd + 12, 103, 25, T["greet_zh"])
    body.append(g1 + dot + g2)
    hx = 72 + w1 + 12 + wd + 12 + w2 + 14
    body.append(f'<text x="{n(hx)}" y="104" font-size="30" class="wave" '
                f'font-family="Apple Color Emoji,Segoe UI Emoji,Noto Color Emoji,sans-serif">&#x1F44B;</text>')
    css.append(".wave{animation:wave 2.8s ease-in-out infinite;transform-box:fill-box;transform-origin:70% 80%}"
               "@keyframes wave{0%,60%,100%{transform:rotate(0)}10%,30%{transform:rotate(16deg)}20%{transform:rotate(-8deg)}40%{transform:rotate(-4deg)}50%{transform:rotate(10deg)}}")

    # name with a marker-pen highlight that swipes in
    nd, nw = F.n9.path(NAME, 66, 204, 108, tracking=1.5)
    mk_y, mk_h = 204 - 36, 32
    body.append(f'<g transform="skewX(-10)"><rect x="{n(66 + (mk_y + mk_h) * math.tan(math.radians(10)) - 6)}" y="{mk_y}" width="0" height="{mk_h}" rx="9" '
                f'fill="url(#marker)" opacity="{T["marker_op"]}"><animate attributeName="width" from="0" to="{n(nw + 22)}" dur=".9s" begin=".25s" '
                f'fill="freeze" calcMode="spline" keySplines=".2 .7 .3 1" keyTimes="0;1"/></rect></g>')
    body.append(f'<path d="{nd}" fill="{T["name"]}"/>')

    # typing line
    tdefs, tbody = typing_block(TYPING, 72, 262, 31, T["type"], F.mix7)
    defs += tdefs
    body.append(tbody)
    body.append("</g>")

    title = f"{NAME}: " + " / ".join(TYPING)
    return svg_doc(W, H, "\n".join(body), title, "".join(css), defs)


# ----------------------------------------------------------------------------
# HOBBY CARDS
# ----------------------------------------------------------------------------
def icon_basketball(cx, cy, c, css):
    css.append(".ball{animation:ball 1.3s infinite;transform-box:fill-box;transform-origin:50% 100%}"
               "@keyframes ball{0%,100%{transform:translateY(0) scale(1.07,.93);animation-timing-function:cubic-bezier(.25,.7,.45,1)}"
               "12%{transform:translateY(-3px) scale(1)}50%{transform:translateY(-22px) scale(1);animation-timing-function:cubic-bezier(.55,0,.75,.3)}}"
               ".bshadow{animation:bshadow 1.3s infinite;transform-box:fill-box;transform-origin:center}"
               "@keyframes bshadow{0%,100%{transform:scale(1);opacity:.22;animation-timing-function:cubic-bezier(.25,.7,.45,1)}50%{transform:scale(.55);opacity:.08;animation-timing-function:cubic-bezier(.55,0,.75,.3)}}")
    r = 27
    seams = (f"M{cx - r} {cy}H{cx + r}M{cx} {cy - r}V{cy + r}"
             f"M{n(cx - r * .72)} {n(cy - r * .7)}Q{n(cx - r * .25)} {cy} {n(cx - r * .72)} {n(cy + r * .7)}"
             f"M{n(cx + r * .72)} {n(cy - r * .7)}Q{n(cx + r * .25)} {cy} {n(cx + r * .72)} {n(cy + r * .7)}")
    return (f'<ellipse cx="{cx}" cy="{cy + r + 9}" rx="22" ry="4.5" fill="#1b2a44" class="bshadow"/>'
            f'<g class="ball"><circle cx="{cx}" cy="{cy}" r="{r}" fill="{c}"/>'
            f'<circle cx="{n(cx - 9)}" cy="{n(cy - 10)}" r="9" fill="#fff" opacity=".22"/>'
            f'<path d="{seams}" fill="none" stroke="#8a3b0c" stroke-width="2.2" stroke-linecap="round" opacity=".8"/></g>')


def icon_hiking(cx, cy, c, css):
    css.append(".trail{stroke-dasharray:4 5;animation:trail 1.6s linear infinite}@keyframes trail{to{stroke-dashoffset:-18}}"
               ".flag{animation:flag 1.4s ease-in-out infinite;transform-box:fill-box;transform-origin:0 50%}"
               "@keyframes flag{50%{transform:skewY(-9deg) scaleX(.85)}}")
    base = cy + 30
    back = f"M{cx + 2} {base}L{cx + 28} {cy - 4}L{cx + 54} {base}Z"
    front = f"M{cx - 46} {base}L{cx - 6} {cy - 24}L{cx + 36} {base}Z"
    snow = f"M{cx - 6} {cy - 24}L{cx - 17} {cy - 10}L{cx - 11} {cy - 12}L{cx - 6} {cy - 7}L{cx - 1} {cy - 12}L{cx + 5} {cy - 10}Z"
    trail = f"M{cx - 30} {base - 2}Q{cx - 4} {base - 10} {cx - 18} {cy + 10}T{cx - 10} {cy - 6}T{cx - 6} {cy - 22}"
    return (f'<path d="{back}" fill="{c}" opacity=".45" stroke-linejoin="round"/>'
            f'<path d="{front}" fill="{c}" stroke="{c}" stroke-width="3" stroke-linejoin="round"/>'
            f'<path d="{snow}" fill="#fff"/>'
            f'<path d="{trail}" fill="none" stroke="#fff" stroke-width="2.4" stroke-linecap="round" class="trail"/>'
            f'<path d="M{cx - 6} {cy - 24}V{cy - 44}" stroke="#46546b" stroke-width="2" stroke-linecap="round"/>'
            f'<path d="M{cx - 5} {cy - 44}L{cx + 12} {cy - 39}L{cx - 5} {cy - 34}Z" fill="#ff5a5f" class="flag"/>'
            f'<rect x="{cx - 52}" y="{base}" width="110" height="3" rx="1.5" fill="{c}" opacity=".5"/>')


def icon_music(cx, cy, c, css):
    out = []
    heights = [0.55, 0.85, 0.65, 1.0, 0.7, 0.9, 0.5]
    for i, h in enumerate(heights):
        x = cx - 45 + i * 13
        hh = 54 * h
        dur = 0.55 + (i * 0.37) % 0.6
        out.append(f'<rect x="{x}" y="{n(cy + 28 - hh)}" width="8" height="{n(hh)}" rx="4" fill="{c}" '
                   f'opacity="{0.55 + 0.45 * (i % 2)}" class="eq" style="animation-duration:{dur:.2f}s;animation-delay:-{i * .13:.2f}s"/>')
    note = (f'<g class="note"><ellipse cx="{cx + 44}" cy="{cy - 10}" rx="6.5" ry="5" transform="rotate(-20 {cx + 44} {cy - 10})" fill="{c}"/>'
            f'<path d="M{cx + 50} {cy - 12}V{cy - 36}Q{cx + 56} {cy - 30} {cx + 60} {cy - 26}" fill="none" stroke="{c}" stroke-width="2.6" stroke-linecap="round"/></g>')
    css.append(".eq{animation:eq .8s ease-in-out infinite alternate;transform-box:fill-box;transform-origin:50% 100%}"
               "@keyframes eq{from{transform:scaleY(1)}to{transform:scaleY(.3)}}"
               ".note{animation:note 2.6s ease-out infinite}@keyframes note{0%{transform:translateY(8px);opacity:0}25%{opacity:1}100%{transform:translateY(-14px);opacity:0}}")
    return "".join(out) + note


def icon_f1(cx, cy, c, css):
    ox, oy = cx - 54, cy - 18
    P = lambda x, y: f"{n(ox + x)} {n(oy + y)}"
    body = (f"M{P(6, 30)}L{P(12, 23)}L{P(30, 20)}L{P(40, 12)}L{P(50, 12)}L{P(53, 18)}L{P(64, 18)}"
            f"Q{P(70, 18)} {P(76, 22)}L{P(100, 27)}Q{P(105, 28)} {P(105, 31)}L{P(6, 32)}Z")
    speed = "".join(
        f'<rect x="{n(ox - 30 + dx)}" y="{n(oy + y)}" width="{wv}" height="2.6" rx="1.3" fill="{c}" opacity=".45" class="speed" style="animation-delay:-{d}s"/>'
        for dx, y, wv, d in [(0, 14, 22, 0), (8, 22, 16, .25), (2, 30, 20, .5)])
    css.append(".speed{animation:speed .75s linear infinite}@keyframes speed{from{transform:translateX(14px);opacity:.6}to{transform:translateX(-18px);opacity:0}}"
               ".car{animation:car .35s ease-in-out infinite alternate}@keyframes car{to{transform:translateY(-1.2px)}}"
               ".spoke{animation:spin .35s linear infinite;transform-box:fill-box;transform-origin:center}")
    wheel = lambda x, y, r: (f'<circle cx="{n(ox + x)}" cy="{n(oy + y)}" r="{r}" fill="#1f2937"/>'
                             f'<g class="spoke"><circle cx="{n(ox + x)}" cy="{n(oy + y)}" r="{r * .42:.1f}" fill="#cbd5e1"/>'
                             f'<rect x="{n(ox + x - r * .42)}" y="{n(oy + y - .8)}" width="{n(r * .84)}" height="1.6" fill="#1f2937"/></g>')
    return (speed + '<g class="car">'
            f'<rect x="{n(ox + 1)}" y="{n(oy + 4)}" width="18" height="5.5" rx="1.5" fill="{c}"/>'
            f'<rect x="{n(ox + 8)}" y="{n(oy + 9)}" width="3" height="14" fill="#374151"/>'
            f'<path d="{body}" fill="{c}"/>'
            f'<path d="M{P(18, 27)}L{P(92, 28.5)}" stroke="#fff" stroke-width="1.8" opacity=".75"/>'
            f'<circle cx="{n(ox + 57)}" cy="{n(oy + 15)}" r="4.2" fill="#fbbf24"/>'
            f'<path d="M{P(49, 14)}Q{P(58, 7)} {P(66, 17)}" fill="none" stroke="#1f2937" stroke-width="2.2" stroke-linecap="round"/>'
            f'<rect x="{n(ox + 92)}" y="{n(oy + 31)}" width="17" height="3.8" rx="1.5" fill="#b91c1c"/>'
            + wheel(22, 32, 10) + wheel(84, 33, 9) + '</g>')


def icon_anime(cx, cy, c, css):
    petal = "M0 0C-10 -8 -12 -22 -5 -30L0 -26L5 -30C12 -22 10 -8 0 0Z"
    flower = "".join(f'<path d="{petal}" transform="rotate({i * 72})" fill="#ffc2dd" stroke="{c}" stroke-width="1.4"/>' for i in range(5))
    stamens = "".join(f'<circle cx="{n(7 * math.cos(math.radians(i * 72 + 36)))}" cy="{n(7 * math.sin(math.radians(i * 72 + 36)))}" r="1.8" fill="{c}"/>' for i in range(5))
    falling = "".join(
        f'<g transform="translate({n(cx + fx)} {n(cy - 40)})"><path d="{petal}" transform="scale(.36)" fill="#ffb3d4" class="fall" '
        f'style="animation-delay:-{d}s;animation-duration:{du}s"/></g>'
        for fx, d, du in [(30, 0, 3.6), (-38, 1.3, 4.2), (48, 2.4, 3.9)])
    css.append(".bloom{animation:spin 14s linear infinite}"
               ".fall{animation:fall 3.8s linear infinite}@keyframes fall{0%{transform:translate(0,0) rotate(0);opacity:0}15%{opacity:1}"
               "100%{transform:translate(-26px,82px) rotate(220deg);opacity:0}}")
    return (falling + f'<g transform="translate({cx} {cy})"><g class="bloom">{flower}'
            f'<circle r="6" fill="#fff4b3"/>{stamens}</g></g>'
            + sparkle(cx + 36, cy - 26, 7, "#fbbf24", 0.3) + sparkle(cx - 38, cy + 18, 5, "#fbbf24", 1.4))


ICONS = {"basketball": icon_basketball, "hiking": icon_hiking, "music": icon_music, "f1": icon_f1, "anime": icon_anime}


def build_hobbies(theme: str):
    T = THEMES[theme]
    W, cw, ch, gap = 1000, 182, 212, 14
    x0 = (W - (5 * cw + 4 * gap)) / 2
    top = 14
    H = ch + 2 * top + 6
    css = [".twinkle{animation:twinkle 2.6s ease-in-out infinite}@keyframes twinkle{0%,100%{transform:scale(.5);opacity:.3}50%{transform:scale(1.1);opacity:1}}"
           "@keyframes spin{to{transform:rotate(360deg)}}"]
    defs = ('<filter id="shadow" x="-10%" y="-10%" width="120%" height="130%">'
            f'<feDropShadow dx="0" dy="4" stdDeviation="6" flood-color="#1b2b4b" flood-opacity="{T["card_shadow"]}"/></filter>')
    body = []
    for i, (key, en, zh, flavour) in enumerate(HOBBIES):
        x = x0 + i * (cw + gap)
        c = HOBBY_COLORS[key]
        mid = x + cw / 2
        defs += (f'<clipPath id="c{i}"><rect x="{n(x)}" y="{top}" width="{cw}" height="{ch}" rx="22"/></clipPath>'
                 f'<radialGradient id="b{i}"><stop offset="0" stop-color="{c}" stop-opacity="{T["blob_op"] * 1.7:.2f}"/>'
                 f'<stop offset=".7" stop-color="{c}" stop-opacity="{T["blob_op"] * .8:.2f}"/><stop offset="1" stop-color="{c}" stop-opacity="0"/></radialGradient>')
        body.append(f'<rect x="{n(x)}" y="{top}" width="{cw}" height="{ch}" rx="22" fill="{T["card"]}" stroke="{T["card_stroke"]}" stroke-width="1.5" filter="url(#shadow)"/>')
        body.append(f'<g clip-path="url(#c{i})"><circle cx="{n(mid)}" cy="{top + 70}" r="62" fill="url(#b{i})"/>'
                    f'{ICONS[key](round(mid), top + 72, c, css)}</g>')
        t1, _ = text(F.n8, en, mid, top + 150, 22, T["title"], anchor="middle")
        t2, _ = text(F.sc7, zh, mid, top + 175, 16.5, c, anchor="middle")
        fs = 14.0
        while F.mix_small.width(flavour, fs) > cw - 18:
            fs -= 0.25
        t3, _ = text(F.mix_small, flavour, mid, top + 199, fs, T["muted"], anchor="middle")
        body.append(t1 + t2 + t3)
    title = "Beyond research: " + ", ".join(f"{en} {zh}" for _, en, zh, _ in HOBBIES)
    return svg_doc(W, H, "\n".join(body), title, "".join(dict.fromkeys(css)), defs)


# ----------------------------------------------------------------------------
# FEATURED PROJECT CARDS
# ----------------------------------------------------------------------------
def wrap(font, s, size, max_w):
    lines, cur = [], ""
    for word in s.split(" "):
        trial = f"{cur} {word}".strip()
        if cur and font.width(trial, size) > max_w:
            lines.append(cur)
            cur = word
        else:
            cur = trial
    return lines + [cur]


def icon_molecule(cx, cy, c, css):
    """A small aromatic ring with two substituents, gently swaying."""
    pts = [(cx + 22 * math.cos(math.radians(a)), cy + 22 * math.sin(math.radians(a))) for a in range(-90, 270, 60)]
    ring = "M" + "L".join(f"{n(x)} {n(y)}" for x, y in pts) + "Z"
    (x0, y0), (x3, y3) = pts[0], pts[2]
    sub = (f"M{n(x0)} {n(y0)}L{n(x0)} {n(y0 - 16)}"
           f"M{n(x3)} {n(y3)}L{n(x3 + 14)} {n(y3 + 8)}")
    css.append(".mol{animation:mol 6s ease-in-out infinite;transform-box:view-box}"
               "@keyframes mol{0%,100%{transform:rotate(-7deg)}50%{transform:rotate(7deg)}}"
               ".atom{animation:atom 2.4s ease-in-out infinite;transform-box:fill-box;transform-origin:center}"
               "@keyframes atom{50%{transform:scale(1.25)}}")
    return (f'<g class="mol" style="transform-origin:{cx}px {cy}px">'
            f'<path d="{ring}" fill="none" stroke="{c}" stroke-width="3.4" stroke-linejoin="round"/>'
            f'<circle cx="{cx}" cy="{cy}" r="11" fill="none" stroke="{c}" stroke-width="2.2" opacity=".55"/>'
            f'<path d="{sub}" stroke="{c}" stroke-width="3.4" stroke-linecap="round"/>'
            f'<circle cx="{n(x0)}" cy="{n(y0 - 20)}" r="6" fill="#ff6b8b" class="atom"/>'
            f'<circle cx="{n(x3 + 18)}" cy="{n(y3 + 10)}" r="6" fill="#4aa8ff" class="atom" style="animation-delay:-1.2s"/></g>')


def icon_paper(cx, cy, c, css):
    """A paper with a magnifying glass sweeping across it."""
    x, y, w, h, f = cx - 22, cy - 26, 38, 50, 11
    sheet = f"M{x} {y}H{x + w - f}L{x + w} {y + f}V{y + h}H{x}Z"
    lines = "".join(f'<rect x="{x + 7}" y="{y + 15 + i * 8}" width="{w - 14 - (i % 2) * 8}" height="3" rx="1.5" fill="{c}" opacity=".5"/>' for i in range(4))
    css.append(".lens{animation:lens 3.2s ease-in-out infinite}@keyframes lens{0%,100%{transform:translate(-6px,-4px)}50%{transform:translate(6px,4px)}}")
    return (f'<path d="{sheet}" fill="#fff" stroke="{c}" stroke-width="2.6" stroke-linejoin="round"/>'
            f'<path d="M{x + w - f} {y}V{y + f}H{x + w}" fill="none" stroke="{c}" stroke-width="2.2" stroke-linejoin="round"/>{lines}'
            f'<g class="lens"><circle cx="{cx + 12}" cy="{cy + 8}" r="12" fill="{c}" fill-opacity=".14" stroke="{c}" stroke-width="3.2"/>'
            f'<path d="M{cx + 20.5} {cy + 16.5}L{cx + 29} {cy + 25}" stroke="{c}" stroke-width="4.2" stroke-linecap="round"/>'
            f'<path d="M{cx + 6.5} {cy + 8}L{cx + 10.5} {cy + 12}L{cx + 17.5} {cy + 4}" fill="none" stroke="{c}" stroke-width="2.6" stroke-linecap="round" stroke-linejoin="round"/></g>')


def build_project(theme: str, p: dict):
    T = THEMES[theme]
    c = p["color"][0 if theme == "light" else 1]
    W, H = 520, 244
    css = []
    defs = ('<filter id="shadow" x="-10%" y="-10%" width="120%" height="130%">'
            f'<feDropShadow dx="0" dy="4" stdDeviation="6" flood-color="#1b2b4b" flood-opacity="{T["card_shadow"]}"/></filter>'
            f'<radialGradient id="glow"><stop offset="0" stop-color="{c}" stop-opacity="{T["blob_op"] * 1.6:.2f}"/>'
            f'<stop offset="1" stop-color="{c}" stop-opacity="0"/></radialGradient>')
    body = [f'<rect x="8" y="8" width="{W - 16}" height="{H - 18}" rx="22" fill="{T["card"]}" stroke="{T["card_stroke"]}" stroke-width="1.5" filter="url(#shadow)"/>',
            f'<circle cx="72" cy="70" r="50" fill="url(#glow)"/>']
    icon = icon_molecule if p["icon"] == "molecule" else icon_paper
    body.append(icon(72, 70, c, css))
    k, _ = text(F.mix_small, p["kicker"], 136, 54, 13, c, 1.2)
    t, _ = text(F.n9, p["name"], 134, 92, 33, T["title"])
    body.append(k + t)
    # "opens in GitHub" arrow
    body.append(f'<path d="M472 50L486 36M476 36H486V46" fill="none" stroke="{T["muted"]}" stroke-width="2.4" stroke-linecap="round" stroke-linejoin="round"/>')
    y = 136
    for line in wrap(F.n7, p["en"], 16.5, W - 64)[:2]:
        d, _ = text(F.n7, line, 32, y, 16.5, T["title"])
        body.append(d)
        y += 23
    zd, _ = text(F.sc5, p["zh"], 32, y + 2, 15, T["muted"])
    body.append(zd)
    tx, ty = 32, H - 50
    for tag in p["tags"]:
        tw = F.n8.width(tag, 13)
        body.append(f'<rect x="{n(tx)}" y="{ty}" width="{n(tw + 22)}" height="25" rx="12.5" fill="{c}" fill-opacity="{0.12 if theme == "light" else 0.2}"/>')
        tt, _ = text(F.n8, tag, tx + 11, ty + 17, 13, c)
        body.append(tt)
        tx += tw + 30
    title = f'{p["name"]}: {p["en"]} · {p["zh"]}'
    return svg_doc(W, H, "\n".join(body), title, "".join(dict.fromkeys(css)), defs)


# ----------------------------------------------------------------------------
# FOOTER
# ----------------------------------------------------------------------------
def build_footer(theme: str):
    T = THEMES[theme]
    W, H = 1200, 190
    css = []
    body = []
    t1w = F.n8.width(FOOTER[0], 27)
    sun_x = W / 2 - t1w / 2 - 12
    tx = W / 2 + 22
    t1, _ = text(F.n8, FOOTER[0], tx, 62, 27, T["foot_title"], anchor="middle")
    t2, _ = text(F.sc6, FOOTER[1], W / 2, 96, 18, T["foot_sub"], anchor="middle")
    rays = "".join(f"M{n(sun_x + 17 * math.cos(math.radians(a)))} {n(52 + 17 * math.sin(math.radians(a)))}"
                   f"L{n(sun_x + 23 * math.cos(math.radians(a)))} {n(52 + 23 * math.sin(math.radians(a)))}" for a in range(0, 360, 45))
    body.append(f'<g class="spin" style="transform-origin:{n(sun_x)}px 52px"><path d="{rays}" stroke="#ffc83d" stroke-width="3.6" stroke-linecap="round"/></g>'
                f'<circle cx="{n(sun_x)}" cy="52" r="11" fill="#ffc83d"/>')
    css.append(".spin{animation:spin 12s linear infinite}@keyframes spin{to{transform:rotate(360deg)}}")
    body.append(t1 + t2)
    body.append(waves(W, H, T["foot_waves"], [138, 152, 166], css, "f"))
    return svg_doc(W, H, "\n".join(body), f"{FOOTER[0]} {FOOTER[1]}", "".join(css))


# ----------------------------------------------------------------------------
def main():
    global F
    F = Fonts()
    os.makedirs(ASSETS, exist_ok=True)
    builders = [("header", build_header), ("hobbies", build_hobbies), ("footer", build_footer)]
    builders += [(f"project-{p['key']}", lambda theme, p=p: build_project(theme, p)) for p in PROJECTS]
    for base, fn in builders:
        for theme in THEMES:
            svg = fn(theme)
            name = f"{base}-{theme}.svg"
            with open(os.path.join(ASSETS, name), "w", encoding="utf-8") as fh:
                fh.write(svg)
            print(f"{name}: {len(svg) / 1024:.1f} KB")


if __name__ == "__main__":
    main()
