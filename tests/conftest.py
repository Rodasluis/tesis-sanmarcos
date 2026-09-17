"""Utilidades compartidas: construye proyectos de prueba en disco.

Las herramientas leen el sistema de archivos, así que las pruebas trabajan sobre
proyectos reales en `tmp_path` en lugar de simular capas. Es más lento y mucho
más difícil de engañar.
"""
from __future__ import annotations

import pathlib

import pytest
import yaml

RAIZ_REAL = pathlib.Path(__file__).resolve().parent.parent

CARPETAS = ("capitulos", "resultados", "decisiones", "registro", "perfiles",
            "datos/crudos", "entregables", "plantillas", "normativa/facultades")


@pytest.fixture
def proyecto(tmp_path: pathlib.Path) -> pathlib.Path:
    """Un proyecto vacío con la estructura de carpetas del repositorio."""
    for c in CARPETAS:
        (tmp_path / c).mkdir(parents=True, exist_ok=True)
    (tmp_path / "referencias.bib").write_text("", encoding="utf8")
    return tmp_path


def escribir_perfil(raiz: pathlib.Path, pid: str = "prueba", **campos) -> pathlib.Path:
    """Crea un perfil mínimo pero completo, con lo que toda herramienta espera."""
    datos = {
        "id": pid,
        "facultad": "Facultad de Prueba",
        "escuelas": ["Prueba"],
        "nivel": "pregrado",
        "hereda_de": None,
        "estado": "verificado",
        "fuente": {"documento": "Norma de prueba", "norma": "RR N.° 1",
                   "archivo_local": "normativa/prueba.pdf"},
        "enfoques_admitidos": ["cuantitativo", "cualitativo"],
        "estilo_citas": "apa7",
        "csl": "plantillas/csl/apa.csl",
        "persona_gramatical": ["tercera"],
        "formato": {"margenes_cm": {"superior": 2.5, "inferior": 2.5,
                                    "izquierdo": 3.0, "derecho": 2.5},
                    "fuente": ["Times New Roman"], "tamano": 12,
                    "interlineado": 1.5, "papel": "A4",
                    "numeracion": {"preliminares": "romanos_minusculas",
                                   "cuerpo": "arabigos", "posicion": "inferior derecha"}},
        "resumen": {"idiomas": ["es", "en"], "palabras_max": 200, "palabras_clave": 5,
                    "lineas_investigacion": False},
        "hipotesis": "obligatoria",
        "informe_final": {
            "origen": "plantilla_norma",
            "modelos": {
                "cuantitativo": {"secciones": [
                    {"numero": "I", "titulo": "Introducción"},
                    {"numero": "II", "titulo": "Revisión de literatura"},
                    {"numero": "III", "titulo": "Materiales y métodos"},
                    {"numero": "IV", "titulo": "Resultados"},
                    {"numero": "V", "titulo": "Conclusiones y recomendaciones"},
                ]},
                "cualitativo": {"secciones": [
                    {"numero": "I", "titulo": "Introducción"},
                    {"numero": "II", "titulo": "Método"},
                    {"numero": "III", "titulo": "Resultados y discusión"},
                ]},
            },
        },
        "preliminares": [{"parte": "caratula", "obligatorio": True},
                         {"parte": "resumen", "obligatorio": True}],
        "etica": {"comite_requerido": False, "consentimiento": "condicional"},
        "autoria": {"max_autores": 3, "objetivos_por_autor": True},
        "vigencia_proyecto_meses": None,
        "sustentacion": {"escala": "vigesimal", "nota_minima": 11},
    }
    datos.update(campos)

    (raiz / "normativa").mkdir(parents=True, exist_ok=True)
    archivo = (datos.get("fuente") or {}).get("archivo_local")
    if archivo:
        destino = raiz / archivo
        destino.parent.mkdir(parents=True, exist_ok=True)
        if not destino.exists():
            destino.write_bytes(b"%PDF-1.4 documento de prueba")

    ruta = raiz / "perfiles" / f"{pid}.yaml"
    ruta.write_text(yaml.safe_dump(datos, allow_unicode=True, sort_keys=False),
                    encoding="utf8")
    (raiz / ".perfil-activo").write_text(pid, encoding="utf8")
    return ruta


def escribir_capitulo(raiz: pathlib.Path, nombre: str, contenido: str) -> pathlib.Path:
    ruta = raiz / "capitulos" / f"{nombre}.qmd"
    ruta.parent.mkdir(parents=True, exist_ok=True)
    ruta.write_text(contenido, encoding="utf8")
    return ruta


def escribir_bib(raiz: pathlib.Path, contenido: str) -> pathlib.Path:
    ruta = raiz / "referencias.bib"
    ruta.write_text(contenido, encoding="utf8")
    return ruta


BIB_MINIMO = """\
@article{perez2020crecimiento,
  author = {Pérez, Ana and Quispe, Luis},
  title = {Crecimiento económico regional en el Perú},
  journal = {Revista de Economía},
  year = {2020},
  volume = {12},
  pages = {33--58},
  doi = {10.1234/rev.2020.12}
}

@book{minedu2019escale,
  author = {{Ministerio de Educación}},
  title = {Estadística de la calidad educativa},
  publisher = {MINEDU},
  year = {2019}
}
"""
