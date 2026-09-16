"""Comprobación de la integración con Zotero y Better BibTeX.

El principio 2 de CLAUDE.md dice que solo se citan claves presentes en
`referencias.bib`. Este módulo comprueba que ese archivo exista, esté al día y
tenga claves utilizables, y explica qué hacer cuando no.

Datos verificados en la documentación de Better BibTeX el 2026-09-16:

- El endpoint local de BBT escucha en el puerto **23119** (24119 en Juris-M).
- Solo responde desde la misma máquina; desde el navegador está bloqueado por
  seguridad desde Zotero 5.0.71, pero el acceso programático funciona.
- **Zotero tiene que estar abierto** para que responda.
- La exportación automática se configura con «Keep updated» al exportar una
  colección, y se administra en la pestaña *Automatic exports* de BBT.

Por eso el camino obligatorio de este repositorio es el **archivo**
`referencias.bib` exportado automáticamente, no el endpoint: el archivo funciona
con Zotero cerrado, en otra máquina y dentro de CI. El endpoint solo se usa para
diagnosticar.

Uso:
    uv run python -m herramientas.zotero
"""
from __future__ import annotations

import argparse
import datetime as dt
import pathlib
import re
import sys

RAIZ = pathlib.Path(__file__).resolve().parent.parent
BIB = RAIZ / "referencias.bib"

PUERTO_BBT = 23119
BASE_BBT = f"http://127.0.0.1:{PUERTO_BBT}"

RE_ENTRADA = re.compile(r"^@(\w+)\s*\{\s*([^,\s]+)\s*,", re.M)


def _verificar_endpoint(timeout: float = 2.0) -> tuple[bool, str]:
    """¿Responde Zotero con Better BibTeX en el puerto local?"""
    try:
        import requests
    except ImportError:  # pragma: no cover
        return False, "falta la dependencia `requests`"
    try:
        r = requests.get(f"{BASE_BBT}/better-bibtex/cayw?probe=probe", timeout=timeout)
        if r.status_code == 200:
            return True, "Zotero con Better BibTeX responde en el puerto local"
        return False, f"el puerto {PUERTO_BBT} respondió {r.status_code}"
    except Exception:
        return False, (
            f"nada responde en {BASE_BBT}. Es lo esperable si Zotero está cerrado: "
            "no es un error si ya tienes referencias.bib al día"
        )


def analizar_bib(ruta: pathlib.Path = BIB) -> dict[str, object]:
    """Resume el estado de referencias.bib."""
    if not ruta.exists():
        return {"existe": False}
    texto = ruta.read_text(encoding="utf8", errors="replace")
    entradas = RE_ENTRADA.findall(texto)
    claves = [c for _, c in entradas]
    tipos: dict[str, int] = {}
    for t, _ in entradas:
        tipos[t.lower()] = tipos.get(t.lower(), 0) + 1

    duplicadas = sorted({c for c in claves if claves.count(c) > 1})
    # Better BibTeX genera claves del tipo autorTITULOaño; las de Zotero
    # "clásico" suelen llevar dos puntos o guiones bajos con el título completo.
    sospechosas = [c for c in claves if ":" in c or len(c) > 45]
    mtime = dt.datetime.fromtimestamp(ruta.stat().st_mtime)

    return {
        "existe": True,
        "ruta": str(ruta.relative_to(RAIZ)),
        "entradas": len(entradas),
        "claves_unicas": len(set(claves)),
        "duplicadas": duplicadas,
        "claves_sospechosas": sospechosas[:10],
        "tipos": dict(sorted(tipos.items(), key=lambda kv: -kv[1])),
        "modificado": mtime.isoformat(timespec="minutes"),
        "antiguedad_dias": (dt.datetime.now() - mtime).days,
    }


INSTRUCCIONES = f"""\
Cómo dejar `referencias.bib` funcionando (una sola vez):

 1. Abre Zotero y crea una colección para tu tesis.
 2. Clic derecho sobre esa colección → «Exportar colección…».
 3. Formato: **Better BibTeX**.
 4. Marca **«Keep updated»**. Es la casilla que lo automatiza todo: cada cambio
    en la colección vuelve a escribir el archivo.
 5. Guarda el archivo como `referencias.bib` en la raíz de este repositorio.

A partir de ahí, cada vez que agregues algo a Zotero el archivo se actualiza
solo. No lo edites a mano: tu edición se perderá en la siguiente exportación.

Para revisar o quitar exportaciones automáticas: preferencias de Better BibTeX,
pestaña «Automatic exports».

El endpoint local de BBT ({BASE_BBT}) solo se usa para diagnosticar; necesita
Zotero abierto y únicamente responde desde esta misma máquina.
"""


def diagnostico(ruta: pathlib.Path = BIB, comprobar_endpoint: bool = True) -> int:
    print("Zotero y Better BibTeX")
    print("=" * 60)

    if comprobar_endpoint:
        vivo, detalle = _verificar_endpoint()
        print(f"  endpoint local : {'sí' if vivo else 'no'} — {detalle}")

    info = analizar_bib(ruta)
    if not info["existe"]:
        print(f"  referencias.bib: NO EXISTE en {ruta}")
        print()
        print(INSTRUCCIONES)
        return 1

    print(f"  referencias.bib: {info['entradas']} entradas, "
          f"{info['claves_unicas']} claves únicas")
    print(f"  modificado     : {info['modificado']} "
          f"(hace {info['antiguedad_dias']} días)")
    tipos = ", ".join(f"{k}={v}" for k, v in list(info["tipos"].items())[:6])
    print(f"  tipos          : {tipos or '—'}")

    problemas = 0
    if info["entradas"] == 0:
        print("  AVISO: el archivo existe pero está vacío. Nada podrá citarse.")
        problemas += 1
    if info["duplicadas"]:
        print(f"  AVISO: claves duplicadas: {', '.join(info['duplicadas'][:5])}")
        problemas += 1
    if info["claves_sospechosas"]:
        print("  AVISO: hay claves que no parecen de Better BibTeX "
              f"(ej.: {info['claves_sospechosas'][0]}).")
        print("         Revisa que exportaste en formato Better BibTeX y no en BibTeX normal.")
        problemas += 1
    if isinstance(info["antiguedad_dias"], int) and info["antiguedad_dias"] > 30:
        print("  AVISO: el archivo no cambia hace más de un mes. "
              "Comprueba que «Keep updated» siga activo.")
        problemas += 1

    if not problemas:
        print("  Todo en orden.")
    return 0 if not problemas else 1


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--bib", type=pathlib.Path, default=BIB)
    ap.add_argument("--sin-red", action="store_true",
                    help="no intenta contactar el endpoint local")
    ap.add_argument("--instrucciones", action="store_true",
                    help="solo imprime cómo configurarlo")
    args = ap.parse_args(argv)

    if args.instrucciones:
        print(INSTRUCCIONES)
        return 0
    return diagnostico(args.bib, comprobar_endpoint=not args.sin_red)


if __name__ == "__main__":
    sys.exit(main())
