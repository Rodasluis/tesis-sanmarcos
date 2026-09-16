"""Numeración de páginas del .docx: romanos en preliminares, arábigos en el cuerpo.

El Anexo 2A de la RR N.° 00744-R-20 exige que los preliminares vayan numerados
"en romanos minúscula, (p.e.: iv, v, vi)" y que el cuerpo lleve numeración
arábiga. Word resuelve eso con **saltos de sección**: cada sección define su
propio formato y su propio reinicio de numeración.

Quarto no genera saltos de sección, así que esto se aplica después, sobre el
`.docx` ya renderizado. No es cosmética: sin esto el documento no cumple el
Anexo 2A.

Cómo lo hace, en corto: en OOXML el salto de sección vive en el `w:sectPr`
incrustado en el `w:pPr` del **último párrafo** de la sección. Aquí se copia el
`w:sectPr` final del documento, se le fija `w:pgNumType` en romanos y se inserta
en el párrafo anterior al inicio del cuerpo. El `w:sectPr` que queda al final del
cuerpo se deja en arábigos, reiniciado en 1.

Uso:
    uv run python -m herramientas.docx_numeracion tesis.docx --inicio-cuerpo "INTRODUCCIÓN"
"""
from __future__ import annotations

import argparse
import copy
import pathlib
import re
import sys

from docx import Document
from docx.oxml.ns import qn

#: Encabezados que, por defecto, marcan el comienzo del cuerpo.
INICIOS_CUERPO = (
    "INTRODUCCIÓN", "INTRODUCCION",
    "I. INTRODUCCIÓN", "CAPÍTULO I", "CAPITULO I",
)


class SinInicioDeCuerpo(ValueError):
    """No se encontró dónde empieza el cuerpo del documento."""


def _normalizar(texto: str) -> str:
    return re.sub(r"\s+", " ", texto).strip().upper()


def localizar_inicio_cuerpo(doc: Document, marcas: tuple[str, ...] = INICIOS_CUERPO) -> int:
    """Índice del párrafo donde empieza el cuerpo.

    Prioriza los encabezados (estilo Heading N) para no confundirse con una
    mención dentro del índice o de una tabla de contenido.
    """
    marcas_norm = tuple(_normalizar(m) for m in marcas)
    candidato_texto = None
    for i, p in enumerate(doc.paragraphs):
        t = _normalizar(p.text)
        if not t:
            continue
        coincide = any(t == m or t.startswith(m + " ") or t.startswith(m + ".")
                       for m in marcas_norm)
        if not coincide:
            continue
        estilo = (p.style.name or "") if p.style is not None else ""
        if estilo.startswith("Heading") or estilo == "Title":
            return i
        if candidato_texto is None:
            candidato_texto = i
    if candidato_texto is not None:
        return candidato_texto
    raise SinInicioDeCuerpo(
        "no se encontró el inicio del cuerpo. Pasa --inicio-cuerpo con el texto "
        "exacto del primer encabezado del cuerpo."
    )


def _fijar_pgnumtype(sect_pr, fmt: str, start: int | None) -> None:
    """Escribe w:pgNumType en un w:sectPr, respetando el orden del esquema."""
    pg = sect_pr.find(qn("w:pgNumType"))
    if pg is None:
        pg = sect_pr.makeelement(qn("w:pgNumType"), {})
        # w:pgNumType va después de w:cols / w:paperSrc y antes de w:docGrid.
        docgrid = sect_pr.find(qn("w:docGrid"))
        if docgrid is not None:
            docgrid.addprevious(pg)
        else:
            sect_pr.append(pg)
    pg.set(qn("w:fmt"), fmt)
    if start is None:
        if pg.get(qn("w:start")) is not None:
            del pg.attrib[qn("w:start")]
    else:
        pg.set(qn("w:start"), str(start))


def _campo_pagina(parrafo) -> None:
    """Inserta un campo PAGE de Word en el párrafo (número de página real)."""
    for run in list(parrafo.runs):
        run._element.getparent().remove(run._element)
    run = parrafo.add_run()
    el = run._element

    begin = el.makeelement(qn("w:fldChar"), {qn("w:fldCharType"): "begin"})
    instr = el.makeelement(qn("w:instrText"), {qn("xml:space"): "preserve"})
    instr.text = " PAGE "
    sep = el.makeelement(qn("w:fldChar"), {qn("w:fldCharType"): "separate"})
    texto = el.makeelement(qn("w:t"), {})
    texto.text = "1"
    end = el.makeelement(qn("w:fldChar"), {qn("w:fldCharType"): "end"})
    for nodo in (begin, instr, sep, texto, end):
        el.append(nodo)


def _pie_con_numero(seccion, alineacion: str) -> None:
    from docx.enum.text import WD_ALIGN_PARAGRAPH

    seccion.footer.is_linked_to_previous = False
    pie = seccion.footer
    parrafo = pie.paragraphs[0] if pie.paragraphs else pie.add_paragraph()
    parrafo.alignment = (WD_ALIGN_PARAGRAPH.RIGHT if alineacion == "derecha"
                         else WD_ALIGN_PARAGRAPH.CENTER)
    _campo_pagina(parrafo)


