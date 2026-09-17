"""Comprueba que las cifras del texto salgan de `resultados/`, no de la memoria.

Es el principio 1 de CLAUDE.md hecho comprobación. Una cifra escrita a mano en un
capítulo de resultados es exactamente el tipo de error que nadie nota hasta que
el jurado pide el dato: puede venir de una versión vieja del análisis, de un
redondeo distinto, o de ninguna parte.

Qué hace:

- En los capítulos de resultados, busca números escritos directamente en la prosa.
- Un número que Quarto calculó (`` `{python} ...` ``, `` `r ...` ``) no es un
  problema: se genera cada vez que se renderiza.
- Un número escrito a mano **que sí aparece en `resultados/`** es un aviso:
  es correcto hoy, pero se desincronizará en cuanto cambie el análisis.
- Un número escrito a mano **que no aparece en ningún archivo de `resultados/`**
  es un error: no hay de dónde salió.
- En investigación cualitativa, comprueba que cada cita de un participante exista
  literalmente en una transcripción de `datos/crudos/`.

Uso:
    uv run python -m herramientas.verificar_cifras
"""
from __future__ import annotations

import argparse
import contextlib
import pathlib
import re
import sys

from herramientas.informe import Informe, iter_qmd
from herramientas.perfiles import ErrorDePerfil, cargar_de, perfil_activo

RAIZ = pathlib.Path(__file__).resolve().parent.parent

BLOQUE_CODIGO = re.compile(r"^(```|~~~)")
#: Expresiones que Quarto evalúa al renderizar.
RE_INLINE = re.compile(r"`(?:\{[a-z]+\}|r|python)\s[^`]*`")
#: Inclusiones de Quarto.
RE_INCLUDE = re.compile(r"\{\{<\s*include\s+([^>]+?)\s*>\}\}")
#: Un número con posible separador de miles y decimales, o porcentaje.
RE_NUMERO = re.compile(r"(?<![\w.,-])(\d{1,3}(?:[ .,]\d{3})+(?:[.,]\d+)?|\d+(?:[.,]\d+)?)"
                       r"\s*(%|por ciento)?")
#: Cita de participante: bloque con un identificador entre paréntesis al final.
RE_PARTICIPANTE = re.compile(r"\(([EPIC]\-?\d{1,3}|[Pp]articipante\s*\d{1,3})\)")

#: Números que no son datos: numeración, años, referencias normativas.
def _es_ruido(valor: str, contexto: str) -> bool:
    limpio = valor.replace(" ", "").replace(",", "").replace(".", "")
    if len(limpio) == 4 and limpio.isdigit() and 1800 <= int(limpio) <= 2100:
        return True                      # año
    if len(limpio) <= 2 and re.search(r"(cap[íi]tulo|secci[óo]n|tabla|figura|"
                                      r"anexo|art[íi]culo|p{1,2}\.|nivel)\s*$",
                                      contexto[-40:], re.I):
        return True                      # numeración de apartados
    # identificador normativo: RR N.° 00744, Ley 29733, DS 016-2024-JUS
    return bool(re.search(r"(RR|RD|N\.?°|Ley|DS)\s*$", contexto[-12:], re.I))


def _sin_codigo(texto: str) -> list[tuple[int, str]]:
    salida: list[tuple[int, str]] = []
    dentro = False
    for i, linea in enumerate(texto.splitlines(), 1):
        if BLOQUE_CODIGO.match(linea.strip()):
            dentro = not dentro
            continue
        if not dentro:
            salida.append((i, linea))
    return salida


def _numeros_de_resultados(raiz: pathlib.Path) -> set[str]:
    """Todos los números que aparecen en `resultados/`, normalizados."""
    numeros: set[str] = set()
    directorio = raiz / "resultados"
    if not directorio.exists():
        return numeros
    for ruta in directorio.rglob("*"):
        if not ruta.is_file() or ruta.name == ".gitkeep":
            continue
        if ruta.suffix.lower() not in {".csv", ".tsv", ".json", ".md", ".txt", ".yaml", ".yml"}:
            continue
        try:
            texto = ruta.read_text(encoding="utf8", errors="replace")
        except OSError:
            continue
        for m in re.finditer(r"-?\d+(?:[.,]\d+)?", texto):
            numeros.add(_normalizar(m.group(0)))
    return numeros


def _normalizar(valor: str) -> str:
    v = valor.strip().replace(" ", "")
    if "," in v and "." in v:
        v = v.replace(".", "") if v.rindex(",") > v.rindex(".") else v.replace(",", "")
    v = v.replace(",", ".")
    try:
        f = float(v)
    except ValueError:
        return v
    return f"{f:g}"


def _capitulos_de_resultados(raiz: pathlib.Path, perfil_id: str | None) -> list[pathlib.Path]:
    """Capítulos donde las cifras importan de verdad."""
    todos = iter_qmd(raiz)
    claves = ["resultado", "analisis", "análisis", "discusion", "discusión", "hallazgo"]
    elegidos = []
    for ruta in todos:
        nombre = ruta.stem.lower()
        if any(k in nombre for k in claves):
            elegidos.append(ruta)
            continue
        try:
            cabeza = ruta.read_text(encoding="utf8", errors="replace")[:2000].lower()
        except OSError:
            continue
        if any(f"# {k}" in cabeza for k in claves):
            elegidos.append(ruta)
    return elegidos or todos


