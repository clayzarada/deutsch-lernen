"""Builds static/js/alexmap.js, the map for the Verbs journey, from Natural Earth country outlines.

    python tools/make_alexmap.py path/to/countries-50m.json

The data is world-atlas@2 (Natural Earth, public domain): https://cdn.jsdelivr.net/npm/world-atlas@2.0.2/countries-50m.json
Modern countries are merged into the regions of Alexander's march; borders inside a region disappear, so the map shows
only coastlines and region edges. An orthographic projection gives the gentle curve of the globe.
"""
import json
import math
import sys
from pathlib import Path

REGIONS = {  # region id -> ISO 3166 numeric codes
    "macedon": ["807"], "hellas": ["300"], "anatolia": ["792"], "phoenicia": ["422", "376", "400", "275"],
    "egypt": ["818"], "syria": ["760"], "persia": ["364"], "bactria": ["004", "860", "762", "795"],
    "indus": ["586"], "babylon": ["368", "414"],
}
LON0, LAT0 = 47.0, 32.0          # centre of the projection
FRAME = (12.0, 76.0, 18.0, 47.0)  # lon/lat box the map is fitted to
WIDTH = 1000
TOL = .55                          # simplification tolerance in output pixels


def project(lon, lat):
    l, p, l0, p0 = map(math.radians, (lon, lat, LON0, LAT0))
    x = math.cos(p) * math.sin(l - l0)
    y = math.cos(p0) * math.sin(p) - math.sin(p0) * math.cos(p) * math.cos(l - l0)
    return x, -y


def decode(topo):
    sx, sy = topo["transform"]["scale"]
    tx, ty = topo["transform"]["translate"]
    arcs = []
    for arc in topo["arcs"]:
        x = y = 0
        pts = []
        for dx, dy in arc:
            x += dx
            y += dy
            pts.append((x * sx + tx, y * sy + ty))
        arcs.append(pts)
    return arcs


def dp(pts, tol):
    """Douglas-Peucker simplification (keeps the end points, so shared arcs still meet)."""
    if len(pts) < 3:
        return pts
    keep = [False] * len(pts)
    keep[0] = keep[-1] = True
    stack = [(0, len(pts) - 1)]
    while stack:
        a, b = stack.pop()
        (x1, y1), (x2, y2) = pts[a], pts[b]
        dx, dy = x2 - x1, y2 - y1
        n = math.hypot(dx, dy) or 1e-9
        best, bi = 0, None
        for i in range(a + 1, b):
            d = abs(dy * pts[i][0] - dx * pts[i][1] + x2 * y1 - y2 * x1) / n
            if d > best:
                best, bi = d, i
        if bi is not None and best > tol:
            keep[bi] = True
            stack += [(a, bi), (bi, b)]
    return [p for p, k in zip(pts, keep) if k]


