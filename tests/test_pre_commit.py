"""Prueba el hook de git de verdad: un repositorio temporal y un commit real.

No se puede probar dentro del repositorio de trabajo porque las reglas `deny`
impiden crear archivos en `datos/crudos/` —que es justamente lo que hay que
simular—, así que cada prueba levanta su propio repositorio.
"""
from __future__ import annotations

import os
import pathlib
import shutil
import subprocess
import sys

import pytest

RAIZ_REAL = pathlib.Path(__file__).resolve().parent.parent
PRE_COMMIT = RAIZ_REAL / ".githooks" / "pre-commit"

def _hay_sh() -> bool:
    """¿Puede git ejecutar un hook de shell?

    En Windows `sh` no suele estar en el PATH, pero Git for Windows trae el suyo
    y lo usa para los hooks. Así que mirar solo el PATH daría un falso negativo
    y las pruebas se saltarían justo donde más hacen falta.
    """
    if shutil.which("sh") or shutil.which("bash"):
        return True
    git = shutil.which("git")
    if not git:
        return False
    base = pathlib.Path(git).parent.parent
    return any((base / sub / "sh.exe").exists() for sub in ("bin", "usr/bin"))


requiere_sh = pytest.mark.skipif(not _hay_sh(), reason="git no puede ejecutar hooks de shell")


def _git(repo: pathlib.Path, *args: str) -> subprocess.CompletedProcess:
    return subprocess.run(["git", *args], cwd=str(repo), capture_output=True,
                          text=True, timeout=60)


@pytest.fixture
def repo(tmp_path: pathlib.Path) -> pathlib.Path:
    """Un repositorio git con el hook instalado y las herramientas disponibles."""
    _git(tmp_path, "init", "-q", "-b", "main")
    _git(tmp_path, "config", "user.email", "prueba@ejemplo.pe")
    _git(tmp_path, "config", "user.name", "Prueba")

    destino = tmp_path / ".githooks"
    destino.mkdir()
    shutil.copy2(PRE_COMMIT, destino / "pre-commit")
    (destino / "pre-commit").chmod(0o755)
    _git(tmp_path, "config", "core.hooksPath", ".githooks")

    # El hook importa `herramientas.datos_personales`, así que tiene que estar.
    shutil.copytree(RAIZ_REAL / "herramientas", tmp_path / "herramientas",
                    ignore=shutil.ignore_patterns("__pycache__"))
    return tmp_path


def _commit(repo: pathlib.Path, mensaje: str) -> subprocess.CompletedProcess:
    entorno = dict(os.environ)
    # El hook busca un intérprete; se le da el de las pruebas.
    entorno["PATH"] = str(pathlib.Path(sys.executable).parent) + os.pathsep + entorno["PATH"]
    entorno["PYTHONPATH"] = str(repo)
    return subprocess.run(["git", "commit", "-m", mensaje], cwd=str(repo),
                          capture_output=True, text=True, timeout=120, env=entorno)


@requiere_sh
def test_bloquea_un_commit_con_datos_crudos(repo):
    crudos = repo / "datos" / "crudos"
    crudos.mkdir(parents=True)
    (crudos / "entrevista01.txt").write_text("Participante: me llamo Ana.", encoding="utf8")
    _git(repo, "add", "-f", "datos/crudos/entrevista01.txt")

    r = _commit(repo, "intento subir datos crudos")
    assert r.returncode != 0, "el commit debería haberse detenido"
    salida = r.stdout + r.stderr
    assert "COMMIT DETENIDO" in salida
    assert "datos/crudos/" in salida


@requiere_sh
def test_deja_pasar_un_capitulo_normal(repo):
    capitulos = repo / "capitulos"
    capitulos.mkdir()
    (capitulos / "01_introduccion.qmd").write_text(
        "# Introducción\n\nEl gasto público regional creció en el periodo.\n",
        encoding="utf8")
    _git(repo, "add", "capitulos/01_introduccion.qmd")

    r = _commit(repo, "agrego la introduccion")
    assert r.returncode == 0, (r.stdout + r.stderr)


