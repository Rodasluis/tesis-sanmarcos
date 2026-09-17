"""Genera los entregables del art. 13 de la Directiva de originalidad.

La RR N.° 000947-2026-R, art. 13 apartado A, exige que la tesis se entregue en
**dos archivos .docx** con nombres exactos, dentro de una estructura de carpetas
concreta, y que las tablas y fórmulas estén como texto y no como imágenes. Todo
eso se genera aquí; el tesista no tiene que recordar ninguna de esas reglas.

Lo que produce:

    entregables/
      TEXTO/
        Apellidos Nombres - Desarrollo Título - Año.docx
        Apellidos Nombres - Protocolo y Complemento Título - Año.docx
      DOCUMENTO/
        checklist_expediente.md
        declaracion_jurada_pids.md          (Anexo 4)
        declaracion_uso_de_ia.md            (voluntaria, ver más abajo)

Sobre la declaración de uso de IA: **ninguna norma leída la exige** (ver
`normativa/requisitos.md`, P-01). Se genera desde `registro/registro_ia.jsonl`
como medida voluntaria de transparencia, apoyada en el principio de transparencia
del art. 5 del Código de Ética. Se le presenta al tesista como tal, no como un
requisito.

Uso:
    uv run python -m herramientas.entregar --comprobar
    uv run python -m herramientas.entregar
"""
from __future__ import annotations

import argparse
import datetime as dt
import json
import pathlib
import re
import shutil
import subprocess
import sys
from dataclasses import dataclass, field

import yaml

from herramientas import docx_numeracion
from herramientas.informe import Informe
from herramientas.perfiles import ErrorDePerfil, cargar_de, perfil_activo

RAIZ = pathlib.Path(__file__).resolve().parent.parent
DATOS = RAIZ / "entregables" / "datos_de_entrega.yaml"

#: Caracteres que Windows no admite en un nombre de archivo.
PROHIBIDOS = r'<>:"/\|?*'

PLANTILLA_DATOS = """\
# Datos para generar los entregables. Los completa /iniciar o el tesista.
# Se usan tal cual en los nombres de archivo que exige el art. 13, así que
# escríbelos como deben aparecer.

titulo: ""                 # título exacto de la tesis
anio: null                 # año de sustentación, p. ej. 2026

autores:                   # hasta tres (RR 00744-R-20, §7.2 a)
  - apellidos: ""
    nombres: ""
    dni: ""
    objetivos: []          # obligatorio si la tesis es grupal (§7.2 b)

asesor:
  nombres_y_apellidos: ""
  correo: ""               # institucional

facultad: ""
escuela: ""
titulo_profesional: ""     # "Economista", "Licenciado en Educación", …
grupo_de_investigacion: ""
fuente_de_financiamiento: ""
disciplina_ocde: ""
titulo_en_ingles: ""
"""


@dataclass
class Autor:
    apellidos: str
    nombres: str
    dni: str = ""
    objetivos: list[str] = field(default_factory=list)

    @property
    def nombre_para_archivo(self) -> str:
        return f"{self.apellidos} {self.nombres}".strip()


def _limpiar(texto: str) -> str:
    """Quita lo que Windows no admite en un nombre de archivo."""
    limpio = "".join(" " if c in PROHIBIDOS else c for c in texto)
    return re.sub(r"\s+", " ", limpio).strip()


def nombre_archivo(autores: list[Autor], rotulo: str, titulo: str, anio: int,
                   extension: str = "docx") -> str:
    """Nombre exacto del art. 13 A.3.

    La directiva ejemplifica:
        Julca Pereda Dante Jorge - Desarrollo Competencia digitales en personas
        adultas - 2025.docx
    Obsérvese que entre el rótulo y el título no lleva guion.
    """
    if not autores:
        raise ValueError("no hay autores para nombrar el archivo")
    quien = autores[0].nombre_para_archivo
    if len(autores) > 1:
        quien = " y ".join(a.nombre_para_archivo for a in autores)
    return _limpiar(f"{quien} - {rotulo} {titulo} - {anio}") + f".{extension}"


def cargar_datos(ruta: pathlib.Path = DATOS) -> dict:
    if not ruta.exists():
        raise FileNotFoundError(ruta)
    return yaml.safe_load(ruta.read_text(encoding="utf8")) or {}