def _encabezado_con_numero(seccion, alineacion: str) -> None:
    from docx.enum.text import WD_ALIGN_PARAGRAPH

    seccion.header.is_linked_to_previous = False
    cab = seccion.header
    parrafo = cab.paragraphs[0] if cab.paragraphs else cab.add_paragraph()
    parrafo.alignment = (WD_ALIGN_PARAGRAPH.RIGHT if alineacion == "derecha"
                         else WD_ALIGN_PARAGRAPH.CENTER)
    _campo_pagina(parrafo)


def aplicar(ruta: pathlib.Path, inicio_cuerpo: str | None = None,
            posicion: str = "inferior_derecha",
            destino: pathlib.Path | None = None) -> pathlib.Path:
    """Aplica la numeración y guarda el documento.

    posicion: 'inferior_derecha', 'inferior_centro' o 'superior_derecha'
              (Letras exige esta última).
    """
    doc = Document(str(ruta))

    marcas = (inicio_cuerpo,) if inicio_cuerpo else INICIOS_CUERPO
    idx = localizar_inicio_cuerpo(doc, marcas)
    if idx == 0:
        raise SinInicioDeCuerpo(
            "el cuerpo empieza en el primer párrafo: no hay preliminares que numerar "
            "en romanos. Revisa que el documento incluya carátula y resumen."
        )

    cuerpo = doc.element.body
    sect_final = cuerpo.find(qn("w:sectPr"))
    if sect_final is None:
        raise ValueError("el documento no tiene w:sectPr final; ¿está corrupto?")

    # Sección 1 (preliminares): el salto va en el párrafo anterior al cuerpo.
    p_anterior = doc.paragraphs[idx - 1]
    p_pr = p_anterior._p.get_or_add_pPr()
    sect_prelim = copy.deepcopy(sect_final)
    for hijo in list(sect_prelim.findall(qn("w:headerReference"))):
        sect_prelim.remove(hijo)
    for hijo in list(sect_prelim.findall(qn("w:footerReference"))):
        sect_prelim.remove(hijo)
    _fijar_pgnumtype(sect_prelim, "lowerRoman", 1)
    p_pr.append(sect_prelim)

    # Sección 2 (cuerpo): arábigos reiniciados en 1.
    _fijar_pgnumtype(sect_final, "decimal", 1)

    secciones = doc.sections
    if len(secciones) < 2:
        raise RuntimeError(
            "no se creó la segunda sección; el documento quedó sin dividir."
        )

    alineacion = "derecha" if posicion.endswith("derecha") else "centro"
    for seccion in secciones:
        if posicion.startswith("superior"):
            _encabezado_con_numero(seccion, alineacion)
        else:
            _pie_con_numero(seccion, alineacion)
    # La segunda sección no debe heredar la numeración de la primera.
    secciones[1].footer.is_linked_to_previous = False
    secciones[1].header.is_linked_to_previous = False

    destino = destino or ruta
    doc.save(str(destino))
    return destino


def describir(ruta: pathlib.Path) -> dict[str, object]:
    """Lee el documento y resume cómo quedó numerado. Se usa en los tests."""
    doc = Document(str(ruta))
    resultado: list[dict[str, object]] = []
    for i, seccion in enumerate(doc.sections):
        pg = seccion._sectPr.find(qn("w:pgNumType"))
        xml_pie = seccion.footer._element.xml if seccion.footer is not None else ""
        xml_cab = seccion.header._element.xml if seccion.header is not None else ""
        resultado.append({
            "seccion": i,
            "formato": pg.get(qn("w:fmt")) if pg is not None else None,
            "inicio": pg.get(qn("w:start")) if pg is not None else None,
            "campo_page_en_pie": "PAGE" in xml_pie,
            "campo_page_en_encabezado": "PAGE" in xml_cab,
        })
    return {"secciones": len(doc.sections), "detalle": resultado}


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("docx", type=pathlib.Path)
    ap.add_argument("--inicio-cuerpo", help="texto exacto del primer encabezado del cuerpo")
    ap.add_argument("--posicion", default="inferior_derecha",
                    choices=["inferior_derecha", "inferior_centro", "superior_derecha"])
    ap.add_argument("--salida", type=pathlib.Path)
    args = ap.parse_args(argv)

    try:
        destino = aplicar(args.docx, args.inicio_cuerpo, args.posicion, args.salida)
    except (SinInicioDeCuerpo, ValueError, RuntimeError) as e:
        print(f"ERROR: {e}", file=sys.stderr)
        return 1
    info = describir(destino)
    print(f"OK  {destino}")
    for d in info["detalle"]:
        print(f"    sección {d['seccion']}: formato={d['formato']} inicio={d['inicio']} "
              f"PAGE en pie={d['campo_page_en_pie']} en encabezado={d['campo_page_en_encabezado']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
