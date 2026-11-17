---
name: ig-carousel
description: Diseña carruseles de Instagram — estructura slide a slide, textos y notas de diseño — y opcionalmente genera las imágenes PNG 1080×1350. Úsala con "/ig-carousel", "hazme un carrusel" o "convierte esto en slides".
---

# /ig-carousel — Carrusel

Entrada: tema o texto fuente. Lee `instagram/marca.md`. Lee también `instagram/aprendizajes.md`: aplica los patrones ganadores, evita los errores listados y, si contradices una regla confirmada, dilo y explica por qué.

## Estructura (7–10 slides)
1. **Portada:** hook de ≤ 8 palabras (usa `../ig-reel/hooks.md`) + subtítulo opcional. Tiene que funcionar como miniatura en el feed.
2. **Slide 2 — re-gancho:** el problema o la promesa concreta; razón para seguir deslizando (Instagram vuelve a mostrar el carrusel desde la slide 2).
3. **Slides de contenido:** una idea por slide, ≤ 30 palabras, título grande + 1–2 líneas.
4. **Penúltima:** resumen / checklist (la slide que se guarda).
5. **Última:** CTA único + recordatorio de quién eres.

## Entregable
Tabla: `# | Título | Texto | Visual / nota de diseño`. Luego caption (versión media de `/ig-caption`).

## Opcional: generar las imágenes
Si el usuario lo pide:
1. Crea `instagram/carruseles/<slug>/slides.html` con una sección de 1080×1350 px por slide (paleta y tipografía de la marca; por defecto fondo oscuro #111, acento #F0A93B, tipografía display condensada).
2. Exporta cada slide a PNG con Playwright (ya instalado: `require('playwright')`, `chromium.launch()`), `deviceScaleFactor: 1`, a `instagram/carruseles/<slug>/01.png`, `02.png`…
3. Revisa visualmente al menos portada y última slide antes de entregar; corrige texto cortado o desbordado.
