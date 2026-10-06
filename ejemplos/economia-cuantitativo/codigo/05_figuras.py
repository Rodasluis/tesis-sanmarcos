"""Genera las figuras del capítulo de resultados.

Van a `resultados/figuras/` en PNG. Cada una lleva su nota de fuente dentro del
propio gráfico, porque una figura que se copia a una diapositiva pierde el pie
de figura del documento.

Sin estilos de color que carguen el significado solos: las series se distinguen
también por marcador y por grosor, para que el gráfico se entienda impreso en
blanco y negro.

Uso:
    uv run python codigo/05_figuras.py
"""
from __future__ import annotations

import pathlib

import matplotlib

matplotlib.use("Agg")           # sin ventana: esto corre en CI
import matplotlib.pyplot as plt  # noqa: E402
import pandas as pd  # noqa: E402

AQUI = pathlib.Path(__file__).resolve().parent.parent
PANEL = AQUI / "datos" / "procesados" / "panel.csv"
RESULTADOS = AQUI / "resultados"
FIGURAS = RESULTADOS / "figuras"

FUENTE = "Fuente: Banco Mundial, World Development Indicators. Elaboración propia."


def _pie(ax, texto: str = FUENTE) -> None:
    ax.figure.text(0.01, 0.01, texto, fontsize=7, color="#444444")


def figura_peru_vs_region(panel: pd.DataFrame) -> pathlib.Path:
    comp = pd.read_csv(RESULTADOS / "peru_vs_region.csv")

    fig, ax = plt.subplots(figsize=(7, 4))
    ax.plot(comp["anio"], comp["internet_peru"], marker="o", linewidth=2,
            label="Perú")
    ax.plot(comp["anio"], comp["internet_region"], marker="s", linewidth=1.5,
            linestyle="--", label="Promedio de la región")
    ax.set_xlabel("Año")
    ax.set_ylabel("Personas que usan internet (% de la población)")
    ax.set_title("Penetración de internet: Perú y América Latina, "
                 f"{int(comp['anio'].min())}–{int(comp['anio'].max())}")
    ax.legend(frameon=False)
    ax.grid(axis="y", alpha=0.3)
    fig.tight_layout(rect=(0, 0.04, 1, 1))
    _pie(ax)

    destino = FIGURAS / "internet_peru_region.png"
    fig.savefig(destino, dpi=200)
    plt.close(fig)
    return destino


def figura_dispersion(panel: pd.DataFrame) -> pathlib.Path:
    """La correlación cruda y la misma relación dentro de cada país.

    Las dos juntas, porque es la diferencia entre ellas lo que el estudio
    encuentra: el panel de la izquierda es la correlación que desaparece.
    """
    fig, (izq, der) = plt.subplots(1, 2, figsize=(10, 4.2))

    izq.scatter(panel["internet"], panel["log_productividad"], s=14, alpha=0.6)
    izq.set_xlabel("Internet (% de la población)")
    izq.set_ylabel("log del PBI por ocupado")
    izq.set_title("Todas las observaciones")
    izq.grid(alpha=0.3)

    # Centrado dentro de cada país: solo variación temporal interna.
    centrado = panel.copy()
    for columna in ("internet", "log_productividad"):
        centrado[f"c_{columna}"] = (
            centrado[columna] - centrado.groupby("iso3")[columna].transform("mean"))
    der.scatter(centrado["c_internet"], centrado["c_log_productividad"],
                s=14, alpha=0.6, marker="^")
    der.axhline(0, color="#888888", linewidth=0.8)
    der.axvline(0, color="#888888", linewidth=0.8)
    der.set_xlabel("Internet, desviación del promedio del país")
    der.set_ylabel("log productividad, desviación del promedio del país")
    der.set_title("Variación dentro de cada país")
    der.grid(alpha=0.3)

    fig.tight_layout(rect=(0, 0.05, 1, 1))
    fig.text(0.01, 0.01, FUENTE, fontsize=7, color="#444444")

    destino = FIGURAS / "dispersion_entre_y_dentro.png"
    fig.savefig(destino, dpi=200)
    plt.close(fig)
    return destino


def figura_robustez() -> pathlib.Path:
    """Los coeficientes de todas las especificaciones, con su intervalo."""
    import json
    datos = json.loads((RESULTADOS / "estimaciones.json").read_text(encoding="utf8"))
    especificaciones = datos["especificaciones"]

    nombres = list(especificaciones)
    coefs = [especificaciones[n]["coeficiente"] for n in nombres]
    bajos = [especificaciones[n]["coeficiente"] - especificaciones[n]["ic_bajo"]
             for n in nombres]
    altos = [especificaciones[n]["ic_alto"] - especificaciones[n]["coeficiente"]
             for n in nombres]

    fig, ax = plt.subplots(figsize=(7.5, 4))
    y = range(len(nombres))
    ax.errorbar(coefs, y, xerr=[bajos, altos], fmt="o", capsize=4, linewidth=1.5)
    ax.axvline(0, color="#333333", linestyle=":", linewidth=1)
    ax.set_yticks(list(y))
    ax.set_yticklabels([n.replace("_", " ") for n in nombres])
    ax.invert_yaxis()
    ax.set_xlabel("Coeficiente de internet sobre el log de la productividad")
    ax.set_title("Todas las especificaciones probadas, con intervalo al 95 %")
    ax.grid(axis="x", alpha=0.3)
    fig.tight_layout(rect=(0, 0.05, 1, 1))
    fig.text(0.01, 0.01, FUENTE, fontsize=7, color="#444444")

    destino = FIGURAS / "robustez.png"
    fig.savefig(destino, dpi=200)
    plt.close(fig)
    return destino


def main() -> int:
    FIGURAS.mkdir(parents=True, exist_ok=True)
    panel = pd.read_csv(PANEL)

    for hacer in (lambda: figura_peru_vs_region(panel),
                  lambda: figura_dispersion(panel),
                  figura_robustez):
        destino = hacer()
        print(f"  {destino.relative_to(AQUI)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
