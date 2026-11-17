#!/usr/bin/env python3
"""Mezcla, masteriza y revisa el sonido de un reel. Solo usa Python estándar + ffmpeg.

  python3 -I instagram/scripts/sonido.py medir  ARCHIVO           # LUFS, true peak, LRA
  python3 -I instagram/scripts/sonido.py anclas SFX.wav...          # ataque, pico y duración audible de cada SFX
  python3 -I instagram/scripts/sonido.py mezclar diseno.json        # render + master + QA (+ mux si hay "video")
  python3 -I instagram/scripts/sonido.py qa     diseno.json         # solo las comprobaciones

diseno.json (rutas relativas al propio JSON):
{
  "duracion": 20.0,
  "voz":    {"file": "voz.mp3", "gain_db": 0, "t": 0},
  "musica": {"file": "musica.mp3", "gain_db": -16, "duck_db": 8, "offset": 0, "fade_in": 0, "fade_out": 1.5,
             "rides": [[30.0, 0], [30.4, -12], [33.0, -12], [33.3, 0]]},   (dB extra en el tiempo del video)
  "sfx": [
    {"file": "sfx/whoosh.wav", "t": 2.00, "anchor": "peak",   "gain_db": -6, "label": "cambio de escena"},
    {"file": "sfx/pop.wav",    "t": 3.40, "anchor": "attack", "gain_db": -8, "pitch": 2, "label": "aparece tarjeta 01"},
    {"file": "sfx/riser.wav",  "t": 9.80, "anchor": "end",    "gain_db": -10, "label": "antes del reveal"}
  ],
  "master": {"lufs": -14, "tp": -1.5},
  "salida": "out/audio.wav",
  "video": "out/reel.mp4",              (opcional: produce out/reel_sonido.mp4)
  "fps": 30
}
anchor: attack = el golpe cae en t (clics, pops, golpes) · peak = el punto más fuerte cae en t (whooshes)
        end = el sonido termina en t (risers; pon t 0.03-0.25 s antes del golpe) · start = empieza en t (ambientes)
"""
import array
import json
import math
import os
import re
import subprocess
import sys

SR = 48000


def run(cmd, capture=True):
    r = subprocess.run(cmd, capture_output=capture, text=True)
    if r.returncode != 0:
        sys.exit(f"ffmpeg falló:\n{' '.join(cmd)}\n{r.stderr[-2000:]}")
    return r


def pcm_mono(path):
    r = subprocess.run(["ffmpeg", "-v", "error", "-i", path, "-ac", "1", "-ar", str(SR), "-f", "s16le", "-"],
                       capture_output=True)
    if r.returncode != 0:
        sys.exit(f"No se pudo leer {path}: {r.stderr.decode()[-500:]}")
    a = array.array("h")
    a.frombytes(r.stdout)
    return a


def envelope(samples, win=0.005):
    hop = max(1, int(SR * win))
    env = []
    for i in range(0, len(samples), hop):
        chunk = samples[i:i + hop]
        if not chunk:
            break
        rms = math.sqrt(sum(x * x for x in chunk) / len(chunk)) / 32768
        env.append(20 * math.log10(rms + 1e-9))
    return env, win


def anclas(path):
    """Tiempos internos del archivo: ataque (primer transitorio), pico, fin audible (-40 dB bajo el pico)."""
    s = pcm_mono(path)
    env, win = envelope(s)
    if not env:
        return {"attack": 0, "peak": 0, "end": 0, "dur": 0, "peak_db": -99}
    pk = max(range(len(env)), key=lambda i: env[i])
    pdb = env[pk]
    attack = next((i for i in range(pk + 1) if env[i] > pdb - 20), pk)
    end = len(env) - 1
    while end > pk and env[end] < pdb - 40:
        end -= 1
    return {"attack": round(attack * win, 4), "peak": round(pk * win, 4), "end": round((end + 1) * win, 4),
            "dur": round(len(s) / SR, 4), "peak_db": round(pdb, 1)}


def medir(path):
    r = subprocess.run(["ffmpeg", "-nostats", "-i", path, "-af", "ebur128=peak=true", "-f", "null", "-"],
                       capture_output=True, text=True)
    txt = r.stderr[r.stderr.rfind("Summary"):]
    get = lambda k: float(re.search(k + r":\s+(-?[\d.]+|-inf)", txt).group(1).replace("-inf", "-99"))
    return {"lufs": get("I"), "lra": get("LRA"), "tp": get("Peak")}


