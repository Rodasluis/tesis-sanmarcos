"""Construye la carátula del proyecto de tesis y de la tesis.

## De dónde sale este diseño

No de una plantilla inventada ni de lo que un modelo recuerde. Se tomó de **dos
tesis reales publicadas en Cybertesis en 2026**, de facultades distintas —una de
Medicina y otra de Letras—, cuyas carátulas son idénticas en estructura:

    [escudo de la UNMSM]
    Universidad Nacional Mayor de San Marcos      (negrita)
    Universidad del Perú. Decana de América       (negrita, menor)
    Facultad de …
    Escuela Profesional de …

    TÍTULO DE LA TESIS                            (negrita, interlineado amplio)

    TESIS                                         (negrita, versales)
    Para optar el Título Profesional de …

    AUTOR                                         (negrita, versales)
    Nombres APELLIDOS

    ASESOR / ASESORA                              (negrita, versales)
    Grado Nombres APELLIDOS

    Lima, Perú
    2026

Eso coincide además con lo que exige el Anexo 2A de la RR N.° 00744-R-20:
escudo, facultad, escuela profesional, título, la fórmula «Tesis para optar al
título profesional de…», nombres y apellidos del bachiller, nombres y apellidos
del asesor, y fecha.

## Dos detalles que se ven en las carátulas reales y no en la norma

- **Se usa el escudo solo**, sin la palabra «UNMSM» debajo. El nombre de la
  universidad va escrito como texto, no como parte de la imagen.
- **Los apellidos van en versales** y los nombres de pila en caja normal:
  «Kathia Tereza BASURTO SALAZAR». Sirve para que no haya duda de cuál es cuál,
  que en el Perú no siempre es obvio.

El rótulo del asesor se declina —ASESOR o ASESORA— y el del autor no: en las dos
carátillas revisadas dice AUTOR incluso cuando la autora es mujer. Se respeta lo
observado y se deja configurable.
"""
from __future__ import annotations

import pathlib

from docx.enum.text import WD_ALIGN_PARAGRAPH, WD_BREAK
from docx.shared import Cm, Pt

RAIZ = pathlib.Path(__file__).resolve().parent.parent

#: El escudo, recortado del logo oficial. Lo genera `herramientas.marca`.
ESCUDO = "plantillas/marca/escudo_unmsm.png"

#: Alto del escudo en la carátula. Medido sobre las tesis publicadas: ocupa algo
#: menos de dos centímetros y el ancho sale solo, por proporción.
ALTO_ESCUDO_CM = 1.9

#: Los espacios entre bloques están ajustados para que la carátula ocupe la
#: página entera, como en las tesis publicadas: el escudo arriba y «Lima, Perú»
#: cerca del pie. Una carátula apelotonada en el tercio superior se nota.

TIPOS = {
    "tesis": {
        "rotulo": "TESIS",
        "formula": "Para optar el Título Profesional de {titulo_profesional}",
    },
    "proyecto": {
        "rotulo": "PROYECTO DE TESIS",
        "formula": "Para optar el Título Profesional de {titulo_profesional}",
    },
}


def buscar_escudo(raiz: pathlib.Path = RAIZ) -> pathlib.Path | None:
    """El escudo del proyecto; si no lo tiene, el del repositorio instalado.

    Un proyecto puede ser una copia a la que le falta `plantillas/marca/`. En
    ese caso usar el escudo que vienen con las herramientas es mejor que
    entregar una carátula sin escudo, y no cambia nada: es el mismo archivo.
    """
    for base in (raiz, RAIZ):
        candidato = base / ESCUDO
        if candidato.exists():
            return candidato
    return None


def nombre_con_apellidos_en_versales(nombres: str, apellidos: str) -> str:
    """«Kathia Tereza» + «Basurto Salazar» → «Kathia Tereza BASURTO SALAZAR»."""
    nombres = " ".join(nombres.split())
    apellidos = " ".join(apellidos.split()).upper()
    return f"{nombres} {apellidos}".strip()


def _parrafo(doc, texto: str, *, negrita: bool = False, tamano: int | None = None,
             espacio_antes: int = 0, espacio_despues: int = 0,
             interlineado: float | None = None):
    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    pf = p.paragraph_format
    pf.space_before = Pt(espacio_antes)
    pf.space_after = Pt(espacio_despues)
    if interlineado:
        pf.line_spacing = interlineado
    if texto:
        r = p.add_run(texto)
        r.bold = negrita
        if tamano:
            r.font.size = Pt(tamano)
    return p


