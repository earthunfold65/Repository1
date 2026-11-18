#!/usr/bin/env python3
"""EP.2 Vaalserberg (EarthUnfold · Border Oddities). Genera index.html, compositions/*.html, cues.json y audio/diseno.json
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
for text, _ in chunks:
    starts.append(words[i]["start"])
    i += len(text.split())
END_VO = words[-1]["end"]
DUR = round(END_VO + 1.25, 2)


def fr(t):
    return round(round(t * FPS) / FPS, 4)


S = {"hook": 0.0, "hill": fr(starts[4] - 0.08), "mor": fr(starts[6] - 0.08), "esp": fr(starts[9] - 0.08),
     "erase": fr(starts[10] - 0.08), "save": fr(starts[12] - 0.08), "end": fr(starts[14] - 0.08)}
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

# ---------- 1. HOOK (0 → c4) ----------
h = "hook"
t_but, t_four, t_and = L(h, starts[1]), L(h, wt("four.")), L(h, starts[3])
t_exist = L(h, wt("exist"))
s_hook = scene_file(h, f"""
    #hk-cam {{ position:absolute; inset:0; transform-origin: 540px 760px; }}
    #hk-pie3, #hk-pie4 {{ position:absolute; left:310px; top:590px; width:460px; height:460px; transform-origin: 230px 230px; }}
    #hk-glow {{ position:absolute; left:240px; top:520px; width:600px; height:600px; border-radius:50%;
               background: radial-gradient(closest-side, rgba(255,200,61,.35), rgba(0,0,0,0)); }}
    .ttl {{ top: 350px; font-size: 100px; }}
    .ttl .g {{ color:{GOLD}; }} .ttl .c {{ color:{CYAN}; }}
    #hk-cnt {{ left: 610px; top: 380px; color:{CYAN}; font-size: 34px; display:none; }}""",
    f"""    <div id="hk-cam">
      <div id="hk-glow"></div>
      <div id="hk-pie3">{pie_svg("hk-p3", P3, r=210, size=460, fs=40)}</div>
      <div id="hk-pie4" style="opacity:0">{pie_svg("hk-p4", P4, r=210, size=460, fs=40)}</div>
    </div>
    <div id="hk-t1" class="big ttl">3 COUNTRIES<br><span class="g">1 SPOT</span></div>
    <div id="hk-t2" class="big ttl" style="opacity:0">ONCE IT WAS<br><span class="c">4 COUNTRIES</span></div>
    <div id="hk-t3" class="big ttl" style="opacity:0">ONE OF THEM<br><span class="c">VANISHED</span></div>""",
    f"""      tl.fromTo("#hk-cam", {{ scale: 1.16 }}, {{ scale: 1, duration: 0.4, ease: "power3.out" }}, 0);
      tl.to("#hk-cam", {{ scale: 1.06, duration: {SLOT[h][1] - 0.4:.3f}, ease: "none" }}, 0.4);
      tl.fromTo("#hk-pie3", {{ rotation: -8 }}, {{ rotation: 0, duration: {t_but:.3f}, ease: "none" }}, 0);
      // "But for almost a hundred years... it was in four"
      tl.to("#hk-pie3", {{ opacity: 0, rotation: 25, duration: 0.3, ease: "power2.in" }}, {t_but:.3f});
      tl.fromTo("#hk-pie4", {{ opacity: 0, rotation: -25, scale: 0.9 }}, {{ opacity: 1, rotation: 0, scale: 1, duration: 0.45, ease: "back.out(1.6)" }}, {t_but + 0.15:.3f});
      tl.to("#hk-t1", {{ opacity: 0, y: -30, duration: 0.2 }}, {t_but:.3f});
      tl.fromTo("#hk-t2", {{ opacity: 0, y: 30 }}, {{ opacity: 1, y: 0, duration: 0.25, ease: "power3.out" }}, {t_but + 0.15:.3f});
      tl.fromTo("#hk-p4-q", {{ scale: 1 }}, {{ scale: 1.18, duration: 0.18, yoyo: true, repeat: 3, ease: "power1.inOut" }}, {t_four:.3f});
      // "that fourth country doesn't exist anymore": parpadea
      tl.to("#hk-t2", {{ opacity: 0, y: -30, duration: 0.2 }}, {t_and:.3f});
      tl.fromTo("#hk-t3", {{ opacity: 0, y: 30 }}, {{ opacity: 1, y: 0, duration: 0.25, ease: "power3.out" }}, {t_and + 0.1:.3f});
      tl.to("#hk-p4-q, #hk-p4-t-q", {{ opacity: 0.1, duration: 0.07, yoyo: true, repeat: 5, ease: "none" }}, {t_exist:.3f});""")
