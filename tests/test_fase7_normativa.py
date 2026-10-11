"""Pruebas de la Fase 7: perfil de Administrativas y depósito en Cybertesis.

Las dos cosas que la Fase 7 agregó al repositorio y que se pueden comprobar:

- `administrativas-fca` pasó de heredar la norma general a tener la suya,
  verificada, con una estructura de tesis que **no** es la del Anexo 2B.
- La directiva de depósito en Cybertesis (RR N.° 06893-R-18), que era un
  escaneo sin leer, ahora produce dos documentos del expediente.
"""
from __future__ import annotations

import pathlib

import pytest

from herramientas import entregar
from herramientas.perfiles import cargar

RAIZ = pathlib.Path(__file__).resolve().parent.parent


# --- el perfil de Ciencias Administrativas --------------------------------

def test_administrativas_tiene_norma_propia_verificada():
    perfil = cargar("administrativas-fca")
    assert perfil.estado == "verificado"
    fuente = perfil.get("fuente")
    assert fuente["norma"] == "RR N.° 007615-2023-R/UNMSM"
    assert (RAIZ / fuente["archivo_local"]).exists(), (
        "un perfil verificado necesita el documento en disco")


def test_la_estructura_de_administrativas_no_es_la_del_anexo_2b():
    """Si fuera igual a la general, el perfil propio no aportaría nada."""
    fca = cargar("administrativas-fca")
    general = cargar("unmsm-general")

    def titulos(p):
        secs = p.get("informe_final")["modelos"]["cuantitativo"]["secciones"]
        return [s.get("titulo") for s in secs if isinstance(s, dict) and s.get("titulo")]

    t_fca, t_gen = titulos(fca), titulos(general)
    assert t_fca != t_gen
    # La discusión de la FCA va dentro del capítulo V, no en uno propio.
    assert "Discusión" in t_gen
    assert "Discusión" not in t_fca
    assert "Análisis e interpretación de los resultados" in t_fca


def test_administrativas_declara_sus_anexos_obligatorios():
    perfil = cargar("administrativas-fca")
    esperados = {"matriz_de_consistencia",
                 "matriz_de_operacionalizacion_de_variables",
                 "instrumento_de_recopilacion_de_datos",
                 "validacion_de_instrumentos"}
    assert set(perfil.get("informe_final")["anexos_obligatorios"]) == esperados
    assert set(perfil.get("proyecto")["anexos_obligatorios"]) == esperados


def test_administrativas_no_inventa_estilo_de_citas_ni_formato():
    """La directiva no los menciona: se heredan y se marcan pendientes.

    Al leerla, buscar «APA» sin límite de palabra daba aciertos dentro de
    «capacidad», y «Arial» dentro de «empresarial». Ninguno de los dos aparece
    de verdad en sus 29 folios.
    """
    perfil = cargar("administrativas-fca")
    assert perfil.get("estilo_citas") == "[PENDIENTE-NORMATIVA]"
    assert perfil.get("csl") is None


def test_administrativas_declara_su_umbral_de_similitud_propio():
    perfil = cargar("administrativas-fca")
    sim = perfil.get("similitud")
    assert sim["umbral_maximo_pct"] == 10
    assert "C-06" in sim["conflicto"], "debe remitir al conflicto registrado"


def test_la_rubrica_de_administrativas_suma_veinte():
    perfil = cargar("administrativas-fca")
    rubrica = perfil.get("sustentacion")["rubrica"]
    assert len(rubrica) == 10
    assert sum(rubrica.values()) == 20


def test_el_jurado_de_administrativas_excluye_al_asesor():
    perfil = cargar("administrativas-fca")
    sus = perfil.get("sustentacion")
    assert sus["jurado"] == 3
    assert "no puede ser miembro" in sus["jurado_detalle"].lower()


# --- el conflicto del umbral ----------------------------------------------

