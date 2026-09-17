"""Detecta repeticiones entre capítulos y fragmentos copiados de la biblioteca.

**Esto no es Turnitin y no estima el porcentaje oficial de similitud.** El
porcentaje que vale lo calcula la plataforma PIDS de la UNMSM y lo carga el
asesor (Directiva de originalidad, RR N.° 000947-2026-R, arts. 12 y 24). Aquí no
hay acceso a esa base de datos ni a la web, así que cualquier número que saliera
de este archivo sería falso y peligroso: le daría al tesista una confianza que
no corresponde.

Lo que sí hace, que es útil y distinto:

1. **Repeticiones internas.** Encuentra pasajes que se repiten entre capítulos.
   Suelen ser párrafos de marco teórico reciclados en la discusión, o resúmenes
   copiados del proyecto al informe final. Turnitin también los marca.
2. **Fragmentos de la biblioteca sin comillas ni cita.** Busca en los PDF que el
   tesista tiene en Zotero pasajes de más de 20 palabras que aparecen en el
   texto sin entrecomillar y sin cita cercana. Eso es lo que la directiva llama
   presentar un manuscrito ajeno como propio (art. 30 a).

El umbral de 20 palabras no es arbitrario: es el que fija el art. 14 de la
directiva para las coincidencias que la PIDS sí contabiliza.

Uso:
    uv run python -m herramientas.similitud_interna
    uv run python -m herramientas.similitud_interna --biblioteca ~/Zotero/storage
"""
from __future__ import annotations

import argparse
import pathlib
import re
import sys
import unicodedata
from collections import defaultdict

from herramientas.informe import Informe, iter_qmd

RAIZ = pathlib.Path(__file__).resolve().parent.parent

#: Art. 14 de la directiva: por debajo de 20 palabras no se contabiliza.
VENTANA = 20

BLOQUE_CODIGO = re.compile(r"^(```|~~~)")
RE_CITA = re.compile(r"\[[^\]]*@[^\]]*\]|(?<![\w`])@[A-Za-z0-9_][\w:.#$%&+?<>~/-]*")
RE_ENTRECOMILLADO = re.compile(r"[«\"“][^«»\"“”]{20,}[»\"”]")

#: Muletillas académicas que se repiten legítimamente y no son plagio.
FRASES_INOCUAS = (
    "universidad nacional mayor de san marcos",
    "de acuerdo con los resultados obtenidos",
    "para optar el titulo profesional de",
)


def _normalizar(texto: str) -> list[str]:
    t = unicodedata.normalize("NFKD", texto)
    t = "".join(c for c in t if not unicodedata.combining(c))
    t = re.sub(r"[^a-z0-9\s]+", " ", t.lower())
    return t.split()


def _texto_util(ruta: pathlib.Path) -> list[tuple[int, str]]:
    """Líneas fuera de bloques de código, con su número."""
    texto = ruta.read_text(encoding="utf8", errors="replace")
    if texto.startswith("---"):
        fin = texto.find("\n---", 3)
        if fin > 0:
            saltos = texto[:fin].count("\n") + 1
            texto = "\n" * saltos + texto[fin + 4:]
    salida: list[tuple[int, str]] = []
    dentro = False
    for i, linea in enumerate(texto.splitlines(), 1):
        if BLOQUE_CODIGO.match(linea.strip()):
            dentro = not dentro
            continue
        if not dentro:
            salida.append((i, linea))
    return salida


def _ventanas(palabras: list[str], indices: list[int], tam: int = VENTANA):
    """Genera (firma, línea_inicial) para cada ventana de `tam` palabras."""
    for i in range(len(palabras) - tam + 1):
        yield " ".join(palabras[i:i + tam]), indices[i]


def _palabras_con_linea(lineas: list[tuple[int, str]]) -> tuple[list[str], list[int]]:
    palabras: list[str] = []
    indices: list[int] = []
    for num, linea in lineas:
        for p in _normalizar(linea):
            palabras.append(p)
            indices.append(num)
    return palabras, indices


def _es_inocua(firma: str) -> bool:
    return any(f in firma for f in FRASES_INOCUAS)


def _lineas_protegidas(lineas: list[tuple[int, str]]) -> set[int]:
    """Líneas entrecomilladas, en bloque de cita, o con cita bibliográfica cerca."""
    protegidas: set[int] = set()
    numeros = [n for n, _ in lineas]
    por_numero = dict(lineas)
    for num, linea in lineas:
        if (RE_ENTRECOMILLADO.search(linea) or RE_CITA.search(linea)
                or linea.lstrip().startswith(">")):
            protegidas.add(num)
    # una cita al final del párrafo cubre las líneas contiguas anteriores
    for num in sorted(protegidas):
        i = numeros.index(num) if num in numeros else -1
        for j in range(max(i - 3, 0), i):
            if por_numero.get(numeros[j], "").strip():
                protegidas.add(numeros[j])
    return protegidas


def _texto_de_pdf(ruta: pathlib.Path, max_paginas: int = 300) -> str:
    try:
        from pypdf import PdfReader
        lector = PdfReader(str(ruta))
    except Exception:  # noqa: BLE001
        return ""
    trozos: list[str] = []
    for pagina in lector.pages[:max_paginas]:
        try:
            trozos.append(pagina.extract_text() or "")
        except Exception:  # noqa: BLE001
            continue
    return " ".join(trozos)


