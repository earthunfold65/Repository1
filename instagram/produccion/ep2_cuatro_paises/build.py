#!/usr/bin/env python3
"""EP.2 (v3) La colina de los 4 países — Vaalserberg + Moresnet (EarthUnfold · Border Oddities). Genera index.html, compositions/*.html, cues.json y audio/diseno.json
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


S = {"hook": 0.0, "maze": fr(starts[2] - 0.06), "crown": fr(starts[4] - 0.06), "nonat": fr(starts[6] - 0.06),
     "casino": fr(starts[7] - 0.06), "esp": fr(starts[8] - 0.06), "what": fr(starts[9] - 0.06),
     "gone": fr(starts[10] - 0.06), "poll": fr(starts[11] - 0.06), "end": fr(starts[12] - 0.06)}
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
# ---------- 5. DOS CORONAS, UNA MINA → LA COMPARTEN (c7–c8) ----------
k = "crown"
t_king, t_zinc, t_shared = L(k, wt("kingdoms")), L(k, wt("zinc")), L(k, wt("shared"))
SCENES[k] = scene_file(k, f"""
    #cr-cam {{ position:absolute; inset:0; transform-origin: 540px 700px; }}
    .crown {{ position:absolute; top: 420px; {EMO} font-size: 190px; line-height:1; }}
    #cr-a {{ left: 150px; top: 600px; }} #cr-b {{ left: 610px; top: 600px; }}
    #cr-name {{ top: 420px; font-size: 76px; }} #cr-name span {{ color:{CYAN}; text-shadow: 0 0 40px rgba(67,217,245,.6); }}
    #cr-zn {{ position:absolute; left: 420px; top: 780px; width: 240px; height: 260px; border-radius: 22px; background:#1e2a44; border: 7px solid {CYAN};
             text-align:center; color:{INK}; font-family:'JetBrains Mono',monospace; box-shadow: 0 20px 60px rgba(0,0,0,.6); transform-origin: 120px 130px; }}
    #cr-zn b {{ display:block; font-family:'Inter Display'; font-size: 116px; line-height: 1; margin-top: 36px; color:{CYAN}; }}
    #cr-zn i {{ position:absolute; left:16px; top:10px; font-style:normal; font-size: 34px; font-weight: 800; }}
    #cr-zn u {{ display:block; text-decoration:none; font-size: 32px; font-weight:800; letter-spacing:.12em; margin-top: 10px; }}
    #cr-vs {{ position:absolute; left:0; width:1000px; top: 650px; text-align:center; {EMO} font-size: 110px; }}
    #cr-hs {{ position:absolute; left:0; width:1000px; top: 600px; text-align:center; {EMO} font-size: 300px; line-height:1; }}
    #cr-sh {{ left:0; width:1000px; top: 920px; text-align:center; border:none; background:none; padding:0; transform-origin: 500px 60px; }}
    #cr-sh span {{ display:inline-block; padding: 12px 30px; border: 7px solid {GOLD}; border-radius: 16px; color:{GOLD}; font-size: 74px; background: rgba(8,10,18,.6); }}""",
    f"""    <div id="cr-cam">
      <div id="cr-a" class="crown">👑</div><div id="cr-vs">⚔️</div><div id="cr-b" class="crown">👑</div>
      <div id="cr-zn"><i>30</i><b>Zn</b><u>ZINC MINE</u></div>
      <div id="cr-hs" style="opacity:0" data-layout-allow-overlap>🤝</div>
      <div id="cr-name" class="big">THE 4TH COUNTRY<br><span>NEUTRAL MORESNET</span></div>
      <div id="cr-sh" class="stamp"><span>SHARED IT</span></div>
    </div>""",
    f"""      tl.fromTo("#cr-cam", {{ scale: 1.08 }}, {{ scale: 1.0, duration: {SLOT[k][1]}, ease: "none" }}, 0);
      tl.fromTo("#cr-name", {{ opacity: 0, scale: 1.4 }}, {{ opacity: 1, scale: 1, duration: 0.22, ease: "power4.in" }}, 0.04);
      tl.fromTo("#cr-a", {{ x: -400, opacity: 0 }}, {{ x: 0, opacity: 1, duration: 0.3, ease: "back.out(1.8)" }}, {max(0.0, t_king - 0.25):.3f});
      tl.fromTo("#cr-b", {{ x: 400, opacity: 0 }}, {{ x: 0, opacity: 1, duration: 0.3, ease: "back.out(1.8)" }}, {max(0.0, t_king - 0.25):.3f});
      tl.fromTo("#cr-vs", {{ opacity: 0, scale: 0.4 }}, {{ opacity: 1, scale: 1, duration: 0.2, ease: "back.out(3)" }}, {t_king + 0.1:.3f});
      tl.fromTo("#cr-a", {{ rotation: -6 }}, {{ rotation: 6, duration: 0.18, yoyo: true, repeat: 7, ease: "sine.inOut" }}, {t_king + 0.3:.3f});
      tl.fromTo("#cr-b", {{ rotation: 6 }}, {{ rotation: -6, duration: 0.18, yoyo: true, repeat: 7, ease: "sine.inOut" }}, {t_king + 0.3:.3f});
      tl.fromTo("#cr-zn", {{ opacity: 0, scale: 0.3, rotation: 20 }}, {{ opacity: 1, scale: 1, rotation: 0, duration: 0.3, ease: "back.out(2.4)" }}, {t_zinc - 0.15:.3f});
      // "So they just... shared it."
      tl.to("#cr-vs, #cr-a, #cr-b, #cr-zn", {{ opacity: 0, scale: 0.6, duration: 0.2 }}, {t_shared - 0.45:.3f});
      tl.fromTo("#cr-hs", {{ opacity: 0, scale: 0.3, rotation: -15 }}, {{ opacity: 1, scale: 1, rotation: 0, duration: 0.3, ease: "back.out(2.6)" }}, {t_shared - 0.3:.3f});
      tl.fromTo("#cr-sh", {{ opacity: 0, scale: 1.7, rotation: -10 }}, {{ opacity: 1, scale: 1, rotation: -4, duration: 0.16, ease: "power4.in" }}, {t_shared:.3f});""")
