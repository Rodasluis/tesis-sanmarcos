"""Valida las skills, los agentes y el catálogo de fuentes.

La prueba que más importa aquí: **ningún crítico puede editar archivos.** La
especificación lo exige y la única forma de que sea cierto es que su lista de
herramientas no incluya Write ni Edit. Una instrucción en el texto del agente no
basta: un modelo puede saltársela, una lista de herramientas no.
"""
from __future__ import annotations

import pathlib
import re

import pytest
import yaml

RAIZ = pathlib.Path(__file__).resolve().parent.parent
SKILLS = RAIZ / ".claude" / "skills"
AGENTES = RAIZ / ".claude" / "agents"
CATALOGO = RAIZ / "herramientas" / "fuentes" / "catalogo.yaml"

HERRAMIENTAS_DE_ESCRITURA = {"Write", "Edit", "MultiEdit", "NotebookEdit"}

#: Las once etapas del flujo, en orden. Cada una es una skill.
SKILLS_DE_ETAPA = {"iniciar", "explorar-datos", "afinar-idea", "literatura",
                   "proyecto", "analizar", "redactar", "jurado", "verificar",
                   "entregar", "sustentacion"}

#: Auxiliares. No son etapas: no marcan etapa ni cierran con decisión propia.
#: `/estado` informa sobre las etapas y marcarlas falsearía el registro.
SKILLS_AUXILIARES = {"autopiloto", "estado", "asesor", "checkpoint"}

SKILLS_ESPERADAS = SKILLS_DE_ETAPA | SKILLS_AUXILIARES

PARES = {
    "explorador-datos": "critico-datos",
    "afinador-ideas": "critico-identificacion",
    "bibliotecario": "critico-citas",
    "analista": "critico-codigo",
    "codificador-cualitativo": "critico-codificacion",
    "redactor": "critico-redaccion",
    "normativo": "critico-perfil",
}

#: La etapa 7 no es un par: son tres lectores hostiles, y de solo lectura.
JURADOS = {"jurado-metodologico", "jurado-tematico", "jurado-formal"}


def _plano(texto: str) -> str:
    """El texto sin saltos de línea, para buscar frases en él.

    Todos los .md van ajustados a 80 columnas, así que cualquier frase de más de
    media docena de palabras cruza un salto. Comparar contra el texto crudo
    comprueba el ajuste de línea, no el contenido.
    """
    return re.sub(r"\s+", " ", texto)


def _frontmatter(ruta: pathlib.Path) -> tuple[dict, str]:
    texto = ruta.read_text(encoding="utf8")
    m = re.match(r"^---\n(.*?)\n---\n(.*)$", texto, re.S)
    if not m:
        raise AssertionError(f"{ruta.name}: no tiene frontmatter YAML")
    return yaml.safe_load(m.group(1)) or {}, m.group(2)


def skills() -> list[pathlib.Path]:
    return sorted(SKILLS.glob("*/SKILL.md"))


def agentes() -> list[pathlib.Path]:
    return sorted(AGENTES.glob("*.md"))


def skills_de_etapa() -> list[pathlib.Path]:
    return [p for p in skills() if p.parent.name in SKILLS_DE_ETAPA]


def skills_auxiliares() -> list[pathlib.Path]:
    return [p for p in skills() if p.parent.name in SKILLS_AUXILIARES]


# --- skills ----------------------------------------------------------------

def test_esta_una_skill_por_cada_etapa_y_auxiliar():
    encontradas = {p.parent.name for p in skills()}
    assert encontradas >= SKILLS_ESPERADAS, f"faltan: {SKILLS_ESPERADAS - encontradas}"


def test_cada_skill_es_etapa_o_auxiliar():
    """Una skill que no es ninguna de las dos cosas no tiene lugar en el flujo."""
    sueltas = {p.parent.name for p in skills()} - SKILLS_ESPERADAS
    assert not sueltas, f"skills sin clasificar: {sueltas}"


