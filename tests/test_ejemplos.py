"""Pruebas de los dos ejemplos y del montador.

Las dos que más importan:

- **Las transcripciones ficticias están marcadas como ficticias**, en el nombre
  del archivo y dentro. Un ejemplo que trae datos inventados sin decirlo es peor
  que no tener ejemplo: enseña exactamente lo que el principio 1 prohíbe.
- **Los ejemplos montados verifican sin errores.** Si un ejemplo del propio
  repositorio no pasa sus propias comprobaciones, las comprobaciones no sirven
  de nada.
"""
from __future__ import annotations

import json
import pathlib
import re

import pytest
import yaml

from herramientas import datos_personales, preparar_ejemplo, verificar_todo
from herramientas.perfiles import enfoque_activo, perfil_activo

RAIZ = pathlib.Path(__file__).resolve().parent.parent
EJEMPLOS = RAIZ / "ejemplos"

NOMBRES = ("economia-cuantitativo", "medicina-cualitativo")


def ejemplo(nombre: str) -> pathlib.Path:
    return EJEMPLOS / nombre


# --- que existan y estén declarados ---------------------------------------

def test_estan_los_dos_ejemplos():
    assert set(preparar_ejemplo.ejemplos_disponibles()) >= set(NOMBRES)


@pytest.mark.parametrize("nombre", NOMBRES)
def test_cada_ejemplo_declara_perfil_y_enfoque(nombre):
    """Sin `.enfoque` las herramientas asumen cuantitativo y se equivocan."""
    raiz = ejemplo(nombre)
    assert perfil_activo(raiz), f"{nombre}: falta .perfil-activo"
    assert enfoque_activo(raiz) in ("cuantitativo", "cualitativo"), \
        f"{nombre}: falta .enfoque o tiene un valor raro"


def test_el_ejemplo_cualitativo_declara_enfoque_cualitativo():
    assert enfoque_activo(ejemplo("medicina-cualitativo")) == "cualitativo"


@pytest.mark.parametrize("nombre", NOMBRES)
def test_cada_ejemplo_tiene_readme_que_dice_que_es_ficticio(nombre):
    texto = (ejemplo(nombre) / "README.md").read_text(encoding="utf8")
    assert re.search(r"FICTICI", texto), \
        f"{nombre}: el README debe decir qué parte del ejemplo es ficticia"


@pytest.mark.parametrize("nombre", NOMBRES)
def test_cada_ejemplo_tiene_capitulos_codigo_y_resultados(nombre):
    raiz = ejemplo(nombre)
    assert list((raiz / "capitulos").glob("*.qmd")), f"{nombre}: sin capítulos"
    assert list((raiz / "codigo").glob("*.py")), f"{nombre}: sin código"
    assert list((raiz / "resultados").iterdir()), f"{nombre}: sin resultados"
    assert (raiz / "referencias.bib").exists(), f"{nombre}: sin referencias.bib"


# --- lo ficticio, marcado como ficticio -----------------------------------

def transcripciones() -> list[pathlib.Path]:
    base = ejemplo("medicina-cualitativo") / "datos" / "crudos"
    return sorted(base.glob("*.txt"))


def test_hay_transcripciones_en_el_ejemplo_cualitativo():
    assert len(transcripciones()) >= 8


@pytest.mark.parametrize("ruta", transcripciones(), ids=lambda p: p.name)
def test_el_nombre_del_archivo_dice_que_es_ficticia(ruta):
    assert ruta.name.startswith("FICTICIA_"), (
        "una transcripción de ejemplo tiene que avisar en el nombre: si alguien "
        "la encuentra suelta, el nombre es lo único que ve")


@pytest.mark.parametrize("ruta", transcripciones(), ids=lambda p: p.name)
def test_el_contenido_dice_que_es_ficticia_en_la_primera_linea(ruta):
    primera = ruta.read_text(encoding="utf8").splitlines()[0]
    assert "FICTICIA" in primera.upper(), (
        f"{ruta.name}: la primera línea debe decir que es ficticia")


