# Reglas del proyecto

## Gasto de créditos (obligatorio)
- **Nunca gastar créditos de ElevenLabs (ni de ningún servicio de pago: Higgsfield, HeyGen, etc.) sin preguntar antes al usuario.**
  Primero `estimate_only: true`, luego decirle el coste (créditos y $) y qué se va a generar, y esperar su "sí".
- Esto incluye voz (TTS), efectos, música, imágenes, video y transcripciones con coste. Una transcripción que la estimación da a 0 créditos también se anuncia.
- Una aprobación vale para esa generación concreta, no para las siguientes.

## Idioma
- Hablar con el usuario en español. Los videos de EarthUnfold van en inglés.

## Voz en off
- Por defecto, voz **expresiva gratis con Chatterbox** (`instagram/scripts/voz_chatterbox.py`, venv `/home/user/.venvs/chatter`, `HF_HUB_DISABLE_XET=1`), imitando la voz elegida por el usuario (Kokoro `am_adam`, referencia en `instagram/produccion/moresnet/audio/ref_adam.wav`). Emoción por frase en `chunks.json` (3.er valor).
- Flujo: `voz_chatterbox.py` → `montar_voz.py --motor chatterbox --tempo 1.07 --pausas 0.7` → `alinear_palabras.py` (verifica con Whisper y da tiempos reales).
- Kokoro (`voz.py`) solo como respaldo rápido. ElevenLabs solo si el usuario lo pide y aprueba el coste.

## Estándar creativo (feedback del usuario, 2026-11-18)
- Nada de contenido "plano": gancho de deseo/imposible en primera persona ("Imagine…"), sorpresa cada 3–4 s, humor, algo en juego, pregunta para comentar al final.
- Música de nivel constante (bucle estable), ducking suave; nunca música que "sube y baja". Entregar también versión SIN música para usar audio en tendencia en la app.
- Voz con matices: emoción alta en sorpresas, pausas dramáticas, ritmo ágil.

## Oído antes de entregar (obligatorio)
- Tras mezclar: `HF_HUB_DISABLE_XET=1 ~/.venvs/chatter/bin/python -I instagram/scripts/oido.py <video.mp4> <cues.json>` (earshot: sincronía de cada efecto, audibilidad sobre voz/música, crítica vs. 7 películas pro, hoja PNG, cómo suena cada SFX).
- Solo se entrega con **VEREDICTO: ENTREGAR**. Efecto tarde/adelantado → moverlo; inaudible (< +3 dB) → subirlo, cambiarlo por uno que corte o quitarlo; "needs work" → arreglar lo que diga "FIX FIRST". Abrir y mirar `out/oido/sheet.png`.
- Skills instaladas en el proyecto: `earshot`, `real-sfx` (con librería `instagram/sonido/libreria` + uisfx CC0), `real-sound`.
- Sonidos buenos medidos: pops `pop/earshot_ui_pop_*.wav`, capa grave `sub/earshot_cut_hit_punch.wav` bajo golpes grandes, clic `click/uisfx_soft_select.mp3` (anclar por pico). Evitar `fs-488534_ui-click` (earshot: suena a tecla de teclado).

## Skills y playbook (leer antes de crear)
- Antes de idear/guionizar/editar un video: leer `instagram/playbook_viralidad.md` y `.agents/product-marketing.md`.
- Skills instaladas en `.claude/skills/` (find-skills de Vercel + marketing de coreyhaines31 + Remotion oficial + diseño de Anthropic + Vercel guidelines). Instalar más con `npx -y skills add <owner/repo> --skill <nombre> -a claude-code -y` (skills.sh está bloqueado; GitHub sí funciona) y **revisar su contenido antes de usarlas**.