cues += [{"t": 0.03, "kind": "hit_soft", "label": "golpe en el fotograma 0 (gancho)"},
         {"t": round(starts[1] + 0.35, 3), "kind": "whoosh", "label": "3 → 4 cuñas (pico)"},
         {"t": round(wt("four.") + 0.02, 3), "kind": "click", "label": "aparece el 4.º hueco"}]

# ---------- 2. COLINA (c4 → c6) ----------
g = "hill"
tn, tb, tg = L(g, wt("Netherlands,")), L(g, wt("Belgium")), L(g, wt("Germany"))
s_hill = scene_file(g, f"""
    #hl-cam {{ position:absolute; inset:0; transform-origin: 540px 800px; }}
    #hl-hill {{ position:absolute; left:0; top:560px; width:1080px; height:480px; }}
    #hl-pin {{ position:absolute; left:430px; top:600px; width:220px; height:220px; transform-origin:110px 110px; }}
    #hl-name {{ left: 0; width: 1080px; top: 470px; text-align:center; background:none; color:{INK}; font-size: 40px; }}
    #hl-name span {{ background: rgba(8,10,18,.85); padding: 10px 22px; border-radius: 12px; border: 3px solid rgba(255,255,255,.35); }}
    #hl-nl {{ left: 120px; top: 392px; color:{ORANGE}; font-size: 32px; }} #hl-de {{ left: 560px; top: 392px; color:{RED}; font-size: 32px; }} #hl-be {{ left: 130px; top: 880px; color:{GOLD}; }}""",
    f"""    <div id="hl-cam">
      <svg id="hl-hill" viewBox="0 0 1080 480"><path d="M0,480 L0,330 C160,300 300,180 440,110 C500,80 580,80 640,110 C780,180 920,290 1080,320 L1080,480 Z" fill="#1b2438" stroke="#3a4766" stroke-width="5"/>
        <path d="M0,480 L0,400 C200,370 380,300 540,290 C700,300 880,370 1080,390 L1080,480 Z" fill="#141b2c"/></svg>
      <div id="hl-pin">{pie_svg("hl-p", P3, r=100, size=220, labels=False)}</div>
      <div id="hl-name" class="tag"><span>VAALSERBERG</span></div>
      <div id="hl-nl" class="tag"><span class="flag">🇳🇱</span> NETHERLANDS</div>
      <div id="hl-de" class="tag"><span class="flag">🇩🇪</span> GERMANY</div>
      <div id="hl-be" class="tag"><span class="flag">🇧🇪</span> BELGIUM</div>
    </div>""",
    f"""      tl.fromTo("#hl-cam", {{ scale: 1.25, y: 80 }}, {{ scale: 1, y: 0, duration: 0.5, ease: "power3.out" }}, 0);
      tl.to("#hl-cam", {{ scale: 1.07, duration: {SLOT[g][1] - 0.5:.3f}, ease: "none" }}, 0.5);
      tl.fromTo("#hl-pin", {{ scale: 0, rotation: -90 }}, {{ scale: 1, rotation: 0, duration: 0.4, ease: "back.out(2)" }}, 0.25);
      tl.fromTo("#hl-name", {{ opacity: 0, y: 20 }}, {{ opacity: 1, y: 0, duration: 0.25 }}, 0.35);
      tl.fromTo("#hl-nl", {{ opacity: 0, scale: 0.6 }}, {{ opacity: 1, scale: 1, duration: 0.2, ease: "back.out(2.5)" }}, {tn:.3f});
      tl.fromTo("#hl-be", {{ opacity: 0, scale: 0.6 }}, {{ opacity: 1, scale: 1, duration: 0.2, ease: "back.out(2.5)" }}, {tb:.3f});
      tl.fromTo("#hl-de", {{ opacity: 0, scale: 0.6 }}, {{ opacity: 1, scale: 1, duration: 0.2, ease: "back.out(2.5)" }}, {tg:.3f});""")
