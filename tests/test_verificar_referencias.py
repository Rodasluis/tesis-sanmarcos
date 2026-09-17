"""Pruebas del verificador de referencias.

Todas corren con `sin_red=True`: una prueba no debe depender de que Crossref
esté disponible. Las rutas de red se prueban aparte, con un cliente simulado.
"""
from __future__ import annotations

import pathlib

from herramientas import verificar_referencias as V
from tests.conftest import BIB_MINIMO, escribir_bib, escribir_capitulo, escribir_perfil


def _preparar(proyecto: pathlib.Path, contenido: str, bib: str = BIB_MINIMO):
    escribir_perfil(proyecto)
    escribir_bib(proyecto, bib)
    escribir_capitulo(proyecto, "04_resultados", contenido)
    return proyecto


# --- extracción ------------------------------------------------------------

def test_reconoce_las_tres_formas_de_citar(proyecto):
    ruta = escribir_capitulo(proyecto, "c", (
        "# Título\n\n"
        "Una idea [@perez2020crecimiento].\n\n"
        "Según @minedu2019escale, el dato es otro.\n\n"
        "Otra cosa [@perez2020crecimiento, p. 45].\n"))
    claves = [c.clave for c in V.extraer_citas(ruta)]
    assert claves.count("perez2020crecimiento") == 2
    assert "minedu2019escale" in claves


def test_ignora_las_citas_dentro_de_bloques_de_codigo(proyecto):
    ruta = escribir_capitulo(proyecto, "c", (
        "# T\n\n```python\n# @noesunacita\nx = 1\n```\n\n"
        "Texto real [@perez2020crecimiento].\n"))
    claves = [c.clave for c in V.extraer_citas(ruta)]
    assert claves == ["perez2020crecimiento"]


def test_ignora_el_front_matter(proyecto):
    ruta = escribir_capitulo(proyecto, "c", (
        "---\ntitle: \"Algo con @arroba\"\n---\n\n"
        "Cuerpo [@perez2020crecimiento].\n"))
    assert [c.clave for c in V.extraer_citas(ruta)] == ["perez2020crecimiento"]


# --- comprobaciones --------------------------------------------------------

def test_clave_inexistente_es_error(proyecto):
    _preparar(proyecto, "# Resultados\n\nAlgo [@noexiste2020].\n")
    inf = V.verificar(proyecto, sin_red=True)
    assert any(h.codigo == "R02" for h in inf.errores)
    assert inf.codigo_salida() == 1


def test_cita_textual_sin_pagina_es_error(proyecto):
    _preparar(proyecto, (
        "# Resultados\n\n"
        "El autor sostiene que «el crecimiento regional dependió del canon minero "
        "durante toda la década» [@perez2020crecimiento].\n"))
    inf = V.verificar(proyecto, sin_red=True)
    assert any(h.codigo == "R03" for h in inf.errores)


def test_cita_textual_con_pagina_pasa(proyecto):
    _preparar(proyecto, (
        "# Resultados\n\n"
        "El autor sostiene que «el crecimiento regional dependió del canon minero "
        "durante toda la década» [@perez2020crecimiento, p. 41].\n"))
    inf = V.verificar(proyecto, sin_red=True)
    assert not any(h.codigo == "R03" for h in inf.errores)


def test_cita_en_bloque_larga_sin_pagina_es_error(proyecto):
    largo = " ".join(["palabra"] * 45)
    _preparar(proyecto, f"# Resultados\n\n> {largo} [@perez2020crecimiento]\n")
    inf = V.verificar(proyecto, sin_red=True)
    assert any(h.codigo == "R03" for h in inf.errores)


def test_parafrasis_sin_pagina_no_es_error(proyecto):
    _preparar(proyecto, "# Resultados\n\nEl canon explicó el gasto [@perez2020crecimiento].\n")
    inf = V.verificar(proyecto, sin_red=True)
    assert not any(h.codigo == "R03" for h in inf.errores)


def test_entrada_no_citada_es_aviso_no_error(proyecto):
    _preparar(proyecto, "# Resultados\n\nAlgo [@perez2020crecimiento].\n")
    inf = V.verificar(proyecto, sin_red=True)
    avisos = [h for h in inf.avisos if h.codigo == "R04"]
    assert any("minedu2019escale" in h.mensaje for h in avisos)
    assert not any(h.codigo == "R04" for h in inf.errores)


def test_campos_minimos_segun_el_estilo(proyecto):
    bib = "@article{incompleto2020, title = {Solo el título}, year = {2020}}"
    _preparar(proyecto, "# Resultados\n\nAlgo [@incompleto2020].\n", bib)
    inf = V.verificar(proyecto, sin_red=True)
    errores = [h for h in inf.errores if h.codigo == "R05"]
    assert errores and "author" in errores[0].mensaje