cues += [{"t": round(S[k] + 0.26, 3), "kind": "stamp", "label": "título NEUTRAL MORESNET"},
         {"t": round(S[k] + max(0.0, t_king - 0.25) + 0.25, 3), "kind": "whoosh", "label": "entran las coronas (pico)"},
         {"t": round(S[k] + t_zinc + 0.1, 3), "kind": "pop", "label": "ficha Zn"},
         {"t": round(S[k] + t_shared + 0.16, 3), "kind": "stamp", "label": "sello SHARED IT"}]

# ---------- 8. 1920: SE LO DAN A BÉLGICA. GONE. (c11) ----------
k = "gone"
t_tw, t_bel, t_gone = L(k, wt("1920...")), L(k, wt("Belgium.", 2)), L(k, wt("Gone."))
assert min(t_tw, t_bel, t_gone) > 0, "palabra fuera de la escena gone"
SCENES[k] = scene_file(k, f"""
    #gn-cam {{ position:absolute; inset:0; transform-origin: 540px 700px; }}
    #gn-ww {{ top: 430px; font-size: 104px; color:{RED}; }} #gn-ww .e {{ font-family:'Noto Color Emoji'; font-size: 150px; }}
    #gn-yr {{ position:absolute; left:0; width:1000px; top: 372px; text-align:center; font-weight:900; font-size: 150px; color:{INK}; line-height: 1; }}
    #gn-map {{ opacity: 0; position:absolute; left: 240px; top: 560px; width: 600px; height: 420px; }}
    #gn-st {{ left:0; width:1000px; top: 760px; text-align:center; border:none; background:none; padding:0; transform-origin: 500px 60px; }}
    #gn-st span {{ display:inline-block; padding: 14px 34px; border: 8px solid {RED}; border-radius: 18px; color:{RED}; font-size: 110px; background: rgba(8,10,18,.7); }}""",
    f"""    <div id="gn-cam">
      <div id="gn-yr">1920</div>
      <div id="gn-ww" class="big" data-layout-allow-overlap><span class="e">⚔️</span><br>WORLD WAR I</div>
      <svg id="gn-map" viewBox="0 0 600 420">
        <path id="gn-be" d="M40,120 L560,80 L520,380 L70,360 Z" fill="rgba(255,200,61,.75)" stroke="#0b1020" stroke-width="6"/>
        <text x="300" y="300" text-anchor="middle" font-family="Inter Display" font-weight="900" font-size="56" fill="#0b1020">BELGIUM</text>
        <path id="gn-tri" d="M250,90 L370,110 L300,200 Z" fill="{CYAN}" stroke="#fff" stroke-width="5" style="transform-origin:306px 133px"/>
      </svg>
      <div id="gn-st" class="stamp" data-layout-allow-overlap><span>GONE</span></div>
    </div>""",
    f"""      tl.fromTo("#gn-cam", {{ scale: 1.0 }}, {{ scale: 1.12, duration: {SLOT[k][1]}, ease: "none" }}, 0);
      tl.fromTo("#gn-ww", {{ opacity: 0, scale: 1.5 }}, {{ opacity: 1, scale: 1, duration: 0.2, ease: "power4.in" }}, 0.03);
      tl.to("#gn-ww", {{ opacity: 0, scale: 0.8, duration: 0.15 }}, {max(0.45, t_tw - 0.15):.3f});
      tl.fromTo("#gn-yr", {{ opacity: 0, scale: 1.6 }}, {{ opacity: 1, scale: 1, duration: 0.2, ease: "power4.in" }}, {max(0.02, t_tw - 0.2):.3f});
      tl.fromTo("#gn-map", {{ opacity: 0, y: 40 }}, {{ opacity: 1, y: 0, duration: 0.3 }}, {max(0.5, t_tw):.3f});
      tl.to("#gn-tri", {{ fill: "{GOLD}", y: 60, scale: 0.85, duration: 0.5, ease: "power2.inOut" }}, {t_bel - 0.3:.3f});
      tl.to("#gn-tri", {{ opacity: 0, duration: 0.3 }}, {t_bel + 0.25:.3f});
      tl.fromTo("#gn-st", {{ opacity: 0, scale: 2, rotation: -16 }}, {{ opacity: 1, scale: 1, rotation: -6, duration: 0.16, ease: "power4.in" }}, {t_gone - 0.12:.3f});
      tl.to("#gn-cam", {{ x: 16, duration: 0.05, yoyo: true, repeat: 5, ease: "none" }}, {t_gone + 0.05:.3f});""")
