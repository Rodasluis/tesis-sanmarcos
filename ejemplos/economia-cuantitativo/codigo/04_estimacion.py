"""Estima la asociación y la pone a prueba.

La especificación principal es un panel con efectos fijos de país y de año, y
errores estándar agrupados por país. Las alternativas están **todas** guardadas,
incluidas las que debilitan el resultado: esconder la que no salió es lo que el
art. 10 d) del Código de Ética llama manipulación de las conclusiones, y además
es lo que el jurado encuentra.

Qué permite leer esto y qué no:

- Los efectos fijos de país absorben todo lo que no cambia en el tiempo dentro
  de un país (geografía, instituciones, historia). Los de año absorben lo que le
  pasa a toda la región el mismo año, como una crisis o la pandemia.
- Lo que **no** resuelven es la simultaneidad: un país más productivo puede
  permitirse más internet. Así que esto es una **asociación condicional**, no un
  efecto causal, y el texto lo dice con esas palabras.

Uso:
    uv run python codigo/04_estimacion.py
"""
from __future__ import annotations

import json
import pathlib

import numpy as np
import pandas as pd
import statsmodels.formula.api as smf

AQUI = pathlib.Path(__file__).resolve().parent.parent
PANEL = AQUI / "datos" / "procesados" / "panel.csv"
RESULTADOS = AQUI / "resultados"

#: Cada entrada es una especificación: su fórmula y por qué está.
ESPECIFICACIONES = {
    "pooled": {
        "formula": "log_productividad ~ internet",
        "agrupado": True,
        "por_que": "Correlación simple, sin controles. Es el punto de partida, "
                   "no un resultado: confunde diferencias entre países con "
                   "cambios dentro de un país.",
    },
    "ef_pais": {
        "formula": "log_productividad ~ internet + C(iso3)",
        "agrupado": True,
        "por_que": "Efectos fijos de país. Usa solo la variación dentro de cada "
                   "país a lo largo del tiempo.",
    },
    "principal": {
        "formula": "log_productividad ~ internet + C(iso3) + C(anio)",
        "agrupado": True,
        "por_que": "Especificación principal: efectos fijos de país y de año. "
                   "Los de año absorben los choques comunes a la región.",
    },
    "con_controles": {
        "formula": "log_productividad ~ internet + desempleo + gasto_educacion "
                   "+ C(iso3) + C(anio)",
        "agrupado": True,
        "por_que": "Agrega desempleo y gasto en educación. Cae la muestra, "
                   "porque el gasto en educación tiene faltantes.",
    },
    "sin_peru": {
        "formula": "log_productividad ~ internet + C(iso3) + C(anio)",
        "agrupado": True,
        "filtro": "iso3 != 'PER'",
        "por_que": "La principal sin el Perú. Si el resultado dependiera de un "
                   "solo país, habría que decirlo.",
    },
    "sin_pandemia": {
        "formula": "log_productividad ~ internet + C(iso3) + C(anio)",
        "agrupado": True,
        "filtro": "anio < 2020",
        "por_que": "Hasta 2019. En 2020 la productividad y el uso de internet "
                   "se movieron juntos por razones que no son las del estudio.",
    },
    "primeras_diferencias": {
        "formula": "d_log_productividad ~ d_internet + C(anio)",
        "agrupado": True,
        # El primer año del panel no tiene diferencia: se excluye de forma
        # explícita para que `C(anio)` no quede con una categoría vacía, que
        # deja la matriz de diseño sin rango completo.
        "filtro": "anio > 2010",
        "por_que": "En primeras diferencias. Si la relación en niveles viniera "
                   "de una tendencia compartida, aquí se debilitaría.",
    },
}


def correr(panel: pd.DataFrame, spec: dict) -> dict:
    datos = panel.query(spec["filtro"]) if spec.get("filtro") else panel
    modelo = smf.ols(spec["formula"], data=datos)

    if spec.get("agrupado"):
        # Agrupar por país: las observaciones de un mismo país no son
        # independientes entre años y los errores estándar ingenuos mentirían.
        #
        # Los grupos se toman de las filas que el modelo realmente usó. En las
        # especificaciones con faltantes —controles, primeras diferencias—
        # statsmodels ya descartó filas, y pasarle la columna entera del panel
        # desalinea los grupos de los residuos.
        usadas = modelo.data.row_labels
        grupos = pd.factorize(datos.loc[usadas, "iso3"])[0]
        ajuste = modelo.fit(cov_type="cluster", cov_kwds={"groups": grupos})
        n_paises = int(datos.loc[usadas, "iso3"].nunique())
    else:
        ajuste = modelo.fit()
        n_paises = int(datos["iso3"].nunique())

    variable = "d_internet" if "d_internet" in ajuste.params.index else "internet"
    return {
        "formula": spec["formula"],
        "por_que": spec["por_que"],
        "filtro": spec.get("filtro"),
        "n": int(ajuste.nobs),
        "paises": n_paises,
        "variable": variable,
        "coeficiente": round(float(ajuste.params[variable]), 5),
        "error_estandar": round(float(ajuste.bse[variable]), 5),
        "t": round(float(ajuste.tvalues[variable]), 3),
        "p": round(float(ajuste.pvalues[variable]), 5),
        "ic_bajo": round(float(ajuste.conf_int().loc[variable, 0]), 5),
        "ic_alto": round(float(ajuste.conf_int().loc[variable, 1]), 5),
        "r2": round(float(ajuste.rsquared), 4),
    }


