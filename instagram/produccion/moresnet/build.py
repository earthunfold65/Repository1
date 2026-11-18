#!/usr/bin/env python3
"""EP.2 (remake) Neutral Moresnet (EarthUnfold · Border Oddities). Genera index.html, compositions/*.html, cues.json y audio/diseno.json
a partir de audio/words.json (voz Kokoro montada frase a frase con instagram/scripts/montar_voz.py)."""
import json
import math
import os
import random

HERE = os.path.dirname(os.path.abspath(__file__))
W, H, FPS = 1080, 1920, 30
GOLD, ORANGE, RED, CYAN = "#FFC83D", "#FF7A1A", "#FF4D5E", "#43D9F5"
INK, NAVY = "#F4F1EA", "#0B1020"
words = [w for w in json.load(open(os.path.join(HERE, "audio/words.json")))["words"]]
chunks = json.load(open(os.path.join(HERE, "audio/chunks.json")))


def norm(s):
    return s.lower().strip(".,?!:…").replace("...", "")


def wt(text, n=1, key="start"):
    c = 0
    for w in words:
        if norm(w["text"]) == norm(text):
            c += 1
            if c == n:
                return w[key]
    raise KeyError(f"{text} #{n}")


# inicio de cada frase (chunk) = primera palabra de cada frase
starts, i = [], 0
for item in chunks:
    text = item[0]
    starts.append(words[i]["start"])
    i += len(text.split())
END_VO = words[-1]["end"]
DUR = round(END_VO + 1.25, 2)


def fr(t):
    return round(round(t * FPS) / FPS, 4)


S = {"dream": 0.0, "fake": fr(starts[3] - 0.06), "real": fr(starts[4] - 0.06), "intro": fr(starts[5] - 0.06),
     "crown": fr(starts[7] - 0.06), "people": fr(starts[9] - 0.06), "stamps": fr(starts[10] - 0.06),
     "gone": fr(starts[11] - 0.06), "poll": fr(starts[12] - 0.06), "end": fr(starts[13] - 0.06)}
order = list(S)
SLOT = {k: (S[k], round((S[order[j + 1]] if j + 1 < len(order) else DUR) - S[k], 4)) for j, k in enumerate(order)}


def L(scene, t):
    return round(t - S[scene], 3)


def pt(cx, cy, r, a):
    a = math.radians(a)
    return cx + r * math.sin(a), cy - r * math.cos(a)


def wedge(cx, cy, r, a0, a1):
    x0, y0 = pt(cx, cy, r, a0)
    x1, y1 = pt(cx, cy, r, a1)
    large = 1 if (a1 - a0) % 360 > 180 else 0
    return f"M{cx},{cy} L{x0:.1f},{y0:.1f} A{r},{r} 0 {large},1 {x1:.1f},{y1:.1f} Z"


def lbl_pos(cx, cy, r, a0, a1, k=0.6):
    return pt(cx, cy, r * k, (a0 + a1) / 2)


# geografía ilustrativa: NL norte, DE este, BE suroeste; Moresnet al sur entre BE y DE
P3 = [("NL", ORANGE, 270, 390), ("DE", RED, 30, 150), ("BE", GOLD, 150, 270)]
P4 = [("NL", ORANGE, 270, 390), ("DE", RED, 30, 140), ("?", CYAN, 140, 192), ("BE", GOLD, 192, 270)]


def pie_svg(idp, parts, r=240, size=520, fourth_style="dashed", labels=True, fs=44):
    c = size / 2
    out = [f'<svg id="{idp}" width="{size}" height="{size}" viewBox="0 0 {size} {size}" style="overflow:visible">']
    for name, col, a0, a1 in parts:
        if name == "?":
            if fourth_style == "dashed":
                out.append(f'<path id="{idp}-q" d="{wedge(c, c, r, a0, a1)}" fill="rgba(67,217,245,.10)" stroke="{CYAN}" stroke-width="5" stroke-dasharray="14 10" style="transform-origin:{c}px {c}px"/>')
            else:
                out.append(f'<path id="{idp}-q" d="{wedge(c, c, r, a0, a1)}" fill="{CYAN}" fill-opacity=".9" stroke="#fff" stroke-width="4" style="transform-origin:{c}px {c}px"/>')
        else:
            out.append(f'<path d="{wedge(c, c, r, a0, a1)}" fill="{col}" fill-opacity=".85" stroke="#0b1020" stroke-width="5"/>')
        if labels:
            x, y = lbl_pos(c, c, r, a0, a1, 0.64 if name != "?" else 0.72)
            t = "?" if name == "?" else name
            col_t = "#0b1020" if name != "?" else (CYAN if fourth_style == "dashed" else "#0b1020")
            out.append(f'<text id="{idp}-t-{t if t != "?" else "q"}" x="{x:.1f}" y="{y + fs * 0.36:.1f}" text-anchor="middle" font-family="Inter Display" font-weight="900" font-size="{fs}" fill="{col_t}">{t}</text>')
    out.append(f'<circle cx="{c}" cy="{c}" r="16" fill="#fff"/></svg>')
    return "".join(out)


