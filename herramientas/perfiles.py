"""Carga de perfiles con resolución de herencia.

Un perfil de facultad hereda de `unmsm-general`. Este módulo devuelve el perfil
ya resuelto, dejando constancia de qué valor vino heredado y de cuál es su
fuente, para que ninguna herramienta tenga que adivinarlo.

Reglas implementadas (ver perfiles/_esquema.yaml):
  R1  todo campo normativo tiene fuente, hereda, o vale "[PENDIENTE-NORMATIVA]"
  R2  `estado: verificado` exige que el archivo de la fuente exista en disco
  R4  una norma de posgrado no sustenta un perfil de pregrado
  R6  `hereda_de` debe resolver y no formar ciclos
"""
from __future__ import annotations

import pathlib
from dataclasses import dataclass, field
from typing import Any

import yaml

PENDIENTE = "[PENDIENTE-NORMATIVA]"

RAIZ = pathlib.Path(__file__).resolve().parent.parent
DIR_PERFILES = RAIZ / "perfiles"

ESTADOS_VALIDOS = {
    "verificado",
    "hereda_general",
    "verificar",
    "solo_fuente_secundaria",
    "plantilla_no_normativa",
}

#: Campos que, si faltan, se toman del perfil padre.
CAMPOS_HEREDABLES = (
    "enfoques_admitidos",
    "estilo_citas",
    "csl",
    "persona_gramatical",
    "formato",
    "extension_paginas",
    "resumen",
    "hipotesis",
    "preliminares",
    "informacion_complementaria",
    "proyecto",
    "informe_final",
    "cierre",
    "etica",
    "autoria",
    "vigencia_proyecto_meses",
    "sustentacion",
    "entrega",
)


class ErrorDePerfil(Exception):
    """El perfil no cumple las reglas de perfiles/_esquema.yaml."""


@dataclass
class Perfil:
    """Perfil con la herencia ya resuelta."""

    id: str
    datos: dict[str, Any]
    heredados: dict[str, str] = field(default_factory=dict)
    cadena: list[str] = field(default_factory=list)

    def __getitem__(self, clave: str) -> Any:
        return self.datos[clave]

    def get(self, clave: str, defecto: Any = None) -> Any:
        return self.datos.get(clave, defecto)

    @property
    def estado(self) -> str:
        return self.datos.get("estado", "")

    @property
    def verificado(self) -> bool:
        return self.estado == "verificado"

    def viene_heredado(self, clave: str) -> str | None:
        """Devuelve el id del perfil del que se heredó `clave`, o None."""
        return self.heredados.get(clave)

    def pendiente(self, clave: str) -> bool:
        return _es_pendiente(self.datos.get(clave))

    def modelo(self, enfoque: str) -> dict[str, Any]:
        """Devuelve el modelo de informe final para un enfoque dado."""
        modelos = (self.datos.get("informe_final") or {}).get("modelos") or {}
        if enfoque not in modelos:
            disponibles = ", ".join(sorted(modelos)) or "ninguno"
            raise ErrorDePerfil(
                f"{self.id}: no hay modelo de informe final para el enfoque "
                f"'{enfoque}'. Disponibles: {disponibles}."
            )
        return modelos[enfoque]


def _es_pendiente(valor: Any) -> bool:
    if valor == PENDIENTE:
        return True
    if isinstance(valor, list):
        return bool(valor) and all(v == PENDIENTE for v in valor)
    if isinstance(valor, dict):
        return bool(valor) and all(_es_pendiente(v) for v in valor.values())
    return False


def _leer(pid: str, dir_perfiles: pathlib.Path) -> dict[str, Any]:
    ruta = dir_perfiles / f"{pid}.yaml"
    if not ruta.exists():
        raise ErrorDePerfil(f"no existe el perfil '{pid}' en {dir_perfiles}")
    datos = yaml.safe_load(ruta.read_text(encoding="utf8"))
    if not isinstance(datos, dict) or datos.get("id") != pid:
        raise ErrorDePerfil(f"{ruta.name}: el campo id no coincide con el nombre del archivo")
    return datos


def _mezclar(hijo: Any, padre: Any) -> Any:
    """Funde un valor del hijo con el del padre.

    Un dict `{"hereda": "<id>"}` significa "toma el del padre entero". Un dict
    con otras claves se funde clave a clave, y el hijo manda.
    """
    if hijo is None:
        return padre
    if isinstance(hijo, dict) and set(hijo) == {"hereda"}:
        return padre
    if isinstance(hijo, dict) and isinstance(padre, dict):
        fundido = dict(padre)
        for k, v in hijo.items():
            if k == "hereda":
                continue
            fundido[k] = _mezclar(v, padre.get(k))
        return fundido
    return hijo


