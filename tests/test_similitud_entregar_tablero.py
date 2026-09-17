"""Pruebas de similitud interna, generación de entregables y tablero."""
from __future__ import annotations

import json

import yaml

from herramientas import entregar as E
from herramientas import similitud_interna as S
from herramientas import tablero as T
from herramientas.entregar import Autor, nombre_archivo
from herramientas.registrar_decision import registrar
from tests.conftest import escribir_capitulo, escribir_perfil

PASAJE = ("el canon minero transfirio recursos significativos a los gobiernos "
          "locales de la region durante el periodo analizado lo que modifico "
          "sustancialmente su capacidad de gasto corriente y de inversion publica")


# --- similitud -------------------------------------------------------------

def test_avisa_de_un_pasaje_repetido_entre_capitulos(proyecto):
    escribir_capitulo(proyecto, "02_marco", f"# Marco teórico\n\n{PASAJE}.\n")
    escribir_capitulo(proyecto, "06_discusion", f"# Discusión\n\n{PASAJE}.\n")
    inf = S.verificar(proyecto)
    assert any(h.codigo == "S02" for h in inf.avisos)


def test_no_avisa_si_no_hay_repeticiones(proyecto):
    escribir_capitulo(proyecto, "02_marco", "# Marco teórico\n\nUn texto corto y único.\n")
    escribir_capitulo(proyecto, "06_discusion",
                      "# Discusión\n\nOtro texto distinto del anterior.\n")
    inf = S.verificar(proyecto)
    assert not any(h.codigo == "S02" for h in inf.hallazgos)


def test_siempre_aclara_que_no_es_turnitin(proyecto):
    inf = S.verificar(proyecto)
    assert any("NO mide el porcentaje de similitud oficial" in h.mensaje
               for h in inf.hallazgos)


def test_avisa_si_la_biblioteca_no_existe(proyecto):
    escribir_capitulo(proyecto, "c", "# T\n\nTexto.\n")
    inf = S.verificar(proyecto, biblioteca=proyecto / "no_existe")
    assert any(h.codigo == "S04" for h in inf.avisos)


def test_sin_biblioteca_lo_dice_en_lugar_de_callarse(proyecto):
    escribir_capitulo(proyecto, "c", "# T\n\nTexto.\n")
    inf = S.verificar(proyecto)
    assert any(h.codigo == "S03" for h in inf.hallazgos)


def test_un_pasaje_entrecomillado_no_es_error(proyecto):
    """El texto citado correctamente no debe reportarse como copiado."""
    escribir_capitulo(proyecto, "a", f'# A\n\nSegún el autor, «{PASAJE}» [@x, p. 3].\n')
    escribir_capitulo(proyecto, "b", f'# B\n\nSegún el autor, «{PASAJE}» [@x, p. 3].\n')
    inf = S.verificar(proyecto)
    assert not inf.hay_errores


# --- nomenclatura del art. 13 ---------------------------------------------

def test_nombre_de_archivo_sigue_el_ejemplo_de_la_directiva():
    autores = [Autor("Julca Pereda", "Dante Jorge")]
    nombre = nombre_archivo(autores, "Desarrollo",
                            "Competencia digitales en personas adultas", 2025)
    assert nombre == ("Julca Pereda Dante Jorge - Desarrollo "
                      "Competencia digitales en personas adultas - 2025.docx")


def test_nombre_del_segundo_archivo():
    autores = [Autor("Julca Pereda", "Dante Jorge")]
    nombre = nombre_archivo(autores, "Protocolo y Complemento",
                            "Competencia digitales en personas adultas", 2025)
    assert nombre.startswith("Julca Pereda Dante Jorge - Protocolo y Complemento ")


def test_quita_caracteres_que_windows_no_admite():
    autores = [Autor("Pérez", "Ana")]
    nombre = nombre_archivo(autores, "Desarrollo", 'Título con "comillas": y / barra', 2026)
    assert not any(c in nombre for c in '<>:"/\\|?*')


def test_tesis_grupal_nombra_a_todos_los_autores():
    autores = [Autor("Pérez", "Ana"), Autor("Quispe", "Luis")]
    nombre = nombre_archivo(autores, "Desarrollo", "Un título", 2026)
    assert "Pérez Ana y Quispe Luis" in nombre


# --- entregables -----------------------------------------------------------

def _datos(proyecto, **cambios):
    datos = {
        "titulo": "Determinantes del gasto municipal en el Perú",
        "anio": 2026,
        "autores": [{"apellidos": "Pérez", "nombres": "Ana", "dni": "12345678",
                     "objetivos": []}],
        "asesor": {"nombres_y_apellidos": "Dr. X", "correo": "x@unmsm.edu.pe"},
    }
    datos.update(cambios)
    (proyecto / "entregables").mkdir(parents=True, exist_ok=True)
    (proyecto / "entregables" / "datos_de_entrega.yaml").write_text(
        yaml.safe_dump(datos, allow_unicode=True), encoding="utf8")
    return datos


def test_crea_la_plantilla_de_datos_si_falta(proyecto):
    escribir_perfil(proyecto)
    inf = E.preparar(proyecto, solo_comprobar=True)
    assert any(h.codigo == "T07" for h in inf.errores)
    assert (proyecto / "entregables" / "datos_de_entrega.yaml").exists()


def test_mas_de_tres_autores_es_error(proyecto):
    escribir_perfil(proyecto)
    _datos(proyecto, autores=[{"apellidos": f"A{i}", "nombres": "N",
                               "objetivos": ["o"]} for i in range(4)])
    inf = E.preparar(proyecto, solo_comprobar=True)
    assert any(h.codigo == "T03" for h in inf.errores)


