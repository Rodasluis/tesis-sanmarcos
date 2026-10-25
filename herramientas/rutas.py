"""El límite de 260 caracteres de Windows, en un solo sitio.

Los nombres de archivo que exige el art. 13 de la Directiva de originalidad son
largos por diseño: llevan apellidos, nombres, el título completo de la tesis y
el año. Con un título de los normales, el nombre solo ya pasa de 120 caracteres.
Basta con que el proyecto esté dos carpetas más abajo de lo habitual —y
`Downloads/Repositorio de…/` lo está— para cruzar el límite.

Cuando se cruza, Windows no dice que la ruta es larga: dice «el sistema no puede
encontrar la ruta especificada», que lleva a buscar el archivo que falta en vez
del carácter que sobra.
"""
from __future__ import annotations

import os
import pathlib

PREFIJO = "\\\\?\\"

# Windows admite rutas de hasta 259 caracteres más el terminador. El margen no
# se reduce: pasado eso, la API ancha con prefijo es la única salida.
MAXIMO = 260


def larga(ruta: pathlib.Path | str) -> str:
    """La ruta absoluta, con el prefijo que Windows necesita si hace falta.

    En cualquier otro sistema devuelve la ruta absoluta tal cual, así que se
    puede llamar sin condicionales.
    """
    absoluta = pathlib.Path(ruta).resolve()
    if os.name != "nt" or str(absoluta).startswith(PREFIJO):
        return str(absoluta)
    return PREFIJO + str(absoluta)


def se_pasa(ruta: pathlib.Path | str) -> bool:
    """Si esta ruta cruza el límite de Windows."""
    return os.name == "nt" and len(str(pathlib.Path(ruta).resolve())) >= MAXIMO


def mas_larga(raiz: pathlib.Path) -> tuple[pathlib.Path | None, int]:
    """La ruta más larga bajo `raiz`, con su longitud.

    Sirve para explicar un fallo ya ocurrido: cuando borrar o mover falla, lo
    primero que hay que saber es si había algo pasado de largo ahí dentro.
    """
    peor, largo = None, 0
    if not raiz.exists():
        return None, 0
    for actual in raiz.rglob("*"):
        n = len(str(actual.resolve()))
        if n > largo:
            peor, largo = actual, n
    return peor, largo
