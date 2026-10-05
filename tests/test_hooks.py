"""Pruebas del hook de registro de IA, del de git y del instalador.

La propiedad que más importa, y por eso se prueba desde varios ángulos: **el
hook nunca puede devolver un código distinto de 0**. La documentación de hooks
dice que solo el código 2 bloquea, así que mientras este archivo no devuelva 2,
una sesión no puede romperse por su culpa. Las pruebas lo fuerzan con entradas
rotas, rutas imposibles y JSON inválido.
"""
from __future__ import annotations

import json
import pathlib
import subprocess
import sys

import pytest

from herramientas import datos_personales as DP
from herramientas import instalar_hooks as IH
from herramientas import registro_ia as RIA

RAIZ_REAL = pathlib.Path(__file__).resolve().parent.parent
HOOK = RAIZ_REAL / ".claude" / "hooks" / "registrar_ia.py"


def correr_hook(carga: str, proyecto: pathlib.Path) -> subprocess.CompletedProcess:
    """Ejecuta el hook tal como lo haría Claude Code."""
    import os
    entorno = dict(os.environ, CLAUDE_PROJECT_DIR=str(proyecto))
    return subprocess.run([sys.executable, str(HOOK)], input=carga, text=True,
                          capture_output=True, timeout=30, env=entorno)


def lineas(proyecto: pathlib.Path) -> list[dict]:
    archivo = proyecto / "registro" / "registro_ia.jsonl"
    if not archivo.exists():
        return []
    crudas = archivo.read_text(encoding="utf8").splitlines()
    return [json.loads(linea) for linea in crudas if linea.strip()]


# --- el hook escribe lo que debe -------------------------------------------

def test_registra_una_escritura(proyecto):
    carga = json.dumps({
        "tool_name": "Write",
        "tool_input": {"file_path": str(proyecto / "capitulos" / "uno.qmd"),
                       "content": "una\ndos\ntres\n"},
        "session_id": "sesion123456",
        "tool_use_id": "toolu_01",
    })
    r = correr_hook(carga, proyecto)
    assert r.returncode == 0

    registradas = lineas(proyecto)
    assert len(registradas) == 1
    a = registradas[0]
    assert a["herramienta"] == "Write"
    assert a["archivo"] == "capitulos/uno.qmd"
    assert a["resumen"] == "escribió 3 líneas"
    assert a["sesion"] == "sesion12"


def test_las_rutas_usan_barras_normales(proyecto):
    """El registro puede leerse en otra máquina; nada de separadores de Windows."""
    carga = json.dumps({
        "tool_name": "Edit",
        "tool_input": {"file_path": str(proyecto / "capitulos" / "sub" / "dos.qmd"),
                       "old_string": "x" * 40},
        "session_id": "s",
    })
    correr_hook(carga, proyecto)
    assert "\\" not in lineas(proyecto)[0]["archivo"]
    assert lineas(proyecto)[0]["archivo"] == "capitulos/sub/dos.qmd"


def test_registra_un_comando(proyecto):
    carga = json.dumps({
        "tool_name": "Bash",
        "tool_input": {"command": "uv run python -m herramientas.verificar_perfil"},
        "session_id": "s",
    })
    correr_hook(carga, proyecto)
    a = lineas(proyecto)[0]
    assert a["herramienta"] == "Bash"
    assert "verificar_perfil" in a["resumen"]


def test_no_registra_credenciales(proyecto):
    """Un comando con pinta de llevar una clave no se transcribe."""
    carga = json.dumps({
        "tool_name": "Bash",
        "tool_input": {"command": 'curl -H "Authorization: Bearer sk-muy-secreto" https://api'},
        "session_id": "s",
    })
    correr_hook(carga, proyecto)
    a = lineas(proyecto)[0]
    assert "sk-muy-secreto" not in json.dumps(a)
    assert "omitido" in a["resumen"]


def test_no_se_registra_a_si_mismo(proyecto):
    """Escribir en registro/ no debe generar una entrada: sería ruido circular."""
    carga = json.dumps({
        "tool_name": "Write",
        "tool_input": {"file_path": str(proyecto / "registro" / "algo.md"),
                       "content": "x"},
        "session_id": "s",
    })
    r = correr_hook(carga, proyecto)
    assert r.returncode == 0
    assert lineas(proyecto) == []


def test_usa_la_etapa_marcada(proyecto):
    RIA.marcar_etapa("redactar", proyecto)
    carga = json.dumps({
        "tool_name": "Write",
        "tool_input": {"file_path": str(proyecto / "capitulos" / "a.qmd"), "content": "x"},
        "session_id": "s",
    })
    correr_hook(carga, proyecto)
    assert lineas(proyecto)[0]["etapa"] == "redactar"


