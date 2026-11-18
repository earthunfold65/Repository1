#!/usr/bin/env python3
"""Voz en off gratis y local con Kokoro-82M (licencia Apache-2.0, uso comercial permitido). Sin créditos ni límites.

  /home/user/.venvs/audio/bin/python -I instagram/scripts/voz.py list
  /home/user/.venvs/audio/bin/python -I instagram/scripts/voz.py <voz> <velocidad> salida.wav guion.txt

Instalar (una vez): python3 -m venv ~/.venvs/audio && ~/.venvs/audio/bin/pip install kokoro-onnx soundfile
Modelo: lo descarga `npx hyperframes tts` la primera vez en ~/.cache/hyperframes/tts/ (HYPERFRAMES_PYTHON=~/.venvs/audio/bin/python).
"""
import os
import sys

import soundfile as sf
from kokoro_onnx import Kokoro

BASE = os.path.expanduser("~/.cache/hyperframes/tts")
k = Kokoro(f"{BASE}/models/kokoro-v1.0.onnx", f"{BASE}/voices/voices-v1.0.bin")
if len(sys.argv) < 2 or sys.argv[1] == "list":
    print(" ".join(v for v in k.get_voices() if v[:2] in ("am", "bm", "af", "bf")))
    sys.exit()
voice, speed, out, txt = sys.argv[1], float(sys.argv[2]), sys.argv[3], sys.argv[4]
samples, sr = k.create(open(txt, encoding="utf-8").read(), voice=voice, speed=speed,
                       lang="en-us" if voice[0] == "a" else "en-gb")
import numpy as np
peak = float(np.max(np.abs(samples))) if len(samples) else 0.0
if peak > 0.891:  # Kokoro puede salir a fondo de escala: deja 1 dB de margen para no recortar
    samples = samples * (0.891 / peak)
sf.write(out, samples, sr, subtype="PCM_24")
print(out, round(len(samples) / sr, 2), "s")
