"""El reparto en dos archivos que exige el art. 13 A.2.

No es cosmético: **el archivo de Desarrollo es el que se somete al análisis de
similitud**. La carátula y la bibliografía son texto que el tesista no redactó
y que coincide con el de cualquier otra tesis, así que la norma los saca de ahí
y los pone en el de «Protocolo y Complemento».

El motor hacía lo contrario: metía la carátula y la bibliografía en el primero
y, si no había ningún .qmd de anexos —el caso normal—, **no generaba el segundo
y no avisaba**. Quedaba un solo .docx en `TEXTO/` con 0 errores y 0 avisos.
"""
from __future__ import annotations

import pathlib

import pytest

from herramientas import entregar
from tests.conftest import escribir_bib, escribir_capitulo, escribir_perfil

RAIZ = pathlib.Path(__file__).resolve().parent.parent


# --- qué claves se citan de verdad ----------------------------------------

def test_las_referencias_cruzadas_de_quarto_no_son_citas(tmp_path):
    """`@fig-dispersion` es «ver figura 1», no una obra.

    Si se colara en el `nocite` del archivo de Complemento, citeproc buscaría
    esa clave en el .bib, no la encontraría y la imprimiría en crudo.
    """
    f = tmp_path / "cap.qmd"
    f.write_text(
        "Como se ve en @fig-dispersion y en la @tbl-resumen, y segun "
        "@Czernich_2011 y @Maurseth_2018 [p. 14], el efecto de @eq-uno "
        "se discute en la @sec-metodos.", encoding="utf8")
    assert entregar.claves_citadas([f]) == ["Czernich_2011", "Maurseth_2018"]


def test_las_claves_salen_sin_repetir_y_en_orden(tmp_path):
    f = tmp_path / "cap.qmd"
    f.write_text("@b dice una cosa; @a otra; @b insiste.", encoding="utf8")
    assert entregar.claves_citadas([f]) == ["b", "a"]


def test_un_correo_no_es_una_cita(tmp_path):
    f = tmp_path / "cap.qmd"
    f.write_text("Escribe a tesis@unmsm.edu.pe para pedirlo.", encoding="utf8")
    assert entregar.claves_citadas([f]) == []


def test_sin_citas_no_hay_claves(tmp_path):
    f = tmp_path / "cap.qmd"
    f.write_text("Un capitulo sin una sola cita.", encoding="utf8")
    assert entregar.claves_citadas([f]) == []


# --- el flujo entero, si hay con qué renderizar ---------------------------

def _tesis_lista(raiz: pathlib.Path) -> None:
    escribir_perfil(raiz, "prueba")
    (raiz / ".perfil-activo").write_text("prueba", encoding="utf8")
    escribir_bib(raiz, """
@article{Czernich_2011,
  author = {Czernich, Nina},
  title = {Broadband Infrastructure and Economic Growth},
  journal = {The Economic Journal},
  year = {2011}
}
""".strip())
    escribir_capitulo(raiz, "01-introduccion.qmd",
                      "# Introduccion\n\nSegun @Czernich_2011, algo pasa.\n")
    (raiz / "entregables").mkdir(exist_ok=True)
    (raiz / "entregables" / "datos_de_entrega.yaml").write_text(
        "titulo: Una tesis de prueba\n"
        "titulo_profesional: Licenciado en Pruebas\n"
        "facultad: Facultad de Prueba\n"
        "escuela: Escuela de Prueba\n"
        "anio: 2026\n"
        "autores:\n"
        "  - apellidos: Rojas Diaz\n"
        "    nombres: Luis\n"
        "    dni: '12345678'\n"
        "asesor:\n"
        "  nombres_y_apellidos: Ana Quispe\n",
        encoding="utf8")


@pytest.mark.skipif(entregar._quarto() is None, reason="no hay Quarto en este equipo")
def test_la_caratula_y_la_bibliografia_van_en_el_segundo_archivo(proyecto):
    import docx

    from herramientas import plantilla_docx
    from herramientas.perfiles import cargar_de

    _tesis_lista(proyecto)
    plantilla_docx.construir(cargar_de(proyecto, "prueba"), raiz=proyecto)

    inf = entregar.preparar(proyecto)
    assert not inf.hay_errores, [h.como_linea() for h in inf.errores]

    texto = proyecto / "entregables" / "TEXTO"
    desarrollo = list(texto.glob("*Desarrollo*.docx"))
    complemento = list(texto.glob("*Protocolo y Complemento*.docx"))
    assert desarrollo, "falta el archivo de Desarrollo"
    assert complemento, (
        "falta el de Protocolo y Complemento: el art. 13 A.2 pide DOS archivos, "
        "y antes se saltaba en silencio cuando no habia .qmd de anexos")

    def parrafos(f):
        return [p.text.strip() for p in docx.Document(str(f)).paragraphs if p.text.strip()]

    d, c = parrafos(desarrollo[0]), parrafos(complemento[0])

    # A.2 a): el primero va «sin caratula […] ni referencias bibliograficas».
    assert not any("Decana de Am" in p for p in d), "la caratula no va en Desarrollo"
    assert not any(p.startswith("Czernich, Nina") for p in d), (
        "la lista de referencias no va en Desarrollo")

    # A.2 b): el segundo lleva la caratula y la bibliografia.
    assert any("Decana de Am" in p for p in c), "falta la caratula en el Complemento"
    assert any(p.startswith("Czernich, Nina") for p in c), (
        "falta la bibliografia en el Complemento")


@pytest.mark.skipif(entregar._quarto() is None, reason="no hay Quarto en este equipo")
def test_la_cita_en_el_texto_se_queda_en_el_cuerpo(proyecto):
    """Sale la LISTA de referencias, no la cita. «(Czernich 2011)» es cuerpo."""
    import docx

    from herramientas import plantilla_docx
    from herramientas.perfiles import cargar_de

    _tesis_lista(proyecto)
    plantilla_docx.construir(cargar_de(proyecto, "prueba"), raiz=proyecto)
    entregar.preparar(proyecto)

    f = list((proyecto / "entregables" / "TEXTO").glob("*Desarrollo*.docx"))[0]
    cuerpo = " ".join(p.text for p in docx.Document(str(f)).paragraphs)
    assert "Czernich" in cuerpo, "la cita en el texto tiene que seguir ahi"
