# Reglas profesionales de sonido para reels

Destilado de **earshot / real-sound** (Leon Lin, MIT — github.com/Leonxlnx/earshot) y **real-sfx** (Clipwing — github.com/Clipwing/skills), que miden películas de lanzamiento profesionales. Las cifras marcadas *(norma)* son medidas; el resto es práctica probada.

## 1. El listón
- **Todo sonido tiene una causa visible** y un volumen proporcional a ella: un cursor susurra, el reveal golpea.
- **Una sola paleta:** una familia de materiales (p. ej. plástico suave + madera), una sola voz de clic y una sola pista de música. Mezclar materiales es la forma más rápida de sonar barato.
- **La música carga el video**; los efectos puntúan. Restricción: ~5 efectos diseñados cada 10 s *(norma)*. El buen diseño sonoro casi no se nota.
- **Los 2 primeros segundos nunca en silencio** (el 100 % de las referencias suena ahí) *(norma)*. Ningún hueco de más de 3–4 s sin razón.

## 2. Qué suena con cada cosa en pantalla
| En pantalla | Sonido | Dónde cae (`anchor`) | Nivel / notas |
|---|---|---|---|
| Cursor que se mueve, scroll, barras de progreso, texto que fluye, contadores rodando | **nada** | | la música cubre el movimiento continuo |
| Clic / tap | UNA voz de clic real para todo el video, siempre igual | `attack` en el fotograma del clic (10–30 ms antes está bien) | ~3 dB bajo la música, centrado |
| Tecleo | teclado real troceado | cada tecla sonora | máx. ~12 teclas/s; la música baja 6–10 dB; la mayoría del tecleo en pantalla en videos pro va **en silencio** (~75 %) *(norma)* |
| Aparece una tarjeta / chip / etiqueta | pop o tick suave | `attack` al 50 % de su recorrido | en una serie, el tono sube (+1…+3 semitonos) |
| Interruptor, encaje, candado, contador que fija su valor | clic / latch seco | `attack` en el contacto | corto; un tick solo en el valor final |
| Zoom, látigo de cámara, gran movimiento | whoosh real | `peak` en el pico de velocidad | **~2 por video**, nunca en cada corte |
| Cortes duros | **nada** | | ~85 % de los cortes pro no tienen sonido propio *(norma)* |
| Tensión antes del reveal | riser (o el build de la música) | `end` 30–250 ms **antes** del golpe | deja un respiro; nunca un crash en el golpe |
| El reveal / el giro | el DROP de la música (edita la pista para que caiga en ese fotograma) + opcional un impacto | `attack` en el fotograma | el momento más fuerte, al 30–60 % del video |
| Logo / cierre | la música se detiene en compás o se filtra, 0,2–0,7 s de casi silencio, UNA nota suave en la tonalidad | cuando el logo se lee | 8–20 dB bajo el pico; cola hasta el silencio |
| Video de producto / UI | acento brillante (campanita, golpe corto) | | **sin sub-drops** salvo que se pidan graves cinematográficos (en pruebas a ciegas se rechazaron 5 de 9) |

## 3. Voz encima (el caso típico de un reel)
- La voz manda: efectos de UI y whooshes 6–10 dB más bajos; golpes fuertes solo en pausas o cambios de frase.
- Nada de camas/ambientes bajo la voz. La música hace **ducking** bajo la voz (`duck_db` 6–10).
- Si un efecto pisa una palabra: muévelo a la pausa, acórtalo o recórtale graves.

## 4. Sincronía
- Un sonido que se adelanta más de ~45 ms se percibe "antes"; uno que pica más de ~75 ms tarde se percibe tarde *(norma: −45…+75 ms, mediana +8)*.
- Las horas salen **del código de la animación** (fotograma / fps), nunca escritas a ojo: a ojo caen 8–11 fotogramas fuera.
- Ojo con las muestras de ataque lento: si el pico llega > 80 ms después del ataque, usa `anchor: peak`.

## 5. Variación sin azar
- Acción repetida: 3–4 tomas distintas en ciclo, ±1–2 dB, ±0,3–0,5 semitonos como mucho. **Nunca** el mismo archivo en ráfaga ("ametralladora").
- Excepción: el clic de UI, siempre la misma voz y nivel.

## 6. Niveles y master
- **−14 LUFS integrados** para redes; **true peak ≤ −1 dBTP medido en el MP4 final** (después del AAC).
- LRA 5–9 LU en un video con arco; < 2 = aplastado.
- Efectos secos, mono y centrados; solo whooshes, risers y música van abiertos. Graves < 120 Hz en mono.
- La banda de 2–6 kHz es la que duele primero en un móvil: ningún efecto mucho más fuerte ahí que la propia música.
- Elementos afinados (campanas, notas) en la tonalidad de la música; booms sin afinar bajo un acorde que resuelve suenan baratos.

## 7. Señales de "sonido barato" (prohibidas)
Pitidos sintetizados, senoidales y barridos de ruido; una muestra en ráfaga; whoosh en cada corte; boom en cada logo; destellos "mágicos" de relleno; reverb en sonidos pequeños; pitch aleatorio en el tecleo; cobertura parcial (unos clics suenan y otros no); clics en los cortes; música cortada a mitad de nota; un loop de ambiente audible; el logo más fuerte que el drop; un final que corta en seco en lugar de una cola hasta el silencio.

## 8. Licencias (un reel de marca es uso comercial)
| Licencia | ¿Se puede? | Crédito |
|---|---|---|
| CC0 / dominio público | ✅ | cortesía |
| CC BY 2.0–4.0 | ✅ | **obligatorio** en el caption: título, autor, link, licencia, "editado" |
| Licencia gratuita de Mixkit | ✅ | no redistribuir archivos sueltos; no registrar el video en Content ID |
| Licencia de Pixabay | ✅ | descarga manual (bloquea scripts) |
| CC BY-NC, BY-ND, BY-SA, Sampling+, "uso personal", "gratis con crédito en redes", rips de YouTube, sin texto de licencia | ❌ | |
- La licencia se lee **en la página del propio audio**, nunca en un buscador o agregador. Si dos fuentes discrepan, se descarta.
- **Música en tendencia de Instagram:** no se puede meter en el MP4 (copyright). Se exporta el video SIN esa música y el usuario la añade desde la app de Instagram al publicar.