def leer_autores(datos: dict) -> list[Autor]:
    salida: list[Autor] = []
    for a in datos.get("autores") or []:
        if not isinstance(a, dict):
            continue
        salida.append(Autor(
            apellidos=(a.get("apellidos") or "").strip(),
            nombres=(a.get("nombres") or "").strip(),
            dni=(a.get("dni") or "").strip(),
            objetivos=[str(o) for o in (a.get("objetivos") or [])],
        ))
    return salida


def comprobar_datos(datos: dict, inf: Informe) -> list[Autor]:
    autores = leer_autores(datos)
    if not autores:
        inf.error("T01", "no hay autores en `entregables/datos_de_entrega.yaml`")
    for i, a in enumerate(autores, 1):
        if not a.apellidos or not a.nombres:
            inf.error("T02", f"el autor {i} no tiene apellidos o nombres completos")
    if len(autores) > 3:
        inf.error("T03", f"hay {len(autores)} autores. La directiva general permite "
                         "un máximo de tres (RR 00744-R-20, §7.2 a)")
    if len(autores) > 1:
        sin_objetivos = [a.nombre_para_archivo for a in autores if not a.objetivos]
        if sin_objetivos:
            inf.error("T04", "en una tesis grupal cada participante debe tener "
                             "objetivos definidos (§7.2 b). Sin objetivos: "
                             + ", ".join(sin_objetivos))
    if not (datos.get("titulo") or "").strip():
        inf.error("T05", "falta el título de la tesis")
    anio = datos.get("anio")
    if not isinstance(anio, int):
        inf.error("T06", "falta el año de sustentación, o no es un número")
    return autores


# ---------------------------------------------------------------------------
# Comprobaciones sobre el .docx generado
# ---------------------------------------------------------------------------

def revisar_docx(ruta: pathlib.Path, inf: Informe) -> None:
    """Art. 13 A.6: tablas y fórmulas como texto, nunca como imágenes."""
    try:
        from docx import Document
    except ImportError:  # pragma: no cover
        inf.aviso("T10", "falta python-docx: no se pudo revisar el .docx")
        return

    doc = Document(str(ruta))
    xml = doc.element.body.xml

    imagenes_en_tabla = 0
    for tabla in doc.tables:
        if "<w:drawing" in tabla._tbl.xml or "<w:pict" in tabla._tbl.xml:
            imagenes_en_tabla += 1
    if imagenes_en_tabla:
        inf.error("T11", f"{imagenes_en_tabla} tabla(s) contienen imágenes. El art. 13 "
                         "A.6 exige que las tablas estén como texto",
                  archivo=ruta)

    # Una ecuación correcta viaja como OMML (<m:oMath>). Si no hay ninguna y sí
    # hay imágenes sueltas, puede que las fórmulas se hayan rasterizado.
    tiene_omml = "<m:oMath" in xml
    imagenes = xml.count("<w:drawing") + xml.count("<w:pict")
    if imagenes and not tiene_omml:
        inf.aviso("T12", f"el documento tiene {imagenes} imágenes y ninguna ecuación "
                         "en formato de Word. Comprueba que ninguna fórmula esté "
                         "insertada como imagen (art. 13 A.6)",
                  archivo=ruta, imagenes=imagenes)

    if not doc.paragraphs:
        inf.error("T13", "el documento salió vacío", archivo=ruta)


# ---------------------------------------------------------------------------
# Documentos del expediente
# ---------------------------------------------------------------------------

