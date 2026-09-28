"""Convert text to SVG path outlines, so the SVGs render identically everywhere.

GitHub shows README images through <img>, which cannot load web fonts, so every
piece of text in the assets is baked into vector outlines with this helper.
Shaping (kerning, ligatures) is done with HarfBuzz; outlines come from fontTools.
"""
from __future__ import annotations

import uharfbuzz as hb
from fontTools.pens.svgPathPen import SVGPathPen
from fontTools.pens.transformPen import TransformPen
from fontTools.ttLib import TTFont


def _num(v: float) -> str:
    s = f"{v:.1f}"
    if s.endswith(".0"):
        s = s[:-2]
    return "0" if s == "-0" else s


class Font:
    """One font file at one weight (variable fonts are instanced via `wght`)."""

    def __init__(self, path: str, wght: float | None = None, features: dict | None = None):
        self.file = path
        self.tt = TTFont(path, lazy=False)
        self.upem = self.tt["head"].unitsPerEm
        self.hbfont = hb.Font(hb.Face(hb.Blob.from_file_path(path)))
        self.location = None
        if wght is not None and "fvar" in self.tt:
            self.location = {"wght": wght}
            self.hbfont.set_variations(self.location)
        self.glyphset = self.tt.getGlyphSet(location=self.location)
        self.order = self.tt.getGlyphOrder()
        self.features = {"kern": True, "liga": True, **(features or {})}
        self.cmap = self.tt.getBestCmap()

    # -- layout -------------------------------------------------------------
    def layout(self, text: str, size: float, tracking: float = 0.0):
        """Return [(glyph_name, x, y, advance)], total width. Units: px."""
        missing = sorted({c for c in text if ord(c) not in self.cmap and not c.isspace()})
        if missing:
            print(f"WARNING: {self.file.rsplit('/', 1)[-1]} has no glyph for {''.join(missing)!r}")
        buf = hb.Buffer()
        buf.add_str(text)
        buf.guess_segment_properties()
        hb.shape(self.hbfont, buf, self.features)
        s = size / self.upem
        out, x = [], 0.0
        for info, pos in zip(buf.glyph_infos, buf.glyph_positions):
            adv = pos.x_advance * s
            out.append((self.order[info.codepoint], x + pos.x_offset * s, -pos.y_offset * s, adv))
            x += adv + tracking
        width = x - tracking if out else 0.0
        return out, width

    def width(self, text: str, size: float, tracking: float = 0.0) -> float:
        return self.layout(text, size, tracking)[1]

    def path(self, text: str, x: float, y: float, size: float, tracking: float = 0.0,
             anchor: str = "start") -> tuple[str, float]:
        """SVG path data for `text` with its baseline at y. Returns (d, width)."""
        glyphs, width = self.layout(text, size, tracking)
        if anchor == "middle":
            x -= width / 2
        elif anchor == "end":
            x -= width
        s = size / self.upem
        pen = SVGPathPen(self.glyphset, ntos=_num)
        for name, gx, gy, _ in glyphs:
            self.glyphset[name].draw(TransformPen(pen, (s, 0, 0, -s, x + gx, y + gy)))
        return pen.getCommands(), width

    def boundaries(self, text: str, x: float, size: float, tracking: float = 0.0) -> list[float]:
        """Right edge (absolute x) after each glyph: used to time typing animations."""
        glyphs, _ = self.layout(text, size, tracking)
        return [x + gx + adv for _, gx, _, adv in glyphs]


def is_cjk(ch: str) -> bool:
    o = ord(ch)
    return (0x2E80 <= o <= 0x9FFF or 0x3000 <= o <= 0x30FF or 0xF900 <= o <= 0xFAFF
            or 0xFF00 <= o <= 0xFFEF)


class Mixed:
    """Bilingual text: Latin runs in one font, CJK runs in another, one baseline."""

    def __init__(self, latin: Font, cjk: Font, cjk_scale: float = 1.0, gap: float = 0.0):
        self.latin, self.cjk, self.cjk_scale, self.gap = latin, cjk, cjk_scale, gap

    def _runs(self, text: str):
        runs: list[tuple[bool, str]] = []
        for ch in text:
            c = is_cjk(ch) or (ch in "，。：；、！？（）·" and runs and runs[-1][0])
            if runs and runs[-1][0] == c:
                runs[-1] = (c, runs[-1][1] + ch)
            else:
                runs.append((c, ch))
        return runs

    def width(self, text: str, size: float, tracking: float = 0.0) -> float:
        w = 0.0
        for c, run in self._runs(text):
            f = self.cjk if c else self.latin
            w += f.width(run, size * (self.cjk_scale if c else 1), tracking) + tracking
        return max(0.0, w - tracking)

    def path(self, text: str, x: float, y: float, size: float, tracking: float = 0.0,
             anchor: str = "start") -> tuple[str, float]:
        total = self.width(text, size, tracking)
        if anchor == "middle":
            x -= total / 2
        elif anchor == "end":
            x -= total
        parts = []
        for c, run in self._runs(text):
            f = self.cjk if c else self.latin
            d, w = f.path(run, x, y, size * (self.cjk_scale if c else 1), tracking)
            parts.append(d)
            x += w + tracking
        return " ".join(parts), total

    def boundaries(self, text: str, x: float, size: float, tracking: float = 0.0) -> list[float]:
        out = []
        for c, run in self._runs(text):
            f = self.cjk if c else self.latin
            sz = size * (self.cjk_scale if c else 1)
            b = f.boundaries(run, x, sz, tracking)
            out += b
            x = (b[-1] if b else x) + tracking
        return out
