---
name: eu-voice
description: Escribe ganchos, guiones, rótulos y captions con la voz de EarthUnfold (Border Oddities) y los verifica con hookscore, detect y caption lint antes de enseñarlos. Úsala al escribir cualquier texto del canal: "gancho para…", "caption para…", "reescríbelo con nuestra voz", o como último paso de /ig-reel y /ig-caption.
---

# /eu-voice — escribir como EarthUnfold

1. Lee `instagram/voice.md` (voz, palabras sí/no, ritmo) y `instagram/playbook_viralidad.md`.
2. Escribe 5 ganchos distintos (fórmulas de `../ig-reel/hooks.md` / `hooks.json`): el dato imposible primero, número o nombre concreto, algo en juego, ≤ 12 palabras.
3. **Puntúa** y elige el mejor; si el mejor no llega a 50, reescribe:
   `python3 -I .claude/skills/ig-reel/hookscore.py ganchos.txt`
   (detecta bien ganchos flojos, AUC 0,83; no distingue entre dos buenos: decide el retention graph).
   Referencia propia: EP.1 "In this town…" = 26,8 (48,7 % de skip real) · EP.2 "This hill is in three countries… used to be four" = 54,9.
4. Guion → beat sheet con tiempos al ritmo real: `python3 -I .claude/skills/ig-reel/beats.py guion.txt --wpm 185`.
5. **Caption**: escribe y pasa los dos filtros hasta PASS/READY:
   `python3 -I .claude/skills/ig-human/detect.py caption.txt` (HUMAN SCORE ≥ 70, sin rayas —, variedad de longitud de frase, "you" y contracciones)
   `python3 -I .claude/skills/ig-caption/caption.py caption.txt` (primera línea entera antes del "… more", una sola petición reconocible, hashtags abajo)
   Si hace falta limpiar: `python3 -I .claude/skills/ig-human/humanize.py caption.txt`.
6. Entrega el texto final con las tres notas.