def test_la_carpeta_de_crudos_explica_que_los_datos_son_ficticios():
    base = ejemplo("medicina-cualitativo") / "datos" / "crudos"
    leeme = base / "LEEME_ESTOS_DATOS_SON_FICTICIOS.md"
    assert leeme.exists()
    texto = leeme.read_text(encoding="utf8")
    assert "no ocurrió" in texto or "No hay participantes" in texto
    assert "principio 1" in texto, (
        "tiene que explicar por qué esto no contradice el principio 1")


@pytest.mark.parametrize("nombre", NOMBRES)
def test_las_decisiones_de_los_ejemplos_estan_marcadas_ficticias(nombre):
    """Una decisión de ejemplo no puede parecer la decisión de una persona."""
    archivos = sorted((ejemplo(nombre) / "decisiones").glob("*.json"))
    assert archivos, f"{nombre}: sin decisiones registradas"
    for ruta in archivos:
        datos = json.loads(ruta.read_text(encoding="utf8"))
        assert "FICTICIO" in datos["autor"].upper(), f"{ruta.name}: autor sin marcar"
        assert "FICTICIO" in datos["respuesta_textual"].upper(), \
            f"{ruta.name}: respuesta textual sin marcar"
        assert datos["aprobado"] is True


# --- datos personales -----------------------------------------------------

@pytest.mark.parametrize("nombre", NOMBRES)
def test_ningun_ejemplo_trae_datos_personales(nombre):
    """Los ejemplos son lo único del repositorio que versiona datos."""
    base = ejemplo(nombre) / "datos"
    rutas = [p for p in base.rglob("*") if p.is_file()]
    assert rutas, f"{nombre}: no hay datos que revisar"
    hallazgos = []
    for ruta in rutas:
        rel = ruta.relative_to(RAIZ).as_posix()
        hallazgos.extend(datos_personales.revisar_archivo(ruta, rel))
    assert not hallazgos, (
        f"{nombre}: posibles datos personales: "
        + "; ".join(str(h) for h in hallazgos[:3]))


# --- el cuantitativo: datos reales y trazables ----------------------------

def test_el_cuantitativo_anota_la_procedencia_de_sus_datos():
    """Los portales corrigen series hacia atrás: sin fecha, el dato no se repite."""
    ruta = ejemplo("economia-cuantitativo") / "datos" / "crudos" / "_procedencia.md"
    texto = ruta.read_text(encoding="utf8")
    assert "Banco Mundial" in texto
    assert "Descargado:" in texto
    assert re.search(r"\d{4}-\d{2}-\d{2}", texto), "falta la fecha de descarga"


def test_el_cuantitativo_reporta_todas_las_especificaciones():
    """Guardar solo la que salió significativa es p-hacking con otro nombre."""
    ruta = ejemplo("economia-cuantitativo") / "resultados" / "estimaciones.json"
    datos = json.loads(ruta.read_text(encoding="utf8"))
    assert len(datos["especificaciones"]) >= 5
    for nombre, e in datos["especificaciones"].items():
        assert e["por_que"], f"{nombre}: sin razón escrita de por qué está"
    significativas = sum(1 for e in datos["especificaciones"].values()
                         if e["p"] < 0.05)
    assert significativas < len(datos["especificaciones"]), (
        "si todas salen significativas, el ejemplo no muestra lo que pasa con "
        "las que no")


def test_el_cuantitativo_declara_que_no_es_causal():
    datos = json.loads(
        (ejemplo("economia-cuantitativo") / "resultados" / "estimaciones.json")
        .read_text(encoding="utf8"))
    assert "no efecto causal" in datos["resumen"]["advertencia"] or \
           "no un efecto causal" in datos["resumen"]["advertencia"]


def test_el_cuantitativo_no_escribe_cifras_a_mano_en_resultados():
    """Todas las cifras se insertan con expresiones de Quarto."""
    qmd = (ejemplo("economia-cuantitativo") / "capitulos" / "05-resultados.qmd")
    texto = qmd.read_text(encoding="utf8")
    assert "`{python}" in texto, "el capítulo debe insertar las cifras, no teclearlas"