def verificar(raiz: pathlib.Path = RAIZ, biblioteca: pathlib.Path | None = None,
              ventana: int = VENTANA) -> Informe:
    inf = Informe("similitud_interna", "Repeticiones internas y fragmentos sin citar",
                  raiz=raiz)
    inf.anotar(ventana_de_palabras=ventana)
    inf.info("S00", "Esta herramienta NO mide el porcentaje de similitud oficial. "
                    "Ese lo calcula la plataforma PIDS de la universidad y lo carga "
                    "tu asesor. Aquí solo se buscan repeticiones y fragmentos sin citar")

    archivos = iter_qmd(raiz)
    inf.anotar(capitulos_revisados=len(archivos))
    if not archivos:
        inf.info("S01", "no hay capítulos todavía; nada que comparar")
        return inf

    # 1 — repeticiones entre capítulos
    apariciones: dict[str, list[tuple[pathlib.Path, int]]] = defaultdict(list)
    protegidas_por_archivo: dict[pathlib.Path, set[int]] = {}
    for ruta in archivos:
        lineas = _texto_util(ruta)
        protegidas_por_archivo[ruta] = _lineas_protegidas(lineas)
        palabras, indices = _palabras_con_linea(lineas)
        vistas_en_este: set[str] = set()
        for firma, linea in _ventanas(palabras, indices, ventana):
            if _es_inocua(firma) or firma in vistas_en_este:
                continue
            vistas_en_este.add(firma)
            apariciones[firma].append((ruta, linea))

    reportadas: set[tuple[str, str]] = set()
    repeticiones = 0
    for firma, sitios in apariciones.items():
        if len(sitios) < 2:
            continue
        archivos_distintos = {r for r, _ in sitios}
        par = tuple(sorted(str(r.relative_to(raiz)) for r in archivos_distintos)[:2])
        if len(par) == 2 and par in reportadas:
            continue
        if len(par) == 2:
            reportadas.add(par)
        repeticiones += 1
        donde = "; ".join(f"{ruta.relative_to(raiz)}:{num}" for ruta, num in sitios[:3])
        nivel = inf.aviso if len(archivos_distintos) > 1 else inf.info
        nivel("S02", f"pasaje de {ventana} palabras repetido en {len(sitios)} sitios "
                     f"({donde}). Reescríbelo o cítalo si corresponde",
              archivo=sitios[0][0], linea=sitios[0][1],
              fragmento=firma[:110])
    inf.anotar(repeticiones_internas=repeticiones)

    # 2 — fragmentos de la biblioteca sin comillas ni cita
    if biblioteca is None:
        inf.info("S03", "no se indicó biblioteca de PDF (`--biblioteca`), así que no "
                        "se buscaron fragmentos copiados de tus lecturas")
        return inf
    if not biblioteca.exists():
        inf.aviso("S04", f"la biblioteca indicada no existe: {biblioteca}")
        return inf

    pdfs = sorted(biblioteca.rglob("*.pdf"))
    inf.anotar(pdfs_en_la_biblioteca=len(pdfs))
    if not pdfs:
        inf.aviso("S05", f"no hay PDF en {biblioteca}")
        return inf

    indice_biblioteca: dict[str, str] = {}
    ilegibles = 0
    for pdf in pdfs:
        texto = _texto_de_pdf(pdf)
        if not texto.strip():
            ilegibles += 1
            continue
        palabras = _normalizar(texto)
        for i in range(0, max(len(palabras) - ventana + 1, 0)):
            firma = " ".join(palabras[i:i + ventana])
            indice_biblioteca.setdefault(firma, pdf.name)
    if ilegibles:
        inf.aviso("S06", f"{ilegibles} PDF no se pudieron leer (¿escaneados sin capa "
                         "de texto?). Sus fragmentos no se comprobaron")
    inf.anotar(fragmentos_indexados=len(indice_biblioteca))

    sin_citar = 0
    for ruta in archivos:
        lineas = _texto_util(ruta)
        protegidas = protegidas_por_archivo.get(ruta, set())
        palabras, indices = _palabras_con_linea(lineas)
        ya = set()
        for firma, linea in _ventanas(palabras, indices, ventana):
            if firma in ya or _es_inocua(firma):
                continue
            origen = indice_biblioteca.get(firma)
            if not origen:
                continue
            ya.add(firma)
            if linea in protegidas:
                inf.info("S07", f"coincide con «{origen}», pero el pasaje está "
                                "entrecomillado o citado",
                         archivo=ruta, linea=linea)
                continue
            sin_citar += 1
            inf.error("S08", f"pasaje de {ventana} palabras que coincide con «{origen}» "
                             "sin comillas y sin cita. La directiva lo trata como "
                             "presentar un texto ajeno como propio (art. 30 a)",
                      archivo=ruta, linea=linea, origen=origen,
                      fragmento=firma[:110])
    inf.anotar(fragmentos_sin_citar=sin_citar)
    return inf


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--biblioteca", type=pathlib.Path,
                    help="carpeta con los PDF de tus lecturas (p. ej. Zotero/storage)")
    ap.add_argument("--ventana", type=int, default=VENTANA,
                    help=f"palabras por ventana (por defecto {VENTANA}, el umbral de la directiva)")
    ap.add_argument("--sin-informe", action="store_true")
    ap.add_argument("--detalle", action="store_true")
    args = ap.parse_args(argv)

    inf = verificar(biblioteca=args.biblioteca, ventana=args.ventana)
    print(inf.volcar(en_disco=not args.sin_informe, mostrar_info=args.detalle))
    return inf.codigo_salida()


if __name__ == "__main__":
    sys.exit(main())
