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
import os
import pathlib
import re
import shutil
import subprocess
import sys
from dataclasses import dataclass, field

import yaml

from herramientas import caratula, docx_numeracion, pdf, registro_ia
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
  orcid: ""                # OBLIGATORIO: RR 06893-R-18, metadata complementaria

facultad: ""
escuela: ""
titulo_profesional: ""     # "Economista", "Licenciado en Educación", …
grupo_de_investigacion: ""
fuente_de_financiamiento: ""
disciplina_ocde: ""
titulo_en_ingles: ""

# Metadata complementaria del depósito en Cybertesis (RR N.° 06893-R-18).
# Va en una hoja después de la carátula.
orcid_autor: ""            # opcional: la directiva dice que no todos lo tienen
ubicacion_geografica: ""   # localidades y/o coordenadas donde se hizo el estudio
anios_de_la_investigacion: ""   # año o rango, p. ej. "2024-2025"
domicilio_para_el_deposito: ""  # lo pide el Anexo 1 de la autorización
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
        if "<w:drawing" not in tabla._tbl.xml and "<w:pict" not in tabla._tbl.xml:
            continue
        # Pandoc emite cada figura con su leyenda dentro de una tabla de una
        # sola celda. Eso es una figura, no una tabla de datos rasterizada, y
        # el art. 13 A.6 habla de lo segundo. Contarlas como infracción
        # bloqueaba la entrega de cualquier tesis que tuviera un gráfico.
        if len(tabla.rows) == 1 and len(tabla.columns) == 1:
            continue
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
    acciones = registro_ia.leer(raiz)
    por_etapa = registro_ia.por_etapa(acciones)
    archivos = registro_ia.archivos_tocados(acciones)
    al_dia, motivo_registro = registro_ia.esta_al_dia(raiz)

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
        lineas += [
            f"- Acciones registradas: **{len(acciones)}**",
            f"- Archivos del repositorio que la herramienta escribió o editó: "
            f"**{len(archivos)}**",
            "",
            "| Etapa | Acciones |", "|---|---|",
        ]
        for etapa, n in por_etapa.items():
            lineas.append(f"| {etapa} | {n} |")
        if not al_dia:
            lineas += [
                "",
                f"> **El registro puede estar incompleto:** {motivo_registro}. Se "
                "declara aquí para no presentar como exhaustivo algo que no lo es.",
            ]
    else:
        lineas += [
            "No hay acciones registradas en `registro/registro_ia.jsonl`.",
            "",
            "> Eso no significa que la herramienta no se haya usado: significa que el",
            "> hook que lleva ese registro no estaba instalado. Se instala con",
            "> `uv run python -m herramientas.instalar_hooks`. Si vas a presentar esta",
            "> declaración, dilo tal cual en lugar de dejar entender que no hubo ayuda.",
        ]
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


