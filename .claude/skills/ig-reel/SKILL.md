---
name: ig-reel
description: Crea un borrador completo de Reel de Instagram — hook (con 26 fórmulas), guion, texto en pantalla y beat sheet segundo a segundo. Úsala cuando pidan un reel, un guion de video corto, un hook o "/ig-reel <tema>".
---

# /ig-reel — Borrador de Reel

Entrada: un tema, una idea o un texto fuente (`$ARGUMENTS`). Si no hay tema, pregúntalo en una línea.

## Antes de escribir
1. Lee `instagram/marca.md` (audiencia, voz, oferta, trato). Si no existe o está vacío, sigue con tono neutro y dilo al final.
2. Lee también `instagram/aprendizajes.md`: aplica los patrones ganadores, evita los errores listados y, si contradices una regla confirmada, dilo y explica por qué.
3. Lee `hooks.md` (en esta misma carpeta): las 26 fórmulas de hook.
4. Decide la duración: 15–30 s por defecto; 30–60 s solo si el tema necesita pasos.

## Entregable (en este orden)

### 1. HOOK — 3 opciones
- Cada una con una fórmula distinta de `hooks.md`; indica el número: `#3 Error común`.
- Máx. 12 palabras habladas. Debe entenderse **sin sonido** (también va como texto en pantalla).
- Marca la recomendada con ⭐ y explica en una línea por qué.

### 2. GUION
- Habla como persona, frases de ≤ 15 palabras, una idea por frase.
- Estructura: hook (0–3 s) → tensión / promesa → 3 puntos o pasos máx. → payoff → CTA.
- Un solo CTA, coherente con la oferta de la marca (seguir, guardar, comentar palabra clave, link).
- Pasa el texto por las reglas de `/ig-human` (sin muletillas de IA).

### 3. TEXTO EN PANTALLA
- Lista de rótulos con su segundo de entrada. Máx. 6 palabras por rótulo.
- Nunca copiar el guion completo: el rótulo resume o contrasta.

### 4. BEAT SHEET
Tabla con un cambio visual cada 1,5–3 s:

| Seg. | Visual / plano | Voz | Texto en pantalla | Sonido / SFX |
|------|----------------|-----|-------------------|--------------|

### 5. Extras
- Caption corto (usa las reglas de `/ig-caption`, versión corta).
- Sugerencia de audio (tipo de música o "trending audio" de la categoría X; no inventes nombres de canciones).
- Portada: texto de 3–5 palabras.

## Guardar
Guarda el borrador en `instagram/reels/AAAA-MM-DD-<slug>.md` y di la ruta.

## Opcional: producirlo
Si el usuario quiere el video, ofrece montarlo con **Remotion** o **HyperFrames** + **GSAP** (instalados en el repo) a 1080×1920, 30 fps, usando el beat sheet como línea de tiempo. Voz en off: ElevenLabs si está conectado.