cues += [{"t": round(S[k] + 0.23, 3), "kind": "hit", "label": "WORLD WAR I"},
         {"t": round(S[k] + max(0.02, t_tw - 0.2) + 0.2, 3), "kind": "thunk", "label": "1920"},
         {"t": round(S[k] + t_gone + 0.04, 3), "kind": "hit", "label": "GONE + sacudida"}]

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
cues += [{"t": round(S[k] + 0.02, 3), "kind": "whoosh_soft", "label": "entra la tarjeta final"}]

# ---------- HOOK: la colina de 3 países… que fueron 4 (c0–c1) ----------
k = "hook"
t_but, t_four, t_ins = L(k, starts[1]), L(k, wt("four...")), L(k, wt("insane."))
SCENES[k] = scene_file(k, f"""
    #hk-cam {{ position:absolute; inset:0; transform-origin: 540px 760px; }}
    #hk-hill {{ position:absolute; left:0; top:820px; width:1080px; height:280px; }}
    #hk-pie3, #hk-pie4 {{ position:absolute; left:330px; top:575px; width:420px; height:420px; transform-origin: 210px 210px; }}
    #hk-glow {{ position:absolute; left:240px; top:470px; width:600px; height:600px; border-radius:50%;
               background: radial-gradient(closest-side, rgba(255,200,61,.35), rgba(0,0,0,0)); }}
    .ttl {{ top: 350px; font-size: 96px; }}
    .ttl .g {{ color:{GOLD}; }} .ttl .c {{ color:{CYAN}; }}
    #hk-mind {{ position:absolute; left: 700px; top: 520px; {EMO} font-size: 150px; line-height: 1; }}""",
    f"""    <div id="hk-cam">
      <div id="hk-glow"></div>
      <svg id="hk-hill" viewBox="0 0 1080 280"><path d="M0,280 L0,200 C200,170 360,70 480,40 C520,30 560,30 600,40 C720,70 880,170 1080,190 L1080,280 Z" fill="#1b2438" stroke="#3a4766" stroke-width="5"/></svg>
      <div id="hk-pie3">{pie_svg("hk-p3", P3, r=190, size=420, fs=38)}</div>
      <div id="hk-pie4" style="opacity:0">{pie_svg("hk-p4", P4, r=190, size=420, fs=38)}</div>
      <div id="hk-mind" style="opacity:0">🤯</div>
    </div>
    <div id="hk-t1" class="big ttl">3 COUNTRIES<br><span class="g">1 HILL</span></div>
    <div id="hk-t2" class="big ttl" style="opacity:0">IT USED TO BE<br><span class="c">4 COUNTRIES</span></div>""",
    f"""      tl.fromTo("#hk-cam", {{ scale: 1.14 }}, {{ scale: 1, duration: 0.35, ease: "power3.out" }}, 0);
      tl.to("#hk-cam", {{ scale: 1.1, duration: {SLOT[k][1] - 0.35:.3f}, ease: "none" }}, 0.35);
      tl.fromTo("#hk-t1", {{ scale: 1.12 }}, {{ scale: 1, duration: 0.3, ease: "power3.out" }}, 0);
      tl.fromTo("#hk-pie3", {{ rotation: -10 }}, {{ rotation: 0, duration: {t_but:.3f}, ease: "none" }}, 0);
      tl.to("#hk-pie3", {{ opacity: 0, rotation: 25, duration: 0.25, ease: "power2.in" }}, {t_but:.3f});
      tl.fromTo("#hk-pie4", {{ opacity: 0, rotation: -25, scale: 0.9 }}, {{ opacity: 1, rotation: 0, scale: 1, duration: 0.4, ease: "back.out(1.7)" }}, {t_but + 0.1:.3f});
      tl.to("#hk-pie4", {{ rotation: 12, duration: {max(0.3, SLOT[k][1] - t_but - 0.5):.3f}, ease: "none" }}, {t_but + 0.5:.3f});
      tl.to("#hk-t1", {{ opacity: 0, y: -30, duration: 0.18 }}, {t_but:.3f});
      tl.fromTo("#hk-t2", {{ opacity: 0, y: 30 }}, {{ opacity: 1, y: 0, duration: 0.22, ease: "power3.out" }}, {t_but + 0.12:.3f});
      tl.fromTo("#hk-p4-q", {{ scale: 1 }}, {{ scale: 1.2, duration: 0.16, yoyo: true, repeat: 3, ease: "power1.inOut" }}, {t_four:.3f});
      tl.fromTo("#hk-mind", {{ opacity: 0, scale: 0.3, rotation: -20 }}, {{ opacity: 1, scale: 1, rotation: 0, duration: 0.25, ease: "back.out(3)" }}, {t_ins - 0.1:.3f});""")
cues += [{"t": 0.03, "kind": "hit_soft", "label": "gancho frame 0"},
         {"t": round(starts[1] + 0.3, 3), "kind": "whoosh", "label": "3 → 4 cuñas (pico)"},
         {"t": round(wt("four...") + 0.03, 3), "kind": "pop", "label": "hueco del 4.º país"},
         {"t": round(wt("insane.") - 0.05, 3), "kind": "hit", "label": "🤯 insane"}]

