"""Lectura del registro de acciones de IA que escribe el hook.

El hook (`.claude/hooks/registrar_ia.py`) solo escribe; aquí vive todo lo que
lee. La separación es deliberada: el hook corre en cada llamada de herramienta y
no puede permitirse importar nada pesado, mientras que esto corre cuando alguien
pide un informe.

También se ocupa de la **etapa actual**, que es el único estado compartido entre
las skills y el hook: la skill anota en qué etapa está y el hook etiqueta con eso
cada acción. Así la declaración de uso de IA puede decir qué se hizo en cada
etapa en lugar de dar una lista plana de 400 escrituras.
"""
from __future__ import annotations

import datetime as dt
import json
import pathlib
from collections import Counter

RAIZ = pathlib.Path(__file__).resolve().parent.parent

ETAPAS_VALIDAS = (
    "iniciar", "explorar-datos", "afinar-idea", "literatura", "proyecto",
    "analizar", "redactar", "jurado", "verificar", "entregar", "sustentacion",
)


# -- etapa actual -----------------------------------------------------------

def marcar_etapa(etapa: str, raiz: pathlib.Path = RAIZ) -> pathlib.Path:
    """Anota la etapa en curso para que el hook etiquete lo que venga."""
    if etapa not in ETAPAS_VALIDAS:
        raise ValueError(
            f"etapa desconocida: {etapa!r}. Las válidas son: {', '.join(ETAPAS_VALIDAS)}")
    destino = raiz / "registro" / ".etapa"
    destino.parent.mkdir(parents=True, exist_ok=True)
    destino.write_text(etapa, encoding="utf8")
    return destino


def etapa_actual(raiz: pathlib.Path = RAIZ) -> str:
    marca = raiz / "registro" / ".etapa"
    try:
        return marca.read_text(encoding="utf8").strip() or "sin etapa"
    except OSError:
        return "sin etapa"


# -- lectura del registro ---------------------------------------------------

def ruta(raiz: pathlib.Path = RAIZ) -> pathlib.Path:
    return raiz / "registro" / "registro_ia.jsonl"


def leer(raiz: pathlib.Path = RAIZ) -> list[dict]:
    """Acciones registradas, en orden. Ignora las líneas que no se puedan leer.

    Que una línea esté corrupta no debe impedir leer el resto: el archivo se
    escribe por anexión desde un hook, y una sesión interrumpida puede dejar una
    línea a medias.
    """
    archivo = ruta(raiz)
    if not archivo.exists():
        return []
    acciones: list[dict] = []
    for linea in archivo.read_text(encoding="utf8", errors="replace").splitlines():
        linea = linea.strip()
        if not linea:
            continue
        try:
            dato = json.loads(linea)
        except json.JSONDecodeError:
            continue
        if isinstance(dato, dict):
            acciones.append(dato)
    return acciones


def por_etapa(acciones: list[dict]) -> dict[str, int]:
    cuenta = Counter(str(a.get("etapa") or "sin etapa") for a in acciones)
    orden = {e: i for i, e in enumerate(ETAPAS_VALIDAS)}
    return dict(sorted(cuenta.items(), key=lambda kv: orden.get(kv[0], 99)))


def por_herramienta(acciones: list[dict]) -> dict[str, int]:
    cuenta = Counter(str(a.get("herramienta") or "?") for a in acciones)
    return dict(cuenta.most_common())


def archivos_tocados(acciones: list[dict]) -> list[str]:
    vistos: dict[str, None] = {}
    for a in acciones:
        archivo = str(a.get("archivo") or "").strip()
        if archivo:
            vistos.setdefault(archivo, None)
    return list(vistos)


def resumen(raiz: pathlib.Path = RAIZ) -> dict:
    acciones = leer(raiz)
    momentos = [a.get("momento") for a in acciones if a.get("momento")]
    return {
        "acciones": len(acciones),
        "por_etapa": por_etapa(acciones),
        "por_herramienta": por_herramienta(acciones),
        "archivos_tocados": len(archivos_tocados(acciones)),
        "sesiones": len({a.get("sesion") for a in acciones if a.get("sesion")}),
        "primera": min(momentos) if momentos else None,
        "ultima": max(momentos) if momentos else None,
    }


def esta_al_dia(raiz: pathlib.Path = RAIZ, margen_horas: int = 24) -> tuple[bool, str]:
    """¿El registro refleja el trabajo reciente?

    El hook puede estar sin instalar, o instalado con un intérprete que no
    arranca. En ambos casos falla en silencio —es su diseño, no bloquear—, así
    que alguien tiene que notar el hueco. Esto compara la última acción
    registrada con el archivo modificado más recientemente del proyecto.
    """
    acciones = leer(raiz)
    if not acciones:
        return False, ("no hay ninguna acción registrada. Si ya trabajaste en la "
                       "tesis, el hook no está instalado: corre "
                       "`uv run python -m herramientas.instalar_hooks`")

    ultima = max((a.get("momento") or "") for a in acciones)
    try:
        momento_ultima = dt.datetime.fromisoformat(ultima)
    except ValueError:
        return False, "la última acción registrada no tiene fecha legible"

    mas_reciente = None
    for carpeta in ("capitulos", "codigo", "resultados", "notas"):
        base = raiz / carpeta
        if not base.exists():
            continue
        for archivo in base.rglob("*"):
            if archivo.is_file() and archivo.name != ".gitkeep":
                marca = dt.datetime.fromtimestamp(archivo.stat().st_mtime)
                if mas_reciente is None or marca > mas_reciente:
                    mas_reciente = marca

    if mas_reciente is None:
        return True, "no hay trabajo nuevo que contrastar"

    atraso = mas_reciente - momento_ultima
    if atraso > dt.timedelta(hours=margen_horas):
        return False, (
            f"hay archivos modificados {atraso.days} días después de la última "
            "acción registrada. El hook pudo dejar de funcionar; compruébalo con "
            "`uv run python -m herramientas.instalar_hooks --comprobar`")
    return True, "el registro está al día"
