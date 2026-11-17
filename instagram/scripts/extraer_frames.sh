#!/usr/bin/env bash
# Extrae lo necesario para analizar un reel descargado (.mp4):
#   - fotogramas del hook (0, 0.5, 1, 1.5, 2, 3 s) y luego uno cada 3 s
#   - audio en mp3 para transcribir
#   - duración y número de cortes de plano (ritmo de edición)
# Uso: bash instagram/scripts/extraer_frames.sh video.mp4 carpeta_salida
set -euo pipefail
in="$1"; out="$2"
mkdir -p "$out/frames"

dur=$(ffprobe -v error -show_entries format=duration -of csv=p=0 "$in")
echo "duracion_s=$dur" > "$out/info.txt"

for t in 0 0.5 1 1.5 2 3; do
  ffmpeg -v error -y -ss "$t" -i "$in" -frames:v 1 -vf scale=540:-2 "$out/frames/hook_${t}s.jpg"
done
ffmpeg -v error -y -i "$in" -vf "fps=1/3,scale=540:-2" "$out/frames/t_%03d.jpg"
ffmpeg -v error -y -i "$in" -vn -ac 1 -b:a 96k "$out/audio.mp3" || echo "sin audio" >> "$out/info.txt"

cortes=$(ffmpeg -v info -i "$in" -vf "select='gt(scene,0.3)',showinfo" -f null - 2>&1 | grep -c "pts_time" || true)
echo "cortes_de_plano=$cortes" >> "$out/info.txt"
awk -v d="$dur" -v c="$cortes" 'BEGIN{ if (c>0) printf "segundos_por_plano=%.1f\n", d/(c+1) }' >> "$out/info.txt"
cat "$out/info.txt"
