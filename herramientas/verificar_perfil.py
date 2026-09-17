"""Valida los perfiles contra `perfiles/_esquema.yaml`.

Es la herramienta que sostiene el principio de que el repositorio no inventa
normativa. Bloquea lo que la especificación prohíbe expresamente:

- declarar `verificado` sin el PDF de la norma en disco (R2);
- sustentar un perfil solo en un esquema de facto (R3);
- aplicar una norma de posgrado a un perfil de pregrado (R4);
- dejar un campo normativo sin fuente, sin herencia y sin `[PENDIENTE-NORMATIVA]` (R1).

Uso:
    uv run python -m herramientas.verificar_perfil
    uv run python -m herramientas.verificar_perfil --perfil medicina-fm
"""
from __future__ import annotations

import argparse
import pathlib
import sys
from typing import Any

import yaml

from herramientas.informe import Informe
from herramientas.perfiles import (
    ESTADOS_VALIDOS,
    PENDIENTE,
    ErrorDePerfil,
    cargar_de,
    listar,
)

RAIZ = pathlib.Path(__file__).resolve().parent.parent

#: Campos que, por ser normativos, exigen respaldo explícito.
CAMPOS_NORMATIVOS = (
    "estilo_citas",
    "persona_gramatical",
    "formato",
    "resumen",
    "hipotesis",
    "informe_final",
    "etica",
    "autoria",
    "sustentacion",
)

#: Estados que obligan a pedir confirmación del asesor antes de /proyecto.
ESTADOS_QUE_EXIGEN_ASESOR = {"hereda_general", "verificar", "solo_fuente_secundaria",
                             "plantilla_no_normativa"}


def _tiene_respaldo(perfil, campo: str, valor: Any) -> bool:
    """¿El campo trae fuente, viene heredado, o está marcado como pendiente?"""
    if valor == PENDIENTE:
        return True
    if isinstance(valor, list) and valor and all(v == PENDIENTE for v in valor):
        return True
    if perfil.viene_heredado(campo):
        return True
    if perfil.get(f"{campo}_fuente"):
        return True
    if isinstance(valor, dict):
        if any(k in valor for k in ("fuente", "hereda", "origen")):
            return True
        if any(str(k).endswith("_fuente") or str(k).startswith("fuente")
               for k in valor):
            return True
        # un dict cuyos valores son todos pendientes también está declarado
        if valor and all(v == PENDIENTE for v in valor.values()):
            return True
    return False


def _revisar_crudo(pid: str, inf: Informe, dir_perfiles: pathlib.Path) -> dict[str, Any] | None:
    ruta = dir_perfiles / f"{pid}.yaml"
    try:
        datos = yaml.safe_load(ruta.read_text(encoding="utf8"))
    except yaml.YAMLError as e:
        inf.error("P01", f"YAML inválido: {e}", archivo=ruta)
        return None
    if not isinstance(datos, dict):
        inf.error("P01", "el archivo no contiene un mapa YAML", archivo=ruta)
        return None
    if datos.get("id") != pid:
        inf.error("P02", f"el campo id ({datos.get('id')!r}) no coincide con el "
                         f"nombre del archivo", archivo=ruta)
    for obligatorio in ("facultad", "escuelas", "nivel", "hereda_de", "estado", "fuente"):
        if obligatorio not in datos:
            inf.error("P03", f"falta el campo obligatorio `{obligatorio}`", archivo=ruta)
    return datos


