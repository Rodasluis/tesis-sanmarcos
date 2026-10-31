"""Genera el proyecto de tesis en .docx y PDF.

El proyecto de tesis es un documento aparte de la tesis y llega antes: es lo que
la escuela registra y aprueba para que el trabajo empiece.

Qué hace esta herramienta:

1. Toma los `.qmd` de `proyecto/`, en orden.
2. Los renderiza a .docx con la plantilla del perfil activo, igual que la tesis.
3. Le antepone la **carátula con el escudo de la UNMSM**, con el rótulo
   «PROYECTO DE TESIS» en lugar de «TESIS».
4. Convierte el .docx a PDF.
5. Comprueba que estén las secciones que el perfil exige para el proyecto.

Las dos salidas van a `entregables/PROYECTO/`.

## Por qué .docx y PDF

El .docx es lo que se entrega y lo que se corrige: la escuela devuelve
observaciones sobre él. El PDF es lo que se imprime, se adjunta a un correo o se
sube a un formulario sin que se descoloque la maquetación. Son el mismo
documento, convertido, no dos documentos distintos.

Uso:
    uv run python -m herramientas.entregar_proyecto
    uv run python -m herramientas.entregar_proyecto --comprobar
"""
from __future__ import annotations

import argparse
import pathlib
import sys

from herramientas import caratula, pdf
from herramientas.entregar import (
    _render,
    cargar_datos,
    comprobar_rutas,
    leer_autores,
    nombre_archivo,
    revisar_docx,
)
from herramientas.informe import Informe
from herramientas.perfiles import (
    ErrorDePerfil,
    cargar_de,
    enfoque_activo,
    perfil_activo,
)

RAIZ = pathlib.Path(__file__).resolve().parent.parent

#: Dónde vive el proyecto. Separado de `capitulos/`, que es la tesis.
DIR_PROYECTO = "proyecto"


def capitulos_del_proyecto(raiz: pathlib.Path) -> list[pathlib.Path]:
    base = raiz / DIR_PROYECTO
    return sorted(base.rglob("*.qmd")) if base.exists() else []


#: Lo que produce la carátula. Reclamarlo como sección ausente mandaría al
#: tesista a escribir a mano una página que esta herramienta ya genera.
LA_PONE_LA_CARATULA = ("primera pagina", "primera página", "caratula", "carátula",
                       "portada")

#: El índice de un .docx es un campo de Word, no texto del .qmd: se inserta en
#: el documento ya generado. No se reclama como sección; se avisa con Y15.
LO_PONE_WORD = ("indice", "índice", "indice general", "índice general",
                "tabla de contenido")


def titulos_del_esquema(perfil, enfoque: str | None = None) -> list[str]:
    """Los títulos del esquema de proyecto, tal como los escribe el perfil.

    Un perfil puede declararlos de dos maneras. La mayoría pone una sola lista
    en `proyecto.secciones`. Medicina trae **un esquema por enfoque** —el anexo
    C para el cuantitativo y el D para el cualitativo— en `proyecto.modelos`.
    """
    proyecto = perfil.get("proyecto") or {}
    crudas = proyecto.get("secciones") or []
    if not crudas and enfoque:
        modelo = (proyecto.get("modelos") or {}).get(enfoque) or {}
        crudas = modelo.get("secciones") or []
    titulos = []
    for s in crudas:
        if isinstance(s, dict):
            t = s.get("titulo") or s.get("parte")
            if t:
                titulos.append(str(t))
        elif isinstance(s, str):
            titulos.append(s)
    return titulos


def secciones_esperadas(perfil, enfoque: str | None = None) -> list[str]:
    """Las del esquema que el tesista sí tiene que escribir en `proyecto/`."""
    fuera = LA_PONE_LA_CARATULA + LO_PONE_WORD
    return [t for t in titulos_del_esquema(perfil, enfoque)
            if t.strip().lower() not in fuera]


def _normalizar(texto: str) -> str:
    import re
    import unicodedata
    t = unicodedata.normalize("NFKD", texto)
    t = "".join(c for c in t if not unicodedata.combining(c))
    return re.sub(r"\s+", " ", re.sub(r"[^a-z0-9 ]+", " ", t.lower())).strip()


def revisar_secciones(raiz: pathlib.Path, perfil, inf: Informe,
                      enfoque: str | None = None) -> None:
    esperadas = secciones_esperadas(perfil, enfoque)
    if not esperadas:
        inf.info("Y05", "el perfil no define secciones propias para el proyecto: "
                        "se usa el orden que el tesista haya decidido")
        return

    texto = " ".join(
        _normalizar(r.read_text(encoding="utf8", errors="replace"))
        for r in capitulos_del_proyecto(raiz))
    faltan = [t for t in esperadas if _normalizar(t) not in texto]
    inf.anotar(secciones_esperadas=len(esperadas), secciones_faltantes=len(faltan))
    for t in faltan:
        inf.aviso("Y06", f"no se encontró la sección «{t}» que el perfil pide para "
                         f"el proyecto")

    if any(t.strip().lower() in LO_PONE_WORD
           for t in titulos_del_esquema(perfil, enfoque)):
        inf.info("Y15", "el esquema del perfil incluye un índice. No se escribe en "
                        "el .qmd: se inserta en el .docx generado, con Referencias "
                        "→ Tabla de contenido, para que las páginas se actualicen "
                        "solas")


