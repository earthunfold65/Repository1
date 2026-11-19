#!/usr/bin/env python3
"""Predictor de retención de EarthUnfold (propio, sin modelos de licencia NC).

Modelo de supervivencia por segundo: cada segundo una parte de la audiencia se va
("hazard"). El riesgo sube cuanto más tiempo pasa sin novedad (corte, efecto,
rótulo nuevo, dato), y baja cuando hay un bucle abierto pendiente ("FACT 2/5",
"but", "wait", una pregunta). El gancho (0–3 s) tiene su propio riesgo, que
depende de hookscore y de cuánto tarda en llegar la promesa.

Uso (venv con numpy/matplotlib):
  ~/.venvs/chatter/bin/python -I instagram/scripts/predictor.py VIDEO.mp4 \
      --words audio/words.json --cues cues.json [--out out/predictor] [--nombre EP2]
  ~/.venvs/chatter/bin/python -I instagram/scripts/predictor.py --calibrar
      (reajusta los parámetros con instagram/predictor/metricas.csv)

Salida: informe.md, curva.png y features.json en --out. Todo es una ESTIMACIÓN:
con pocos videos calibrados el error típico es grande; se dice en el informe.
"""
import argparse
import csv
import importlib.util
import json
import math
import os
import re
import subprocess
import sys

import numpy as np

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
PRED_DIR = os.path.join(ROOT, "instagram", "predictor")
CALIB = os.path.join(PRED_DIR, "calibracion.json")
METRICAS = os.path.join(PRED_DIR, "metricas.csv")
HOOKSCORE = os.path.join(ROOT, ".claude", "skills", "ig-reel", "hookscore.py")

DEFAULT = {
    # riesgo del gancho (fracción que se va en 0-3 s) = sigmoide(a0 + a1*(hook-50)/25 + a2*promesa_s + a3*frame0)
    "a0": -0.35, "a1": -0.55, "a2": 0.25, "a3": -0.30,
    # riesgo por segundo del cuerpo
    "h_base": 0.030,      # salida "natural" por segundo
    "k_gap": 0.22,        # +22 % de riesgo por cada segundo sin novedad por encima de GAP_OK
    "gap_ok": 2.5,        # s sin novedad que se toleran
    "k_loop": 0.35,       # -35 % de riesgo con un bucle abierto pendiente
    "k_speech": 0.25,     # +25 % si no hay voz ni música en ese segundo (silencio)
    "end_bonus": 0.5,     # en los 2 últimos s el riesgo baja (payoff / CTA)
    "k_static": 0.30,     # +30 % si la imagen está casi congelada ese segundo
    "n_videos": 0,
}

OPEN_LOOP = re.compile(r"\b(but|wait|until|secret|still|never|why|how|nobody|here's|fact|number|guess|"
                       r"last one|the weird|turns out|except|actually|plot twist)\b|\?", re.I)
PROMISE = re.compile(r"\b(\d[\d,.]*|one|two|three|four|five|six|seven|eight|nine|ten|hundred|thousand|"
                     r"million|every|only|never|impossible|illegal|same|once|countr(y|ies)|border|switch(es)?|decides?)\b", re.I)


# ---------------------------------------------------------------- utilidades
def load_calib():
    if os.path.exists(CALIB):
        with open(CALIB) as f:
            p = dict(DEFAULT)
            p.update(json.load(f))
            return p
    return dict(DEFAULT)


def sigmoid(x):
    return 1.0 / (1.0 + math.exp(-x))


def hook_score(text):
    if not text.strip() or not os.path.exists(HOOKSCORE):
        return 50.0
    spec = importlib.util.spec_from_file_location("hookscore", HOOKSCORE)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    _, overall, _, _ = mod.run(text)
    return float(overall)


def duration_of(video):
    out = subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration",
                          "-of", "csv=p=0", video], capture_output=True, text=True, check=True)
    return float(out.stdout.strip())


def motion_curve(video, fps=10, w=72, h=128):
    """Diferencia media entre fotogramas (0-1) a `fps`, en gris y baja resolución."""
    cmd = ["ffmpeg", "-v", "error", "-i", video, "-vf", f"fps={fps},scale={w}:{h},format=gray",
           "-f", "rawvideo", "-"]
    raw = subprocess.run(cmd, capture_output=True, check=True).stdout
    frames = np.frombuffer(raw, np.uint8).reshape(-1, h, w).astype(np.float32) / 255.0
    diff = np.abs(np.diff(frames, axis=0)).mean(axis=(1, 2))
    return np.concatenate([[diff[0] if len(diff) else 0.0], diff]), frames