# ---------- FACT 1: el laberinto en 3 países (c2–c3) ----------
k = "maze"
t_lost, t_maze = L(k, wt("lost")), L(k, wt("maze"))
g = random.Random(11)
N, CELL, X0, Y0 = 9, 58, 279, 445
walls = {(x, y, d) for x in range(N) for y in range(N) for d in "RD"}
seen, stack = {(0, 0)}, [(0, 0)]
while stack:
    x, y = stack[-1]
    nb = [(x + dx, y + dy, dx, dy) for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)) if 0 <= x + dx < N and 0 <= y + dy < N and (x + dx, y + dy) not in seen]
    if not nb:
        stack.pop()
        continue
    nx, ny, dx, dy = g.choice(nb)
    if dx == 1: walls.discard((x, y, "R"))
    if dx == -1: walls.discard((nx, ny, "R"))
    if dy == 1: walls.discard((x, y, "D"))
    if dy == -1: walls.discard((nx, ny, "D"))
    seen.add((nx, ny)); stack.append((nx, ny))
segs = []
for (x, y, d) in walls:
    if d == "R" and x < N - 1:
        segs.append(f"M{X0 + (x + 1) * CELL},{Y0 + y * CELL} v{CELL}")
    if d == "D" and y < N - 1:
        segs.append(f"M{X0 + x * CELL},{Y0 + (y + 1) * CELL} h{CELL}")
W_ = N * CELL
maze_path = " ".join(segs) + f" M{X0},{Y0} h{W_} v{W_} h{-W_} Z"
cx, cy = X0 + W_ / 2, Y0 + W_ / 2
SCENES[k] = scene_file(k, f"""
    #mz-cam {{ position:absolute; inset:0; transform-origin: {cx:.0f}px {cy:.0f}px; }}
    #mz-svg {{ position:absolute; left:0; top:0; width:1080px; height:1100px; }}
    #mz-tag {{ left:0; width:1000px; top: 1090px; text-align:center; background:none; color:{INK}; font-size: 30px; display:none; }}
    #mz-me {{ position:absolute; left: {X0 + 8}px; top: {Y0 + 6}px; {EMO} font-size: 52px; line-height:1; }}
    #mz-lbl {{ left:0; width:1000px; top: 1000px; font-size: 30px; text-align:center; background:none; color:{GOLD}; font-size: 34px; }}
    #mz-lbl span {{ background: rgba(8,10,18,.88); padding: 10px 22px; border-radius: 12px; border: 3px solid rgba(255,200,61,.6); }}""",
    f"""    <div id="mz-cam">
      <svg id="mz-svg" viewBox="0 0 1080 1100" data-layout-allow-overlap>
        <path d="{wedge(cx, cy, 460, 270, 390)}" fill="rgba(255,122,26,.22)" clip-path="url(#mzc)"/>
        <path d="{wedge(cx, cy, 460, 30, 150)}" fill="rgba(255,77,94,.22)" clip-path="url(#mzc)"/>
        <path d="{wedge(cx, cy, 460, 150, 270)}" fill="rgba(255,200,61,.22)" clip-path="url(#mzc)"/>
        <clipPath id="mzc"><rect x="{X0}" y="{Y0}" width="{W_}" height="{W_}"/></clipPath>
        <path id="mz-walls" d="{maze_path}" stroke="#3fae5a" stroke-width="14" stroke-linecap="round" fill="none"/>
        <text x="{cx - 170:.0f}" y="{Y0 + 70}" font-family="Inter Display" font-weight="900" font-size="46" fill="{ORANGE}">NL</text>
        <text x="{cx + 140:.0f}" y="{cy + 60:.0f}" font-family="Inter Display" font-weight="900" font-size="46" fill="{RED}">DE</text>
        <text x="{cx - 230:.0f}" y="{Y0 + W_ - 40}" font-family="Inter Display" font-weight="900" font-size="46" fill="{GOLD}">BE</text>
      </svg>
      <div id="mz-me">🧍</div>
    </div>
    <div id="mz-lbl" class="tag"><span>EUROPE'S BIGGEST OUTDOOR HEDGE MAZE</span></div>""",
    f"""      tl.fromTo("#mz-cam", {{ scale: 0.6, rotation: -8, opacity: 0 }}, {{ scale: 1, rotation: 0, opacity: 1, duration: 0.45, ease: "back.out(1.5)" }}, 0);
      tl.to("#mz-cam", {{ scale: 1.12, rotation: 3, duration: {SLOT[k][1] - 0.45:.3f}, ease: "none" }}, 0.45);
      tl.fromTo("#mz-me", {{ x: 0, y: 0 }}, {{ x: {W_ / 2 - 40:.0f}, y: {W_ / 2 - 30:.0f}, duration: {max(0.8, t_maze - t_lost):.3f}, ease: "steps(8)" }}, {t_lost:.3f});
      tl.fromTo("#mz-lbl", {{ opacity: 0, y: 20 }}, {{ opacity: 1, y: 0, duration: 0.25, ease: "back.out(2)" }}, {t_maze - 0.6:.3f});""")
