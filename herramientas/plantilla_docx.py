"""Genera `plantillas/<perfil>/referencia.docx` a partir de un perfil.

Quarto necesita un documento de referencia de Word para saber con qué márgenes,
tipografía e interlineado maquetar la salida. Ese documento se construye aquí
desde el perfil, para que el formato no viva duplicado en dos sitios.

Se parte del `reference.docx` que trae pandoc y se sobrescriben los valores que
el perfil fija. Cuando la norma calla, se aplica un valor operativo y se deja
constancia en `plantillas/<perfil>/FORMATO.md`: el estudiante debe poder ver de
un vistazo qué le exige su escuela y qué elegimos nosotros por él.

Uso:
    uv run python -m herramientas.plantilla_docx --perfil letras-flch
    uv run python -m herramientas.plantilla_docx --todos
"""
from __future__ import annotations

import argparse
import pathlib
import shutil
import subprocess
import sys
import tempfile
from typing import Any

from docx import Document
from docx.enum.text import WD_LINE_SPACING
from docx.oxml.ns import qn
from docx.shared import Cm, Pt

from herramientas.perfiles import PENDIENTE, Perfil, cargar, listar

RAIZ = pathlib.Path(__file__).resolve().parent.parent

# Valores operativos para cuando la norma no dice nada. No son requisitos.
OPERATIVOS: dict[str, Any] = {
    "papel": "A4",
    "fuente": "Times New Roman",
    "tamano": 12,
    "interlineado": 1.5,
    "margenes_cm": {"superior": 2.5, "inferior": 2.5, "izquierdo": 3.0, "derecho": 2.5},
}

A4 = (Cm(21.0), Cm(29.7))
CARTA = (Cm(21.59), Cm(27.94))

#: Estilos de pandoc que llevan el cuerpo del texto.
ESTILOS_CUERPO = ("Normal", "Body Text", "First Paragraph", "Compact")
#: Estilos que van a espacio simple y cuerpo menor cuando la norma lo pide.
ESTILOS_MENORES = ("Footnote Text", "Block Text", "Bibliography")


class SinPandoc(RuntimeError):
    pass


def _norma_o_operativo(valor: Any, clave: str) -> tuple[Any, bool]:
    """Devuelve (valor_a_usar, es_operativo)."""
    if valor is None or valor == PENDIENTE or (isinstance(valor, dict) and not valor):
        return OPERATIVOS[clave], True
    if isinstance(valor, list):
        if not valor or all(v == PENDIENTE for v in valor):
            return OPERATIVOS[clave], True
        return valor[0], False
    return valor, False


def _base_pandoc(destino: pathlib.Path) -> pathlib.Path:
    """Extrae el reference.docx por defecto de pandoc."""
    pandoc = shutil.which("pandoc") or shutil.which("quarto")
    if pandoc is None:
        raise SinPandoc(
            "no se encontró pandoc ni quarto en el PATH. "
            "Instálalos (ver README.md) y vuelve a intentarlo."
        )
    if pandoc.endswith(("quarto", "quarto.exe")):
        cmd = [pandoc, "pandoc", "--print-default-data-file", "reference.docx"]
    else:
        cmd = [pandoc, "--print-default-data-file", "reference.docx"]
    salida = subprocess.run(cmd, capture_output=True, check=True)
    destino.write_bytes(salida.stdout)
    return destino


def _fijar_defaults(doc: Document, familia: str, tamano: int) -> None:
    """Escribe la tipografía en w:docDefaults, que es de donde heredan todos."""
    estilos = doc.styles.element
    defaults = estilos.find(qn("w:docDefaults"))
    if defaults is None:
        return
    rpr_default = defaults.find(qn("w:rPrDefault"))
    if rpr_default is None:
        return
    rpr = rpr_default.find(qn("w:rPr"))
    if rpr is None:
        return

    rfonts = rpr.find(qn("w:rFonts"))
    if rfonts is None:
        rfonts = rpr.makeelement(qn("w:rFonts"), {})
        rpr.append(rfonts)
    for attr in ("w:ascii", "w:hAnsi", "w:cs", "w:eastAsia"):
        rfonts.set(qn(attr), familia)

    for tag, val in (("w:sz", str(tamano * 2)), ("w:szCs", str(tamano * 2))):
        el = rpr.find(qn(tag))
        if el is None:
            el = rpr.makeelement(qn(tag), {})
            rpr.append(el)
        el.set(qn("w:val"), val)


