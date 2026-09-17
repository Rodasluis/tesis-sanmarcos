"""Tablero HTML autocontenido con el estado del proyecto.

Un archivo que se abre con doble clic y responde tres preguntas: en qué etapa
voy, qué está bloqueando la entrega, y qué decidí hasta ahora.

Deliberadamente **sin gráficos**: los datos que hay son estados y cuentas, y una
cifra grande con su etiqueta se lee mejor que cualquier gráfico. Tampoco hay
dependencias: todo el CSS va en el archivo, que funciona sin conexión.

Los colores de estado nunca cargan el significado solos: cada uno viene con un
símbolo y una etiqueta, para que se entienda en impresión, en blanco y negro y
con daltonismo.

Uso:
    uv run python -m herramientas.tablero
    uv run python -m herramientas.tablero --abrir
"""
from __future__ import annotations

import argparse
import datetime as dt
import html
import json
import pathlib
import sys
import webbrowser

from herramientas.perfiles import ErrorDePerfil, cargar_de, perfil_activo
from herramientas.registrar_decision import ETAPAS

RAIZ = pathlib.Path(__file__).resolve().parent.parent

ESTADOS = {
    "bien":     {"color": "#0ca30c", "simbolo": "✓", "etiqueta": "en orden"},
    "atencion": {"color": "#fab219", "simbolo": "!", "etiqueta": "atención"},
    "serio":    {"color": "#ec835a", "simbolo": "▲", "etiqueta": "revisar"},
    "critico":  {"color": "#d03b3b", "simbolo": "✕", "etiqueta": "bloquea"},
    "neutro":   {"color": "#8b8a83", "simbolo": "·", "etiqueta": "sin datos"},
}

NOMBRES_ETAPA = {
    "iniciar": "Iniciar", "explorar-datos": "Explorar datos",
    "afinar-idea": "Afinar la idea", "literatura": "Literatura",
    "proyecto": "Proyecto", "analizar": "Analizar", "redactar": "Redactar",
    "jurado": "Jurado simulado", "verificar": "Verificar",
    "entregar": "Entregar", "sustentacion": "Sustentación",
}


def _decisiones(raiz: pathlib.Path) -> dict[str, dict]:
    salida: dict[str, dict] = {}
    for ruta in sorted((raiz / "decisiones").glob("*.json")):
        if ruta.name.startswith("_"):
            continue
        try:
            d = json.loads(ruta.read_text(encoding="utf8"))
        except (json.JSONDecodeError, OSError):
            continue
        if d.get("etapa"):
            salida[d["etapa"]] = d
    return salida


def _informes(raiz: pathlib.Path) -> dict[str, dict]:
    salida: dict[str, dict] = {}
    for ruta in sorted((raiz / "registro").glob("*.json")):
        try:
            d = json.loads(ruta.read_text(encoding="utf8"))
        except (json.JSONDecodeError, OSError):
            continue
        if "resumen" in d:
            salida[d.get("herramienta", ruta.stem)] = d
    return salida


def _estado_de_informe(resumen: dict[str, int]) -> str:
    if resumen.get("error"):
        return "critico"
    if resumen.get("aviso"):
        return "atencion"
    return "bien"


def _contar(raiz: pathlib.Path, patron: str) -> int:
    return sum(1 for p in raiz.glob(patron) if p.is_file() and p.name != ".gitkeep")