def test_sin_etapa_marcada_lo_dice(proyecto):
    carga = json.dumps({
        "tool_name": "Write",
        "tool_input": {"file_path": str(proyecto / "capitulos" / "a.qmd"), "content": "x"},
        "session_id": "s",
    })
    correr_hook(carga, proyecto)
    assert lineas(proyecto)[0]["etapa"] == "sin etapa"


def test_va_anadiendo_sin_pisar(proyecto):
    for i in range(3):
        correr_hook(json.dumps({
            "tool_name": "Write",
            "tool_input": {"file_path": str(proyecto / "capitulos" / f"{i}.qmd"),
                           "content": "x"},
            "session_id": "s",
        }), proyecto)
    assert len(lineas(proyecto)) == 3


# --- el hook nunca bloquea -------------------------------------------------

@pytest.mark.parametrize("carga", [
    "",                                   # nada
    "esto no es json",                    # basura
    "{}",                                 # json vacío
    '{"tool_name": ""}',                  # sin herramienta
    '{"tool_input": {"file_path": "x"}}',  # sin tool_name
    '{"tool_name": "Write"}',             # sin tool_input
    '{"tool_name": "Write", "tool_input": null}',
    '[1, 2, 3]',                          # json que no es un objeto
])
def test_nunca_devuelve_un_codigo_de_bloqueo(carga, proyecto):
    """Solo el código 2 bloquea. Este hook no debe devolverlo jamás."""
    r = correr_hook(carga, proyecto)
    assert r.returncode == 0, f"con la entrada {carga!r} devolvió {r.returncode}"


def test_no_falla_si_no_puede_escribir(tmp_path):
    """Aunque la carpeta de destino sea imposible, el hook sale con 0."""
    inexistente = tmp_path / "no" / "existe" / "ni" / "existira"
    carga = json.dumps({
        "tool_name": "Write",
        "tool_input": {"file_path": "x.qmd", "content": "x"},
        "session_id": "s",
    })
    r = correr_hook(carga, inexistente)
    assert r.returncode == 0


# --- lectura del registro --------------------------------------------------

def test_resumen_agrupa_por_etapa_y_herramienta(proyecto):
    RIA.marcar_etapa("analizar", proyecto)
    for _ in range(2):
        correr_hook(json.dumps({
            "tool_name": "Bash", "tool_input": {"command": "ls"}, "session_id": "s"}),
            proyecto)
    RIA.marcar_etapa("redactar", proyecto)
    correr_hook(json.dumps({
        "tool_name": "Write",
        "tool_input": {"file_path": str(proyecto / "capitulos" / "a.qmd"), "content": "x"},
        "session_id": "s"}), proyecto)

    r = RIA.resumen(proyecto)
    assert r["acciones"] == 3
    assert r["por_etapa"] == {"analizar": 2, "redactar": 1}
    assert r["por_herramienta"]["Bash"] == 2


def test_una_linea_corrupta_no_impide_leer_el_resto(proyecto):
    archivo = proyecto / "registro" / "registro_ia.jsonl"
    archivo.parent.mkdir(parents=True, exist_ok=True)
    archivo.write_text(
        json.dumps({"herramienta": "Write", "etapa": "redactar"}) + "\n"
        + "{esto esta a medias\n"
        + json.dumps({"herramienta": "Bash", "etapa": "redactar"}) + "\n",
        encoding="utf8")
    assert len(RIA.leer(proyecto)) == 2


def test_registro_vacio_avisa_de_que_falta_el_hook(proyecto):
    al_dia, motivo = RIA.esta_al_dia(proyecto)
    assert not al_dia
    assert "instalar_hooks" in motivo


def test_etapa_invalida_se_rechaza(proyecto):
    with pytest.raises(ValueError, match="etapa desconocida"):
        RIA.marcar_etapa("inventada", proyecto)


# --- datos personales ------------------------------------------------------

def test_bloquea_los_datos_crudos():
    indicios = DP.revisar_ruta("datos/crudos/entrevista01.txt")
    assert DP.hay_bloqueantes(indicios)


def test_bloquea_los_docx_de_entrega():
    assert DP.hay_bloqueantes(DP.revisar_ruta("entregables/TEXTO/algo.docx"))


def test_bloquea_el_env():
    assert DP.hay_bloqueantes(DP.revisar_ruta(".env"))


def test_un_capitulo_normal_no_se_bloquea():
    assert not DP.hay_bloqueantes(DP.revisar_ruta("capitulos/01_introduccion.qmd"))


def test_advierte_por_el_nombre_del_archivo():
    indicios = DP.revisar_ruta("datos/procesados/padron_participantes.csv")
    assert indicios and all(i.nivel == "advierte" for i in indicios)


def test_detecta_un_dni_con_su_etiqueta():
    indicios = DP.revisar_contenido("x.md", "El DNI del participante es 45678912.\n")
    assert any("DNI" in i.motivo for i in indicios)


