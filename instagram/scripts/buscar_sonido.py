#!/usr/bin/env python3
"""Busca sonidos con licencia abierta (Openverse -> Freesound) y los descarga con la licencia verificada.

  python3 -I instagram/scripts/buscar_sonido.py buscar "swipe whoosh" [--max-ms 1500] [--n 10]
  python3 -I instagram/scripts/buscar_sonido.py bajar <id_openverse> [<id>...] [--rol whoosh]

Solo acepta CC0 y CC BY (uso comercial + edición). La licencia se comprueba en la página del
propio sonido en Freesound; si no coincide con Openverse, NO se descarga.
Descarga a instagram/sonido/libreria/<rol>/ y apunta cada archivo en instagram/sonido/licencias.md
con el crédito listo para el caption (obligatorio en CC BY).
"""
import datetime
import json
import os
import re
import sys
import time
import urllib.parse
import urllib.error
import urllib.request

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
LIB = os.path.join(ROOT, "instagram", "sonido", "libreria")
LIC = os.path.join(ROOT, "instagram", "sonido", "licencias.md")
UA = {"User-Agent": "reel-sound-tool/1.0"}
OK_LIC = {"cc0", "by"}
LIC_URL = {"cc0": "https://creativecommons.org/publicdomain/zero/1.0/",
           "by": "https://creativecommons.org/licenses/by/{v}/"}


def get(url, binary=False, intentos=4):
    for n in range(intentos):
        try:
            req = urllib.request.Request(url, headers=UA)
            with urllib.request.urlopen(req, timeout=30) as r:
                data = r.read()
            return data if binary else data.decode("utf-8", "replace")
        except urllib.error.HTTPError as e:
            if e.code not in (403, 429, 500, 502, 503) or n == intentos - 1:
                raise
            time.sleep(5 * (n + 1))  # el servidor limita ráfagas: espera y reintenta


def args_opt(argv, name, default):
    if name in argv:
        i = argv.index(name)
        v = argv[i + 1]
        del argv[i:i + 2]
        return v
    return default


def buscar(argv):
    max_ms = int(args_opt(argv, "--max-ms", "0"))
    n = int(args_opt(argv, "--n", "10"))
    q = " ".join(argv)
    url = ("https://api.openverse.org/v1/audio/?" +
           urllib.parse.urlencode({"q": q, "license": "cc0,by", "source": "freesound", "page_size": 20}))
    res = json.loads(get(url))["results"]
    if max_ms:
        res = [r for r in res if r.get("duration") and r["duration"] <= max_ms]
    print(f"{'id_openverse':38} {'licencia':9} {'ms':>6}  título — autor")
    for r in res[:n]:
        print(f"{r['id']:38} {r['license']} {r.get('license_version') or '':5} {r.get('duration') or 0:>6}  "
              f"{r['title'][:45]} — {r.get('creator')}")


def slug(s):
    return re.sub(r"[^a-z0-9]+", "-", s.lower()).strip("-")[:40]


def bajar(argv):
    rol = args_opt(argv, "--rol", "varios")
    os.makedirs(os.path.join(LIB, rol), exist_ok=True)
    if not os.path.exists(LIC):
        os.makedirs(os.path.dirname(LIC), exist_ok=True)
        with open(LIC, "w", encoding="utf-8") as f:
            f.write("# Licencias de los sonidos\n\n| Archivo | Licencia | Autor | Página | Verificada | Crédito para el caption |\n|---|---|---|---|---|---|\n")
    for oid in argv:
        try:
            bajar_uno(oid, rol)
        except Exception as e:  # un fallo no detiene el resto
            print(f"✗ {oid}: {e}")
        time.sleep(1.5)  # descargas educadas, de una en una


def bajar_uno(oid, rol):
    if True:
        r = json.loads(get(f"https://api.openverse.org/v1/audio/{oid}/"))
        lic, ver = r["license"], r.get("license_version") or ""
        page = r.get("foreign_landing_url") or ""
        if lic not in OK_LIC:
            print(f"✗ {r['title']}: licencia {lic} no permitida"); return
        if "freesound.org" not in page:
            print(f"✗ {r['title']}: no es de Freesound, verifica a mano: {page}"); return
        html = get(page)
        links = set(re.findall(r"creativecommons\.org/(publicdomain/zero/1\.0|licenses/[a-z\-]+/[\d.]+)", html))
        esperado = "publicdomain/zero/1.0" if lic == "cc0" else f"licenses/by/{ver}"
        if links != {esperado}:
            print(f"✗ {r['title']}: la página dice {links or 'nada'}, Openverse dice {esperado}. Descartado."); return
        audio = r["url"]
        ext = os.path.splitext(urllib.parse.urlparse(audio).path)[1] or ".mp3"
        fid = re.search(r"/sounds/(\d+)", page).group(1)
        name = f"fs-{fid}_{slug(r['title'])}{ext}"
        dest = os.path.join(LIB, rol, name)
        with open(dest, "wb") as f:
            f.write(get(audio, binary=True))
        lic_txt = "CC0 1.0" if lic == "cc0" else f"CC BY {ver}"
        cred = "— (CC0, crédito de cortesía)" if lic == "cc0" else (
            f"\"{r['title']}\" por {r.get('creator')} ({page}), {lic_txt} ({LIC_URL['by'].format(v=ver)}), editado")
        rel = os.path.relpath(dest, ROOT)
        with open(LIC, "a", encoding="utf-8") as f:
            f.write(f"| `{rel}` | {lic_txt} | {r.get('creator')} | {page} | {datetime.date.today()} en la página | {cred} |\n")
        print(f"✓ {rel}  ({lic_txt}, verificada en {page})")


def main():
    if len(sys.argv) < 3:
        sys.exit(__doc__)
    cmd, argv = sys.argv[1], sys.argv[2:]
    {"buscar": buscar, "bajar": bajar}.get(cmd, lambda a: sys.exit(__doc__))(argv)


if __name__ == "__main__":
    main()