def scene_file(cid, css, body, js):
    return f"""<template>
  <style>
    @font-face {{ font-family: 'Noto Color Emoji'; src: url('assets/fonts/NotoColorEmoji.ttf'); }}
    #root {{ position: absolute; inset: 0; overflow: hidden; font-family: 'Inter Display', 'Inter', sans-serif; }}
    #root * {{ box-sizing: border-box; }}
    .tag {{ position:absolute; padding: 12px 22px; border-radius: 14px; font-family:'JetBrains Mono',monospace;
           font-weight: 800; font-size: 36px; letter-spacing: .1em; background: rgba(8,10,18,.85); white-space: nowrap; }}
    .stamp {{ position:absolute; padding: 16px 30px; border: 7px solid {GOLD}; border-radius: 16px; color: {GOLD};
             font-weight: 900; font-size: 58px; background: rgba(8,10,18,.6); white-space: nowrap; }}
    .flag {{ font-family: 'Noto Color Emoji'; letter-spacing: 0; }}
    .big {{ position:absolute; left:0; width:1000px; text-align:center; font-weight:900; line-height:.95; color:{INK};
           text-shadow: 0 8px 30px rgba(0,0,0,.6); }}
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


cues = []
SCENES = {}
EMO = "font-family:'Noto Color Emoji';"

# ---------- 1. DREAM: la lista imposible (c0–c2) ----------
k = "dream"
t1, t2, t3 = 0.0, L(k, starts[1]), L(k, wt("casino!"))
SCENES[k] = scene_file(k, f"""
    #dr-cam {{ position:absolute; inset:0; transform-origin: 540px 640px; }}
    #dr-ttl {{ top: 350px; font-size: 84px; }}
    #dr-ttl span {{ color:{GOLD}; }}
    .it {{ position:absolute; left: 150px; width: 730px; height: 150px; border-radius: 28px; background: rgba(14,18,32,.92);
          border: 5px solid rgba(255,255,255,.14); display:flex; align-items:center; gap: 26px; padding: 0 30px;
          box-shadow: 0 20px 50px rgba(0,0,0,.5); transform-origin: 400px 75px; }}
    .it .ic {{ {EMO} font-size: 84px; line-height: 1; }}
    .it .tx {{ font-weight: 900; font-size: 58px; color:{INK}; flex: 1; }}
    .it .ok {{ {EMO} font-size: 70px; }}
    #dr-i1 {{ top: 560px; }} #dr-i2 {{ top: 730px; }} #dr-i3 {{ top: 900px; border-color: {GOLD}; }}""",
    f"""    <div id="dr-cam">
      <div id="dr-i1" class="it"><span class="ic">🪖</span><span class="tx">NO ARMY DRAFT</span><span class="ok">✅</span></div>
      <div id="dr-i2" class="it"><span class="ic">💸</span><span class="tx">ALMOST NO TAXES</span><span class="ok">✅</span></div>
      <div id="dr-i3" class="it"><span class="ic">🎰</span><span class="tx">ITS OWN CASINO</span><span class="ok">✅</span></div>
    </div>
    <div id="dr-ttl" class="big">A COUNTRY<br><span>WITH…</span></div>""",
    f"""      tl.fromTo("#dr-cam", {{ scale: 1.0 }}, {{ scale: 1.06, duration: {SLOT[k][1]}, ease: "none" }}, 0);
      // fotograma 0 = miniatura: titular y primera tarjeta YA visibles, con golpe de escala
      tl.fromTo("#dr-ttl", {{ scale: 1.12 }}, {{ scale: 1, duration: 0.3, ease: "power3.out" }}, 0);
      tl.fromTo("#dr-i1", {{ scale: 1.2, rotation: -3 }}, {{ scale: 1, rotation: 0, duration: 0.3, ease: "back.out(2)" }}, 0);
      tl.fromTo("#dr-i2", {{ x: 700, rotation: 8, opacity: 0 }}, {{ x: 0, rotation: 0, opacity: 1, duration: 0.28, ease: "back.out(1.7)" }}, {t2:.3f});
      tl.fromTo("#dr-i3", {{ scale: 2.2, opacity: 0, rotation: -6 }}, {{ scale: 1, opacity: 1, rotation: 0, duration: 0.22, ease: "power4.in" }}, {t3 - 0.18:.3f});
      tl.to("#dr-cam", {{ x: 14, duration: 0.05, yoyo: true, repeat: 5, ease: "none" }}, {t3 + 0.04:.3f});""")
cues += [{"t": 0.03, "kind": "hit_soft", "label": "entra NO ARMY (frame 0)"},
         {"t": round(starts[1] + 0.12, 3), "kind": "thunk", "pitch": 2, "label": "entra NO TAXES"},
         {"t": round(wt("casino!") + 0.04, 3), "kind": "hit", "label": "golpe CASINO + sacudida"}]

# ---------- 2. FAKE? (c3) ----------
k = "fake"
SCENES[k] = scene_file(k, f"""
    #fk-cam {{ position:absolute; inset:0; transform-origin: 540px 700px; }}
    #fk-em {{ position:absolute; left:0; width:1000px; top: 420px; text-align:center; {EMO} font-size: 300px; line-height: 1; }}
    #fk-st {{ left:0; width:1000px; top: 800px; text-align:center; border:none; background:none; padding:0; transform-origin: 500px 60px; }}
    #fk-st span {{ display:inline-block; padding: 14px 34px; border: 8px solid {RED}; border-radius: 18px; color:{RED}; font-size: 96px; background: rgba(8,10,18,.6); }}""",
    f"""    <div id="fk-cam"><div id="fk-em">🤔</div><div id="fk-st" class="stamp"><span>FAKE?</span></div></div>""",
    f"""      tl.fromTo("#fk-cam", {{ scale: 1.1 }}, {{ scale: 1.0, duration: {SLOT[k][1]}, ease: "power1.out" }}, 0);
      tl.fromTo("#fk-em", {{ scale: 0.3, rotation: -20 }}, {{ scale: 1, rotation: 0, duration: 0.3, ease: "back.out(2.5)" }}, 0.02);
      tl.fromTo("#fk-st", {{ opacity: 0, scale: 1.8, rotation: -14 }}, {{ opacity: 1, scale: 1, rotation: -6, duration: 0.16, ease: "power4.in" }}, {L(k, wt("made")):.3f});""")
cues += [{"t": round(S[k] + L(k, wt("made")) + 0.16, 3), "kind": "stamp", "label": "sello FAKE?"}]

