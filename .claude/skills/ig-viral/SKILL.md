---
name: ig-viral
description: Analiza métricas de posts de Instagram (propios o de referentes) para encontrar qué funciona — outliers, patrones de hook, formato, tema y duración — y propone ideas para replicarlo. Úsala con "/ig-viral", "qué me funciona", "por qué este reel pegó" o al pasar un CSV/captura de métricas.
---

# /ig-viral — Encuentra lo que funciona

## Datos
Claude no puede leer Instagram directamente desde aquí. Pide UNA de estas fuentes:
- CSV/Excel exportado (Meta Business Suite → Contenido → Exportar), o
- tabla pegada / capturas de Insights, o
- lista de reels de referentes con vistas aproximadas y tema.

Mínimo útil: 10 posts. Campos ideales: fecha, formato, tema/hook, duración, alcance o vistas, me gusta, comentarios, guardados, compartidos, seguidores ganados.

Si llegan archivos, procésalos con un script (Python/Node) en el scratchpad; no hagas cuentas de cabeza.

## Análisis
1. **Normaliza:** tasa de interacción = (likes + comentarios + guardados + compartidos) / alcance. Calcula también guardados/alcance y compartidos/alcance (las dos señales más fuertes).
2. **Outliers:** posts con vistas o interacción ≥ 2× la mediana de la cuenta. Esos son los "virales" reales para ESTA cuenta.
3. **Etiqueta** cada post: fórmula de hook (usa `../ig-reel/hooks.md`), formato, pilar, duración, tipo de CTA.
4. **Compara** outliers vs. resto: qué etiquetas se repiten arriba y faltan abajo.
5. **Descarta casualidades:** si un patrón se apoya en 1 solo post, dilo.

## Entregable
- Tabla top 5 posts con métricas normalizadas y por qué funcionaron.
- **3–5 patrones** ganadores, cada uno con la evidencia (qué posts).
- **Qué dejar de hacer** (patrones de los peores).
- **5 ideas nuevas** que replican los patrones; cada una con hook listo y lista para `/ig-reel`.
- Añade las reglas nuevas a `instagram/aprendizajes.md` (mismo formato que usa `/ig-referentes`).
- Para analizar cuentas ajenas usa `/ig-referentes`.
- Guarda el informe en `instagram/analisis/AAAA-MM-DD-viral.md`.