cues += [{"t": round(S[g] + 0.3, 3), "kind": "whoosh2", "label": "zoom a la colina (pico)"}]
cues += [{"t": round(S[g] + x + 0.03, 3), "kind": "click", "pitch": p, "label": n} for x, p, n in ((tn, 0, "NL"), (tb, 2, "BE"), (tg, 4, "DE"))]

# ---------- 3. MORESNET (c6 → c9) ----------
m = "mor"
t_neu, t_tiny, t_zinc = L(m, wt("Neutral")), L(m, starts[7]), L(m, wt("zinc"))
s_mor = scene_file(m, f"""
    #mr-cam {{ position:absolute; inset:0; transform-origin: 540px 760px; }}
    #mr-pie {{ position:absolute; left:280px; top:510px; width:520px; height:520px; transform-origin:260px 260px; }}
    #mr-stamp {{ left:0; width:1000px; top: 372px; text-align:center; border:none; background:none; padding:0; transform-origin: 500px 60px; }}
    #mr-stamp span {{ display:inline-block; padding: 14px 26px; border: 7px solid {CYAN}; border-radius: 16px; color:{CYAN}; background: rgba(8,10,18,.75); font-size: 54px; }}
    #mr-pr {{ left: 110px; top: 880px; color:{INK}; }} #mr-nl {{ left: 560px; top: 880px; color:{ORANGE}; }}
    #mr-vs {{ left: 0; width: 1000px; top: 885px; text-align:center; background:none; color:{CYAN}; font-size: 40px; }}
    #mr-zn {{ position:absolute; left: 440px; top: 840px; width: 200px; height: 220px; border-radius: 18px; background: #1e2a44; border: 6px solid {CYAN};
             text-align:center; color:{INK}; font-family:'JetBrains Mono',monospace; box-shadow: 0 20px 60px rgba(0,0,0,.6); }}
    #mr-zn b {{ display:block; font-family:'Inter Display'; font-size: 96px; line-height: 1; margin-top: 30px; color:{CYAN}; }}
    #mr-zn i {{ position:absolute; left:14px; top:10px; font-style:normal; font-size: 30px; font-weight: 800; }}
    #mr-zn u {{ display:block; text-decoration:none; font-size: 30px; font-weight:800; letter-spacing:.12em; margin-top: 8px; }}""",
    f"""    <div id="mr-cam">
      <div id="mr-pie">{pie_svg("mr-p", P4, fourth_style="solid")}</div>
      <div id="mr-stamp" class="stamp"><span>NEUTRAL MORESNET · 1816</span></div>
      <div id="mr-pr" class="tag">PRUSSIA</div><div id="mr-vs" class="tag">⇄</div><div id="mr-nl" class="tag">NETHERLANDS</div>
      <div id="mr-zn"><i>30</i><b>Zn</b><u>ZINC</u></div>
    </div>""",
    f"""      tl.fromTo("#mr-cam", {{ scale: 1.1 }}, {{ scale: 1, duration: 0.4, ease: "power3.out" }}, 0);
      tl.fromTo("#mr-p-q", {{ scale: 0.2, opacity: 0 }}, {{ scale: 1, opacity: 1, duration: 0.35, ease: "back.out(2.2)" }}, {t_neu:.3f});
      tl.fromTo("#mr-p-t-q", {{ opacity: 0 }}, {{ opacity: 0, duration: 0.01 }}, 0);
      tl.fromTo("#mr-stamp", {{ opacity: 0, scale: 1.6, rotation: -12 }}, {{ opacity: 1, scale: 1, rotation: -4, duration: 0.18, ease: "power4.in" }}, {t_neu + 0.1:.3f});
      // "a tiny territory nobody could agree on": tira y afloja
      tl.to("#mr-pie", {{ scale: 0.74, y: -70, duration: 0.4, ease: "power2.inOut" }}, {t_tiny:.3f});
      tl.fromTo("#mr-pr, #mr-nl, #mr-vs", {{ opacity: 0, y: 30 }}, {{ opacity: 1, y: 0, duration: 0.25 }}, {t_tiny + 0.2:.3f});
      tl.fromTo("#mr-pr", {{ x: 0 }}, {{ x: -18, duration: 0.25, yoyo: true, repeat: 5, ease: "sine.inOut" }}, {t_tiny + 0.45:.3f});
      tl.fromTo("#mr-nl", {{ x: 0 }}, {{ x: 18, duration: 0.25, yoyo: true, repeat: 5, ease: "sine.inOut" }}, {t_tiny + 0.45:.3f});
      // "because of a zinc mine"
      tl.to("#mr-pr, #mr-nl, #mr-vs", {{ opacity: 0, duration: 0.15 }}, {t_zinc - 0.15:.3f});
      tl.fromTo("#mr-zn", {{ opacity: 0, scale: 0.4, rotation: -10 }}, {{ opacity: 1, scale: 1, rotation: 0, duration: 0.3, ease: "back.out(2.4)" }}, {t_zinc - 0.05:.3f});""")
