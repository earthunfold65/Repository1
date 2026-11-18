#!/usr/bin/env python3
"""Voz expresiva gratis con Chatterbox (Resemble AI, licencia MIT: uso comercial permitido). CPU, sin créditos.

  /home/user/.venvs/chatter/bin/python -I instagram/scripts/voz_chatterbox.py <carpeta_audio> [--ref voz_referencia.wav] [--cfg 0.4]

Lee <carpeta_audio>/chunks.json = [[frase, pausa_s, emocion], ...]
  emocion (exaggeration) 0.3 = calmado · 0.5 = natural · 0.7–1.0 = sorprendido / enfático.
Escribe <carpeta_audio>/chunks/cNN.wav (una por frase). Después: montar_voz.py --motor chatterbox.
--ref: clip de 6–15 s de la voz a imitar (opcional; sin él usa la voz por defecto del modelo).
--cfg: ritmo (0.3 = más lento y dramático, 0.5 = estándar).
"""
import json
import os
import sys

import numpy as np
import soundfile as sf
import torch
from chatterbox.tts import ChatterboxTTS


def opt(name, default):
    return sys.argv[sys.argv.index(name) + 1] if name in sys.argv else default


def main():
    if len(sys.argv) < 2:
        sys.exit(__doc__)
    d = os.path.abspath(sys.argv[1])
    ref, cfg = opt("--ref", None), float(opt("--cfg", "0.4"))
    torch.manual_seed(7)  # tomas reproducibles
    model = ChatterboxTTS.from_pretrained(device="cpu")
    ch = json.load(open(os.path.join(d, "chunks.json"), encoding="utf-8"))
    os.makedirs(os.path.join(d, "chunks"), exist_ok=True)
    for i, item in enumerate(ch):
        text, emo = item[0], float(item[2]) if len(item) > 2 else 0.5
        wav = model.generate(text, audio_prompt_path=ref, exaggeration=emo, cfg_weight=cfg)
        a = wav.squeeze(0).cpu().numpy().astype(np.float32)
        peak = float(np.max(np.abs(a))) or 1.0
        if peak > 0.891:
            a *= 0.891 / peak
        out = os.path.join(d, "chunks", f"c{i:02d}.wav")
        sf.write(out, a, model.sr, subtype="PCM_24")
        print(f"  {i:02d} emo={emo:.2f} {len(a) / model.sr:5.2f}s  {text}", flush=True)


if __name__ == "__main__":
    main()
