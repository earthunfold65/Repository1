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
