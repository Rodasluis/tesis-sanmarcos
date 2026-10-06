"""Describe el panel: cobertura, descriptivos y calidad.

Todo lo que produce va a `resultados/`, para que los capítulos lo citen con
expresiones de Quarto en lugar de números escritos a mano.

Uso:
    uv run python codigo/03_descriptivos.py
"""
from __future__ import annotations

import json
import pathlib

import pandas as pd

AQUI = pathlib.Path(__file__).resolve().parent.parent
PANEL = AQUI / "datos" / "procesados" / "panel.csv"
RESULTADOS = AQUI / "resultados"

ETIQUETAS = {
    "productividad": "PBI por persona ocupada (USD 2021 PPA)",
    "internet": "Personas que usan internet (% de la población)",
    "gasto_educacion": "Gasto público en educación (% del PBI)",
    "desempleo": "Desempleo (% de la fuerza laboral)",
    "pbi_per_capita": "PBI per cápita (USD 2015 constantes)",
}


def main() -> int:
    RESULTADOS.mkdir(parents=True, exist_ok=True)
    panel = pd.read_csv(PANEL)

    # Descriptivos de las variables del análisis.
    filas = []
    for variable, etiqueta in ETIQUETAS.items():
        s = panel[variable].dropna()
        filas.append({
            "variable": variable,
            "etiqueta": etiqueta,
            "n": len(s),
            "media": round(s.mean(), 2),
            "desviacion": round(s.std(), 2),
            "minimo": round(s.min(), 2),
            "mediana": round(s.median(), 2),
            "maximo": round(s.max(), 2),
        })
    descriptivos = pd.DataFrame(filas)
    descriptivos.to_csv(RESULTADOS / "descriptivos.csv", index=False)

    # Correlaciones, para decir en qué nos vamos a meter.
    correlaciones = panel[list(ETIQUETAS)].corr().round(3)
    correlaciones.to_csv(RESULTADOS / "correlaciones.csv")

    # El Perú contra la región, que es lo que al tesista le interesa.
    peru = panel[panel["iso3"] == "PER"].sort_values("anio")
    region = panel.groupby("anio")[["productividad", "internet"]].mean().round(2)
    comparacion = peru[["anio", "productividad", "internet"]].merge(
        region, on="anio", suffixes=("_peru", "_region"))
    comparacion = comparacion.round(2)
    comparacion.to_csv(RESULTADOS / "peru_vs_region.csv", index=False)

    # Cobertura del panel: un panel con huecos no es un panel balanceado y el
    # texto no puede decir que lo sea.
    por_pais = panel.groupby(["pais", "iso3"]).agg(
        anios=("anio", "nunique"),
        desde=("anio", "min"),
        hasta=("anio", "max"),
    ).reset_index().sort_values("pais")
    por_pais.to_csv(RESULTADOS / "cobertura_por_pais.csv", index=False)

    contexto = {
        "paises": int(panel["pais"].nunique()),
        "anios": int(panel["anio"].nunique()),
        "desde": int(panel["anio"].min()),
        "hasta": int(panel["anio"].max()),
        "observaciones": int(len(panel)),
        "balanceado": bool((por_pais["anios"] == panel["anio"].nunique()).all()),
        "internet_peru_inicio": round(
            float(peru.iloc[0]["internet"]), 1) if len(peru) else None,
        "internet_peru_final": round(
            float(peru.iloc[-1]["internet"]), 1) if len(peru) else None,
        "productividad_peru_inicio": round(
            float(peru.iloc[0]["productividad"]), 0) if len(peru) else None,
        "productividad_peru_final": round(
            float(peru.iloc[-1]["productividad"]), 0) if len(peru) else None,
        "fuente": "Banco Mundial, World Development Indicators",
    }
    (RESULTADOS / "contexto.json").write_text(
        json.dumps(contexto, ensure_ascii=False, indent=1), encoding="utf8")

    print(f"  {contexto['paises']} países, {contexto['anios']} años, "
          f"{contexto['observaciones']} observaciones")
    print(f"  panel balanceado: {'sí' if contexto['balanceado'] else 'no'}")
    print(f"  internet en el Perú: {contexto['internet_peru_inicio']} % "
          f"-> {contexto['internet_peru_final']} %")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
