"""Verifica las citas de los capítulos contra `referencias.bib` y contra el mundo.

Implementa el principio 2 de CLAUDE.md: solo se citan claves que existen, las
citas textuales llevan página, y nada se da por bueno porque suene bien.

Qué comprueba:

1. Toda clave citada existe en `referencias.bib`.
2. Qué entradas del `.bib` no se citan nunca (aviso, no error).
3. Citas textuales sin número de página.
4. Campos mínimos según el estilo del perfil (APA 7 o Vancouver).
5. El DOI resuelve en Crossref y su título y año coinciden con el `.bib`.
   Sin DOI, se busca en OpenAlex. En perfiles de salud, además en PubMed.
6. Entradas duplicadas y retractaciones, cuando la fuente lo informa.
7. Con `--respaldo`, busca en el PDF un pasaje que se parezca a la cita textual.

Sobre el modo `--respaldo`: **nunca afirma que una cita está respaldada.** Como
mucho dice que encontró un pasaje parecido, que es una pista para el revisor
humano. Lo que sí afirma es lo contrario: cuando no encuentra nada, lo marca
para que alguien lo mire.

Uso:
    uv run python -m herramientas.verificar_referencias
    uv run python -m herramientas.verificar_referencias --sin-red
    uv run python -m herramientas.verificar_referencias --respaldo --biblioteca ~/Zotero/storage
"""
from __future__ import annotations

import argparse
import pathlib
import re
import sys
from dataclasses import dataclass

from herramientas import bibtex
from herramientas.informe import Informe, iter_qmd
from herramientas.perfiles import PENDIENTE, ErrorDePerfil, cargar_de, perfil_activo
from herramientas.red import Cliente, parecido

RAIZ = pathlib.Path(__file__).resolve().parent.parent

CLAVE = r"[A-Za-z0-9_][A-Za-z0-9_:.#$%&+?<>~/-]*"
RE_CITA_CORCHETES = re.compile(r"\[([^\[\]]*@" + CLAVE + r"[^\[\]]*)\]")
RE_CLAVE_EN_CITA = re.compile(r"-?@(" + CLAVE + r")")
RE_CITA_SUELTA = re.compile(r"(?<![\w`\[])@(" + CLAVE + r")")
RE_PAGINA = re.compile(r"\b(p{1,2}\.?|págs?\.?|pág\.|párr\.|cap\.)\s*\d", re.I)

#: Prefijos de referencia cruzada de Quarto. `@fig-dispersion` no es una cita:
#: es un enlace a una figura del propio documento. Buscarlos en el .bib hacía
#: fallar a cualquier tesis que numerara sus figuras o sus tablas.
#: https://quarto.org/docs/authoring/cross-references.html
CRUCES_QUARTO = ("fig-", "tbl-", "eq-", "sec-", "lst-", "thm-", "lem-", "cor-",
                 "prp-", "cnj-", "def-", "exm-", "exr-", "sol-", "rem-")

#: Expresiones que Quarto evalúa al renderizar.
RE_INLINE = re.compile(r"`(?:\{[a-z]+\}|r|python)\s[^`]*`")

#: Comillas que en español marcan cita textual.
RE_ENTRECOMILLADO = re.compile(r"[«\"“]([^«»\"“”]{25,})[»\"”]")

#: Palabras a partir de las cuales una cita en bloque se considera textual larga.
PALABRAS_CITA_LARGA = 40

#: Tolerancia al comparar títulos con la fuente externa.
UMBRAL_TITULO = 0.82

PERFILES_DE_SALUD = {"medicina-fm", "farmacia-fb", "odontologia-fo",
                     "veterinaria-fmv", "psicologia-fpsi"}

BLOQUE_CODIGO = re.compile(r"^(```|~~~)")


@dataclass
class Cita:
    clave: str
    archivo: pathlib.Path
    linea: int
    texto_cita: str
    parrafo: str
    tiene_pagina: bool
    en_bloque_de_cita: bool


def _lineas_utiles(texto: str) -> list[tuple[int, str]]:
    """Numera las líneas y descarta el interior de los bloques de código."""
    salida: list[tuple[int, str]] = []
    dentro = False
    for i, linea in enumerate(texto.splitlines(), 1):
        if BLOQUE_CODIGO.match(linea.strip()):
            dentro = not dentro
            continue
        if not dentro:
            salida.append((i, linea))
    return salida


