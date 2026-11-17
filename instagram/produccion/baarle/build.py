#!/usr/bin/env python3
"""Genera el reel "Baarle" (EarthUnfold · Border Oddities EP.1) a partir de los tiempos reales de la voz.

  python3 -I build.py      -> index.html, compositions/*.html, cues.json, audio/diseno.json

Todo tiempo de pantalla y de sonido sale de audio/words.json (Scribe) mapeado por T(): nada escrito a ojo.
"""
import json
import os
import random

HERE = os.path.dirname(os.path.abspath(__file__))
W, H = 1080, 1920
SPEED = 1.06          # la voz se acelera 1.06x (atempo)
LEAD = 0.20           # la voz empieza a 0.20 s
GOLD, ORANGE, CYAN = "#FFC83D", "#FF7A1A", "#43D9F5"
INK, NAVY = "#F4F1EA", "#0B1020"

words = [w for w in json.load(open(os.path.join(HERE, "audio/words.json")))["words"] if w["type"] == "word"]


def T(t):
    return round(LEAD + t / SPEED, 3)


def wt(text, n=1, key="start"):
    """Tiempo (en el video) de la n-ésima aparición de una palabra (comparando sin puntuación)."""
    norm = lambda s: s.lower().strip(".,?!:…").replace("...", "")
    c = 0
    for w in words:
        if norm(w["text"]) == norm(text):
            c += 1
            if c == n:
                return T(w[key])
    raise KeyError(f"{text} #{n}")


END_VO = T(words[-1]["end"])
DUR = round(END_VO + 0.9, 2)
FPS = 30


def fr(t):  # redondea al fotograma
    return round(round(t * FPS) / FPS, 4)


# ---------- escenas (inicio en el video) ----------
S = {
    "hook":   0.0,
    "map":    fr(wt("Baarle") - 0.05),
    "nest":   fr(wt("Countries") - 0.12),
    "street": fr(wt("The", 3) - 0.05),
    "house":  fr(wt("So") - 0.05),
    "cut":    fr(wt("On", 2) - 0.05),
    "brk":    fr(wt("that's") - 0.15),
    "end":    fr(wt("Next:") - 0.10),
}
order = list(S)
SLOT = {k: (S[k], round((S[order[i + 1]] if i + 1 < len(order) else DUR) - S[k], 4)) for i, k in enumerate(order)}


def L(scene, t):  # tiempo local de escena
    return round(t - S[scene], 3)


rng = random.Random(42)

# ---------- blobs (enclaves) deterministas ----------
blobs = []
while len(blobs) < 22:
    r = rng.uniform(20, 52)
    x, y = rng.uniform(90 + r, 810 - r), rng.uniform(270 + r, 820 - r)
    if all((x - bx) ** 2 + (y - by) ** 2 > (r + br + 14) ** 2 for bx, by, br in blobs):
        blobs.append((x, y, r))


def blob_path(x, y, r, seed):
    g = random.Random(seed)
    pts = []
    n = 9
    for i in range(n):
        a = 6.2832 * i / n
        rr = r * g.uniform(0.72, 1.18)
        pts.append((x + rr * __import__("math").cos(a), y + rr * __import__("math").sin(a)))
    d = f"M{pts[0][0]:.1f},{pts[0][1]:.1f} "
    for i in range(1, n + 1):
        p0, p1 = pts[i - 1], pts[i % n]
        mx, my = (p0[0] + p1[0]) / 2, (p0[1] + p1[1]) / 2
        d += f"Q{p0[0]:.1f},{p0[1]:.1f} {mx:.1f},{my:.1f} "
    return d + "Z"


big7 = sorted(range(22), key=lambda i: -blobs[i][2])[:7]
zx = sum(blobs[i][0] for i in big7) / 7
zy = sum(blobs[i][1] for i in big7) / 7

# ---------- captions ----------
KEY = {"belgium", "netherlands", "twenty-two", "seven", "dutch", "front", "door", "border", "three", "belgian", "strangest"}
groups, cur = [], []
for i, w in enumerate(words):
    if T(w["start"]) >= S["end"]:
        break
    cur.append(w)
    nxt = words[i + 1] if i + 1 < len(words) else None
    gap = (nxt["start"] - w["end"]) if nxt else 9
    punct = w["text"][-1] in ".,?!:" or w["text"].endswith("...")
    if len(cur) == 3 or punct or gap >= 0.3 or (nxt and T(nxt["start"]) >= S["end"]):
        groups.append(cur)
        cur = []
if cur:
    groups.append(cur)
cap = []
for gi, g in enumerate(groups):
    st = T(g[0]["start"]) - 0.04
    en = T(groups[gi + 1][0]["start"]) - 0.02 if gi + 1 < len(groups) else T(g[-1]["end"]) + 0.25
    en = min(en, T(g[-1]["end"]) + 0.6, S["end"] - 0.02)
    html_words = []
    for w in g:
        t = w["text"].upper().strip(",:")
        clean = w["text"].lower().strip(".,?!:")
        col = GOLD if clean in KEY else INK
        html_words.append(f'<span style="color:{col}">{t}</span>')
    cap.append({"id": f"cg{gi}", "start": round(st, 3), "end": round(en, 3), "html": " ".join(html_words),
                "text": " ".join(w["text"].upper() for w in g)})

# ---------- helpers HTML ----------


def scene_file(cid, css, body, js):
    return f"""<template>
  <style>
    #root {{ position: absolute; inset: 0; overflow: hidden; font-family: 'Inter Display', 'Inter', sans-serif; }}
    #root * {{ box-sizing: border-box; }}
    .mono {{ font-family: 'JetBrains Mono', monospace; letter-spacing: 0.12em; }}
    .tag {{ position:absolute; padding: 14px 26px; border-radius: 14px; font-family:'JetBrains Mono',monospace;
           font-weight: 800; font-size: 40px; letter-spacing: .12em; background: rgba(8,10,18,.82); }}
    .stamp {{ position:absolute; padding: 18px 34px; border: 7px solid {GOLD}; border-radius: 16px; color: {GOLD};
             font-weight: 900; font-size: 64px; letter-spacing: .02em; background: rgba(8,10,18,.55); white-space: nowrap; }}
{css}
  </style>
  <div id="root" data-composition-id="{cid}" data-width="{W}" data-height="{H}">
{body}
  </div>
  <script>
    (function () {{
      const tl = gsap.timeline({{ paused: true }});
{js}
      window.__timelines["{cid}"] = tl;
    }})();
  </script>
</template>
"""