def autorizacion_cybertesis(autores: list[Autor], datos: dict) -> str:
    """Anexo 1 de la RR N.° 06893-R-18: autorización para depositar en Cybertesis.

    Es obligatoria ("El documento debidamente firmado por el autor y que da la
    autorización para el depósito y publicación de la tesis en CYBERTESIS es
    obligatorio") y fija la licencia: Creative Commons
    Reconocimiento-NoComercial-CompartirIgual 4.0 Internacional.

    El texto de abajo sigue el del anexo. Lo que el tesista firma es una cesión
    de uso a título gratuito y a nivel mundial, así que conviene que lo lea antes
    de firmarlo y no después.
    """
    lineas = [
        "# Autorización para el depósito y publicación en CYBERTESIS",
        "",
        "> Anexo 1 de la Directiva para el depósito de documentos de Grados y",
        "> Títulos en CYBERTESIS, aprobada por RR N.° 06893-R-18 del 07/11/2018.",
        "",
        f"**Documento:** Tesis titulada «{datos.get('titulo', '')}»",
        f"**Para optar:** {datos.get('titulo_profesional', '__________')}",
        f"**Facultad:** {datos.get('facultad', '__________')}",
        f"**Escuela Profesional:** {datos.get('escuela', '__________')}",
        "",
        "## Declaración",
        "",
        "Por medio del presente documento, afirmo y garantizo ser el legítimo, único",
        "y exclusivo titular de todos los derechos de propiedad intelectual sobre los",
        "documentos arriba mencionados, las obras, los contenidos, los productos y/o",
        "las creaciones en general (en adelante, los «Contenidos») que serán incluidos",
        "en el repositorio institucional CYBERTESIS de la Universidad Nacional Mayor",
        "de San Marcos (en adelante, la «Universidad»).",
        "",
        "También, doy seguridad de que los contenidos entregados se encuentran libres",
        "de toda contraseña, restricción o medida tecnológica de protección, con la",
        "finalidad de permitir que se puedan leer, descargar, reproducir, distribuir,",
        "imprimir, buscar y enlazar los textos completos, sin limitación alguna.",
        "",
        "Autorizo a la Universidad Nacional Mayor de San Marcos a publicar los",
        "Contenidos en los Repositorios Institucionales de la Universidad y, en",
        "consecuencia, en el Repositorio Nacional Digital de Ciencia, Tecnología e",
        "Innovación de Acceso Abierto, sobre la base de lo establecido en la Ley",
        "N.° 30035, sus normas reglamentarias, modificatorias, sustitutorias y",
        "conexas, y de acuerdo con las políticas de acceso abierto que la Universidad",
        "aplique en relación con sus Repositorios Institucionales. Autorizo",
        "expresamente toda consulta y uso de los Contenidos, por parte de cualquier",
        "persona, por el tiempo de duración de los derechos patrimoniales de autor y",
        "derechos conexos, a título gratuito y a nivel mundial.",
        "",
        "Autorizo que los Contenidos sean puestos a disposición del público a través",
        "de la siguiente licencia:",
        "",
        "**Creative Commons Reconocimiento-NoComercial-CompartirIgual 4.0",
        "Internacional** — <https://creativecommons.org/licenses/by-nc-sa/4.0/>",
        "",
        "En señal de conformidad, suscribo el presente documento.",
        "",
    ]
    for a in autores:
        lineas += [
            "Firma: ______________________________________",
            f"Nombre: {a.nombres} {a.apellidos}",
            f"DNI: {a.dni or '__________'}",
            f"Domicilio: {datos.get('domicilio_para_el_deposito') or '__________'}",
            "",
            "Fecha: ______ / ______ / ________",
            "",
            "---",
            "",
        ]
    lineas += [
        "## Si necesitas postergar la publicación",
        "",
        "La directiva admite, a solicitud justificada, postergar la publicación del",
        "documento **hasta un máximo de 2 años** (DS N.° 006-2015-PCM, art. 13), tras",
        "los cuales se publica de inmediato. La solicitud, con su justificación, se",
        "adjunta a esta autorización. Es el Anexo 2 de la misma directiva.",
    ]
    return "\n".join(lineas)