@pytest.mark.parametrize("ruta", skills(), ids=lambda p: p.parent.name)
def test_cada_skill_tiene_frontmatter_valido(ruta):
    meta, cuerpo = _frontmatter(ruta)
    assert meta.get("name"), f"{ruta.parent.name}: falta `name`"
    assert meta.get("description"), f"{ruta.parent.name}: falta `description`"
    assert len(cuerpo.strip()) > 400, "el cuerpo es demasiado corto para guiar una etapa"


@pytest.mark.parametrize("ruta", skills(), ids=lambda p: p.parent.name)
def test_el_nombre_de_la_skill_coincide_con_su_carpeta(ruta):
    meta, _ = _frontmatter(ruta)
    assert meta["name"] == ruta.parent.name


@pytest.mark.parametrize("ruta", skills(), ids=lambda p: p.parent.name)
def test_las_skills_son_comandos_explicitos(ruta):
    """Son etapas del flujo: las invoca el tesista, no se disparan solas."""
    meta, _ = _frontmatter(ruta)
    assert meta.get("disable-model-invocation") is True


@pytest.mark.parametrize("ruta", skills_de_etapa(), ids=lambda p: p.parent.name)
def test_cada_skill_de_etapa_marca_su_etapa(ruta):
    """Sin esto el registro de IA no sabe a qué etapa pertenece lo que se hace."""
    _, cuerpo = _frontmatter(ruta)
    assert "marcar_etapa" in cuerpo, "la skill debe marcar la etapa en curso"


@pytest.mark.parametrize("ruta", skills_de_etapa(), ids=lambda p: p.parent.name)
def test_cada_skill_de_etapa_cierra_con_un_punto_de_decision(ruta):
    _, cuerpo = _frontmatter(ruta)
    assert "registrar_decision" in cuerpo or "Punto de decisión" in cuerpo


@pytest.mark.parametrize("ruta", [p for p in skills_auxiliares()
                                  if p.parent.name != "autopiloto"],
                         ids=lambda p: p.parent.name)
def test_las_auxiliares_no_marcan_etapa(ruta):
    """`/estado` informa sobre las etapas; marcarlas falsearía el registro.

    `/autopiloto` queda fuera porque sí corre etapas: las encadena.
    """
    _, cuerpo = _frontmatter(ruta)
    assert "marcar_etapa(" not in cuerpo, (
        f"{ruta.parent.name} no es una etapa y no debe marcar ninguna")


#: Hablar de que el asesor confirme algo solo vale para negarlo.
PUERTA = re.compile(r"(confirmaci[óo]n del asesor|que (un|el) asesor confirme|"
                    r"sin (la )?confirmaci[óo]n de)", re.I)
NEGACION = re.compile(r"\b(no|nada|ning[úu]n|ninguna|nunca|sin)\b", re.I)


@pytest.mark.parametrize("ruta", skills(), ids=lambda p: p.parent.name)
def test_ninguna_skill_condiciona_el_avance_a_un_asesor(ruta):
    """Decisión del usuario: nada queda afecto a que un asesor confirme.

    No basta con que la frase no aparezca: `/asesor` tiene que poder decir que
    el asesor **no** es una puerta. Así que se admite la mención y se exige que
    la frase donde aparece la niegue.
    """
    _, cuerpo = _frontmatter(ruta)
    for frase in re.split(r"(?<=[.:;])\s+", _plano(cuerpo)):
        hallado = PUERTA.search(frase)
        if hallado and not NEGACION.search(frase):
            raise AssertionError(
                f"{ruta.parent.name} condiciona el avance: «{frase.strip()}»")


def test_iniciar_no_pide_requisitos_administrativos():
    _, cuerpo = _frontmatter(SKILLS / "iniciar" / "SKILL.md")
    assert "No preguntes si tiene el grado de bachiller" in cuerpo
    assert "Nada de eso condiciona nada" in cuerpo


# --- agentes ---------------------------------------------------------------

def test_estan_los_pares_trabajador_critico():
    nombres = {p.stem for p in agentes()}
    for trabajador, critico in PARES.items():
        assert trabajador in nombres, f"falta el trabajador {trabajador}"
        assert critico in nombres, f"falta el crítico {critico}"