def _transcripciones(raiz: pathlib.Path) -> dict[pathlib.Path, str]:
    textos: dict[pathlib.Path, str] = {}
    base = raiz / "datos" / "crudos"
    if not base.exists():
        return textos
    for ruta in base.rglob("*"):
        if ruta.is_file() and ruta.suffix.lower() in {".txt", ".md", ".vtt", ".srt", ".json"}:
            try:
                textos[ruta] = re.sub(r"\s+", " ", ruta.read_text(encoding="utf8",
                                                                  errors="replace")).lower()
            except OSError:
                continue
    return textos


def verificar(raiz: pathlib.Path = RAIZ, perfil_id: str | None = None) -> Informe:
    inf = Informe("verificacion_cifras", "Verificación de cifras y citas de participantes",
                  raiz=raiz)

    pid = perfil_id or perfil_activo(raiz)
    enfoques: list[str] = []
    if pid:
        with contextlib.suppress(ErrorDePerfil):
            enfoques = cargar_de(raiz, pid).get("enfoques_admitidos") or []
    inf.anotar(perfil=pid or "sin perfil activo")

    capitulos = _capitulos_de_resultados(raiz, pid)
    inf.anotar(capitulos_revisados=len(capitulos))
    if not capitulos:
        inf.info("C00", "no hay capítulos todavía; nada que verificar")
        return inf

    conocidos = _numeros_de_resultados(raiz)
    inf.anotar(numeros_en_resultados=len(conocidos))
    if not conocidos:
        inf.aviso("C01", "`resultados/` no tiene ningún archivo con cifras. "
                         "Mientras no lo tenga, ninguna cifra del texto puede "
                         "rastrearse hasta su origen")

    a_mano = 0
    for ruta in capitulos:
        texto = ruta.read_text(encoding="utf8", errors="replace")
        for num, linea in _sin_codigo(texto):
            limpia = RE_INLINE.sub(" ", linea)
            limpia = RE_INCLUDE.sub(" ", limpia)
            limpia = re.sub(r"\[[^\]]*@[^\]]*\]", " ", limpia)   # citas
            limpia = re.sub(r"^#{1,6}\s.*$", " ", limpia)        # encabezados
            limpia = re.sub(r"https?://\S+", " ", limpia)

            for m in RE_NUMERO.finditer(limpia):
                valor = m.group(1)
                contexto = limpia[:m.start()]
                if _es_ruido(valor, contexto):
                    continue
                a_mano += 1
                normal = _normalizar(valor)
                if normal in conocidos:
                    inf.aviso("C02", f"la cifra {valor} está escrita a mano. Existe en "
                                     "`resultados/`, pero si el análisis cambia el texto "
                                     "quedará desfasado: insértala con una expresión de "
                                     "Quarto",
                              archivo=ruta, linea=num, valor=valor)
                else:
                    inf.error("C03", f"la cifra {valor} está escrita a mano y no aparece "
                                     "en ningún archivo de `resultados/`. No hay de dónde "
                                     "salió",
                              archivo=ruta, linea=num, valor=valor)

    inf.anotar(cifras_escritas_a_mano=a_mano)

    # Citas de participantes en investigación cualitativa
    if "cualitativo" in enfoques or not enfoques:
        transcripciones = _transcripciones(raiz)
        inf.anotar(transcripciones=len(transcripciones))
        revisadas = 0
        for ruta in iter_qmd(raiz):
            texto = ruta.read_text(encoding="utf8", errors="replace")
            for num, linea in _sin_codigo(texto):
                if not RE_PARTICIPANTE.search(linea):
                    continue
                cita = re.sub(r"^\s*>\s?", "", linea)
                cita = RE_PARTICIPANTE.sub("", cita)
                cita = re.sub(r"[«»\"“”]", "", cita).strip()
                if len(cita.split()) < 5:
                    continue
                revisadas += 1
                aguja = re.sub(r"\s+", " ", cita).lower()
                if not transcripciones:
                    inf.error("C04", "hay citas de participantes pero no hay ninguna "
                                     "transcripción en `datos/crudos/` contra la cual "
                                     "comprobarlas",
                              archivo=ruta, linea=num)
                    break
                if not any(aguja[:80] in t for t in transcripciones.values()):
                    inf.error("C05", "esta cita de participante no aparece literalmente "
                                     "en ninguna transcripción de `datos/crudos/`",
                              archivo=ruta, linea=num, fragmento=cita[:120])
        inf.anotar(citas_de_participantes_revisadas=revisadas)

    return inf


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--perfil")
    ap.add_argument("--sin-informe", action="store_true")
    ap.add_argument("--detalle", action="store_true")
    args = ap.parse_args(argv)

    inf = verificar(perfil_id=args.perfil)
    print(inf.volcar(en_disco=not args.sin_informe, mostrar_info=args.detalle))
    return inf.codigo_salida()


if __name__ == "__main__":
    sys.exit(main())