def recolectar(raiz: pathlib.Path = RAIZ) -> dict:
    pid = perfil_activo(raiz)
    perfil = None
    if pid:
        try:
            perfil = cargar_de(raiz, pid)
        except ErrorDePerfil:
            perfil = None

    decisiones = _decisiones(raiz)
    informes = _informes(raiz)

    etapas = []
    for etapa in ETAPAS:
        d = decisiones.get(etapa)
        etapas.append({
            "id": etapa,
            "nombre": NOMBRES_ETAPA.get(etapa, etapa),
            "decidida": bool(d),
            "momento": (d or {}).get("momento", ""),
            "eleccion": (d or {}).get("eleccion", ""),
            "preguntas_sin_responder": sum(
                1 for p in (d or {}).get("preguntas_comprension", [])
                if not (p.get("respuesta") or "").strip()),
        })

    alertas: list[dict] = []
    if perfil is None:
        alertas.append({
            "estado": "critico",
            "texto": "No hay perfil activo. Actívalo con <code>uv run python -m "
                     "herramientas.activar_perfil &lt;id&gt;</code>."})
    else:
        if not perfil.verificado:
            alertas.append({
                "estado": "atencion",
                "texto": f"El perfil <strong>{html.escape(perfil.id)}</strong> está en estado "
                         f"<code>{html.escape(perfil.estado)}</code>: necesita que tu asesor "
                         "confirme la estructura antes de <code>/proyecto</code>."})
        vig = perfil.get("vigencia_proyecto_meses")
        if isinstance(vig, int):
            alertas.append({
                "estado": "atencion",
                "texto": f"El proyecto de tu facultad caduca a los <strong>{vig} meses</strong> "
                         "de aprobado. Si vence sin informe final, se anula de oficio."})
        if (perfil.get("etica") or {}).get("comite_requerido") is True:
            alertas.append({
                "estado": "atencion",
                "texto": "Tu facultad exige aprobación de un <strong>Comité de Ética</strong> "
                         "antes de ejecutar el proyecto. Ese trámite toma tiempo."})

    bib = raiz / "referencias.bib"
    entradas = 0
    if bib.exists():
        entradas = bib.read_text(encoding="utf8", errors="replace").count("@")
    if entradas == 0:
        alertas.append({"estado": "critico",
                        "texto": "<code>referencias.bib</code> está vacío: ninguna cita "
                                 "puede verificarse."})

    return {
        "generado": dt.datetime.now(),
        "perfil": perfil,
        "etapas": etapas,
        "decididas": sum(1 for e in etapas if e["decidida"]),
        "informes": informes,
        "alertas": alertas,
        "cuentas": {
            "Capítulos": _contar(raiz, "capitulos/**/*.qmd"),
            "Referencias": entradas,
            "Resultados": _contar(raiz, "resultados/**/*"),
            "Decisiones": len(decisiones),
        },
    }


def _tile(valor: str, etiqueta: str, estado: str = "neutro", nota: str = "") -> str:
    e = ESTADOS[estado]
    nota_html = f'<p class="nota">{html.escape(nota)}</p>' if nota else ""
    return f"""      <div class="tile">
        <p class="valor" style="color:{e['color']}">{html.escape(valor)}</p>
        <p class="etiqueta">{html.escape(etiqueta)}</p>
        {nota_html}
      </div>"""


def _chip(estado: str) -> str:
    e = ESTADOS[estado]
    return (f'<span class="chip" style="--c:{e["color"]}">'
            f'<span class="sim">{e["simbolo"]}</span>{e["etiqueta"]}</span>')