def test_detecta_una_tabla_de_participantes():
    """El caso real: una hoja con columnas de datos personales.

    La cabecera y el dato van en líneas distintas, así que buscar «dni» junto a
    ocho dígitos no lo encuentra; hay que mirar los nombres de columna.
    """
    indicios = DP.revisar_contenido("padron.csv", "nombre,dni,celular\nAna,45678912,987654321\n")
    assert any("columnas de datos personales" in i.motivo for i in indicios)


def test_una_tabla_de_resultados_no_se_marca():
    indicios = DP.revisar_contenido("tabla1.csv", "region,pib,desempleo\nLima,3.4,7.1\n")
    assert not any("columnas de datos personales" in i.motivo for i in indicios)


def test_no_marca_cualquier_numero_de_ocho_cifras():
    """Un monto no es un DNI. Marcar de más haría que nadie lea los avisos."""
    indicios = DP.revisar_contenido("x.md", "El presupuesto fue de 12500000 soles.\n")
    assert not indicios


def test_detecta_un_correo_personal():
    indicios = DP.revisar_contenido("x.md", "Escribir a juan.perez.lopez@gmail.com\n")
    assert any("correo" in i.motivo for i in indicios)


def test_no_marca_los_correos_de_ejemplo():
    texto = "Correo del asesor: email@unmsm.edu.pe\nnoreply@anthropic.com\n"
    assert not DP.revisar_contenido("x.md", texto)


def test_el_informe_distingue_bloqueo_de_aviso():
    bloquea = DP.revisar_ruta("datos/crudos/x.txt")
    texto = DP.informar(bloquea)
    assert "COMMIT DETENIDO" in texto

    advierte = DP.revisar_contenido("x.md", "contacto: ana.torres@gmail.com\n")
    texto2 = DP.informar(advierte)
    assert "COMMIT DETENIDO" not in texto2
    assert "aviso, no un bloqueo" in texto2


def test_sin_indicios_lo_dice_claro():
    assert "Sin indicios" in DP.informar([])


# --- instalador ------------------------------------------------------------

def test_instala_y_reconoce_su_propio_hook(proyecto):
    (proyecto / ".claude" / "hooks").mkdir(parents=True, exist_ok=True)
    destino, cambio = IH.instalar_hook_claude(proyecto)
    assert cambio
    ajustes = json.loads(destino.read_text(encoding="utf8"))
    post = ajustes["hooks"]["PostToolUse"]
    assert len(post) == 1
    assert IH._es_nuestro(post[0])


def test_instalar_dos_veces_no_duplica(proyecto):
    (proyecto / ".claude" / "hooks").mkdir(parents=True, exist_ok=True)
    IH.instalar_hook_claude(proyecto)
    destino, cambio = IH.instalar_hook_claude(proyecto)
    assert not cambio
    ajustes = json.loads(destino.read_text(encoding="utf8"))
    assert len(ajustes["hooks"]["PostToolUse"]) == 1


def test_respeta_los_hooks_de_otros(proyecto):
    destino = proyecto / ".claude" / "settings.local.json"
    destino.parent.mkdir(parents=True, exist_ok=True)
    ajeno = {"matcher": "Read",
             "hooks": [{"type": "command", "command": "otra-cosa"}]}
    destino.write_text(json.dumps({"hooks": {"PostToolUse": [ajeno]}}), encoding="utf8")

    IH.instalar_hook_claude(proyecto)
    post = json.loads(destino.read_text(encoding="utf8"))["hooks"]["PostToolUse"]
    assert len(post) == 2
    assert ajeno in post


def test_desinstalar_deja_los_de_otros(proyecto):
    destino = proyecto / ".claude" / "settings.local.json"
    destino.parent.mkdir(parents=True, exist_ok=True)
    ajeno = {"matcher": "Read", "hooks": [{"type": "command", "command": "otra-cosa"}]}
    destino.write_text(json.dumps({"hooks": {"PostToolUse": [ajeno]}}), encoding="utf8")

    IH.instalar_hook_claude(proyecto)
    assert IH.desinstalar_hook_claude(proyecto)
    post = json.loads(destino.read_text(encoding="utf8"))["hooks"]["PostToolUse"]
    assert post == [ajeno]


def test_el_intérprete_configurado_es_uno_que_arranca():
    assert IH.interprete().exists()


def test_el_matcher_no_registra_lecturas():
    """Leer no cambia la tesis; registrar cada Read llenaría el log de ruido."""
    assert "Read" not in IH.MATCHER
    assert "Grep" not in IH.MATCHER
    for herramienta in ("Write", "Edit", "Bash"):
        assert herramienta in IH.MATCHER


def test_la_comprobacion_del_repositorio_real_pasa():
    """Prueba de regresión: los hooks instalados aquí funcionan de verdad."""
    filas = IH.comprobar(RAIZ_REAL)
    fallan = [nombre for nombre, ok, _ in filas if not ok]
    assert not fallan, f"fallan: {fallan}"