# ---------- 3. REAL… y desaparece (c4) ----------
k = "real"
t_real, t_van = L(k, wt("real...")), L(k, wt("vanished"))
SCENES[k] = scene_file(k, f"""
    #rl-cam {{ position:absolute; inset:0; transform-origin: 540px 700px; }}
    #rl-map {{ position:absolute; left: 190px; top: 420px; width: 700px; height: 520px; }}
    #rl-st {{ left:0; width:1000px; top: 380px; text-align:center; border:none; background:none; padding:0; transform-origin: 500px 60px; }}
    #rl-st span {{ display:inline-block; padding: 14px 34px; border: 8px solid #34d399; border-radius: 18px; color:#34d399; font-size: 96px; background: rgba(8,10,18,.6); }}""",
    f"""    <div id="rl-cam">
      <svg id="rl-map" viewBox="0 0 700 520">
        <path d="M40,60 L330,30 L360,250 L60,300 Z" fill="rgba(255,122,26,.55)" stroke="#0b1020" stroke-width="5"/>
        <path d="M330,30 L660,80 L640,330 L360,250 Z" fill="rgba(160,170,190,.55)" stroke="#0b1020" stroke-width="5"/>
        <path d="M60,300 L360,250 L640,330 L600,490 L90,480 Z" fill="rgba(255,200,61,.5)" stroke="#0b1020" stroke-width="5"/>
        <path id="rl-tri" d="M300,230 L420,250 L350,330 Z" fill="{CYAN}" stroke="#fff" stroke-width="5" style="transform-origin:356px 270px"/>
      </svg>
      <div id="rl-st" class="stamp"><span>REAL</span></div>
    </div>""",
    f"""      tl.fromTo("#rl-cam", {{ scale: 1.0 }}, {{ scale: 1.12, duration: {SLOT[k][1]}, ease: "none" }}, 0);
      tl.fromTo("#rl-map", {{ opacity: 0, y: 40 }}, {{ opacity: 1, y: 0, duration: 0.3 }}, 0.0);
      tl.fromTo("#rl-st", {{ opacity: 0, scale: 1.8, rotation: 10 }}, {{ opacity: 1, scale: 1, rotation: 4, duration: 0.16, ease: "power4.in" }}, {t_real:.3f});
      tl.fromTo("#rl-tri", {{ scale: 1, opacity: 1 }}, {{ scale: 1.5, opacity: 1, duration: 0.25, ease: "back.out(2)" }}, {t_real + 0.3:.3f});
      tl.to("#rl-tri", {{ opacity: 0, scale: 0.2, rotation: 90, duration: 0.6, ease: "power2.in" }}, {t_van:.3f});""")
cues += [{"t": round(S[k] + t_real + 0.16, 3), "kind": "stamp", "label": "sello REAL"},
         {"t": round(S[k] + t_van + 0.3, 3), "kind": "whoosh_soft", "label": "el triángulo desaparece (pico)"}]

# ---------- 4. NEUTRAL MORESNET · 1816 (c5–c6) ----------
k = "intro"
t_name, t_1816 = L(k, wt("Moresnet.")), L(k, wt("1816..."))
SCENES[k] = scene_file(k, f"""
    #in-cam {{ position:absolute; inset:0; transform-origin: 540px 700px; }}
    #in-name {{ top: 360px; font-size: 104px; }}
    #in-name span {{ color:{CYAN}; text-shadow: 0 0 40px rgba(67,217,245,.6); }}
    #in-tri {{ position:absolute; left: 340px; top: 650px; width: 400px; height: 360px; transform-origin: 200px 200px; }}
    #in-nl {{ left: 150px; top: 870px; color:{ORANGE}; font-size: 32px; }}
    #in-pr {{ left: 615px; top: 870px; color:#cfd6e4; font-size: 32px; }}
    #in-yr {{ left:0; width:1000px; top: 585px; text-align:center; background:none; color:{GOLD}; font-size: 40px; }}
    #in-yr span {{ background: rgba(8,10,18,.88); padding: 10px 24px; border-radius: 12px; border: 3px solid rgba(255,200,61,.6); }}""",
    f"""    <div id="in-cam">
      <svg id="in-tri" viewBox="0 0 400 360"><path d="M40,40 L360,70 L190,330 Z" fill="{CYAN}" fill-opacity=".9" stroke="#fff" stroke-width="8" stroke-linejoin="round"/></svg>
      <div id="in-nl" class="tag">🇳🇱 NL</div>
      <div id="in-pr" class="tag">👑 PRUSSIA</div>
      <div id="in-yr" class="tag"><span>BORN IN 1816 · TINY</span></div>
    </div>
    <div id="in-name" class="big">NEUTRAL<br><span>MORESNET</span></div>""",
    f"""      tl.fromTo("#in-cam", {{ scale: 1.2 }}, {{ scale: 1.0, duration: 0.5, ease: "power3.out" }}, 0);
      tl.to("#in-cam", {{ scale: 1.08, duration: {SLOT[k][1] - 0.5:.3f}, ease: "none" }}, 0.5);
      tl.fromTo("#in-name", {{ opacity: 0, scale: 1.4 }}, {{ opacity: 1, scale: 1, duration: 0.22, ease: "power4.in" }}, {max(0.0, t_name - 0.2):.3f});
      tl.fromTo("#in-tri", {{ scale: 0, rotation: -40 }}, {{ scale: 1, rotation: 0, duration: 0.45, ease: "back.out(2)" }}, {max(0.05, t_name - 0.1):.3f});
      tl.to("#in-tri", {{ rotation: 6, duration: {SLOT[k][1] - t_name:.3f}, ease: "none" }}, {t_name + 0.35:.3f});
      tl.fromTo("#in-nl, #in-pr", {{ opacity: 0, y: 20 }}, {{ opacity: 1, y: 0, duration: 0.25 }}, {t_name + 0.3:.3f});
      tl.fromTo("#in-yr", {{ opacity: 0, scale: 0.7 }}, {{ opacity: 1, scale: 1, duration: 0.22, ease: "back.out(2.5)" }}, {min(t_name + 0.45, t_1816 - 0.1):.3f});""")
cues += [{"t": round(S[k] + max(0.0, t_name - 0.2) + 0.22, 3), "kind": "hit", "label": "título NEUTRAL MORESNET"},
         {"t": round(S[k] + t_1816, 3), "kind": "click", "label": "chip 1816"}]