@pytest.mark.parametrize("ruta", agentes(), ids=lambda p: p.stem)
def test_cada_agente_tiene_frontmatter_valido(ruta):
    meta, cuerpo = _frontmatter(ruta)
    assert meta.get("name"), f"{ruta.stem}: falta `name`"
    assert meta.get("description"), f"{ruta.stem}: falta `description`"
    assert meta["name"] == ruta.stem
    assert ":" not in meta["name"] and not meta["name"].startswith("-")
    assert len(cuerpo.strip()) > 300


@pytest.mark.parametrize("ruta", [p for p in agentes() if p.stem.startswith("critico-")],
                         ids=lambda p: p.stem)
def test_ningun_critico_puede_editar_archivos(ruta):
    """La regla de la sección 8, hecha estructura y no buena intención."""
    meta, _ = _frontmatter(ruta)
    herramientas = meta.get("tools")
    assert herramientas, (
        f"{ruta.stem}: un crítico DEBE declarar `tools`. Sin lista explícita "
        "hereda todas las herramientas, incluidas Write y Edit.")
    if isinstance(herramientas, str):
        permitidas = {h.strip() for h in herramientas.split(",")}
    else:
        permitidas = set(herramientas)
    prohibidas = permitidas & HERRAMIENTAS_DE_ESCRITURA
    assert not prohibidas, f"{ruta.stem} puede escribir con: {prohibidas}"


@pytest.mark.parametrize("ruta", [p for p in agentes() if p.stem.startswith("critico-")],
                         ids=lambda p: p.stem)
def test_cada_critico_dice_que_no_edita(ruta):
    """Además de no poder, lo dice: el modelo debe saber cuál es su papel."""
    _, cuerpo = _frontmatter(ruta)
    assert re.search(r"No puedes editar archivos", cuerpo), (
        f"{ruta.stem}: el cuerpo debe decir explícitamente que no edita")


@pytest.mark.parametrize("ruta", [p for p in agentes() if p.stem.startswith("critico-")],
                         ids=lambda p: p.stem)
def test_cada_critico_exige_criterio_de_refutacion(ruta):
    """«Qué me haría cambiar de opinión» convierte una opinión en una crítica."""
    _, cuerpo = _frontmatter(ruta)
    assert re.search(r"(cambiar de opinión|lo arreglaría|lo cambiaría|debería decir)",
                     cuerpo, re.I)


@pytest.mark.parametrize("ruta", agentes(), ids=lambda p: p.stem)
def test_ningun_agente_aprueba_nada(ruta):
    """Ningún agente emite un visto bueno: la decisión es del tesista."""
    _, cuerpo = _frontmatter(ruta)
    assert not re.search(r"\bdas el visto bueno\b|\bapruebas la tesis\b", cuerpo, re.I)


# --- catálogo de fuentes ---------------------------------------------------

ESTADOS_VALIDOS = {"api_verificada", "api_bloqueada", "manual_verificada", "verificar"}


def catalogo() -> dict:
    return yaml.safe_load(CATALOGO.read_text(encoding="utf8"))


def test_el_catalogo_parsea_y_tiene_fuentes():
    datos = catalogo()
    assert datos.get("comprobado"), "el catálogo debe decir cuándo se comprobó"
    assert len(datos["fuentes"]) >= 15


@pytest.mark.parametrize("fuente", catalogo()["fuentes"], ids=lambda f: f["id"])
def test_cada_fuente_esta_completa(fuente):
    for campo in ("id", "nombre", "url", "estado", "tipo_acceso", "facultades"):
        assert fuente.get(campo), f"{fuente.get('id')}: falta `{campo}`"
    assert fuente["estado"] in ESTADOS_VALIDOS
    assert str(fuente["url"]).startswith("http")


