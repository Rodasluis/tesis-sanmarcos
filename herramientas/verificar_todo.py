"""Corre todas las verificaciones y resume el estado de la tesis.

Es lo que ejecuta `/verificar`. Llama a las herramientas de verificación, junta
sus informes y calcula un puntaje por componente.

## Sobre los puntajes

Son un **semáforo**, no una medida de calidad. Un 92 no significa que la tesis
sea buena: significa que estas comprobaciones automáticas no encontraron casi
nada. Una tesis con la pregunta mal planteada puede sacar 100, porque ninguna
herramienta sabe si la pregunta vale la pena.

Los umbrales vienen de la especificación del proyecto y sirven para decidir
cuándo tiene sentido seguir, no para certificar nada:

- **80** para hacer un commit del borrador.
- **85** para pasar de etapa.
- **90** para entregar, y además ningún componente por debajo de 80.

## Por qué cuenta cuánto material revisó

Una tesis vacía no tiene errores. Si el puntaje saliera solo de contar
hallazgos, un repositorio recién creado sacaría 100 y diría "listo para
entregar", que es exactamente la clase de mentira cómoda que este repositorio
existe para no decir.

Así que cada componente informa **cuánto revisó**. Si no revisó nada, no saca
100: queda en `sin material`, no entra en el promedio, y bloquea los umbrales de
etapa y de entrega. En la etapa 1 es lo normal y no es un problema; lo que no
puede pasar es que el vacío se lea como aprobación.

Uso:
    uv run python -m herramientas.verificar_todo
    uv run python -m herramientas.verificar_todo --rapido --detalle
"""
from __future__ import annotations

import argparse
import json
import pathlib
import sys
from dataclasses import dataclass, field

from herramientas import (
    similitud_interna,
    verificar_cifras,
    verificar_decisiones,
    verificar_estructura,
    verificar_perfil,
    verificar_referencias,
)
from herramientas.informe import Informe, puntaje

RAIZ = pathlib.Path(__file__).resolve().parent.parent

UMBRAL_COMMIT = 80
UMBRAL_ETAPA = 85
UMBRAL_ENTREGA = 90
UMBRAL_COMPONENTE = 80

SIN_MATERIAL = "sin material"


@dataclass
class Componente:
    nombre: str
    etiqueta: str
    #: Clave del contexto del informe que dice cuánto material se revisó.
    clave_material: str
    #: Qué falta, en palabras, cuando no hay material. Se le muestra al tesista.
    que_falta: str
    informe: Informe | None = None
    puntaje: int | None = None
    material: int = 0
    error: str = ""

    @property
    def corrio(self) -> bool:
        return self.informe is not None

    @property
    def hay_material(self) -> bool:
        return self.corrio and self.material > 0

    @property
    def ok(self) -> bool:
        return self.hay_material and not self.informe.hay_errores

    @property
    def estado(self) -> str:
        if not self.corrio:
            return "no corrió"
        if not self.hay_material:
            return SIN_MATERIAL
        return "ok" if self.ok else "con hallazgos"