def declaracion_uso_de_ia(raiz: pathlib.Path, autores: list[Autor], datos: dict) -> str:
    """Anexo voluntario, construido desde registro/registro_ia.jsonl."""
    registro = raiz / "registro" / "registro_ia.jsonl"
    acciones: list[dict] = []
    if registro.exists():
        for linea in registro.read_text(encoding="utf8", errors="replace").splitlines():
            linea = linea.strip()
            if not linea:
                continue
            try:
                acciones.append(json.loads(linea))
            except json.JSONDecodeError:
                continue

    por_etapa: dict[str, int] = {}
    for a in acciones:
        etapa = str(a.get("etapa") or a.get("stage") or "sin etapa")
        por_etapa[etapa] = por_etapa.get(etapa, 0) + 1

    lineas = [
        "# Declaración de uso de inteligencia artificial generativa",
        "",
        "> **Esta declaración es voluntaria.** A la fecha de generarla, ninguna norma",
        "> de la UNMSM que se haya podido consultar exige declarar el uso de IA",
        "> generativa en una tesis de pregrado (ver `normativa/requisitos.md`, P-01).",
        "> Se emite por transparencia, apoyándose en el principio de transparencia del",
        "> art. 5 del Código de Ética en Investigación de la UNMSM",
        "> (RR N.° 012648-2023-R), y en que la Directiva de originalidad",
        "> (RR N.° 000947-2026-R, art. 5 q) admite la IA generativa «como apoyo,",
        "> siempre respetando la originalidad».",
        "",
        f"**Tesis:** {datos.get('titulo', '')}",
        "",
        "**Autor(es):** " + "; ".join(a.nombre_para_archivo for a in autores),
        "",
        "## Herramienta utilizada",
        "",
        "Claude Code (Anthropic), a través del repositorio `tesis-sanmarcos`.",
        "",
        "## Alcance de la participación",
        "",
        "La herramienta ejecutó trabajo operativo: exploración y preparación de datos,",
        "búsqueda y síntesis de literatura, análisis, redacción de borradores, formato",
        "y verificación. **Las decisiones de investigación las tomó el autor**, y están",
        "registradas una por una en `decisiones/`, con sus respuestas textuales.",
        "",
        "## Registro de acciones",
        "",
    ]
    if acciones:
        lineas += [f"- Acciones registradas: **{len(acciones)}**", "",
                   "| Etapa | Acciones |", "|---|---|"]
        for etapa, n in sorted(por_etapa.items(), key=lambda kv: -kv[1]):
            lineas.append(f"| {etapa} | {n} |")
    else:
        lineas.append("No hay acciones registradas en `registro/registro_ia.jsonl`.")
    lineas += [
        "",
        "## Lo que no se hizo",
        "",
        "- No se simularon ni completaron datos, resultados ni testimonios.",
        "- No se citó ninguna fuente que no estuviera en la biblioteca Zotero del autor.",
        "- No se empleó ninguna técnica para reducir artificialmente la similitud ni",
        "  para evadir su detección.",
        "",
        f"Generada el {dt.date.today().isoformat()}.",
        "",
        "Firma del autor: ______________________",
    ]
    return "\n".join(lineas)


def declaracion_jurada_pids(autores: list[Autor], datos: dict) -> str:
    """Anexo 4 de la RR N.° 000947-2026-R, con los datos ya puestos."""
    lineas = [
        "# Anexo 4 — Declaración jurada para la evaluación de documentos con la PIDS",
        "",
        "> Formato tomado de la Directiva de originalidad y similitud de trabajos",
        "> académicos, de investigación y producción intelectual de la UNMSM,",
        "> aprobada por RR N.° 000947-2026-R, Anexo 4.",
        "",
    ]
    for a in autores:
        lineas += [
            f"Yo, **{a.nombres} {a.apellidos}**, identificado(a) con DNI "
            f"**{a.dni or '__________'}**, en mi calidad de autor(a) de la Tesis "
            f"titulada «{datos.get('titulo', '')}»,",
            "",
            "**DECLARO BAJO JURAMENTO** que autorizo la evaluación de mi documento a",
            "través de la Plataforma PIDS de la UNMSM, aceptando los resultados que se",
            "consignen en el informe correspondiente, así como las disposiciones,",
            "infracciones y sanciones que pudieran derivarse del análisis efectuado",
            "conforme a la normativa vigente.",
            "",
            "Me ratifico en lo expresado, firmando la presente declaración en señal de",
            "conformidad.",
            "",
            "Lima, ____ de ______________ del 20____",
            "",
            "Firma del autor(a): ______________________",
            f"DNI N.°: {a.dni or '__________'}",
            "",
            "---",
            "",
        ]
    return "\n".join(lineas)