@pytest.mark.parametrize("fuente", catalogo()["fuentes"], ids=lambda f: f["id"])
def test_lo_no_verificado_no_se_presenta_como_api(fuente):
    """Una fuente que no respondió no puede ofrecerse como acceso programático."""
    if fuente["estado"] in ("api_bloqueada", "verificar"):
        assert fuente["tipo_acceso"] != "api", (
            f"{fuente['id']}: estado `{fuente['estado']}` pero se ofrece como API")


@pytest.mark.parametrize("fuente", catalogo()["fuentes"], ids=lambda f: f["id"])
def test_lo_bloqueado_explica_por_que_y_que_hacer(fuente):
    if fuente["estado"] in ("api_bloqueada", "verificar"):
        assert fuente.get("notas"), f"{fuente['id']}: debe explicar qué pasó"


def test_el_bcrp_no_se_presenta_como_api_usable():
    """Se comprobó: devuelve un muro anti-bot, no JSON."""
    bcrp = next(f for f in catalogo()["fuentes"] if f["id"] == "bcrp")
    assert bcrp["estado"] == "api_bloqueada"
    assert bcrp["tipo_acceso"] == "manual"
    assert bcrp.get("descarga_manual"), "debe decir cómo descargarlo a mano"


def test_las_apis_verificadas_traen_un_ejemplo_probado():
    for fuente in catalogo()["fuentes"]:
        if fuente["estado"] == "api_verificada":
            assert fuente.get("ejemplo"), f"{fuente['id']}: falta `ejemplo`"
            assert "{" not in fuente["ejemplo"], "el ejemplo debe ser una URL real"


def test_el_catalogo_recuerda_las_reglas_de_uso():
    reglas = " ".join(catalogo()["reglas"])
    assert "datos/crudos/" in reglas
    assert "29733" in reglas
    assert "factor de expansión" in reglas


# --- encuestas que no son del INEI -----------------------------------------
#
# El error de búsqueda más caro de una tesis peruana es suponer que todo lo que
# se encuesta lo encuesta el INEI. Estas pruebas protegen lo contrario.

def _fuente(ident: str) -> dict:
    return next(f for f in catalogo()["fuentes"] if f["id"] == ident)


def test_el_inei_lista_sus_encuestas_nacionales():
    siglas = {e["sigla"] for e in _fuente("inei_microdatos")["encuestas"]}
    assert {"ENAHO", "ENDES", "ENAPRES", "CENSOS"} <= siglas


def test_el_inei_declara_las_encuestas_que_aloja_por_encargo():
    """ENA es del MIDAGRI y ENSUSALUD de SUSALUD, pero viven en el INEI."""
    encuestas = {e["sigla"]: e for e in _fuente("inei_microdatos")["encuestas"]}
    assert "ENA" in encuestas and encuestas["ENA"].get("encargada_por")
    assert "ENSUSALUD" in encuestas and encuestas["ENSUSALUD"].get("encargada_por")
    notas = _fuente("inei_microdatos")["notas"]
    assert "por encargo" in notas


@pytest.mark.parametrize("ident", ["sbs", "osiptel", "osinergmin", "produce",
                                   "mtpe", "smv", "sunat", "sunass"])
def test_estan_las_fuentes_de_organismos_supervisores(ident):
    assert _fuente(ident)


@pytest.mark.parametrize("ident,encuesta", [
    ("sbs", "Demanda de Servicios Financieros"),
    ("osiptel", "ERESTEL"),
    ("osinergmin", "ERCUE"),
])
def test_cada_regulador_con_encuesta_la_nombra(ident, encuesta):
    fuente = _fuente(ident)
    texto = str(fuente.get("encuestas", "")) + str(fuente.get("notas", ""))
    assert encuesta in texto


def test_osiptel_declara_oai_y_no_una_api_json_que_no_existe():
    """Su REST moderna devuelve 404; lo que funciona es OAI-PMH."""
    osiptel = _fuente("osiptel")
    assert osiptel["estado"] == "api_verificada"
    assert "oai" in osiptel["api"].lower()
    assert "OAI-PMH" in osiptel["notas"]