def main(src, out):
    topo = json.loads(Path(src).read_text(encoding="utf-8"))
    arcs = decode(topo)
    geoms = topo["objects"]["countries"]["geometries"]
    group_of = {c: r for r, cs in REGIONS.items() for c in cs}

    # which countries to draw at all: anything near the frame
    def near(g):
        lons, lats = [], []
        for ring in _rings(g):
            for i in ring:
                for lon, lat in arcs[~i if i < 0 else i][::20]:
                    lons.append(lon)
                    lats.append(lat)
        return lons and min(lons) < FRAME[1] + 25 and max(lons) > FRAME[0] - 25 and min(lats) < FRAME[3] + 18 and max(lats) > FRAME[2] - 18

    drawn = [g for g in geoms if g.get("id") in group_of or near(g)]

    # fit the frame to WIDTH
    corners = [project(lon, lat) for lon in (FRAME[0], FRAME[1], (FRAME[0] + FRAME[1]) / 2) for lat in (FRAME[2], FRAME[3])]
    minx, maxx = min(c[0] for c in corners), max(c[0] for c in corners)
    miny, maxy = min(c[1] for c in corners), max(c[1] for c in corners)
    k = WIDTH / (maxx - minx)
    height = round((maxy - miny) * k)

    def px(lon, lat):
        x, y = project(lon, lat)
        return ((x - minx) * k, (y - miny) * k)

    proj = [dp([px(*p) for p in arc], TOL) for arc in arcs]

    # who uses each arc
    users = {}
    for g in drawn:
        grp = group_of.get(g.get("id"), "land")
        for ring in _rings(g):
            for i in ring:
                users.setdefault(i if i >= 0 else ~i, []).append(grp)

    def ring_path(ring):
        pts = []
        for i in ring:
            a = proj[i] if i >= 0 else proj[~i][::-1]
            pts.extend(a if not pts else a[1:])
        return "M" + "L".join(f"{x:.1f} {y:.1f}" for x, y in pts) + "Z" if len(pts) > 2 else ""

    def arc_path(i):
        return "M" + "L".join(f"{x:.1f} {y:.1f}" for x, y in proj[i])

    fills = {}
    for g in drawn:
        grp = group_of.get(g.get("id"), "land")
        fills.setdefault(grp, []).extend(p for p in (ring_path(r) for r in _rings(g)) if p)

    def edges(grp):
        out = []
        for i, us in users.items():
            if grp in us and (len(us) == 1 or any(u != grp for u in us)):
                out.append(arc_path(i))
        return "".join(out)

    coast = "".join(arc_path(i) for i, us in users.items() if us == ["land"])
    regions = {}
    for r in REGIONS:
        cx, cy, area, box = _centroid(r, drawn, group_of, proj, px)
        regions[r] = {"d": "".join(fills.get(r, [])), "edge": edges(r), "cx": round(cx, 1), "cy": round(cy, 1),
                      "box": [round(v, 1) for v in box]}

    grat = []
    for lon in range(0, 100, 10):
        grat.append("M" + "L".join("%.1f %.1f" % px(lon, lat) for lat in range(0, 66, 3)))
    for lat in range(10, 61, 10):
        grat.append("M" + "L".join("%.1f %.1f" % px(lon, lat) for lon in range(-10, 101, 3)))

    data = {"w": WIDTH, "h": height, "land": "".join(fills.get("land", [])), "coast": coast, "graticule": "".join(grat),
            "regions": regions}
    js = ("// Generated by tools/make_alexmap.py from Natural Earth outlines (public domain). Do not edit by hand.\n"
          "export const ALEXMAP = " + json.dumps(data, separators=(",", ":")) + ";\n")
    Path(out).write_text(js, encoding="utf-8")
    print(f"wrote {out}: {len(js) / 1024:.0f} KB, {WIDTH}x{height}")


def _rings(g):
    if g["type"] == "Polygon":
        return g["arcs"]
    if g["type"] == "MultiPolygon":
        return [r for poly in g["arcs"] for r in poly]
    return []


def _centroid(region, drawn, group_of, proj, px):
    """Area-weighted centre of the region's largest pieces (where its label and the kitty go)."""
    best = []
    for g in drawn:
        if group_of.get(g.get("id")) != region:
            continue
        polys = [g["arcs"]] if g["type"] == "Polygon" else g["arcs"]
        for poly in polys:
            ring = poly[0]
            pts = []
            for i in ring:
                a = proj[i] if i >= 0 else proj[~i][::-1]
                pts.extend(a)
            a = cx = cy = 0
            for (x1, y1), (x2, y2) in zip(pts, pts[1:] + pts[:1]):
                c = x1 * y2 - x2 * y1
                a += c
                cx += (x1 + x2) * c
                cy += (y1 + y2) * c
            if abs(a) > 1e-6:
                best.append((abs(a) / 2, cx / (3 * a), cy / (3 * a), pts))
    best.sort(reverse=True)
    tot = sum(b[0] for b in best[:4])
    cx = sum(b[0] * b[1] for b in best[:4]) / tot
    cy = sum(b[0] * b[2] for b in best[:4]) / tot
    allpts = [p for b in best for p in b[3]]
    box = (min(p[0] for p in allpts), min(p[1] for p in allpts), max(p[0] for p in allpts), max(p[1] for p in allpts))
    return cx, cy, tot, box


if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2] if len(sys.argv) > 2 else "static/js/alexmap.js")