def audio_activity(video, dur):
    """Volumen por segundo (dBFS RMS) de la pista de audio; None si no hay audio."""
    cmd = ["ffmpeg", "-v", "error", "-i", video, "-vn", "-ac", "1", "-ar", "8000", "-f", "s16le", "-"]
    raw = subprocess.run(cmd, capture_output=True).stdout
    if not raw:
        return None
    a = np.frombuffer(raw, np.int16).astype(np.float32) / 32768.0
    n = int(math.ceil(dur))
    out = []
    for s in range(n):
        seg = a[s * 8000:(s + 1) * 8000]
        rms = float(np.sqrt(np.mean(seg ** 2))) if len(seg) else 0.0
        out.append(20 * math.log10(rms + 1e-9))
    return np.array(out)


# ---------------------------------------------------------------- features
def features(video, words_path=None, cues_path=None, hook_text=None):
    dur = duration_of(video)
    n = int(math.ceil(dur))
    motion, frames = motion_curve(video)
    fps = 10
    # cortes = picos de diferencia muy por encima de la mediana
    med = float(np.median(motion)) + 1e-4
    cuts = [i / fps for i in range(1, len(motion)) if motion[i] > max(0.06, 6 * med)
            and motion[i] >= motion[max(0, i - 1)] and motion[i] >= motion[min(len(motion) - 1, i + 1)]]
    # energía de movimiento por segundo
    mot_s = np.array([motion[s * fps:(s + 1) * fps].mean() if len(motion[s * fps:(s + 1) * fps]) else 0
                      for s in range(n)])

    words = []
    if words_path and os.path.exists(words_path):
        with open(words_path) as f:
            w = json.load(f)
        words = [x for x in (w.get("words", w) if isinstance(w, dict) else w) if x.get("type", "word") == "word"]
    text = " ".join(x["text"] for x in words)

    cues, captions = [], []
    if cues_path and os.path.exists(cues_path):
        with open(cues_path) as f:
            c = json.load(f)
        cues = sorted(float(x["t"]) for x in c.get("cues", []))
        captions = sorted(float(x["start"]) for x in c.get("captions", []))
        scenes = c.get("scenes", {})
        for v in scenes.values():
            if isinstance(v, list) and v:
                cues.append(float(v[0]))
        cues.sort()

    # novedades: cortes, efectos, inicio de escena, frases con dato nuevo (número / bucle)
    novelty = list(cuts) + cues
    loops = []
    for i, x in enumerate(words):
        t = float(x["start"])
        if OPEN_LOOP.search(x["text"]):
            loops.append(t)
        if re.search(r"\d", x["text"]):
            novelty.append(t)
    novelty = sorted(set(round(t, 2) for t in novelty if 0 <= t <= dur))

    # gancho: primera frase hablada (hasta el primer punto o 12 palabras)
    if hook_text is None:
        first = []  # todo lo que se dice en los 3 primeros segundos, hasta el fin de esa frase
        for x in words:
            if float(x["start"]) >= 3.0 and first and re.search(r"[.!?]$", first[-1]):
                break
            first.append(x["text"])
            if len(first) >= 16:
                break
        hook_text = " ".join(first)
    hs = hook_score(hook_text)
    promise_t = next((float(x["start"]) for x in words if PROMISE.search(x["text"])), 3.0)
    # frame 0: ¿hay algo en pantalla (contraste) y movimiento en el primer segundo?
    f0 = frames[0]
    frame0 = float(min(1.0, f0.std() * 4)) * 0.5 + float(min(1.0, mot_s[0] * 20)) * 0.5

    speech = np.zeros(n)
    for x in words:
        for s in range(int(x["start"]), min(n, int(math.ceil(x["end"])))):
            speech[s] = 1
    act = audio_activity(video, dur)
    silent = np.zeros(n) if act is None else (act < -45).astype(float)
    if act is None:
        silent = 1 - speech

    # bucle abierto pendiente: desde que se abre hasta 6 s después (o un "FACT n/5" que dura todo el video)
    loop_on = np.zeros(n)
    for t in loops:
        loop_on[int(t):min(n, int(t) + 6)] = 1
    if re.search(r"\bfact\b|number (one|two|three|1|2|3)", text, re.I):
        loop_on[:] = np.maximum(loop_on, 0.5)

    # segundos desde la última novedad, por segundo
    gap = np.zeros(n)
    for s in range(n):
        prev = [t for t in novelty if t <= s + 0.5]
        gap[s] = (s + 0.5 - prev[-1]) if prev else s + 0.5

    return {
        "duracion": dur, "hook_text": hook_text, "hookscore": hs, "promesa_s": promise_t,
        "frame0": frame0, "cortes": cuts, "novedades": novelty, "bucles": loops,
        "gap": gap.tolist(), "loop_on": loop_on.tolist(), "silencio": silent.tolist(),
        "movimiento": mot_s.tolist(),
        "estatico": [float(m < 0.0015) for m in mot_s], "wps": len(words) / dur if dur else 0,
    }


