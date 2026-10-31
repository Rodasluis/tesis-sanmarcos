"""Detecta datos personales antes de que salgan del equipo del tesista.

El principio 8 de CLAUDE.md dice que los datos personales se anonimizan antes de
salir de `datos/crudos/` y nunca se suben al repositorio remoto. Un `.gitignore`
cubre lo previsible; esto cubre el descuido: la transcripción que alguien copió a
`capitulos/`, el Excel con DNI que acabó en `datos/procesados/`.

Lo que busca son **indicios**, no certezas. Un número de ocho dígitos puede ser
un DNI o puede ser un monto; por eso el pre-commit distingue entre lo que
bloquea (rutas que nunca deben subirse) y lo que advierte (patrones que podrían
ser datos personales).

Marco legal: Ley N.° 29733 y su reglamento, DS N.° 016-2024-JUS.
"""
from __future__ import annotations

import pathlib
import re
from dataclasses import dataclass

#: Rutas que nunca deben llegar al repositorio remoto.
RUTAS_PROHIBIDAS = (
    "datos/crudos/",
    "entregables/TEXTO/",
    "entregables/DOCUMENTO/",
    ".env",
)

#: Extensiones que tiene sentido inspeccionar por dentro.
TEXTO = {".md", ".qmd", ".txt", ".csv", ".tsv", ".json", ".yaml", ".yml",
         ".py", ".r", ".sql", ".vtt", ".srt"}

#: Un DNI peruano son 8 dígitos. Se exige que esté suelto y acompañado de una
#: palabra que lo delate, para no marcar cualquier cifra de ocho dígitos.
RE_DNI = re.compile(
    r"(?:\b(?:dni|d\.n\.i\.?|documento de identidad|c[eé]dula)\b[^\n]{0,40}?(?<!\d)(\d{8})(?!\d)"
    r"|(?<!\d)(\d{8})(?!\d)[^\n]{0,20}?\b(?:dni|d\.n\.i\.?)\b)", re.I)

#: Un dominio termina en letras. Sin esa exigencia, `hyperframes@0.8.222`
#: —una versión fijada de un paquete— se denunciaba como correo personal, y
#: con ella se denunciaría cualquier `paquete@1.2.3` que el tesista escriba.
RE_CORREO = re.compile(r"\b[\w.+-]+@[\w-]+(?:\.[\w-]+)*\.[A-Za-z]{2,}\b")
RE_TELEFONO = re.compile(r"(?<!\d)(?:\+51\s?)?9\d{8}(?!\d)")
#: Nombres de archivo que suelen acompañar a datos sin anonimizar.
RE_NOMBRE_ARCHIVO = re.compile(
    r"(padr[oó]n|nominal|matr[ií]cula|participantes?|entrevistad|consentimiento|"
    r"transcripci[oó]n|datos[_-]?personales|identificad)", re.I)

#: Correos que no son de una persona concreta.
CORREOS_INOCUOS = re.compile(
    r"(noreply|no-reply|ejemplo|example|correo@|usuario@|tu-correo|"
    r"@unmsm\.edu\.pe$)", re.I)


@dataclass
class Indicio:
    nivel: str          # "bloquea" | "advierte"
    motivo: str
    archivo: str
    linea: int | None = None
    muestra: str = ""


def _es_ruta_prohibida(rel: str) -> str | None:
    normal = rel.replace("\\", "/")
    for prohibida in RUTAS_PROHIBIDAS:
        if normal == prohibida.rstrip("/") or normal.startswith(prohibida):
            return prohibida
    if normal.startswith(".env"):
        return ".env"
    return None


def revisar_ruta(rel: str) -> list[Indicio]:
    """Indicios que surgen del nombre del archivo, sin abrirlo."""
    salida: list[Indicio] = []
    prohibida = _es_ruta_prohibida(rel)
    if prohibida:
        salida.append(Indicio(
            "bloquea",
            f"está bajo `{prohibida}`, que nunca debe subirse al repositorio remoto",
            rel))
        return salida
    if RE_NOMBRE_ARCHIVO.search(pathlib.PurePath(rel).name):
        salida.append(Indicio(
            "advierte",
            "el nombre del archivo sugiere que contiene datos de personas",
            rel))
    return salida


#: Columnas que delatan una tabla de personas identificables.
COLUMNAS_SENSIBLES = {
    "dni", "documento", "nro_documento", "num_documento", "cedula",
    "nombre", "nombres", "apellido", "apellidos", "nombre_completo",
    "telefono", "celular", "correo", "email", "direccion", "domicilio",
    "fecha_nacimiento", "codigo_estudiante", "codigo_alumno",
}


def _columnas_sensibles(primera_linea: str) -> list[str]:
    """Columnas con nombre sensible en la cabecera de un CSV o TSV.

    Va aparte de la búsqueda por línea porque en una tabla el nombre de la
    columna y el dato están en líneas distintas: buscar «dni» junto a ocho
    dígitos no encuentra el caso más común, que es una hoja de participantes.
    """
    separador = "\t" if primera_linea.count("\t") > primera_linea.count(",") else ","
    encontradas = []
    for celda in primera_linea.split(separador):
        nombre = re.sub(r"[^a-z0-9_]", "", celda.strip().strip('"').lower().replace(" ", "_"))
        if nombre in COLUMNAS_SENSIBLES:
            encontradas.append(nombre)
    return encontradas