def test_las_fuentes_de_registro_administrativo_declaran_su_limite():
    """Un registro administrativo no tiene error muestral, pero sí omisiones."""
    assert "informal" in _fuente("mtpe")["notas"]
    assert "listadas" in _fuente("smv")["notas"]
    assert "agregados" in _fuente("sunat")["notas"]


def test_el_explorador_sabe_que_hay_encuestas_fuera_del_inei():
    agente = (RAIZ / ".claude" / "agents" / "explorador-datos.md").read_text(encoding="utf8")
    assert "No todo lo que se encuesta lo encuesta el INEI" in agente
    for sigla in ("ERESTEL", "ERCUE", "SBS", "Planilla Electrónica"):
        assert sigla in agente


# --- fuentes internacionales y privadas ------------------------------------

@pytest.mark.parametrize("ident", ["bm_microdatos", "dhs", "young_lives", "ipums",
                                   "bm_enterprise_surveys",
                                   "encuestas_regionales_comparadas"])
def test_estan_los_microdatos_internacionales_con_peru(ident):
    assert _fuente(ident)


@pytest.mark.parametrize("ident", ["who_gho", "ilostat", "unesco_uis", "comtrade",
                                   "owid", "faostat", "doaj"])
def test_estan_las_apis_de_organismos_internacionales(ident):
    assert _fuente(ident)["estado"] == "api_verificada"


@pytest.mark.parametrize("ident", ["grade", "think_tanks_peru",
                                   "mercado_financiero_peru", "encuestadoras_peru"])
def test_estan_las_fuentes_privadas_peruanas(ident):
    assert _fuente(ident)


def test_el_catalogo_explica_que_endes_es_parte_de_dhs():
    """Es lo que permite comparar al Perú con otros países con la misma medición."""
    notas = _fuente("dhs")["notas"]
    assert "ENDES" in notas
    assert "comparables con otros países" in notas or "comparables" in notas


def test_young_lives_se_presenta_como_longitudinal():
    notas = _fuente("young_lives")["notas"]
    assert "longitudinal" in notas.lower()
    assert "2002" in notas


def test_las_fuentes_privadas_declaran_que_no_son_oficiales():
    """Citar una encuestadora como si fuera el INEI es un error de fondo."""
    assert "no son fuentes oficiales" in _fuente("think_tanks_peru")["notas"].lower()
    assert "ficha" in _fuente("encuestadoras_peru")["notas"].lower()


def test_las_fuentes_con_registro_lo_advierten():
    """Un microdato que exige cuenta no se puede prometer como descarga directa."""
    for ident in ("bm_microdatos", "dhs", "ipums", "young_lives"):
        fuente = _fuente(ident)
        texto = str(fuente.get("notas", "")) + str(fuente.get("descarga_manual", ""))
        assert "registr" in texto.lower(), f"{ident}: no advierte que pide registro"


def test_owid_y_osiptel_declaran_formatos_que_no_son_json():
    """El verificador acepta CSV y XML como acceso programático; el catálogo lo dice."""
    assert ".csv" in _fuente("owid")["ejemplo"]
    assert "oai" in _fuente("osiptel")["api"].lower()


# --- fase 5: etapas 6 a 10 y auxiliares ------------------------------------

def _cuerpo(skill: str) -> str:
    return _plano(_frontmatter(SKILLS / skill / "SKILL.md")[1])


def _agente(nombre: str) -> str:
    return _plano(_frontmatter(AGENTES / f"{nombre}.md")[1])


def test_redactar_nombra_sus_tres_fuentes_y_ninguna_mas():
    """El principio 1 y el 2, hechos instrucción: decisiones, resultados, bib."""
    cuerpo = _cuerpo("redactar")
    for fuente in ("decisiones/", "resultados/", "referencias.bib"):
        assert fuente in cuerpo, f"redactar no nombra {fuente}"
    assert "[VERIFICAR]" in cuerpo


