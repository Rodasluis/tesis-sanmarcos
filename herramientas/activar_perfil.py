"""Activa un perfil: genera `_quarto.yml` y deja la marca `.perfil-activo`.

`_quarto.yml` es un archivo derivado. No se edita a mano: se regenera desde el
perfil cada vez que se activa uno, y cualquier cambio manual se pierde. El
formato vive en `perfiles/<id>.yaml`, en un solo sitio.

Uso:
    uv run python -m herramientas.activar_perfil letras-flch
    uv run python -m herramientas.activar_perfil --cual
    uv run python -m herramientas.activar_perfil --listar
"""
from __future__ import annotations

import argparse
import pathlib
import sys

from herramientas.perfiles import PENDIENTE, ErrorDePerfil, Perfil, cargar, listar, perfil_activo

RAIZ = pathlib.Path(__file__).resolve().parent.parent

CSL_POR_ESTILO = {
    "apa7": "plantillas/csl/apa.csl",
    "vancouver": "plantillas/csl/vancouver.csl",
}


def _csl_de(perfil: Perfil) -> tuple[str | None, str | None]:
    """Devuelve (ruta_csl, aviso)."""
    declarado = perfil.get("csl")
    if isinstance(declarado, str) and declarado and declarado != PENDIENTE:
        ruta = declarado.replace("plantillas/csl/apa-es.csl", "plantillas/csl/apa.csl")
        return ruta, None
    estilo = perfil.get("estilo_citas")
    if estilo in CSL_POR_ESTILO:
        return CSL_POR_ESTILO[estilo], None
    return None, (
        "el perfil no fija estilo de citas. El _quarto.yml queda sin `csl` y la "
        "bibliografía saldrá con el estilo por defecto de pandoc. Decide el estilo "
        "con el asesor y regístralo antes de redactar."
    )


def construir_quarto_yml(perfil: Perfil, raiz: pathlib.Path = RAIZ) -> tuple[str, list[str]]:
    avisos: list[str] = []
    csl, aviso = _csl_de(perfil)
    if aviso:
        avisos.append(aviso)

    referencia = f"plantillas/{perfil.id}/referencia.docx"
    if not (raiz / referencia).exists():
        avisos.append(
            f"falta {referencia}. Genérala con: "
            f"uv run python -m herramientas.plantilla_docx --perfil {perfil.id}"
        )

    if not perfil.verificado:
        avisos.append(
            f"el perfil está en estado '{perfil.estado}': hereda la estructura del "
            "perfil base, que sí es norma. Se puede trabajar con normalidad; si tu "
            "escuela pide otra cosa, se ajusta el perfil."
        )

    fuente = perfil.get("fuente") or {}
    encabezado = [
        "# ARCHIVO GENERADO. No lo edites: se sobrescribe al activar un perfil.",
        f"# Perfil activo : {perfil.id} ({perfil.get('facultad')})",
        f"# Estado        : {perfil.estado}",
        f"# Norma         : {fuente.get('norma') or fuente.get('documento') or '—'}",
        f"# Herencia      : {' <- '.join(perfil.cadena)}",
        "# Regenerar con : uv run python -m herramientas.activar_perfil "
        f"{perfil.id}",
        "",
    ]

    lineas = [
        "project:",
        "  type: default",
        "  output-dir: entregables/_render",
        "",
        "bibliography: referencias.bib",
        "lang: es",
    ]
    if csl:
        lineas.append(f"csl: {csl}")
    lineas += [
        "",
        "format:",
        "  docx:",
        f"    reference-doc: {referencia}",
        "    number-sections: false",
        "    toc: false",
        "    fig-align: center",
        "    tbl-cap-location: top",
        "",
        "# La numeración romana de los preliminares y el reinicio en arábigos NO se",
        "# configuran aquí: Quarto no genera saltos de sección. Los aplica",
        "# herramientas/docx_numeracion.py sobre el .docx ya renderizado.",
        "",
        "execute:",
        "  echo: false",
        "  warning: false",
        "  freeze: auto",
    ]
    return "\n".join(encabezado + lineas) + "\n", avisos


def activar(pid: str, raiz: pathlib.Path = RAIZ) -> list[str]:
    perfil = cargar(pid, raiz=raiz)
    contenido, avisos = construir_quarto_yml(perfil, raiz)
    (raiz / "_quarto.yml").write_text(contenido, encoding="utf8")
    (raiz / ".perfil-activo").write_text(perfil.id + "\n", encoding="utf8")
    return avisos


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("perfil", nargs="?", help="id del perfil a activar")
    ap.add_argument("--listar", action="store_true", help="muestra los perfiles disponibles")
    ap.add_argument("--cual", action="store_true", help="muestra el perfil activo")
    args = ap.parse_args(argv)

    if args.listar:
        for pid in listar():
            try:
                p = cargar(pid, validar=False)
                print(f"  {pid:<22} {p.estado:<24} {p.get('facultad')}")
            except ErrorDePerfil as e:
                print(f"  {pid:<22} ERROR: {e}")
        return 0

    if args.cual:
        actual = perfil_activo(RAIZ)
        if actual:
            print(actual)
            return 0
        print("no hay perfil activo. Actívalo con:")
        print("  uv run python -m herramientas.activar_perfil <id>")
        return 1

    if not args.perfil:
        ap.error("indica un perfil, o usa --listar / --cual")

    try:
        avisos = activar(args.perfil)
    except ErrorDePerfil as e:
        print(f"ERROR: {e}", file=sys.stderr)
        return 1

    print(f"OK  perfil activo: {args.perfil}")
    print("    generado _quarto.yml y .perfil-activo")
    for a in avisos:
        print(f"    AVISO: {a}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