cues += [{"t": round(S[m] + t_neu + 0.28, 3), "kind": "stamp", "label": "sello NEUTRAL MORESNET"},
         {"t": round(S[m] + t_zinc + 0.12, 3), "kind": "thunk", "pitch": 2, "label": "ficha Zn"}]

# ---------- 4. ESPERANTO (c9 → c10) ----------
e = "esp"
t_esp = L(e, wt("Esperanto"))
s_esp = scene_file(e, f"""
    #es-cam {{ position:absolute; inset:0; transform-origin: 540px 700px; }}
    #es-bub {{ position:absolute; left: 220px; top: 520px; width: 640px; height: 300px; border-radius: 60px; background: #fff;
              color: #0b1020; text-align:center; font-weight:900; font-size: 130px; line-height: 300px; box-shadow: 0 30px 80px rgba(0,0,0,.55); transform-origin: 200px 300px; }}
    #es-tail {{ position:absolute; left: 300px; top: 800px; width: 0; height: 0; border-left: 40px solid transparent; border-right: 40px solid transparent; border-top: 80px solid #fff; }}
    #es-flag {{ position:absolute; left: 400px; top: 360px; width: 280px; height: 120px; background: #1f9d55; border-radius: 10px; }}
    #es-flag i {{ position:absolute; left:0; top:0; width:120px; height:120px; background:#fff; border-radius: 10px 0 0 10px; color:#1f9d55; font-style:normal; font-size: 90px; line-height:120px; text-align:center; }}
    #es-lbl {{ left:0; width:1000px; top: 900px; text-align:center; background:none; color:{INK}; }}
    #es-lbl span {{ background: rgba(8,10,18,.85); padding: 12px 22px; border-radius: 12px; }}""",
    f"""    <div id="es-cam">
      <div id="es-flag"><i>★</i></div>
      <div id="es-bub">Saluton!</div><div id="es-tail"></div>
      <div id="es-lbl" class="tag"><span>"AMIKEJO" · ESPERANTO STATE?</span></div>
    </div>""",
    f"""      tl.fromTo("#es-cam", {{ scale: 1 }}, {{ scale: 1.08, duration: {SLOT[e][1]}, ease: "none" }}, 0);
      tl.fromTo("#es-bub, #es-tail", {{ opacity: 0, scale: 0.3 }}, {{ opacity: 1, scale: 1, duration: 0.3, ease: "back.out(2.2)" }}, {max(0.05, t_esp - 0.35):.3f});
      tl.fromTo("#es-flag", {{ opacity: 0, y: -30 }}, {{ opacity: 1, y: 0, duration: 0.3 }}, 0.1);
      tl.fromTo("#es-lbl", {{ opacity: 0 }}, {{ opacity: 1, duration: 0.25 }}, {max(0.1, t_esp - 0.6):.3f});""")
cues += [{"t": round(S[e] + max(0.05, t_esp - 0.35) + 0.08, 3), "kind": "click", "pitch": 6, "label": "bocadillo Saluton!"}]