def test_redactar_separa_resultados_de_discusion():
    """Es el error más frecuente y el que un jurado detecta primero."""
    cuerpo = _cuerpo("redactar")
    assert re.search(r"En V no se interpreta", cuerpo)
    assert re.search(r"En VI no aparecen cifras nuevas", cuerpo)


def test_redactar_respeta_las_ediciones_del_tesista():
    """Principio 4: las ediciones a mano se respetan en las regeneraciones."""
    cuerpo = _cuerpo("redactar").lower()
    assert "ediciones del tesista se conservan" in cuerpo or \
           "ediciones del tesista se respetan" in cuerpo


def test_redactar_toma_el_estilo_del_perfil_y_no_del_motor():
    """Principio 7: persona gramatical y estilo de citas los fija el perfil."""
    cuerpo = _cuerpo("redactar")
    assert "Persona gramatical" in cuerpo
    assert "PENDIENTE-NORMATIVA" in cuerpo


def test_jurado_dice_que_no_es_una_nota_ni_un_pronostico():
    """Una simulación presentada como aprobación deja al tesista peor que antes."""
    cuerpo = _cuerpo("jurado")
    assert "No predice la calificación y no aprueba nada" in cuerpo
    assert "puntos ciegos" in cuerpo


def test_jurado_lanza_los_tres_jurados():
    cuerpo = _cuerpo("jurado")
    for agente in JURADOS:
        assert agente in cuerpo, f"/jurado no lanza {agente}"


def test_jurado_guarda_las_observaciones_no_atendidas():
    """Lo que se decide no atender vuelve como pregunta en la sustentación."""
    cuerpo = _cuerpo("jurado")
    assert "no atender" in cuerpo
    assert "banco_preguntas" in cuerpo


def test_jurado_no_da_por_respondida_una_pregunta_del_tesista():
    cuerpo = _cuerpo("jurado")
    assert "respuesta_apoyo" in cuerpo
    assert "no la respuesta del tesista" in cuerpo


def test_verificar_distingue_el_puntaje_de_una_nota():
    cuerpo = _cuerpo("verificar")
    assert "No son una nota" in cuerpo
    assert "no los pone" in cuerpo and "universidad" in cuerpo


def test_verificar_niega_que_la_similitud_interna_sea_turnitin():
    """Es el malentendido más caro: el umbral de 20 % se mide en PIDS."""
    cuerpo = _cuerpo("verificar")
    assert "no es Turnitin" in cuerpo
    assert "PIDS" in cuerpo
    assert "no hay forma de conocer ese número desde aquí" in cuerpo


def test_verificar_nombra_lo_que_ninguna_herramienta_comprueba():
    """Un informe en verde invita a olvidar justo lo que decide la sustentación."""
    cuerpo = _cuerpo("verificar")
    assert "ninguna herramienta puede comprobar" in cuerpo


def test_verificar_no_arregla_una_cita_inexistente_cambiandola():
    cuerpo = _cuerpo("verificar").lower()
    assert "no se cambia por otra que sí exista" in cuerpo


def test_entregar_pide_los_dos_docx_con_las_carpetas_del_articulo_13():
    cuerpo = _cuerpo("entregar")
    assert "TEXTO/" in cuerpo and "DOCUMENTO/" in cuerpo
    assert "El entregable es .docx" in cuerpo
    assert "El PDF no sirve" in cuerpo


def test_entregar_presenta_la_declaracion_de_ia_como_voluntaria():
    """Principio 5: ninguna norma leída la exige y no se presenta como requisito."""
    cuerpo = _cuerpo("entregar")
    assert "no la exige ninguna norma leída" in cuerpo
    assert "No le digas que tiene que entregarla" in cuerpo


def test_entregar_distingue_el_anexo_4_de_la_declaracion_de_ia():
    """Una es requisito y la otra no: confundirlas desinforma al tesista."""
    cuerpo = _cuerpo("entregar")
    assert "Anexo 4 sí es un requisito" in cuerpo


def test_entregar_trata_el_checklist_como_informacion_no_como_puerta():
    cuerpo = _cuerpo("entregar")
    assert "no una puerta" in cuerpo


