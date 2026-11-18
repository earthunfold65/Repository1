#!/usr/bin/env python3
"""EL OÍDO: escucha el video terminado con earshot ANTES de entregarlo y dice qué corregir.

  HF_HUB_DISABLE_XET=1 ~/.venvs/chatter/bin/python -I instagram/scripts/oido.py <video.mp4> <cues.json> [--out carpeta]

<cues.json> = el que escribe build.py ({"cues":[{t, kind, label}], ...}).
Hace:
  1. earshot timeline --cues  → por cada efecto: ¿suena?, ¿a tiempo?, ¿se oye sobre la voz/música?
  2. earshot critique         → comparación con 7 películas profesionales (espectro, loudness, arco, densidad…)
  3. earshot sheet            → PNG con fotogramas, espectrograma y marcas de cada cue (abrirlo y mirarlo)
  4. earshot describe         → cómo suena cada archivo de efecto usado (y si parece sintético)
Veredicto: ENTREGAR solo si no hay efectos tarde/adelantados/inaudibles y la crítica no es "needs work".

Umbrales (de real-sound/earshot, medidos en películas pro):
  sync: el ataque entre −45 ms y +75 ms del evento visual · audible: ≥ 3 dB sobre el fondo (≥ 6 dB claro)
"""
import json
import os
import subprocess
import sys

ES = os.environ.get("EARSHOT", "/home/user/.venvs/chatter/bin/earshot")
ENV = {**os.environ, "HF_HUB_DISABLE_XET": "1"}


def run(args, **kw):
    r = subprocess.run([ES, *args], capture_output=True, text=True, env=ENV, **kw)
    if r.returncode != 0:
        sys.exit(f"earshot {' '.join(args[:2])} falló:\n{r.stderr[-1500:]}")
    return r.stdout


def main():
    if len(sys.argv) < 3:
        sys.exit(__doc__)
    video, cues_path = os.path.abspath(sys.argv[1]), os.path.abspath(sys.argv[2])
    out = os.path.abspath(sys.argv[sys.argv.index("--out") + 1]) if "--out" in sys.argv else os.path.join(os.path.dirname(video), "oido")
    os.makedirs(out, exist_ok=True)
    c = json.load(open(cues_path))
    cues = sorted(c["cues"], key=lambda x: x["t"])
    ev = {"fps": 30, "events": [{"f": round(x["t"] * 30), "kind": x["kind"], "id": f'{i:02d} {x["label"][:40]}'} for i, x in enumerate(cues)]}
    cf = os.path.join(out, "earshot_cues.json")
    json.dump(ev, open(cf, "w"))

    print("· escuchando la línea de tiempo…", flush=True)
    run(["timeline", video, "--cues", cf, "--detail", "normal", "--out", os.path.join(out, "timeline.json")])
    tl = json.load(open(os.path.join(out, "timeline.json")))
    print("· comparando con películas profesionales…", flush=True)
    crit = run(["critique", video])
    open(os.path.join(out, "critique.txt"), "w").write(crit)
    print("· dibujando la hoja de escucha…", flush=True)
    run(["sheet", video, "-o", os.path.join(out, "sheet.png"), "--cues", cf, "--detail", "low"])

    problemas = []
    filas = []
    for it in tl["sync"]["cues"]["items"]:
        off, prom, st = it.get("offset_ms"), it.get("event_prominence_db"), it.get("status")
        if st not in ("OK", "near") or off is None:
            estado = "NO SUENA"
        elif off > 75:
            estado = f"TARDE {off:+.0f} ms"
        elif off < -45:
            estado = f"ADELANTADO {off:+.0f} ms"
        elif prom is not None and prom < 3:
            estado = f"INAUDIBLE (+{prom:.1f} dB)"
        elif prom is not None and prom < 6:
            estado = f"débil (+{prom:.1f} dB)"
        else:
            estado = "ok"
        filas.append((it["t"], it["id"], off, prom, estado))
        if estado != "ok" and not estado.startswith("débil"):
            problemas.append(f'{it["t"]:6.2f}s {it["id"]}: {estado}')

    veredicto_crit = next((l for l in crit.splitlines() if l.startswith("VERDICT")), "VERDICT: ?")
    fixes = []
    capt = False
    for l in crit.splitlines():
        if l.startswith("FIX FIRST"):
            capt = True
            continue
        if capt:
            if not l.startswith("  ") or l.startswith("SCORECARD"):
                break
            fixes.append(l.strip())

    # cómo suena cada archivo de efecto usado (una sola vez por archivo)
    dis = json.load(open(os.path.join(os.path.dirname(cues_path), "audio", "diseno.json")))
    base = os.path.join(os.path.dirname(cues_path), "audio")
    files = sorted({s["file"] for s in dis.get("sfx", [])})
    desc = {}
    for f in files:
        p = f if os.path.isabs(f) else os.path.normpath(os.path.join(base, f))
        txt = run(["describe", p])
        desc[os.path.basename(p)] = txt.strip().splitlines()[0][:260]

    rep = ["# Informe del oído (earshot)", "", f"**Video:** `{os.path.basename(video)}`", "",
           f"**Crítica vs. películas profesionales:** {veredicto_crit.replace('VERDICT: ', '')}", ""]
    if fixes:
        rep += ["**Arreglar primero:**"] + [f"- {x}" for x in fixes] + [""]
    rep += ["## Efectos: sincronía y audibilidad", "", "| t | efecto | desfase | sobre el fondo | estado |", "|---|---|---|---|---|"]
    for t, i, off, prom, e in filas:
        rep.append(f"| {t:.2f} s | {i} | {'' if off is None else f'{off:+.0f} ms'} | {'' if prom is None else f'+{prom:.1f} dB'} | {e} |")
    rep += ["", "## Cómo suena cada archivo de efecto", ""] + [f"- `{k}`: {v}" for k, v in desc.items()]
    ok = not problemas and "needs work" not in veredicto_crit and "not launch" not in veredicto_crit
    rep += ["", f"## VEREDICTO: {'ENTREGAR' if ok else 'CORREGIR ANTES DE ENTREGAR'}"] + [f"- {p}" for p in problemas]
    rep += ["", f"Hoja de escucha: `{os.path.join(out, 'sheet.png')}` (abrirla y mirarla)."]
    open(os.path.join(out, "INFORME_OIDO.md"), "w").write("\n".join(rep) + "\n")
    print("\n".join(rep))


if __name__ == "__main__":
    main()
