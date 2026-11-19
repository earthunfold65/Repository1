# Predictor de retención (propio, uso comercial OK)

Sin modelos de licencia no comercial: solo ffmpeg + numpy + matplotlib + nuestro `hookscore.py` (MIT).

## Qué mide
- **Gancho (0–3 s):** hookscore de lo que se dice en los 3 primeros segundos, segundo en que llega la promesa (número / imposible / país), si el fotograma 0 tiene contenido y movimiento.
- **Cuerpo:** cada segundo se va una parte de la audiencia. El riesgo sube con los segundos sin novedad (efecto, escena, número), con silencio y con imagen casi congelada; baja si hay un bucle abierto ("but", "wait", "?", "FACT n/5").
- **Salida:** skip 0–3 s, watch time medio, % que llega al final, zonas de peligro y `curva.png`.

## Uso
```bash
P=~/.venvs/chatter/bin/python
$P -I instagram/scripts/predictor.py VIDEO.mp4 --words audio/words.json --cues cues.json \
   --out instagram/predictor/<slug> --nombre "EP3"
```

## Calibración (cada video publicado lo hace más preciso)
1. A las 48 h, añade una fila a `metricas.csv` con skip % y watch time medio de Insights.
2. `$P -I instagram/scripts/predictor.py --calibrar`
- Con 1–4 videos ajusta 2 parámetros (gancho y caída base). Con ≥ 5 ajusta también el peso del gancho y de los huecos sin novedad.
- Hoy: 1 video (EP1). Error esperado grande (±30 %). Úsalo para COMPARAR versiones, no como cifra exacta.

## Resultados actuales
| Video | Skip 0–3 s | Watch medio | Llegan al final |
|---|---|---|---|
| EP1 Baarle (real) | 48,7 % | 9 s | — |
| EP1 Baarle (pred.) | 48,5 % | 9,0 s | 4 % |
| EP2 v3 (pred.) | 24,5 % | 15,2 s | 9 % |