def _rotulo_asesor(asesor: dict) -> str:
    """ASESOR o ASESORA, según lo que el propio tesista haya declarado."""
    explicito = (asesor.get("rotulo") or "").strip()
    if explicito:
        return explicito.upper()
    if str(asesor.get("genero", "")).strip().lower() in {"f", "femenino", "mujer"}:
        return "ASESORA"
    return "ASESOR"


def _nombre_de_asesor(asesor: dict) -> str:
    """Grado + nombre, con los apellidos en versales si vienen separados."""
    if asesor.get("apellidos") or asesor.get("nombres"):
        base = nombre_con_apellidos_en_versales(
            asesor.get("nombres", ""), asesor.get("apellidos", ""))
    else:
        base = " ".join(str(asesor.get("nombres_y_apellidos", "")).split())
    grado = (asesor.get("grado") or "").strip()
    return f"{grado} {base}".strip()


def construir(doc, datos: dict, perfil, tipo: str = "tesis",
              raiz: pathlib.Path = RAIZ, salto_al_final: bool = True) -> list[str]:
    """Escribe la carátula al principio de `doc`.

    `doc` es un `docx.Document` recién abierto: la carátula va primero y todo lo
    demás viene después.

    Devuelve la lista de avisos. El más importante es la falta del escudo: si se
    omitiera en silencio, saldría una carátula que parece correcta y que la
    escuela devuelve.
    """
    avisos: list[str] = []
    if tipo not in TIPOS:
        raise ValueError(f"tipo de carátula desconocido: {tipo!r}. "
                         f"Los válidos son: {', '.join(TIPOS)}")
    conf = TIPOS[tipo]

    escudo = buscar_escudo(raiz)
    if escudo is not None:
        p = doc.add_paragraph()
        p.alignment = WD_ALIGN_PARAGRAPH.CENTER
        p.paragraph_format.space_after = Pt(10)
        p.add_run().add_picture(str(escudo), height=Cm(ALTO_ESCUDO_CM))
    else:
        avisos.append(
            f"no se encontró {ESCUDO} ni en el proyecto ni en el repositorio, "
            f"así que la carátula sale SIN el escudo de la UNMSM. Regenéralo "
            f"con `uv run python -m herramientas.marca`")

    _parrafo(doc, "Universidad Nacional Mayor de San Marcos",
             negrita=True, tamano=14)
    _parrafo(doc, "Universidad del Perú. Decana de América",
             negrita=True, tamano=11)
    _parrafo(doc, str(datos.get("facultad") or perfil.get("facultad") or ""),
             tamano=13)
    _parrafo(doc, str(datos.get("escuela") or ""), tamano=13, espacio_despues=54)

    _parrafo(doc, str(datos.get("titulo") or ""), negrita=True, tamano=14,
             interlineado=1.5, espacio_despues=54)

    _parrafo(doc, conf["rotulo"], negrita=True, tamano=12)
    _parrafo(doc,
             conf["formula"].format(
                 titulo_profesional=str(datos.get("titulo_profesional") or "")),
             tamano=12, espacio_despues=48)

    autores = datos.get("autores") or []
    _parrafo(doc, "AUTORA" if _una_sola_autora(autores) else
             ("AUTORES" if len(autores) > 1 else "AUTOR"),
             negrita=True, tamano=12)
    for autor in autores:
        _parrafo(doc, nombre_con_apellidos_en_versales(
            autor.get("nombres", ""), autor.get("apellidos", "")), tamano=12)
    if not autores:
        _parrafo(doc, "", tamano=12)

    asesor = datos.get("asesor") or {}
    _parrafo(doc, _rotulo_asesor(asesor), negrita=True, tamano=12,
             espacio_antes=36)
    _parrafo(doc, _nombre_de_asesor(asesor), tamano=12, espacio_despues=60)

    _parrafo(doc, "Lima, Perú", tamano=12)
    _parrafo(doc, str(datos.get("anio") or ""), tamano=12)

    if salto_al_final:
        doc.add_paragraph().add_run().add_break(WD_BREAK.PAGE)
    return avisos