def preparar(raiz: pathlib.Path = RAIZ, solo_comprobar: bool = False,
             perfil_id: str | None = None) -> Informe:
    inf = Informe("entrega_proyecto", "Generación del proyecto de tesis", raiz=raiz)

    pid = perfil_id or perfil_activo(raiz)
    if not pid:
        inf.error("Y00", "no hay perfil activo. Actívalo con "
                         "`uv run python -m herramientas.activar_perfil <id>`")
        return inf
    try:
        perfil = cargar_de(raiz, pid)
    except ErrorDePerfil as e:
        inf.error("Y00", f"no se pudo cargar el perfil: {e}")
        return inf
    # El esquema del proyecto depende del enfoque donde la facultad trae uno
    # por enfoque, como Medicina: el anexo C para el cuantitativo y el D
    # para el cualitativo. Sin `.enfoque` no se adivina.
    enfoque = enfoque_activo(raiz)
    inf.anotar(perfil=pid, enfoque=enfoque or "sin declarar")

    entradas = capitulos_del_proyecto(raiz)
    inf.anotar(qmd_del_proyecto=len(entradas))
    if not entradas:
        inf.error("Y01", f"no hay archivos .qmd en `{DIR_PROYECTO}/`. El proyecto se "
                         f"redacta en /proyecto antes de generarlo")
        return inf

    ruta_datos = raiz / "entregables" / "datos_de_entrega.yaml"
    if not ruta_datos.exists():
        inf.error("Y02", "falta `entregables/datos_de_entrega.yaml`. Córrelo primero "
                         "con `uv run python -m herramientas.entregar --comprobar`, "
                         "que crea la plantilla")
        return inf

    datos = cargar_datos(ruta_datos)
    autores = leer_autores(datos)
    if not autores:
        inf.error("Y03", "no hay autores en `datos_de_entrega.yaml`")
        return inf

    # La carátula del proyecto necesita lo mismo que la de la tesis, pero aquí
    # nada de esto bloquea: el proyecto se genera incompleto y se completa.
    for falta in caratula.faltantes(datos, perfil):
        inf.aviso("Y04", f"la carátula del proyecto va incompleta: falta {falta}")

    revisar_secciones(raiz, perfil, inf, enfoque)

    if solo_comprobar or inf.hay_errores:
        return inf

    referencia = raiz / "plantillas" / pid / "referencia.docx"
    if not referencia.exists():
        inf.error("Y07", f"falta la plantilla {referencia.relative_to(raiz)}. Genérala "
                         f"con `uv run python -m herramientas.plantilla_docx "
                         f"--perfil {pid}`")
        return inf

    titulo = str(datos.get("titulo") or "").strip()
    anio = int(datos.get("anio") or 0) or None
    nombre = nombre_archivo(autores, "Proyecto de Tesis", titulo, anio or 0)

    destino_dir = raiz / "entregables" / "PROYECTO"
    destino_dir.mkdir(parents=True, exist_ok=True)
    destino = destino_dir / nombre

    if not comprobar_rutas([destino], inf):
        return inf

    ok, motivo = _render(entradas, destino, referencia, raiz)
    if not ok:
        inf.error("Y08", f"no se pudo generar el .docx del proyecto: {motivo}")
        return inf

    revisar_docx(destino, inf)

    try:
        avisos = caratula.anteponer(destino, datos, perfil, "proyecto", raiz=raiz)
        for aviso in avisos:
            inf.aviso("Y14", aviso)
        inf.info("Y09", "carátula del proyecto insertada, con el escudo de la UNMSM")
    except Exception as e:  # noqa: BLE001
        inf.aviso("Y10", f"no se pudo insertar la carátula: {e}. El contenido del "
                         f"proyecto está bien")

    inf.info("Y11", f"generado {destino.relative_to(raiz)}")

    hechos, problemas = pdf.convertir_varios([destino])
    for ruta in hechos:
        inf.info("Y12", f"PDF generado: {ruta.relative_to(raiz)}")
    for p in problemas:
        inf.aviso("Y13", f"no se generó el PDF; el .docx está completo. {p}")

    return inf


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--comprobar", action="store_true",
                    help="revisa sin generar nada")
    ap.add_argument("--perfil")
    ap.add_argument("--raiz", type=pathlib.Path, default=RAIZ)
    ap.add_argument("--sin-informe", action="store_true")
    ap.add_argument("--detalle", action="store_true")
    args = ap.parse_args(argv)

    inf = preparar(raiz=args.raiz, solo_comprobar=args.comprobar,
                   perfil_id=args.perfil)
    print(inf.volcar(en_disco=not args.sin_informe, mostrar_info=args.detalle))
    return inf.codigo_salida()


if __name__ == "__main__":
    sys.exit(main())
