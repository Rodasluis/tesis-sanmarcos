"""Pruebas de `verificar_perfil`, que es lo que impide inventar normativa."""
from __future__ import annotations

import yaml

from herramientas import verificar_perfil as V
from tests.conftest import escribir_perfil


def _revisar(proyecto, pid="prueba"):
    inf = V.Informe("t", "t", raiz=proyecto)
    V.revisar(pid, inf, proyecto)
    return inf


def _guardar(proyecto, pid, datos):
    (proyecto / "perfiles").mkdir(parents=True, exist_ok=True)
    (proyecto / "perfiles" / f"{pid}.yaml").write_text(
        yaml.safe_dump(datos, allow_unicode=True, sort_keys=False), encoding="utf8")


def test_un_perfil_correcto_no_da_errores(proyecto):
    escribir_perfil(proyecto)
    assert not _revisar(proyecto).hay_errores


def test_verificado_sin_el_pdf_en_disco_es_error(proyecto):
    """Regla R2: es la comprobación que sostiene todo el diseño."""
    escribir_perfil(proyecto)
    (proyecto / "normativa" / "prueba.pdf").unlink()
    errores = [h.codigo for h in _revisar(proyecto).errores]
    assert "P07" in errores


def test_verificado_sin_indicar_documento_es_error(proyecto):
    escribir_perfil(proyecto, fuente={"documento": "Algo", "norma": "RR 1"})
    assert "P06" in [h.codigo for h in _revisar(proyecto).errores]


def test_una_norma_de_posgrado_no_sustenta_pregrado(proyecto):
    """Regla R4."""
    escribir_perfil(proyecto, fuente={
        "documento": "Dictamen de la Unidad de Posgrado de Letras",
        "norma": "N.° 2", "archivo_local": "normativa/prueba.pdf"})
    assert "P10" in [h.codigo for h in _revisar(proyecto).errores]


def test_un_esquema_de_facto_no_habilita_verificado(proyecto):
    """Regla R3."""
    escribir_perfil(proyecto,
                    fuente={"documento": "Observación de tesis", "norma": None},
                    esquema_de_facto="normativa/facultades/x/esquema_de_facto.md")
    codigos = [h.codigo for h in _revisar(proyecto).errores]
    assert "P09" in codigos or "P06" in codigos


def test_esquema_de_facto_inexistente_es_error(proyecto):
    escribir_perfil(proyecto, esquema_de_facto="normativa/facultades/no/existe.md")
    assert "P13" in [h.codigo for h in _revisar(proyecto).errores]


def test_un_perfil_sin_modelos_de_informe_es_error(proyecto):
    escribir_perfil(proyecto, informe_final={"origen": "plantilla_norma", "modelos": {}})
    assert "P14" in [h.codigo for h in _revisar(proyecto).errores]


def test_estado_invalido_es_error(proyecto):
    escribir_perfil(proyecto, estado="mas_o_menos")
    codigos = [h.codigo for h in _revisar(proyecto).errores]
    assert "P05" in codigos or "P04" in codigos


def test_yaml_roto_se_reporta_sin_reventar(proyecto):
    (proyecto / "perfiles").mkdir(parents=True, exist_ok=True)
    (proyecto / "perfiles" / "roto.yaml").write_text(
        "id: roto\n  mal: [indentado\n", encoding="utf8")
    inf = _revisar(proyecto, "roto")
    assert "P01" in [h.codigo for h in inf.errores]


def test_falta_un_campo_obligatorio(proyecto):
    _guardar(proyecto, "pelado", {"id": "pelado", "estado": "verificado"})
    codigos = [h.codigo for h in _revisar(proyecto, "pelado").errores]
    assert "P03" in codigos


def test_el_id_debe_coincidir_con_el_nombre_del_archivo(proyecto):
    escribir_perfil(proyecto, pid="prueba")
    ruta = proyecto / "perfiles" / "prueba.yaml"
    datos = yaml.safe_load(ruta.read_text(encoding="utf8"))
    datos["id"] = "otro"
    ruta.write_text(yaml.safe_dump(datos, allow_unicode=True), encoding="utf8")
    assert "P02" in [h.codigo for h in _revisar(proyecto).errores]


def test_un_perfil_no_verificado_debe_advertir_al_tesista(proyecto):
    escribir_perfil(proyecto, estado="hereda_general",
                    fuente={"documento": "(sin documento propio)", "norma": None,
                            "archivo_local": None})
    inf = _revisar(proyecto)
    assert "P15" in [h.codigo for h in inf.avisos]


def test_un_perfil_no_verificado_con_advertencias_solo_informa(proyecto):
    escribir_perfil(proyecto, estado="hereda_general",
                    fuente={"documento": "(sin documento propio)", "norma": None,
                            "archivo_local": None},
                    advertencias_al_tesista=["Confirma con tu asesor."])
    inf = _revisar(proyecto)
    assert not inf.hay_errores
    assert "P16" in [h.codigo for h in inf.hallazgos]


def test_los_perfiles_reales_del_repositorio_pasan():
    """La prueba de regresión que protege los 21 perfiles ya escritos."""
    inf = V.verificar()
    assert not inf.hay_errores, [h.mensaje for h in inf.errores]
    assert inf.contexto["cobertura"].startswith("20 de 20")
