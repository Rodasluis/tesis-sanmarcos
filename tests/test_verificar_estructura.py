"""Pruebas del verificador de estructura.

La prueba que más importa: que **no** exija lo que el perfil no exige.
"""
from __future__ import annotations

from herramientas import verificar_estructura as V
from herramientas.registrar_decision import registrar
from tests.conftest import escribir_capitulo, escribir_perfil

COMPLETO = """\
# Introducción

Texto.

# Revisión de literatura

Texto.

# Materiales y métodos

Texto.

# Resultados

Texto.

# Conclusiones y recomendaciones

Texto.
"""


def test_una_estructura_completa_no_da_errores(proyecto):
    escribir_perfil(proyecto)
    escribir_capitulo(proyecto, "tesis", COMPLETO)
    inf = V.verificar(proyecto)
    assert not inf.hay_errores


def test_seccion_ausente_es_error(proyecto):
    escribir_perfil(proyecto)
    escribir_capitulo(proyecto, "tesis",
                      COMPLETO.replace("# Materiales y métodos\n\nTexto.\n\n", ""))
    inf = V.verificar(proyecto)
    errores = [h for h in inf.errores if h.codigo == "E09"]
    assert errores and "Materiales y métodos" in errores[0].mensaje


def test_secciones_fuera_de_orden_es_error(proyecto):
    escribir_perfil(proyecto)
    desordenado = """\
# Introducción

Texto.

# Resultados

Texto.

# Revisión de literatura

Texto.

# Materiales y métodos

Texto.

# Conclusiones y recomendaciones

Texto.
"""
    escribir_capitulo(proyecto, "tesis", desordenado)
    inf = V.verificar(proyecto)
    assert any(h.codigo == "E10" for h in inf.errores)


def test_denominacion_distinta_es_aviso_no_error(proyecto):
    escribir_perfil(proyecto)
    escribir_capitulo(proyecto, "tesis",
                      COMPLETO.replace("# Revisión de literatura",
                                       "# Revision de la literatura"))
    inf = V.verificar(proyecto)
    assert any(h.codigo == "E05" for h in inf.avisos)
    assert not any(h.codigo == "E09" for h in inf.errores)


def test_reconoce_capitulos_numerados(proyecto):
    escribir_perfil(proyecto)
    numerado = COMPLETO.replace("# Introducción", "# CAPÍTULO I. INTRODUCCIÓN")
    escribir_capitulo(proyecto, "tesis", numerado)
    inf = V.verificar(proyecto)
    assert not any("Introducción" in h.mensaje for h in inf.errores)


def test_un_capitulo_de_mas_es_aviso(proyecto):
    escribir_perfil(proyecto)
    escribir_capitulo(proyecto, "tesis", COMPLETO + "\n# Apéndice metodológico\n\nTexto.\n")
    inf = V.verificar(proyecto)
    assert any(h.codigo == "E11" for h in inf.avisos)


def test_los_preliminares_no_se_reportan_como_sobrantes(proyecto):
    escribir_perfil(proyecto)
    escribir_capitulo(proyecto, "tesis",
                      "# Resumen\n\nTexto.\n\n# Abstract\n\nText.\n\n" + COMPLETO
                      + "\n# Referencias\n\n")
    inf = V.verificar(proyecto)
    sobrantes = [h.mensaje for h in inf.avisos if h.codigo == "E11"]
    assert not any("Resumen" in m or "Referencias" in m for m in sobrantes)


def test_el_enfoque_cambia_lo_que_se_exige(proyecto):
    escribir_perfil(proyecto)
    cualitativo = "# Introducción\n\nT.\n\n# Método\n\nT.\n\n# Resultados y discusión\n\nT.\n"
    escribir_capitulo(proyecto, "tesis", cualitativo)
    assert V.verificar(proyecto, enfoque="cualitativo").hay_errores is False
    assert V.verificar(proyecto, enfoque="cuantitativo").hay_errores is True


def test_no_exige_matriz_de_consistencia_si_el_perfil_no_la_pide(proyecto):
    """Es el caso de Economía: su guía no la exige y el verificador no debe inventarla."""
    escribir_perfil(proyecto)
    escribir_capitulo(proyecto, "tesis", COMPLETO)
    inf = V.verificar(proyecto)
    assert not any("matriz" in h.mensaje.lower() for h in inf.hallazgos)


def test_exclusion_justificada_baja_de_error_a_aviso(proyecto):
    escribir_perfil(proyecto, proyecto={"items_excluibles_con_justificacion": True})
    escribir_capitulo(proyecto, "tesis",
                      COMPLETO.replace("# Materiales y métodos\n\nTexto.\n\n", ""))

    sin_justificar = V.verificar(proyecto)
    assert any(h.codigo == "E08" for h in sin_justificar.errores)

    registrar({
        "etapa": "proyecto",
        "eleccion": "Excluir la sección de materiales y métodos",
        "respuesta_textual": "Mi tesis es documental, así que excluyo "
                             "materiales y métodos como permite la guía.",
        "aprobado": True,
        "preguntas_comprension": [],
    }, proyecto / "decisiones")

    con_justificacion = V.verificar(proyecto)
    assert any(h.codigo == "E07" for h in con_justificacion.avisos)
    assert not any(h.codigo == "E08" for h in con_justificacion.errores)


def test_sin_perfil_activo_es_error(proyecto):
    inf = V.verificar(proyecto)
    assert any(h.codigo == "E00" for h in inf.errores)


def test_sin_capitulos_no_falla(proyecto):
    escribir_perfil(proyecto)
    inf = V.verificar(proyecto)
    assert not inf.hay_errores
