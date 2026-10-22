"""Monta un ejemplo de `ejemplos/` como proyecto ejecutable y verificable.

## Por qué hace falta

Las herramientas del repositorio trabajan sobre una **raíz de proyecto**: ahí
buscan `perfiles/`, `capitulos/`, `resultados/`, `decisiones/` y
`referencias.bib`. Un tesista real trabaja en la raíz del repositorio, así que
todo está donde debe.

Un ejemplo, en cambio, tiene su propio `capitulos/` pero no sus propios
`perfiles/`: duplicar los 21 perfiles dentro de cada ejemplo haría que se
quedaran viejos en cuanto cambiara el original, y un perfil desactualizado en un
ejemplo es peor que no tener ejemplo.

Así que el ejemplo guarda solo lo suyo, y esta herramienta lo monta: copia el
contenido del ejemplo a un directorio de trabajo y le añade, desde el
repositorio, el perfil que usa con toda su cadena de herencia, su plantilla .docx
y los CSL. El resultado es un proyecto completo que `verificar_todo.py` y Quarto
pueden tratar como cualquier otro.

Uso:
    uv run python -m herramientas.preparar_ejemplo economia-cuantitativo
    uv run python -m herramientas.preparar_ejemplo --todos --destino build/
"""
from __future__ import annotations

import argparse
import pathlib
import shutil
import sys

from herramientas.perfiles import ErrorDePerfil, cargar, perfil_activo

RAIZ = pathlib.Path(__file__).resolve().parent.parent
EJEMPLOS = RAIZ / "ejemplos"
DESTINO_POR_DEFECTO = RAIZ / ".ejemplos-montados"

#: Lo que se copia del ejemplo. Lo que no está aquí no viaja: `datos/crudos/`
#: se incluye porque sin él el análisis no se puede rehacer, pero ningún ejemplo
#: lleva datos personales y hay una prueba que lo comprueba.
DEL_EJEMPLO = ("capitulos", "proyecto", "codigo", "datos", "decisiones",
               "resultados", "entregables", "referencias.bib", ".perfil-activo",
               ".enfoque", "README.md")


def ejemplos_disponibles() -> list[str]:
    if not EJEMPLOS.exists():
        return []
    return sorted(d.name for d in EJEMPLOS.iterdir()
                  if d.is_dir() and (d / ".perfil-activo").exists())


def _cadena_de_perfiles(pid: str) -> list[str]:
    """El perfil y todos sus ancestros, para copiar solo lo necesario."""
    cadena, visto = [], set()
    actual: str | None = pid
    while actual and actual not in visto:
        visto.add(actual)
        cadena.append(actual)
        ruta = RAIZ / "perfiles" / f"{actual}.yaml"
        if not ruta.exists():
            raise ErrorDePerfil(f"el perfil {actual!r} no existe en perfiles/")
        import yaml
        actual = (yaml.safe_load(ruta.read_text(encoding="utf8")) or {}).get("hereda_de")
    return cadena