def door(id_, w, h, extra=""):
    return f"""<div id="{id_}" class="door" style="width:{w}px;height:{h}px;{extra}">
        <div class="panel" style="left:12%;top:7%;width:76%;height:38%"></div>
        <div class="panel" style="left:12%;top:52%;width:76%;height:40%"></div>
        <div class="knob" style="right:10%;top:52%"></div>
      </div>"""


DOOR_CSS = f""".door {{ position:absolute; border-radius: 18px 18px 6px 6px; background: linear-gradient(180deg,#6b4527,#3d2615);
            border: 12px solid #24150b; box-shadow: 0 30px 80px rgba(0,0,0,.55), inset 0 0 0 4px rgba(255,200,61,.15); }}
    .door .panel {{ position:absolute; border: 6px solid rgba(0,0,0,.35); border-radius: 8px; background: rgba(255,255,255,.03); }}
    .door .knob {{ position:absolute; width: 34px; height: 34px; border-radius: 50%; background: {GOLD}; box-shadow: 0 0 24px {GOLD}; }}"""

# ---------- escena 1: hook ----------
h = "hook"
x_left, x_right = 300, 780      # posiciones de la frontera
s_hook = scene_file(h, DOOR_CSS + f"""
    #hook-wrap {{ position:absolute; inset:0; transform-origin: 540px 700px; }}
    #hook-be {{ position:absolute; left:0; top:0; width:{W}px; height:{H}px; background: linear-gradient(90deg, rgba(255,200,61,.20), rgba(255,200,61,.07)); transform-origin: 0 0; }}
    #hook-line {{ position:absolute; top:385px; left:0; width:0; height:610px; border-left: 8px dashed {GOLD}; filter: drop-shadow(0 0 14px {GOLD}); }}
    #hook-lbl-be, #hook-lbl-nl {{ position:absolute; top: 1000px; font-weight:900; font-size: 30px; }}
    #hook-lbl-be {{ left: 110px; color:{GOLD}; }}  #hook-lbl-nl {{ left: 570px; color:{ORANGE}; }}
    #hook-tag {{ left: 0; width:{W}px; top: 360px; height: 90px; background:none; text-align:center; padding:0; }}
    #hook-tag-nl, #hook-tag-be {{ position:absolute; left:0; width:100%; top:0; font-size: 56px; }}
    #hook-tag-nl {{ color:{ORANGE}; }} #hook-tag-be {{ color:{GOLD}; opacity:0; }}""",
    f"""    <div id="hook-wrap">
      <div id="hook-be"></div>
      <div id="hook-line"></div>
      {door("hook-door", 300, 500, "left:390px;top:470px;")}
      <div id="hook-lbl-be" class="mono">◀ BELGIUM</div>
      <div id="hook-lbl-nl" class="mono">NETHERLANDS ▶</div>
      <div id="hook-tag" class="tag"><div id="hook-tag-nl">NETHERLANDS</div><div id="hook-tag-be">BELGIUM</div></div>
    </div>""",
    f"""      const sweep = {L(h, wt('decides'))}, flip = {L(h, wt('country', 1))};
      tl.fromTo("#hook-wrap", {{ scale: 1.0 }}, {{ scale: 1.07, duration: {SLOT[h][1]}, ease: "none" }}, 0);
      tl.fromTo("#hook-be", {{ scaleX: {x_left / W:.4f} }}, {{ scaleX: {x_left / W:.4f}, duration: 0.01 }}, 0);
      tl.fromTo("#hook-line", {{ x: {x_left} }}, {{ x: {x_left}, duration: 0.01 }}, 0);
      tl.to("#hook-be", {{ scaleX: {x_right / W:.4f}, duration: 0.55, ease: "power3.inOut" }}, sweep);
      tl.to("#hook-line", {{ x: {x_right}, duration: 0.55, ease: "power3.inOut" }}, sweep);
      tl.fromTo("#hook-tag-nl", {{ opacity: 1, y: 0 }}, {{ opacity: 0, y: -40, duration: 0.16, ease: "power2.in" }}, flip - 0.16);
      tl.fromTo("#hook-tag-be", {{ opacity: 0, y: 40, scale: 1.15 }}, {{ opacity: 1, y: 0, scale: 1, duration: 0.2, ease: "back.out(2)" }}, flip);""")
cues = [
    {"t": round(wt("decides") + 0.28, 3), "kind": "whoosh", "label": "frontera barre la puerta (pico de velocidad)"},
    {"t": wt("country", 1), "kind": "click", "label": "etiqueta cambia a BELGIUM"},
]

# ---------- escena 2: mapa ----------
m = "map"
blob_svg = "\n".join(f'        <path id="map-b{i}" class="blob" d="{blob_path(x, y, r, i)}" style="transform-origin:{x:.1f}px {y:.1f}px"/>'
                     for i, (x, y, r) in enumerate(blobs))
dots_svg = "\n".join(f'        <circle id="map-d{k}" class="dot" cx="{blobs[i][0]:.1f}" cy="{blobs[i][1]:.1f}" r="{blobs[i][2] * 0.38:.1f}" style="transform-origin:{blobs[i][0]:.1f}px {blobs[i][1]:.1f}px"/>'
                     for k, i in enumerate(big7))
jag = "M0,450 " + " ".join(f"L{x},{450 + (-1) ** k * rng.randint(30, 110)}" for k, x in enumerate(range(60, 901, 60)))
t_but, t_bel = L(m, wt("But", 1)), L(m, wt("Belgium", 2))
t_isl0, t_isl1 = L(m, wt("islands", 1)), L(m, wt("inside", 1))
t_and, t_seven = L(m, wt("And", 2)), L(m, wt("Seven"))
pop_js = "\n".join(f'      tl.fromTo("#map-b{i}", {{ scale: 0, opacity: 0 }}, {{ scale: 1, opacity: 1, duration: 0.22, ease: "back.out(2.2)" }}, {t_isl0 + i * (t_isl1 - t_isl0 - 0.25) / 21:.3f});'
                   for i in range(22))