# ---------------------------------------------------------------- modelo
def predict(F, p):
    n = len(F["gap"])
    hook_drop = sigmoid(p["a0"] + p["a1"] * (F["hookscore"] - 50) / 25 + p["a2"] * F["promesa_s"]
                        + p["a3"] * (F["frame0"] - 0.5) * 2)
    S = [1.0]
    hz = []
    for s in range(n):
        if s < 3:
            h = 1 - (1 - hook_drop) ** (1 / 3)  # reparte la caída del gancho en 3 s
        else:
            h = p["h_base"]
            h *= 1 + p["k_gap"] * max(0.0, F["gap"][s] - p["gap_ok"])
            h *= 1 - p["k_loop"] * F["loop_on"][s]
            h *= 1 + p["k_speech"] * F["silencio"][s]
            h *= 1 + p["k_static"] * F["estatico"][s]
            if s >= n - 2:
                h *= p["end_bonus"]
        h = min(0.6, max(0.0, h))
        hz.append(h)
        S.append(S[-1] * (1 - h))
    S = np.array(S)
    frac_last = F["duracion"] - (n - 1)
    # tiempo medio visto = área bajo la curva
    mid = (S[:-1] + S[1:]) / 2  # supervivencia media en cada segundo
    avg = float(mid[:-1].sum() + mid[-1] * frac_last)
    return {"curva": S.tolist(), "riesgo": hz, "skip_3s": 1 - float(S[min(3, n)]),
            "watch_medio_s": avg, "watch_pct": avg / F["duracion"], "llegan_final": float(S[-1])}


# ---------------------------------------------------------------- informe
def zonas_peligro(F, p, R):
    z = []
    gap = F["gap"]
    s = 3
    n = len(gap)
    while s < n:
        if gap[s] > p["gap_ok"] + 1 and F["loop_on"][s] < 1:
            e = s
            while e + 1 < n and gap[e + 1] > p["gap_ok"] and F["loop_on"][e + 1] < 1:
                e += 1
            perdida = R["curva"][s] - R["curva"][min(n, e + 1)]
            z.append((s, e + 1, max(gap[s:e + 1]), perdida))
            s = e + 1
        else:
            s += 1
    return sorted(z, key=lambda x: -x[3])


def informe(nombre, F, p, R, out):
    os.makedirs(out, exist_ok=True)
    zs = zonas_peligro(F, p, R)
    lines = [f"# Predictor de retención · {nombre}", "",
             f"Calibrado con {p.get('n_videos', 0)} video(s) con métricas reales. "
             + ("Con menos de 5 videos es una estimación orientativa (±30 %)." if p.get("n_videos", 0) < 5 else ""),
             "", "| Métrica | Predicción |", "|---|---|",
             f"| Skip en 0–3 s | {R['skip_3s']*100:.1f} % |",
             f"| Watch time medio | {R['watch_medio_s']:.1f} s de {F['duracion']:.1f} s ({R['watch_pct']*100:.0f} %) |",
             f"| Llegan al final | {R['llegan_final']*100:.1f} % |",
             "", "## Gancho",
             f"- \"{F['hook_text']}\" → hookscore **{F['hookscore']:.1f}**",
             f"- La promesa (número / imposible) llega en el **{F['promesa_s']:.1f} s** (ideal < 1 s)",
             f"- Fotograma 0 con contenido y movimiento: {F['frame0']:.2f} (0–1)",
             "", "## Ritmo",
             f"- {len(F['novedades'])} novedades en {F['duracion']:.0f} s "
             f"(una cada {F['duracion']/max(1,len(F['novedades'])):.1f} s; objetivo ≤ 3,5 s)",
             f"- {len(F['cortes'])} cortes de imagen detectados · {F['wps']*60:.0f} palabras/min",
             f"- Segundos con imagen casi congelada: {[i for i, v in enumerate(F['estatico']) if v] or 'ninguno'}",
             f"- {len(F['bucles'])} bucles abiertos en la voz (but / wait / ? / fact…)",
             "", "## Dónde se va la gente (FIX FIRST arriba)"]
    if not zs:
        lines.append("- Ningún tramo largo sin novedad. 👍")
    for a, b, g, loss in zs[:6]:
        lines.append(f"- **{a}–{b} s**: hasta {g:.1f} s sin novedad → pierdes {loss*100:.1f} pts. "
                     "Mete un dato nuevo, un corte/zoom, un efecto o un \"but…\" ahí.")
    if F["hookscore"] < 50:
        lines.insert(lines.index("## Ritmo") - 1, "- **FIX FIRST:** gancho < 50. Reescríbelo con /eu-voice.")
    with open(os.path.join(out, "informe.md"), "w") as f:
        f.write("\n".join(lines) + "\n")
    with open(os.path.join(out, "features.json"), "w") as f:
        json.dump({"features": F, "prediccion": R}, f, indent=1)
    try:
        import matplotlib
        matplotlib.use("Agg")
        import matplotlib.pyplot as plt
        fig, ax = plt.subplots(figsize=(10, 4), dpi=120)
        t = np.arange(len(R["curva"]))
        ax.plot(t, np.array(R["curva"]) * 100, lw=2.5, color="#e4572e", label="retención prevista")
        for nv in F["novedades"]:
            ax.axvline(nv, color="#2e86ab", alpha=0.25, lw=1)
        for a, b, _, _ in zs[:6]:
            ax.axvspan(a, b, color="#f3a712", alpha=0.25)
        ax.set_ylim(0, 100)
        ax.set_xlim(0, F["duracion"])
        ax.set_xlabel("segundo")
        ax.set_ylabel("% que sigue viendo")
        ax.set_title(f"{nombre}: skip {R['skip_3s']*100:.0f} % · watch {R['watch_medio_s']:.1f} s · "
                     f"final {R['llegan_final']*100:.0f} %  (azul = novedad, naranja = peligro)")
        ax.grid(alpha=0.2)
        fig.tight_layout()
        fig.savefig(os.path.join(out, "curva.png"))
    except ImportError:
        pass
    return "\n".join(lines)