def preparar(nombre: str, destino_base: pathlib.Path = DESTINO_POR_DEFECTO,
             limpiar: bool = True) -> pathlib.Path:
    """Monta el ejemplo `nombre` y devuelve la raíz del proyecto resultante."""
    origen = EJEMPLOS / nombre
    if not origen.is_dir():
        raise FileNotFoundError(
            f"no hay un ejemplo llamado {nombre!r}. "
            f"Disponibles: {', '.join(ejemplos_disponibles()) or 'ninguno'}")

    pid = perfil_activo(origen)
    if not pid:
        raise ErrorDePerfil(
            f"{nombre} no declara perfil activo: falta el archivo .perfil-activo")

    destino = destino_base / nombre
    if limpiar and destino.exists():
        try:
            shutil.rmtree(destino)
        except OSError as e:
            # En Windows basta con tener una terminal abierta dentro del
            # directorio para que el borrado falle a medias. Si eso pasa sin
            # avisar, queda un árbol incompleto que parece montado y no lo
            # está: el render dice «no hay archivos de entrada» y nadie sabe
            # por qué.
            raise RuntimeError(
                f"no se pudo limpiar {destino}: {e}\n"
                f"Algo lo tiene abierto —una terminal dentro de la carpeta, un "
                f"editor, un .docx—. Ciérralo y vuelve a intentarlo, o monta en "
                f"otro sitio con --destino.") from e
    destino.mkdir(parents=True, exist_ok=True)

    # 1. Lo propio del ejemplo.
    for parte in DEL_EJEMPLO:
        fuente = origen / parte
        if not fuente.exists():
            continue
        if fuente.is_dir():
            shutil.copytree(fuente, destino / parte, dirs_exist_ok=True)
        else:
            shutil.copy2(fuente, destino / parte)

    # 2. El perfil con su cadena de herencia, desde el repositorio.
    (destino / "perfiles").mkdir(exist_ok=True)
    cadena = _cadena_de_perfiles(pid)
    for ancestro in cadena:
        shutil.copy2(RAIZ / "perfiles" / f"{ancestro}.yaml",
                     destino / "perfiles" / f"{ancestro}.yaml")
    esquema = RAIZ / "perfiles" / "_esquema.yaml"
    if esquema.exists():
        shutil.copy2(esquema, destino / "perfiles" / "_esquema.yaml")

    # 3. La plantilla del perfil y los CSL.
    for sub in (pid, "csl", "marca"):
        fuente = RAIZ / "plantillas" / sub
        if fuente.is_dir():
            shutil.copytree(fuente, destino / "plantillas" / sub, dirs_exist_ok=True)

    # 4. Los archivos a los que apuntan los perfiles de toda la cadena: la
    #    norma que citan y su esquema de facto. `verificar_perfil` comprueba que
    #    esos archivos existan en disco, así que sin copiarlos el ejemplo
    #    montado reportaría errores que el repositorio no tiene.
    for ancestro in cadena:
        perfil = cargar(ancestro, dir_perfiles=destino / "perfiles", raiz=destino,
                        validar=False)
        referenciados = [
            (perfil.datos.get("fuente") or {}).get("archivo_local"),
            perfil.datos.get("esquema_de_facto"),
        ]
        for relativo in referenciados:
            if not relativo or not (RAIZ / relativo).exists():
                continue
            (destino / relativo).parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(RAIZ / relativo, destino / relativo)

    # 5. `_quarto.yml` se genera desde el perfil, nunca a mano.
    from herramientas import activar_perfil
    activar_perfil.activar(pid, raiz=destino)

    (destino / "registro").mkdir(exist_ok=True)
    return destino


#: Tamaño por debajo del cual un .docx está vacío de contenido real. Un .docx
#: mínimo con la plantilla y ningún texto ronda los 11 KB.
MINIMO_DOCX = 10_000


def comprobar_render(nombre: str, destino_base: pathlib.Path) -> list[str]:
    """¿Se renderizó un .docx por cada capítulo, y tiene contenido?

    Quarto puede terminar con código 0 habiendo fallado un documento, así que
    después de renderizar hay que mirar los archivos. Un .docx que existe pero
    pesa lo mismo que la plantilla vacía es un render que no escribió nada.
    """
    raiz = destino_base / nombre
    capitulos = sorted((raiz / "capitulos").glob("*.qmd"))
    render = raiz / "entregables" / "_render" / "capitulos"
    problemas = []

    if not capitulos:
        return [f"{nombre}: no hay capítulos en el ejemplo montado"]

    for qmd in capitulos:
        docx = render / f"{qmd.stem}.docx"
        if not docx.exists():
            problemas.append(f"{nombre}: falta {docx.relative_to(raiz)}")
        elif docx.stat().st_size < MINIMO_DOCX:
            problemas.append(
                f"{nombre}: {docx.name} pesa {docx.stat().st_size} bytes, menos que "
                f"un .docx vacío ({MINIMO_DOCX}). El render no escribió el contenido")
    return problemas


