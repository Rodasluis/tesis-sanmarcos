"""El límite de 260 caracteres de Windows.

No es una rareza del equipo de nadie: el ejemplo montado del repositorio llega
a 261 caracteres, uno por encima, porque los nombres que exige el art. 13 de la
Directiva de originalidad llevan apellidos, nombres, el título entero y el año.
"""
from __future__ import annotations

import os
import pathlib

import pytest

from herramientas import rutas


def test_larga_devuelve_una_ruta_absoluta():
    assert pathlib.Path(rutas.larga("herramientas")).is_absolute()


@pytest.mark.skipif(os.name != "nt", reason="el prefijo solo existe en Windows")
def test_en_windows_antepone_el_prefijo():
    assert rutas.larga("herramientas").startswith(rutas.PREFIJO)


@pytest.mark.skipif(os.name != "nt", reason="el prefijo solo existe en Windows")
def test_no_lo_antepone_dos_veces():
    una = rutas.larga("herramientas")
    assert rutas.larga(una) == una


@pytest.mark.skipif(os.name == "nt", reason="fuera de Windows no hay prefijo")
def test_fuera_de_windows_no_toca_nada():
    assert not rutas.larga("herramientas").startswith("\\")


def test_mas_larga_encuentra_la_peor(tmp_path):
    (tmp_path / "corto.txt").write_text("a", encoding="utf8")
    hondo = tmp_path / "una" / "carpeta" / "bastante" / "honda"
    hondo.mkdir(parents=True)
    peor_esperado = hondo / "un nombre de archivo deliberadamente largo.txt"
    peor_esperado.write_text("a", encoding="utf8")

    peor, largo = rutas.mas_larga(tmp_path)
    assert peor == peor_esperado
    assert largo == len(str(peor_esperado.resolve()))


def test_mas_larga_no_revienta_si_no_existe(tmp_path):
    assert rutas.mas_larga(tmp_path / "no-existe") == (None, 0)


def test_se_pasa_es_falso_para_una_ruta_normal():
    assert not rutas.se_pasa("herramientas")


def test_entregar_usa_el_mismo_limite():
    """Tenía su propia copia del helper; se unificaron."""
    from herramientas import entregar
    assert entregar.MAX_RUTA_WINDOWS == rutas.MAXIMO
    assert not hasattr(entregar, "_ruta_larga")
