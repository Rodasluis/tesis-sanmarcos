"""Pruebas del verificador de cifras y de citas de participantes."""
from __future__ import annotations

from herramientas import verificar_cifras as V
from tests.conftest import escribir_capitulo, escribir_perfil


def _resultados(proyecto, contenido="metrica,valor\npib,3.4\ndesempleo,7.1\nn,1250\n"):
    (proyecto / "resultados").mkdir(parents=True, exist_ok=True)
    (proyecto / "resultados" / "tabla1.csv").write_text(contenido, encoding="utf8")


def test_cifra_a_mano_que_no_esta_en_resultados_es_error(proyecto):
    escribir_perfil(proyecto)
    _resultados(proyecto)
    escribir_capitulo(proyecto, "05_resultados",
                      "# Resultados\n\nEl PIB creció 9.9 % en el periodo.\n")
    inf = V.verificar(proyecto)
    errores = [h for h in inf.errores if h.codigo == "C03"]
    assert errores and "9.9" in errores[0].mensaje


def test_cifra_a_mano_que_si_esta_en_resultados_es_aviso(proyecto):
    escribir_perfil(proyecto)
    _resultados(proyecto)
    escribir_capitulo(proyecto, "05_resultados",
                      "# Resultados\n\nEl PIB creció 3.4 % en el periodo.\n")
    inf = V.verificar(proyecto)
    assert any(h.codigo == "C02" for h in inf.avisos)
    assert not any(h.codigo == "C03" for h in inf.errores)


def test_una_expresion_de_quarto_no_es_una_cifra_a_mano(proyecto):
    escribir_perfil(proyecto)
    _resultados(proyecto)
    escribir_capitulo(proyecto, "05_resultados",
                      "# Resultados\n\nEl PIB creció `{python} pib` % en el periodo.\n")
    inf = V.verificar(proyecto)
    assert not inf.hay_errores
    assert not any(h.codigo in ("C02", "C03") for h in inf.avisos)


def test_ignora_los_numeros_dentro_de_bloques_de_codigo(proyecto):
    escribir_perfil(proyecto)
    _resultados(proyecto)
    escribir_capitulo(proyecto, "05_resultados",
                      "# Resultados\n\n```python\nx = 99999\n```\n\nSin cifras aquí.\n")
    inf = V.verificar(proyecto)
    assert not any(h.codigo == "C03" for h in inf.errores)


def test_los_anios_no_se_confunden_con_datos(proyecto):
    escribir_perfil(proyecto)
    _resultados(proyecto)
    escribir_capitulo(proyecto, "05_resultados",
                      "# Resultados\n\nEntre 2019 y 2023 la tendencia se mantuvo.\n")
    inf = V.verificar(proyecto)
    assert not any(h.codigo == "C03" for h in inf.errores)


def test_la_numeracion_de_tablas_no_se_confunde_con_datos(proyecto):
    escribir_perfil(proyecto)
    _resultados(proyecto)
    escribir_capitulo(proyecto, "05_resultados",
                      "# Resultados\n\nSegún la tabla 2 y la figura 3, el patrón se repite.\n")
    inf = V.verificar(proyecto)
    assert not any(h.codigo == "C03" for h in inf.errores)


def test_avisa_si_resultados_esta_vacio(proyecto):
    escribir_perfil(proyecto)
    escribir_capitulo(proyecto, "05_resultados", "# Resultados\n\nTexto.\n")
    inf = V.verificar(proyecto)
    assert any(h.codigo == "C01" for h in inf.avisos)


def test_cita_de_participante_que_no_esta_en_la_transcripcion_es_error(proyecto):
    escribir_perfil(proyecto, enfoques_admitidos=["cualitativo"])
    (proyecto / "datos" / "crudos").mkdir(parents=True, exist_ok=True)
    (proyecto / "datos" / "crudos" / "e01.txt").write_text(
        "Entrevistadora: ¿cómo lo vivió? Participante: fue muy difícil al comienzo, "
        "pero luego nos organizamos.", encoding="utf8")
    escribir_capitulo(proyecto, "05_resultados", (
        "# Resultados\n\n"
        "> nunca recibimos ningún tipo de apoyo de la municipalidad (E-01)\n"))
    inf = V.verificar(proyecto)
    assert any(h.codigo == "C05" for h in inf.errores)