def metadata_complementaria(autores: list[Autor], datos: dict) -> str:
    """La hoja que va después de la carátula, según la RR N.° 06893-R-18.

    Sin esta hoja no se deposita: "No se realizará el depósito del documento
    cuando no cumplan con lo establecido en la presente norma".
    """
    asesor = datos.get("asesor") or {}
    orcid_asesor = asesor.get("orcid") or ""

    filas = [
        ("Código ORCID del autor", datos.get("orcid_autor") or "",
         "opcional según la directiva"),
        ("Código ORCID del asesor", orcid_asesor, "**obligatorio**"),
        ("Grupo de investigación", datos.get("grupo_de_investigacion") or "", ""),
        ("Institución que financia la investigación",
         datos.get("fuente_de_financiamiento") or "",
         "parcial o totalmente; si no hubo, decláralo"),
        ("Ubicación geográfica donde se desarrolló",
         datos.get("ubicacion_geografica") or "",
         "localidades y/o coordenadas geográficas"),
        ("Año o rango de años que abarcó",
         datos.get("anios_de_la_investigacion") or "", ""),
    ]

    lineas = [
        "# Metadata complementaria del documento",
        "",
        "> Hoja exigida por la Directiva para el depósito de documentos de Grados y",
        "> Títulos en CYBERTESIS (RR N.° 06893-R-18). Va **después de la carátula**.",
        "",
        "| Campo | Valor | Nota |",
        "|---|---|---|",
    ]
    for campo, valor, nota in filas:
        lineas.append(f"| {campo} | {valor or '**FALTA**'} | {nota} |")

    faltan = [c for c, v, _ in filas if not v]
    if faltan:
        lineas += [
            "",
            "## Lo que falta completar",
            "",
            "En `entregables/datos_de_entrega.yaml`:",
            "",
        ]
        lineas += [f"- {c}" for c in faltan]
        if not orcid_asesor:
            lineas += [
                "",
                "El **ORCID del asesor es obligatorio** y es el que más veces falta.",
                "Se saca de <https://orcid.org>; si tu asesor no lo tiene, lo crea en",
                "cinco minutos. Sin él, Biblioteca no deposita el documento.",
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
                   f"- [ ] El perfil `{perfil.id}` está en estado `{perfil.estado}`: "
                   "la estructura usada es la general de la universidad (Anexos 2A "
                   "y 2B de la RR N.° 00744-R-20). Si tu escuela pide otra, "
                   "ajústala antes de imprimir.", ""]

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
    # El .qmd combinado se arma EN LA RAÍZ del proyecto, que es desde donde el
    # repositorio ejecuta el código (`execute-dir: project`). Así no hace falta
    # `--execute-dir`, que en Windows mata el kernel de Jupyter cuando apunta a
    # un directorio distinto del del archivo.
    #
    # El precio es que las rutas relativas de los capítulos —sus figuras, que
    # apuntan a `../resultados/…` desde `capitulos/`— dejan de ser válidas. Se
    # reubican una por una. Si no se hiciera, pandoc no encontraría la imagen,
    # la sustituiría por su texto alternativo y NO fallaría: saldría una tesis
    # sin figuras y sin aviso.
    combinado = raiz / f"_entrega_{abs(hash(destino.name)) % 10**8}.qmd"
    partes = [_reubicar_rutas(r.read_text(encoding="utf8", errors="replace"),
                              r.parent, raiz)
              for r in entradas]
    # El archivo combinado no hereda el `_quarto.yml` del proyecto, porque no
    # está en su lista de `render:`. Sin declarar el idioma, las leyendas salen
    # en inglés —«Figure 1», «Table 2»— en una tesis escrita en español.
    cabecera = ["---", "lang: es", f'bibliography: "{_bib(raiz)}"' if _bib(raiz) else "",
                "---", ""]
    texto = "\n".join(ln for ln in cabecera if ln) + "\n\n" + "\n\n".join(partes)
    combinado.write_text(texto, encoding="utf8")

    salida = raiz / destino.name
    cmd = [quarto, "render", combinado.name, "--to", "docx",
           "--reference-doc", str(referencia.resolve()),
           "--output", destino.name]
    try:
        r = _correr_quarto(cmd, raiz)
    except Exception as e:  # noqa: BLE001
        return False, f"falló el render: {e}"
    finally:
        _limpiar_residuos(combinado)

    if r.returncode != 0 or not salida.exists():
        return False, _motivo_util(r.stderr, r.stdout) or "quarto no escribió el .docx"

    destino.parent.mkdir(parents=True, exist_ok=True)
    salida.replace(destino)

    perdidas = [ln.split("Could not fetch resource", 1)[1].split(":")[0].strip()
                for ln in (r.stderr or "").splitlines()
                if "Could not fetch resource" in ln]
    if perdidas:
        return True, "FIGURAS: " + "; ".join(perdidas[:6])
    return True, ""


#: Rutas de recurso en Markdown: `![pie](ruta)`, `[texto](ruta)` y los
#: `{{< include ruta >}}` de Quarto.
RE_RUTA_MD = re.compile(r"(!?\[[^\]]*\]\()([^)\s]+)")
RE_INCLUDE_QMD = re.compile(r"(\{\{<\s*include\s+)([^>\s]+)")


