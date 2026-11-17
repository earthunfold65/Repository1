#!/usr/bin/env python3
"""Ranking de reels de referentes por "outlier score".

Uso:  python3 -I instagram/scripts/analizar_reels.py instagram/referentes/reels.csv [salida.md]

El score compara cada reel con la MEDIANA DE SU PROPIA CUENTA, así una cuenta
pequeña y una enorme se pueden comparar: 3.0 = 3 veces más vistas de lo normal
para esa cuenta.

Columnas obligatorias: cuenta, url, vistas
Opcionales: fecha, likes, comentarios, compartidos, guardados, duracion_s,
            seguidores, hook_formula, formato, tema, notas
"""
import csv
import statistics
import sys
from collections import Counter, defaultdict

VIRAL, BUENO, FLOP = 3.0, 1.5, 0.5


def num(value):
    if value is None:
        return None
    s = str(value).strip().lower().replace(" ", "")
    if not s:
        return None
    mult = 1
    if s.endswith("k"):
        mult, s = 1_000, s[:-1]
    elif s.endswith("m"):
        mult, s = 1_000_000, s[:-1]
    if mult == 1:
        s = s.replace(".", "").replace(",", "")  # 12.345 / 12,345 -> 12345
    else:
        s = s.replace(",", ".")  # 1,2k -> 1.2k
    try:
        return float(s) * mult
    except ValueError:
        return None


def etiqueta(score):
    if score >= VIRAL:
        return "VIRAL"
    if score >= BUENO:
        return "BUENO"
    if score <= FLOP:
        return "FLOP"
    return "NORMAL"


def fmt(n):
    if n is None:
        return "-"
    if n >= 1_000_000:
        return f"{n / 1_000_000:.1f}M"
    if n >= 1_000:
        return f"{n / 1_000:.1f}k"
    return f"{n:.0f}"


def main():
    if len(sys.argv) < 2:
        sys.exit(__doc__)
    with open(sys.argv[1], newline="", encoding="utf-8-sig") as f:
        filas = [r for r in csv.DictReader(f) if (r.get("cuenta") or "").strip()]

    por_cuenta = defaultdict(list)
    for r in filas:
        r["_vistas"] = num(r.get("vistas"))
        if r["_vistas"]:
            por_cuenta[r["cuenta"].strip()].append(r)

    out = ["# Ranking de reels de referentes\n"]
    todos = []
    out.append("| Cuenta | Reels | Mediana vistas | Aviso |\n|---|---|---|---|")
    for cuenta, rs in sorted(por_cuenta.items()):
        med = statistics.median(r["_vistas"] for r in rs)
        aviso = "pocos datos (<8 reels): score poco fiable" if len(rs) < 8 else ""
        out.append(f"| {cuenta} | {len(rs)} | {fmt(med)} | {aviso} |")
        for r in rs:
            r["_score"] = r["_vistas"] / med if med else 0
            r["_tag"] = etiqueta(r["_score"])
            inter = [num(r.get(k)) for k in ("likes", "comentarios", "compartidos", "guardados")]
            inter = [x for x in inter if x is not None]
            r["_eng"] = (sum(inter) / r["_vistas"] * 100) if inter else None
            todos.append(r)

    todos.sort(key=lambda r: r["_score"], reverse=True)
    out.append("\n## Todos los reels (ordenados por outlier score)\n")
    out.append("| # | Cuenta | Score | Etiqueta | Vistas | Interacción % | Duración | Hook | Tema | URL |")
    out.append("|---|---|---|---|---|---|---|---|---|---|")
    for i, r in enumerate(todos, 1):
        eng = f"{r['_eng']:.1f}" if r["_eng"] is not None else "-"
        out.append(
            f"| {i} | {r['cuenta']} | {r['_score']:.2f} | {r['_tag']} | {fmt(r['_vistas'])} | {eng} "
            f"| {r.get('duracion_s') or '-'} | {r.get('hook_formula') or '-'} | {r.get('tema') or '-'} | {r.get('url') or '-'} |"
        )

    ganadores = [r for r in todos if r["_tag"] in ("VIRAL", "BUENO")]
    flops = [r for r in todos if r["_tag"] == "FLOP"]
    out.append("\n## Ganadores vs flops\n")
    out.append(f"- Ganadores (score ≥ {BUENO}): {len(ganadores)} · Flops (score ≤ {FLOP}): {len(flops)}")

    def dur(rs):
        d = [num(r.get("duracion_s")) for r in rs]
        d = [x for x in d if x]
        return f"{statistics.median(d):.0f} s" if d else "sin datos"

    out.append(f"- Duración mediana: ganadores {dur(ganadores)} · flops {dur(flops)}")
    for campo in ("hook_formula", "formato", "tema"):
        g = Counter((r.get(campo) or "").strip() for r in ganadores if (r.get(campo) or "").strip())
        fl = Counter((r.get(campo) or "").strip() for r in flops if (r.get(campo) or "").strip())
        if g or fl:
            out.append(f"- **{campo}** en ganadores: {dict(g.most_common(5))} · en flops: {dict(fl.most_common(5))}")

    texto = "\n".join(out) + "\n"
    if len(sys.argv) > 2:
        with open(sys.argv[2], "w", encoding="utf-8") as f:
            f.write(texto)
        print(f"Guardado en {sys.argv[2]}")
    else:
        print(texto)


if __name__ == "__main__":
    main()
