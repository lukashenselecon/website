# -*- coding: utf-8 -*-
"""
Route map for the Cohort 7 cycling trip, 27 September 2026.

The basemap is Amap (AutoNavi) raster tiles, loaded by the reader's browser, so
the page works inside mainland China without a VPN. The route itself was routed
over OpenStreetMap with OSRM (bike profile) and is stored here in WGS-84; Amap
tiles use GCJ-02, so every point is shifted before it is projected.
"""
import io, json, math, os

Z = 16
BOUNDS = dict(n=39.9492, w=116.3770, s=39.9222, e=116.4122)
TILE_HOSTS = ["webrd01", "webrd02", "webrd03", "webrd04"]

_a, _ee = 6378245.0, 0.00669342162296594323


def _tl(x, y):
    r = -100 + 2*x + 3*y + 0.2*y*y + 0.1*x*y + 0.2*math.sqrt(abs(x))
    r += (20*math.sin(6*x*math.pi) + 20*math.sin(2*x*math.pi)) * 2/3
    r += (20*math.sin(y*math.pi) + 40*math.sin(y/3*math.pi)) * 2/3
    r += (160*math.sin(y/12*math.pi) + 320*math.sin(y*math.pi/30)) * 2/3
    return r


def _tg(x, y):
    r = 300 + x + 2*y + 0.1*x*x + 0.1*x*y + 0.1*math.sqrt(abs(x))
    r += (20*math.sin(6*x*math.pi) + 20*math.sin(2*x*math.pi)) * 2/3
    r += (20*math.sin(x*math.pi) + 40*math.sin(x/3*math.pi)) * 2/3
    r += (150*math.sin(x/12*math.pi) + 300*math.sin(x/30*math.pi)) * 2/3
    return r


def wgs2gcj(lat, lon):
    dlat, dlon = _tl(lon-105.0, lat-35.0), _tg(lon-105.0, lat-35.0)
    rad = math.radians(lat)
    m = 1 - _ee*math.sin(rad)**2
    sm = math.sqrt(m)
    dlat = (dlat*180.0) / ((_a*(1-_ee))/(m*sm)*math.pi)
    dlon = (dlon*180.0) / (_a/sm*math.cos(rad)*math.pi)
    return lat+dlat, lon+dlon


def _tile(lat, lon, z=Z):
    n = 2**z
    x = (lon+180.0)/360.0*n
    y = (1 - math.log(math.tan(math.radians(lat)) + 1/math.cos(math.radians(lat)))/math.pi)/2*n
    return x, y


_c = [_tile(*wgs2gcj(BOUNDS["n"], BOUNDS["w"])), _tile(*wgs2gcj(BOUNDS["s"], BOUNDS["e"]))]
X0, X1 = math.floor(_c[0][0]), math.ceil(_c[1][0])
Y0, Y1 = math.floor(_c[0][1]), math.ceil(_c[1][1])
W, H = (X1-X0)*256, (Y1-Y0)*256


def px(lat, lon):
    x, y = _tile(*wgs2gcj(lat, lon))
    return (x-X0)*256, (y-Y0)*256


ROUTE = json.load(io.open(os.path.join(os.path.dirname(os.path.abspath(__file__)),
                                       "cycling-route.json"), encoding="utf-8"))

# (number, lat, lon, label dx, dy, text anchor)
STOPS = [
    (1, 39.94697, 116.41024, -18, 40, "end"),
    (2, 39.94710, 116.40639,   0, -40, "middle"),
    (3, 39.94514, 116.40831, -18, 34, "end"),
    (4, 39.93935, 116.38974, -18, -6, "end"),
    (5, 39.94089, 116.38095,   0, -40, "middle"),
    (6, 39.93225, 116.39760,  18, -6, "start"),
    (7, 39.92334, 116.39913,  18, -6, "start"),
    (8, 39.92447, 116.39324, -18, -6, "end"),
]
LABELS = {
    1: ("Lama Temple", "雍和宫"), 2: ("Wudaoying Hutong", "五道营胡同"),
    3: ("Confucius Temple", "孔庙 / 国子监"), 4: ("Drum & Bell Towers", "鼓楼 / 钟楼"),
    5: ("Houhai", "后海"), 6: ("Voyage Coffee", "Voyage Coffee"),
    7: ("Red Building", "北大红楼"), 8: ("Jingshan Park", "景山公园"),
}


def map_html(lang="en"):
    zh = lang == "zh"
    tiles = []
    for j, y in enumerate(range(Y0, Y1)):
        for i, x in enumerate(range(X0, X1)):
            host = TILE_HOSTS[(i+j) % len(TILE_HOSTS)]
            url = ("https://%s.is.autonavi.com/appmaptile?lang=zh_cn&size=1&scale=1&style=7"
                   "&x=%d&y=%d&z=%d" % (host, x, y, Z))
            tiles.append('<img src="%s" alt="" width="256" height="256" loading="lazy" decoding="async">' % url)

    d = " ".join(("M" if k == 0 else "L") + "%.0f %.0f" % px(p[1], p[0])
                 for k, p in enumerate(ROUTE))
    marks = []
    for n, lat, lon, dx, dy, anchor in STOPS:
        x, y = px(lat, lon)
        en, zhs = LABELS[n]
        text = zhs if zh else en
        tx = x + dx + (6 if anchor == "start" else -6 if anchor == "end" else 0)
        marks.append(
            '<g><circle cx="%.0f" cy="%.0f" r="26" fill="#fff" stroke="#101112" stroke-width="6"/>'
            '<text x="%.0f" y="%.0f" text-anchor="middle" font-size="30" font-weight="700" '
            'fill="#101112">%d</text>'
            '<text class="lb" x="%.0f" y="%.0f" text-anchor="%s" font-size="32" font-weight="700" '
            'stroke="#fff" stroke-width="7" paint-order="stroke" fill="#101112">%s</text></g>'
            % (x, y, x, y+11, n, tx, y+dy, anchor, text))

    return ('<div class="mapwrap"><div class="mapgrid" style="--cols:%d;--w:%d;--h:%d">%s'
            '<svg viewBox="0 0 %d %d" preserveAspectRatio="xMidYMid meet" aria-hidden="true">'
            '<path d="%s" fill="none" stroke="#fff" stroke-width="22" stroke-linejoin="round" stroke-linecap="round"/>'
            '<path d="%s" fill="none" stroke="#C1272D" stroke-width="12" stroke-linejoin="round" stroke-linecap="round"/>'
            '%s</svg></div></div>'
            % (X1-X0, W, H, "".join(tiles), W, H, d, d, "".join(marks)))