def test_tesis_grupal_sin_objetivos_por_autor_es_error(proyecto):
    escribir_perfil(proyecto)
    _datos(proyecto, autores=[{"apellidos": "Pérez", "nombres": "Ana", "objetivos": []},
                              {"apellidos": "Quispe", "nombres": "Luis", "objetivos": []}])
    inf = E.preparar(proyecto, solo_comprobar=True)
    errores = [h for h in inf.errores if h.codigo == "T04"]
    assert errores and "objetivos definidos" in errores[0].mensaje


def test_genera_el_expediente_completo(proyecto):
    escribir_perfil(proyecto)
    _datos(proyecto)
    escribir_capitulo(proyecto, "01_introduccion", "# Introducción\n\nTexto.\n")
    E.preparar(proyecto, solo_comprobar=True)
    documento = proyecto / "entregables" / "DOCUMENTO"
    assert (documento / "declaracion_jurada_pids.md").exists()
    assert (documento / "declaracion_uso_de_ia.md").exists()
    assert (documento / "checklist_expediente.md").exists()


def test_la_declaracion_de_ia_dice_que_es_voluntaria(proyecto):
    escribir_perfil(proyecto)
    _datos(proyecto)
    E.preparar(proyecto, solo_comprobar=True)
    texto = (proyecto / "entregables" / "DOCUMENTO" /
             "declaracion_uso_de_ia.md").read_text(encoding="utf8")
    assert "voluntaria" in texto.lower()
    assert "ninguna norma" in texto.lower()


def test_la_declaracion_jurada_reproduce_el_anexo_4(proyecto):
    escribir_perfil(proyecto)
    _datos(proyecto)
    E.preparar(proyecto, solo_comprobar=True)
    texto = (proyecto / "entregables" / "DOCUMENTO" /
             "declaracion_jurada_pids.md").read_text(encoding="utf8")
    assert "DECLARO BAJO JURAMENTO" in texto
    assert "Plataforma PIDS" in texto
    assert "12345678" in texto


def test_el_checklist_incluye_la_vigencia_de_noventa_dias(proyecto):
    escribir_perfil(proyecto)
    _datos(proyecto)
    E.preparar(proyecto, solo_comprobar=True)
    texto = (proyecto / "entregables" / "DOCUMENTO" /
             "checklist_expediente.md").read_text(encoding="utf8")
    assert "90 días" in texto
    assert "S/ 20" in texto


def test_el_checklist_pide_comite_de_etica_si_el_perfil_lo_exige(proyecto):
    escribir_perfil(proyecto, etica={"comite_requerido": True,
                                     "consentimiento": "obligatorio"})
    _datos(proyecto)
    E.preparar(proyecto, solo_comprobar=True)
    texto = (proyecto / "entregables" / "DOCUMENTO" /
             "checklist_expediente.md").read_text(encoding="utf8")
    assert "Comité de Ética" in texto


def test_la_declaracion_de_ia_resume_el_registro(proyecto):
    escribir_perfil(proyecto)
    _datos(proyecto)
    registro = proyecto / "registro" / "registro_ia.jsonl"
    registro.parent.mkdir(parents=True, exist_ok=True)
    registro.write_text(
        json.dumps({"etapa": "redactar", "accion": "escribir"}) + "\n" +
        json.dumps({"etapa": "redactar", "accion": "editar"}) + "\n",
        encoding="utf8")
    E.preparar(proyecto, solo_comprobar=True)
    texto = (proyecto / "entregables" / "DOCUMENTO" /
             "declaracion_uso_de_ia.md").read_text(encoding="utf8")
    assert "**2**" in texto and "redactar" in texto


# --- tablero ---------------------------------------------------------------

def test_genera_un_html_autocontenido(proyecto):
    escribir_perfil(proyecto)
    destino = T.generar(proyecto, proyecto / "registro" / "tablero.html")
    html = destino.read_text(encoding="utf8")
    assert html.startswith("<!doctype html>")
    assert "<script" not in html.lower()
    assert "http://" not in html and "https://" not in html


def test_el_tablero_avisa_del_bib_vacio(proyecto):
    escribir_perfil(proyecto)
    datos = T.recolectar(proyecto)
    assert any("referencias.bib" in a["texto"] for a in datos["alertas"])


def test_el_tablero_avisa_si_el_perfil_no_esta_verificado(proyecto):
    escribir_perfil(proyecto, estado="hereda_general")
    datos = T.recolectar(proyecto)
    assert any("confirme la estructura" in a["texto"] for a in datos["alertas"])


def test_el_tablero_cuenta_las_etapas_decididas(proyecto):
    escribir_perfil(proyecto)
    registrar({"etapa": "iniciar", "eleccion": "A", "respuesta_textual": "sí",
               "aprobado": True, "preguntas_comprension": []},
              proyecto / "decisiones")
    datos = T.recolectar(proyecto)
    assert datos["decididas"] == 1


def test_el_estado_nunca_va_solo_con_color(proyecto):
    """Cada chip lleva símbolo y etiqueta además del color."""
    escribir_perfil(proyecto)
    html = T.construir_html(T.recolectar(proyecto))
    for estado in T.ESTADOS.values():
        if estado["etiqueta"] in html:
            assert estado["simbolo"] in html


def test_el_tablero_recuerda_que_no_certifica_nada(proyecto):
    escribir_perfil(proyecto)
    html = T.construir_html(T.recolectar(proyecto))
    assert "No certifica nada" in html
    assert "PIDS" in html