def _aplicar_estilo(doc: Document, nombre: str, *, familia: str | None = None,
                    tamano: float | None = None, interlineado: float | None = None,
                    espacio_exacto: bool = False) -> None:
    estilo = next((st for st in doc.styles if st.name == nombre), None)
    if estilo is None:
        return
    if familia is not None:
        estilo.font.name = familia
        rpr = estilo.element.get_or_add_rPr()
        rfonts = rpr.find(qn("w:rFonts"))
        if rfonts is None:
            rfonts = rpr.makeelement(qn("w:rFonts"), {})
            rpr.append(rfonts)
        for attr in ("w:ascii", "w:hAnsi", "w:cs", "w:eastAsia"):
            rfonts.set(qn(attr), familia)
    if tamano is not None:
        estilo.font.size = Pt(tamano)
    if interlineado is not None and hasattr(estilo, "paragraph_format"):
        pf = estilo.paragraph_format
        if espacio_exacto or abs(interlineado - 1.0) < 1e-6:
            pf.line_spacing_rule = WD_LINE_SPACING.SINGLE
        else:
            pf.line_spacing = interlineado


def construir(perfil: Perfil, raiz: pathlib.Path = RAIZ) -> tuple[pathlib.Path, list[str]]:
    """Construye la plantilla del perfil. Devuelve (ruta, notas de lo operativo)."""
    formato = perfil.get("formato") or {}
    notas: list[str] = []

    familia, op = _norma_o_operativo(formato.get("fuente"), "fuente")
    if op:
        notas.append(f"tipografía: {familia} (valor operativo; la norma no la fija)")

    tamano, op = _norma_o_operativo(formato.get("tamano"), "tamano")
    if op:
        notas.append(f"cuerpo: {tamano} pt (valor operativo)")
    tamano = int(tamano)

    interlineado, op = _norma_o_operativo(formato.get("interlineado"), "interlineado")
    if op:
        notas.append(f"interlineado: {interlineado} (valor operativo)")
    interlineado = float(interlineado)

    margenes, op = _norma_o_operativo(formato.get("margenes_cm"), "margenes_cm")
    if op:
        notas.append(
            "márgenes: 2,5 cm salvo el izquierdo, 3,0 cm para encuadernación "
            "(valores operativos; la norma no los fija)"
        )

    papel, op = _norma_o_operativo(formato.get("papel"), "papel")
    if op:
        notas.append("papel: A4 (valor operativo)")

    with tempfile.TemporaryDirectory() as tmp:
        base = _base_pandoc(pathlib.Path(tmp) / "reference.docx")
        doc = Document(str(base))

        seccion = doc.sections[0]
        ancho, alto = CARTA if str(papel).lower().startswith("carta") else A4
        seccion.page_width, seccion.page_height = ancho, alto
        seccion.top_margin = Cm(float(margenes["superior"]))
        seccion.bottom_margin = Cm(float(margenes["inferior"]))
        seccion.left_margin = Cm(float(margenes["izquierdo"]))
        seccion.right_margin = Cm(float(margenes["derecho"]))

        _fijar_defaults(doc, familia, tamano)

        for nombre in ESTILOS_CUERPO:
            _aplicar_estilo(doc, nombre, familia=familia, tamano=tamano,
                            interlineado=interlineado)

        tam_menor = formato.get("tamano_notas_y_citas_largas")
        tam_menor = int(tam_menor) if isinstance(tam_menor, (int, float)) else tamano
        il_citas = formato.get("interlineado_citas_largas")
        il_notas = formato.get("interlineado_notas")
        il_refs = formato.get("interlineado_referencias")

        _aplicar_estilo(doc, "Block Text", familia=familia, tamano=tam_menor,
                        interlineado=float(il_citas) if il_citas else interlineado)
        _aplicar_estilo(doc, "Footnote Text", familia=familia, tamano=tam_menor,
                        interlineado=float(il_notas) if il_notas else 1.0)
        _aplicar_estilo(doc, "Bibliography", familia=familia, tamano=tamano,
                        interlineado=float(il_refs) if il_refs else interlineado)

        for nivel, escala in ((1, 1.0), (2, 1.0), (3, 1.0)):
            _aplicar_estilo(doc, f"Heading {nivel}", familia=familia,
                            tamano=round(tamano * escala), interlineado=interlineado)
        _aplicar_estilo(doc, "Title", familia=familia, tamano=tamano + 2)
        for cap in ("Caption", "Table Caption", "Image Caption"):
            _aplicar_estilo(doc, cap, familia=familia, tamano=max(tamano - 1, 8),
                            interlineado=1.0)

        destino_dir = raiz / "plantillas" / perfil.id
        destino_dir.mkdir(parents=True, exist_ok=True)
        destino = destino_dir / "referencia.docx"
        doc.save(str(destino))

    _escribir_formato_md(perfil, destino_dir, {
        "papel": papel, "fuente": familia, "tamano": tamano,
        "interlineado": interlineado, "margenes": margenes,
    }, notas)
    return destino, notas