def revisar(pid: str, inf: Informe, raiz: pathlib.Path = RAIZ) -> None:
    dir_perfiles = raiz / "perfiles"
    ruta = dir_perfiles / f"{pid}.yaml"
    crudo = _revisar_crudo(pid, inf, dir_perfiles)
    if crudo is None:
        return

    try:
        # Sin validar: las reglas se comprueban aquí abajo una por una, para
        # poder reportarlas todas con su código en lugar de parar en la primera.
        perfil = cargar_de(raiz, pid, validar=False)
    except ErrorDePerfil as e:
        inf.error("P04", str(e), archivo=ruta)
        return

    estado = perfil.estado
    if estado not in ESTADOS_VALIDOS:
        inf.error("P05", f"estado inválido: {estado!r}", archivo=ruta)

    fuente = perfil.get("fuente") or {}

    # R2 — verificado exige el documento en disco
    if estado == "verificado":
        archivo = fuente.get("archivo_local")
        if not archivo:
            inf.error("P06", "declara `verificado` pero no dice en qué documento "
                             "se apoya (`fuente.archivo_local`)", archivo=ruta)
        elif not (raiz / archivo).exists():
            inf.error("P07", f"declara `verificado` pero falta el documento: {archivo}",
                      archivo=ruta, documento=archivo)
        if not fuente.get("norma") and pid != "unmsm-general":
            inf.aviso("P08", "declara `verificado` sin número de resolución en "
                             "`fuente.norma`; conviene identificarla", archivo=ruta)

    # R3 — el esquema de facto no sustenta nada
    solo_de_facto = (estado == "verificado" and not fuente.get("archivo_local")
                     and perfil.get("esquema_de_facto"))
    if solo_de_facto:
        inf.error("P09", "un esquema de facto no habilita `verificado`", archivo=ruta)

    # R4 — posgrado no sustenta pregrado
    doc = (fuente.get("documento") or "").lower()
    if perfil.get("nivel") == "pregrado" and ("posgrado" in doc or "postgrado" in doc):
        inf.error("P10", "un perfil de pregrado no puede apoyarse en una norma de "
                         "posgrado", archivo=ruta)

    # R1 — todo campo normativo con respaldo
    for campo in CAMPOS_NORMATIVOS:
        if campo not in perfil.datos:
            inf.error("P11", f"el campo normativo `{campo}` no resuelve ni por "
                             f"herencia", archivo=ruta)
            continue
        if not _tiene_respaldo(perfil, campo, perfil.get(campo)):
            inf.aviso("P12", f"`{campo}` no declara fuente, herencia ni "
                             f"`{PENDIENTE}`", archivo=ruta, campo=campo)

    # El esquema de facto declarado debe existir
    ef = perfil.get("esquema_de_facto")
    if ef and not (raiz / ef).exists():
        inf.error("P13", f"`esquema_de_facto` apunta a un archivo inexistente: {ef}",
                  archivo=ruta)

    # Todo perfil debe resolver una estructura utilizable
    modelos = (perfil.get("informe_final") or {}).get("modelos") or {}
    if not modelos:
        inf.error("P14", "no resuelve ningún modelo de informe final: el estudiante "
                         "se quedaría sin estructura", archivo=ruta)

    # Advertencias al estudiante cuando el perfil no está verificado
    if estado in ESTADOS_QUE_EXIGEN_ASESOR:
        advertencias = perfil.get("advertencias_al_estudiante") or []
        if not advertencias:
            inf.aviso("P15", f"estado `{estado}` sin `advertencias_al_estudiante`; "
                             "el estudiante no sabría que necesita confirmar con su "
                             "asesor", archivo=ruta)
        else:
            inf.info("P16", f"estado `{estado}`: requiere confirmación del asesor "
                            "antes de /proyecto", archivo=ruta)

    # El estilo de citas pendiente es normal, pero conviene verlo
    if perfil.get("estilo_citas") == PENDIENTE:
        inf.info("P17", "sin estilo de citas fijado por norma: debe decidirlo el "
                        "asesor y registrarse como decisión", archivo=ruta)


def verificar(perfiles: list[str] | None = None, raiz: pathlib.Path = RAIZ) -> Informe:
    inf = Informe("verificacion_perfiles", "Verificación de perfiles", raiz=raiz)
    ids = perfiles or listar(raiz / "perfiles")
    inf.anotar(perfiles_revisados=len(ids))

    for pid in ids:
        revisar(pid, inf, raiz)

    # Cobertura: toda facultad del índice debe tener perfil
    indice = raiz / "normativa" / "facultades" / "indice.yaml"
    if indice.exists() and perfiles is None:
        datos = yaml.safe_load(indice.read_text(encoding="utf8"))
        del_indice = {f["nombre"] for f in datos.get("facultades", [])}
        con_perfil = set()
        for pid in ids:
            try:
                p = cargar_de(raiz, pid, validar=False)
            except ErrorDePerfil:
                continue
            if p.get("facultad") and p.get("facultad") != "(todas)":
                con_perfil.add(p.get("facultad"))
        faltan = del_indice - con_perfil
        for f in sorted(faltan):
            inf.aviso("P18", f"la facultad «{f}» está en el índice pero no tiene perfil")
        inf.anotar(cobertura=f"{len(con_perfil)} de {len(del_indice)} facultades")

    return inf


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--perfil", action="append", help="id concreto; repetible")
    ap.add_argument("--sin-informe", action="store_true",
                    help="no escribe registro/*.md ni *.json")
    ap.add_argument("--detalle", action="store_true", help="muestra también las notas")
    args = ap.parse_args(argv)

    inf = verificar(args.perfil)
    print(inf.volcar(en_disco=not args.sin_informe, mostrar_info=args.detalle))
    return inf.codigo_salida()


if __name__ == "__main__":
    sys.exit(main())