# --- el cualitativo: trazabilidad y saturación ----------------------------

def test_el_libro_de_codigos_tiene_criterio_de_exclusion():
    """Sin criterio de exclusión, un libro de códigos es una lista de nombres."""
    ruta = ejemplo("medicina-cualitativo") / "resultados" / "libro_de_codigos.yaml"
    libro = yaml.safe_load(ruta.read_text(encoding="utf8"))
    total = 0
    for categoria, datos in libro.items():
        for nombre, codigo in datos["codigos"].items():
            total += 1
            for campo in ("definicion", "incluye", "excluye", "cita", "de"):
                assert codigo.get(campo), f"{categoria}/{nombre}: falta `{campo}`"
    assert total >= 10


def test_cada_cita_del_libro_existe_en_su_transcripcion():
    """La misma regla que aplica verificar_cifras, comprobada en el análisis."""
    base = ejemplo("medicina-cualitativo")
    libro = yaml.safe_load(
        (base / "resultados" / "libro_de_codigos.yaml").read_text(encoding="utf8"))
    textos = {
        p.name.replace("FICTICIA_entrevista_", "").replace(".txt", ""):
            re.sub(r"\s+", " ", p.read_text(encoding="utf8")).lower()
        for p in transcripciones()
    }
    for categoria, datos in libro.items():
        for nombre, codigo in datos["codigos"].items():
            aguja = re.sub(r"\s+", " ", codigo["cita"]).lower()
            assert aguja in textos[codigo["de"]], (
                f"{categoria}/{nombre}: la cita no está en {codigo['de']}")


def test_el_cualitativo_no_afirma_una_saturacion_que_no_alcanzo():
    """El caso incómodo: el ejemplo lo declara en vez de maquillarlo."""
    base = ejemplo("medicina-cualitativo")
    ctx = json.loads((base / "resultados" / "contexto.json").read_text(encoding="utf8"))
    assert ctx["saturacion_alcanzada"] is False

    for nombre in ("00-preliminares", "01-introduccion", "03-metodo",
                   "04-resultados-discusion", "05-conclusiones"):
        crudo = (base / "capitulos" / f"{nombre}.qmd").read_text(encoding="utf8")
        # El texto va ajustado a 80 columnas: cualquier frase cruza un salto.
        texto = re.sub(r"\s+", " ", crudo)
        assert re.search(r"no se alcanz|no hubo saturaci|antes de la saturaci",
                         texto, re.I), (
            f"{nombre}: no dice que la saturación no se alcanzó")


def test_el_cualitativo_usa_vancouver_porque_lo_pide_el_perfil():
    from herramientas.perfiles import cargar
    perfil = cargar(perfil_activo(ejemplo("medicina-cualitativo")))
    assert perfil.get("estilo_citas") == "vancouver"


# --- el montador ----------------------------------------------------------

def test_montar_un_ejemplo_produce_un_proyecto_completo(tmp_path):
    destino = preparar_ejemplo.preparar("economia-cuantitativo", tmp_path)

    assert (destino / "_quarto.yml").exists(), "falta _quarto.yml generado"
    assert (destino / "perfiles" / "economia-fce.yaml").exists()
    assert (destino / "perfiles" / "unmsm-general.yaml").exists(), \
        "falta el perfil del que hereda"
    assert list((destino / "capitulos").glob("*.qmd"))
    assert (destino / "referencias.bib").exists()
    assert (destino / ".enfoque").exists()


def test_el_montaje_copia_la_cadena_de_herencia_entera(tmp_path):
    destino = preparar_ejemplo.preparar("medicina-cualitativo", tmp_path)
    perfiles = {p.stem for p in (destino / "perfiles").glob("*.yaml")}
    assert {"medicina-fm", "unmsm-general"} <= perfiles


def test_el_montaje_copia_la_normativa_que_citan_los_perfiles(tmp_path):
    """Sin el documento en disco, verificar_perfil reporta un error que no existe."""
    destino = preparar_ejemplo.preparar("economia-cuantitativo", tmp_path)
    pdfs = list((destino / "normativa").rglob("*"))
    assert [p for p in pdfs if p.is_file()], "no copió ningún documento de normativa"


