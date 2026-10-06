"""Construye `referencias.bib` desde Crossref, a partir de una lista de DOI.

**En una tesis de verdad este archivo no existe.** `referencias.bib` lo exporta
Better BibTeX desde Zotero y no se edita a mano.

Aquí existe para que ninguna referencia del ejemplo venga de la memoria de un
modelo: cada DOI se baja de Crossref, y si uno no existe el script falla en lugar
de inventar la entrada.

El perfil `medicina-fm` exige **Vancouver** (art. 13 del reglamento de la
facultad). El estilo lo aplica el CSL al renderizar, no el .bib: las entradas son
las mismas y lo que cambia es cómo se formatean.

Uso:
    uv run python codigo/00_referencias.py
"""
from __future__ import annotations

import pathlib
import urllib.error
import urllib.parse
import urllib.request

AQUI = pathlib.Path(__file__).resolve().parent.parent

CORREO = "rodasluis1308@gmail.com"
UA = f"tesis-sanmarcos/0.1 (mailto:{CORREO})"

DOIS = {
    "10.17843/rpmesp.2017.343.2622":
        "Herrera-Añazco et al.: autoconocimiento, adherencia y control de la "
        "hipertensión en el Perú. Es el antecedente nacional y da la magnitud "
        "del problema que este estudio explora de forma cualitativa.",
    "10.2147/ppa.s12326":
        "Tsiantou et al.: estudio cualitativo sobre adherencia al tratamiento "
        "antihipertensivo. Es el antecedente metodológicamente más cercano.",
    "10.1016/j.pec.2008.06.016":
        "Maguire et al.: creencias sobre el medicamento y adherencia en "
        "hipertensión. Sostiene la categoría de los modelos explicativos "
        "propios.",
    "10.2196/52998":
        "Squire et al.: cuántas entrevistas hacen falta para saturar los "
        "códigos. Se cita al discutir que en este estudio la saturación no se "
        "alcanzó.",
}


def bibtex_de(doi: str) -> str:
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
        "% referencias.bib del ejemplo medicina-cualitativo.",
        "%",
        "% GENERADO por codigo/00_referencias.py desde Crossref. En una tesis",
        "% real este archivo lo exporta Better BibTeX desde Zotero.",
        "%",
        "% El perfil medicina-fm pide Vancouver. El estilo lo aplica",
        "% plantillas/csl/vancouver.csl al renderizar; el .bib es el mismo.",
        "",
    ]
    for doi, por_que in DOIS.items():
        entrada = bibtex_de(doi)
        clave = entrada.split("{", 1)[1].split(",", 1)[0]
        print(f"  {clave:<26} {doi}")
        partes += [f"% {por_que}", entrada, ""]

    destino = AQUI / "referencias.bib"
    destino.write_text("\n".join(partes), encoding="utf8")
    print(f"\n  {len(DOIS)} entradas en {destino.name}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
