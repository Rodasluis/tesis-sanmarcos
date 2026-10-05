"""Vuelve a comprobar las URL del catálogo de fuentes.

Las URL de los portales del Estado se rompen: cambian de dominio, el organismo
cambia de nombre, una ruta se retira. Un catálogo con direcciones muertas es
peor que no tener catálogo, porque manda al tesista a perder una tarde.

Esto comprueba cada una y dice qué sigue en pie. No reescribe el catálogo: los
estados se actualizan a mano, porque decidir si algo pasa de `api_verificada` a
`api_bloqueada` requiere mirar qué devolvió, no solo el código HTTP.

Uso:
    uv run python -m herramientas.fuentes.verificar
    uv run python -m herramientas.fuentes.verificar --solo-apis
"""
from __future__ import annotations

import argparse
import pathlib
import sys
import time
from concurrent.futures import ThreadPoolExecutor

import yaml

AQUI = pathlib.Path(__file__).resolve().parent
CATALOGO = AQUI / "catalogo.yaml"

UA = ("Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
      "(KHTML, like Gecko) Chrome/140.0 Safari/537.36")

#: Estados del catálogo y qué se espera de cada uno al comprobarlo.
ESPERADO = {
    "api_verificada": "debería seguir respondiendo con datos",
    "api_bloqueada": "se sabe que no atiende peticiones automáticas",
    "manual_verificada": "el portal debería abrir",
    "verificar": "estaba pendiente de resolver",
}


def cargar(ruta: pathlib.Path = CATALOGO) -> dict:
    return yaml.safe_load(ruta.read_text(encoding="utf8"))


def _probar(url: str, timeout: float = 30.0, intentos: int = 2
            ) -> tuple[int | None, str, bool]:
    """Devuelve (código, tipo de contenido, parece_json).

    Reintenta una vez antes de dar una fuente por caída. Varios portales del
    Estado peruano fallan de forma intermitente cuando se les consulta en
    paralelo, y una falsa alarma es peor que no comprobar: si la herramienta
    cría fama de equivocarse, nadie vuelve a mirar su salida.
    """
    try:
        import requests
        import urllib3
        # Varios portales del Estado tienen la cadena de certificados mal
        # configurada. Se comprueba igual, pero sin llenar la salida de avisos.
        urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
    except ImportError:
        return None, "falta requests", False

    r = None
    for intento in range(intentos):
        try:
            r = requests.get(url, headers={"User-Agent": UA}, timeout=timeout,
                             verify=False, allow_redirects=True)
            break
        except Exception as e:  # noqa: BLE001
            if intento == intentos - 1:
                return None, type(e).__name__, False
            time.sleep(2.0)
    if r is None:  # pragma: no cover - el bucle siempre devuelve o asigna
        return None, "sin respuesta", False
    tipo = r.headers.get("content-type", "").split(";")[0]
    parece_json = False
    if r.status_code == 200:
        try:
            r.json()
            parece_json = True
        except ValueError:
            parece_json = False
    return r.status_code, tipo, parece_json


def _url_de_prueba(fuente: dict) -> str | None:
    """La URL más informativa de una fuente: el ejemplo, la API, o el portal."""
    for clave in ("ejemplo", "api", "url"):
        valor = fuente.get(clave)
        if isinstance(valor, str) and valor.startswith("http") and "{" not in valor:
            return valor
    return None


def comprobar(solo_apis: bool = False, ruta: pathlib.Path = CATALOGO) -> list[dict]:
    catalogo = cargar(ruta)
    fuentes = catalogo.get("fuentes") or []
    if solo_apis:
        fuentes = [f for f in fuentes if f.get("estado", "").startswith("api")]

    objetivos = [(f, _url_de_prueba(f)) for f in fuentes]

    def tarea(par):
        fuente, url = par
        if not url:
            return {"id": fuente.get("id"), "url": None, "codigo": None,
                    "nota": "sin URL comprobable"}
        codigo, tipo, es_json = _probar(url)
        return {"id": fuente.get("id"), "estado_declarado": fuente.get("estado"),
                "url": url, "codigo": codigo, "tipo": tipo, "json": es_json}

    with ThreadPoolExecutor(max_workers=6) as ex:
        return list(ex.map(tarea, objetivos))


def _formato_no_json(url: str) -> str | None:
    """¿El endpoint devuelve datos legibles por máquina que no son JSON?

    Acceso programático no es sinónimo de JSON. OAI-PMH devuelve XML y la
    descarga de Our World in Data devuelve CSV; ambos se leen con una línea de
    código y cuentan como API verificada.
    """
    u = (url or "").lower()
    if "/oai/" in u or "verb=" in u:
        return "XML (OAI-PMH)"
    if ".csv" in u:
        return "CSV"
    return None


def _discrepa(fila: dict) -> str | None:
    """¿Lo observado contradice lo que declara el catálogo?"""
    declarado = fila.get("estado_declarado")
    codigo = fila.get("codigo")
    url = fila.get("url") or ""
    if declarado == "api_verificada":
        if codigo != 200:
            return f"declara API verificada y respondió {codigo}"
        if not fila.get("json") and not _formato_no_json(url):
            return "declara API verificada y no devolvió JSON"
    if declarado == "manual_verificada" and codigo != 200:
        return f"declara portal verificado y respondió {codigo}"
    if declarado == "api_bloqueada" and fila.get("json"):
        return "declara API bloqueada pero ahora devuelve JSON: se puede promover"
    return None


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--solo-apis", action="store_true")
    args = ap.parse_args(argv)

    filas = comprobar(solo_apis=args.solo_apis)
    print("Comprobación del catálogo de fuentes")
    print("=" * 62)

    discrepancias = []
    for fila in sorted(filas, key=lambda f: f.get("id") or ""):
        codigo = fila.get("codigo")
        marca = "ok" if codigo == 200 else ("  " if codigo else "ER")
        extra = " json" if fila.get("json") else ""
        print(f"  [{marca}] {fila.get('id'):<24} {codigo}{extra}")
        problema = _discrepa(fila)
        if problema:
            discrepancias.append((fila.get("id"), problema))

    print()
    if discrepancias:
        print("El catálogo ya no describe la realidad:")
        for ident, problema in discrepancias:
            print(f"  - {ident}: {problema}")
        print()
        print("Actualiza `estado` en catalogo.yaml. No lo hace esta herramienta")
        print("porque decidir el estado exige mirar qué devolvió, no solo el código.")
        return 1

    print("Todo coincide con lo que declara el catálogo.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
