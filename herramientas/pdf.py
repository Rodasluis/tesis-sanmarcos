"""Convierte a PDF el .docx ya generado, sin volver a maquetarlo.

## Por qué se convierte y no se renderiza aparte

La tesis se entrega en .docx —lo exige el art. 13 de la Directiva de
originalidad— y se deposita en Cybertesis **en PDF** —lo exige la RR N.°
06893-R-18—. Son dos trámites distintos sobre **el mismo documento**.

Si el PDF se generara por su cuenta, por ejemplo con LaTeX, saldría otro
documento: otra tipografía, otros saltos de página, otra numeración. Y entonces
el PDF que se deposita no sería el .docx que se evaluó. Por eso aquí se convierte
el .docx tal cual, con LibreOffice, que respeta la maquetación, el escudo de la
carátula y los saltos de sección que pone `docx_numeracion.py`.

## Si no hay LibreOffice

No pasa nada grave: **el .docx es el entregable normativo y se genera igual**.
El PDF queda pendiente y la herramienta dice cómo obtenerlo. Nunca bloquea.

Uso:
    uv run python -m herramientas.pdf entregables/TEXTO/*.docx
"""
from __future__ import annotations

import argparse
import os
import pathlib
import shutil
import subprocess
import sys

RAIZ = pathlib.Path(__file__).resolve().parent.parent

#: Dónde suele estar LibreOffice en cada sistema. Se prueban en orden y solo se
#: usa el que exista: no se inventa una ruta.
CANDIDATOS = (
    r"C:\Program Files\LibreOffice\program\soffice.exe",
    r"C:\Program Files (x86)\LibreOffice\program\soffice.exe",
    "/Applications/LibreOffice.app/Contents/MacOS/soffice",
    "/usr/bin/soffice",
    "/usr/bin/libreoffice",
    "/snap/bin/libreoffice",
)

COMO_INSTALARLO = (
    "Para obtener también el PDF hace falta LibreOffice, que es gratuito:\n"
    "  Windows  winget install TheDocumentFoundation.LibreOffice\n"
    "  macOS    brew install --cask libreoffice\n"
    "  Linux    sudo apt install libreoffice-writer\n"
    "Si ya lo tienes instalado en otra ruta, indícala en la variable de entorno "
    "SOFFICE."
)


class SinConversor(RuntimeError):
    """No hay con qué convertir a PDF. No es un error de la tesis."""


def buscar_soffice() -> str | None:
    """La ruta de LibreOffice, o None. Se comprueba que el archivo exista."""
    env = os.environ.get("SOFFICE")
    if env and pathlib.Path(env).exists():
        return env
    for nombre in ("soffice", "libreoffice"):
        hallado = shutil.which(nombre)
        if hallado:
            return hallado
    for ruta in CANDIDATOS:
        if pathlib.Path(ruta).exists():
            return ruta
    return None


def disponible() -> bool:
    return buscar_soffice() is not None


def convertir(docx: pathlib.Path, destino: pathlib.Path | None = None,
              tiempo_max: int = 300) -> pathlib.Path:
    """Convierte un .docx a PDF y devuelve la ruta del PDF.

    Lanza `SinConversor` si no hay LibreOffice, y `RuntimeError` si lo hay pero
    la conversión falla.
    """
    docx = pathlib.Path(docx)
    if not docx.exists():
        raise FileNotFoundError(f"no existe {docx}")

    soffice = buscar_soffice()
    if soffice is None:
        raise SinConversor(COMO_INSTALARLO)

    destino = pathlib.Path(destino) if destino else docx.parent
    destino.mkdir(parents=True, exist_ok=True)

    # LibreOffice escribe <nombre>.pdf en --outdir y no admite elegir el nombre.
    cmd = [soffice, "--headless", "--norestore", "--convert-to", "pdf:writer_pdf_Export",
           "--outdir", str(destino.resolve()), str(docx.resolve())]
    try:
        r = subprocess.run(cmd, capture_output=True, text=True, timeout=tiempo_max)
    except subprocess.TimeoutExpired as e:
        raise RuntimeError(
            f"LibreOffice no terminó en {tiempo_max} s. Suele pasar cuando hay "
            f"otra instancia abierta: ciérrala y vuelve a intentarlo.") from e

    pdf = destino / (docx.stem + ".pdf")
    if not pdf.exists():
        salida = (r.stderr or r.stdout or "").strip()[-400:]
        raise RuntimeError(
            f"LibreOffice terminó con código {r.returncode} y no escribió el PDF. "
            f"{salida}")
    return pdf


def convertir_varios(docxs: list[pathlib.Path],
                     destino: pathlib.Path | None = None
                     ) -> tuple[list[pathlib.Path], list[str]]:
    """Convierte varios y devuelve (pdfs generados, problemas).

    No se detiene en el primer fallo: si un documento no convierte, los demás
    sí, y el tesista ve todo lo que pasó de una vez.
    """
    hechos: list[pathlib.Path] = []
    problemas: list[str] = []
    for docx in docxs:
        try:
            hechos.append(convertir(docx, destino))
        except SinConversor as e:
            problemas.append(str(e))
            break          # falta la herramienta: no tiene sentido seguir
        except (OSError, RuntimeError) as e:
            problemas.append(f"{pathlib.Path(docx).name}: {e}")
    return hechos, problemas


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("archivos", nargs="*", type=pathlib.Path,
                    help=".docx a convertir")
    ap.add_argument("--destino", type=pathlib.Path)
    ap.add_argument("--comprobar", action="store_true",
                    help="solo dice si hay con qué convertir")
    args = ap.parse_args(argv)

    soffice = buscar_soffice()
    if args.comprobar:
        if soffice:
            print(f"LibreOffice: {soffice}")
            return 0
        print("No se encontró LibreOffice.\n" + COMO_INSTALARLO, file=sys.stderr)
        return 1

    if not args.archivos:
        ap.error("di qué archivos convertir, o usa --comprobar")

    hechos, problemas = convertir_varios(args.archivos, args.destino)
    for pdf in hechos:
        print(f"  {pdf}")
    for p in problemas:
        print(f"ERROR {p}", file=sys.stderr)
    return 1 if problemas else 0


if __name__ == "__main__":
    sys.exit(main())