def test_cita_de_participante_que_si_esta_pasa(proyecto):
    escribir_perfil(proyecto, enfoques_admitidos=["cualitativo"])
    (proyecto / "datos" / "crudos").mkdir(parents=True, exist_ok=True)
    (proyecto / "datos" / "crudos" / "e01.txt").write_text(
        "Participante: fue muy difícil al comienzo, pero luego nos organizamos.",
        encoding="utf8")
    escribir_capitulo(proyecto, "05_resultados", (
        "# Resultados\n\n"
        "> fue muy difícil al comienzo, pero luego nos organizamos (E-01)\n"))
    inf = V.verificar(proyecto)
    assert not any(h.codigo == "C05" for h in inf.errores)


def test_citas_de_participantes_sin_transcripciones_es_error(proyecto):
    escribir_perfil(proyecto, enfoques_admitidos=["cualitativo"])
    escribir_capitulo(proyecto, "05_resultados",
                      "# Resultados\n\n> algo que alguien dijo alguna vez (P-3)\n")
    inf = V.verificar(proyecto)
    assert any(h.codigo == "C04" for h in inf.errores)


def test_sin_capitulos_no_falla(proyecto):
    escribir_perfil(proyecto)
    inf = V.verificar(proyecto)
    assert not inf.hay_errores


# --- falsos positivos que aparecieron al escribir los ejemplos -------------

def test_el_ancho_de_una_figura_no_es_una_cifra(proyecto):
    """`{#fig-x width=90%}` es cómo se dibuja la figura, no un dato."""
    escribir_perfil(proyecto)
    (proyecto / "resultados").mkdir(exist_ok=True)
    (proyecto / "resultados" / "r.csv").write_text("v\n1\n", encoding="utf8")
    escribir_capitulo(proyecto, "05-resultados",
                      "# Resultados\n\n"
                      "![Pie de figura.](../resultados/f.png){#fig-uno width=90%}\n")
    inf = V.verificar(proyecto)
    assert not inf.hay_errores, [h.como_linea() for h in inf.errores]


def test_la_numeracion_de_una_lista_no_es_una_cifra(proyecto):
    """El «1.» de «1. Primera hipótesis» enumera, no mide."""
    escribir_perfil(proyecto)
    (proyecto / "resultados").mkdir(exist_ok=True)
    (proyecto / "resultados" / "r.csv").write_text("v\n99\n", encoding="utf8")
    escribir_capitulo(proyecto, "05-resultados",
                      "# Resultados\n\n"
                      "1. Primera hipótesis sostenida.\n"
                      "2. Segunda hipótesis no sostenida.\n\n"
                      "| Hipótesis | Resultado |\n|---|---|\n"
                      "| 1. La primera | se sostiene |\n")
    inf = V.verificar(proyecto)
    assert not inf.hay_errores, [h.como_linea() for h in inf.errores]


def test_el_nivel_de_confianza_no_es_un_dato_del_analisis(proyecto):
    """El 95 de «intervalo al 95 %» es una convención, no un resultado."""
    escribir_perfil(proyecto)
    (proyecto / "resultados").mkdir(exist_ok=True)
    (proyecto / "resultados" / "r.csv").write_text("v\n0.34\n", encoding="utf8")
    escribir_capitulo(proyecto, "05-resultados",
                      "# Resultados\n\n"
                      "El intervalo de confianza al 95 % incluye el cero, "
                      "con p < 0.001 en la primera especificación.\n")
    inf = V.verificar(proyecto)
    assert not inf.hay_errores, [h.como_linea() for h in inf.errores]


def test_una_cifra_inventada_sigue_siendo_un_error(proyecto):
    """Los filtros anteriores no pueden abrir la puerta a lo que sí importa."""
    escribir_perfil(proyecto)
    (proyecto / "resultados").mkdir(exist_ok=True)
    (proyecto / "resultados" / "r.csv").write_text("v\n0.34\n", encoding="utf8")
    escribir_capitulo(proyecto, "05-resultados",
                      "# Resultados\n\nEl efecto estimado fue de 7.219 puntos.\n")
    inf = V.verificar(proyecto)
    assert inf.hay_errores
    assert any("7.219" in h.mensaje for h in inf.errores)