# ---------- 5. DOS CORONAS, UNA MINA → LA COMPARTEN (c7–c8) ----------
k = "crown"
t_king, t_zinc, t_shared = L(k, wt("kingdoms")), L(k, wt("zinc")), L(k, wt("shared"))
SCENES[k] = scene_file(k, f"""
    #cr-cam {{ position:absolute; inset:0; transform-origin: 540px 700px; }}
    .crown {{ position:absolute; top: 420px; {EMO} font-size: 190px; line-height:1; }}
    #cr-a {{ left: 150px; }} #cr-b {{ left: 610px; }}
    #cr-zn {{ position:absolute; left: 420px; top: 640px; width: 240px; height: 260px; border-radius: 22px; background:#1e2a44; border: 7px solid {CYAN};
             text-align:center; color:{INK}; font-family:'JetBrains Mono',monospace; box-shadow: 0 20px 60px rgba(0,0,0,.6); transform-origin: 120px 130px; }}
    #cr-zn b {{ display:block; font-family:'Inter Display'; font-size: 116px; line-height: 1; margin-top: 36px; color:{CYAN}; }}
    #cr-zn i {{ position:absolute; left:16px; top:10px; font-style:normal; font-size: 34px; font-weight: 800; }}
    #cr-zn u {{ display:block; text-decoration:none; font-size: 32px; font-weight:800; letter-spacing:.12em; margin-top: 10px; }}
    #cr-vs {{ position:absolute; left:0; width:1000px; top: 470px; text-align:center; {EMO} font-size: 110px; }}
    #cr-hs {{ position:absolute; left:0; width:1000px; top: 380px; text-align:center; {EMO} font-size: 300px; line-height:1; }}
    #cr-sh {{ left:0; width:1000px; top: 920px; text-align:center; border:none; background:none; padding:0; transform-origin: 500px 60px; }}
    #cr-sh span {{ display:inline-block; padding: 12px 30px; border: 7px solid {GOLD}; border-radius: 16px; color:{GOLD}; font-size: 74px; background: rgba(8,10,18,.6); }}""",
    f"""    <div id="cr-cam">
      <div id="cr-a" class="crown">👑</div><div id="cr-vs">⚔️</div><div id="cr-b" class="crown">👑</div>
      <div id="cr-zn"><i>30</i><b>Zn</b><u>ZINC MINE</u></div>
      <div id="cr-hs" style="opacity:0">🤝</div>
      <div id="cr-sh" class="stamp"><span>SHARED IT</span></div>
    </div>""",
    f"""      tl.fromTo("#cr-cam", {{ scale: 1.08 }}, {{ scale: 1.0, duration: {SLOT[k][1]}, ease: "none" }}, 0);
      tl.fromTo("#cr-a", {{ x: -400 }}, {{ x: 0, duration: 0.3, ease: "back.out(1.8)" }}, {max(0.0, t_king - 0.25):.3f});
      tl.fromTo("#cr-b", {{ x: 400 }}, {{ x: 0, duration: 0.3, ease: "back.out(1.8)" }}, {max(0.0, t_king - 0.25):.3f});
      tl.fromTo("#cr-vs", {{ opacity: 0, scale: 0.4 }}, {{ opacity: 1, scale: 1, duration: 0.2, ease: "back.out(3)" }}, {t_king + 0.1:.3f});
      tl.fromTo("#cr-a", {{ rotation: -6 }}, {{ rotation: 6, duration: 0.18, yoyo: true, repeat: 7, ease: "sine.inOut" }}, {t_king + 0.3:.3f});
      tl.fromTo("#cr-b", {{ rotation: 6 }}, {{ rotation: -6, duration: 0.18, yoyo: true, repeat: 7, ease: "sine.inOut" }}, {t_king + 0.3:.3f});
      tl.fromTo("#cr-zn", {{ opacity: 0, scale: 0.3, rotation: 20 }}, {{ opacity: 1, scale: 1, rotation: 0, duration: 0.3, ease: "back.out(2.4)" }}, {t_zinc - 0.15:.3f});
      // "So they just... shared it."
      tl.to("#cr-vs, #cr-a, #cr-b, #cr-zn", {{ opacity: 0, scale: 0.6, duration: 0.2 }}, {t_shared - 0.45:.3f});
      tl.fromTo("#cr-hs", {{ opacity: 0, scale: 0.3, rotation: -15 }}, {{ opacity: 1, scale: 1, rotation: 0, duration: 0.3, ease: "back.out(2.6)" }}, {t_shared - 0.3:.3f});
      tl.fromTo("#cr-sh", {{ opacity: 0, scale: 1.7, rotation: -10 }}, {{ opacity: 1, scale: 1, rotation: -4, duration: 0.16, ease: "power4.in" }}, {t_shared:.3f});""")
cues += [{"t": round(S[k] + max(0.0, t_king - 0.25) + 0.25, 3), "kind": "whoosh", "label": "entran las coronas (pico)"},
         {"t": round(S[k] + t_zinc + 0.1, 3), "kind": "thunk", "pitch": 2, "label": "ficha Zn"},
         {"t": round(S[k] + t_shared + 0.16, 3), "kind": "stamp", "label": "sello SHARED IT"}]

# ---------- 6. LA GENTE LLEGA: 256 → MILES (c9) ----------
k = "people"
t_rush, t_256, t_th = L(k, starts[9]), L(k, wt("256")), L(k, wt("thousands."))
rng2 = random.Random(5)
dots = []
for r_ in range(9):
    for c_ in range(12):
        dots.append((150 + c_ * 64 + rng2.randint(-6, 6), 520 + r_ * 54 + rng2.randint(-5, 5)))
