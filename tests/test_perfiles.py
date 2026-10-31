"""Pruebas de la carga de perfiles y de las reglas de perfiles/_esquema.yaml."""
from __future__ import annotations

import pathlib

import pytest
import yaml

from herramientas import perfiles as P

RAIZ = pathlib.Path(__file__).resolve().parent.parent
INDICE = RAIZ / "normativa" / "facultades" / "indice.yaml"


def ids():
    return P.listar()


def test_hay_perfiles():
    assert len(ids()) >= 20, "deberían existir al menos los 20 perfiles de facultad"


@pytest.mark.parametrize("pid", ids())
def test_cada_perfil_carga_y_valida(pid):
    perfil = P.cargar(pid)
    assert perfil.id == pid
    assert perfil.estado in P.ESTADOS_VALIDOS


@pytest.mark.parametrize("pid", ids())
def test_la_herencia_termina_en_el_perfil_base(pid):
    perfil = P.cargar(pid)
    assert perfil.cadena[-1] == "unmsm-general", (
        f"{pid}: toda cadena de herencia debe terminar en unmsm-general, "
        f"y esta termina en {perfil.cadena[-1]}"
    )


@pytest.mark.parametrize("pid", ids())
def test_verificado_exige_documento_en_disco(pid):
    """Regla R2: no se puede declarar verificado sin el PDF."""
    perfil = P.cargar(pid)
    if perfil.verificado:
        ruta = (perfil.get("fuente") or {}).get("archivo_local")
        assert ruta, f"{pid}: verificado sin archivo_local"
        assert (RAIZ / ruta).exists(), f"{pid}: falta {ruta}"


@pytest.mark.parametrize("pid", ids())
def test_el_esquema_de_facto_existe_si_se_declara(pid):
    perfil = P.cargar(pid)
    ruta = perfil.get("esquema_de_facto")
    if ruta:
        assert (RAIZ / ruta).exists(), f"{pid}: esquema_de_facto inexistente: {ruta}"


@pytest.mark.parametrize("pid", ids())
def test_todo_perfil_resuelve_estructura_de_informe(pid):
    """Un perfil sin modelos propios debe heredarlos: nadie queda sin estructura."""
    perfil = P.cargar(pid)
    informe = perfil.get("informe_final") or {}
    modelos = informe.get("modelos") or {}
    assert modelos, f"{pid}: no resuelve ningún modelo de informe final"
    assert "cuantitativo" in modelos or "cualitativo" in modelos


def test_el_perfil_base_no_hereda_de_nadie():
    base = P.cargar("unmsm-general")
    assert base.get("hereda_de") is None
    assert base.verificado


def test_medicina_usa_vancouver_y_exige_comite_de_etica():
    m = P.cargar("medicina-fm")
    assert m.get("estilo_citas") == "vancouver"
    assert (m.get("etica") or {}).get("comite_requerido") is True
    assert m.get("vigencia_proyecto_meses") == 12


def test_letras_usa_apa7_y_numera_arriba_a_la_derecha():
    letras = P.cargar("letras-flch")
    assert letras.get("estilo_citas") == "apa7"
    numeracion = (letras.get("formato") or {}).get("numeracion") or {}
    assert "superior" in str(numeracion.get("posicion", "")).lower()


def test_derecho_hereda_la_estructura_del_perfil_base():
    d = P.cargar("derecho-fdcp")
    assert (d.get("informe_final") or {}).get("origen") == "herencia"
    # pese a heredar la estructura, su formato propio manda
    assert (d.get("formato") or {}).get("fuente") == ["Arial"]


def test_solo_esta_verificado_lo_que_tiene_documento_en_disco():
    """La regla que importa, comprobada sobre los 21 perfiles.

    Lo que se protege no es el estado de una facultad concreta sino la regla:
    nadie lleva `verificado` sin el documento que lo respalde.
    """
    for pid in P.listar():
        perfil = P.cargar(pid)
        if not perfil.verificado:
            continue
        fuente = perfil.get("fuente") or {}
        archivo = fuente.get("archivo_local")
        assert archivo, f"{pid}: dice `verificado` y no declara documento"
        assert (RAIZ / archivo).exists(), (
            f"{pid}: dice `verificado` y falta {archivo}")
        assert fuente.get("norma"), (
            f"{pid}: dice `verificado` y no declara número de resolución")