dot_js = "\n".join(f'      tl.fromTo("#map-d{k}", {{ scale: 0, opacity: 0 }}, {{ scale: 1, opacity: 1, duration: 0.2, ease: "back.out(2.5)" }}, {t_seven + k * 0.07:.3f});'
                   for k in range(7))
s_map = scene_file(m, f"""
    #map-fit {{ position:absolute; left:200px; top:360px; width:900px; height:900px; transform: scale(0.7556); transform-origin: 0 0; overflow: hidden; border-radius: 24px; }}
    #map-drift {{ position:absolute; left:0; top:0; width:900px; height:900px; transform-origin: 450px 450px; }}
    #map-cam {{ position:absolute; left:0; top:0; width:900px; height:900px; transform-origin: {zx:.0f}px {zy:.0f}px; }}
    #map-cam svg {{ position:absolute; inset:0; overflow: visible; }}
    .blob {{ fill: rgba(255,200,61,.85); stroke: {GOLD}; stroke-width: 3; }}
    .dot {{ fill: {ORANGE}; stroke: #fff; stroke-width: 3; }}
    #map-pin {{ position:absolute; left: 400px; top: 410px; width: 100px; height: 80px; }}
    #map-pin div {{ position:absolute; left: 36px; top: 26px; width: 28px; height: 28px; border-radius: 50%; background:#fff; box-shadow: 0 0 0 10px rgba(255,255,255,.25), 0 0 30px #fff; }}
    #map-pinlbl {{ left: 300px; top: 300px; width: 300px; text-align:center; color:#fff; font-size: 38px; padding: 10px 0; }}
    #map-lbl-nl {{ left: 60px; top: 150px; color:{ORANGE}; }}  #map-lbl-be {{ left: 60px; top: 700px; color:{GOLD}; }}
    #map-stamp {{ left: 0; top: 520px; width: 900px; text-align:center; transform-origin: 450px 560px; }}
    #map-count {{ left: 340px; top: 372px; width: 400px; text-align: center; background: rgba(8,10,18,.82); padding: 8px 0 14px; }}
    #map-count-n {{ font-size: 120px; font-weight: 900; color: {GOLD}; line-height: 1; font-family: 'Inter Display'; letter-spacing: 0; }}
    .cl {{ font-size: 28px; color: {INK}; }}
    #map-count2 {{ left: 240px; width: 600px; text-align: center; background: rgba(8,10,18,.85); padding: 8px 0 14px; top: 372px; opacity: 0; }}
    #map-count2-n {{ font-size: 120px; font-weight: 900; color: {ORANGE}; line-height: 1; font-family: 'Inter Display'; letter-spacing: 0; }}
    #map-note {{ left: 90px; top: 1010px; width: 900px; text-align: center; font-size: 28px; color: rgba(244,241,234,.55); background:none; }}""",
    f"""    <div id="map-fit"><div id="map-drift"><div id="map-cam">
      <svg width="900" height="900" viewBox="0 0 900 900">
        <path id="map-nl" d="M20,40 Q450,0 880,40 L880,450 L20,450 Z" fill="rgba(255,122,26,.16)" stroke="{ORANGE}" stroke-width="4"/>
        <path id="map-be" d="M20,450 L880,450 L880,860 Q450,900 20,860 Z" fill="rgba(255,200,61,.14)" stroke="{GOLD}" stroke-width="4"/>
        <path id="map-nlfull" d="M20,40 Q450,0 880,40 L880,860 Q450,900 20,860 Z" fill="rgba(255,122,26,.16)" stroke="{ORANGE}" stroke-width="4" opacity="0"/>
        <path id="map-line" d="M0,450 L900,450" stroke="{GOLD}" stroke-width="8" stroke-dasharray="22 16" fill="none"/>
        <path id="map-jag" d="{jag}" stroke="{GOLD}" stroke-width="8" stroke-dasharray="22 16" fill="none" opacity="0"/>
{blob_svg}
{dots_svg}
      </svg>
      <div id="map-pin"><div></div></div>
      <div id="map-pinlbl" class="tag">BAARLE</div>
      <div id="map-lbl-nl" class="tag">NETHERLANDS</div>
      <div id="map-lbl-be" class="tag">BELGIUM</div>
      <div id="map-stamp" class="stamp">NOT THAT SIMPLE</div>
    </div></div></div>
    <div id="map-count" class="tag"><div id="map-count-n">0</div><div class="cl">BELGIAN ENCLAVES</div></div>
    <div id="map-count2" class="tag"><div id="map-count2-n">7</div><div class="cl">DUTCH ENCLAVES INSIDE THEM</div></div>
    <div id="map-note" class="tag">ILLUSTRATIVE MAP · NOT TO SCALE</div>""",
    f"""      tl.fromTo("#map-drift", {{ scale: 1, rotation: -1.2 }}, {{ scale: 1.1, rotation: 1.2, duration: {SLOT[m][1]}, ease: "none" }}, 0);
      tl.fromTo("#map-cam", {{ scale: 0.86, opacity: 0 }}, {{ scale: 1, opacity: 1, duration: 0.45, ease: "power3.out" }}, 0);
      tl.fromTo("#map-pin", {{ scale: 0 }}, {{ scale: 1, duration: 0.3, ease: "back.out(2)" }}, 0.35);
      tl.fromTo("#map-pinlbl", {{ opacity: 0, y: 20 }}, {{ opacity: 1, y: 0, duration: 0.25 }}, 0.45);
      tl.fromTo("#map-lbl-nl, #map-lbl-be", {{ opacity: 0 }}, {{ opacity: 1, duration: 0.3 }}, 0.25);
      tl.fromTo("#map-count, #map-count2, #map-stamp", {{ opacity: 0 }}, {{ opacity: 0, duration: 0.01 }}, 0);
      // "But not with one simple line": la línea recta se rompe
      tl.to("#map-line", {{ opacity: 0, duration: 0.15 }}, {t_but});
      tl.fromTo("#map-jag", {{ opacity: 0 }}, {{ opacity: 1, duration: 0.15 }}, {t_but});
      tl.fromTo("#map-stamp", {{ opacity: 0, scale: 1.6, rotation: -14 }}, {{ opacity: 1, scale: 1, rotation: -6, duration: 0.18, ease: "power4.in" }}, {L(m, wt("simple")) - 0.18});
      // "Belgium owns 22 islands": todo es Países Bajos, aparecen los enclaves
      tl.to("#map-stamp, #map-jag, #map-be, #map-lbl-be, #map-pin, #map-pinlbl", {{ opacity: 0, duration: 0.25 }}, {t_bel - 0.1});
      tl.to("#map-nl", {{ opacity: 0, duration: 0.25 }}, {t_bel - 0.1});
      tl.fromTo("#map-nlfull", {{ opacity: 0 }}, {{ opacity: 1, duration: 0.3 }}, {t_bel - 0.1});
      tl.to("#map-lbl-nl", {{ opacity: 0, duration: 0.2 }}, {t_bel - 0.1});
      tl.fromTo("#map-count", {{ opacity: 0, y: 20 }}, {{ opacity: 1, y: 0, duration: 0.25 }}, {t_bel});
      const c = {{ n: 0 }}, el = document.querySelector("#map-count-n");
      tl.fromTo(c, {{ n: 0 }}, {{ n: 22, duration: {t_isl1 - t_isl0:.3f}, ease: "none", onUpdate: () => {{ el.textContent = Math.round(c.n); }} }}, {t_isl0});
      tl.fromTo("#map-note", {{ opacity: 0 }}, {{ opacity: 1, duration: 0.3 }}, {t_isl0});
{pop_js}
      // "And inside those Belgian islands? Seven Dutch ones": zoom
      tl.to("#map-cam", {{ scale: 1.28, duration: 1.1, ease: "power3.inOut" }}, {t_and});
      tl.to("#map-count, #map-note", {{ opacity: 0, duration: 0.2 }}, {t_and});
      tl.fromTo("#map-count2", {{ opacity: 0, scale: 0.7 }}, {{ opacity: 1, scale: 1, duration: 0.25, ease: "back.out(2)" }}, {t_seven});
{dot_js}
      tl.to("#map-cam", {{ scale: 1.33, duration: {SLOT[m][1] - t_and - 1.1:.3f}, ease: "none" }}, {t_and + 1.1:.3f});""")