def cargar(dpath):
    with open(dpath, encoding="utf-8") as f:
        d = json.load(f)
    base = os.path.dirname(os.path.abspath(dpath))
    p = lambda x: x if os.path.isabs(x) else os.path.join(base, x)
    for k in ("voz", "musica"):
        if d.get(k):
            d[k]["file"] = p(d[k]["file"])
    for s in d.get("sfx", []):
        s["file"] = p(s["file"])
    d["salida"] = p(d.get("salida", "audio.wav"))
    if d.get("video"):
        d["video"] = p(d["video"])
    return d


def colocar(d):
    """Calcula cuándo arranca cada SFX para que su ancla caiga en t."""
    cache = {}
    for s in d.get("sfx", []):
        if s["file"] not in cache:
            cache[s["file"]] = anclas(s["file"])
        a = cache[s["file"]]
        anchor = s.get("anchor", "attack")
        inner = {"attack": a["attack"], "peak": a["peak"], "end": a["end"], "start": 0}[anchor]
        s["_a"] = a
        s["_inicio"] = s["t"] - inner          # puede ser negativo -> se recorta la cabeza
        s["_fin"] = s["_inicio"] + a["end"]
    return d


def qa(d, master=None, video_master=None):
    ok, avisos, errores = [], [], []
    dur = d.get("duracion")
    sfx = sorted(d.get("sfx", []), key=lambda s: s["t"])
    fps = d.get("fps", 30)
    for s in sfx:
        if s["_inicio"] < 0 and s.get("anchor") != "start":
            avisos.append(f"{s.get('label', s['file'])}: el ancla cae antes del inicio del video; se recorta {-s['_inicio']:.2f} s de cabeza")
        if s["t"] * fps % 1 > 1e-6 and abs(round(s["t"] * fps) - s["t"] * fps) > 0.01:
            avisos.append(f"{s.get('label', '?')}: t={s['t']} no cae en un fotograma exacto a {fps} fps (usa frame/{fps})")
        if s["_a"]["peak"] - s["_a"]["attack"] > 0.08 and s.get("anchor", "attack") == "attack":
            avisos.append(f"{s.get('label', '?')}: su pico llega {1000 * (s['_a']['peak'] - s['_a']['attack']):.0f} ms después del ataque; puede sentirse tarde (prueba anchor=peak)")
        if dur and s["_fin"] > dur + 0.05:
            avisos.append(f"{s.get('label', '?')}: termina en {s['_fin']:.2f} s, después del final ({dur} s); se corta")
    # densidad: ~5 efectos diseñados cada 10 s es la norma; > 8 suena a feria
    if dur and sfx:
        for w0 in range(0, int(math.ceil(dur)), 5):
            n = sum(1 for s in sfx if w0 <= s["t"] < w0 + 10)
            if n > 8:
                avisos.append(f"{n} efectos entre {w0}-{w0 + 10} s: demasiados (norma ~5/10 s); deja que la música cargue")
                break
    # repetición tipo ametralladora
    run_len = 1
    for a, b in zip(sfx, sfx[1:]):
        run_len = run_len + 1 if a["file"] == b["file"] else 1
        if run_len == 4:
            avisos.append(f"El mismo archivo 4 veces seguidas ({os.path.basename(b['file'])}): alterna 3-4 tomas o varía ±1-2 dB")
    # el gancho: algo debe sonar en los 2 primeros segundos
    if not d.get("voz") and not d.get("musica") and not any(s["t"] < 2 for s in sfx):
        errores.append("Nada suena en los primeros 2 s (el 100 % de las referencias tiene sonido ahí)")
    # huecos largos sin nada
    if not d.get("musica") and dur and sfx:
        marcas = [0] + [s["t"] for s in sfx] + [dur]
        hueco = max(b - a for a, b in zip(marcas, marcas[1:]))
        if hueco > 3.5:
            avisos.append(f"Hueco de {hueco:.1f} s sin sonido: suena a error si no es intencional")
    if master:
        tgt = d.get("master", {})
        lufs_t, tp_t = tgt.get("lufs", -14), tgt.get("tp", -1.5)
        if abs(master["lufs"] - lufs_t) > 0.7:
            errores.append(f"Loudness {master['lufs']} LUFS, objetivo {lufs_t} ±0.7")
        else:
            ok.append(f"Loudness {master['lufs']} LUFS (objetivo {lufs_t})")
        if master["tp"] > tp_t + 0.3:
            errores.append(f"True peak {master['tp']} dBTP > {tp_t}: puede distorsionar tras la compresión AAC de Instagram")
        else:
            ok.append(f"True peak {master['tp']} dBTP")
        if video_master:
            lim = tgt.get("tp_aac", -1.0)
            if video_master["tp"] > lim + 0.05:
                errores.append(f"En el MP4 (AAC) el true peak es {video_master['tp']} dBTP > {lim}")
            else:
                ok.append(f"MP4 final: {video_master['lufs']} LUFS, true peak {video_master['tp']} dBTP")
        if master["lra"] < 2:
            avisos.append(f"LRA {master['lra']} LU: mezcla muy aplastada (con arco narrativo la norma es 5-9)")
    return ok, avisos, errores