def test_economia_y_educacion_heredan_el_marco_general():
    """Decisión del tesista del 23/10/2026.

    Ninguno de los dos documentos acreditó rango normativo y mantenerlos en un
    estado intermedio obligaba a advertir en cada etapa sobre algo que no
    cambia la estructura de la tesis.
    """
    for pid in ("economia-fce", "educacion-fe"):
        perfil = P.cargar(pid)
        assert perfil.estado == "hereda_general", pid
        assert not perfil.verificado, pid


def test_la_herencia_no_pisa_lo_propio():
    """Medicina redefine hipótesis; no debe quedarse con el valor del base."""
    base = P.cargar("unmsm-general")
    med = P.cargar("medicina-fm")
    assert base.get("hipotesis") == "obligatoria"
    assert med.get("hipotesis") == "condicional"


def test_cobertura_de_las_veinte_facultades():
    indice = yaml.safe_load(INDICE.read_text(encoding="utf8"))
    del_indice = {f["nombre"] for f in indice["facultades"]}
    con_perfil = set()
    for pid in ids():
        p = P.cargar(pid)
        if p.get("facultad") != "(todas)":
            con_perfil.add(p.get("facultad"))
    assert del_indice == con_perfil, f"sin perfil: {del_indice - con_perfil}"


def test_un_perfil_inexistente_falla_claro():
    with pytest.raises(P.ErrorDePerfil):
        P.cargar("no-existe-esta-facultad")


def test_ciclo_de_herencia_se_detecta(tmp_path):
    (tmp_path / "a.yaml").write_text(
        "id: a\nhereda_de: b\nestado: verificado\nnivel: pregrado\n", encoding="utf8")
    (tmp_path / "b.yaml").write_text(
        "id: b\nhereda_de: a\nestado: verificado\nnivel: pregrado\n", encoding="utf8")
    with pytest.raises(P.ErrorDePerfil, match="ciclo"):
        P.cargar("a", dir_perfiles=tmp_path, raiz=tmp_path)


def test_verificado_sin_documento_es_rechazado(tmp_path):
    """Regla R2 sobre un perfil de juguete."""
    (tmp_path / "x.yaml").write_text(
        "id: x\nhereda_de: null\nnivel: pregrado\nestado: verificado\n"
        "fuente:\n  documento: inventado\n  archivo_local: no/existe.pdf\n",
        encoding="utf8")
    with pytest.raises(P.ErrorDePerfil, match="falta el documento"):
        P.cargar("x", dir_perfiles=tmp_path, raiz=tmp_path)


def test_norma_de_posgrado_no_sustenta_pregrado(tmp_path):
    """Regla R4."""
    doc = tmp_path / "doc.pdf"
    doc.write_bytes(b"%PDF-1.4")
    (tmp_path / "y.yaml").write_text(
        "id: y\nhereda_de: null\nnivel: pregrado\nestado: verificado\n"
        "fuente:\n  documento: Dictamen de la Unidad de Posgrado\n"
        "  archivo_local: doc.pdf\n",
        encoding="utf8")
    with pytest.raises(P.ErrorDePerfil, match="posgrado"):
        P.cargar("y", dir_perfiles=tmp_path, raiz=tmp_path)


def test_nadie_cita_una_resolucion_de_medicina_que_el_perfil_no_declara():
    """Una norma que no consta en `normativa/` no se cita.

    La norma verificada de Medicina es la RD N.° 002373-2023-D-FM. Cualquier
    otra resolucion «D-FM» citada en los .md y .qmd del repositorio es un error.
    """
    import re

    buena = P.cargar("medicina-fm").get("fuente")["norma"]
    patron = re.compile(r"R[RD] N\.°\s*[\w./-]*D-FM[\w./-]*")

    malas = []
    for ruta in list(RAIZ.glob("**/*.md")) + list(RAIZ.glob("**/*.qmd")):
        partes = ruta.relative_to(RAIZ).parts
        if partes[0] in (".venv", ".ejemplos-montados", ".git"):
            continue
        for cita in patron.findall(ruta.read_text(encoding="utf8", errors="replace")):
            if cita.strip().rstrip(".,;:)") != buena:
                malas.append(f"{ruta.relative_to(RAIZ)}: {cita}")

    assert not malas, "citan una resolucion de Medicina que no es la del perfil:\n" \
                      + "\n".join(malas)