def _reubicar_rutas(texto: str, desde: pathlib.Path, hacia: pathlib.Path) -> str:
    """Reescribe las rutas relativas de un .qmd que cambia de carpeta.

    Solo toca lo que es relativo y apunta a un archivo que existe: una URL, una
    ruta absoluta o un enlace a algo inexistente se dejan como están, porque
    cambiarlos sería adivinar.
    """
    if desde.resolve() == hacia.resolve():
        return texto

    def nueva(ruta: str) -> str:
        if re.match(r"^[a-z]+:", ruta, re.I) or ruta.startswith(("/", "#")):
            return ruta
        destino = (desde / ruta).resolve()
        if not destino.exists():
            return ruta
        try:
            return os.path.relpath(destino, hacia.resolve()).replace("\\", "/")
        except ValueError:          # unidades distintas en Windows
            return ruta

    texto = RE_RUTA_MD.sub(lambda m: m.group(1) + nueva(m.group(2)), texto)
    return RE_INCLUDE_QMD.sub(lambda m: m.group(1) + nueva(m.group(2)), texto)


def _bib(raiz: pathlib.Path) -> str:
    """`referencias.bib`, si existe. Sin él, las citas saldrían sin resolver."""
    return "referencias.bib" if (raiz / "referencias.bib").exists() else ""


def _limpiar_residuos(combinado: pathlib.Path) -> None:
    """Borra el .qmd temporal y lo que Quarto deja a su lado."""
    combinado.unlink(missing_ok=True)
    combinado.with_suffix(".quarto_ipynb").unlink(missing_ok=True)
    adjuntos = combinado.with_name(combinado.stem + "_files")
    if adjuntos.is_dir():
        shutil.rmtree(adjuntos, ignore_errors=True)


def _correr_quarto(cmd: list[str], raiz: pathlib.Path):
    """Corre Quarto y, si el kernel muere, limpia su caché y reintenta una vez.

    «Kernel died before replying to kernel_info» no dice nada del documento:
    es estado viejo en `.quarto/` o en `_freeze/` de un render anterior que se
    interrumpió. Pasa, y dejar al tesista con ese mensaje es abandonarlo.
    """
    r = subprocess.run(cmd, capture_output=True, text=True, cwd=str(raiz),
                       timeout=900)
    if r.returncode == 0:
        return r
    salida = (r.stderr or "") + (r.stdout or "")
    if "Kernel died" not in salida and "kernel_info" not in salida:
        return r

    for cache in (".quarto", "_freeze"):
        shutil.rmtree(raiz / cache, ignore_errors=True)
    return subprocess.run(cmd, capture_output=True, text=True, cwd=str(raiz),
                          timeout=900)