cues += [{"t": round(S[k] + 0.12, 3), "kind": "whoosh2", "label": "entra el laberinto (pico)"},
         {"t": round(S[k] + t_maze - 0.6 + 0.05, 3), "kind": "pop", "pitch": 2, "label": "etiqueta laberinto"}]

# ---------- FACT 3: sin nacionalidad, sin ejército (c6) ----------
k = "nonat"
t_nat, t_army = L(k, wt("nationality.")), L(k, wt("army."))
SCENES[k] = scene_file(k, f"""
    #nn-cam {{ position:absolute; inset:0; transform-origin: 540px 700px; }}
    #nn-pass {{ position:absolute; left: 190px; top: 450px; width: 700px; height: 440px; border-radius: 26px; background: linear-gradient(160deg,#1f3b6e,#142647);
               border: 6px solid #c9a646; box-shadow: 0 30px 70px rgba(0,0,0,.6); color: #e9d9a6; font-family:'JetBrains Mono',monospace; transform-origin: 350px 220px; }}
    #nn-pass h3 {{ font-family:'Inter Display'; font-weight:900; font-size: 46px; letter-spacing:.12em; text-align:center; margin-top: 30px; }}
    #nn-pass p {{ font-size: 34px; font-weight: 800; margin: 26px 0 0 50px; }}
    #nn-pass b {{ color:#fff; }}
    #nn-none {{ left: 380px; top: 640px; border-color: {RED}; color: {RED}; font-size: 80px; transform-origin: 160px 50px; }}
    #nn-army {{ position:absolute; left: 0; width: 1000px; top: 930px; text-align:center; {EMO} font-size: 110px; line-height:1; }}""",
    f"""    <div id="nn-cam">
      <div id="nn-pass"><h3>PASSPORT</h3><p>STATE: <b>NEUTRAL MORESNET</b></p><p>NATIONALITY: <b>_______</b></p><p>ARMY: <b>_______</b></p></div>
      <div id="nn-none" class="stamp" data-layout-allow-overlap>NONE</div>
      <div id="nn-army">🪖🚫</div>
    </div>""",
    f"""      tl.fromTo("#nn-cam", {{ scale: 1.08 }}, {{ scale: 1.0, duration: {SLOT[k][1]}, ease: "none" }}, 0);
      tl.fromTo("#nn-pass", {{ opacity: 0, y: 160, rotation: 6 }}, {{ opacity: 1, y: 0, rotation: -2, duration: 0.4, ease: "back.out(1.6)" }}, 0.02);
      tl.fromTo("#nn-none", {{ opacity: 0, scale: 2.2, rotation: -20 }}, {{ opacity: 1, scale: 1, rotation: -10, duration: 0.16, ease: "power4.in" }}, {t_nat - 0.1:.3f});
      tl.to("#nn-cam", {{ x: 14, duration: 0.05, yoyo: true, repeat: 3, ease: "none" }}, {t_nat + 0.07:.3f});
      tl.fromTo("#nn-army", {{ opacity: 0, scale: 0.4 }}, {{ opacity: 1, scale: 1, duration: 0.25, ease: "back.out(2.6)" }}, {t_army - 0.15:.3f});""")
cues += [{"t": round(S[k] + 0.2, 3), "kind": "thunk", "pitch": 2, "label": "cae el pasaporte"},
         {"t": round(S[k] + t_nat + 0.06, 3), "kind": "stamp", "label": "sello NONE"},
         {"t": round(S[k] + t_army - 0.05, 3), "kind": "pop", "pitch": -2, "label": "sin ejército"}]

# ---------- FACT 4: el casino de la noche a la mañana (c7) ----------
k = "casino"
t_ban, t_cas, t_night = L(k, wt("banned")), L(k, wt("casino.")), L(k, wt("overnight."))
SCENES[k] = scene_file(k, f"""
    #cs-cam {{ position:absolute; inset:0; transform-origin: 540px 700px; }}
    #cs-slot {{ position:absolute; left:0; width:1000px; top: 470px; text-align:center; {EMO} font-size: 260px; line-height:1; }}
    #cs-ban {{ left: 190px; top: 450px; border-color: {RED}; color: {RED}; font-size: 60px; transform-origin: 300px 50px; }}
    #cs-open {{ position:absolute; left: 250px; top: 780px; width: 520px; height: 150px; border-radius: 30px; border: 8px solid #ff3fd1; color:#ffd6f6;
               text-align:center; font-weight:900; font-size: 96px; line-height: 134px; text-shadow: 0 0 22px #ff3fd1, 0 0 44px #ff3fd1;
               box-shadow: 0 0 40px rgba(255,63,209,.6), inset 0 0 30px rgba(255,63,209,.4); background: rgba(20,4,24,.8); transform-origin: 260px 75px; }}
    #cs-clock {{ position:absolute; left: 790px; top: 820px; {EMO} font-size: 80px; transform-origin: 40px 40px; }}""",
    f"""    <div id="cs-cam">
      <div id="cs-slot">🎰</div>
      <div id="cs-ban" class="stamp" data-layout-allow-overlap>🇧🇪 GAMBLING BANNED</div>
      <div id="cs-open">OPEN!</div>
      <div id="cs-clock">⏰</div>
    </div>""",
    f"""      tl.fromTo("#cs-cam", {{ scale: 1.0 }}, {{ scale: 1.1, duration: {SLOT[k][1]}, ease: "none" }}, 0);
      tl.fromTo("#cs-slot", {{ opacity: 0.25, scale: 0.85 }}, {{ opacity: 0.25, scale: 0.85, duration: 0.01 }}, 0);
      tl.fromTo("#cs-ban", {{ opacity: 0, scale: 2, rotation: -16 }}, {{ opacity: 1, scale: 1, rotation: -7, duration: 0.16, ease: "power4.in" }}, {t_ban - 0.1:.3f});
      tl.to("#cs-ban", {{ opacity: 0, scale: 0.7, duration: 0.2 }}, {t_cas - 0.45:.3f});
      tl.to("#cs-slot", {{ opacity: 1, scale: 1.08, duration: 0.25, ease: "back.out(2.5)" }}, {t_cas - 0.3:.3f});
      tl.fromTo("#cs-open", {{ opacity: 0, scale: 0.5 }}, {{ opacity: 1, scale: 1, duration: 0.22, ease: "back.out(3)" }}, {t_cas - 0.15:.3f});
      tl.to("#cs-open", {{ opacity: 0.55, duration: 0.07, yoyo: true, repeat: 5, ease: "none" }}, {t_cas + 0.15:.3f});
      tl.fromTo("#cs-clock", {{ opacity: 0, rotation: 0 }}, {{ opacity: 1, rotation: 720, duration: 0.6, ease: "power2.out" }}, {t_night - 0.3:.3f});
      tl.to("#cs-slot", {{ rotation: 4, duration: 0.12, yoyo: true, repeat: 5, ease: "sine.inOut" }}, {t_cas:.3f});""")