def cargar(pid: str, dir_perfiles: pathlib.Path | None = None,
           raiz: pathlib.Path | None = None, validar: bool = True) -> Perfil:
    """Carga un perfil resolviendo su cadena de herencia."""
    dir_perfiles = dir_perfiles or DIR_PERFILES
    raiz = raiz or RAIZ

    cadena: list[str] = []
    crudos: list[dict[str, Any]] = []
    actual: str | None = pid
    while actual is not None:
        if actual in cadena:
            raise ErrorDePerfil(f"ciclo de herencia: {' -> '.join([*cadena, actual])}")
        cadena.append(actual)
        d = _leer(actual, dir_perfiles)
        crudos.append(d)
        actual = d.get("hereda_de")

    # De la raíz hacia el hijo, para que el hijo sobrescriba.
    resuelto: dict[str, Any] = {}
    heredados: dict[str, str] = {}
    for d in reversed(crudos):
        for clave, valor in d.items():
            if clave in CAMPOS_HEREDABLES:
                previo = resuelto.get(clave)
                fundido = _mezclar(valor, previo)
                if fundido == previo and previo is not None and d is not crudos[0]:
                    heredados[clave] = d["id"]
                resuelto[clave] = fundido
            else:
                resuelto[clave] = valor
        # los campos que el hijo no menciona quedan marcados como heredados
        for clave in CAMPOS_HEREDABLES:
            if clave in resuelto and clave not in d and d is not crudos[-1]:
                heredados.setdefault(clave, d["id"])

    propio = crudos[0]
    for clave in CAMPOS_HEREDABLES:
        if clave in resuelto and clave not in propio:
            heredados.setdefault(clave, cadena[1] if len(cadena) > 1 else cadena[0])

    resuelto["id"] = propio["id"]
    resuelto["estado"] = propio.get("estado")
    resuelto["fuente"] = propio.get("fuente")

    perfil = Perfil(id=propio["id"], datos=resuelto, heredados=heredados, cadena=cadena)
    if validar:
        validar_perfil(perfil, raiz)
    return perfil


def validar_perfil(perfil: Perfil, raiz: pathlib.Path) -> None:
    """Aplica las reglas del esquema. Lanza ErrorDePerfil con todo lo que falle."""
    fallos: list[str] = []
    datos = perfil.datos

    estado = datos.get("estado")
    if estado not in ESTADOS_VALIDOS:
        fallos.append(f"estado inválido: {estado!r}")

    fuente = datos.get("fuente") or {}

    # R2
    if estado == "verificado":
        ruta = fuente.get("archivo_local")
        if not ruta:
            fallos.append("estado 'verificado' sin fuente.archivo_local")
        elif not (raiz / ruta).exists():
            fallos.append(f"estado 'verificado' pero falta el documento en disco: {ruta}")

    # R4
    documento = (fuente.get("documento") or "").lower()
    if datos.get("nivel") == "pregrado" and ("posgrado" in documento or "postgrado" in documento):
        fallos.append("un perfil de pregrado no puede sustentarse en una norma de posgrado")

    # R3: el esquema de facto nunca sustenta por sí solo
    if estado == "verificado" and not fuente.get("archivo_local") and datos.get("esquema_de_facto"):
        fallos.append("'verificado' sustentado únicamente en un esquema de facto")

    if fallos:
        raise ErrorDePerfil(f"{perfil.id}: " + "; ".join(fallos))


def cargar_de(raiz: pathlib.Path, pid: str, validar: bool = True) -> Perfil:
    """Carga un perfil desde `raiz/perfiles/`.

    Las herramientas reciben la raíz del proyecto como parámetro para poder
    trabajar sobre proyectos de prueba; sin esto acabarían leyendo siempre los
    perfiles del repositorio instalado.
    """
    return cargar(pid, dir_perfiles=raiz / "perfiles", raiz=raiz, validar=validar)


def listar(dir_perfiles: pathlib.Path | None = None) -> list[str]:
    """Ids de todos los perfiles disponibles, sin los archivos que empiezan por _."""
    dir_perfiles = dir_perfiles or DIR_PERFILES
    return sorted(p.stem for p in dir_perfiles.glob("*.yaml") if not p.name.startswith("_"))


def perfil_activo(raiz: pathlib.Path | None = None) -> str | None:
    """Lee el id del perfil activo de `.perfil-activo`, si existe."""
    raiz = raiz or RAIZ
    marca = raiz / ".perfil-activo"
    if marca.exists():
        return marca.read_text(encoding="utf8").strip() or None
    return None