cues += [{"t": wt("simple"), "kind": "stamp", "label": "sello NOT THAT SIMPLE"}]
for k, i in enumerate([0, 11, 21]):  # 3 de los 22 pops suenan (norma ~5 efectos/10 s), tono subiendo
    cues.append({"t": round(S[m] + t_isl0 + i * (t_isl1 - t_isl0 - 0.25) / 21 + 0.05, 3), "kind": "pop", "pitch": k * 2, "label": f"enclave {i + 1}"})
cues += [{"t": round(S[m] + t_and + 0.45, 3), "kind": "whoosh2", "label": "zoom a los enclaves (pico)"},
         {"t": round(S[m] + t_seven + 0.03, 3), "kind": "tick", "pitch": 3, "label": "aparecen los 7 neerlandeses"}]

# ---------- escena 3: países dentro de países ----------
n = "nest"
tn = [L(n, wt("countries", 1)), L(n, wt("countries", 2)), L(n, wt("countries", 3))]
s_nest = scene_file(n, f"""
    #nest-cam {{ position:absolute; inset:0; transform-origin: 540px 700px; }}
    .box {{ position:absolute; border-radius: 40px; border: 8px solid; }}
    .box .tag {{ left: 20px; top: 16px; font-size: 28px; padding: 8px 14px; }}
    #nest-a {{ left:205px; top:375px; width:670px; height:670px; border-color:{ORANGE}; background: rgba(255,122,26,.12); }}
    #nest-b {{ left:310px; top:490px; width:460px; height:460px; border-color:{GOLD}; background: rgba(255,200,61,.16); }}
    #nest-c {{ left:425px; top:610px; width:230px; height:230px; border-color:{ORANGE}; background: rgba(255,122,26,.45); }}""",
    f"""    <div id="nest-cam">
      <div id="nest-a" class="box"><div class="tag" style="color:{ORANGE}">NETHERLANDS</div></div>
      <div id="nest-b" class="box"><div class="tag" style="color:{GOLD}">BELGIUM</div></div>
      <div id="nest-c" class="box"><div class="tag" style="color:#fff;font-size:30px">NL</div></div>
    </div>""",
    f"""      tl.fromTo("#nest-cam", {{ scale: 1 }}, {{ scale: 1.05, duration: {SLOT[n][1]}, ease: "none" }}, 0);
      tl.fromTo("#nest-a", {{ opacity: 0, scale: 1.2 }}, {{ opacity: 1, scale: 1, duration: 0.3, ease: "power3.out" }}, {max(0.0, tn[0] - 0.05)});
      tl.fromTo("#nest-b", {{ opacity: 0, scale: 0.4 }}, {{ opacity: 1, scale: 1, duration: 0.3, ease: "back.out(1.8)" }}, {tn[1]});
      tl.fromTo("#nest-c", {{ opacity: 0, scale: 0.3 }}, {{ opacity: 1, scale: 1, duration: 0.3, ease: "back.out(2.2)" }}, {tn[2]});""")
cues += [{"t": round(S[n] + tn[1] + 0.12, 3), "kind": "thunk", "pitch": 2, "label": "caja Bélgica encaja"},
         {"t": round(S[n] + tn[2] + 0.12, 3), "kind": "thunk", "pitch": 4, "label": "caja NL encaja"}]

# ---------- escena 4: la calle ----------
st = "street"
bx = 40
bld = []
for k in range(6):
    bw = rng.randint(130, 175)
    bh = rng.randint(300, 480)
    bld.append((bx, bw, bh))
    bx += bw + 8