@dataclass
class Resultado:
    componentes: list[Componente] = field(default_factory=list)
    raiz: pathlib.Path = RAIZ

    @property
    def con_material(self) -> list[Componente]:
        return [c for c in self.componentes if c.hay_material]

    @property
    def vacios(self) -> list[Componente]:
        return [c for c in self.componentes if c.corrio and not c.hay_material]

    @property
    def caidos(self) -> list[Componente]:
        return [c for c in self.componentes if not c.corrio]

    @property
    def global_(self) -> int:
        """Promedio de los componentes que tuvieron algo que revisar."""
        vivos = self.con_material
        if not vivos:
            return 0
        return round(sum(c.puntaje for c in vivos) / len(vivos))

    @property
    def peor_componente(self) -> int:
        vivos = [c.puntaje for c in self.con_material]
        return min(vivos) if vivos else 0

    @property
    def errores_totales(self) -> int:
        return sum(len(c.informe.errores) for c in self.componentes if c.corrio)

    @property
    def avisos_totales(self) -> int:
        return sum(len(c.informe.avisos) for c in self.componentes if c.corrio)

    def puede(self, umbral: int) -> bool:
        """Si no hubo nada que revisar, la respuesta es no, aunque el promedio sea alto."""
        if not self.con_material or self.vacios or self.caidos:
            return False
        return self.global_ >= umbral and self.peor_componente >= UMBRAL_COMPONENTE

    def razon_de_no(self) -> str:
        """Por qué no se puede avanzar, en una línea, cuando no es por el puntaje."""
        if self.caidos:
            quienes = ", ".join(c.etiqueta for c in self.caidos)
            return f"hay comprobaciones que no se pudieron correr: {quienes}"
        if not self.con_material:
            return "todavía no hay nada que revisar"
        if self.vacios:
            # Varios componentes esperan lo mismo (los capítulos): no se repite.
            faltas = list(dict.fromkeys(c.que_falta for c in self.vacios))
            return "falta " + "; ".join(faltas)
        if self.peor_componente < UMBRAL_COMPONENTE:
            peor = min(self.con_material, key=lambda c: c.puntaje)
            return (f"«{peor.etiqueta}» está en {peor.puntaje} y ningún componente "
                    f"puede bajar de {UMBRAL_COMPONENTE}")
        return ""

    def veredicto(self) -> list[str]:
        """Qué se puede hacer con este estado, en palabras."""
        lineas = []
        for umbral, que in ((UMBRAL_COMMIT, "hacer commit del borrador"),
                            (UMBRAL_ETAPA, "pasar de etapa"),
                            (UMBRAL_ENTREGA, "entregar")):
            if self.puede(umbral):
                lineas.append(f"  {que}: sí")
            else:
                razon = self.razon_de_no() or f"el global está en {self.global_}"
                lineas.append(f"  {que}: todavía no — {razon}")
        return lineas


def _correr(nombre: str, etiqueta: str, clave_material: str, que_falta: str,
            fn, **kw) -> Componente:
    c = Componente(nombre=nombre, etiqueta=etiqueta,
                   clave_material=clave_material, que_falta=que_falta)
    try:
        c.informe = fn(**kw)
    except Exception as e:  # noqa: BLE001
        # Que una herramienta falle no puede tumbar la verificación entera: el
        # tesista necesita saber qué dicen las demás. Pero tampoco se disimula:
        # un componente caído bloquea los umbrales igual que uno vacío.
        c.error = f"{type(e).__name__}: {e}"
        return c

    c.material = int(c.informe.contexto.get(clave_material, 0) or 0)
    if c.material > 0:
        total = sum(c.informe.resumen().values()) or 1
        c.puntaje = puntaje(c.informe, total)
    return c


def verificar(raiz: pathlib.Path = RAIZ, sin_red: bool = True,
              rapido: bool = False, biblioteca: pathlib.Path | None = None
              ) -> Resultado:
    """Corre todo. `sin_red` por defecto, para no depender de que una API responda."""
    componentes = [
        _correr("perfil", "Perfil y normativa",
                "perfiles_revisados", "un perfil de facultad activo",
                verificar_perfil.verificar, raiz=raiz),
        _correr("decisiones", "Decisiones del tesista",
                "decisiones_encontradas", "registrar las decisiones de cada etapa",
                verificar_decisiones.verificar, raiz=raiz),
        _correr("referencias", "Citas y referencias",
                "capitulos_revisados", "capítulos escritos en `capitulos/`",
                verificar_referencias.verificar, raiz=raiz, sin_red=sin_red),
        _correr("cifras", "Cifras y citas de participantes",
                "capitulos_revisados", "capítulos escritos en `capitulos/`",
                verificar_cifras.verificar, raiz=raiz),
        _correr("estructura", "Estructura del documento",
                "encabezados_de_primer_nivel", "las secciones que pide el perfil",
                verificar_estructura.verificar, raiz=raiz),
    ]
    if not rapido:
        componentes.append(
            _correr("similitud", "Repeticiones y fragmentos sin citar",
                    "capitulos_revisados", "capítulos escritos en `capitulos/`",
                    similitud_interna.verificar, raiz=raiz, biblioteca=biblioteca))
    return Resultado(componentes=componentes, raiz=raiz)