def _una_sola_autora(autores: list[dict]) -> bool:
    """Solo se declina si el propio tesista lo pidió; no se adivina por el nombre."""
    if len(autores) != 1:
        return False
    genero = str(autores[0].get("genero", "")).strip().lower()
    return genero in {"f", "femenino", "mujer"}


def texto_plano(datos: dict, perfil, tipo: str = "tesis") -> str:
    """La misma carátula en texto, para comprobarla sin abrir Word."""
    conf = TIPOS[tipo]
    autores = datos.get("autores") or []
    lineas = [
        "[escudo de la UNMSM]",
        "Universidad Nacional Mayor de San Marcos",
        "Universidad del Perú. Decana de América",
        str(datos.get("facultad") or perfil.get("facultad") or ""),
        str(datos.get("escuela") or ""),
        "",
        str(datos.get("titulo") or ""),
        "",
        conf["rotulo"],
        conf["formula"].format(
            titulo_profesional=str(datos.get("titulo_profesional") or "")),
        "",
        "AUTORA" if _una_sola_autora(autores) else
        ("AUTORES" if len(autores) > 1 else "AUTOR"),
    ]
    lineas += [nombre_con_apellidos_en_versales(a.get("nombres", ""),
                                                a.get("apellidos", ""))
               for a in autores]
    asesor = datos.get("asesor") or {}
    lineas += ["", _rotulo_asesor(asesor), _nombre_de_asesor(asesor), "",
               "Lima, Perú", str(datos.get("anio") or "")]
    return "\n".join(lineas)


def faltantes(datos: dict, perfil) -> list[str]:
    """Qué le falta a la carátula para estar completa, en palabras del tesista."""
    falta = []
    if not str(datos.get("titulo") or "").strip():
        falta.append("el título de la tesis")
    if not (datos.get("facultad") or perfil.get("facultad")):
        falta.append("la facultad")
    if not str(datos.get("escuela") or "").strip():
        falta.append("la escuela profesional")
    if not str(datos.get("titulo_profesional") or "").strip():
        falta.append("el título profesional al que optas "
                     "(«Economista», «Licenciada en Enfermería»…)")
    if not (datos.get("autores") or []):
        falta.append("los autores")
    asesor = datos.get("asesor") or {}
    if not (asesor.get("nombres_y_apellidos") or asesor.get("apellidos")):
        falta.append("el nombre del asesor")
    if not str(datos.get("anio") or "").strip():
        falta.append("el año")
    return falta


def anteponer(ruta_docx: pathlib.Path, datos: dict, perfil, tipo: str = "tesis",
              raiz: pathlib.Path = RAIZ) -> list[str]:
    """Pone la carátula al principio de un .docx que ya existe.

    Hay una trampa de python-docx aquí, y cuesta verla porque no da ningún
    error: si la carátula se construye en un documento aparte y luego se mueven
    sus elementos XML al documento destino, **la imagen del escudo se pierde**.
    El párrafo viaja con una referencia (`r:embed`) a una relación que vive en
    el documento de origen; en el destino esa relación no existe. El .docx se
    abre, `inline_shapes` dice que hay una imagen, y la página sale en blanco.

    Por eso la carátula se construye DENTRO del documento destino —así la
    imagen y su relación quedan en la misma parte— y después sus elementos se
    mueven al principio del cuerpo.
    """
    import docx
    from docx.oxml.ns import qn

    doc = docx.Document(str(ruta_docx))
    cuerpo = doc.element.body

    # `add_paragraph` inserta ANTES del `w:sectPr` final del cuerpo, si lo hay.
    # Así que los elementos de contenido ocupan siempre las primeras
    # posiciones y el `sectPr` queda al final. Se cuenta sobre eso.
    #
    # No sirve identificar los elementos nuevos con `id()`: lxml crea un proxy
    # de Python distinto cada vez que se recorre el árbol, así que dos
    # recorridos del mismo nodo dan identidades distintas.
    def sin_sectpr() -> int:
        return len(cuerpo) - (1 if cuerpo.find(qn("w:sectPr")) is not None else 0)

    antes = sin_sectpr()
    avisos = construir(doc, datos, perfil, tipo, raiz=raiz)
    despues = sin_sectpr()

    nuevos = [cuerpo[i] for i in range(antes, despues)]
    for posicion, elemento in enumerate(nuevos):
        cuerpo.remove(elemento)
        cuerpo.insert(posicion, elemento)

    doc.save(str(ruta_docx))
    return avisos