def mezclar(d):
    dur = d["duracion"]
    ins, chains, mixlabels = [], [], []

    def add_input(f):
        ins.extend(["-i", f])
        return len(ins) // 2 - 1

    voz_lbl = None
    if d.get("voz"):
        v = d["voz"]
        i = add_input(v["file"])
        ms = int(round(v.get("t", 0) * 1000))
        chains.append(f"[{i}:a]aresample={SR},aformat=channel_layouts=stereo,volume={v.get('gain_db', 0)}dB,"
                      f"adelay={ms}:all=1,apad,atrim=0:{dur}[voz]")
        if d.get("musica") and d["musica"].get("duck_db", 0) > 0:
            chains.append("[voz]asplit=2[vozmix][vozkey]")
            voz_lbl = "vozmix"
        else:
            voz_lbl = "voz"
        mixlabels.append(f"[{voz_lbl}]")
    if d.get("musica"):
        m = d["musica"]
        i = add_input(m["file"])
        fo = m.get("fade_out", 1.5)
        c = (f"[{i}:a]aresample={SR},aformat=channel_layouts=stereo,atrim=start={m.get('offset', 0)},asetpts=PTS-STARTPTS,"
             f"volume={m.get('gain_db', -16)}dB,apad,atrim=0:{dur}")
        if m.get("rides"):
            pts = sorted(m["rides"])
            expr = f"{pts[0][1]}"
            for (t0, d0), (t1, d1) in zip(pts, pts[1:]):
                expr = f"if(gte(t,{t0}),if(lt(t,{t1}),{d0}+({d1}-({d0}))*(t-{t0})/({t1}-{t0}),{d1}),{expr})"
            c += f",volume='pow(10,({expr})/20)':eval=frame"
        if m.get("fade_in"):
            c += f",afade=t=in:d={m['fade_in']}"
        if fo:
            c += f",afade=t=out:st={max(0, dur - fo)}:d={fo}"
        if voz_lbl == "vozmix":
            # ducking: la música baja ~duck_db cuando habla la voz
            ratio = min(20, max(2, m["duck_db"] / 2))
            chains.append(c + "[mus]")
            chains.append(f"[mus][vozkey]sidechaincompress=threshold=0.02:ratio={ratio}:attack=15:release=350:makeup=1[musd]")
            mixlabels.append("[musd]")
        else:
            chains.append(c + "[musd]")
            mixlabels.append("[musd]")
    for k, s in enumerate(d.get("sfx", [])):
        i = add_input(s["file"])
        st = s["_inicio"]
        head = max(0.0, -st)
        ms = int(round(max(0.0, st) * 1000))
        pan = max(-1.0, min(1.0, s.get("pan", 0)))
        l, r = (1 - max(0, pan)), (1 + min(0, pan))
        st_ = s.get("pitch", 0)
        pitch = f"asetrate={SR}*{2 ** (st_ / 12):.6f},aresample={SR}," if st_ else ""
        c = (f"[{i}:a]aresample={SR},aformat=channel_layouts=mono,atrim=start={head}:end={s['_a']['end']},asetpts=PTS-STARTPTS,{pitch}"
             f"afade=t=out:st={max(0, s['_a']['end'] - head - 0.01)}:d=0.01,volume={s.get('gain_db', -6)}dB,"
             f"pan=stereo|c0={l:.3f}*c0|c1={r:.3f}*c0,adelay={ms}:all=1[s{k}]")
        chains.append(c)
        mixlabels.append(f"[s{k}]")
    if not mixlabels:
        sys.exit("El diseño no tiene voz, música ni sfx")
    chains.append("".join(mixlabels) + f"amix=inputs={len(mixlabels)}:normalize=0:duration=longest,"
                  f"apad,atrim=0:{dur},highpass=f=25[pre]")
    os.makedirs(os.path.dirname(d["salida"]) or ".", exist_ok=True)
    pre = d["salida"] + ".pre.wav"
    run(["ffmpeg", "-v", "error", "-y", *ins, "-filter_complex", ";".join(chains), "-map", "[pre]",
         "-ar", str(SR), "-c:a", "pcm_s24le", pre])

    # master: ganancia + limitador true-peak (sobremuestreado x4), corregido en bucle hasta el objetivo
    tgt = d.get("master", {})
    lufs_t, tp_t = tgt.get("lufs", -14), tgt.get("tp", -1.5)
    tp_aac_max = tgt.get("tp_aac", -1.0)   # pico permitido DESPUÉS de codificar a AAC (lo que sube Instagram)
    ceiling = tp_t
    for _ in range(4):
        gain = lufs_t - medir(pre)["lufs"]
        m = None
        for _ in range(4):
            limit = 10 ** (ceiling / 20)
            run(["ffmpeg", "-v", "error", "-y", "-i", pre, "-af",
                 f"volume={gain:.2f}dB,aresample=192000,alimiter=limit={limit:.4f}:attack=0.5:release=50:level=false,"
                 f"aresample={SR}", "-c:a", "pcm_s24le", d["salida"]])
            m = medir(d["salida"])
            if abs(m["lufs"] - lufs_t) <= 0.2:
                break
            gain += lufs_t - m["lufs"]      # el limitador se comió volumen: compensa y repite
        out = {"audio": d["salida"], "master": m}
        if not d.get("video"):
            break
        root, _ = os.path.splitext(d["video"])
        vout = root + "_sonido.mp4"
        run(["ffmpeg", "-v", "error", "-y", "-i", d["video"], "-i", d["salida"], "-map", "0:v:0", "-map", "1:a:0",
             "-c:v", "copy", "-c:a", "aac", "-b:a", "256k", "-ar", str(SR), "-shortest", "-movflags", "+faststart", vout])
        vm = medir(vout)
        out.update(video=vout, video_master=vm)
        if vm["tp"] <= tp_aac_max:
            break
        ceiling -= (vm["tp"] - tp_aac_max) + 0.2   # el AAC subió el pico: baja el techo y rehaz
    os.remove(pre)
    out["techo_limitador_dbtp"] = round(ceiling, 2)
    return out