def test_el_quarto_yml_generado_ejecuta_desde_la_raiz(tmp_path):
    """Si el código corriera desde capitulos/, `resultados/x.csv` no existiría."""
    destino = preparar_ejemplo.preparar("economia-cuantitativo", tmp_path)
    texto = (destino / "_quarto.yml").read_text(encoding="utf8")
    assert "execute-dir: project" in texto
    assert "render:" in texto and "capitulos/*.qmd" in texto


def test_montar_un_ejemplo_que_no_existe_falla_claro(tmp_path):
    with pytest.raises(FileNotFoundError, match="no hay un ejemplo"):
        preparar_ejemplo.preparar("no-existe", tmp_path)


def test_comprobar_render_detecta_que_faltan_los_docx(tmp_path):
    preparar_ejemplo.preparar("economia-cuantitativo", tmp_path)
    problemas = preparar_ejemplo.comprobar_render("economia-cuantitativo", tmp_path)
    assert problemas, "recién montado no hay .docx: tiene que avisarlo"
    assert any("falta" in p for p in problemas)


# --- la prueba que da sentido a los ejemplos ------------------------------

@pytest.mark.parametrize("nombre", NOMBRES)
def test_los_ejemplos_montados_verifican_sin_errores(tmp_path, nombre):
    """Un ejemplo del repositorio que no pasa sus propias comprobaciones
    convierte las comprobaciones en decoración."""
    destino = preparar_ejemplo.preparar(nombre, tmp_path)
    r = verificar_todo.verificar(destino, rapido=True)

    detalle = [h.como_linea() for c in r.componentes if c.corrio
               for h in c.informe.errores]
    assert r.errores_totales == 0, f"{nombre}:\n" + "\n".join(detalle)
    assert not r.vacios, f"{nombre}: componentes sin material: " \
                         f"{[c.nombre for c in r.vacios]}"
    assert r.puede(verificar_todo.UMBRAL_ENTREGA), \
        f"{nombre}: global {r.global_}, peor {r.peor_componente}"


# --- los cuatro entregables -----------------------------------------------

def test_el_ejemplo_cuantitativo_trae_su_proyecto_de_tesis():
    """`proyecto/` y `capitulos/` son dos documentos distintos."""
    base = ejemplo("economia-cuantitativo")
    assert list((base / "proyecto").glob("*.qmd")), "sin proyecto de tesis"
    assert list((base / "capitulos").glob("*.qmd")), "sin capítulos de la tesis"


def test_el_ejemplo_trae_sus_datos_de_entrega():
    """Sin ellos no se puede generar ni probar la carátula."""
    ruta = (ejemplo("economia-cuantitativo") / "entregables"
            / "datos_de_entrega.yaml")
    assert ruta.exists()
    datos = yaml.safe_load(ruta.read_text(encoding="utf8"))
    for campo in ("titulo", "anio", "autores", "asesor", "facultad", "escuela",
                  "titulo_profesional"):
        assert datos.get(campo), f"falta `{campo}` para la carátula"
    assert "FICTICIO" in ruta.read_text(encoding="utf8").upper(), (
        "los datos del ejemplo tienen que decir que el tesista es ficticio")


def test_el_montaje_lleva_el_escudo_al_ejemplo(tmp_path):
    destino = preparar_ejemplo.preparar("economia-cuantitativo", tmp_path)
    assert (destino / "plantillas" / "marca" / "escudo_unmsm.png").exists()
    assert list((destino / "proyecto").glob("*.qmd"))


def test_comprobar_entregables_detecta_que_faltan(tmp_path):
    preparar_ejemplo.preparar("economia-cuantitativo", tmp_path)
    problemas = preparar_ejemplo.comprobar_entregables(
        "economia-cuantitativo", tmp_path)
    assert problemas, "recién montado no hay entregables: tiene que avisarlo"
    assert any("proyecto .docx" in p for p in problemas)
    assert any("PDF" in p for p in problemas)