def test_entregar_avisa_del_vencimiento_y_del_costo():
    cuerpo = _cuerpo("entregar")
    assert "90 días" in cuerpo
    assert "S/ 20" in cuerpo


def test_sustentacion_lee_los_tiempos_del_perfil_y_no_los_supone():
    cuerpo = _cuerpo("sustentacion")
    assert "No asumas veinte minutos" in cuerpo
    assert "PENDIENTE-NORMATIVA" in cuerpo


def test_sustentacion_trae_la_rubrica_cuando_el_perfil_la_tiene():
    """Medicina reparte 20 puntos en cinco criterios; el tesista debe verlos."""
    cuerpo = _cuerpo("sustentacion")
    assert "Coherencia entre aspectos metodológicos" in cuerpo
    assert "10 de 20 se ganan hablando" in cuerpo


def test_sustentacion_ensaya_decir_que_no_lo_sabe():
    """Inventar una respuesta ante el jurado es lo peor que puede pasar ahí."""
    cuerpo = _cuerpo("sustentacion")
    assert "No lo sé" in cuerpo and "dicho bien" in cuerpo


def test_sustentacion_no_pone_cifras_fuera_de_resultados():
    cuerpo = _cuerpo("sustentacion")
    assert "Cada cifra sale de `resultados/`" in cuerpo


def test_autopiloto_no_puede_registrar_una_decision_no_tomada():
    """El punto donde es más fácil violar el principio 3."""
    cuerpo = _cuerpo("autopiloto")
    assert "se niega" in cuerpo
    assert "No hay bandera para saltárselo" in cuerpo
    assert "respuesta_textual" in cuerpo


def test_autopiloto_no_acepta_haz_lo_que_creas_mejor_como_decision():
    cuerpo = _cuerpo("autopiloto")
    assert "haz lo que creas mejor" in cuerpo
    assert "no es una respuesta que puedas registrar" in cuerpo


def test_autopiloto_acuerda_el_alcance_antes_de_correr():
    cuerpo = _cuerpo("autopiloto")
    assert "hasta dónde" in cuerpo


def test_estado_esta_pensada_para_volver_despues_de_semanas():
    """El público son egresados que avanzan a ritmo irregular."""
    cuerpo = _cuerpo("estado")
    assert "semanas" in cuerpo
    assert "una cosa, concreta" in cuerpo.lower()


def test_estado_no_convierte_un_tramite_en_un_requisito():
    cuerpo = _cuerpo("estado")
    assert "Nunca como condición para seguir trabajando" in cuerpo


def test_estado_no_reprocha_el_tiempo_que_paso():
    cuerpo = _cuerpo("estado")
    assert "Sin comentarlo" in cuerpo or "no lo menciones como un problema" in cuerpo


def test_asesor_no_es_una_puerta():
    """Instrucción del usuario: nada queda afecto a la confirmación de un asesor."""
    cuerpo = _cuerpo("asesor")
    assert "No convierte al asesor en una puerta" in cuerpo
    assert "sin haber hablado con él" in cuerpo


def test_asesor_no_cede_ante_lo_que_la_normativa_prohibe():
    cuerpo = _cuerpo("asesor")
    assert "aunque lo pida un" in cuerpo


def test_asesor_distingue_la_observacion_de_la_decision():
    cuerpo = _cuerpo("asesor")
    assert "La observación del asesor no es la decisión" in cuerpo


def test_asesor_no_verifica_un_perfil_de_palabra():
    """Un perfil `verificado` necesita documento, no el recuerdo de una reunión."""
    cuerpo = _cuerpo("asesor")
    assert "no marques el perfil como `verificado`" in cuerpo


def test_checkpoint_deja_una_nota_de_retorno():
    cuerpo = _cuerpo("checkpoint")
    assert "retomar.md" in cuerpo
    assert "Lo primero que hay que hacer al volver" in cuerpo


def test_checkpoint_no_bloquea_por_errores_de_verificacion():
    """Guardar el avance a medias es mejor que perderlo."""
    cuerpo = _cuerpo("checkpoint").lower()
    assert "no bloquean el checkpoint" in cuerpo