def imprimir_qa(ok, avisos, errores):
    for x in ok:
        print("  OK     ", x)
    for x in avisos:
        print("  AVISO  ", x)
    for x in errores:
        print("  ERROR  ", x)
    print("VEREDICTO:", "NO ENTREGAR" if errores else ("revisar avisos" if avisos else "listo"))


def main():
    if len(sys.argv) < 3:
        sys.exit(__doc__)
    cmd, args = sys.argv[1], sys.argv[2:]
    if cmd == "medir":
        for f in args:
            print(f, medir(f))
    elif cmd == "anclas":
        for f in args:
            print(f, anclas(f))
    elif cmd in ("mezclar", "qa"):
        d = colocar(cargar(args[0]))
        for s in d.get("sfx", []):
            print(f"  {s.get('label', os.path.basename(s['file'])):28} t={s['t']:.3f}  anchor={s.get('anchor', 'attack'):6} "
                  f"arranca={s['_inicio']:.3f}  termina={s['_fin']:.3f}")
        res = mezclar(d) if cmd == "mezclar" else None
        if res:
            print(json.dumps(res, ensure_ascii=False, indent=1))
        imprimir_qa(*qa(d, res["master"] if res else None, res.get("video_master") if res else None))
    else:
        sys.exit(__doc__)


if __name__ == "__main__":
    main()