@requiere_sh
def test_advierte_pero_no_bloquea_un_posible_dato_personal(repo):
    """Un indicio no es una certeza: avisa y deja seguir."""
    datos = repo / "datos" / "procesados"
    datos.mkdir(parents=True)
    (datos / "muestra.csv").write_text("region,contacto\nLima,ana.torres@gmail.com\n",
                                       encoding="utf8")
    _git(repo, "add", "datos/procesados/muestra.csv")

    r = _commit(repo, "agrego la muestra")
    assert r.returncode == 0, "un indicio no debe bloquear el commit"
    salida = r.stdout + r.stderr
    assert "correo" in salida


@requiere_sh
def test_no_revienta_si_no_encuentra_python(repo, monkeypatch):
    """Sin intérprete el hook avisa y deja pasar; no deja al tesista encerrado."""
    capitulos = repo / "capitulos"
    capitulos.mkdir()
    (capitulos / "a.qmd").write_text("# A\n", encoding="utf8")
    _git(repo, "add", "capitulos/a.qmd")

    # Un PATH sin intérprete, pero **con** el shell: vaciarlo del todo deja a
    # git sin `sh` y entonces la prueba ya no comprueba lo que dice comprobar,
    # sino que git no puede lanzar el hook.
    shell = shutil.which("sh") or shutil.which("bash")
    entorno = dict(os.environ)
    entorno["PATH"] = os.pathsep.join([str(repo), str(pathlib.Path(shell).parent)])

    r = subprocess.run(["git", "commit", "-m", "sin python"], cwd=str(repo),
                       capture_output=True, text=True, timeout=120, env=entorno)
    assert r.returncode == 0, (r.stdout + r.stderr)


# --- nada personal en un repositorio publico -------------------------------

#: `tests/` queda fuera a proposito: sus archivos existen para contener correos
#: y datos falsos con los que se prueba el detector de datos personales.
NO_SE_REVISA = ("tests/",)

#: Marcadores de posicion que un README tiene que poder usar.
MARCADORES = ("tu-usuario", "usuario", "tuusuario", "ejemplo")


def _publicados(sufijos=(".py", ".md", ".yaml", ".yml")):
    import subprocess
    salida = subprocess.run(["git", "ls-files"], cwd=RAIZ_REAL, capture_output=True,
                            text=True, encoding="utf8").stdout
    for nombre in salida.splitlines():
        if not nombre or nombre.startswith(NO_SE_REVISA):
            continue
        if pathlib.Path(nombre).suffix not in sufijos:
            continue
        ruta = RAIZ_REAL / nombre
        if ruta.exists():
            yield nombre, ruta.read_text(encoding="utf8", errors="replace")


def test_ningun_correo_personal_incrustado():
    """El correo del tesista estaba en los dos ejemplos, como `mailto:` del
    «polite pool» de Crossref. En un repositorio publico MIT eso es su
    direccion expuesta a cualquier rastreador. Ahora sale de
    `CROSSREF_MAILTO`, y sin esa variable se usa la cola comun.
    """
    import re
    correo = re.compile(r"[\w.+-]+@(?!unmsm\.edu\.pe|ejemplo\.)[\w-]+\.[\w.]+")
    permitidos = {"noreply@anthropic.com"}
    hallados = [f"{n}: {m}" for n, txt in _publicados()
                for m in correo.findall(txt) if m not in permitidos]
    assert not hallados, f"correos personales en archivos publicados: {hallados}"


def test_ninguna_ruta_de_la_maquina_de_nadie():
    """Una ruta como la del equipo de alguien, en un archivo publicado, dice
    de quien es la maquina y que carpetas tiene. Aparecio en el plan de
    implementacion, con el nombre de una carpeta del tesista."""
    import re
    patron = re.compile(r"[Cc]:.Users.([A-Za-z0-9_.-]+)|/home/([a-z0-9_-]+)/")
    hallados = []
    for nombre, txt in _publicados():
        for a, b in patron.findall(txt):
            quien = a or b
            if quien.lower() not in MARCADORES:
                hallados.append(f"{nombre}: {quien}")
    assert not hallados, (
        f"rutas de una maquina concreta (usa un marcador como «tu-usuario»): "
        f"{hallados}")