# ---------- 5. BORRADO (c10 → c12) ----------
x_ = "erase"
t_then, t_era = L(x_, starts[10]), L(x_, wt("erased"))
t_twenty = L(x_, wt("twenty..."))
s_erase = scene_file(x_, f"""
    #er-cam {{ position:absolute; inset:0; transform-origin: 540px 760px; }}
    #er-year {{ position:absolute; left:0; width:1000px; top: 370px; text-align:center; font-weight:900; font-size: 150px; color:{INK}; line-height:1; }}
    #er-pie {{ position:absolute; left:330px; top:540px; width:420px; height:420px; transform-origin:210px 210px; }}
    #er-x {{ position:absolute; left: 470px; top: 760px; width: 180px; height: 180px; }}
    #er-stamp {{ left:0; width:1000px; top: 960px; text-align:center; border:none; background:none; padding:0; }}
    #er-stamp span {{ display:inline-block; padding: 12px 26px; border: 7px solid {RED}; border-radius: 16px; color:{RED}; background: rgba(8,10,18,.75); font-size: 52px; }}""",
    f"""    <div id="er-cam">
      <div id="er-year">1816</div>
      <div id="er-pie">{pie_svg("er-p", P4, r=190, size=420, fourth_style="solid", labels=False)}</div>
      <svg id="er-x" viewBox="0 0 180 180"><path id="er-x1" d="M20,20 L160,160" stroke="{RED}" stroke-width="22" stroke-linecap="round"/><path id="er-x2" d="M160,20 L20,160" stroke="{RED}" stroke-width="22" stroke-linecap="round"/></svg>
      <div id="er-stamp" class="stamp"><span>ERASED · 1920</span></div>
    </div>""",
    f"""      const y = {{ v: 1816 }}, ye = document.querySelector("#er-year");
      tl.fromTo(y, {{ v: 1816 }}, {{ v: 1920, duration: {max(0.4, t_twenty + 0.3 - t_then):.3f}, ease: "power2.inOut", onUpdate: () => {{ ye.textContent = Math.round(y.v); }} }}, {t_then:.3f});
      tl.fromTo("#er-cam", {{ scale: 1 }}, {{ scale: 1.1, duration: {SLOT[x_][1]}, ease: "none" }}, 0);
      tl.fromTo("#er-x", {{ opacity: 0, scale: 1.6 }}, {{ opacity: 1, scale: 1, duration: 0.15, ease: "power4.in" }}, {t_era - 0.1:.3f});
      tl.to("#er-p-q", {{ opacity: 0, duration: 0.5 }}, {t_era + 0.15:.3f});
      tl.fromTo("#er-stamp", {{ opacity: 0, scale: 1.5, rotation: -10 }}, {{ opacity: 1, scale: 1, rotation: -3, duration: 0.18, ease: "power4.in" }}, {t_era + 0.2:.3f});""")
cues += [{"t": round(S[x_] + t_twenty + 0.3, 3), "kind": "tick", "label": "año se fija en 1920"},
         {"t": round(S[x_] + t_era + 0.05, 3), "kind": "hit", "label": "X: borrado del mapa"}]

