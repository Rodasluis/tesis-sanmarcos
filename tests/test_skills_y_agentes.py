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

#: Las seis etapas que cubre la fase 4.
SKILLS_ESPERADAS = {"iniciar", "explorar-datos", "afinar-idea", "literatura",
                    "proyecto", "analizar"}

PARES = {
    "explorador-datos": "critico-datos",
    "afinador-ideas": "critico-identificacion",
    "bibliotecario": "critico-citas",
    "analista": "critico-codigo",
    "codificador-cualitativo": "critico-codificacion",
    "normativo": "critico-perfil",
}


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


# --- skills ----------------------------------------------------------------

def test_estan_las_seis_skills_de_la_fase_4():
    encontradas = {p.parent.name for p in skills()}
    assert encontradas >= SKILLS_ESPERADAS, f"faltan: {SKILLS_ESPERADAS - encontradas}"


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


@pytest.mark.parametrize("ruta", skills(), ids=lambda p: p.parent.name)
def test_cada_skill_marca_su_etapa(ruta):
    """Sin esto el registro de IA no sabe a qué etapa pertenece lo que se hace."""
    _, cuerpo = _frontmatter(ruta)
    assert "marcar_etapa" in cuerpo, "la skill debe marcar la etapa en curso"


@pytest.mark.parametrize("ruta", skills(), ids=lambda p: p.parent.name)
def test_cada_skill_cierra_con_un_punto_de_decision(ruta):
    _, cuerpo = _frontmatter(ruta)
    assert "registrar_decision" in cuerpo or "Punto de decisión" in cuerpo


@pytest.mark.parametrize("ruta", skills(), ids=lambda p: p.parent.name)
def test_ninguna_skill_condiciona_el_avance_a_un_asesor(ruta):
    """Decisión del usuario: nada queda afecto a que un asesor confirme."""
    _, cuerpo = _frontmatter(ruta)
    prohibido = re.compile(
        r"(confirmaci[óo]n del asesor|que el asesor confirme|"
        r"sin (la )?confirmaci[óo]n de)", re.I)
    encontrado = prohibido.search(cuerpo)
    assert not encontrado, f"condiciona el avance: «{encontrado.group(0)}»"


def test_iniciar_no_pide_requisitos_administrativos():
    _, cuerpo = _frontmatter(SKILLS / "iniciar" / "SKILL.md")
    assert "No preguntes si tiene el grado de bachiller" in cuerpo
    assert "Nada de eso condiciona nada" in cuerpo


# --- agentes ---------------------------------------------------------------

def test_estan_los_seis_pares_trabajador_critico():
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