def _escribir_formato_md(perfil: Perfil, destino_dir: pathlib.Path,
                         aplicado: dict[str, Any], notas: list[str]) -> None:
    formato = perfil.get("formato") or {}
    fuente_datos = formato.get("fuente_de_estos_datos") or perfil.get("fuente", {}).get("documento")
    heredado = perfil.viene_heredado("formato")

    lineas = [
        f"# Formato aplicado — `{perfil.id}`",
        "",
        f"- Facultad: {perfil.get('facultad')}",
        f"- Estado del perfil: `{perfil.estado}`",
    ]
    if heredado:
        lineas.append(f"- El bloque `formato` se hereda de `{heredado}`.")
    if fuente_datos:
        lineas.append(f"- Fuente del formato: {fuente_datos}")
    lineas += [
        "",
        "## Valores con los que se generó `referencia.docx`",
        "",
        "| Parámetro | Valor |",
        "|---|---|",
        f"| Papel | {aplicado['papel']} |",
        f"| Tipografía | {aplicado['fuente']} |",
        f"| Cuerpo | {aplicado['tamano']} pt |",
        f"| Interlineado | {aplicado['interlineado']} |",
        f"| Margen superior | {aplicado['margenes']['superior']} cm |",
        f"| Margen inferior | {aplicado['margenes']['inferior']} cm |",
        f"| Margen izquierdo | {aplicado['margenes']['izquierdo']} cm |",
        f"| Margen derecho | {aplicado['margenes']['derecho']} cm |",
        "",
    ]
    if notas:
        lineas += [
            "## Atención: valores que NO vienen de una norma",
            "",
            "La norma aplicable a este perfil no fija los siguientes puntos. Se",
            "aplicaron valores operativos para poder maquetar. **No son requisitos**",
            "y conviene confirmarlos con el asesor antes de la entrega:",
            "",
        ]
        lineas += [f"- {n}" for n in notas]
        lineas.append("")
    else:
        lineas += [
            "## Procedencia",
            "",
            "Todos los valores de arriba provienen de la norma citada. No se aplicó",
            "ningún valor inventado.",
            "",
        ]
    lineas += [
        "## Qué NO resuelve esta plantilla",
        "",
        "La numeración en romanos minúsculos de los preliminares y el reinicio en",
        "arábigos desde el cuerpo **no** se configuran aquí: Word los implementa con",
        "saltos de sección, que Quarto no genera. Los aplica",
        "`herramientas/docx_numeracion.py` al final, sobre el `.docx` ya renderizado.",
        "",
        "Este archivo se regenera con:",
        "",
        "```",
        f"uv run python -m herramientas.plantilla_docx --perfil {perfil.id}",
        "```",
    ]
    (destino_dir / "FORMATO.md").write_text("\n".join(lineas), encoding="utf8")


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--perfil", help="id del perfil")
    ap.add_argument("--todos", action="store_true", help="genera la plantilla de cada perfil")
    args = ap.parse_args(argv)

    if not args.perfil and not args.todos:
        ap.error("indica --perfil <id> o --todos")

    ids = listar() if args.todos else [args.perfil]
    fallos = 0
    for pid in ids:
        try:
            perfil = cargar(pid)
            ruta, notas = construir(perfil)
            marca = " (con valores operativos)" if notas else ""
            print(f"OK  {pid:<22} -> {ruta.relative_to(RAIZ)}{marca}")
        except SinPandoc as e:
            print(f"ERR {pid}: {e}", file=sys.stderr)
            return 2
        except Exception as e:  # noqa: BLE001
            print(f"ERR {pid}: {e}", file=sys.stderr)
            fallos += 1
    return 1 if fallos else 0


if __name__ == "__main__":
    raise SystemExit(main())
