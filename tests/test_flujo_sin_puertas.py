"""El flujo no se detiene a esperar a nadie.

El tesista tiene que poder llevar su tesis de la idea a la sustentación con este
repositorio, sin que ninguna etapa quede en pausa esperando que un asesor
confirme algo o que un jurado se pronuncie. El asesor y el jurado existen, son
reales y su criterio pesa; lo que no pueden es bloquear el trabajo.

Esto se comprueba aquí porque es fácil de perder: basta una frase bien
intencionada —«antes de continuar, que tu asesor revise…»— en cualquiera de los
treinta y tantos documentos del repositorio.
"""
from __future__ import annotations

import pathlib
import re

import pytest

RAIZ = pathlib.Path(__file__).resolve().parent.parent

#: Dónde se le habla al tesista. El prompt original del encargo queda fuera:
#: es el documento de partida, no una instrucción viva.
FUENTES = sorted(
    {p for carpeta in (".claude", "perfiles", "docs", "normativa")
     for p in (RAIZ / carpeta).rglob("*")
     if p.suffix in {".md", ".yaml"} and p.is_file()}
    | {RAIZ / "README.md", RAIZ / "CLAUDE.md"}
)
FUENTES = [p for p in FUENTES if "prompt_claude_code" not in p.name]

#: Construcciones que ponen a un tercero delante del trabajo del tesista.
PUERTAS = re.compile(
    r"(antes de (?:continuar|seguir|avanzar|pasar)[^.]{0,80}(?:asesor|jurado)"
    r"|(?:asesor|jurado)[^.]{0,40}debe (?:aprobar|confirmar|autorizar|dar el visto)"
    r"|espera(?:r)? (?:a )?(?:que|la|el) (?:asesor|jurado|aprobaci[óo]n|confirmaci[óo]n)"
    r"|no (?:puedes?|podr[áa]s?|avances?)[^.]{0,60}(?:hasta|sin)[^.]{0,40}(?:asesor|jurado)"
    r"|requiere[^.]{0,40}(?:aprobaci[óo]n|confirmaci[óo]n) del (?:asesor|jurado))",
    re.I)

#: Negaciones. Decir «esto NO espera al asesor» es exactamente lo que queremos.
NEGACION = re.compile(r"\b(no|nada|ning[úu]n|ninguna|nunca|sin|jam[áa]s)\b", re.I)


def _frases(texto: str) -> list[str]:
    return re.split(r"(?<=[.;:])\s+", re.sub(r"\s+", " ", texto))


@pytest.mark.parametrize("ruta", FUENTES, ids=lambda p: str(p.relative_to(RAIZ)))
def test_ningun_documento_pone_al_asesor_o_al_jurado_como_puerta(ruta):
    texto = ruta.read_text(encoding="utf8", errors="replace")
    for frase in _frases(texto):
        hallado = PUERTAS.search(frase)
        if hallado and not NEGACION.search(frase):
            raise AssertionError(
                f"{ruta.relative_to(RAIZ)} condiciona el avance a un tercero:\n"
                f"  «{frase.strip()[:220]}»")


def test_las_once_etapas_tienen_su_skill():
    """De la idea a la sustentación, sin huecos."""
    etapas = ["iniciar", "explorar-datos", "afinar-idea", "literatura", "proyecto",
              "analizar", "redactar", "jurado", "verificar", "entregar",
              "sustentacion"]
    for etapa in etapas:
        assert (RAIZ / ".claude" / "skills" / etapa / "SKILL.md").exists(), (
            f"falta la skill de la etapa {etapa}: el flujo tendría un hueco")


def test_los_dos_entregables_se_generan_con_una_orden_cada_uno():
    """El proyecto y la tesis salen en .docx y PDF sin pasos manuales."""
    from herramientas import entregar, entregar_proyecto
    for modulo in (entregar, entregar_proyecto):
        assert hasattr(modulo, "preparar")
        assert hasattr(modulo, "main")


def test_nada_del_flujo_exige_libreoffice():
    """Sin LibreOffice se entrega igual: el .docx es lo que pide el art. 13."""
    from herramientas import entregar
    fuente = pathlib.Path(entregar.__file__).read_text(encoding="utf8")
    assert "inf.aviso" in fuente.split("_convertir_a_pdf")[-1], (
        "la falta de PDF tiene que ser aviso, nunca error")


def test_la_caratula_se_genera_aunque_falten_datos():
    """Un dato que falta se avisa; no se convierte en un bloqueo."""
    import docx

    from herramientas import caratula
    from herramientas.perfiles import cargar

    doc = docx.Document()
    avisos = caratula.construir(doc, {}, cargar("unmsm-general"), "tesis")
    assert isinstance(avisos, list)
    assert doc.paragraphs, "la carátula vacía debe generarse igual"
    assert caratula.faltantes({}, cargar("unmsm-general")), (
        "y debe decir qué falta")
