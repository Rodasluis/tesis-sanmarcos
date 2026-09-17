"""Pruebas del registro de decisiones: el principio 3 hecho comprobación.

Lo que más importa aquí no es que grabe bien, sino que **se niegue** a grabar una
decisión que el tesista no tomó.
"""
from __future__ import annotations

import json

import pytest

from herramientas import verificar_decisiones as V
from herramientas.registrar_decision import (
    DecisionInvalida,
    calcular_hash,
    registrar,
)

DECISION = {
    "etapa": "afinar-idea",
    "opciones_presentadas": [
        {"id": "A", "titulo": "Efecto del canon en el gasto municipal",
         "ventajas": ["datos del MEF disponibles"], "riesgos": ["endogeneidad"],
         "factibilidad": "alta"},
        {"id": "B", "titulo": "Brechas de aprendizaje", "factibilidad": "media"},
    ],
    "recomendada": "A",
    "eleccion": "B",
    "respuesta_textual": "Prefiero la B porque trabajo en un colegio y conozco el tema.",
    "cambios_pedidos": ["acotar a Lima Metropolitana"],
    "preguntas_comprension": [
        {"pregunta": "¿Por qué la muestra es representativa?",
         "respuesta": "Porque cubre las cinco UGEL de Lima."},
        {"pregunta": "¿Qué pasaría si el efecto fuera cero?", "respuesta": ""},
    ],
    "aprobado": True,
}


def test_registra_y_deja_los_dos_archivos(proyecto):
    ruta_json, ruta_md = registrar(dict(DECISION), proyecto / "decisiones")
    assert ruta_json.exists() and ruta_md.exists()
    datos = json.loads(ruta_json.read_text(encoding="utf8"))
    assert datos["eleccion"] == "B"
    assert datos["hash"] == calcular_hash(datos)


def test_conserva_la_respuesta_textual_sin_tocarla(proyecto):
    ruta_json, ruta_md = registrar(dict(DECISION), proyecto / "decisiones")
    datos = json.loads(ruta_json.read_text(encoding="utf8"))
    assert datos["respuesta_textual"] == DECISION["respuesta_textual"]
    assert DECISION["respuesta_textual"] in ruta_md.read_text(encoding="utf8")


def test_el_markdown_muestra_cual_se_recomendo(proyecto):
    _, ruta_md = registrar(dict(DECISION), proyecto / "decisiones")
    texto = ruta_md.read_text(encoding="utf8")
    assert "(recomendada)" in texto
    assert "Efecto del canon" in texto


def test_sin_respuesta_textual_no_registra_nada(proyecto):
    datos = dict(DECISION, respuesta_textual="")
    with pytest.raises(DecisionInvalida, match="respuesta_textual"):
        registrar(datos, proyecto / "decisiones")
    assert not list((proyecto / "decisiones").glob("*.json"))


def test_sin_aprobacion_no_registra_nada(proyecto):
    datos = dict(DECISION, aprobado=False)
    with pytest.raises(DecisionInvalida, match="aprobado"):
        registrar(datos, proyecto / "decisiones")


def test_sin_eleccion_no_registra_nada(proyecto):
    datos = dict(DECISION, eleccion="   ")
    with pytest.raises(DecisionInvalida, match="eleccion"):
        registrar(datos, proyecto / "decisiones")


def test_etapa_desconocida_se_rechaza(proyecto):
    datos = dict(DECISION, etapa="inventada")
    with pytest.raises(DecisionInvalida, match="etapa desconocida"):
        registrar(datos, proyecto / "decisiones")


def test_el_numero_de_archivo_sale_del_orden_de_la_etapa(proyecto):
    ruta_json, _ = registrar(dict(DECISION), proyecto / "decisiones")
    assert ruta_json.name.startswith("02_")      # afinar-idea es la etapa 2


# --- verificación ----------------------------------------------------------

def test_un_proyecto_sin_decisiones_ni_trabajo_no_da_errores(proyecto):
    inf = V.verificar(proyecto)
    assert not inf.hay_errores


def test_detecta_una_decision_editada_a_mano(proyecto):
    ruta_json, _ = registrar(dict(DECISION), proyecto / "decisiones")
    datos = json.loads(ruta_json.read_text(encoding="utf8"))
    datos["eleccion"] = "A"           # alguien cambió la elección después
    ruta_json.write_text(json.dumps(datos, ensure_ascii=False), encoding="utf8")

    inf = V.verificar(proyecto)
    codigos = [h.codigo for h in inf.errores]
    assert "D06" in codigos
    assert any("modificada después" in h.mensaje for h in inf.errores)


def test_detecta_trabajo_sin_decision_registrada(proyecto):
    (proyecto / "capitulos" / "01_introduccion.qmd").write_text("# Introducción",
                                                                encoding="utf8")
    inf = V.verificar(proyecto)
    assert any(h.codigo == "D10" for h in inf.errores)


def test_no_reclama_si_la_decision_existe(proyecto):
    (proyecto / "capitulos" / "01_introduccion.qmd").write_text("# Introducción",
                                                                encoding="utf8")
    registrar(dict(DECISION, etapa="redactar"), proyecto / "decisiones")
    inf = V.verificar(proyecto)
    assert not any(h.codigo == "D10" for h in inf.errores)


def test_exigir_hasta_reclama_las_etapas_previas(proyecto):
    registrar(dict(DECISION, etapa="iniciar"), proyecto / "decisiones")
    inf = V.verificar(proyecto, exigir_hasta="proyecto")
    faltan = [h.detalle.get("etapa") for h in inf.errores if h.codigo == "D12"]
    assert "explorar-datos" in faltan and "proyecto" in faltan
    assert "iniciar" not in faltan


def test_avisa_de_preguntas_de_comprension_sin_responder(proyecto):
    registrar(dict(DECISION), proyecto / "decisiones")
    inf = V.verificar(proyecto)
    assert any(h.codigo == "D09" for h in inf.hallazgos)


def test_una_decision_no_aprobada_en_disco_es_error(proyecto):
    """Si alguien la creó por fuera de la herramienta, se detecta."""
    (proyecto / "decisiones" / "02_afinar-idea.json").write_text(
        json.dumps({"etapa": "afinar-idea", "aprobado": False,
                    "respuesta_textual": "x", "hash": "sin-sentido"}),
        encoding="utf8")
    inf = V.verificar(proyecto)
    codigos = {h.codigo for h in inf.errores}
    assert "D03" in codigos and "D06" in codigos
