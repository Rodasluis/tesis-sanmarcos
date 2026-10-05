"""Pruebas del orquestador de verificación.

La que más importa: **una tesis vacía no puede salir aprobada.** Si el puntaje
saliera solo de contar hallazgos, un repositorio recién creado sacaría 100 y
diría «listo para entregar», porque donde no hay texto no hay errores. Esa es la
clase de mentira cómoda que este repositorio existe para no decir, así que cada
componente informa cuánto material revisó y el que no revisó nada no puntúa.
"""
from __future__ import annotations

from herramientas import verificar_todo as V
from herramientas.registrar_decision import registrar
from tests.conftest import escribir_capitulo, escribir_perfil

CAPITULO = """\
# Introducción

Texto de la introducción.

# Revisión de literatura

Texto.

# Materiales y métodos

Texto.

# Resultados

Texto.

# Conclusiones y recomendaciones

Texto.
"""


def _decidir(raiz, etapa: str) -> None:
    registrar({
        "etapa": etapa,
        "opciones_presentadas": ["A", "B"],
        "recomendada": "A",
        "eleccion": "A",
        "respuesta_textual": "Elijo A porque encaja con los datos que tengo.",
        "cambios_pedidos": [],
        "preguntas_comprension": [],
        "aprobado": True,
        "autor": "tesista",
    }, dir_decisiones=raiz / "decisiones")


# --- el caso que da sentido a todo lo demás --------------------------------

def test_una_tesis_vacia_no_puede_entregar(proyecto):
    escribir_perfil(proyecto)
    r = V.verificar(proyecto, rapido=True)

    assert not r.puede(V.UMBRAL_ENTREGA)
    assert not r.puede(V.UMBRAL_ETAPA)
    assert not r.puede(V.UMBRAL_COMMIT)


def test_un_componente_sin_material_no_vale_cien(proyecto):
    escribir_perfil(proyecto)
    r = V.verificar(proyecto, rapido=True)

    vacios = {c.nombre for c in r.vacios}
    assert "decisiones" in vacios
    assert "referencias" in vacios
    for c in r.vacios:
        assert c.puntaje is None, f"{c.nombre} puntuó sin haber revisado nada"
        assert c.estado == V.SIN_MATERIAL


def test_el_promedio_solo_cuenta_lo_que_tuvo_material(proyecto):
    escribir_perfil(proyecto)
    r = V.verificar(proyecto, rapido=True)

    assert r.con_material, "el perfil sí se puede revisar"
    assert len(r.con_material) < len(r.componentes)
    assert r.global_ == round(
        sum(c.puntaje for c in r.con_material) / len(r.con_material))


def test_dice_que_falta_y_no_solo_que_no_puede(proyecto):
    """Un «todavía no» sin motivo deja al tesista sin saber qué hacer."""
    escribir_perfil(proyecto)
    r = V.verificar(proyecto, rapido=True)

    razon = r.razon_de_no()
    assert razon
    assert "falta" in razon
    for linea in r.veredicto():
        assert "todavía no" in linea


def test_no_repite_la_misma_falta_varias_veces(proyecto):
    """Tres componentes esperan los capítulos; se dice una vez."""
    escribir_perfil(proyecto)
    r = V.verificar(proyecto, rapido=True)

    razon = r.razon_de_no()
    assert razon.count("capítulos escritos") <= 1


# --- con material de verdad ------------------------------------------------

def test_con_material_limpio_puntua_alto(proyecto):
    escribir_perfil(proyecto)
    escribir_capitulo(proyecto, "01-tesis", CAPITULO)
    for etapa in ("iniciar", "explorar-datos", "afinar-idea", "literatura",
                  "proyecto", "analizar"):
        _decidir(proyecto, etapa)

    r = V.verificar(proyecto, rapido=True)

    assert not r.vacios, [c.nombre for c in r.vacios]
    assert r.global_ >= V.UMBRAL_COMMIT
    assert r.peor_componente > 0


def test_los_errores_bajan_el_puntaje(proyecto):
    escribir_perfil(proyecto)
    escribir_capitulo(proyecto, "01-tesis", CAPITULO + "\nEl PBI creció 7.3 %.\n")
    for etapa in ("iniciar", "explorar-datos"):
        _decidir(proyecto, etapa)

    r = V.verificar(proyecto, rapido=True)

    assert r.errores_totales > 0, "una cifra inventada tiene que dar error"
    cifras = next(c for c in r.componentes if c.nombre == "cifras")
    assert cifras.puntaje < 100
    assert not cifras.ok