dots_html = "".join(f'<i id="pp-{n}" style="left:{x}px;top:{y}px">🧍</i>' for n, (x, y) in enumerate(dots))
first = 10
SCENES[k] = scene_file(k, f"""
    #pp-cam {{ position:absolute; inset:0; transform-origin: 540px 700px; }}
    #pp-dots i {{ position:absolute; {EMO} font-style:normal; font-size: 46px; line-height: 1; }}
    #pp-n {{ position:absolute; left:0; width:1000px; top: 372px; text-align:center; font-weight:900; font-size: 108px; color:{GOLD}; line-height:1;
            text-shadow: 0 0 40px rgba(255,200,61,.5); }}
    #pp-l {{ left:0; width:1000px; top: 990px; text-align:center; background:none; color:{INK}; font-size: 34px; }}
    #pp-l span {{ background: rgba(8,10,18,.88); padding: 10px 22px; border-radius: 12px; }}""",
    f"""    <div id="pp-cam"><div id="pp-dots" data-layout-allow-overlap>{dots_html}</div>
      <div id="pp-n">256</div>
      </div>""",
    "      tl.fromTo(\"#pp-cam\", { scale: 1.0 }, { scale: 1.04, duration: " + str(SLOT[k][1]) + ", ease: \"none\" }, 0);\n"
    + "".join(f'      tl.fromTo("#pp-{n}", {{ opacity: 0, scale: 0 }}, {{ opacity: 1, scale: 1, duration: 0.12, ease: "back.out(3)" }}, {0.05 + n * 0.04:.3f});\n' for n in range(first))
    + "".join(f'      tl.fromTo("#pp-{n}", {{ opacity: 0, scale: 0 }}, {{ opacity: 1, scale: 1, duration: 0.1, ease: "back.out(3)" }}, {t_th - 0.5 + (n - first) * 0.009:.3f});\n' for n in range(first, len(dots)))
    + f"""      const pn = {{ v: 256 }}, pe = document.querySelector("#pp-n");
      tl.fromTo(pn, {{ v: 256 }}, {{ v: 3000, duration: 0.9, ease: "power2.in", onUpdate: () => {{ pe.textContent = Math.round(pn.v).toLocaleString("en-US") + (pn.v > 2990 ? "+" : ""); }} }}, {t_th - 0.5:.3f});
      tl.fromTo("#pp-n", {{ scale: 1 }}, {{ scale: 1.15, duration: 0.15, yoyo: true, repeat: 1 }}, {t_th + 0.4:.3f});
""")
cues += [{"t": round(S[k] + 0.08, 3), "kind": "click", "label": "primeras personas"},
         {"t": round(S[k] + t_th - 0.45, 3), "kind": "whoosh2", "label": "llegan miles (pico)"},
         {"t": round(S[k] + t_th + 0.42, 3), "kind": "tick", "pitch": 4, "label": "contador 3,000+"}]

# ---------- 7. SELLOS + ESPERANTO (c10) ----------
k = "stamps"
t_st, t_esp = L(k, wt("stamps,")), L(k, wt("Esperanto"))
SCENES[k] = scene_file(k, f"""
    #sp-cam {{ position:absolute; inset:0; transform-origin: 540px 700px; }}
    #sp-stamp {{ position:absolute; left: 160px; top: 430px; width: 340px; height: 420px; background:#f3e6c8; transform-origin: 170px 210px;
                 outline: 12px dotted #0b1020; outline-offset: -6px; padding: 26px; box-shadow: 0 25px 60px rgba(0,0,0,.6); }}
    #sp-in {{ width:100%; height:100%; border: 6px solid #7a3b1d; background: linear-gradient(160deg,#c0582a,#7a2f16); color:#fff3d6; text-align:center; font-weight:900; }}
    #sp-in b {{ display:block; font-size: 46px; margin-top: 26px; letter-spacing:.04em; }}
    #sp-in i {{ display:block; {EMO} font-style:normal; font-size: 110px; margin-top: 18px; }}
    #sp-in u {{ display:block; text-decoration:none; font-size: 54px; margin-top: 16px; }}
    #sp-flag {{ position:absolute; left: 570px; top: 470px; width: 340px; height: 230px; background:#1f9d55; border-radius: 12px; transform-origin: 170px 115px; }}
    #sp-flag i {{ position:absolute; left:0; top:0; width:120px; height:120px; background:#fff; border-radius: 12px 0 0 0; color:#1f9d55; font-style:normal; font-size: 90px; line-height:120px; text-align:center; }}
    #sp-bub {{ position:absolute; left: 560px; top: 730px; width: 360px; height: 140px; border-radius: 40px; background:#fff; color:#0b1020; font-weight:900; font-size: 64px; line-height:140px; text-align:center; transform-origin: 60px 140px; }}""",
    f"""    <div id="sp-cam">
      <div id="sp-stamp"><div id="sp-in"><b>MORESNET</b><i>⛏️</i><u>5c</u></div></div>
      <div id="sp-flag"><i>★</i></div>
      <div id="sp-bub">Saluton!</div>
    </div>""",
    f"""      tl.fromTo("#sp-cam", {{ scale: 1.06 }}, {{ scale: 1.0, duration: {SLOT[k][1]}, ease: "none" }}, 0);
      tl.fromTo("#sp-stamp", {{ opacity: 0, scale: 1.8, rotation: -25 }}, {{ opacity: 1, scale: 1, rotation: -6, duration: 0.2, ease: "power4.in" }}, {max(0.02, t_st - 0.35):.3f});
      tl.fromTo("#sp-flag", {{ opacity: 0, x: 300 }}, {{ opacity: 1, x: 0, duration: 0.3, ease: "back.out(1.8)" }}, {t_esp - 0.5:.3f});
      tl.fromTo("#sp-bub", {{ opacity: 0, scale: 0.3 }}, {{ opacity: 1, scale: 1, duration: 0.25, ease: "back.out(2.5)" }}, {t_esp - 0.1:.3f});
      tl.to("#sp-stamp", {{ rotation: -2, duration: {SLOT[k][1] - t_st:.3f}, ease: "none" }}, {t_st:.3f});""")
cues += [{"t": round(S[k] + max(0.02, t_st - 0.35) + 0.2, 3), "kind": "stamp", "label": "sello postal cae"},
         {"t": round(S[k] + t_esp - 0.1 + 0.05, 3), "kind": "click", "pitch": 6, "label": "Saluton!"}]