cues += [{"t": round(S[k] + t_ban + 0.06, 3), "kind": "stamp", "label": "sello GAMBLING BANNED"},
         {"t": round(S[k] + t_cas - 0.15 + 0.05, 3), "kind": "hit", "label": "OPEN! casino"},
         {"t": round(S[k] + t_night - 0.25, 3), "kind": "whoosh_soft", "label": "reloj gira (pico)"}]

# ---------- FACT 5: capital mundial del esperanto (c8) ----------
k = "esp"
t_1908, t_cap, t_esp = L(k, wt("1908,")), L(k, wt("capital")), L(k, wt("Esperanto."))
SCENES[k] = scene_file(k, f"""
    #es-cam {{ position:absolute; inset:0; transform-origin: 540px 700px; }}
    #es-flag {{ position:absolute; left: 330px; top: 560px; width: 420px; height: 280px; background:#1f9d55; border-radius: 14px; box-shadow: 0 20px 60px rgba(0,0,0,.5); transform-origin: 210px 140px; }}
    #es-flag i {{ position:absolute; left:0; top:0; width:140px; height:140px; background:#fff; border-radius: 14px 0 0 0; color:#1f9d55; font-style:normal; font-size: 110px; line-height:140px; text-align:center; }}
    #es-crown {{ position:absolute; left:0; width:1000px; top: 420px; text-align:center; {EMO} font-size: 120px; line-height:1; }}
    #es-yr {{ left:0; width:1000px; top: 865px; text-align:center; background:none; color:{GOLD}; font-size: 40px; }}
    #es-yr span {{ background: rgba(8,10,18,.88); padding: 10px 22px; border-radius: 12px; }}
    #es-st {{ left:0; width:1000px; top: 945px; text-align:center; border:none; background:none; padding:0; transform-origin: 500px 60px; }}
    #es-st span {{ display:inline-block; padding: 12px 26px; border: 7px solid #34d399; border-radius: 16px; color:#34d399; background: rgba(8,10,18,.7); font-size: 44px; }}
    #es-bub {{ position:absolute; left: 660px; top: 540px; padding: 16px 22px; border-radius: 30px; background:#fff; color:#0b1020; font-weight:900; font-size: 40px; transform-origin: 0 100%; }}""",
    f"""    <div id="es-cam">
      <div id="es-crown" style="opacity:0" data-layout-allow-overlap>👑</div>
      <div id="es-flag"><i>★</i></div>
      <div id="es-bub">Saluton!</div>
      <div id="es-yr" class="tag"><span>1908</span></div>
      <div id="es-st" class="stamp"><span>WORLD CAPITAL OF ESPERANTO</span></div>
    </div>""",
    f"""      tl.fromTo("#es-cam", {{ scale: 1.0 }}, {{ scale: 1.1, duration: {SLOT[k][1]}, ease: "none" }}, 0);
      tl.fromTo("#es-flag", {{ opacity: 0, y: -200, rotation: -8 }}, {{ opacity: 1, y: 0, rotation: 0, duration: 0.35, ease: "back.out(1.8)" }}, 0.02);
      tl.fromTo("#es-bub", {{ opacity: 0, scale: 0.3 }}, {{ opacity: 1, scale: 1, duration: 0.22, ease: "back.out(2.6)" }}, 0.5);
      tl.fromTo("#es-yr", {{ opacity: 0, scale: 0.6 }}, {{ opacity: 1, scale: 1, duration: 0.2, ease: "back.out(2.5)" }}, {t_1908 - 0.1:.3f});
      tl.fromTo("#es-crown", {{ opacity: 0, y: -80 }}, {{ opacity: 1, y: 0, duration: 0.3, ease: "bounce.out" }}, {t_cap - 0.2:.3f});
      tl.fromTo("#es-st", {{ opacity: 0, scale: 1.7, rotation: -10 }}, {{ opacity: 1, scale: 1, rotation: -3, duration: 0.16, ease: "power4.in" }}, {t_esp - 0.25:.3f});""")
