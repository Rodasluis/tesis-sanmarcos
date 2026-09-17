"""Pruebas del informe común y del lector de BibTeX."""
from __future__ import annotations

import json

import pytest

from herramientas import bibtex
from herramientas.informe import Informe, puntaje, unir
from tests.conftest import BIB_MINIMO

# --- informe ---------------------------------------------------------------

def test_el_codigo_de_salida_depende_solo_de_los_errores(proyecto):
    inf = Informe("x", "Prueba", raiz=proyecto)
    inf.aviso("A1", "algo menor")
    inf.info("I1", "contexto")
    assert inf.codigo_salida() == 0
    inf.error("E1", "algo grave")
    assert inf.codigo_salida() == 1


def test_escribe_markdown_y_json(proyecto):
    inf = Informe("x", "Prueba", raiz=proyecto)
    inf.error("E1", "falla", archivo=proyecto / "capitulos" / "uno.qmd", linea=7)
    md = inf.a_markdown(proyecto / "registro" / "x.md")
    js = inf.a_json(proyecto / "registro" / "x.json")

    texto = md.read_text(encoding="utf8")
    assert "E1" in texto and "falla" in texto
    datos = json.loads(js.read_text(encoding="utf8"))
    assert datos["resumen"]["error"] == 1
    assert datos["hallazgos"][0]["linea"] == 7
    assert datos["hallazgos"][0]["archivo"] == "capitulos\\uno.qmd".replace("\\", "/") or \
           datos["hallazgos"][0]["archivo"].endswith("uno.qmd")


def test_todo_informe_lleva_el_descargo(proyecto):
    """Sin errores no es lo mismo que aprobado, y debe decirlo."""
    inf = Informe("x", "Prueba", raiz=proyecto)
    salida = inf.a_consola()
    assert "no significa aprobado" in salida
    md = inf.a_markdown(proyecto / "registro" / "x.md")
    assert "no significa aprobado" in md.read_text(encoding="utf8")


def test_nivel_desconocido_es_un_error_de_programacion(proyecto):
    inf = Informe("x", "Prueba", raiz=proyecto)
    with pytest.raises(ValueError):
        inf._agregar("grave", "E", "m")


def test_puntaje_descuenta_errores_y_avisos(proyecto):
    inf = Informe("x", "Prueba", raiz=proyecto)
    assert puntaje(inf, 10) == 100
    inf.aviso("A", "m")
    assert puntaje(inf, 10) == 98
    for _ in range(12):
        inf.error("E", "m")
    assert puntaje(inf, 10) == 0


def test_unir_agrega_varios_informes(proyecto):
    a = Informe("a", "A", raiz=proyecto)
    a.error("E", "m")
    b = Informe("b", "B", raiz=proyecto)
    b.aviso("A", "m")
    resultado = unir(a, b)
    assert resultado["total"] == {"error": 1, "aviso": 1, "info": 0}
    assert resultado["hay_errores"] is True


# --- bibtex ----------------------------------------------------------------

def test_lee_entradas_y_campos():
    entradas = bibtex.parsear(BIB_MINIMO)
    assert len(entradas) == 2
    por_clave = bibtex.indexar(entradas)
    e = por_clave["perez2020crecimiento"]
    assert e.tipo == "article"
    assert e.anio == "2020"
    assert e.doi == "10.1234/rev.2020.12"
    assert "Crecimiento económico" in e.titulo_limpio
    assert e.primer_autor == "Pérez"


def test_quita_el_prefijo_de_url_en_el_doi():
    entradas = bibtex.parsear(
        "@article{a, title={T}, doi={https://doi.org/10.1/xyz}, year={2020}}")
    assert entradas[0].doi == "10.1/xyz"


def test_soporta_llaves_anidadas_y_comillas():
    texto = ('@book{b, title = {Un {Título} con llaves}, '
             'author = "Autor, Un", year = 2021, publisher={X}}')
    e = bibtex.parsear(texto)[0]
    assert e.titulo_limpio == "Un Título con llaves"
    assert e.primer_autor == "Autor"
    assert e.anio == "2021"


def test_ignora_comentarios_y_strings():
    texto = "@string{rev = {Revista}}\n@comment{nada}\n" + BIB_MINIMO
    assert len(bibtex.parsear(texto)) == 2


def test_detecta_campos_faltantes_segun_el_estilo():
    e = bibtex.parsear("@article{a, title={T}, year={2020}}")[0]
    faltan = e.campos_faltantes("apa7")
    assert "author" in faltan and "journal" in faltan


def test_detecta_claves_repetidas():
    texto = ("@article{a, title={T}, year={2020}}\n"
             "@article{a, title={Otro}, year={2021}}")
    assert bibtex.claves_repetidas(bibtex.parsear(texto)) == {"a": 2}


def test_detecta_la_misma_obra_con_claves_distintas():
    texto = ("@article{uno, title={Mismo título exacto}, year={2020}, doi={10.1/x}}\n"
             "@article{dos, title={Mismo título exacto}, year={2020}, doi={10.1/x}}")
    grupos = bibtex.duplicados(bibtex.parsear(texto))
    assert len(grupos) == 1
    assert {e.clave for e in next(iter(grupos.values()))} == {"uno", "dos"}


def test_archivo_inexistente_devuelve_lista_vacia(tmp_path):
    assert bibtex.cargar(tmp_path / "no_existe.bib") == []
