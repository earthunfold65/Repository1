#!/usr/bin/env python3
"""Genera la voz en off completa de un reel, frase a frase, con Kokoro (gratis) y tiempos de palabra.

  python3 -I instagram/scripts/montar_voz.py <carpeta_audio> [--voz am_adam] [--vel 1.08] [--inicio 0.05] [--motor kokoro|chatterbox]
  (con --motor chatterbox, antes: ~/.venvs/chatter/bin/python -I instagram/scripts/voz_chatterbox.py <carpeta_audio>)

<carpeta_audio>/chunks.json = [["Frase uno.", pausa_s], ["Frase dos...", pausa_s], ...]
Salida en <carpeta_audio>: vo.wav (48 kHz) y words.json (mismo formato que Scribe: words[].text/start/end).
Las frases se generan por separado: el inicio de cada una es exacto; dentro de una frase la palabra se
estima por número de letras (error típico < 0,1 s en frases cortas).
"""
import json
import os
import re
import subprocess
import sys

PY = os.environ.get("VOZ_PYTHON") or next((p for p in (os.path.expanduser("~/.venvs/audio/bin/python"), "/home/user/.venvs/audio/bin/python") if os.path.exists(p)), "python3")
VOZ_PY = os.path.join(os.path.dirname(os.path.abspath(__file__)), "voz.py")
SR = 48000


def opt(name, default):
    if name in sys.argv:
        i = sys.argv.index(name)
        return sys.argv[i + 1]
    return default


def dur(f):
    return float(subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", f],
                                capture_output=True, text=True, check=True).stdout)


def main():
    if len(sys.argv) < 2:
        sys.exit(__doc__)
    d = os.path.abspath(sys.argv[1])
    voz, vel, t = opt("--voz", "am_adam"), opt("--vel", "1.08"), float(opt("--inicio", "0.05"))
    ch = json.load(open(os.path.join(d, "chunks.json"), encoding="utf-8"))
    os.makedirs(os.path.join(d, "chunks"), exist_ok=True)
    words, parts = [], []
    for i, item in enumerate(ch):
        text, pause = item[0], item[1]
        txt, raw, cut = (os.path.join(d, "chunks", f"{p}{i:02d}.{e}") for p, e in (("c", "txt"), ("c", "wav"), ("t", "wav")))
        open(txt, "w", encoding="utf-8").write(text)
        if opt("--motor", "kokoro") == "kokoro":
            subprocess.run([PY, "-I", VOZ_PY, voz, vel, raw, txt], check=True, capture_output=True)
        elif not os.path.exists(raw):
            sys.exit(f"Falta {raw}: genera antes las frases con voz_chatterbox.py")
        subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", raw, "-af",
                        "silenceremove=start_periods=1:start_threshold=-45dB:start_silence=0.02,areverse,"
                        "silenceremove=start_periods=1:start_threshold=-45dB:start_silence=0.04,areverse,afade=t=in:d=0.005",
                        "-ar", str(SR), "-ac", "1", "-c:a", "pcm_s24le", cut], check=True)
        L = dur(cut)
        toks = text.split()
        w = [len(re.sub(r"[^\w']", "", x)) + 1 for x in toks]
        tot, acc = sum(w), 0
        for x, wi in zip(toks, w):
            s = t + L * acc / tot
            acc += wi
            words.append({"text": x, "type": "word", "start": round(s, 3), "end": round(t + L * acc / tot, 3)})
        parts.append((cut, t))
        print(f"  {t:6.2f}  {text}")
        t += L + float(pause)
    ins, fl = [], []
    for k, (f, st) in enumerate(parts):
        ins += ["-i", f]
        fl.append(f"[{k}:a]adelay={int(round(st * 1000))}:all=1[a{k}]")
    fl.append("".join(f"[a{k}]" for k in range(len(parts))) +
              f"amix=inputs={len(parts)}:normalize=0:duration=longest,apad,atrim=0:{t + 0.3:.3f}[o]")
    subprocess.run(["ffmpeg", "-v", "error", "-y", *ins, "-filter_complex", ";".join(fl), "-map", "[o]",
                    "-ar", str(SR), "-c:a", "pcm_s24le", os.path.join(d, "vo.wav")], check=True)
    json.dump({"words": words}, open(os.path.join(d, "words.json"), "w"), indent=0)
    print(f"voz: {t:.2f} s · {len(words)} palabras → {d}/vo.wav, words.json")


if __name__ == "__main__":
    main()