# ---------- 8. 1920: SE LO DAN A BÉLGICA. GONE. (c11) ----------
k = "gone"
t_tw, t_bel, t_gone = L(k, wt("1920...")), L(k, wt("Belgium.")), L(k, wt("Gone."))
SCENES[k] = scene_file(k, f"""
    #gn-cam {{ position:absolute; inset:0; transform-origin: 540px 700px; }}
    #gn-yr {{ position:absolute; left:0; width:1000px; top: 350px; text-align:center; font-weight:900; font-size: 150px; color:{INK}; line-height: 1; }}
    #gn-map {{ position:absolute; left: 240px; top: 560px; width: 600px; height: 420px; }}
    #gn-st {{ left:0; width:1000px; top: 760px; text-align:center; border:none; background:none; padding:0; transform-origin: 500px 60px; }}
    #gn-st span {{ display:inline-block; padding: 14px 34px; border: 8px solid {RED}; border-radius: 18px; color:{RED}; font-size: 110px; background: rgba(8,10,18,.7); }}""",
    f"""    <div id="gn-cam">
      <div id="gn-yr">1920</div>
      <svg id="gn-map" viewBox="0 0 600 420">
        <path id="gn-be" d="M40,120 L560,80 L520,380 L70,360 Z" fill="rgba(255,200,61,.75)" stroke="#0b1020" stroke-width="6"/>
        <text x="300" y="300" text-anchor="middle" font-family="Inter Display" font-weight="900" font-size="56" fill="#0b1020">BELGIUM</text>
        <path id="gn-tri" d="M250,90 L370,110 L300,200 Z" fill="{CYAN}" stroke="#fff" stroke-width="5" style="transform-origin:306px 133px"/>
      </svg>
      <div id="gn-st" class="stamp" data-layout-allow-overlap><span>GONE</span></div>
    </div>""",
    f"""      tl.fromTo("#gn-cam", {{ scale: 1.0 }}, {{ scale: 1.12, duration: {SLOT[k][1]}, ease: "none" }}, 0);
      tl.fromTo("#gn-yr", {{ opacity: 0, scale: 1.6 }}, {{ opacity: 1, scale: 1, duration: 0.2, ease: "power4.in" }}, {max(0.02, t_tw - 0.2):.3f});
      tl.fromTo("#gn-map", {{ opacity: 0, y: 40 }}, {{ opacity: 1, y: 0, duration: 0.3 }}, 0.1);
      tl.to("#gn-tri", {{ fill: "{GOLD}", y: 60, scale: 0.85, duration: 0.5, ease: "power2.inOut" }}, {t_bel - 0.3:.3f});
      tl.to("#gn-tri", {{ opacity: 0, duration: 0.3 }}, {t_bel + 0.25:.3f});
      tl.fromTo("#gn-st", {{ opacity: 0, scale: 2, rotation: -16 }}, {{ opacity: 1, scale: 1, rotation: -6, duration: 0.16, ease: "power4.in" }}, {t_gone - 0.12:.3f});
      tl.to("#gn-cam", {{ x: 16, duration: 0.05, yoyo: true, repeat: 5, ease: "none" }}, {t_gone + 0.05:.3f});""")
cues += [{"t": round(S[k] + max(0.02, t_tw - 0.2) + 0.2, 3), "kind": "thunk", "label": "1920"},
         {"t": round(S[k] + t_gone + 0.04, 3), "kind": "hit", "label": "GONE + sacudida"}]

# ---------- 9. ENCUESTA (c12) ----------
k = "poll"
SCENES[k] = scene_file(k, f"""
    #pl-q {{ top: 360px; font-size: 92px; }}
    #pl-q span {{ color:{GOLD}; }}
    .btn {{ position:absolute; left: 190px; width: 620px; height: 150px; border-radius: 30px; font-weight:900; font-size: 70px; line-height: 150px; text-align:center;
           box-shadow: 0 20px 60px rgba(0,0,0,.5); transform-origin: 310px 75px; }}
    .btn i {{ {EMO} font-style:normal; }}
    #pl-y {{ top: 640px; background: #34d399; color:#062b1d; }}
    #pl-n {{ top: 830px; background: #ff4d5e; color:#2b0609; }}""",
    f"""    <div id="pl-q" class="big">WOULD YOU HAVE<br><span>MOVED THERE?</span></div>
    <div id="pl-y" class="btn"><i>🙋</i> YES</div>
    <div id="pl-n" class="btn"><i>🙅</i> NO</div>""",
    f"""      tl.fromTo("#pl-q", {{ opacity: 0, y: 30 }}, {{ opacity: 1, y: 0, duration: 0.25, ease: "power3.out" }}, 0.02);
      tl.fromTo("#pl-y", {{ opacity: 0, x: -500 }}, {{ opacity: 1, x: 0, duration: 0.3, ease: "back.out(1.8)" }}, 0.25);
      tl.fromTo("#pl-n", {{ opacity: 0, x: 500 }}, {{ opacity: 1, x: 0, duration: 0.3, ease: "back.out(1.8)" }}, 0.4);
      tl.to("#pl-y", {{ scale: 1.06, duration: 0.3, yoyo: true, repeat: 3, ease: "sine.inOut" }}, 0.8);""")
cues += [{"t": round(S[k] + 0.3, 3), "kind": "click", "pitch": 2, "label": "YES"},
         {"t": round(S[k] + 0.45, 3), "kind": "click", "pitch": -2, "label": "NO"}]