def revisar_contenido(rel: str, texto: str, max_indicios: int = 5) -> list[Indicio]:
    """Indicios dentro del texto de un archivo."""
    salida: list[Indicio] = []

    lineas = texto.splitlines()
    if lineas and pathlib.PurePath(rel).suffix.lower() in {".csv", ".tsv"}:
        columnas = _columnas_sensibles(lineas[0])
        if columnas:
            salida.append(Indicio(
                "advierte",
                "es una tabla con columnas de datos personales: "
                + ", ".join(columnas[:5]),
                rel, 1))

    for num, linea in enumerate(texto.splitlines(), 1):
        if len(salida) >= max_indicios:
            break

        m = RE_DNI.search(linea)
        if m:
            numero = m.group(1) or m.group(2) or ""
            salida.append(Indicio("advierte", "parece un número de DNI", rel, num,
                                  numero[:3] + "*****"))
            continue

        for m in RE_CORREO.finditer(linea):
            correo = m.group(0)
            if CORREOS_INOCUOS.search(correo):
                continue
            salida.append(Indicio("advierte", "hay una dirección de correo personal",
                                  rel, num, correo.split("@")[0][:3] + "***@***"))
            break

        m = RE_TELEFONO.search(linea)
        if m:
            salida.append(Indicio("advierte", "parece un número de teléfono móvil",
                                  rel, num, m.group(0)[:3] + "******"))
    return salida


def revisar_archivo(ruta: pathlib.Path, rel: str) -> list[Indicio]:
    indicios = revisar_ruta(rel)
    if any(i.nivel == "bloquea" for i in indicios):
        return indicios
    if ruta.suffix.lower() not in TEXTO:
        return indicios
    try:
        texto = ruta.read_text(encoding="utf8", errors="replace")
    except OSError:
        return indicios
    if len(texto) > 2_000_000:
        texto = texto[:2_000_000]
    return indicios + revisar_contenido(rel, texto)


def revisar(rutas: list[tuple[pathlib.Path, str]]) -> list[Indicio]:
    """Revisa una lista de (ruta absoluta, ruta relativa)."""
    salida: list[Indicio] = []
    for absoluta, rel in rutas:
        salida.extend(revisar_archivo(absoluta, rel))
    return salida


def hay_bloqueantes(indicios: list[Indicio]) -> bool:
    return any(i.nivel == "bloquea" for i in indicios)


# -- uso desde el hook de git -----------------------------------------------

def archivos_en_staging(raiz: pathlib.Path) -> list[tuple[pathlib.Path, str]]:
    """Los archivos que entrarían en el commit."""
    import subprocess
    try:
        r = subprocess.run(
            ["git", "diff", "--cached", "--name-only", "--diff-filter=ACMR"],
            capture_output=True, text=True, cwd=str(raiz), timeout=30)
    except (OSError, subprocess.SubprocessError):
        return []
    if r.returncode != 0:
        return []
    salida: list[tuple[pathlib.Path, str]] = []
    for linea in r.stdout.splitlines():
        rel = linea.strip()
        if not rel:
            continue
        salida.append((raiz / rel, rel))
    return salida


def informar(indicios: list[Indicio]) -> str:
    if not indicios:
        return "Sin indicios de datos personales en lo que vas a subir."

    bloquean = [i for i in indicios if i.nivel == "bloquea"]
    advierten = [i for i in indicios if i.nivel == "advierte"]
    lineas: list[str] = []

    if bloquean:
        lineas += ["", "COMMIT DETENIDO — hay archivos que no deben subirse:", ""]
        for i in bloquean:
            lineas.append(f"  {i.archivo}")
            lineas.append(f"      {i.motivo}")
        lineas += [
            "",
            "Quítalos del commit con:",
            "    git restore --staged <archivo>",
            "",
            "Si de verdad tienen que estar en el repositorio, revisa antes que no",
            "contengan datos de personas identificables (Ley N.° 29733).",
        ]

    if advierten:
        lineas += ["", f"Revisa esto antes de subirlo ({len(advierten)} indicios):", ""]
        for i in advierten[:15]:
            donde = f"{i.archivo}:{i.linea}" if i.linea else i.archivo
            muestra = f"  ({i.muestra})" if i.muestra else ""
            lineas.append(f"  {donde} — {i.motivo}{muestra}")
        if len(advierten) > 15:
            lineas.append(f"  … y {len(advierten) - 15} más")
        lineas += [
            "",
            "Son indicios, no certezas: un número de ocho dígitos puede ser un DNI",
            "o un monto. Si son datos de participantes, anonimízalos antes de subir.",
        ]
        if not bloquean:
            lineas += ["", "El commit continúa: esto es un aviso, no un bloqueo."]

    return "\n".join(lineas)


#: Código de salida cuando hay algo que NO debe subirse.
#:
#: Es un número poco común a propósito. El hook de git solo detiene el commit
#: con este código exacto: cualquier otro fallo —un intérprete que no arranca,
#: un import roto— deja pasar el commit con un aviso. Si usáramos el 1, que es
#: lo que devuelve Python ante cualquier excepción, un error nuestro dejaría al
#: tesista sin poder commitear y sin entender por qué.
SALIDA_BLOQUEA = 9


def main(argv: list[str] | None = None) -> int:
    import argparse

    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--staged", action="store_true",
                    help="revisa lo que está en el área de preparación de git")
    ap.add_argument("rutas", nargs="*", help="archivos concretos a revisar")
    ap.add_argument("--raiz", type=pathlib.Path,
                    default=pathlib.Path(__file__).resolve().parent.parent)
    args = ap.parse_args(argv)

    if args.staged:
        objetivos = archivos_en_staging(args.raiz)
    else:
        objetivos = [(pathlib.Path(r), r) for r in args.rutas]

    if not objetivos:
        print("No hay archivos que revisar.")
        return 0

    indicios = revisar(objetivos)
    print(informar(indicios))
    return SALIDA_BLOQUEA if hay_bloqueantes(indicios) else 0


if __name__ == "__main__":
    raise SystemExit(main())
