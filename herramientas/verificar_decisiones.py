"""Comprueba que cada etapa completada tenga su decisión aprobada e intacta.

Dos preguntas, que son distintas:

1. **¿Falta alguna decisión?** Si el trabajo de una etapa ya existe en disco
   (capítulos, resultados, proyecto) pero nadie registró la decisión que lo
   sostiene, algo se avanzó sin que el tesista decidiera.
2. **¿Alguien editó una decisión después de registrarla?** Cada archivo lleva un
   sello; si el contenido cambió, el sello no cuadra.

La segunda pregunta es la que da valor al registro frente al asesor: sin ella,
un `decisiones/` sería un montón de archivos de texto que cualquiera puede
retocar.

Uso:
    uv run python -m herramientas.verificar_decisiones
    uv run python -m herramientas.verificar_decisiones --exigir-hasta proyecto
"""
from __future__ import annotations

import argparse
import json
import pathlib
import sys

from herramientas.informe import Informe
from herramientas.registrar_decision import ETAPAS, calcular_hash

RAIZ = pathlib.Path(__file__).resolve().parent.parent
DIR_DECISIONES = RAIZ / "decisiones"

#: Señales en disco de que una etapa ya se trabajó.
EVIDENCIA_DE_ETAPA: dict[str, tuple[str, ...]] = {
    "explorar-datos": ("datos/procesados/*", "datos/diccionarios/*"),
    "literatura": ("notas/lecturas/*",),
    "proyecto": ("capitulos/proyecto*.qmd", "entregables/proyecto*"),
    "analizar": ("resultados/*", "codigo/*.py"),
    "redactar": ("capitulos/*.qmd",),
    "entregar": ("entregables/TEXTO/*",),
}


def _cargar(ruta: pathlib.Path) -> dict | None:
    try:
        return json.loads(ruta.read_text(encoding="utf8"))
    except (json.JSONDecodeError, OSError):
        return None


def _hay_evidencia(raiz: pathlib.Path, patrones: tuple[str, ...]) -> list[str]:
    encontrados: list[str] = []
    for patron in patrones:
        for p in raiz.glob(patron):
            if p.name == ".gitkeep":
                continue
            if p.is_file():
                encontrados.append(str(p.relative_to(raiz)))
    return encontrados


def verificar(raiz: pathlib.Path = RAIZ, exigir_hasta: str | None = None,
              dir_decisiones: pathlib.Path | None = None) -> Informe:
    dir_decisiones = dir_decisiones or (raiz / "decisiones")
    inf = Informe("verificacion_decisiones", "Verificación de decisiones", raiz=raiz)

    archivos = sorted(p for p in dir_decisiones.glob("*.json")
                      if not p.name.startswith("_"))
    inf.anotar(decisiones_encontradas=len(archivos))

    registradas: dict[str, dict] = {}

    for ruta in archivos:
        datos = _cargar(ruta)
        if datos is None:
            inf.error("D01", "el archivo no es un JSON legible", archivo=ruta)
            continue

        etapa = datos.get("etapa")
        if not etapa:
            inf.error("D02", "la decisión no dice a qué etapa corresponde", archivo=ruta)
            continue

        if datos.get("aprobado") is not True:
            inf.error("D03", f"la decisión de `{etapa}` no está aprobada; una "
                             "decisión no aprobada no debería existir en disco",
                      archivo=ruta)

        if not (datos.get("respuesta_textual") or "").strip():
            inf.error("D04", f"la decisión de `{etapa}` no conserva la respuesta "
                             "textual del tesista", archivo=ruta)

        sello = datos.get("hash")
        if not sello:
            inf.error("D05", f"la decisión de `{etapa}` no tiene sello", archivo=ruta)
        elif sello != calcular_hash(datos):
            inf.error("D06", f"la decisión de `{etapa}` fue modificada después de "
                             "registrarse: el sello no coincide con el contenido",
                      archivo=ruta, sello_guardado=sello[:16])

        gemelo = ruta.with_suffix(".md")
        if not gemelo.exists():
            inf.aviso("D07", f"falta el `.md` legible de la decisión de `{etapa}`",
                      archivo=ruta)

        if etapa in registradas:
            inf.aviso("D08", f"hay más de una decisión para la etapa `{etapa}`",
                      archivo=ruta)
        registradas[etapa] = datos

        sin_responder = [p.get("pregunta") for p in datos.get("preguntas_comprension") or []
                         if not (p.get("respuesta") or "").strip()]
        if sin_responder:
            inf.info("D09", f"`{etapa}`: {len(sin_responder)} preguntas de "
                            "comprensión sin responder. No bloquean, pero conviene "
                            "retomarlas antes de la sustentación", archivo=ruta)

    # Etapas trabajadas sin decisión registrada
    for etapa, patrones in EVIDENCIA_DE_ETAPA.items():
        evidencia = _hay_evidencia(raiz, patrones)
        if evidencia and etapa not in registradas:
            inf.error("D10", f"hay trabajo de la etapa `{etapa}` en disco "
                             f"({evidencia[0]}) pero no existe su decisión registrada",
                      etapa=etapa, ejemplos=evidencia[:3])

    # Exigencia explícita hasta cierta etapa (la usan los hooks de la Fase 3)
    if exigir_hasta:
        if exigir_hasta not in ETAPAS:
            inf.error("D11", f"etapa desconocida en --exigir-hasta: {exigir_hasta!r}")
        else:
            tope = ETAPAS.index(exigir_hasta)
            for etapa in ETAPAS[:tope + 1]:
                if etapa not in registradas:
                    inf.error("D12", f"para avanzar se necesita la decisión de la "
                                     f"etapa `{etapa}`, que no está registrada",
                              etapa=etapa)

    inf.anotar(etapas_con_decision=", ".join(sorted(registradas)) or "ninguna")
    return inf


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--exigir-hasta", help="etapa hasta la que deben existir decisiones")
    ap.add_argument("--sin-informe", action="store_true")
    ap.add_argument("--detalle", action="store_true")
    args = ap.parse_args(argv)

    inf = verificar(exigir_hasta=args.exigir_hasta)
    print(inf.volcar(en_disco=not args.sin_informe, mostrar_info=args.detalle))
    return inf.codigo_salida()


if __name__ == "__main__":
    sys.exit(main())