# ---------- 10. CIERRE: EP. 3 (c13) ----------
k = "end"
SCENES[k] = scene_file(k, f"""
    #en-isl {{ position:absolute; left: 290px; top: 380px; width: 500px; height: 300px; }}
    #en-ring {{ position:absolute; left: 300px; top: 300px; width: 480px; height: 460px; transform-origin: 240px 230px; }}
    #en-ep {{ left: 0; width: 1000px; top: 770px; text-align:center; background:none; color:{GOLD}; font-size: 38px; }}
    #en-title {{ position:absolute; left: 100px; width: 800px; top: 830px; text-align:center; font-weight:900; font-size: 64px; line-height: 1.02; color:{INK}; }}
    #en-title b {{ color:{GOLD}; }}
    #en-follow {{ left: 0; width: 1000px; top: 1065px; text-align:center; background:none; color:{INK}; font-size: 30px; }}""",
    f"""    <svg id="en-isl" viewBox="0 0 500 300">
      <path d="M40,150 C40,80 140,40 250,40 L250,260 C140,260 40,220 40,150 Z" fill="#2f5bd3"/>
      <path d="M250,40 C360,40 460,80 460,150 C460,220 360,260 250,260 Z" fill="#d93a3a"/>
      <text x="145" y="168" text-anchor="middle" font-family="Inter Display" font-weight="900" font-size="54" fill="#fff">FR</text>
      <text x="355" y="168" text-anchor="middle" font-family="Inter Display" font-weight="900" font-size="54" fill="#fff">ES</text>
    </svg>
    <svg id="en-ring" viewBox="0 0 480 460"><path d="M240,20 A220,210 0 1,1 60,110" fill="none" stroke="#fff" stroke-width="10" stroke-linecap="round" stroke-dasharray="26 18"/>
      <path d="M60,110 L40,60 L100,80 Z" fill="#fff"/></svg>
    <div id="en-ep" class="tag">EP. 3 · NEXT</div>
    <div id="en-title">THE ISLAND THAT SWITCHES COUNTRIES <b>EVERY 6 MONTHS</b></div>
    <div id="en-follow" class="tag">FOLLOW SO YOU DON'T MISS IT</div>""",
    f"""      tl.fromTo("#en-isl", {{ scale: 0.6, opacity: 0 }}, {{ scale: 1, opacity: 1, duration: 0.45, ease: "back.out(1.8)" }}, 0);
      tl.fromTo("#en-ring", {{ rotation: 0, opacity: 0 }}, {{ rotation: 360, opacity: 1, duration: {SLOT[k][1]:.3f}, ease: "none" }}, 0);
      tl.fromTo("#en-ep", {{ opacity: 0, y: 20 }}, {{ opacity: 1, y: 0, duration: 0.25 }}, 0.2);
      tl.fromTo("#en-title", {{ opacity: 0, y: 40 }}, {{ opacity: 1, y: 0, duration: 0.35, ease: "power3.out" }}, {max(0.3, L(k, wt('island')) - 0.1):.3f});
      tl.fromTo("#en-follow", {{ opacity: 0, scale: 0.9 }}, {{ opacity: 1, scale: 1, duration: 0.3, ease: "back.out(2)" }}, {L(k, wt('switches')):.3f});""")
cues += [{"t": round(S[k] + 0.12, 3), "kind": "whoosh_soft", "label": "entra la tarjeta final"}]
# ---------- captions ----------
KEY = {"army", "taxes", "casino", "real", "vanished", "moresnet", "1816", "kingdoms", "zinc", "shared", "256",
       "thousands", "stamps", "esperanto", "1920", "belgium", "gone", "forever", "moved", "island", "six"}
groups, cur = [], []
for k, w in enumerate(words):
    if w["start"] >= S["end"]:
        break
    cur.append(w)
    nxt = words[k + 1] if k + 1 < len(words) else None
    gap = (nxt["start"] - w["end"]) if nxt else 9
    punct = w["text"][-1] in ".,?!:" or w["text"].endswith("...")
    if len(cur) == 3 or punct or gap >= 0.2 or (nxt and nxt["start"] >= S["end"]):
        groups.append(cur)
        cur = []
if cur:
    groups.append(cur)
cap = []
for gi, gr in enumerate(groups):
    st = max(0.1, gr[0]["start"] - 0.04)
    en_ = groups[gi + 1][0]["start"] - 0.02 if gi + 1 < len(groups) else gr[-1]["end"] + 0.25
    en_ = min(en_, gr[-1]["end"] + 0.6, S["end"] - 0.02)
    hw = []
    for w in gr:
        t = w["text"].upper().strip(",:")
        hw.append(f'<span style="color:{GOLD if norm(w["text"]) in KEY else INK}">{t}</span>')
    cap.append({"id": f"cg{gi}", "start": round(st, 3), "end": round(en_, 3), "html": " ".join(hw),
                "text": " ".join(x["text"].upper() for x in gr)})
