"""Construye `referencias.bib` desde Crossref, a partir de una lista de DOI.

**En una tesis de verdad este archivo no existe.** `referencias.bib` lo exporta
Better BibTeX desde Zotero, como dice CLAUDE.md, y no se edita a mano.

Aquí existe por una razón concreta: un ejemplo del repositorio no puede traer
referencias tecleadas de memoria. Cada entrada se baja de Crossref por su DOI, y
si un DOI no existe el script falla en lugar de inventar la entrada. Así el
ejemplo es coherente con el principio 2 y `verificar_referencias --con-red` lo
confirma contra la misma fuente.

Uso:
    uv run python codigo/00_referencias.py
"""
from __future__ import annotations

import os
import pathlib
import urllib.error
import urllib.parse
import urllib.request

AQUI = pathlib.Path(__file__).resolve().parent.parent

#: Crossref atiende mejor a quien se identifica —es su «polite pool»—, pero un
#: repositorio publico no puede llevar el correo de nadie incrustado. Pon el
#: tuyo en la variable de entorno si quieres esa cola:
#:     CROSSREF_MAILTO=tucorreo@ejemplo.pe uv run python codigo/00_referencias.py
#: Sin ella funciona igual, solo que en la cola comun.
CORREO = os.environ.get("CROSSREF_MAILTO", "").strip()
UA = f"tesis-sanmarcos/0.1 (mailto:{CORREO})" if CORREO else "tesis-sanmarcos/0.1"

#: Las fuentes de la tesis, cada una con por qué está. El orden es el de la
#: discusión del capítulo II, no alfabético.
DOIS = {
    "10.1111/j.1468-0297.2011.02420.x":
        "Czernich et al.: el hallazgo positivo de referencia para banda ancha "
        "y crecimiento en países de la OCDE.",
    "10.1016/j.econlet.2018.08.034":
        "Maurseth: evidencia en contra con datos de panel entre países. Es el "
        "antecedente más cercano a lo que encuentra esta tesis.",
    "10.1006/redy.1998.0016":
        "Yorukoglu: la paradoja de la productividad, que es el marco del "
        "problema.",
    "10.1257/jep.14.4.23":
        "Brynjolfsson y Hitt: por qué el efecto aparece al nivel de la empresa "
        "y se diluye en los agregados.",
    "10.18080/jtde.v12n4.1128":
        "Endres y Steula: revisión reciente, con banda ancha fija y móvil "
        "separadas.",
}

#: La base de datos. No tiene DOI, así que su entrada se escribe aquí: es la
#: ficha de un dataset público, no una referencia bibliográfica recordada.
DATASET = """\
@misc{bancomundial2026wdi,
  author       = {{Banco Mundial}},
  title        = {World Development Indicators},
  year         = {2026},
  howpublished = {Base de datos en línea},
  note         = {Indicadores SL.GDP.PCAP.EM.KD, IT.NET.USER.ZS,
                  SE.XPD.TOTL.GD.ZS, SL.UEM.TOTL.ZS y NY.GDP.PCAP.KD;
                  consultado mediante la API v2. Licencia CC BY 4.0},
  url          = {https://datos.bancomundial.org}
}
"""


def bibtex_de(doi: str) -> str:
    """Pide a Crossref el BibTeX canónico de un DOI, por negociación de contenido."""
    url = f"https://doi.org/{urllib.parse.quote(doi)}"
    peticion = urllib.request.Request(
        url, headers={"Accept": "application/x-bibtex", "User-Agent": UA})
    try:
        with urllib.request.urlopen(peticion, timeout=60) as r:
            return r.read().decode("utf8").strip()
    except urllib.error.HTTPError as e:
        if e.code == 404:
            raise RuntimeError(
                f"el DOI {doi} no existe. No se escribe una entrada inventada "
                f"en su lugar: revisa el DOI o quita la referencia.") from e
        raise


def main() -> int:
    partes = [
        "% referencias.bib del ejemplo economia-cuantitativo.",
        "%",
        "% GENERADO por codigo/00_referencias.py desde Crossref. En una tesis",
        "% real este archivo lo exporta Better BibTeX desde Zotero y no se",
        "% edita a mano. Aquí se genera para que ninguna entrada venga de la",
        "% memoria de un modelo: cada DOI se comprobó contra Crossref.",
        "",
    ]

    for doi, por_que in DOIS.items():
        entrada = bibtex_de(doi)
        clave = entrada.split("{", 1)[1].split(",", 1)[0]
        print(f"  {clave:<28} {doi}")
        partes += [f"% {por_que}", entrada, ""]

    partes += ["% La base de datos de la que salen todas las cifras.", DATASET]

    destino = AQUI / "referencias.bib"
    destino.write_text("\n".join(partes), encoding="utf8")
    print(f"\n  {len(DOIS) + 1} entradas en {destino.name}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
