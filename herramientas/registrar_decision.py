"""Registra una decisión del tesista. Es la única vía de escritura en `decisiones/`.

El principio 3 de CLAUDE.md dice que Claude no inventa, no resume ni reescribe
las respuestas del tesista, no elige por él y no avanza de etapa sin una
decisión aprobada. Esta herramienta es lo que hace que ese principio sea
comprobable en lugar de ser una buena intención:

- **Exige la respuesta textual del tesista.** Sin ella no escribe nada. No
  hay bandera para saltárselo, ni siquiera en `/autopiloto`.
- **Sella el archivo con un hash.** Si alguien edita la decisión después,
  `verificar_decisiones.py` lo detecta.
- **Guarda las opciones presentadas y cuál se recomendó**, para que el asesor vea
  qué se le ofreció al tesista, no solo qué eligió.
- **Guarda las preguntas de comprensión con sus respuestas**, que alimentan
  `/sustentacion`.

Uso:
    uv run python -m herramientas.registrar_decision --json decision.json
    ... | uv run python -m herramientas.registrar_decision --stdin
"""
from __future__ import annotations

import argparse
import datetime as dt
import hashlib
import json
import pathlib
import re
import sys
from typing import Any

RAIZ = pathlib.Path(__file__).resolve().parent.parent
DIR_DECISIONES = RAIZ / "decisiones"

#: Etapas del flujo, en orden. El número del archivo sale de aquí.
ETAPAS = (
    "iniciar", "explorar-datos", "afinar-idea", "literatura", "proyecto",
    "analizar", "redactar", "jurado", "verificar", "entregar", "sustentacion",
)

CAMPOS_SELLADOS = (
    "etapa", "numero", "momento", "opciones_presentadas", "recomendada",
    "eleccion", "respuesta_textual", "cambios_pedidos", "preguntas_comprension",
    "aprobado", "autor",
)


class DecisionInvalida(ValueError):
    """Los datos no permiten registrar una decisión legítima."""


def _slug(texto: str) -> str:
    t = re.sub(r"[^a-z0-9]+", "-", texto.lower()).strip("-")
    return t or "sin-nombre"


def calcular_hash(datos: dict[str, Any]) -> str:
    """Hash estable del contenido sellado de la decisión."""
    sellado = {k: datos.get(k) for k in CAMPOS_SELLADOS}
    canonico = json.dumps(sellado, ensure_ascii=False, sort_keys=True,
                          separators=(",", ":"))
    return hashlib.sha256(canonico.encode("utf8")).hexdigest()


def validar(datos: dict[str, Any]) -> None:
    """Rechaza todo lo que no sea una decisión realmente tomada."""
    etapa = (datos.get("etapa") or "").strip()
    if not etapa:
        raise DecisionInvalida("falta `etapa`")
    if etapa not in ETAPAS:
        raise DecisionInvalida(
            f"etapa desconocida: {etapa!r}. Las válidas son: {', '.join(ETAPAS)}"
        )

    respuesta = (datos.get("respuesta_textual") or "").strip()
    if not respuesta:
        raise DecisionInvalida(
            "falta `respuesta_textual`: la respuesta literal del tesista. "
            "Sin ella no hay decisión que registrar. Esto no se puede omitir, "
            "tampoco en /autopiloto."
        )
    if len(respuesta) < 2:
        raise DecisionInvalida("`respuesta_textual` es demasiado corta para ser una respuesta")

    if datos.get("aprobado") is not True:
        raise DecisionInvalida(
            "`aprobado` debe ser true. Una decisión no aprobada no se registra: "
            "se sigue iterando con el tesista."
        )

    if not (datos.get("eleccion") or "").strip():
        raise DecisionInvalida(
            "falta `eleccion`: qué opción eligió el tesista. Si propuso algo "
            "distinto de lo ofrecido, descríbelo aquí con sus palabras."
        )

    preguntas = datos.get("preguntas_comprension") or []
    if not isinstance(preguntas, list):
        raise DecisionInvalida("`preguntas_comprension` debe ser una lista")
    for i, p in enumerate(preguntas, 1):
        if not isinstance(p, dict) or "pregunta" not in p:
            raise DecisionInvalida(f"la pregunta de comprensión {i} no tiene `pregunta`")

    opciones = datos.get("opciones_presentadas") or []
    if not isinstance(opciones, list):
        raise DecisionInvalida("`opciones_presentadas` debe ser una lista")


def _siguiente_numero(etapa: str, dir_decisiones: pathlib.Path) -> int:
    """Número de orden del archivo: el de la etapa en el flujo."""
    try:
        return ETAPAS.index(etapa)
    except ValueError:  # pragma: no cover - validar() ya lo impide
        return len(list(dir_decisiones.glob("*.json")))