def _parrafos(lineas: list[tuple[int, str]]) -> list[tuple[int, str, bool]]:
    """Agrupa en párrafos. Devuelve (línea_inicial, texto, es_cita_en_bloque)."""
    parrafos: list[tuple[int, str, bool]] = []
    actual: list[str] = []
    inicio = 0
    bloque = False
    for num, linea in lineas:
        if linea.strip():
            if not actual:
                inicio = num
                bloque = linea.lstrip().startswith(">")
            actual.append(linea)
        elif actual:
            parrafos.append((inicio, "\n".join(actual), bloque))
            actual, bloque = [], False
    if actual:
        parrafos.append((inicio, "\n".join(actual), bloque))
    return parrafos


def es_referencia_cruzada(clave: str) -> bool:
    """¿La clave es una referencia cruzada de Quarto y no una cita?"""
    return clave.startswith(CRUCES_QUARTO)


def extraer_citas(ruta: pathlib.Path) -> list[Cita]:
    """Encuentra todas las citas de un .qmd, con su contexto."""
    texto = ruta.read_text(encoding="utf8", errors="replace")
    # el front-matter YAML no lleva citas
    if texto.startswith("---"):
        fin = texto.find("\n---", 3)
        if fin > 0:
            cabecera = texto[:fin].count("\n") + 1
            texto = "\n" * cabecera + texto[fin + 4:]

    citas: list[Cita] = []
    for inicio, parrafo, bloque in _parrafos(_lineas_utiles(texto)):
        vistas: set[tuple[str, str]] = set()

        for m in RE_CITA_CORCHETES.finditer(parrafo):
            interior = m.group(1)
            pagina = bool(RE_PAGINA.search(interior))
            for mk in RE_CLAVE_EN_CITA.finditer(interior):
                clave = mk.group(1).rstrip(".,;:")
                if es_referencia_cruzada(clave):
                    continue
                desplazamiento = parrafo.count("\n", 0, m.start())
                citas.append(Cita(clave, ruta, inicio + desplazamiento,
                                  m.group(0), parrafo, pagina, bloque))
                vistas.add((clave, m.group(0)))

        sin_corchetes = RE_CITA_CORCHETES.sub(" ", parrafo)
        for m in RE_CITA_SUELTA.finditer(sin_corchetes):
            clave = m.group(1).rstrip(".,;:")
            if es_referencia_cruzada(clave) or any(clave == c for c, _ in vistas):
                continue
            desplazamiento = sin_corchetes.count("\n", 0, m.start())
            citas.append(Cita(clave, ruta, inicio + desplazamiento,
                              m.group(0), parrafo, False, bloque))
    return citas


def _texto_entrecomillado(parrafo: str) -> str | None:
    """El pasaje entrecomillado del párrafo, si hay uno.

    Las expresiones de Quarto se quitan primero. Un `` `{python} f"{x:.2f}"` ``
    lleva comillas dentro, y sin descontarlo cualquier párrafo con una cifra
    insertada parecía contener una cita textual y se le exigía página.
    """
    m = RE_ENTRECOMILLADO.search(RE_INLINE.sub(" ", parrafo))
    return m.group(1).strip() if m else None


def _es_cita_textual(cita: Cita) -> tuple[bool, str | None]:
    """¿La cita acompaña a una transcripción literal? Devuelve (sí/no, el texto)."""
    entrecomillado = _texto_entrecomillado(cita.parrafo)
    if entrecomillado:
        return True, entrecomillado
    if cita.en_bloque_de_cita:
        limpio = re.sub(r"^\s*>\s?", "", cita.parrafo, flags=re.M)
        limpio = RE_CITA_CORCHETES.sub("", limpio).strip()
        if len(limpio.split()) >= PALABRAS_CITA_LARGA:
            return True, limpio
    return False, None


def _estilo_del_perfil(raiz: pathlib.Path, pid: str | None) -> tuple[str, str | None]:
    if not pid:
        return "apa7", None
    try:
        perfil = cargar_de(raiz, pid)
    except ErrorDePerfil:
        return "apa7", pid
    estilo = perfil.get("estilo_citas")
    if not estilo or estilo == PENDIENTE:
        return "apa7", pid
    return estilo, pid


def _pdf_de(entrada: bibtex.Entrada, biblioteca: pathlib.Path | None) -> pathlib.Path | None:
    campo = entrada.get("file")
    if campo:
        for trozo in re.split(r"[;:]", campo):
            trozo = trozo.strip()
            if trozo.lower().endswith(".pdf"):
                p = pathlib.Path(trozo)
                if p.exists():
                    return p
    if biblioteca and biblioteca.exists():
        for p in biblioteca.rglob("*.pdf"):
            if entrada.clave.lower() in p.stem.lower():
                return p
    return None