cues += [{"t": round(S[k] + 0.3, 3), "kind": "thunk", "pitch": 3, "label": "cae la bandera"},
         {"t": round(S[k] + t_cap - 0.05, 3), "kind": "pop", "pitch": 4, "label": "corona"},
         {"t": round(S[k] + t_esp - 0.09, 3), "kind": "stamp", "label": "sello WORLD CAPITAL"}]

# ---------- ¿QUÉ PASÓ? (c9) ----------
k = "what"
SCENES[k] = scene_file(k, f"""
    #wh-cam {{ position:absolute; inset:0; transform-origin: 540px 700px; }}
    #wh-q {{ position:absolute; left:0; width:1000px; top: 430px; text-align:center; font-size: 420px; font-weight: 900; line-height:1; color:{GOLD}; text-shadow: 0 0 60px rgba(255,200,61,.6); }}
    #wh-tri {{ position:absolute; left: 430px; top: 520px; width: 220px; height: 200px; }}""",
    f"""    <div id="wh-cam"><div id="wh-q">?</div></div>""",
    f"""      tl.fromTo("#wh-cam", {{ scale: 1.25 }}, {{ scale: 1.0, duration: {SLOT[k][1]}, ease: "power2.out" }}, 0);
      tl.fromTo("#wh-q", {{ opacity: 0, rotation: -30, scale: 0.4 }}, {{ opacity: 1, rotation: 0, scale: 1, duration: 0.35, ease: "back.out(2)" }}, 0.02);""")
cues += [{"t": round(S[k] + 0.15, 3), "kind": "whoosh2", "label": "entra la pregunta (pico)"}]

# ---------- ENCUESTA (c11) ----------
k = "poll"
btns = "".join(f'<div id="pl-b{n}" class="nb" style="left:{150 + (n - 1) * 150}px">{n}</div>' for n in range(1, 6))
SCENES[k] = scene_file(k, f"""
    #pl-q {{ top: 400px; font-size: 92px; }}
    #pl-q span {{ color:{GOLD}; }}
    .nb {{ position:absolute; top: 700px; width: 130px; height: 130px; border-radius: 26px; background:{GOLD}; color:#0b1020; font-weight:900;
          font-size: 84px; line-height: 130px; text-align:center; box-shadow: 0 16px 40px rgba(0,0,0,.5); transform-origin: 65px 65px; }}
    #pl-c {{ left:0; width:1000px; top: 900px; text-align:center; background:none; color:{INK}; font-size: 34px; }}
    #pl-c span {{ background: rgba(8,10,18,.88); padding: 10px 22px; border-radius: 12px; }}""",
    f"""    <div id="pl-q" class="big">WHICH FACT<br><span>GOT YOU?</span></div>
    {btns}
    <div id="pl-c" class="tag"><span>💬 COMMENT 1–5</span></div>""",
    f"""      tl.fromTo("#pl-q", {{ opacity: 0, y: 30 }}, {{ opacity: 1, y: 0, duration: 0.25, ease: "power3.out" }}, 0.02);
""" + "".join(f'      tl.fromTo("#pl-b{n}", {{ opacity: 0, scale: 0.3 }}, {{ opacity: 1, scale: 1, duration: 0.22, ease: "back.out(3)" }}, {0.2 + n * 0.08:.2f});\n' for n in range(1, 6))
    + f"""      tl.to("#pl-b4", {{ scale: 1.12, duration: 0.3, yoyo: true, repeat: 3, ease: "sine.inOut" }}, 0.9);
      tl.fromTo("#pl-c", {{ opacity: 0 }}, {{ opacity: 1, duration: 0.25 }}, 0.7);""")
cues += [{"t": round(S[k] + 0.3, 3), "kind": "pop", "label": "botones 1–5"}]

# ---------- contador FACT n/5 (capa superior del index) ----------
FACTS = [("maze", 1), ("crown", 2), ("nonat", 3), ("casino", 4), ("esp", 5)]
hud_html = ""
for key, n in FACTS:
    st, du = SLOT[key]
    dots = "".join(f'<i class="{"on" if j <= n else ""}"></i>' for j in range(1, 6))
    hud_html += (f'      <div id="hud{n}" class="clip hud" data-start="{st}" data-duration="{du}" data-track-index="7">'
                 f'<b>FACT {n}/5</b><span>{dots}</span></div>\n')
