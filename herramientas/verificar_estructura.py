"""Compara los capítulos con la estructura que exige el perfil activo.

La regla que gobierna esta herramienta: **solo se exige lo que el perfil marca
como obligatorio**. Es fácil escribir un verificador que reclame matriz de
consistencia a todo el mundo; sería cómodo y estaría mal. La guía de Economía,
por ejemplo, no pide matriz de consistencia ni cronograma, y exigírselos a un
estudiante de la FCE sería inventar normativa.

Qué comprueba:

1. Que estén todas las secciones que el perfil declara, con sus denominaciones.
2. Que vayan en el orden del perfil.
3. Que las secciones ausentes tengan justificación registrada, cuando el perfil
   permite excluir ítems con justificación.
4. Que no haya capítulos que no correspondan a ninguna sección del perfil.

Uso:
    uv run python -m herramientas.verificar_estructura
    uv run python -m herramientas.verificar_estructura --enfoque cualitativo
"""
from __future__ import annotations

import argparse
import json
import pathlib
import re
import sys
import unicodedata
from dataclasses import dataclass

from herramientas.informe import Informe, iter_qmd
from herramientas.perfiles import ErrorDePerfil, Perfil, cargar_de, perfil_activo
from herramientas.red import parecido

RAIZ = pathlib.Path(__file__).resolve().parent.parent

BLOQUE_CODIGO = re.compile(r"^(```|~~~)")
RE_ENCABEZADO = re.compile(r"^(#{1,6})\s+(.*?)\s*(?:\{[^}]*\})?\s*$")

#: A partir de aquí se considera que dos denominaciones son la misma sección.
UMBRAL_COINCIDENCIA = 0.80

#: Ruido a quitar antes de comparar títulos.
RE_ORDINAL = re.compile(
    r"^\s*(cap[ií]tulo|cap\.?|parte)?\s*"
    r"([ivxlcdm]{1,6}|\d{1,2})?\s*[\.\:\-–)]*\s*", re.I)


@dataclass
class Encabezado:
    texto: str
    nivel: int
    archivo: pathlib.Path
    linea: int


def _normalizar(texto: str) -> str:
    t = unicodedata.normalize("NFKD", texto)
    t = "".join(c for c in t if not unicodedata.combining(c))
    t = RE_ORDINAL.sub("", t)
    t = re.sub(r"[^a-z0-9 ]+", " ", t.lower())
    return re.sub(r"\s+", " ", t).strip()


def leer_encabezados(raiz: pathlib.Path) -> list[Encabezado]:
    salida: list[Encabezado] = []
    for ruta in iter_qmd(raiz):
        texto = ruta.read_text(encoding="utf8", errors="replace")
        if texto.startswith("---"):
            fin = texto.find("\n---", 3)
            if fin > 0:
                saltos = texto[:fin].count("\n") + 1
                texto = "\n" * saltos + texto[fin + 4:]
        dentro = False
        for i, linea in enumerate(texto.splitlines(), 1):
            if BLOQUE_CODIGO.match(linea.strip()):
                dentro = not dentro
                continue
            if dentro:
                continue
            m = RE_ENCABEZADO.match(linea)
            if m:
                salida.append(Encabezado(m.group(2).strip(), len(m.group(1)), ruta, i))
    return salida


def secciones_esperadas(perfil: Perfil, enfoque: str) -> list[dict]:
    """Secciones de primer nivel del modelo de informe final del perfil."""
    modelos = (perfil.get("informe_final") or {}).get("modelos") or {}
    if enfoque not in modelos:
        disponibles = sorted(modelos)
        enfoque = disponibles[0] if disponibles else ""
    modelo = modelos.get(enfoque) or {}
    crudas = modelo.get("secciones") or []

    esperadas: list[dict] = []
    for s in crudas:
        if isinstance(s, dict):
            titulo = s.get("titulo") or s.get("parte") or ""
            if not titulo:
                continue
            esperadas.append({
                "titulo": str(titulo),
                "numero": s.get("numero"),
                "opcional": bool(s.get("opcional") or s.get("obligatorio") is False),
                "nota": s.get("nota") or s.get("contenido"),
            })
        elif isinstance(s, str):
            esperadas.append({"titulo": s, "numero": None, "opcional": False, "nota": None})
    return esperadas


def _justificaciones_registradas(raiz: pathlib.Path) -> str:
    """Texto de todas las decisiones, para buscar justificaciones de exclusión."""
    trozos: list[str] = []
    for ruta in sorted((raiz / "decisiones").glob("*.json")):
        try:
            datos = json.loads(ruta.read_text(encoding="utf8"))
        except (json.JSONDecodeError, OSError):
            continue
        trozos.append(json.dumps(datos, ensure_ascii=False))
    return _normalizar(" ".join(trozos))