def _motivo_util(stderr: str | None, stdout: str | None) -> str:
    """El mensaje que explica el fallo, no el rastro de pila de Quarto.

    Quarto escribe su stack de JavaScript al final de la salida, así que
    quedarse con los últimos caracteres devolvía siempre lo mismo y nunca la
    causa.
    """
    texto = ((stderr or "") + "\n" + (stdout or "")).strip()
    if not texto:
        return ""
    lineas = [ln for ln in texto.splitlines()
              if ln.strip() and not ln.lstrip().startswith("at ")]
    for i, ln in enumerate(lineas):
        if "ERROR" in ln.upper():
            return " | ".join(lineas[i:i + 6])[:500]
    return " | ".join(lineas[-6:])[:500]


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
    (dir_documento / "autorizacion_cybertesis.md").write_text(
        autorizacion_cybertesis(autores, datos), encoding="utf8")
    (dir_documento / "metadata_complementaria.md").write_text(
        metadata_complementaria(autores, datos), encoding="utf8")
    inf.info("T20", f"documentos del expediente escritos en "
                    f"{dir_documento.relative_to(raiz)}")

    # El ORCID del asesor es obligatorio para el depósito (RR N.° 06893-R-18) y
    # no figura en la información complementaria del Anexo 2A, así que es el que
    # más veces falta: sin él, Biblioteca no deposita el documento.
    if not (datos.get("asesor") or {}).get("orcid"):
        inf.aviso("T21", "falta el ORCID del asesor, que la directiva de depósito "
                         "en Cybertesis (RR N.° 06893-R-18) exige como obligatorio. "
                         "Complétalo en `entregables/datos_de_entrega.yaml`")

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

    generados: list[pathlib.Path] = []
    for etiqueta, entradas in (("desarrollo", desarrollo), ("complemento", complemento)):
        if not entradas:
            continue
        destino = dir_texto / nombres[etiqueta]
        ok, motivo = _render(entradas, destino, referencia, raiz)
        if not ok:
            inf.error("T15", f"no se pudo generar el archivo de {etiqueta}: {motivo}")
            continue
        if motivo.startswith("FIGURAS:"):
            # Pandoc sustituye la imagen que no encuentra por su texto
            # alternativo y sigue. El .docx sale, pero sin figuras.
            inf.error("T19", f"el archivo de {etiqueta} se generó SIN estas figuras, "
                             f"porque no se encontraron: "
                             f"{motivo.removeprefix('FIGURAS:').strip()}. Revisa las "
                             f"rutas en los capítulos")
        revisar_docx(destino, inf)

        # La carátula va en el archivo de Desarrollo, que es el que abre la
        # tesis. Se inserta sobre el .docx YA RENDERIZADO: la plantilla de
        # referencia solo aporta estilos, y copiarla traería su contenido de
        # muestra.
        if etiqueta == "desarrollo":
            try:
                for aviso in caratula.anteponer(destino, datos, perfil, "tesis", raiz):
                    inf.aviso("T27", aviso, archivo=destino)
                inf.info("T22", "carátula con el escudo de la UNMSM insertada",
                         archivo=destino)
            except Exception as e:  # noqa: BLE001
                inf.aviso("T23", f"no se pudo insertar la carátula: {e}. El resto "
                                 f"del documento está bien; la carátula se puede "
                                 f"pegar a mano", archivo=destino)
            for falta in caratula.faltantes(datos, perfil):
                inf.aviso("T24", f"la carátula va incompleta: falta {falta}")

        if etiqueta == "complemento":
            try:
                docx_numeracion.aplicar(destino, posicion=posicion)
            except docx_numeracion.SinInicioDeCuerpo:
                inf.info("T16", "el archivo de Protocolo y Complemento no lleva cuerpo, "
                                "así que va entero en numeración romana", archivo=destino)
            except Exception as e:  # noqa: BLE001
                inf.aviso("T17", f"no se pudo aplicar la numeración: {e}", archivo=destino)
        generados.append(destino)
        inf.info("T18", f"generado {destino.relative_to(raiz)}")

    _convertir_a_pdf(generados, inf, raiz)
    return inf


def _convertir_a_pdf(docxs: list[pathlib.Path], inf: Informe,
                     raiz: pathlib.Path) -> None:
    """El PDF del depósito en Cybertesis, desde el mismo .docx de la entrega.

    Nunca bloquea: el .docx es el entregable que exige el art. 13 y se genera
    igual. El PDF es lo que pide la directiva de depósito (RR N.° 06893-R-18).
    """
    if not docxs:
        return
    hechos, problemas = pdf.convertir_varios(docxs)
    for ruta in hechos:
        inf.info("T25", f"PDF generado: {ruta.relative_to(raiz)}")
    for p in problemas:
        inf.aviso("T26", f"no se generó el PDF. El .docx, que es el entregable "
                         f"del art. 13, está completo. {p}")


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--comprobar", action="store_true",
                    help="valida los datos y genera el expediente, sin renderizar")
    ap.add_argument("--perfil")
    ap.add_argument("--raiz", type=pathlib.Path, default=RAIZ,
                    help="raíz del proyecto; por defecto, este repositorio")
    ap.add_argument("--sin-informe", action="store_true")
    ap.add_argument("--detalle", action="store_true")
    args = ap.parse_args(argv)

    inf = preparar(raiz=args.raiz, solo_comprobar=args.comprobar,
                   perfil_id=args.perfil)
    print(inf.volcar(en_disco=not args.sin_informe, mostrar_info=args.detalle))
    return inf.codigo_salida()


if __name__ == "__main__":
    sys.exit(main())