def test_un_componente_bajo_bloquea_aunque_el_promedio_alcance(proyecto):
    """Ningún componente puede bajar de 80, aunque el resto esté perfecto."""
    r = V.Resultado(componentes=[
        V.Componente("a", "A", "n", "algo", informe=_informe_vacio(proyecto),
                     puntaje=100, material=1),
        V.Componente("b", "B", "n", "algo", informe=_informe_vacio(proyecto),
                     puntaje=100, material=1),
        V.Componente("c", "C", "n", "algo", informe=_informe_vacio(proyecto),
                     puntaje=40, material=1),
    ], raiz=proyecto)

    assert r.global_ == 80
    assert not r.puede(V.UMBRAL_COMMIT)
    assert str(V.UMBRAL_COMPONENTE) in r.razon_de_no()


def _informe_vacio(raiz):
    from herramientas.informe import Informe
    return Informe("prueba", "Prueba", raiz=raiz)


# --- que una herramienta falle no puede tumbar el resto --------------------

def test_una_herramienta_caida_no_impide_ver_las_demas(proyecto, monkeypatch):
    escribir_perfil(proyecto)

    def explota(**_):
        raise RuntimeError("se cayó")

    monkeypatch.setattr(V.verificar_cifras, "verificar", explota)
    r = V.verificar(proyecto, rapido=True)

    caidos = {c.nombre for c in r.caidos}
    assert caidos == {"cifras"}
    assert any(c.nombre == "perfil" and c.corrio for c in r.componentes)
    assert "se cayó" in next(c for c in r.caidos).error


def test_una_herramienta_caida_bloquea_los_umbrales(proyecto, monkeypatch):
    """No se disimula: si no se pudo comprobar, no se puede decir que está bien."""
    escribir_perfil(proyecto)
    escribir_capitulo(proyecto, "01-tesis", CAPITULO)
    for etapa in ("iniciar", "explorar-datos"):
        _decidir(proyecto, etapa)

    monkeypatch.setattr(V.verificar_cifras, "verificar",
                        lambda **_: (_ for _ in ()).throw(RuntimeError("se cayó")))
    r = V.verificar(proyecto, rapido=True)

    assert not r.puede(V.UMBRAL_COMMIT)
    assert "no se pudieron correr" in r.razon_de_no()


# --- salidas ---------------------------------------------------------------

def test_la_consola_nunca_presenta_el_puntaje_como_calidad(proyecto):
    escribir_perfil(proyecto)
    texto = V.a_consola(V.verificar(proyecto, rapido=True))

    assert "semáforo" in texto
    assert "no una medida de calidad" in texto


def test_la_consola_explica_los_componentes_vacios(proyecto):
    escribir_perfil(proyecto)
    texto = V.a_consola(V.verificar(proyecto, rapido=True))

    assert "nada que revisar todavía" in texto
    assert "no se puede" in texto and "aprobación" in texto


def test_el_resumen_json_no_inventa_un_puntaje_cuando_no_hay_material(proyecto):
    escribir_perfil(proyecto)
    r = V.verificar(proyecto, rapido=True)
    ruta = V.escribir_resumen(r)

    import json
    datos = json.loads(ruta.read_text(encoding="utf8"))
    assert datos["puede_entregar"] is False
    assert datos["razon_de_no"]
    assert datos["componentes"]["decisiones"]["puntaje"] is None
    assert datos["componentes"]["decisiones"]["estado"] == V.SIN_MATERIAL
    assert "descargo" in datos


def test_el_modo_rapido_omite_la_similitud(proyecto):
    escribir_perfil(proyecto)

    nombres_rapido = {c.nombre for c in V.verificar(proyecto, rapido=True).componentes}
    nombres_completo = {c.nombre for c in V.verificar(proyecto, rapido=False).componentes}

    assert "similitud" not in nombres_rapido
    assert "similitud" in nombres_completo


def test_sin_red_es_el_valor_por_defecto(proyecto):
    """Una verificación que depende de que una API responda no sirve de semáforo."""
    import inspect
    assert inspect.signature(V.verificar).parameters["sin_red"].default is True