def main() -> int:
    RESULTADOS.mkdir(parents=True, exist_ok=True)
    panel = pd.read_csv(PANEL).sort_values(["iso3", "anio"])

    # Primeras diferencias dentro de cada país.
    panel["d_log_productividad"] = panel.groupby("iso3")["log_productividad"].diff()
    panel["d_internet"] = panel.groupby("iso3")["internet"].diff()

    estimaciones = {}
    for nombre, spec in ESPECIFICACIONES.items():
        estimaciones[nombre] = correr(panel, spec)
        e = estimaciones[nombre]
        signo = "+" if e["coeficiente"] > 0 else "-"
        print(f"  {nombre:<22} {signo}{abs(e['coeficiente']):.5f}  "
              f"(ee {e['error_estandar']:.5f}, p {e['p']:.4f}, n {e['n']})")

    principal = estimaciones["principal"]
    # Un punto porcentual más de penetración se asocia con este cambio
    # porcentual en la productividad: 100 * coeficiente, porque la dependiente
    # está en logaritmos.
    resumen = {
        "coeficiente": principal["coeficiente"],
        "efecto_porcentual_por_punto": round(principal["coeficiente"] * 100, 3),
        "efecto_porcentual_por_diez_puntos": round(principal["coeficiente"] * 1000, 2),
        "p": principal["p"],
        "significativo_al_5": bool(principal["p"] < 0.05),
        "n": principal["n"],
        "paises": principal["paises"],
        "especificaciones_probadas": len(ESPECIFICACIONES),
        "especificaciones_con_mismo_signo": sum(
            1 for e in estimaciones.values()
            if np.sign(e["coeficiente"]) == np.sign(principal["coeficiente"])),
        "especificaciones_significativas_al_5": sum(
            1 for e in estimaciones.values() if e["p"] < 0.05),
        "advertencia": ("Asociación condicional, no efecto causal: los efectos "
                        "fijos no resuelven la simultaneidad entre productividad "
                        "y adopción de internet."),
    }

    # El hallazgo de este estudio no es el coeficiente principal: es que el
    # coeficiente CAMBIA DE SIGNO Y PIERDE SIGNIFICANCIA al entrar los efectos
    # de año. Si el resumen solo guardara la principal, el texto podría contarlo
    # como «no encontramos relación» y perder lo interesante.
    pooled = estimaciones["pooled"]
    resumen["comparacion_clave"] = {
        "pooled_coeficiente": pooled["coeficiente"],
        "pooled_p": pooled["p"],
        "principal_coeficiente": principal["coeficiente"],
        "principal_p": principal["p"],
        "cambia_de_signo": bool(np.sign(pooled["coeficiente"])
                                != np.sign(principal["coeficiente"])),
        "pierde_significancia": bool(pooled["p"] < 0.05 <= principal["p"]),
        "lectura": ("La correlación simple es positiva y significativa; con "
                    "efectos fijos de país y de año desaparece. Lo que la "
                    "correlación recogía era la tendencia común: en toda la "
                    "región el uso de internet y la productividad subieron a la "
                    "vez, sin que lo uno explique lo otro."),
    }

    (RESULTADOS / "estimaciones.json").write_text(
        json.dumps({"resumen": resumen, "especificaciones": estimaciones},
                   ensure_ascii=False, indent=1), encoding="utf8")

    # La misma tabla, en CSV, para pegarla en el capítulo de resultados.
    pd.DataFrame([
        {"especificacion": nombre, "coeficiente": e["coeficiente"],
         "error_estandar": e["error_estandar"], "p": e["p"], "n": e["n"],
         "r2": e["r2"]}
        for nombre, e in estimaciones.items()
    ]).to_csv(RESULTADOS / "tabla_estimaciones.csv", index=False)

    print(f"\n  {resumen['especificaciones_con_mismo_signo']} de "
          f"{resumen['especificaciones_probadas']} especificaciones con el mismo signo")
    print(f"  {resumen['especificaciones_significativas_al_5']} de "
          f"{resumen['especificaciones_probadas']} significativas al 5 %")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