def test_el_conflicto_del_umbral_esta_registrado():
    texto = (RAIZ / "normativa" / "conflictos.md").read_text(encoding="utf8")
    assert "## C-06" in texto
    assert "06893-R-18" in texto and "007615-2023-R" in texto
    assert "000947-2026-R" in texto


def test_requisitos_ya_no_dice_que_cybertesis_esta_sin_leer():
    texto = (RAIZ / "normativa" / "requisitos.md").read_text(encoding="utf8")
    assert "sin leer aún" not in texto.lower()
    assert "ORCID del asesor" in texto


# --- lo que exige la directiva de depósito --------------------------------

def _datos(**extra) -> dict:
    base = {
        "titulo": "Una tesis de prueba",
        "titulo_profesional": "Licenciado en Pruebas",
        "facultad": "Facultad de Prueba",
        "escuela": "Escuela de Prueba",
        "asesor": {"nombres_y_apellidos": "Ana Quispe", "correo": "a@unmsm.edu.pe"},
    }
    base.update(extra)
    return base


AUTOR = entregar.Autor(apellidos="Rojas Díaz", nombres="Luis", dni="12345678")


def test_la_autorizacion_de_cybertesis_fija_la_licencia_de_la_directiva():
    texto = entregar.autorizacion_cybertesis([AUTOR], _datos())
    assert "Reconocimiento-NoComercial-CompartirIgual 4.0" in texto
    assert "creativecommons.org/licenses/by-nc-sa/4.0/" in texto
    assert "06893-R-18" in texto


def test_la_autorizacion_pide_lo_que_pide_el_anexo_1():
    texto = entregar.autorizacion_cybertesis([AUTOR], _datos())
    for campo in ("Firma:", "Nombre:", "DNI:", "Domicilio:", "Fecha:"):
        assert campo in texto, f"falta el campo {campo} del Anexo 1"
    assert "Rojas Díaz" in texto and "12345678" in texto


def test_la_autorizacion_avisa_de_la_postergacion_posible():
    texto = entregar.autorizacion_cybertesis([AUTOR], _datos())
    assert "2 años" in texto


def test_la_metadata_complementaria_marca_lo_que_falta():
    texto = entregar.metadata_complementaria([AUTOR], _datos())
    assert "**FALTA**" in texto
    assert "ORCID del asesor" in texto
    assert "obligatorio" in texto


def test_la_metadata_completa_no_reclama_nada():
    datos = _datos(
        asesor={"nombres_y_apellidos": "Ana Quispe", "orcid": "0000-0002-1825-0097"},
        orcid_autor="0000-0001-2345-6789",
        grupo_de_investigacion="Grupo de Prueba",
        fuente_de_financiamiento="Sin financiamiento externo",
        ubicacion_geografica="Lima, Perú (-12.046, -77.042)",
        anios_de_la_investigacion="2024-2025",
    )
    texto = entregar.metadata_complementaria([AUTOR], datos)
    assert "**FALTA**" not in texto
    assert "Lo que falta completar" not in texto


def test_el_orcid_del_asesor_es_obligatorio_y_no_estaba_en_el_anexo_2a():
    """No figura en la información complementaria del Anexo 2A: es el que más
    veces falta, y sin él Biblioteca no deposita."""
    general = cargar("unmsm-general")
    campos = " ".join(general.get("informacion_complementaria")["campos"]).lower()
    assert "orcid" not in campos, (
        "si el Anexo 2A ya lo pidiera, este aviso sobraría")

    texto = entregar.metadata_complementaria([AUTOR], _datos())
    assert "orcid.org" in texto


@pytest.mark.parametrize("generador", [entregar.autorizacion_cybertesis,
                                       entregar.metadata_complementaria])
def test_los_generadores_no_revientan_sin_datos(generador):
    """El tesista los corre antes de tener todo completo, que es el caso normal."""
    texto = generador([AUTOR], {})
    assert texto.strip()
