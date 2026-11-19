---
name: ig-human
description: Reescribe textos para que suenen humanos y con la voz de la marca, quitando muletillas y patrones típicos de IA. Úsala con "/ig-human", "que no suene a IA", "humaniza esto" o automáticamente como último paso de las otras skills /ig-*.
---

# /ig-human — Que suene a persona

Entrada: un texto (guion, caption, DM). Lee la sección **Voz** de `instagram/marca.md`.

## Elimina
- Aperturas vacías: "En el mundo actual…", "Hoy en día…", "¿Alguna vez te has preguntado…?", "Imagina…".
- Estructuras de IA: "No es X, es Y" en serie; tríadas forzadas ("rápido, fácil y eficaz"); cada párrafo cerrando con moraleja.
- Palabras infladas: "potenciar", "desbloquear", "sumergirse", "crucial", "fascinante", "transformador", "viaje", "elevar", "sin duda".
- Rayas (—) en exceso, punto y coma, signos de exclamación en cada frase, emojis decorativos en cada línea.
- Cierres tipo "¡Espero que te sirva!" o "En resumen…".

## Añade
- Detalle concreto (número, nombre, lugar, error real) donde haya generalidades.
- Ritmo variado: alguna frase de 3 palabras entre otras largas.
- Las expresiones propias y el trato (tú/vos/usted) de la ficha de marca.
- Lenguaje hablado si es guion: contracciones, "mira", "o sea", según el país.

## Entregable
El texto reescrito. Debajo, máx. 5 viñetas con los cambios más importantes. No cambies datos ni el mensaje de fondo.

## Herramientas (MIT, repo original)
- Detectar: `python3 -I .claude/skills/ig-human/detect.py texto.txt` (5 señales: burstiness, specificity, slop, fingerprint, voice).
- Limpiar: `python3 -I .claude/skills/ig-human/humanize.py texto.txt --report` (quita rayas, vocabulario de IA y caracteres invisibles; lista en `slop.json`).
