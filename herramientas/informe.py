"""Informe común a todas las herramientas de verificación.

La sección 9 de la especificación pide, para cada herramienta, salida en
consola, un `.md` en `registro/` y un JSON, y código de salida distinto de 0
cuando hay errores. Eso vive aquí una sola vez.

Tres niveles, con un criterio fijo:

- `error`  algo que impide entregar. Hace fallar el comando.
- `aviso`  algo que el tesista debe mirar, pero que no bloquea.
- `info`   contexto útil que no exige acción.

Un principio que atraviesa todo el repositorio: **la ausencia de errores no es
una certificación**. Cada informe lo dice explícitamente, para que nadie lea un
"sin errores" como "ya está aprobado".
"""
from __future__ import annotations

import datetime as dt
import json
import pathlib
from collections.abc import Iterable
from dataclasses import asdict, dataclass, field
from typing import Any

RAIZ = pathlib.Path(__file__).resolve().parent.parent
DIR_REGISTRO = RAIZ / "registro"

NIVELES = ("error", "aviso", "info")

_SIMBOLO = {"error": "X", "aviso": "!", "info": "·"}


@dataclass
class Hallazgo:
    nivel: str
    codigo: str
    mensaje: str
    archivo: str | None = None
    linea: int | None = None
    detalle: dict[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        if self.nivel not in NIVELES:
            raise ValueError(f"nivel desconocido: {self.nivel!r}")

    @property
    def ubicacion(self) -> str:
        if self.archivo and self.linea:
            return f"{self.archivo}:{self.linea}"
        return self.archivo or ""

    def como_linea(self) -> str:
        loc = f" [{self.ubicacion}]" if self.ubicacion else ""
        return f"  {_SIMBOLO[self.nivel]} {self.codigo}: {self.mensaje}{loc}"


class Informe:
    """Acumula hallazgos y los vuelca en los tres formatos."""

    def __init__(self, herramienta: str, titulo: str, raiz: pathlib.Path = RAIZ) -> None:
        self.herramienta = herramienta
        self.titulo = titulo
        self.raiz = raiz
        self.hallazgos: list[Hallazgo] = []
        self.contexto: dict[str, Any] = {}
        self.momento = dt.datetime.now()

    # -- registro de hallazgos -------------------------------------------------

    def _agregar(self, nivel: str, codigo: str, mensaje: str,
                 archivo: str | pathlib.Path | None = None,
                 linea: int | None = None, **detalle: Any) -> Hallazgo:
        if isinstance(archivo, pathlib.Path):
            try:
                archivo = str(archivo.relative_to(self.raiz))
            except ValueError:
                archivo = str(archivo)
        h = Hallazgo(nivel, codigo, mensaje, archivo, linea, detalle)
        self.hallazgos.append(h)
        return h

    def error(self, codigo: str, mensaje: str, **kw: Any) -> Hallazgo:
        return self._agregar("error", codigo, mensaje, **kw)

    def aviso(self, codigo: str, mensaje: str, **kw: Any) -> Hallazgo:
        return self._agregar("aviso", codigo, mensaje, **kw)

    def info(self, codigo: str, mensaje: str, **kw: Any) -> Hallazgo:
        return self._agregar("info", codigo, mensaje, **kw)

    def anotar(self, **contexto: Any) -> None:
        """Guarda datos de contexto que aparecerán en el encabezado del informe."""
        self.contexto.update(contexto)

    # -- consultas -------------------------------------------------------------

    def de_nivel(self, nivel: str) -> list[Hallazgo]:
        return [h for h in self.hallazgos if h.nivel == nivel]

    @property
    def errores(self) -> list[Hallazgo]:
        return self.de_nivel("error")

    @property
    def avisos(self) -> list[Hallazgo]:
        return self.de_nivel("aviso")

    @property
    def hay_errores(self) -> bool:
        return bool(self.errores)

    def codigo_salida(self) -> int:
        return 1 if self.hay_errores else 0

    def resumen(self) -> dict[str, int]:
        return {n: len(self.de_nivel(n)) for n in NIVELES}

    # -- salidas ---------------------------------------------------------------

    def a_consola(self, mostrar_info: bool = False) -> str:
        lineas = [self.titulo, "=" * max(len(self.titulo), 40)]
        for clave, valor in self.contexto.items():
            lineas.append(f"  {clave}: {valor}")
        if self.contexto:
            lineas.append("")

        rotulos = {"error": "ERRORES", "aviso": "AVISOS", "info": "NOTAS"}
        niveles = ("error", "aviso") + (("info",) if mostrar_info else ())
        for nivel in niveles:
            grupo = self.de_nivel(nivel)
            if not grupo:
                continue
            lineas.append(f"{rotulos[nivel]} ({len(grupo)})")
            lineas.extend(h.como_linea() for h in grupo)
            lineas.append("")

        r = self.resumen()
        lineas.append(f"Resultado: {r['error']} errores, {r['aviso']} avisos, "
                      f"{r['info']} notas.")
        if not self.hay_errores:
            lineas.append(self.descargo())
        return "\n".join(lineas)

    @staticmethod
    def descargo() -> str:
        return ("Sin errores no significa aprobado: significa que estas "
                "comprobaciones no encontraron nada. La revisión del asesor y del "
                "jurado sigue siendo necesaria.")

    def a_markdown(self, destino: pathlib.Path | None = None) -> pathlib.Path:
        destino = destino or (self.raiz / "registro" / f"{self.herramienta}.md")
        destino.parent.mkdir(parents=True, exist_ok=True)

        r = self.resumen()
        lineas = [
            f"# {self.titulo}",
            "",
            f"- Herramienta: `{self.herramienta}`",
            f"- Ejecutada: {self.momento.isoformat(timespec='seconds')}",
            f"- Resultado: **{r['error']} errores**, {r['aviso']} avisos, {r['info']} notas",
        ]
        for clave, valor in self.contexto.items():
            lineas.append(f"- {clave}: {valor}")
        lineas += ["", f"> {self.descargo()}", ""]

        for nivel in NIVELES:
            grupo = self.de_nivel(nivel)
            if not grupo:
                continue
            titulo = {"error": "Errores", "aviso": "Avisos", "info": "Notas"}[nivel]
            lineas += [f"## {titulo} ({len(grupo)})", "",
                       "| Código | Dónde | Qué pasa |", "|---|---|---|"]
            for h in grupo:
                lineas.append(f"| `{h.codigo}` | {h.ubicacion or '—'} | {h.mensaje} |")
            lineas.append("")

        if not self.hallazgos:
            lineas += ["No se encontró nada que reportar.", ""]

        destino.write_text("\n".join(lineas), encoding="utf8")
        return destino

    def a_json(self, destino: pathlib.Path | None = None) -> pathlib.Path:
        destino = destino or (self.raiz / "registro" / f"{self.herramienta}.json")
        destino.parent.mkdir(parents=True, exist_ok=True)
        datos = {
            "herramienta": self.herramienta,
            "titulo": self.titulo,
            "momento": self.momento.isoformat(timespec="seconds"),
            "contexto": self.contexto,
            "resumen": self.resumen(),
            "descargo": self.descargo(),
            "hallazgos": [asdict(h) for h in self.hallazgos],
        }
        destino.write_text(json.dumps(datos, ensure_ascii=False, indent=1),
                           encoding="utf8")
        return destino

    def volcar(self, en_disco: bool = True, mostrar_info: bool = False) -> str:
        """Imprime en consola y, si procede, escribe el .md y el .json."""
        texto = self.a_consola(mostrar_info=mostrar_info)
        if en_disco:
            self.a_markdown()
            self.a_json()
        return texto


def puntaje(informe: Informe, total_revisado: int) -> int:
    """Puntaje 0-100 orientativo de un componente.

    Cada error descuenta 10 puntos y cada aviso 2, sobre 100. No es una medida
    de calidad de la tesis: es un semáforo para saber si vale la pena seguir.
    Nunca sustituye la decisión del tesista ni la del asesor.
    """
    if total_revisado == 0:
        return 0
    r = informe.resumen()
    bruto = 100 - r["error"] * 10 - r["aviso"] * 2
    return max(0, min(100, bruto))


def unir(*informes: Informe) -> dict[str, Any]:
    """Resumen agregado de varios informes, para `/verificar` y el tablero."""
    total = {"error": 0, "aviso": 0, "info": 0}
    por_herramienta = {}
    for inf in informes:
        r = inf.resumen()
        for k in total:
            total[k] += r[k]
        por_herramienta[inf.herramienta] = r
    return {"total": total, "por_herramienta": por_herramienta,
            "hay_errores": total["error"] > 0}


def iter_qmd(raiz: pathlib.Path, subdirs: Iterable[str] = ("capitulos",)) -> list[pathlib.Path]:
    """Archivos .qmd del proyecto, en orden estable."""
    salida: list[pathlib.Path] = []
    for sub in subdirs:
        d = raiz / sub
        if d.exists():
            salida.extend(sorted(d.rglob("*.qmd")))
    return salida