bld_html = ""
for k, (x0, bw, bh) in enumerate(bld):
    wins = "".join(f'<i style="left:{20 + c * 44}px;top:{30 + r * 70}px"></i>' for r in range((bh - 120) // 70) for c in range((bw - 30) // 44))
    bld_html += f'      <div class="bld" style="left:{x0}px;top:{960 - bh}px;width:{bw}px;height:{bh}px">{wins}</div>\n'
ts = [L(st, wt("streets,")), L(st, wt("shops...")), L(st, wt("homes."))]
s_street = scene_file(st, f"""
    #street-cam {{ position:absolute; inset:0; transform-origin: 540px 800px; }}
    .bld {{ position:absolute; background: #1b2235; border: 4px solid #2c3550; border-radius: 6px 6px 0 0; }}
    .bld i {{ position:absolute; width: 22px; height: 34px; background: rgba(255,200,61,.55); border-radius: 3px; }}
    #street-ground {{ position:absolute; left:0; top:960px; width:{W}px; height: 90px; background:#141a2a; border-top: 4px solid #39425e; }}
    #street-line {{ position:absolute; left: 0; top: 0; width:{W}px; height: 1110px; transform-origin: 0 0; }}
    #street-mark {{ left: 420px; top: 975px; font-size: 34px; color: #fff; background: none; border: 4px solid #fff; padding: 6px 20px; }}
    #street-c0 {{ left: 110px; top: 380px; color:{GOLD}; }} #street-c1 {{ left: 390px; top: 450px; color:{GOLD}; }} #street-c2 {{ left: 650px; top: 380px; color:{GOLD}; }}""",
    f"""    <div id="street-cam">
{bld_html}      <div id="street-ground"></div>
      <svg id="street-line" width="{W}" height="1110" viewBox="0 0 {W} 1110"><path d="M560,400 L520,560 L600,680 L500,800 L560,900 L520,1050" stroke="{GOLD}" stroke-width="9" stroke-dasharray="24 16" fill="none"/></svg>
      <div id="street-mark" class="tag">NL&nbsp;&nbsp;|&nbsp;&nbsp;B</div>
      <div id="street-c0" class="tag">STREETS</div><div id="street-c1" class="tag">SHOPS</div><div id="street-c2" class="tag">HOMES</div>
    </div>""",
    f"""      tl.fromTo("#street-cam", {{ scale: 1.08 }}, {{ scale: 1, duration: {SLOT[st][1]}, ease: "none" }}, 0);
      tl.fromTo("#street-line", {{ scaleY: 0 }}, {{ scaleY: 1, duration: 0.7, ease: "power2.inOut" }}, {L(st, wt('runs')) - 0.2:.3f});
      tl.fromTo("#street-mark", {{ opacity: 0 }}, {{ opacity: 1, duration: 0.3 }}, 0.3);
      tl.fromTo("#street-c0", {{ opacity: 0, y: 30 }}, {{ opacity: 1, y: 0, duration: 0.2, ease: "back.out(2)" }}, {ts[0]});
      tl.fromTo("#street-c1", {{ opacity: 0, y: 30 }}, {{ opacity: 1, y: 0, duration: 0.2, ease: "back.out(2)" }}, {ts[1]});
      tl.fromTo("#street-c2", {{ opacity: 0, y: 30 }}, {{ opacity: 1, y: 0, duration: 0.2, ease: "back.out(2)" }}, {ts[2]});""")
cues += [{"t": round(S[st] + t, 3), "kind": "click", "label": lbl} for t, lbl in zip(ts, ["STREETS", "SHOPS", "HOMES"])]

# ---------- escena 5: la regla de la puerta ----------
ho = "house"
t_side, t_fd = L(ho, wt("Whichever")), L(ho, wt("front", 2))
s_house = scene_file(ho, DOOR_CSS + f"""
    #house-cam {{ position:absolute; inset:0; transform-origin: 540px 760px; }}
    #house-body {{ position:absolute; left: 220px; top: 600px; width: 640px; height: 380px; background:#1d2438; border: 6px solid #36405c; }}
    #house-roof {{ position:absolute; left: 180px; top: 420px; width: 0; height: 0; border-left: 360px solid transparent; border-right: 360px solid transparent; border-bottom: 180px solid #2b3350; }}
    #house-line {{ position:absolute; left: 536px; top: 400px; width: 0; height: 575px; border-left: 8px dashed {GOLD}; }}
    #house-tag {{ left:0; width:{W}px; top: 995px; text-align:center; background:none; padding:0; }}
    #house-t-be, #house-t-nl {{ position:absolute; left:0; width:100%; font-size: 40px; }}
    #house-t-be {{ color:{GOLD}; }} #house-t-nl {{ color:{ORANGE}; opacity:0; }}
    #house-stamp {{ left: 0; width: {W}px; top: 372px; text-align:center; border:none; background:none; padding:0; }}
    #house-stamp span {{ display:inline-block; padding: 16px 30px; border: 7px solid {GOLD}; border-radius: 16px; background: rgba(8,10,18,.6); }}""",
    f"""    <div id="house-cam">
      <div id="house-roof"></div><div id="house-body"></div>
      {door("house-door", 170, 290, "left:320px;top:690px;")}
      <div id="house-line"></div>
      <div id="house-be" class="tag" style="left:240px;top:620px;color:{GOLD};font-size:32px">BE</div>
      <div id="house-nl" class="tag" style="left:762px;top:620px;color:{ORANGE};font-size:32px">NL</div>
      <div id="house-tag" class="tag"><div id="house-t-be">DOOR IN BELGIUM → BELGIAN</div><div id="house-t-nl">DOOR IN NL → DUTCH</div></div>
      <div id="house-stamp" class="stamp"><span>THE FRONT DOOR RULE</span></div>
    </div>""",
    f"""      tl.fromTo("#house-cam", {{ scale: 1 }}, {{ scale: 1.06, duration: {SLOT[ho][1]}, ease: "none" }}, 0);
      tl.fromTo("#house-line", {{ scaleY: 0 }}, {{ scaleY: 1, duration: 0.5, ease: "power2.out", transformOrigin: "50% 0%" }}, 0.1);
      tl.fromTo("#house-tag, #house-be, #house-nl", {{ opacity: 0 }}, {{ opacity: 1, duration: 0.25 }}, 0.5);
      tl.fromTo("#house-door", {{ x: 0 }}, {{ x: 280, duration: 0.55, ease: "power3.inOut" }}, {t_side});
      tl.fromTo("#house-t-be", {{ opacity: 1 }}, {{ opacity: 0, duration: 0.15 }}, {t_side + 0.4:.3f});
      tl.fromTo("#house-t-nl", {{ opacity: 0, scale: 1.12 }}, {{ opacity: 1, scale: 1, duration: 0.2, ease: "back.out(2)" }}, {t_side + 0.55:.3f});
      tl.fromTo("#house-stamp", {{ opacity: 0, scale: 1.6, rotation: -10 }}, {{ opacity: 1, scale: 1, rotation: -4, duration: 0.18, ease: "power4.in" }}, {t_fd - 0.18:.3f});""")
cues += [{"t": round(S[ho] + t_fd, 3), "kind": "stamp", "label": "sello FRONT DOOR RULE"}]

# ---------- escena 6: la frontera parte una puerta ----------
cu = "cut"
t_cuts = L(cu, wt("cuts"))
hit_t = round(t_cuts + 0.42, 3)
s_cut = scene_file(cu, DOOR_CSS + f"""
    #cut-cam {{ position:absolute; inset:0; transform-origin: 540px 690px; }}
    #cut-l, #cut-r {{ position:absolute; top: 385px; width: 200px; height: 640px; opacity: 0; }}
    #cut-l {{ left: 340px; background: rgba(255,200,61,.42); border-radius: 18px 0 0 6px; }}
    #cut-r {{ left: 540px; background: rgba(255,122,26,.42); border-radius: 0 18px 6px 0; }}
    #cut-line {{ position:absolute; left: 536px; top: 360px; width: 0; height: 690px; border-left: 9px dashed {GOLD}; filter: drop-shadow(0 0 16px {GOLD}); transform-origin: 50% 0%; }}
    #cut-be {{ left: 160px; top: 680px; color:{GOLD}; }} #cut-nl {{ left: 790px; top: 680px; color:{ORANGE}; }}""",
    f"""    <div id="cut-cam">
      {door("cut-door", 400, 640, "left:340px;top:385px;")}
      <div id="cut-l"></div><div id="cut-r"></div>
      <div id="cut-line"></div>
      <div id="cut-be" class="tag">BE</div><div id="cut-nl" class="tag">NL</div>
    </div>""",
    f"""      tl.fromTo("#cut-cam", {{ scale: 1.12 }}, {{ scale: 1.0, duration: {t_cuts}, ease: "none" }}, 0);
      tl.fromTo("#cut-line", {{ scaleY: 0 }}, {{ scaleY: 1, duration: 0.42, ease: "power3.in" }}, {t_cuts});
      tl.to("#cut-cam", {{ scale: 1.05, duration: 0.08, ease: "power2.out" }}, {hit_t});
      tl.to("#cut-cam", {{ scale: 1.02, duration: 0.5, ease: "power2.out" }}, {hit_t + 0.08:.3f});
      tl.to("#cut-cam", {{ scale: 1.1, duration: {SLOT[cu][1] - hit_t - 0.6:.3f}, ease: "none" }}, {hit_t + 0.58:.3f});
      tl.fromTo("#cut-l, #cut-r", {{ opacity: 0 }}, {{ opacity: 1, duration: 0.2 }}, {hit_t});
      tl.fromTo("#cut-be, #cut-nl", {{ opacity: 0, y: 20 }}, {{ opacity: 1, y: 0, duration: 0.25 }}, {hit_t + 0.1:.3f});""")
cues += [{"t": round(S[cu] + hit_t, 3), "kind": "hit", "label": "la frontera parte la puerta (golpe)"}]

# ---------- escena 7: giro ----------
b = "brk"
dots = "".join(f'<i style="left:{rng.randint(110, 960)}px;top:{rng.randint(300, 1040)}px;opacity:{rng.uniform(.15, .6):.2f}"></i>' for _ in range(90))
s_brk = scene_file(b, f"""
    #brk-cam {{ position:absolute; inset:0; transform-origin: 540px 650px; }}
    #brk-dots i {{ position:absolute; width: 8px; height: 8px; border-radius: 50%; background: {CYAN}; }}
    #brk-q {{ position:absolute; left:0; width:{W}px; top: 400px; text-align:center; font-size: 460px; font-weight: 900; line-height: 1; color: {GOLD}; text-shadow: 0 0 60px rgba(255,200,61,.6); }}""",
    f"""    <div id="brk-cam"><div id="brk-dots">{dots}</div><div id="brk-q">?</div></div>""",
    f"""      tl.fromTo("#brk-cam", {{ scale: 1.0 }}, {{ scale: 1.22, duration: {SLOT[b][1]}, ease: "none" }}, 0);
      tl.fromTo("#brk-q", {{ opacity: 0, scale: 0.6 }}, {{ opacity: 1, scale: 1, duration: 0.4, ease: "back.out(1.6)" }}, {L(b, wt('strangest')):.3f});""")

# ---------- escena 8: cierre ----------
e = "end"
s_end = scene_file(e, f"""
    #end-tri {{ position:absolute; left: 330px; top: 330px; width: 420px; height: 420px; transform-origin: 210px 210px; }}
    #end-ring, #end-ring2 {{ position:absolute; left: 500px; top: 500px; width: 80px; height: 80px; border-radius: 50%; border: 8px solid #fff; }}
    #end-ep {{ left: 0; width: {W}px; top: 780px; text-align: center; background: none; color: {GOLD}; font-size: 40px; }}
    #end-title {{ transform-origin: 400px 100px; position:absolute; left: 140px; width: 800px; top: 850px; text-align:center; font-weight: 900; font-size: 72px; line-height: 1.02; color: {INK}; }}
    #end-title b {{ color: {GOLD}; }}
    #end-follow {{ left: 0; width: {W}px; top: 1090px; text-align:center; background:none; color: {INK}; font-size: 34px; }}""",
    f"""    <svg id="end-tri" viewBox="0 0 600 600">
      <path d="M300,300 L300,0 A300,300 0 0,1 559.8,450 Z" fill="rgba(255,200,61,.75)"/>
      <path d="M300,300 L559.8,450 A300,300 0 0,1 40.2,450 Z" fill="rgba(255,122,26,.75)"/>
      <path d="M300,300 L40.2,450 A300,300 0 0,1 300,0 Z" fill="rgba(67,217,245,.7)"/>
      <circle cx="300" cy="300" r="26" fill="#fff"/>
    </svg>
    <div id="end-ring"></div><div id="end-ring2"></div>
    <div id="end-ep" class="tag">EP. 2 · NEXT</div>
    <div id="end-title">THE HILL WHERE <b>3 COUNTRIES</b> MEET</div>
    <div id="end-follow" class="tag">FOLLOW SO YOU DON'T MISS IT</div>""",
    f"""      tl.fromTo("#end-tri", {{ scale: 0.5, rotation: -40, opacity: 0 }}, {{ scale: 1, rotation: 0, opacity: 1, duration: 0.6, ease: "power3.out" }}, 0);
      tl.to("#end-tri", {{ rotation: 45, duration: {SLOT[e][1] - 0.6:.3f}, ease: "none" }}, 0.6);
      tl.fromTo("#end-ring", {{ scale: 0.6, opacity: 0.9 }}, {{ scale: 2.4, opacity: 0, duration: 1.2, ease: "power2.out" }}, 0.5);
      tl.fromTo("#end-ring2", {{ scale: 0.6, opacity: 0.9 }}, {{ scale: 2.4, opacity: 0, duration: 1.2, ease: "power2.out" }}, 1.8);
      tl.fromTo("#end-ep", {{ opacity: 0, y: 20 }}, {{ opacity: 1, y: 0, duration: 0.25 }}, 0.2);
      tl.fromTo("#end-title", {{ opacity: 0, y: 40 }}, {{ opacity: 1, y: 0, duration: 0.35, ease: "power3.out" }}, {L(e, wt('hill')) - 0.1:.3f});
      tl.fromTo("#end-title", {{ scale: 1 }}, {{ scale: 1.06, duration: {SLOT[e][1] - L(e, wt('hill')) - 0.3:.3f}, ease: "none" }}, {L(e, wt('hill')) + 0.25:.3f});
      tl.fromTo("#end-follow", {{ opacity: 0, scale: 0.9 }}, {{ opacity: 1, scale: 1, duration: 0.3, ease: "back.out(2)" }}, {L(e, wt('Follow')):.3f});""")
cues += [{"t": round(S[e] + 0.05, 3), "kind": "whoosh_soft", "label": "entra la tarjeta final (giro)"}]

# ---------- captions ----------
cap_items = "\n".join(f'    <div id="{c["id"]}" class="cg"><span class="in">{c["html"]}</span></div>' for c in cap)
cap_js = "\n".join(
    f'      fit("#{c["id"]}", {json.dumps(c["text"])});\n'
    f'      tl.fromTo("#{c["id"]}", {{ opacity: 0, scale: 1.12, visibility: "hidden" }}, {{ opacity: 1, scale: 1, visibility: "visible", duration: 0.16, ease: "back.out(2)" }}, {c["start"]});\n'
    f'      tl.to("#{c["id"]}", {{ opacity: 0, duration: 0.08, ease: "power2.in" }}, {round(c["end"] - 0.08, 3)});\n'
    f'      tl.set("#{c["id"]}", {{ visibility: "hidden" }}, {c["end"]});'
    for c in cap)
s_caps = scene_file("captions", """
    .cg { position:absolute; left:0; top: 1070px; width: 1000px; text-align:center; font-family:'Inter Display'; font-weight: 900;
          line-height: 1.05; overflow: visible; visibility: hidden; transform-origin: 500px 60px; }
    .cg .in { -webkit-text-stroke: 8px rgba(5,6,12,.95); paint-order: stroke fill; text-shadow: 0 6px 18px rgba(0,0,0,.6); }""",
    cap_items,
    """      const fit = (sel, text) => {
        let fs = 96;
        const r = window.__hyperframes && window.__hyperframes.fitTextFontSize
          ? window.__hyperframes.fitTextFontSize(text, { fontFamily: "Inter Display", fontWeight: 900, maxWidth: 760, fontSize: 96, minFontSize: 54 })
          : null;
        if (r && r.fontSize) fs = Math.min(96, r.fontSize);
        document.querySelector(sel).style.fontSize = fs + "px";
      };
""" + cap_js)

# ---------- index ----------
hosts = "\n".join(
    f'      <div id="{k}" data-composition-id="{k}" data-composition-src="compositions/{k}.html" data-start="{SLOT[k][0]}" '
    f'data-duration="{SLOT[k][1]}" data-track-index="1" data-track-kind="graphics" data-width="{W}" data-height="{H}" style="z-index:10"></div>'
    for k in order)
index = f"""<!doctype html>
<html lang="en">
  <head>
    <meta charset="UTF-8" />
    <meta name="viewport" content="width={W}, height={H}" />
    <script src="assets/gsap.min.js"></script>
    <style>
      @font-face {{ font-family: 'Inter Display'; font-weight: 900; src: url('assets/fonts/InterDisplay-Black.otf'); }}
      * {{ margin: 0; padding: 0; box-sizing: border-box; }}
      html, body {{ width: {W}px; height: {H}px; overflow: hidden; background: {NAVY}; }}
      #bg-base {{ position:absolute; inset:0; z-index: 0; background: radial-gradient(120% 80% at 50% 35%, #1a1f33 0%, {NAVY} 60%, #05070d 100%); }}
      #bg-warm {{ position:absolute; inset:0; z-index: 1; background: radial-gradient(90% 60% at 50% 40%, rgba(255,160,60,.16), rgba(0,0,0,0) 70%); }}
      #bg-night {{ position:absolute; inset:0; z-index: 2; background: radial-gradient(100% 70% at 50% 40%, #0d2a5c 0%, #06122b 70%); opacity: 0; }}
      #vignette {{ position:absolute; inset:0; background: radial-gradient(130% 95% at 50% 45%, rgba(0,0,0,0) 55%, rgba(0,0,0,.65) 100%); z-index: 50; pointer-events: none; }}
      #chip {{ position:absolute; left: 0; width: {W}px; top: 276px; text-align:center; z-index: 60; }}
      #chip span {{ display:inline-block; font-family:'JetBrains Mono',monospace; font-weight: 800; font-size: 28px; letter-spacing:.14em;
                   color:{GOLD}; padding: 10px 22px; border: 3px solid rgba(255,200,61,.6); border-radius: 999px; background: rgba(8,10,18,.7); }}
    </style>
  </head>
  <body>
    <div id="root" data-composition-id="main" data-start="0" data-duration="{DUR}" data-width="{W}" data-height="{H}">
      <div id="bg-base" class="clip" data-start="0" data-duration="{DUR}" data-track-index="0"></div>
      <div id="bg-warm" class="clip" data-start="0" data-duration="{DUR}" data-track-index="5"></div>
      <div id="bg-night" class="clip" data-start="0" data-duration="{DUR}" data-track-index="6"></div>
{hosts}
      <div id="captions" data-composition-id="captions" data-composition-src="compositions/captions.html" data-start="0" data-duration="{S['end']}" data-track-index="2" data-track-kind="captions" data-width="{W}" data-height="{H}" style="z-index:30"></div>
      <div id="chip" class="clip" data-start="0" data-duration="{S['end']}" data-track-index="3"><span>BORDER ODDITIES · EP. 1</span></div>
      <div id="vignette" class="clip" data-start="0" data-duration="{DUR}" data-track-index="4" data-layout-ignore></div>
    </div>
    <script>
      window.__timelines = window.__timelines || {{}};
      const tl = gsap.timeline({{ paused: true }});
      tl.to("#bg-night", {{ opacity: 1, duration: 0.4, ease: "power2.out" }}, {S['brk']});
      tl.to("#bg-warm", {{ opacity: 0, duration: 0.4 }}, {S['brk']});
      tl.to("#bg-night", {{ opacity: 0.35, duration: 0.5 }}, {S['end']});
      window.__timelines["main"] = tl;
    </script>
  </body>
</html>
"""

os.makedirs(os.path.join(HERE, "compositions"), exist_ok=True)
files = {"hook": s_hook, "map": s_map, "nest": s_nest, "street": s_street, "house": s_house, "cut": s_cut,
         "brk": s_brk, "end": s_end, "captions": s_caps}
for k, v in files.items():
    open(os.path.join(HERE, "compositions", f"{k}.html"), "w").write(v)
open(os.path.join(HERE, "index.html"), "w").write(index)

# ---------- sonido: cues -> diseno.json ----------
LIBR = "../../../sonido/libreria"
SFX = {
    "whoosh": (f"{LIBR}/whoosh/fs-60007_swipe-whoosh.mp3", "peak", -13),
    "whoosh2": (f"{LIBR}/whoosh/fs-539172_melee-combat-whoosh.mp3", "peak", -15),
    "whoosh_soft": (f"{LIBR}/whoosh/fs-60007_swipe-whoosh.mp3", "peak", -17),
    "click": (f"{LIBR}/click/fs-488534_ui-click.mp3", "attack", -15),
    "pop": (f"{LIBR}/click/fs-488534_ui-click.mp3", "attack", -19),
    "tick": (f"{LIBR}/click/fs-488534_ui-click.mp3", "attack", -14),
    "stamp": (f"{LIBR}/stamp/fs-362624_stamp.mp3", "attack", -11),
    "thunk": (f"{LIBR}/stamp/fs-347325_thick-stamp-nosub-wav.mp3", "attack", -17),
    "hit": (f"{LIBR}/hit/fs-377303_deep-cinematic-impact.mp3", "attack", -9),
}
sfx = []
for c in sorted(cues, key=lambda c: c["t"]):
    f, a, g = SFX[c["kind"]]
    item = {"file": f, "t": fr(c["t"]), "anchor": a, "gain_db": g, "label": c["label"]}
    if c.get("pitch"):
        item["pitch"] = c["pitch"]
    sfx.append(item)
brk, end_ = S["brk"], S["end"]
diseno = {
    "duracion": DUR, "fps": FPS,
    "voz": {"file": "vo.wav", "gain_db": 0, "t": LEAD},
    "musica": {"file": f"{LIBR}/musica/fs-631776_documentary-music-strings.mp3", "gain_db": -6, "duck_db": 8,
               "offset": 8.0, "fade_in": 0.4, "fade_out": 1.2,
               # el giro: la música se retira bajo "that's not the strangest..." y vuelve en la tarjeta final
               "rides": [[brk - 0.1, 0], [brk + 0.35, -10], [end_ - 0.3, -10], [end_ + 0.4, 0]]},
    "sfx": sfx,
    "master": {"lufs": -14, "tp": -1.5, "tp_aac": -1.0},
    "salida": "out/audio.wav",
    "video": "../out/baarle_silent.mp4",
}
os.makedirs(os.path.join(HERE, "audio"), exist_ok=True)
json.dump(diseno, open(os.path.join(HERE, "audio/diseno.json"), "w"), indent=1, ensure_ascii=False)
json.dump({"scenes": SLOT, "cues": cues, "captions": [{k: c[k] for k in ("id", "start", "end", "text")} for c in cap],
           "duration": DUR}, open(os.path.join(HERE, "cues.json"), "w"), indent=1, ensure_ascii=False)
print(f"duración {DUR} s · {len(cap)} grupos de subtítulos · {len(sfx)} efectos")
for k in order:
    print(f"  {k:8} {SLOT[k][0]:6.2f} → {SLOT[k][0] + SLOT[k][1]:6.2f}")