def checklist_expediente(perfil, autores: list[Autor], datos: dict) -> str:
    lineas = [
        "# Checklist del expediente",
        "",
        f"Perfil: `{perfil.id}` — {perfil.get('facultad')}",
        "",
        "## Lo que exige la Directiva de originalidad (art. 17)",
        "",
        "- [ ] **Certificado de Similitud** firmado por el asesor (Anexo 1).",
        "      Vence a los **90 días** de emitido.",
        "- [ ] Último **reporte de similitud** de la PIDS, dentro del rango permitido "
        "(0 % a 20 %).",
        "- [ ] **Historial de análisis** de la PIDS, si hubo varias revisiones.",
        "- [ ] **Anexo 4** firmado por cada autor (se generó en esta carpeta).",
        "- [ ] Comprobantes de pago de S/ 20 por cada revisión **a partir de la "
        "segunda** (art. 27). La primera es gratuita.",
        "",
        "## Archivos de entrega (art. 13)",
        "",
        "- [ ] Carpeta `TEXTO/` con los dos .docx.",
        "- [ ] Carpeta `DOCUMENTO/` nombrada según el tipo de documento.",
        "- [ ] Tablas y fórmulas como texto, no como imágenes.",
        "",
    ]

    if len(autores) > 1:
        lineas += ["## Tesis grupal (RR 00744-R-20, §7.2)", "",
                   f"- [ ] Son {len(autores)} autores (el máximo es tres).",
                   "- [ ] El problema es complejo o multidisciplinario.",
                   "- [ ] Cada participante tiene objetivos definidos:", ""]
        for a in autores:
            lineas.append(f"  - **{a.nombre_para_archivo}**")
            for o in a.objetivos:
                lineas.append(f"    - {o}")
        lineas.append("")

    etica = perfil.get("etica") or {}
    if etica.get("comite_requerido") is True:
        lineas += ["## Ética", "",
                   "- [ ] Aprobación del **Comité de Investigación** de la escuela.",
                   "- [ ] Aprobación de un **Comité de Ética en Investigación**.",
                   "- [ ] Resolución decanal de aprobación del proyecto.", ""]

    vigencia = perfil.get("vigencia_proyecto_meses")
    if isinstance(vigencia, int):
        lineas += ["## Vigencia del proyecto", "",
                   f"- [ ] El proyecto sigue vigente: caduca a los {vigencia} meses de "
                   "aprobado.", ""]

    if not perfil.verificado:
        lineas += ["## Atención", "",
                   f"- [ ] El perfil `{perfil.id}` está en estado `{perfil.estado}`. "
                   "Confirma con tu asesor que la estructura usada es la que tu "
                   "escuela espera.", ""]

    lineas += ["## Voluntario", "",
               "- [ ] Declaración de uso de IA (no exigida por norma; ver el archivo "
               "en esta carpeta).", ""]
    return "\n".join(lineas)


# ---------------------------------------------------------------------------
# Render
# ---------------------------------------------------------------------------

def _quarto() -> str | None:
    return shutil.which("quarto")


def _render(entradas: list[pathlib.Path], destino: pathlib.Path,
            referencia: pathlib.Path, raiz: pathlib.Path) -> tuple[bool, str]:
    quarto = _quarto()
    if quarto is None:
        return False, "no se encontró quarto en el PATH"
    combinado = destino.with_suffix(".qmd")
    partes = []
    for ruta in entradas:
        partes.append(ruta.read_text(encoding="utf8", errors="replace"))
    combinado.write_text("\n\n".join(partes), encoding="utf8")
    cmd = [quarto, "render", str(combinado), "--to", "docx",
           "--reference-doc", str(referencia.resolve()),
           "--output", destino.name]
    try:
        r = subprocess.run(cmd, capture_output=True, text=True, cwd=str(destino.parent),
                           timeout=600)
    except Exception as e:  # noqa: BLE001
        return False, f"falló el render: {e}"
    finally:
        combinado.unlink(missing_ok=True)
    if r.returncode != 0:
        return False, (r.stderr or r.stdout or "").strip()[-400:]
    return destino.exists(), ""


def _clasificar_capitulos(raiz: pathlib.Path) -> tuple[list[pathlib.Path], list[pathlib.Path]]:
    """Separa los .qmd en Desarrollo y Protocolo y Complemento (art. 13 A.2)."""
    claves_complemento = ("caratula", "carátula", "dedicatoria", "agradecimiento",
                          "indice", "índice", "lista", "referencias", "bibliografia",
                          "bibliografía", "anexo")
    desarrollo, complemento = [], []
    for ruta in sorted((raiz / "capitulos").rglob("*.qmd")):
        nombre = ruta.stem.lower()
        (complemento if any(k in nombre for k in claves_complemento) else desarrollo).append(ruta)
    return desarrollo, complemento


