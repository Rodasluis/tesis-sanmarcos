"""Descarga los datos de la tesis desde la API del Banco Mundial.

Los datos son **reales**. Se bajan de `api.worldbank.org`, que es una de las
fuentes con acceso programático comprobado del catálogo
(`herramientas/fuentes/catalogo.yaml`, fuente `banco_mundial`): no pide clave,
no tiene cuota publicada y responde en JSON.

Lo que queda en `datos/crudos/` no se toca después. Toda transformación va en
los scripts siguientes, para que se pueda ver qué se hizo con qué.

Uso:
    uv run python codigo/01_descarga.py
"""
from __future__ import annotations

import datetime as dt
import json
import pathlib
import time
import urllib.error
import urllib.request

AQUI = pathlib.Path(__file__).resolve().parent.parent
CRUDOS = AQUI / "datos" / "crudos"

BASE = "https://api.worldbank.org/v2"

#: Países de América Latina continental más los de habla hispana del Caribe,
#: en ISO-3. Se eligieron por comparabilidad regional, no por conveniencia.
PAISES = ["PER", "BOL", "ECU", "COL", "CHL", "BRA", "ARG", "URY", "PRY",
          "MEX", "CRI", "PAN", "DOM", "GTM", "HND", "SLV", "NIC"]

DESDE, HASTA = 2010, 2023

#: Indicadores, con el nombre de variable que usaremos después.
INDICADORES = {
    "SL.GDP.PCAP.EM.KD": "productividad",   # PBI por persona ocupada, USD 2021 PPA
    "IT.NET.USER.ZS": "internet",           # personas que usan internet, % población
    "SE.XPD.TOTL.GD.ZS": "gasto_educacion",  # gasto público en educación, % del PBI
    "SL.UEM.TOTL.ZS": "desempleo",          # desempleo, % de la fuerza laboral
    "NY.GDP.PCAP.KD": "pbi_per_capita",     # PBI per cápita, USD 2015 constantes
}


def _pedir(url: str, intentos: int = 3) -> list:
    """Pide una URL con reintentos. La API devuelve 503 de vez en cuando."""
    ultimo: Exception | None = None
    for n in range(intentos):
        try:
            with urllib.request.urlopen(url, timeout=60) as r:
                return json.load(r)
        except (urllib.error.URLError, TimeoutError, json.JSONDecodeError) as e:
            ultimo = e
            if n < intentos - 1:
                time.sleep(2 * (n + 1))
    raise RuntimeError(f"la API no respondió tras {intentos} intentos: {ultimo}")


def descargar(indicador: str) -> dict:
    paises = ";".join(PAISES)
    url = (f"{BASE}/country/{paises}/indicator/{indicador}"
           f"?format=json&date={DESDE}:{HASTA}&per_page=1000")
    datos = _pedir(url)

    if not isinstance(datos, list) or len(datos) < 2 or not datos[1]:
        raise RuntimeError(f"{indicador}: la API no devolvió observaciones")

    meta, filas = datos[0], datos[1]
    if meta.get("pages", 1) > 1:
        # Con per_page=1000 y 17 países por 14 años no debería pasar nunca, pero
        # si pasara estaríamos perdiendo datos en silencio.
        raise RuntimeError(f"{indicador}: la respuesta viene paginada "
                           f"({meta['pages']} páginas); sube per_page")
    return {"indicador": indicador, "meta": meta, "observaciones": filas}


def main() -> int:
    CRUDOS.mkdir(parents=True, exist_ok=True)
    procedencia = [
        "# Procedencia de los datos",
        "",
        "Generado por `codigo/01_descarga.py`. No editar a mano.",
        "",
        f"- Descargado: {dt.date.today().isoformat()}",
        "- Fuente: API del Banco Mundial, `api.worldbank.org/v2`",
        "- Licencia: CC BY 4.0 (World Bank Open Data)",
        f"- Países ({len(PAISES)}): {', '.join(PAISES)}",
        f"- Periodo: {DESDE}–{HASTA}",
        "",
        "## Indicadores",
        "",
        "| Código | Variable | Observaciones con valor |",
        "|---|---|---|",
    ]

    for indicador, variable in INDICADORES.items():
        paquete = descargar(indicador)
        destino = CRUDOS / f"bm_{variable}.json"
        destino.write_text(json.dumps(paquete, ensure_ascii=False, indent=1),
                           encoding="utf8")

        con_valor = sum(1 for o in paquete["observaciones"] if o.get("value") is not None)
        total = len(paquete["observaciones"])
        print(f"  {variable:<16} {con_valor:>4} de {total} observaciones con valor")
        procedencia.append(f"| `{indicador}` | {variable} | {con_valor} de {total} |")

    procedencia += [
        "",
        "## Cómo volver a bajarlos",
        "",
        "```",
        "uv run python codigo/01_descarga.py",
        "```",
        "",
        "El Banco Mundial revisa sus series hacia atrás sin avisar, así que una",
        "descarga nueva puede no coincidir con esta. Por eso la fecha está arriba.",
    ]
    (CRUDOS / "_procedencia.md").write_text("\n".join(procedencia) + "\n",
                                            encoding="utf8")
    print(f"\nCrudos en {CRUDOS.relative_to(AQUI)}/ y procedencia anotada.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