def a_consola(r: Resultado, detalle: bool = False) -> str:
    lineas = ["Verificación completa", "=" * 52, ""]

    ancho = max(len(c.etiqueta) for c in r.componentes)
    for c in r.componentes:
        if not c.corrio:
            lineas.append(f"  [!!] {c.etiqueta:<{ancho}}  no se pudo correr: {c.error}")
            continue
        res = c.informe.resumen()
        if not c.hay_material:
            lineas.append(f"  [--] {c.etiqueta:<{ancho}}    --      "
                          f"nada que revisar todavía")
            continue
        marca = "ok" if c.ok else "  "
        lineas.append(
            f"  [{marca}] {c.etiqueta:<{ancho}}  {c.puntaje:>3}/100   "
            f"{res['error']} errores, {res['aviso']} avisos")

    if r.con_material:
        de = f"{len(r.con_material)} de {len(r.componentes)} componentes"
        lineas += ["",
                   f"Puntaje global: {r.global_}/100, sobre {de}   "
                   f"(el más bajo está en {r.peor_componente})"]
    else:
        lineas += ["", "Puntaje global: no hay material que revisar todavía."]
    lineas += [f"Total: {r.errores_totales} errores, {r.avisos_totales} avisos", ""]
    lineas += r.veredicto()

    if r.vacios:
        lineas += ["",
                   "Los componentes marcados `--` no revisaron nada. En las primeras",
                   "etapas eso es lo normal y no es un problema; lo que no se puede",
                   "es leerlo como aprobación."]

    lineas += [
        "",
        "Los puntajes son un semáforo, no una medida de calidad. Dicen que estas",
        "comprobaciones no encontraron nada, no que la tesis esté bien: ninguna",
        "herramienta sabe si la pregunta de investigación vale la pena.",
    ]

    if detalle:
        for c in r.componentes:
            if c.corrio and (c.informe.errores or c.informe.avisos):
                lineas += ["", f"--- {c.etiqueta} ---"]
                lineas += [h.como_linea() for h in c.informe.errores]
                lineas += [h.como_linea() for h in c.informe.avisos]
    else:
        lineas += ["", "Detalle de cada componente en `registro/`, o usa --detalle."]

    return "\n".join(lineas)


def escribir_resumen(r: Resultado) -> pathlib.Path:
    destino = r.raiz / "registro" / "verificacion_global.json"
    destino.parent.mkdir(parents=True, exist_ok=True)
    datos = {
        "global": r.global_ if r.con_material else None,
        "peor_componente": r.peor_componente if r.con_material else None,
        "errores": r.errores_totales,
        "avisos": r.avisos_totales,
        "puede_commit": r.puede(UMBRAL_COMMIT),
        "puede_pasar_de_etapa": r.puede(UMBRAL_ETAPA),
        "puede_entregar": r.puede(UMBRAL_ENTREGA),
        "razon_de_no": r.razon_de_no() or None,
        "componentes": {
            c.nombre: {
                "estado": c.estado,
                "puntaje": c.puntaje,
                "material_revisado": c.material if c.corrio else None,
                "errores": len(c.informe.errores) if c.corrio else None,
                "avisos": len(c.informe.avisos) if c.corrio else None,
                "error_al_correr": c.error or None,
            }
            for c in r.componentes
        },
        "descargo": ("Los puntajes son un semáforo, no una medida de calidad. "
                     "Un componente sin material no vale 100: no revisó nada. "
                     "Quien aprueba una tesis es el jurado, en la sustentación."),
    }
    destino.write_text(json.dumps(datos, ensure_ascii=False, indent=1), encoding="utf8")
    return destino


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--con-red", action="store_true",
                    help="consulta Crossref, OpenAlex y PubMed (por defecto no)")
    ap.add_argument("--rapido", action="store_true",
                    help="omite la comprobación de similitud, que es la más lenta")
    ap.add_argument("--biblioteca", type=pathlib.Path)
    ap.add_argument("--raiz", type=pathlib.Path, default=RAIZ,
                    help="raíz del proyecto a verificar; por defecto, este repositorio")
    ap.add_argument("--detalle", action="store_true")
    ap.add_argument("--sin-informe", action="store_true")
    args = ap.parse_args(argv)

    if not (args.raiz / "perfiles").is_dir():
        print(f"{args.raiz} no parece la raíz de un proyecto: no tiene perfiles/.",
              file=sys.stderr)
        return 2

    r = verificar(raiz=args.raiz, sin_red=not args.con_red, rapido=args.rapido,
                  biblioteca=args.biblioteca)
    print(a_consola(r, detalle=args.detalle))

    if not args.sin_informe:
        for c in r.componentes:
            if c.corrio:
                c.informe.a_markdown()
                c.informe.a_json()
        escribir_resumen(r)

    return 1 if r.errores_totales else 0


if __name__ == "__main__":
    sys.exit(main())
