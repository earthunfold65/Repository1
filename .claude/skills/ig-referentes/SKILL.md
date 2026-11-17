---
name: ig-referentes
description: Analiza cuentas de Instagram de referentes o competencia, encuentra su reel más viral respecto a la media de cada cuenta, estudia por qué funcionó y por qué fallaron los que tuvieron pocas vistas, y guarda las lecciones en instagram/aprendizajes.md para usarlas en los reels propios. Úsala con "/ig-referentes", "analiza estas cuentas", "aprende de los reels virales de @..." o "por qué este reel pegó y este no".
---

# /ig-referentes — Aprender de reels virales ajenos

Objetivo: no copiar, sino extraer **reglas** que expliquen por qué un reel supera la media de su cuenta y por qué otro se queda corto, y aplicarlas al nicho propio.

## 1. Conseguir los datos
Claude no puede navegar Instagram desde aquí (bloqueado y requiere sesión). Usa la mejor fuente disponible, en este orden:
1. **Videos .mp4** de los reels que el usuario suba al repo (`instagram/referentes/videos/<cuenta>/`). Es lo que permite el análisis más profundo.
2. **Capturas** de la cuadrícula de reels de cada cuenta (muestran vistas en cada miniatura) + capturas de reels concretos.
3. **Lista pegada**: url, vistas, likes, comentarios, duración, de qué trata.
4. **Servicio de scraping** (p. ej. Apify) si el usuario lo quiere y aporta una clave: pídela con `request_credential` para el host del servicio; nunca en el chat.

Pide **8–15 reels por cuenta**, incluidos los flojos: sin flops no se puede saber qué falló. 3–5 cuentas del mismo nicho o de nicho vecino con audiencia parecida.

Vuelca todo en `instagram/referentes/reels.csv` (las capturas: lee los números de la imagen; "12,4 mil" = 12400).

## 2. Ranking por cuenta
```
python3 -I instagram/scripts/analizar_reels.py instagram/referentes/reels.csv instagram/analisis/AAAA-MM-DD-ranking.md
```
El **score = vistas / mediana de su cuenta**. VIRAL ≥ 3 · BUENO ≥ 1,5 · FLOP ≤ 0,5. No compares vistas absolutas entre cuentas de tamaño distinto. Avisa si una cuenta tiene < 8 reels.

## 3. Disección (el viral #1 de cada cuenta + 2 flops de la misma cuenta)
Si hay video:
```
bash instagram/scripts/extraer_frames.sh <video.mp4> instagram/referentes/analisis/<cuenta>-<id>
```
Mira los fotogramas (`hook_0s.jpg` … y `t_*.jpg`) con Read, y transcribe `audio.mp3` (ElevenLabs `creative_transcribe_audio` si está conectado).

Rellena esta ficha para cada reel analizado:
| Aspecto | Qué mirar |
|---|---|
| Primer fotograma | ¿Para el dedo sin sonido? ¿Cara, movimiento, texto grande, algo raro? |
| Hook (0–3 s) | Texto hablado y en pantalla; fórmula # de `../ig-reel/hooks.md`; ¿promete algo concreto? |
| Tema / ángulo | ¿Curiosidad universal o nicho cerrado? ¿Ángulo nuevo o repetido? |
| Estructura | Hook → tensión → payoff; ¿cuándo llega el payoff?; ¿hay bucle (final enlaza con el inicio)? |
| Ritmo | Duración, segundos por plano (`info.txt`), silencios, relleno |
| Texto en pantalla | Tamaño, legibilidad, zona segura (no tapado por la interfaz) |
| Audio | Voz, música, SFX, audio en tendencia |
| CTA | ¿Pide guardar/compartir/comentar? ¿Mata la retención antes de tiempo? |
| Caption y portada | Primera línea, palabras clave |
| Contexto | Fecha (¿tema de actualidad?), colaboración, si parece promocionado |

## 4. Viral vs flops: diagnóstico
Compara el viral con los flops **de la misma cuenta** (mismo público, misma cara: lo que cambia es el reel). Para cada flop indica la causa más probable:
- Hook lento (lo interesante llega después del segundo 3) o sin promesa clara.
- Primer fotograma estático / sin texto / ilegible.
- Tema demasiado de nicho o ya muy visto.
- Payoff flojo o que nunca llega → la gente no termina el video.
- Demasiado largo para lo que cuenta; planos de > 4 s sin cambio.
- CTA o autopromoción al principio.
- Calidad (audio malo, vertical mal encuadrado, texto bajo la interfaz).
Distingue causa observada de hipótesis. Recuerda: también influyen factores invisibles (hora, algoritmo, anuncios pagados); dilo cuando la diferencia no se explique por el contenido.

## 5. Guardar lo aprendido
Actualiza `instagram/aprendizajes.md` siguiendo su formato: reglas accionables con evidencia (cuenta, reel, score), marcadas **hipótesis** o **confirmada** (3+ ejemplos de cuentas distintas). Añade los hooks reales que funcionaron y 3–5 ideas adaptadas al nicho de `instagram/marca.md`. No borres reglas antiguas: si algo las contradice, anótalo.

## 6. Entregable al usuario
- Top viral por cuenta con su score y la razón principal en una frase.
- Los 3–5 patrones ganadores más sólidos y los 3–5 errores de los flops.
- 3 ideas de reel para su cuenta listas para `/ig-reel`.
- Rutas del ranking y de `aprendizajes.md`.