# ---------- 6. GUARDAR (c12 → c14) ----------
v = "save"
t_save = L(v, starts[13])
s_save = scene_file(v, f"""
    #sv-cam {{ position:absolute; inset:0; transform-origin: 540px 700px; }}
    #sv-q {{ top: 350px; font-size: 92px; }}
    #sv-q span {{ color:{GOLD}; }}
    #sv-pin {{ position:absolute; left: 460px; top: 590px; width: 160px; height: 200px; }}
    #sv-place {{ left:0; width:1000px; top: 780px; text-align:center; background:none; color:{INK}; font-size: 34px; }}
    #sv-place span {{ background: rgba(8,10,18,.85); padding: 10px 20px; border-radius: 12px; }}
    #sv-card {{ position:absolute; left: 170px; top: 880px; width: 660px; height: 130px; border-radius: 26px; background:{GOLD};
               color:#0b1020; font-weight:900; font-size: 52px; line-height:130px; text-align:center; box-shadow: 0 20px 60px rgba(0,0,0,.5); transform-origin: 330px 65px; }}""",
    f"""    <div id="sv-cam">
      <svg id="sv-pin" viewBox="0 0 160 200"><path d="M80,195 C80,195 10,110 10,70 A70,70 0 0,1 150,70 C150,110 80,195 80,195 Z" fill="{RED}" stroke="#fff" stroke-width="6"/><circle cx="80" cy="70" r="26" fill="#fff"/></svg>
      <div id="sv-place" class="tag"><span>DRIELANDENPUNT · VAALS <span class="flag">🇳🇱</span></span></div>
      <div id="sv-card">🔖 SAVE FOR YOUR TRIP</div>
    </div>
    <div id="sv-q" class="big">WOULD YOU<br><span>STAND HERE?</span></div>""",
    f"""      tl.fromTo("#sv-cam", {{ scale: 1.1 }}, {{ scale: 1.0, duration: {SLOT[v][1]}, ease: "none" }}, 0);
      tl.fromTo("#sv-q", {{ opacity: 0, y: 30 }}, {{ opacity: 1, y: 0, duration: 0.25, ease: "power3.out" }}, 0.05);
      tl.fromTo("#sv-pin", {{ opacity: 0, y: -120 }}, {{ opacity: 1, y: 0, duration: 0.4, ease: "bounce.out" }}, 0.15);
      tl.fromTo("#sv-place", {{ opacity: 0 }}, {{ opacity: 1, duration: 0.25 }}, 0.45);
      tl.fromTo("#sv-card", {{ opacity: 0, scale: 0.6 }}, {{ opacity: 1, scale: 1, duration: 0.3, ease: "back.out(2.5)" }}, {t_save:.3f});
      tl.to("#sv-card", {{ scale: 1.05, duration: 0.3, yoyo: true, repeat: 1, ease: "sine.inOut" }}, {t_save + 0.5:.3f});""")
cues += [{"t": round(S[v] + 0.5, 3), "kind": "thunk", "pitch": 4, "label": "cae el pin"},
         {"t": round(S[v] + t_save + 0.05, 3), "kind": "click", "pitch": 3, "label": "tarjeta guardar"}]

# ---------- 7. CIERRE (c14 → fin) ----------
en = "end"
s_end = scene_file(en, f"""
    #en-isl {{ position:absolute; left: 290px; top: 380px; width: 500px; height: 300px; }}
    #en-ring {{ position:absolute; left: 300px; top: 300px; width: 480px; height: 460px; transform-origin: 240px 230px; }}
    #en-ep {{ left: 0; width: 1000px; top: 770px; text-align:center; background:none; color:{GOLD}; font-size: 38px; }}
    #en-title {{ position:absolute; left: 100px; width: 800px; top: 830px; text-align:center; font-weight:900; font-size: 64px; line-height: 1.02; color:{INK}; }}
    #en-title b {{ color:{GOLD}; }}
    #en-follow {{ left: 0; width: 1000px; top: 1065px; text-align:center; background:none; color:{INK}; font-size: 30px; }}""",
    f"""    <svg id="en-isl" viewBox="0 0 500 300">
      <path d="M40,150 C40,80 140,40 250,40 L250,260 C140,260 40,220 40,150 Z" fill="#2f5bd3"/>
      <path d="M250,40 C360,40 460,80 460,150 C460,220 360,260 250,260 Z" fill="#d93a3a"/>
      <path d="M250,40 C360,40 460,80 460,150 C460,220 360,260 250,260 Z" fill="none" stroke="{GOLD}" stroke-width="6" stroke-dasharray="1 0"/>
      <text x="145" y="168" text-anchor="middle" font-family="Inter Display" font-weight="900" font-size="54" fill="#fff">FR</text>
      <text x="355" y="168" text-anchor="middle" font-family="Inter Display" font-weight="900" font-size="54" fill="#fff">ES</text>
    </svg>
    <svg id="en-ring" viewBox="0 0 480 460"><path d="M240,20 A220,210 0 1,1 60,110" fill="none" stroke="#fff" stroke-width="10" stroke-linecap="round" stroke-dasharray="26 18"/>
      <path d="M60,110 L40,60 L100,80 Z" fill="#fff"/></svg>
    <div id="en-ep" class="tag">EP. 3 · NEXT</div>
    <div id="en-title">THE ISLAND THAT CHANGES COUNTRY <b>EVERY 6 MONTHS</b></div>
    <div id="en-follow" class="tag">FOLLOW SO YOU DON'T MISS IT</div>""",
    f"""      tl.fromTo("#en-isl", {{ scale: 0.6, opacity: 0 }}, {{ scale: 1, opacity: 1, duration: 0.45, ease: "back.out(1.8)" }}, 0);
      tl.fromTo("#en-ring", {{ rotation: 0, opacity: 0 }}, {{ rotation: 360, opacity: 1, duration: {SLOT[en][1]:.3f}, ease: "none" }}, 0);
      tl.fromTo("#en-ep", {{ opacity: 0, y: 20 }}, {{ opacity: 1, y: 0, duration: 0.25 }}, 0.2);
      tl.fromTo("#en-title", {{ opacity: 0, y: 40 }}, {{ opacity: 1, y: 0, duration: 0.35, ease: "power3.out" }}, {L(en, wt('island')) - 0.1:.3f});
      tl.fromTo("#en-follow", {{ opacity: 0, scale: 0.9 }}, {{ opacity: 1, scale: 1, duration: 0.3, ease: "back.out(2)" }}, {L(en, wt('changes')):.3f});""")