def test_checkpoint_para_ante_datos_personales():
    cuerpo = _cuerpo("checkpoint")
    assert "datos_personales" in cuerpo
    assert "para" in cuerpo and "aquí" in cuerpo


# --- los tres jurados ------------------------------------------------------

def test_estan_los_tres_jurados():
    nombres = {p.stem for p in agentes()}
    assert nombres >= JURADOS, f"faltan: {JURADOS - nombres}"


@pytest.mark.parametrize("nombre", sorted(JURADOS))
def test_ningun_jurado_puede_editar_archivos(nombre):
    """Un jurado observa. Si pudiera editar, estaría arreglando lo que critica."""
    meta, _ = _frontmatter(AGENTES / f"{nombre}.md")
    herramientas = meta.get("tools")
    assert herramientas, (
        f"{nombre}: debe declarar `tools`. Sin lista explícita hereda todas, "
        "incluidas Write y Edit.")
    if isinstance(herramientas, str):
        permitidas = {h.strip() for h in herramientas.split(",")}
    else:
        permitidas = set(herramientas)
    assert not (permitidas & HERRAMIENTAS_DE_ESCRITURA)


@pytest.mark.parametrize("nombre", sorted(JURADOS))
def test_cada_jurado_dice_que_no_edita(nombre):
    cuerpo = _agente(nombre)
    assert "No puedes editar archivos" in cuerpo


@pytest.mark.parametrize("nombre", sorted(JURADOS))
def test_cada_jurado_formula_preguntas_y_no_solo_quejas(nombre):
    """El banco de preguntas de /sustentacion sale de aquí."""
    cuerpo = _agente(nombre)
    assert re.search(r"pregunta", cuerpo, re.I)
    assert re.search(r"(dificultad|alta, media o baja|por dificultad)", cuerpo, re.I)


@pytest.mark.parametrize("nombre", sorted(JURADOS))
def test_ningun_jurado_inventa_la_norma_que_dice_incumplida(nombre):
    cuerpo = _agente(nombre)
    assert re.search(r"(no inventes|Inventar|no lo afirmes)", cuerpo)


def test_el_jurado_metodologico_pregunta_por_el_factor_de_expansion():
    """Es la observación más fatal en tesis con ENAHO o ENDES."""
    cuerpo = _agente("jurado-metodologico")
    assert "factor de expansión" in cuerpo.lower()
    assert "p-hacking" in cuerpo


def test_el_jurado_metodologico_cubre_lo_cualitativo():
    """La mitad de los perfiles admite enfoque cualitativo."""
    cuerpo = _agente("jurado-metodologico")
    assert "saturación" in cuerpo.lower()
    assert "libro de códigos" in cuerpo.lower()


def test_el_jurado_tematico_no_inventa_referencias_que_faltan():
    """Pedir una cita recordada es exactamente cómo se inventan fuentes."""
    cuerpo = _agente("jurado-tematico")
    assert "Inventar una referencia" in cuerpo
    assert "no son una fuente" in cuerpo


def test_el_jurado_tematico_pide_literatura_peruana():
    cuerpo = _agente("jurado-tematico")
    assert "peruana" in cuerpo.lower()


def test_el_jurado_formal_no_trata_un_pendiente_como_incumplimiento():
    cuerpo = _agente("jurado-formal")
    assert "PENDIENTE-NORMATIVA" in cuerpo
    assert "no lo reportes como incumplimiento" in cuerpo


def test_el_jurado_formal_no_sugiere_evadir_la_similitud():
    """Principio 6, y art. 30 de la Directiva de originalidad."""
    cuerpo = _agente("jurado-formal")
    assert "art. 30" in cuerpo
    assert "reduzca artificialmente la similitud" in cuerpo


def test_el_jurado_formal_corrige_la_idea_de_haber_pasado_pids():
    cuerpo = _agente("jurado-formal")
    assert "no lo anticipa" in cuerpo
