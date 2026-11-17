---
name: ig-audit
description: Hace una auditoría completa de una cuenta de Instagram — perfil, contenido, hooks, constancia, interacción y conversión — con puntuación y plan de acción priorizado. Úsala con "/ig-audit", "audita mi cuenta" o "por qué no crezco".
---

# /ig-audit — Auditoría de cuenta

## Datos necesarios
Claude no puede abrir Instagram desde aquí. Pide:
- Captura del perfil (bio, destacados, primeras filas del feed).
- Los últimos 12–20 posts con métricas (CSV de Meta Business Suite o capturas de Insights).
- Seguidores actuales y de hace 30/90 días, si los tiene.
- Objetivo de la cuenta (crecer, vender, marca personal).

Si faltan datos, audita lo que haya y marca cada categoría como "sin datos".

## Categorías (puntúa 1–10 cada una)
1. **Perfil** — criterios de `/ig-profile`.
2. **Hooks** — ¿los primeros 2 s y la portada paran el dedo? (fórmulas de `../ig-reel/hooks.md`).
3. **Contenido** — claridad de nicho, pilares, valor guardable.
4. **Formatos** — mezcla reels / carruseles / historias.
5. **Constancia** — frecuencia y regularidad reales.
6. **Interacción** — tasas de guardado y compartido (cálculo de `/ig-viral`), respuesta a comentarios.
7. **Conversión** — CTA, link, palabra clave, camino de seguidor a cliente.

## Entregable
- Tabla de puntuación con 1 frase de evidencia por categoría y nota global.
- **Top 3 arreglos** de mayor impacto / menor esfuerzo, con la skill /ig-* que lo resuelve.
- Plan de 30 días (semana a semana).
- Guarda en `instagram/analisis/AAAA-MM-DD-auditoria.md`.