cap_items = "\n".join(f'    <div id="{c["id"]}" class="cg"><span class="in">{c["html"]}</span></div>' for c in cap)
cap_js = "\n".join(
    f'      fit("#{c["id"]}", {json.dumps(c["text"])});\n'
    f'      tl.fromTo("#{c["id"]}", {{ opacity: 0, scale: 1.12, visibility: "hidden" }}, {{ opacity: 1, scale: 1, visibility: "visible", duration: 0.14, ease: "back.out(2)" }}, {c["start"]});\n'
    f'      tl.to("#{c["id"]}", {{ opacity: 0, duration: 0.07, ease: "power2.in" }}, {round(c["end"] - 0.07, 3)});\n'
    f'      tl.set("#{c["id"]}", {{ visibility: "hidden" }}, {c["end"]});' for c in cap)
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
      #bg-base {{ position:absolute; inset:0; z-index:0; background: radial-gradient(120% 80% at 50% 35%, #1a1f33 0%, {NAVY} 60%, #05070d 100%); }}
      #bg-warm {{ position:absolute; inset:0; z-index:1; background: radial-gradient(90% 60% at 50% 40%, rgba(255,160,60,.18), rgba(0,0,0,0) 70%); }}
      #bg-night {{ position:absolute; inset:0; z-index:2; background: radial-gradient(100% 70% at 50% 40%, #0d2a5c 0%, #06122b 70%); opacity: 0; }}
      #vignette {{ position:absolute; inset:0; z-index: 50; pointer-events:none; background: radial-gradient(130% 95% at 50% 45%, rgba(0,0,0,0) 55%, rgba(0,0,0,.65) 100%); }}
      #chip {{ position:absolute; left: 0; width: {W}px; top: 276px; text-align:center; z-index: 60; }}
      #chip span {{ display:inline-block; font-family:'JetBrains Mono',monospace; font-weight: 800; font-size: 28px; letter-spacing:.14em;
                   color:{GOLD}; padding: 10px 22px; border: 3px solid rgba(255,200,61,.6); border-radius: 999px; background: rgba(8,10,18,.7); }}
      #hud {{ position:absolute; left: 0; width: {W}px; top: 222px; text-align:center; z-index: 60; }}
      #hud span {{ display:inline-block; font-family:'JetBrains Mono',monospace; font-weight: 800; font-size: 26px; letter-spacing:.12em; color:{CYAN}; }}
    </style>
  </head>
  <body>
    <div id="root" data-composition-id="main" data-start="0" data-duration="{DUR}" data-width="{W}" data-height="{H}">
      <div id="bg-base" class="clip" data-start="0" data-duration="{DUR}" data-track-index="0"></div>
      <div id="bg-warm" class="clip" data-start="0" data-duration="{DUR}" data-track-index="5"></div>
      <div id="bg-night" class="clip" data-start="0" data-duration="{DUR}" data-track-index="6"></div>
{hosts}
      <div id="captions" data-composition-id="captions" data-composition-src="compositions/captions.html" data-start="0" data-duration="{S['end']}" data-track-index="2" data-track-kind="captions" data-width="{W}" data-height="{H}" style="z-index:30"></div>
      <div id="chip" class="clip" data-start="0" data-duration="{S['end']}" data-track-index="3"><span>BORDER ODDITIES · EP. 2</span></div>
      <div id="vignette" class="clip" data-start="0" data-duration="{DUR}" data-track-index="4" data-layout-ignore></div>
    </div>
    <script>
      window.__timelines = window.__timelines || {{}};
      const tl = gsap.timeline({{ paused: true }});
      tl.to("#bg-night", {{ opacity: 1, duration: 0.4 }}, {S['gone']});
      tl.to("#bg-warm", {{ opacity: 0, duration: 0.4 }}, {S['gone']});
      tl.to("#bg-night", {{ opacity: 0, duration: 0.4 }}, {S['poll']});
      tl.to("#bg-warm", {{ opacity: 1, duration: 0.4 }}, {S['poll']});
      tl.to("#bg-night", {{ opacity: 0.5, duration: 0.5 }}, {S['end']});
      window.__timelines["main"] = tl;
    </script>
  </body>
</html>
"""
os.makedirs(os.path.join(HERE, "compositions"), exist_ok=True)
for k, txt in {**SCENES, "captions": s_caps}.items():
    open(os.path.join(HERE, "compositions", f"{k}.html"), "w").write(txt)
open(os.path.join(HERE, "index.html"), "w").write(index)

LIBR = "../../../sonido/libreria"
SFX = {
    "whoosh": (f"{LIBR}/whoosh/fs-60007_swipe-whoosh.mp3", "peak", -13),
    "whoosh2": (f"{LIBR}/whoosh/fs-539172_melee-combat-whoosh.mp3", "peak", -15),
    "whoosh_soft": (f"{LIBR}/whoosh/fs-60007_swipe-whoosh.mp3", "peak", -17),
    "click": (f"{LIBR}/click/fs-488534_ui-click.mp3", "attack", -15),
    "tick": (f"{LIBR}/click/fs-488534_ui-click.mp3", "attack", -14),
    "stamp": (f"{LIBR}/stamp/fs-362624_stamp.mp3", "attack", -11),
    "thunk": (f"{LIBR}/stamp/fs-347325_thick-stamp-nosub-wav.mp3", "attack", -17),
    "hit": (f"{LIBR}/hit/fs-377303_deep-cinematic-impact.mp3", "attack", -10),
    "hit_soft": (f"{LIBR}/hit/fs-377303_deep-cinematic-impact.mp3", "attack", -15),
}
sfx = []
for c in sorted(cues, key=lambda c: c["t"]):
    f, a, gdb = SFX[c["kind"]]
    it = {"file": f, "t": fr(c["t"]), "anchor": a, "gain_db": gdb, "label": c["label"]}
    if c.get("pitch"):
        it["pitch"] = c["pitch"]
    sfx.append(it)
diseno = {
    "duracion": DUR, "fps": FPS,
    "voz": {"file": "vo.wav", "gain_db": 0, "t": 0},
    # bucle de misterio de nivel constante (LRA 2 LU) + ducking suave: sin "respiraciones"
    "musica": {"file": f"{LIBR}/musica/fs-446745_dilemma-2a-mystery-music-loop.mp3", "gain_db": -9, "duck_db": 5,
               "loop": True, "offset": 0.0, "fade_in": 0.05, "fade_out": 1.2,
               "rides": [[S["gone"] - 0.05, 0], [S["gone"] + 0.25, -9], [S["poll"] - 0.2, -9], [S["poll"] + 0.3, 0]]},
    "sfx": sfx,
    "master": {"lufs": -14, "tp": -1.5, "tp_aac": -1.0},
    "salida": "out/audio.wav",
    "video": "../out/moresnet_silent.mp4", "video_salida": "../out/moresnet_CON_MUSICA.mp4",
}
json.dump(diseno, open(os.path.join(HERE, "audio/diseno.json"), "w"), indent=1, ensure_ascii=False)
# versión SIN música: para añadir el audio en tendencia dentro de Instagram / TikTok / Shorts / Facebook
sin = {k2: v2 for k2, v2 in diseno.items() if k2 != "musica"}
sin.update(salida="out/audio_sin_musica.wav", video_salida="../out/moresnet_SIN_MUSICA.mp4")
json.dump(sin, open(os.path.join(HERE, "audio/diseno_sin_musica.json"), "w"), indent=1, ensure_ascii=False)
json.dump({"scenes": SLOT, "cues": cues, "captions": [{k: c[k] for k in ("id", "start", "end", "text")} for c in cap], "duration": DUR},
          open(os.path.join(HERE, "cues.json"), "w"), indent=1, ensure_ascii=False)
print(f"duración {DUR} s · {len(cap)} subtítulos · {len(sfx)} efectos")
for k in order:
    print(f"  {k:6} {SLOT[k][0]:6.2f} → {SLOT[k][0] + SLOT[k][1]:6.2f}")
print(" | ".join(c["text"] for c in cap))