def test_clave_duplicada_en_el_bib_es_error(proyecto):
    bib = (BIB_MINIMO
           + "\n@book{perez2020crecimiento, title={Otro}, author={X, Y}, "
             "publisher={Z}, year={2021}}\n")
    _preparar(proyecto, "# Resultados\n\nAlgo [@perez2020crecimiento].\n", bib)
    inf = V.verificar(proyecto, sin_red=True)
    assert any(h.codigo == "R06" for h in inf.errores)


def test_bib_vacio_es_error_si_hay_capitulos(proyecto):
    escribir_perfil(proyecto)
    escribir_bib(proyecto, "")
    escribir_capitulo(proyecto, "c", "# Resultados\n\nTexto sin citas.\n")
    inf = V.verificar(proyecto, sin_red=True)
    assert any(h.codigo == "R01" for h in inf.errores)


def test_sin_capitulos_no_falla(proyecto):
    escribir_perfil(proyecto)
    escribir_bib(proyecto, BIB_MINIMO)
    inf = V.verificar(proyecto, sin_red=True)
    assert not inf.hay_errores


def test_sin_red_no_convierte_en_error_lo_no_comprobado(proyecto):
    _preparar(proyecto, "# Resultados\n\nAlgo [@perez2020crecimiento].\n")
    inf = V.verificar(proyecto, sin_red=True)
    sin_comprobar = [h for h in inf.hallazgos if h.codigo == "R08"]
    assert sin_comprobar
    assert all(h.nivel == "info" for h in sin_comprobar)


def test_el_estilo_sale_del_perfil(proyecto):
    escribir_perfil(proyecto, estilo_citas="vancouver")
    escribir_bib(proyecto, BIB_MINIMO)
    escribir_capitulo(proyecto, "c", "# Resultados\n\nAlgo [@perez2020crecimiento].\n")
    inf = V.verificar(proyecto, sin_red=True)
    assert inf.contexto["estilo_de_citas"] == "vancouver"


# --- rutas de red, con un cliente simulado ---------------------------------

class ClienteFalso:
    def __init__(self, datos=None, ok=True, motivo=""):
        self._datos, self._ok, self._motivo = datos or {}, ok, motivo

    def crossref(self, doi):
        from herramientas.red import Respuesta
        return Respuesta(self._ok, self._datos, self._motivo)

    def openalex(self, titulo, anio=""):
        return self.crossref("")

    def pubmed(self, titulo):
        from herramientas.red import Respuesta
        return Respuesta(False, motivo="no consultado")

    def estadisticas(self):
        return {"consultas_de_red": 0, "aciertos_de_cache": 0}


def test_titulo_que_no_coincide_con_la_fuente_es_error(proyecto, monkeypatch):
    _preparar(proyecto, "# Resultados\n\nAlgo [@perez2020crecimiento].\n")
    monkeypatch.setattr(V, "Cliente", lambda **kw: ClienteFalso(
        {"titulo": "Un título completamente distinto sobre pesca artesanal",
         "anio": "2020", "fuente": "crossref"}))
    inf = V.verificar(proyecto, sin_red=False)
    assert any(h.codigo == "R09" for h in inf.errores)


def test_anio_distinto_es_aviso(proyecto, monkeypatch):
    _preparar(proyecto, "# Resultados\n\nAlgo [@perez2020crecimiento].\n")
    monkeypatch.setattr(V, "Cliente", lambda **kw: ClienteFalso(
        {"titulo": "Crecimiento económico regional en el Perú",
         "anio": "2019", "fuente": "crossref"}))
    inf = V.verificar(proyecto, sin_red=False)
    assert any(h.codigo == "R10" for h in inf.avisos)
    assert not any(h.codigo == "R10" for h in inf.errores)


def test_una_referencia_retractada_es_error(proyecto, monkeypatch):
    _preparar(proyecto, "# Resultados\n\nAlgo [@perez2020crecimiento].\n")
    monkeypatch.setattr(V, "Cliente", lambda **kw: ClienteFalso(
        {"titulo": "Crecimiento económico regional en el Perú", "anio": "2020",
         "retirado": True, "fuente": "crossref"}))
    inf = V.verificar(proyecto, sin_red=False)
    errores = [h for h in inf.errores if h.codigo == "R11"]
    assert errores and "RETRACTADA" in errores[0].mensaje


def test_doi_que_no_resuelve_es_aviso_no_error(proyecto, monkeypatch):
    _preparar(proyecto, "# Resultados\n\nAlgo [@perez2020crecimiento].\n")
    monkeypatch.setattr(V, "Cliente",
                        lambda **kw: ClienteFalso(ok=False, motivo="no encontrado"))
    inf = V.verificar(proyecto, sin_red=False)
    assert any(h.codigo == "R08" and h.nivel == "aviso" for h in inf.hallazgos)
