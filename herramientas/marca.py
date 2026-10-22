"""Prepara el escudo de la UNMSM para la carátula, desde el logo oficial.

El logo que publica la universidad trae el escudo y, debajo, la palabra «UNMSM»
con el nombre completo. Las carátulas de las tesis publicadas usan **solo el
escudo**: el nombre de la universidad va escrito como texto, con la tipografía
del documento, no como parte de una imagen.

Así que el escudo se recorta. Esta herramienta lo hace de forma reproducible, en
lugar de dejar un PNG recortado a mano del que nadie sepa de dónde salió:

1. Busca la primera banda horizontal completamente vacía por debajo del escudo.
   Ahí termina el blasón y empieza el texto del logo.
2. Recorta, ajusta al contenido y compone sobre blanco, porque la transparencia
   de un PNG no se ve igual en todos los visores de Word.

Uso:
    uv run python -m herramientas.marca
    uv run python -m herramientas.marca --comprobar
"""
from __future__ import annotations

import argparse
import pathlib
import sys

RAIZ = pathlib.Path(__file__).resolve().parent.parent
DESTINO = RAIZ / "plantillas" / "marca"

#: De dónde se lee el logo. El primero que exista.
ORIGENES = ("plantillas/marca/logo_unmsm.webp", "logo_unmsm.webp",
            "plantillas/marca/logo_unmsm.png")

ESCUDO = "escudo_unmsm.png"
LOGO = "logo_unmsm.png"

#: Un recorte más corto que esto no es el escudo: algo salió mal.
MINIMO_ALTO_PX = 300


def origen(raiz: pathlib.Path = RAIZ) -> pathlib.Path | None:
    for rel in ORIGENES:
        ruta = raiz / rel
        if ruta.exists():
            return ruta
    return None


def _primera_banda_vacia(im, desde: int) -> int | None:
    """La primera fila sin tinta por debajo de `desde`, o None."""
    ancho, alto = im.size
    px = im.load()
    for y in range(desde, alto, 2):
        if all(px[x, y][3] < 20 or sum(px[x, y][:3]) > 720
               for x in range(0, ancho, 3)):
            return y
    return None


def preparar(raiz: pathlib.Path = RAIZ) -> tuple[pathlib.Path, pathlib.Path]:
    """Escribe el escudo y el logo completo. Devuelve sus rutas."""
    from PIL import Image

    fuente = origen(raiz)
    if fuente is None:
        raise FileNotFoundError(
            "no se encontró el logo de la UNMSM. Se busca, en este orden: "
            + ", ".join(ORIGENES))

    im = Image.open(fuente).convert("RGBA")
    ancho, alto = im.size

    # El escudo ocupa la parte de arriba. La banda vacía que lo separa del
    # texto se busca a partir de la mitad: antes de ahí hay dibujo.
    corte = _primera_banda_vacia(im, desde=int(alto * 0.55)) or alto

    destino = raiz / "plantillas" / "marca"
    destino.mkdir(parents=True, exist_ok=True)

    def sobre_blanco(recorte):
        caja = recorte.getbbox()
        recorte = recorte.crop(caja) if caja else recorte
        fondo = Image.new("RGBA", recorte.size, (255, 255, 255, 255))
        fondo.alpha_composite(recorte)
        return fondo.convert("RGB")

    escudo = sobre_blanco(im.crop((0, 0, ancho, corte)))
    if escudo.size[1] < MINIMO_ALTO_PX:
        raise ValueError(
            f"el recorte del escudo quedó en {escudo.size[1]} píxeles de alto, "
            f"menos de {MINIMO_ALTO_PX}. El logo de origen no tiene la forma "
            f"esperada: revísalo antes de usarlo en una carátula")
    ruta_escudo = destino / ESCUDO
    escudo.save(ruta_escudo, "PNG", optimize=True)

    ruta_logo = destino / LOGO
    sobre_blanco(im.copy()).save(ruta_logo, "PNG", optimize=True)

    return ruta_escudo, ruta_logo


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--raiz", type=pathlib.Path, default=RAIZ)
    ap.add_argument("--comprobar", action="store_true",
                    help="solo dice si el escudo está listo")
    args = ap.parse_args(argv)

    escudo = args.raiz / "plantillas" / "marca" / ESCUDO
    if args.comprobar:
        if escudo.exists():
            print(f"escudo listo: {escudo}")
            return 0
        print(f"falta {escudo}. Genéralo con "
              f"`uv run python -m herramientas.marca`", file=sys.stderr)
        return 1

    try:
        ruta_escudo, ruta_logo = preparar(args.raiz)
    except (FileNotFoundError, ValueError) as e:
        print(f"ERROR {e}", file=sys.stderr)
        return 1
    print(f"  {ruta_escudo.relative_to(args.raiz)}")
    print(f"  {ruta_logo.relative_to(args.raiz)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