# ---------- captions ----------
KEY = {"three", "four", "insane", "lost", "maze", "border", "zinc", "kingdoms", "shared", "nationality", "army", "banned",
       "casino", "overnight", "1908", "capital", "esperanto", "happened", "1920", "belgium", "gone", "fact", "island", "six"}
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
      .hud {{ position:absolute; left: 0; width: {W}px; top: 342px; text-align:center; z-index: 61; }}
      .hud b {{ display:inline-block; font-family:'Inter Display'; font-weight: 900; font-size: 40px; color:#0b1020; background:{GOLD}; padding: 4px 18px; border-radius: 10px; vertical-align: middle; }}
      .hud span {{ display:inline-block; margin-left: 16px; vertical-align: middle; }}
      .hud i {{ display:inline-block; width: 18px; height: 18px; border-radius: 50%; margin: 0 5px; background: rgba(255,255,255,.25); }}
      .hud i.on {{ background:{GOLD}; box-shadow: 0 0 12px {GOLD}; }}
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
{hud_html}      <div id="vignette" class="clip" data-start="0" data-duration="{DUR}" data-track-index="4" data-layout-ignore></div>
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
SFX = {   # elegidos y ajustados con earshot (ver out/oido/INFORME_OIDO.md)
    "whoosh": (f"{LIBR}/whoosh/fs-60007_swipe-whoosh.mp3", "peak", -11),
    "whoosh2": (f"{LIBR}/whoosh/fs-539172_melee-combat-whoosh.mp3", "peak", -13),
    "whoosh_soft": (f"{LIBR}/whoosh/fs-60007_swipe-whoosh.mp3", "peak", -10),
    "click": (f"{LIBR}/click/uisfx_soft_select.mp3", "peak", -9),
    "tick": (f"{LIBR}/pop/earshot_ui_pop_step.wav", "attack", -8),
    "pop": (f"{LIBR}/pop/earshot_ui_pop_wide.wav", "attack", -8),
    "stamp": (f"{LIBR}/stamp/fs-362624_stamp.mp3", "attack", -10),
    "thunk": (f"{LIBR}/stamp/fs-347325_thick-stamp-nosub-wav.mp3", "attack", -14),
    "hit": (f"{LIBR}/hit/fs-377303_deep-cinematic-impact.mp3", "attack", -8),
    "hit_soft": (f"{LIBR}/hit/fs-377303_deep-cinematic-impact.mp3", "attack", -13),
    "sub": (f"{LIBR}/sub/earshot_cut_hit_punch.wav", "attack", -7),
}
# correcciones de sincronía medidas con earshot (s): el impacto se percibía ~55 ms antes
OFFSET = {"hit": 0.05, "sub": 0.05}
sfx = []
# capa grave bajo cada golpe grande (earshot: "thin bottom")
GRAVE = ("REAL", "SHARED IT", "1920")
cues += [{"t": c["t"], "kind": "sub", "label": c["label"] + " · capa grave"} for c in list(cues)
         if c["kind"] == "hit" or any(g in c["label"] for g in GRAVE)]
for c in sorted(cues, key=lambda c: c["t"]):
    f, a, gdb = SFX[c["kind"]]
    it = {"file": f, "t": fr(c["t"] + OFFSET.get(c["kind"], 0)), "anchor": a, "gain_db": gdb + c.get("gain", 0), "label": c["label"]}
    if c.get("pitch"):
        it["pitch"] = c["pitch"]
    sfx.append(it)
diseno = {
    "duracion": DUR, "fps": FPS,
    "voz": {"file": "vo.wav", "gain_db": 0, "t": 0, "eq": [["peak", 2500, -2.5, 1.0]]},
    # bucle de misterio de nivel constante (LRA 2 LU) + ducking suave: sin "respiraciones"
    "musica": {"file": f"{LIBR}/musica/fs-446745_dilemma-2a-mystery-music-loop.mp3", "gain_db": -12, "duck_db": 5,
               "loop": True, "offset": 0.0, "eq": [["low", 55, 7], ["low", 120, 2]], "fade_in": 0.05, "fade_out": 1.2,
               "rides": [[S["gone"] - 0.05, 0], [S["gone"] + 0.25, -9], [S["poll"] - 0.2, -9], [S["poll"] + 0.3, 0]]},
    "sfx": sfx,
    "master": {"lufs": -14, "tp": -1.5, "tp_aac": -1.0},
    "salida": "out/audio.wav",
    "video": "../out/ep2_silent.mp4", "video_salida": "../out/EP2_CON_MUSICA.mp4",
}
json.dump(diseno, open(os.path.join(HERE, "audio/diseno.json"), "w"), indent=1, ensure_ascii=False)
# versión SIN música: para añadir el audio en tendencia dentro de Instagram / TikTok / Shorts / Facebook
sin = {k2: v2 for k2, v2 in diseno.items() if k2 != "musica"}
sin.update(salida="out/audio_sin_musica.wav", video_salida="../out/EP2_SIN_MUSICA.mp4")
json.dump(sin, open(os.path.join(HERE, "audio/diseno_sin_musica.json"), "w"), indent=1, ensure_ascii=False)
json.dump({"scenes": SLOT, "cues": cues, "captions": [{k: c[k] for k in ("id", "start", "end", "text")} for c in cap], "duration": DUR},
          open(os.path.join(HERE, "cues.json"), "w"), indent=1, ensure_ascii=False)
print(f"duración {DUR} s · {len(cap)} subtítulos · {len(sfx)} efectos")
for k in order:
    print(f"  {k:6} {SLOT[k][0]:6.2f} → {SLOT[k][0] + SLOT[k][1]:6.2f}")
print(" | ".join(c["text"] for c in cap))