def construir_html(datos: dict) -> str:
    perfil = datos["perfil"]
    total = len(datos["etapas"])
    hechas = datos["decididas"]

    tiles = [
        _tile(f"{hechas}/{total}", "etapas decididas",
              "bien" if hechas else "neutro"),
        _tile(str(datos["cuentas"]["Capítulos"]), "capítulos escritos",
              "bien" if datos["cuentas"]["Capítulos"] else "neutro"),
        _tile(str(datos["cuentas"]["Referencias"]), "referencias en Zotero",
              "bien" if datos["cuentas"]["Referencias"] else "critico"),
        _tile(str(datos["cuentas"]["Resultados"]), "archivos de resultados",
              "bien" if datos["cuentas"]["Resultados"] else "neutro"),
    ]

    filas_etapas = []
    for e in datos["etapas"]:
        estado = "bien" if e["decidida"] else "neutro"
        extra = ""
        if e["decidida"] and e["preguntas_sin_responder"]:
            estado = "atencion"
            extra = f" · {e['preguntas_sin_responder']} preguntas sin responder"
        eleccion = html.escape(e["eleccion"][:90]) if e["eleccion"] else "—"
        filas_etapas.append(
            f"<tr><td>{html.escape(e['nombre'])}</td>"
            f"<td>{_chip(estado)}</td>"
            f"<td>{eleccion}{html.escape(extra)}</td>"
            f"<td class='tenue'>{html.escape(e['momento'][:16])}</td></tr>")

    filas_informes = []
    for nombre, d in sorted(datos["informes"].items()):
        r = d.get("resumen", {})
        estado = _estado_de_informe(r)
        filas_informes.append(
            f"<tr><td>{html.escape(nombre)}</td>"
            f"<td>{_chip(estado)}</td>"
            f"<td>{r.get('error', 0)}</td><td>{r.get('aviso', 0)}</td>"
            f"<td class='tenue'>{html.escape(str(d.get('momento', ''))[:16])}</td></tr>")
    if not filas_informes:
        filas_informes.append(
            "<tr><td colspan='5' class='tenue'>Todavía no se ha ejecutado ninguna "
            "verificación. Usa <code>/verificar</code>.</td></tr>")

    alertas_html = "".join(
        f'<li>{_chip(a["estado"])} {a["texto"]}</li>' for a in datos["alertas"]
    ) or '<li>' + _chip("bien") + ' Sin alertas.</li>'

    if perfil is not None:
        cabecera_perfil = (f"{html.escape(perfil.get('facultad', ''))} · perfil "
                           f"<code>{html.escape(perfil.id)}</code> "
                           f"({html.escape(perfil.estado)})")
    else:
        cabecera_perfil = "sin perfil activo"

    return f"""<!doctype html>
<html lang="es">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Estado de la tesis</title>
<style>
  :root {{
    color-scheme: light;
    --surface: #fcfcfb;
    --panel: #ffffff;
    --borde: #e4e3de;
    --ink: #0b0b0b;
    --ink-2: #52514e;
    --ink-3: #8b8a83;
  }}
  @media (prefers-color-scheme: dark) {{
    :root:not([data-theme="light"]) {{
      color-scheme: dark;
      --surface: #1a1a19;
      --panel: #232321;
      --borde: #3a3a37;
      --ink: #ffffff;
      --ink-2: #c3c2b7;
      --ink-3: #8b8a83;
    }}
  }}
  :root[data-theme="dark"] {{
    color-scheme: dark;
    --surface: #1a1a19; --panel: #232321; --borde: #3a3a37;
    --ink: #ffffff; --ink-2: #c3c2b7; --ink-3: #8b8a83;
  }}
  * {{ box-sizing: border-box; }}
  body {{
    margin: 0; background: var(--surface); color: var(--ink);
    font: 16px/1.55 system-ui, -apple-system, "Segoe UI", Roboto, sans-serif;
    padding: 32px 16px 64px;
  }}
  .envoltorio {{ max-width: 980px; margin: 0 auto; }}
  h1 {{ font-size: 1.6rem; margin: 0 0 4px; letter-spacing: -0.01em; }}
  .sub {{ color: var(--ink-2); margin: 0 0 28px; font-size: 0.95rem; }}
  h2 {{ font-size: 1.05rem; margin: 32px 0 12px; letter-spacing: -0.005em; }}
  .tiles {{ display: grid; gap: 12px;
            grid-template-columns: repeat(auto-fit, minmax(150px, 1fr)); }}
  .tile {{ background: var(--panel); border: 1px solid var(--borde);
           border-radius: 10px; padding: 16px; }}
  .valor {{ font-size: 2rem; font-weight: 650; margin: 0;
            letter-spacing: -0.02em; font-variant-numeric: tabular-nums; }}
  .etiqueta {{ margin: 2px 0 0; color: var(--ink-2); font-size: 0.85rem; }}
  .nota {{ margin: 6px 0 0; color: var(--ink-3); font-size: 0.78rem; }}
  table {{ width: 100%; border-collapse: collapse; background: var(--panel);
           border: 1px solid var(--borde); border-radius: 10px; overflow: hidden; }}
  th, td {{ text-align: left; padding: 9px 12px; border-bottom: 1px solid var(--borde);
            font-size: 0.9rem; vertical-align: top; }}
  th {{ color: var(--ink-2); font-weight: 600; font-size: 0.78rem;
        text-transform: uppercase; letter-spacing: 0.04em; }}
  tr:last-child td {{ border-bottom: none; }}
  .tenue {{ color: var(--ink-3); }}
  .chip {{ display: inline-flex; align-items: center; gap: 5px; white-space: nowrap;
           font-size: 0.78rem; color: var(--ink-2); }}
  .chip .sim {{ display: inline-grid; place-items: center; width: 17px; height: 17px;
                border-radius: 50%; background: var(--c); color: #fff;
                font-size: 0.7rem; font-weight: 700; }}
  ul.alertas {{ list-style: none; padding: 0; margin: 0; display: grid; gap: 10px; }}
  ul.alertas li {{ background: var(--panel); border: 1px solid var(--borde);
                   border-radius: 10px; padding: 12px 14px; font-size: 0.9rem; }}
  code {{ background: color-mix(in srgb, var(--ink) 8%, transparent);
          padding: 1px 5px; border-radius: 4px; font-size: 0.85em; }}
  footer {{ margin-top: 40px; color: var(--ink-3); font-size: 0.8rem; }}
  @media (max-width: 560px) {{ .valor {{ font-size: 1.6rem; }} }}
</style>
</head>
<body>
<div class="envoltorio">
  <h1>Estado de la tesis</h1>
  <p class="sub">{cabecera_perfil} · generado el
     {datos['generado'].strftime('%d/%m/%Y %H:%M')}</p>

  <div class="tiles">
{chr(10).join(tiles)}
  </div>

  <h2>Qué necesita tu atención</h2>
  <ul class="alertas">{alertas_html}</ul>

  <h2>Etapas y decisiones</h2>
  <table>
    <thead><tr><th>Etapa</th><th>Estado</th><th>Qué se decidió</th><th>Cuándo</th></tr></thead>
    <tbody>{''.join(filas_etapas)}</tbody>
  </table>

  <h2>Verificaciones</h2>
  <table>
    <thead><tr><th>Herramienta</th><th>Estado</th><th>Errores</th><th>Avisos</th><th>Ejecutada</th></tr></thead>
    <tbody>{''.join(filas_informes)}</tbody>
  </table>

  <footer>
    Este tablero resume lo que las herramientas encontraron. No certifica nada:
    la revisión del asesor y del jurado sigue siendo necesaria. El porcentaje de
    similitud oficial lo calcula la plataforma PIDS de la universidad, no este
    repositorio.
  </footer>
</div>
</body>
</html>
"""


def generar(raiz: pathlib.Path = RAIZ, destino: pathlib.Path | None = None) -> pathlib.Path:
    datos = recolectar(raiz)
    destino = destino or (raiz / "registro" / "tablero.html")
    destino.parent.mkdir(parents=True, exist_ok=True)
    destino.write_text(construir_html(datos), encoding="utf8")
    return destino


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--salida", type=pathlib.Path)
    ap.add_argument("--abrir", action="store_true", help="lo abre en el navegador")
    args = ap.parse_args(argv)

    ruta = generar(destino=args.salida)
    print(f"OK  tablero generado: {ruta}")
    if args.abrir:
        webbrowser.open(ruta.resolve().as_uri())
    return 0


if __name__ == "__main__":
    sys.exit(main())