cues += [{"t": round(S[en] + 0.12, 3), "kind": "whoosh_soft", "label": "entra la tarjeta final"}]

# ---------- captions ----------
KEY = {"three", "four", "four.", "fourth", "vaalserberg", "netherlands", "belgium", "germany", "moresnet", "zinc", "esperanto",
       "twenty", "erased", "save", "island", "six"}
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
        t = w["text"].upper().strip(",:").replace("NINETEEN", "19").replace("TWENTY...", "20...")
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
      tl.to("#bg-night", {{ opacity: 1, duration: 0.4 }}, {S['erase']});
      tl.to("#bg-warm", {{ opacity: 0, duration: 0.4 }}, {S['erase']});
      tl.to("#bg-night", {{ opacity: 0, duration: 0.4 }}, {S['save']});
      tl.to("#bg-warm", {{ opacity: 1, duration: 0.4 }}, {S['save']});
      tl.to("#bg-night", {{ opacity: 0.5, duration: 0.5 }}, {S['end']});
      window.__timelines["main"] = tl;
    </script>
  </body>
</html>
"""
os.makedirs(os.path.join(HERE, "compositions"), exist_ok=True)
for k, txt in {"hook": s_hook, "hill": s_hill, "mor": s_mor, "esp": s_esp, "erase": s_erase, "save": s_save, "end": s_end,
               "captions": s_caps}.items():
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
    "musica": {"file": f"{LIBR}/musica/fs-631776_documentary-music-strings.mp3", "gain_db": -6, "duck_db": 8,
               "offset": 20.0, "fade_in": 0.2, "fade_out": 1.0,
               "rides": [[S["erase"] - 0.1, 0], [S["erase"] + 0.3, -8], [S["save"] - 0.2, -8], [S["save"] + 0.3, 0]]},
    "sfx": sfx,
    "master": {"lufs": -14, "tp": -1.5, "tp_aac": -1.0},
    "salida": "out/audio.wav",
    "video": "../out/vaalserberg_silent.mp4",
}
json.dump(diseno, open(os.path.join(HERE, "audio/diseno.json"), "w"), indent=1, ensure_ascii=False)
json.dump({"scenes": SLOT, "cues": cues, "captions": [{k: c[k] for k in ("id", "start", "end", "text")} for c in cap], "duration": DUR},
          open(os.path.join(HERE, "cues.json"), "w"), indent=1, ensure_ascii=False)
print(f"duración {DUR} s · {len(cap)} subtítulos · {len(sfx)} efectos")
for k in order:
    print(f"  {k:6} {SLOT[k][0]:6.2f} → {SLOT[k][0] + SLOT[k][1]:6.2f}")
print(" | ".join(c["text"] for c in cap))