def preparar(raiz: pathlib.Path = RAIZ, solo_comprobar: bool = False,
             perfil_id: str | None = None) -> Informe:
    inf = Informe("entrega", "Generación de entregables", raiz=raiz)

    pid = perfil_id or perfil_activo(raiz)
    if not pid:
        inf.error("T00", "no hay perfil activo")
        return inf
    try:
        perfil = cargar_de(raiz, pid)
    except ErrorDePerfil as e:
        inf.error("T00", f"no se pudo cargar el perfil: {e}")
        return inf
    inf.anotar(perfil=pid, estado_del_perfil=perfil.estado)

    ruta_datos = raiz / "entregables" / "datos_de_entrega.yaml"
    if not ruta_datos.exists():
        ruta_datos.parent.mkdir(parents=True, exist_ok=True)
        ruta_datos.write_text(PLANTILLA_DATOS, encoding="utf8")
        inf.error("T07", f"no existía {ruta_datos.relative_to(raiz)}. Se creó una "
                         "plantilla: complétala y vuelve a ejecutar")
        return inf

    datos = cargar_datos(ruta_datos)
    autores = comprobar_datos(datos, inf)
    if inf.hay_errores:
        return inf

    titulo = str(datos["titulo"]).strip()
    anio = int(datos["anio"])
    nombres = {
        "desarrollo": nombre_archivo(autores, "Desarrollo", titulo, anio),
        "complemento": nombre_archivo(autores, "Protocolo y Complemento", titulo, anio),
    }
    inf.anotar(archivo_desarrollo=nombres["desarrollo"],
               archivo_complemento=nombres["complemento"])

    for etiqueta, nombre in nombres.items():
        if len(nombre) > 200:
            inf.aviso("T08", f"el nombre del archivo de {etiqueta} tiene {len(nombre)} "
                             "caracteres; en Windows puede dar problemas al copiarlo a "
                             "rutas largas")

    desarrollo, complemento = _clasificar_capitulos(raiz)
    inf.anotar(qmd_en_desarrollo=len(desarrollo), qmd_en_complemento=len(complemento))
    if not desarrollo:
        inf.error("T09", "no hay capítulos en `capitulos/` para el archivo de Desarrollo")

    # Documentos del expediente: se generan siempre, también en modo comprobación
    dir_documento = raiz / "entregables" / "DOCUMENTO"
    dir_documento.mkdir(parents=True, exist_ok=True)
    (dir_documento / "declaracion_jurada_pids.md").write_text(
        declaracion_jurada_pids(autores, datos), encoding="utf8")
    (dir_documento / "declaracion_uso_de_ia.md").write_text(
        declaracion_uso_de_ia(raiz, autores, datos), encoding="utf8")
    (dir_documento / "checklist_expediente.md").write_text(
        checklist_expediente(perfil, autores, datos), encoding="utf8")
    inf.info("T20", f"documentos del expediente escritos en "
                    f"{dir_documento.relative_to(raiz)}")

    if solo_comprobar or inf.hay_errores:
        return inf

    referencia = raiz / "plantillas" / pid / "referencia.docx"
    if not referencia.exists():
        inf.error("T14", f"falta la plantilla {referencia.relative_to(raiz)}. Genérala "
                         f"con `uv run python -m herramientas.plantilla_docx --perfil {pid}`")
        return inf

    dir_texto = raiz / "entregables" / "TEXTO"
    dir_texto.mkdir(parents=True, exist_ok=True)

    posicion = "inferior_derecha"
    numeracion = (perfil.get("formato") or {}).get("numeracion") or {}
    if "superior" in str(numeracion.get("posicion", "")).lower():
        posicion = "superior_derecha"

    for etiqueta, entradas in (("desarrollo", desarrollo), ("complemento", complemento)):
        if not entradas:
            continue
        destino = dir_texto / nombres[etiqueta]
        ok, motivo = _render(entradas, destino, referencia, raiz)
        if not ok:
            inf.error("T15", f"no se pudo generar el archivo de {etiqueta}: {motivo}")
            continue
        revisar_docx(destino, inf)
        if etiqueta == "complemento":
            try:
                docx_numeracion.aplicar(destino, posicion=posicion)
            except docx_numeracion.SinInicioDeCuerpo:
                inf.info("T16", "el archivo de Protocolo y Complemento no lleva cuerpo, "
                                "así que va entero en numeración romana", archivo=destino)
            except Exception as e:  # noqa: BLE001
                inf.aviso("T17", f"no se pudo aplicar la numeración: {e}", archivo=destino)
        inf.info("T18", f"generado {destino.relative_to(raiz)}")

    return inf


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--comprobar", action="store_true",
                    help="valida los datos y genera el expediente, sin renderizar")
    ap.add_argument("--perfil")
    ap.add_argument("--sin-informe", action="store_true")
    ap.add_argument("--detalle", action="store_true")
    args = ap.parse_args(argv)

    inf = preparar(solo_comprobar=args.comprobar, perfil_id=args.perfil)
    print(inf.volcar(en_disco=not args.sin_informe, mostrar_info=args.detalle))
    return inf.codigo_salida()


if __name__ == "__main__":
    sys.exit(main())