# ---------------------------------------------------------------- calibración
def calibrar():
    """Ajusta a0 (gancho) y h_base (cuerpo) para que la predicción case con las métricas reales.
    Con >= 5 videos ajusta también a1 y k_gap. Búsqueda en rejilla: robusta y sin dependencias."""
    rows = list(csv.DictReader(open(METRICAS)))
    data = []
    for r in rows:
        if not r.get("skip_pct") or not r.get("watch_medio_s"):
            continue
        fp = os.path.join(ROOT, r["features_json"])
        F = json.load(open(fp))["features"]
        data.append((F, float(r["skip_pct"]) / 100, float(r["watch_medio_s"])))
    if not data:
        sys.exit("metricas.csv no tiene filas con skip_pct y watch_medio_s")
    p = dict(DEFAULT)
    grid_a0 = np.linspace(-2.5, 1.5, 81)
    grid_h = np.linspace(0.005, 0.12, 116)
    grid_a1 = [p["a1"]] if len(data) < 5 else np.linspace(-1.2, 0.0, 13)
    grid_k = [p["k_gap"]] if len(data) < 5 else np.linspace(0.05, 0.5, 10)
    best = None
    for a1 in grid_a1:
        for k in grid_k:
            for a0 in grid_a0:
                for h in grid_h:
                    q = dict(p, a0=float(a0), h_base=float(h), a1=float(a1), k_gap=float(k))
                    err = 0
                    for F, skip, watch in data:
                        R = predict(F, q)
                        err += ((R["skip_3s"] - skip) / 0.1) ** 2 + ((R["watch_medio_s"] - watch) / 2.0) ** 2
                    if best is None or err < best[0]:
                        best = (err, q)
    q = best[1]
    q["n_videos"] = len(data)
    os.makedirs(PRED_DIR, exist_ok=True)
    keep = {k: q[k] for k in DEFAULT}
    json.dump(keep, open(CALIB, "w"), indent=1)
    print(f"Calibrado con {len(data)} video(s). Error {best[0]:.3f}")
    for F, skip, watch in data:
        R = predict(F, q)
        print(f"  real skip {skip*100:.1f} % / watch {watch:.1f} s  →  pred {R['skip_3s']*100:.1f} % / {R['watch_medio_s']:.1f} s")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("video", nargs="?")
    ap.add_argument("--words")
    ap.add_argument("--cues")
    ap.add_argument("--hook")
    ap.add_argument("--out")
    ap.add_argument("--nombre")
    ap.add_argument("--calibrar", action="store_true")
    a = ap.parse_args()
    if a.calibrar:
        return calibrar()
    if not a.video:
        ap.error("falta VIDEO")
    F = features(a.video, a.words, a.cues, a.hook)
    p = load_calib()
    R = predict(F, p)
    out = a.out or os.path.join(os.path.dirname(os.path.abspath(a.video)), "predictor")
    print(informe(a.nombre or os.path.basename(a.video), F, p, R, out))
    print(f"\n→ {out}/informe.md y curva.png")


if __name__ == "__main__":
    main()