def _buscar_en_pdf(ruta: pathlib.Path, fragmento: str) -> float:
    """Mejor parecido entre el fragmento y alguna ventana del PDF."""
    try:
        from pypdf import PdfReader
        lector = PdfReader(str(ruta))
    except Exception:  # noqa: BLE001
        return -1.0
    objetivo = re.sub(r"\s+", " ", fragmento).strip().lower()
    if len(objetivo) < 20:
        return -1.0
    mejor = 0.0
    for pagina in lector.pages[:400]:
        try:
            texto = (pagina.extract_text() or "")
        except Exception:  # noqa: BLE001
            continue
        texto = re.sub(r"\s+", " ", texto).lower()
        if not texto:
            continue
        if objetivo[:60] in texto:
            return 1.0
        paso = max(len(objetivo), 80)
        for i in range(0, max(len(texto) - paso, 1), paso // 2):
            mejor = max(mejor, parecido(objetivo, texto[i:i + paso * 2]))
            if mejor >= 0.95:
                return mejor
    return mejor


def verificar(raiz: pathlib.Path = RAIZ, sin_red: bool = False,
              respaldo: bool = False, biblioteca: pathlib.Path | None = None,
              perfil_id: str | None = None) -> Informe:
    inf = Informe("verificacion_referencias", "Verificación de referencias", raiz=raiz)

    pid = perfil_id or perfil_activo(raiz)
    estilo, pid_usado = _estilo_del_perfil(raiz, pid)
    inf.anotar(perfil=pid_usado or "sin perfil activo", estilo_de_citas=estilo)

    bib_ruta = raiz / "referencias.bib"
    entradas = bibtex.cargar(bib_ruta)
    indice = bibtex.indexar(entradas)
    inf.anotar(**bibtex.resumen(entradas))

    archivos = iter_qmd(raiz)
    inf.anotar(capitulos_revisados=len(archivos))

    if not archivos:
        inf.info("R00", "no hay capítulos en `capitulos/` todavía; nada que verificar")
        return inf

    if not entradas:
        inf.error("R01", "`referencias.bib` está vacío o no existe: ninguna cita "
                         "puede verificarse. Configúralo con "
                         "`uv run python -m herramientas.zotero --instrucciones`",
                  archivo=bib_ruta)

    citas: list[Cita] = []
    for ruta in archivos:
        citas.extend(extraer_citas(ruta))
    inf.anotar(citas_encontradas=len(citas))

    # 1 y 3 — existencia y página en citas textuales
    claves_citadas: set[str] = set()
    for cita in citas:
        claves_citadas.add(cita.clave)
        if cita.clave not in indice:
            inf.error("R02", f"se cita `@{cita.clave}` y esa clave no existe en "
                             "referencias.bib. No la inventes: agrégala en Zotero",
                      archivo=cita.archivo, linea=cita.linea, clave=cita.clave)
            continue
        textual, fragmento = _es_cita_textual(cita)
        if textual and not cita.tiene_pagina:
            inf.error("R03", f"cita textual de `@{cita.clave}` sin número de página",
                      archivo=cita.archivo, linea=cita.linea, clave=cita.clave,
                      fragmento=(fragmento or "")[:120])

    # 2 — entradas nunca citadas
    for e in entradas:
        if e.clave not in claves_citadas:
            inf.aviso("R04", f"`{e.clave}` está en referencias.bib pero no se cita "
                             "en ningún capítulo", archivo=bib_ruta, linea=e.linea)

    # 4 — campos mínimos del estilo
    for clave in sorted(claves_citadas & set(indice)):
        faltan = indice[clave].campos_faltantes(estilo)
        if faltan:
            inf.error("R05", f"`{clave}` no tiene los campos que {estilo} exige para "
                             f"un `{indice[clave].tipo}`: falta {', '.join(faltan)}",
                      archivo=bib_ruta, linea=indice[clave].linea, clave=clave)

    # 6a — claves y obras duplicadas
    for clave, veces in bibtex.claves_repetidas(entradas).items():
        inf.error("R06", f"la clave `{clave}` aparece {veces} veces en referencias.bib",
                  archivo=bib_ruta)
    for firma, grupo in bibtex.duplicados(entradas).items():
        claves = ", ".join(e.clave for e in grupo)
        inf.aviso("R07", f"parecen la misma obra con claves distintas: {claves}",
                  archivo=bib_ruta, firma=firma)

    # 5 y 6b — contraste con fuentes externas
    cliente = Cliente(sin_red=sin_red)
    es_salud = (pid_usado or "") in PERFILES_DE_SALUD
    sin_comprobar = 0

    for clave in sorted(claves_citadas & set(indice)):
        e = indice[clave]
        r = cliente.crossref(e.doi) if e.doi else cliente.openalex(e.titulo_limpio, e.anio)

        if r.sin_comprobar:
            sin_comprobar += 1
            nivel = inf.info if sin_red else inf.aviso
            nivel("R08", f"no se pudo comprobar `{clave}` contra una fuente externa "
                         f"({r.motivo}). No significa que la cita esté mal",
                  archivo=bib_ruta, clave=clave)
            continue

        datos = r.datos or {}
        externo_titulo = datos.get("titulo", "")
        if externo_titulo and e.titulo_limpio:
            sem = parecido(e.titulo_limpio, externo_titulo)
            if sem < UMBRAL_TITULO:
                inf.error("R09", f"`{clave}`: el título del .bib no coincide con el de "
                                 f"{datos.get('fuente')} (parecido {sem:.2f}). "
                                 f"En el .bib: «{e.titulo_limpio[:70]}»; "
                                 f"en la fuente: «{externo_titulo[:70]}»",
                          archivo=bib_ruta, linea=e.linea, clave=clave)

        externo_anio = str(datos.get("anio") or "")
        if externo_anio and e.anio and externo_anio != e.anio:
            inf.aviso("R10", f"`{clave}`: el año del .bib ({e.anio}) no coincide con "
                             f"el de {datos.get('fuente')} ({externo_anio})",
                      archivo=bib_ruta, linea=e.linea, clave=clave)

        if datos.get("retirado"):
            inf.error("R11", f"`{clave}` figura como RETRACTADA en "
                             f"{datos.get('fuente')}. No debe citarse como evidencia",
                      archivo=bib_ruta, linea=e.linea, clave=clave)

        if es_salud and not e.get("pmid"):
            rp = cliente.pubmed(e.titulo_limpio)
            if rp.ok and rp.datos:
                if rp.datos.get("retirado"):
                    inf.error("R12", f"`{clave}`: PubMed la marca como retractada",
                              archivo=bib_ruta, clave=clave)
                else:
                    inf.info("R13", f"`{clave}`: PMID {rp.datos.get('pmid')} "
                                    "(conviene guardarlo en Zotero)",
                             archivo=bib_ruta, clave=clave)

    inf.anotar(**cliente.estadisticas())
    if sin_comprobar:
        inf.anotar(sin_comprobar=sin_comprobar)

    # 7 — respaldo en el PDF
    if respaldo:
        revisadas = 0
        for cita in citas:
            if cita.clave not in indice:
                continue
            textual, fragmento = _es_cita_textual(cita)
            if not textual or not fragmento:
                continue
            revisadas += 1
            pdf = _pdf_de(indice[cita.clave], biblioteca)
            if pdf is None:
                inf.aviso("R14", f"no hay PDF para `{cita.clave}`: no se pudo buscar "
                                 "respaldo de la cita textual",
                          archivo=cita.archivo, linea=cita.linea, clave=cita.clave)
                continue
            puntaje = _buscar_en_pdf(pdf, fragmento)
            if puntaje < 0:
                inf.aviso("R15", f"el PDF de `{cita.clave}` no se pudo leer "
                                 "(¿escaneado sin capa de texto?)",
                          archivo=cita.archivo, linea=cita.linea, clave=cita.clave)
            elif puntaje < 0.75:
                inf.aviso("R16", f"sin respaldo encontrado para la cita textual de "
                                 f"`{cita.clave}` en su PDF. Revísalo a mano",
                          archivo=cita.archivo, linea=cita.linea, clave=cita.clave,
                          parecido=round(puntaje, 2))
            else:
                inf.info("R17", f"`{cita.clave}`: se encontró un pasaje parecido "
                                f"(parecido {puntaje:.2f}). Es una pista, no una "
                                "confirmación: compruébalo tú",
                         archivo=cita.archivo, linea=cita.linea, clave=cita.clave)
        inf.anotar(citas_textuales_revisadas=revisadas)

    return inf


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--sin-red", action="store_true",
                    help="no consulta Crossref, OpenAlex ni PubMed")
    ap.add_argument("--respaldo", action="store_true",
                    help="busca en los PDF pasajes que respalden las citas textuales")
    ap.add_argument("--biblioteca", type=pathlib.Path,
                    help="carpeta con los PDF (p. ej. la carpeta storage de Zotero)")
    ap.add_argument("--perfil", help="fuerza un perfil en lugar del activo")
    ap.add_argument("--sin-informe", action="store_true")
    ap.add_argument("--detalle", action="store_true")
    args = ap.parse_args(argv)

    inf = verificar(sin_red=args.sin_red, respaldo=args.respaldo,
                    biblioteca=args.biblioteca, perfil_id=args.perfil)
    print(inf.volcar(en_disco=not args.sin_informe, mostrar_info=args.detalle))
    return inf.codigo_salida()


if __name__ == "__main__":
    sys.exit(main())
