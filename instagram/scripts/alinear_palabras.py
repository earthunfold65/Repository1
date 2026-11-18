#!/usr/bin/env python3
"""Refina words.json con tiempos REALES de cada palabra (faster-whisper local, gratis) y verifica la locución.

  ~/.venvs/chatter/bin/python -I instagram/scripts/alinear_palabras.py <carpeta_audio>

Necesita: chunks.json, chunks/tNN.wav (frases recortadas) y chunk_starts.json (los escribe montar_voz.py).
Si Whisper oye otra cosa que el guion en una frase, lo avisa (REVISAR) y deja la estimación por letras.
Une números dichos con letras para los subtítulos: "eighteen sixteen..." → "1816...".
"""
import json, os, re, subprocess, sys
import numpy as np
from faster_whisper import WhisperModel

NUM = {("eighteen", "sixteen"): "1816", ("nineteen", "twenty"): "1920"}


def load(f):
    raw = subprocess.run(["ffmpeg", "-v", "error", "-i", f, "-ac", "1", "-ar", "16000", "-f", "f32le", "-"], capture_output=True).stdout
    return np.frombuffer(raw, np.float32)


def clean(s):
    return re.sub(r"[^a-z0-9']", "", s.lower())


def main():
    d = os.path.abspath(sys.argv[1])
    ch = json.load(open(os.path.join(d, "chunks.json")))
    starts = json.load(open(os.path.join(d, "chunk_starts.json")))
    est = json.load(open(os.path.join(d, "words.json")))["words"]
    m = WhisperModel("small.en", device="cpu", compute_type="int8")
    out, k, avisos = [], 0, []
    for i, item in enumerate(ch):
        toks = item[0].split()
        mine = est[k:k + len(toks)]
        k += len(toks)
        segs, _ = m.transcribe(load(os.path.join(d, "chunks", f"t{i:02d}.wav")), language="en", word_timestamps=True)
        ws = [w for s in segs for w in s.words]
        if len(ws) == len(toks):
            for tok, w in zip(toks, ws):
                out.append({"text": tok, "type": "word", "start": round(starts[i] + w.start, 3), "end": round(starts[i] + w.end, 3)})
        else:
            heard = " ".join(w.word.strip() for w in ws)
            if [clean(x) for x in heard.split()] != [clean(x) for x in toks]:
                avisos.append(f"frase {i + 1}: guion «{item[0]}» · oído «{heard}»")
            out.extend(mine)
    # números con letras → cifra en los subtítulos
    j, res = 0, []
    while j < len(out):
        pair = (clean(out[j]["text"]), clean(out[j + 1]["text"])) if j + 1 < len(out) else None
        if pair in NUM:
            tail = re.sub(r"^[A-Za-z']+", "", out[j + 1]["text"])
            res.append({**out[j], "text": NUM[pair] + tail, "end": out[j + 1]["end"]})
            j += 2
        else:
            res.append(out[j]); j += 1
    json.dump({"words": res}, open(os.path.join(d, "words.json"), "w"), indent=0)
    print(f"{len(res)} palabras con tiempos reales → words.json")
    for a in avisos:
        print("  REVISAR", a)


if __name__ == "__main__":
    main()