def comprobar_entregables(nombre: str, destino_base: pathlib.Path) -> list[str]:
    """¿Salieron los cuatro entregables, y llevan el escudo en la carátula?

    Son cuatro porque son dos documentos —proyecto de tesis y tesis— en dos
    formatos: .docx para la evaluación de originalidad (art. 13) y PDF para el
    depósito en Cybertesis (RR N.° 06893-R-18).

    Lo del escudo se comprueba aparte porque es el fallo que no avisa: el .docx
    se abre, dice que tiene una imagen, y la primera página sale en blanco.
    """
    import docx

    raiz = destino_base / nombre / "entregables"
    problemas: list[str] = []

    esperados = {
        "proyecto .docx": list(raiz.glob("PROYECTO/*.docx")),
        "proyecto PDF": list(raiz.glob("PROYECTO/*.pdf")),
        "tesis .docx": list(raiz.glob("TEXTO/*.docx")),
        "tesis PDF": list(raiz.glob("TEXTO/*.pdf")),
    }
    for etiqueta, hallados in esperados.items():
        if not hallados:
            problemas.append(f"{nombre}: no se generó el {etiqueta}")

    for patron in ("PROYECTO/*.docx", "TEXTO/*Desarrollo*.docx"):
        for archivo in raiz.glob(patron):
            doc = docx.Document(str(archivo))
            if not doc.paragraphs:
                problemas.append(f"{nombre}: {archivo.name} salió vacío")
            elif "<w:drawing" not in doc.paragraphs[0]._p.xml:
                problemas.append(
                    f"{nombre}: {archivo.name} no lleva el escudo en la "
                    f"primera página")
    return problemas


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("nombre", nargs="?", help="ejemplo a montar")
    ap.add_argument("--todos", action="store_true")
    ap.add_argument("--listar", action="store_true")
    ap.add_argument("--comprobar-render", action="store_true",
                    help="no monta nada: revisa los .docx ya renderizados")
    ap.add_argument("--comprobar-entregables", action="store_true",
                    help="revisa que estén los cuatro entregables y el escudo")
    ap.add_argument("--destino", type=pathlib.Path, default=DESTINO_POR_DEFECTO)
    args = ap.parse_args(argv)

    disponibles = ejemplos_disponibles()
    if args.listar:
        for nombre in disponibles:
            print(f"  {nombre}  (perfil {perfil_activo(EJEMPLOS / nombre)})")
        return 0

    if args.comprobar_entregables:
        objetivos = [args.nombre] if args.nombre else disponibles
        problemas = [p for n in objetivos
                     for p in comprobar_entregables(n, args.destino)]
        for p in problemas:
            print(f"ERROR {p}", file=sys.stderr)
        if problemas:
            return 1
        for nombre in objetivos:
            print(f"  {nombre}: proyecto y tesis, en .docx y PDF, con escudo")
        return 0

    if args.comprobar_render:
        objetivos = [args.nombre] if args.nombre else disponibles
        problemas = [p for n in objetivos for p in comprobar_render(n, args.destino)]
        for p in problemas:
            print(f"ERROR {p}", file=sys.stderr)
        if problemas:
            return 1
        for nombre in objetivos:
            cuantos = len(list((args.destino / nombre / "capitulos").glob("*.qmd")))
            print(f"  {nombre}: {cuantos} capítulos renderizados a .docx")
        return 0

    objetivos = disponibles if args.todos else ([args.nombre] if args.nombre else [])
    if not objetivos:
        ap.error("di qué ejemplo montar, o usa --todos o --listar")

    for nombre in objetivos:
        try:
            destino = preparar(nombre, args.destino)
        except (FileNotFoundError, ErrorDePerfil) as e:
            print(f"ERROR en {nombre}: {e}", file=sys.stderr)
            return 1
        print(f"  {nombre} montado en {destino}")

    print("\nPara verificarlo:")
    print(f"  uv run python -m herramientas.verificar_todo --raiz "
          f"{args.destino / objetivos[0]}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
