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

    entorno = dict(os.environ)
    entorno["PATH"] = str(repo)          # un PATH donde no hay python
    r = subprocess.run(["git", "commit", "-m", "sin python"], cwd=str(repo),
                       capture_output=True, text=True, timeout=120, env=entorno)
    assert r.returncode == 0, (r.stdout + r.stderr)