def _markdown(datos: dict[str, Any]) -> str:
    lineas = [
        f"# Decisión {datos['numero']:02d} — etapa `{datos['etapa']}`",
        "",
        f"- Registrada: {datos['momento']}",
        "- Aprobada por el tesista: **sí**",
        f"- Sello: `{datos['hash'][:16]}…`",
        "",
        "> Este archivo lo escribe `registrar_decision.py`. Si lo editas a mano, "
        "`verificar_decisiones.py` lo detectará y marcará la decisión como alterada.",
        "",
    ]

    opciones = datos.get("opciones_presentadas") or []
    if opciones:
        lineas += ["## Opciones que se le presentaron", ""]
        for o in opciones:
            if isinstance(o, dict):
                marca = " **(recomendada)**" if o.get("id") == datos.get("recomendada") else ""
                lineas.append(f"### {o.get('id', '—')}. {o.get('titulo', '')}{marca}")
                for clave, etiqueta in (("ventajas", "Ventajas"),
                                        ("riesgos", "Riesgos"),
                                        ("factibilidad", "Factibilidad")):
                    v = o.get(clave)
                    if isinstance(v, list) and v:
                        lineas.append(f"- {etiqueta}: " + "; ".join(str(x) for x in v))
                    elif v:
                        lineas.append(f"- {etiqueta}: {v}")
                razon = o.get("razon_de_la_recomendacion")
                if razon:
                    lineas.append(f"- Razón de la recomendación: {razon}")
            else:
                lineas.append(f"- {o}")
            lineas.append("")

    lineas += [
        "## Qué decidió el tesista",
        "",
        f"**Eligió:** {datos['eleccion']}",
        "",
        "**En sus palabras:**",
        "",
    ]
    lineas += ["> " + linea if linea.strip() else ">"
               for linea in datos["respuesta_textual"].splitlines()]
    lineas.append("")

    cambios = datos.get("cambios_pedidos") or []
    if cambios:
        lineas += ["## Cambios que pidió", ""]
        lineas += [f"- {c}" for c in cambios]
        lineas.append("")

    preguntas = datos.get("preguntas_comprension") or []
    if preguntas:
        lineas += ["## Preguntas de comprensión", "",
                   "No bloquean el avance. Quedan registradas y alimentan "
                   "`/sustentacion`.", ""]
        for i, p in enumerate(preguntas, 1):
            lineas.append(f"**{i}. {p.get('pregunta', '')}**")
            lineas.append("")
            r = (p.get("respuesta") or "").strip()
            if r:
                lineas += ["> " + linea for linea in r.splitlines()]
            else:
                lineas.append("> *(sin responder)*")
            lineas.append("")

    return "\n".join(lineas)


def registrar(datos: dict[str, Any], dir_decisiones: pathlib.Path = DIR_DECISIONES
              ) -> tuple[pathlib.Path, pathlib.Path]:
    """Valida, sella y escribe la decisión. Devuelve (ruta_json, ruta_md)."""
    validar(datos)

    dir_decisiones.mkdir(parents=True, exist_ok=True)
    etapa = datos["etapa"].strip()
    numero = datos.get("numero")
    if not isinstance(numero, int):
        numero = _siguiente_numero(etapa, dir_decisiones)

    registro = {
        "etapa": etapa,
        "numero": numero,
        "momento": datos.get("momento") or dt.datetime.now().isoformat(timespec="seconds"),
        "opciones_presentadas": datos.get("opciones_presentadas") or [],
        "recomendada": datos.get("recomendada"),
        "eleccion": datos["eleccion"].strip(),
        "respuesta_textual": datos["respuesta_textual"],
        "cambios_pedidos": datos.get("cambios_pedidos") or [],
        "preguntas_comprension": datos.get("preguntas_comprension") or [],
        "aprobado": True,
        "autor": datos.get("autor") or "tesista",
    }
    registro["hash"] = calcular_hash(registro)

    base = f"{numero:02d}_{_slug(etapa)}"
    ruta_json = dir_decisiones / f"{base}.json"
    ruta_md = dir_decisiones / f"{base}.md"
    ruta_json.write_text(json.dumps(registro, ensure_ascii=False, indent=1),
                         encoding="utf8")
    ruta_md.write_text(_markdown(registro), encoding="utf8")
    return ruta_json, ruta_md


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    origen = ap.add_mutually_exclusive_group(required=True)
    origen.add_argument("--json", type=pathlib.Path, help="archivo JSON con la decisión")
    origen.add_argument("--stdin", action="store_true", help="lee el JSON de la entrada estándar")
    ap.add_argument("--dir", type=pathlib.Path, default=DIR_DECISIONES)
    args = ap.parse_args(argv)

    try:
        crudo = sys.stdin.read() if args.stdin else args.json.read_text(encoding="utf8")
        datos = json.loads(crudo)
    except json.JSONDecodeError as e:
        print(f"ERROR: el JSON no es válido: {e}", file=sys.stderr)
        return 2
    except OSError as e:
        print(f"ERROR: no se pudo leer la decisión: {e}", file=sys.stderr)
        return 2

    try:
        ruta_json, ruta_md = registrar(datos, args.dir)
    except DecisionInvalida as e:
        print(f"ERROR: {e}", file=sys.stderr)
        return 1

    print("OK  decisión registrada")
    print(f"    {ruta_json}")
    print(f"    {ruta_md}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
