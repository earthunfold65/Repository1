---
name: ig-sonido
description: Diseño de sonido profesional para reels y videos hechos con código (Remotion, HyperFrames, GSAP) — voz, música con ducking, efectos sincronizados al fotograma exacto con grabaciones reales y licencias verificadas, master a −14 LUFS / −1 dBTP medido en el MP4 final, y QA automático. Úsala cuando un reel necesite sonido, SFX, whooshes, pops, música, mezcla, master o "que suene profesional", y como paso final de /ig-reel cuando se produzca el video.
---

# /ig-sonido — Sonido sin errores

Eres el supervisor de sonido de un video que **no puedes oír**. Por eso todo se decide con números, fotogramas y reglas, y al final le dices al usuario exactamente qué momentos escuchar. Nunca digas "suena bien": di qué mediste.

Reglas completas: `reglas.md` (en esta carpeta). Léelas antes de diseñar.

## 0. Qué hay ya
- ¿Hay voz (ElevenLabs o grabada)? ¿Música? ¿El render trae audio sintetizado? Si lo trae, **se reemplaza, no se superpone**.
- Si la música será un audio en tendencia de Instagram: el MP4 sale sin música y el usuario la añade al publicar; diseña los efectos dejando sitio para ella.

## 1. Lista de cues desde el código de la animación
Cada sonido va en un fotograma que calcula el propio código (Remotion: `frame / fps`; HyperFrames: `data-start` + duraciones; GSAP: las posiciones de la timeline). Nunca horas escritas a ojo.
Para cada evento: qué pasa en pantalla → qué sonido según la tabla de `reglas.md` §2 (incluido "nada") → `anchor`.
Si solo hay un video ya renderizado: `bash instagram/scripts/extraer_frames.sh` y revisa los fotogramas para encontrar los eventos.

## 2. Conseguir sonidos reales (por orden)
1. **Librería propia del usuario** en `instagram/sonido/libreria/` (lo mejor: él la eligió).
2. **Openverse → Freesound** (CC0 / CC BY, preview HQ ~192 kbps), con el script que verifica la licencia en la página de cada sonido:
   ```
   python3 -I instagram/scripts/buscar_sonido.py buscar "swipe whoosh" --max-ms 900
   python3 -I instagram/scripts/buscar_sonido.py bajar <id_openverse> --rol whoosh
   ```
   Busca en inglés (así están etiquetados). Baja 3–5 candidatos por rol y elige midiendo. Si la página y Openverse no coinciden, el script lo descarta solo.
   **Mixkit** (WAV, licencia gratuita: assets.mixkit.co) también está permitido en la red; anota la licencia a mano en `licencias.md`.
   El entorno "Repository1" permite estos hosts (cdn.freesound.org, freesound.org, api.openverse.org, assets.mixkit.co, mixkit.co).
3. **ElevenLabs** (conectado): voz en off y efectos generados como último recurso para un efecto concreto; avisa de que es generado y revísalo igual que una grabación.
- Nunca sintetices efectos con código (senoidales, ruido filtrado): es la señal nº 1 de sonido barato.
- Cada archivo: licencia leída en su página → anótala en `instagram/sonido/licencias.md` (archivo, URL, licencia, autor, fecha). Licencia dudosa = fuera.
- Mide cada candidato: `python3 -I instagram/scripts/sonido.py anclas archivo.wav` (ataque, pico, final audible). Descarta los que tengan silencio largo, pico tardío para un golpe, o duren demasiado para el momento.

## 3. Diseño
Escribe `instagram/sonido/<slug>/diseno.json` (formato en el encabezado de `instagram/scripts/sonido.py`):
- voz a 0 dB, música −16…−20 dB con `duck_db` 6–10, efectos −6…−12 dB (más bajos con voz encima).
- Respeta: ~5 efectos / 10 s, 2 whooshes por video como máximo, nada en los cortes duros, una paleta, una voz de clic.

## 4. Mezclar, masterizar, comprobar
```
python3 -I instagram/scripts/sonido.py mezclar instagram/sonido/<slug>/diseno.json
```
Hace: colocación por ancla, ducking de música bajo la voz, suma, master a −14 LUFS con limitador true-peak, mux al MP4 y **vuelve a medir el MP4** (el AAC sube los picos; si pasa de −1 dBTP baja el techo y rehace solo).
El QA imprime OK / AVISO / ERROR. **Con un ERROR no se entrega.** Cada AVISO se corrige o se justifica por escrito.

## 5. Revisión visual
- Saca fotogramas del MP4 final alrededor de cada efecto (`ffmpeg -ss <t-0.1> -frames:v 1`) y confirma que el sonido coincide con el evento.
- Comprueba que ningún efecto pisa una palabra de la voz (si hay transcripción con tiempos, compáralos).

## 6. Entrega
- MP4 con sonido + WAV separado + `diseno.json` + `licencias.md`.
- Créditos CC BY listos para pegar en el caption.
- **3–5 momentos para que el usuario escuche** (con segundo exacto) y qué preguntarse en cada uno: ¿se entiende la voz?, ¿el golpe cae en el fotograma?, ¿algo chirría en el altavoz del móvil? Recomienda una escucha en el altavoz del móvil, no solo con auriculares.

## Herramientas originales (opcional, más potentes)
`earshot` (escucha con modelos: describir, comparar, real vs sintético, informe frente a películas profesionales) y `real-sfx` necesitan instalar su código, PyTorch (~1 GB de modelos desde huggingface.co) y hosts de red que este entorno bloquea. Solo con permiso explícito del usuario. Mientras tanto esta skill aplica su método con ffmpeg.