def verificar(raiz: pathlib.Path = RAIZ, perfil_id: str | None = None,
              enfoque: str | None = None) -> Informe:
    inf = Informe("verificacion_estructura", "Verificación de estructura", raiz=raiz)

    pid = perfil_id or perfil_activo(raiz)
    if not pid:
        inf.error("E00", "no hay perfil activo. Actívalo con "
                         "`uv run python -m herramientas.activar_perfil <id>`")
        return inf
    try:
        perfil = cargar_de(raiz, pid)
    except ErrorDePerfil as e:
        inf.error("E01", f"no se pudo cargar el perfil: {e}")
        return inf

    enfoques = perfil.get("enfoques_admitidos") or ["cuantitativo"]
    enfoque = enfoque or (enfoques[0] if enfoques else "cuantitativo")
    inf.anotar(perfil=pid, estado_del_perfil=perfil.estado, enfoque=enfoque)

    if not perfil.verificado:
        inf.info("E02", f"el perfil está en estado `{perfil.estado}`: la estructura "
                        "que se exige aquí proviene de la norma general heredada. "
                        "Confírmala con tu asesor")

    esperadas = secciones_esperadas(perfil, enfoque)
    if not esperadas:
        inf.error("E03", f"el perfil no declara secciones para el enfoque `{enfoque}`")
        return inf
    inf.anotar(secciones_esperadas=len(esperadas))

    encabezados = leer_encabezados(raiz)
    if not encabezados:
        inf.info("E04", "no hay capítulos en `capitulos/` todavía; nada que comparar")
        return inf
    de_primer_nivel = [e for e in encabezados if e.nivel == 1]
    inf.anotar(encabezados_de_primer_nivel=len(de_primer_nivel))

    # Emparejar cada sección esperada con el encabezado que más se le parece
    usados: set[int] = set()
    posiciones: list[tuple[dict, int | None]] = []
    for sec in esperadas:
        objetivo = _normalizar(sec["titulo"])
        mejor_i, mejor_v = None, 0.0
        for i, enc in enumerate(de_primer_nivel):
            if i in usados:
                continue
            v = parecido(objetivo, _normalizar(enc.texto))
            if v > mejor_v:
                mejor_i, mejor_v = i, v
        if mejor_i is not None and mejor_v >= UMBRAL_COINCIDENCIA:
            usados.add(mejor_i)
            posiciones.append((sec, mejor_i))
            enc = de_primer_nivel[mejor_i]
            if _normalizar(enc.texto) != _normalizar(sec["titulo"]):
                inf.aviso("E05", f"«{enc.texto}» se corresponde con la sección "
                                 f"«{sec['titulo']}» del perfil, pero no usa su "
                                 "denominación exacta",
                          archivo=enc.archivo, linea=enc.linea,
                          esperado=sec["titulo"], encontrado=enc.texto)
        else:
            posiciones.append((sec, None))

    justificaciones = _justificaciones_registradas(raiz)
    permite_excluir = bool((perfil.get("proyecto") or {}).get("items_excluibles_con_justificacion"))

    # Secciones ausentes
    for sec, pos in posiciones:
        if pos is not None:
            continue
        if sec["opcional"]:
            inf.info("E06", f"la sección opcional «{sec['titulo']}» no está presente",
                     seccion=sec["titulo"])
            continue
        objetivo = _normalizar(sec["titulo"])
        justificada = objetivo and objetivo[:30] in justificaciones
        if justificada and permite_excluir:
            inf.aviso("E07", f"falta la sección «{sec['titulo']}», pero hay una "
                             "justificación registrada en `decisiones/`. El perfil "
                             "permite excluir ítems con justificación",
                      seccion=sec["titulo"])
        elif permite_excluir:
            inf.error("E08", f"falta la sección «{sec['titulo']}». El perfil permite "
                             "excluirla, pero solo con justificación registrada, y no "
                             "hay ninguna en `decisiones/`",
                      seccion=sec["titulo"])
        else:
            inf.error("E09", f"falta la sección «{sec['titulo']}» que exige el perfil",
                      seccion=sec["titulo"])

    # Orden
    encontradas = [(sec, pos) for sec, pos in posiciones if pos is not None]
    for anterior, siguiente in zip(encontradas, encontradas[1:], strict=False):
        if anterior[1] > siguiente[1]:
            enc = de_primer_nivel[siguiente[1]]
            inf.error("E10", f"«{siguiente[0]['titulo']}» aparece antes que "
                             f"«{anterior[0]['titulo']}»; el perfil las ordena al revés",
                      archivo=enc.archivo, linea=enc.linea)

    # Encabezados que no corresponden a ninguna sección del perfil
    preliminares = {_normalizar(p.get("parte", "")) for p in (perfil.get("preliminares") or [])
                    if isinstance(p, dict)}
    preliminares |= {"resumen", "abstract", "indice", "introduccion",
                     "referencias", "referencias bibliograficas", "bibliografia",
                     "anexos", "dedicatoria", "agradecimiento", "agradecimientos"}
    for i, enc in enumerate(de_primer_nivel):
        if i in usados:
            continue
        if _normalizar(enc.texto) in preliminares:
            continue
        inf.aviso("E11", f"«{enc.texto}» no corresponde a ninguna sección del perfil. "
                         "Si es intencional, regístralo como decisión",
                  archivo=enc.archivo, linea=enc.linea)

    inf.anotar(secciones_encontradas=len(encontradas))
    return inf


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--perfil")
    ap.add_argument("--enfoque", help="cuantitativo, cualitativo, …")
    ap.add_argument("--sin-informe", action="store_true")
    ap.add_argument("--detalle", action="store_true")
    args = ap.parse_args(argv)

    inf = verificar(perfil_id=args.perfil, enfoque=args.enfoque)
    print(inf.volcar(en_disco=not args.sin_informe, mostrar_info=args.detalle))
    return inf.codigo_salida()


if __name__ == "__main__":
    sys.exit(main())
