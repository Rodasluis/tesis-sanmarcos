"""Arma el panel país-año desde los crudos y deja constancia de lo que se pierde.

De `datos/crudos/` no se toca nada: se lee. El resultado va a
`datos/procesados/panel.csv`.

Lo que un jurado pregunta de este script no es cómo se hizo el merge, sino
**cuántas observaciones entraron, cuántas salieron y si las que se fueron se
parecían a las que quedaron**. Eso se calcula aquí y se guarda en
`resultados/flujo_de_muestra.csv`, para que el capítulo de métodos pueda citarlo
en lugar de decir "se eliminaron los casos incompletos".

Uso:
    uv run python codigo/02_limpieza.py
"""
from __future__ import annotations

import json
import pathlib

import numpy as np
import pandas as pd

AQUI = pathlib.Path(__file__).resolve().parent.parent
CRUDOS = AQUI / "datos" / "crudos"
PROCESADOS = AQUI / "datos" / "procesados"
RESULTADOS = AQUI / "resultados"

VARIABLES = ["productividad", "internet", "gasto_educacion", "desempleo",
             "pbi_per_capita"]

#: La variable dependiente y la explicativa de interés. Sin estas dos no hay
#: observación posible, así que su ausencia excluye la fila.
IMPRESCINDIBLES = ["productividad", "internet"]


def leer(variable: str) -> pd.DataFrame:
    ruta = CRUDOS / f"bm_{variable}.json"
    paquete = json.loads(ruta.read_text(encoding="utf8"))
    filas = [
        {"pais": o["country"]["value"],
         "iso3": o["countryiso3code"],
         "anio": int(o["date"]),
         variable: o["value"]}
        for o in paquete["observaciones"]
    ]
    return pd.DataFrame(filas)


def main() -> int:
    PROCESADOS.mkdir(parents=True, exist_ok=True)
    RESULTADOS.mkdir(parents=True, exist_ok=True)

    panel = leer(VARIABLES[0])
    for variable in VARIABLES[1:]:
        panel = panel.merge(leer(variable), on=["pais", "iso3", "anio"], how="outer")

    panel = panel.sort_values(["pais", "anio"]).reset_index(drop=True)
    flujo = [("Observaciones país-año descargadas", len(panel))]

    # Qué falta, variable por variable. Esto va al capítulo de métodos tal cual.
    faltantes = (panel[VARIABLES].isna().sum()
                 .rename("faltantes").reset_index()
                 .rename(columns={"index": "variable"}))
    faltantes["porcentaje"] = (faltantes["faltantes"] / len(panel) * 100).round(1)
    faltantes.to_csv(RESULTADOS / "faltantes_por_variable.csv", index=False)

    # Comparar lo que se va con lo que se queda, antes de tirarlo.
    completo = panel[IMPRESCINDIBLES].notna().all(axis=1)
    if (~completo).any():
        comparacion = pd.DataFrame({
            "se_queda": panel.loc[completo, VARIABLES].mean(numeric_only=True),
            "se_excluye": panel.loc[~completo, VARIABLES].mean(numeric_only=True),
        }).round(2)
        comparacion.to_csv(RESULTADOS / "comparacion_excluidos.csv")

    panel = panel.loc[completo].copy()
    flujo.append(("Con productividad e internet observadas", len(panel)))

    # Las variables de control se conservan con faltantes: cada estimación dirá
    # con cuántas observaciones corrió. Eliminar filas aquí por un control
    # cambiaría la muestra de la estimación principal sin que se note.
    # En logaritmos, para leer los coeficientes como elasticidades y porque la
    # productividad entre Nicaragua y Chile se reparte en dos ordenes de magnitud.
    for columna in ("productividad", "pbi_per_capita"):
        panel[f"log_{columna}"] = np.log(panel[columna].where(panel[columna] > 0))

    flujo.append(("Países en el panel", panel["pais"].nunique()))
    flujo.append(("Años cubiertos", panel["anio"].nunique()))

    pd.DataFrame(flujo, columns=["paso", "n"]).to_csv(
        RESULTADOS / "flujo_de_muestra.csv", index=False)

    panel.to_csv(PROCESADOS / "panel.csv", index=False, encoding="utf8")

    for paso, n in flujo:
        print(f"  {paso:<42} {n:>5}")
    print(f"\nPanel en {(PROCESADOS / 'panel.csv').relative_to(AQUI)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
