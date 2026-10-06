"""Registra las decisiones **ficticias** de este ejemplo.

En una tesis de verdad este script no existe: las decisiones se toman en sesión y
las escribe `registrar_decision.py` con las palabras del tesista. Aquí hace falta
porque un ejemplo completo necesita un historial, y la única vía de escritura en
`decisiones/` es esa herramienta, que además exige una respuesta textual.

**Todo lo que registra es ficticio y está marcado como tal.** Nadie tomó estas
decisiones.

Uso:
    uv run python codigo/02_decisiones_de_ejemplo.py
"""
from __future__ import annotations

import pathlib
import shutil
import sys

AQUI = pathlib.Path(__file__).resolve().parent.parent
sys.path.insert(0, str(AQUI.parent.parent))

from herramientas.registrar_decision import registrar  # noqa: E402

AUTOR = "Tesista de ejemplo (FICTICIO)"
MARCA = "[EJEMPLO FICTICIO] "

# Nombrada una sola vez: aparece en `opciones_presentadas`, en `recomendada` y
# en `eleccion`, y teclearla tres veces es la forma de que dejen de coincidir.
TEMA_BARRERAS = ("Barreras percibidas para la adherencia al tratamiento "
                 "antihipertensivo (cualitativo)")

DECISIONES = [
    {
        "etapa": "iniciar",
        "opciones_presentadas": [
            "Prevalencia de hipertensión no controlada en un centro de salud "
            "(cuantitativo)",
            TEMA_BARRERAS,
            "Ensayo de una intervención educativa sobre adherencia",
        ],
        "recomendada": TEMA_BARRERAS,
        "eleccion": TEMA_BARRERAS,
        "respuesta_textual": MARCA + (
            "La cualitativa. La prevalencia ya está medida a nivel nacional y yo "
            "no voy a mejorar eso con un centro de salud. Lo que no sé es por qué "
            "mis pacientes dejan el tratamiento, y eso solo lo averiguo "
            "preguntándoles. El ensayo necesita un comité, aleatorización y un año "
            "largo; no me da el tiempo."),
        "cambios_pedidos": [],
        "preguntas_comprension": [
            {"pregunta": "¿Qué puede responder un estudio cualitativo que no "
                         "responda una encuesta?",
             "respuesta": MARCA + "Las razones. La encuesta me dice cuántos no "
                          "adhieren; la entrevista me dice qué los frena, y eso no lo "
                          "puedo poner yo de antemano en un cuestionario."},
            {"pregunta": "¿Por qué fenomenológico y no teoría fundamentada?",
             "respuesta": MARCA + "Porque quiero describir la experiencia como ellos "
                          "la cuentan, no construir una teoría general. Para teoría "
                          "fundamentada necesitaría muestreo teórico y muchas más "
                          "entrevistas."},
        ],
    },
    {
        "etapa": "explorar-datos",
        "opciones_presentadas": [
            "Datos propios: entrevistas semiestructuradas",
            "Análisis secundario de la ENDES",
            "Revisión de historias clínicas del establecimiento",
        ],
        "recomendada": "Datos propios: entrevistas semiestructuradas",
        "eleccion": "Datos propios: entrevistas semiestructuradas",
        "respuesta_textual": MARCA + (
            "Entrevistas propias. La ENDES no pregunta por qué alguien dejó la "
            "pastilla, y las historias clínicas registran si recogió la receta, no "
            "qué le pasó. Asumo el costo de levantar los datos yo."),
        "cambios_pedidos": [
            "Anonimizar antes de transcribir, no después",
            "Que las transcripciones no se suban al repositorio",
        ],
        "preguntas_comprension": [
            {"pregunta": "¿Qué pasa con las transcripciones al terminar la tesis?",
             "respuesta": MARCA + "Se quedan en datos/crudos/, que no se versiona, y "
                          "anonimizadas. Al repositorio no sube nada con nombres."},
            {"pregunta": "¿Qué necesitas antes de la primera entrevista?",
             "respuesta": MARCA + "El consentimiento informado por escrito y la "
                          "aprobación del comité de ética, que en Medicina es "
                          "obligatoria por el art. 23."},
        ],
    },
    {
        "etapa": "afinar-idea",
        "opciones_presentadas": [
            "¿Cuáles son las barreras para la adherencia? (descriptiva)",
            "¿Cómo describen los usuarios las barreras que encuentran? (fenomenológica)",
            "¿Qué relación hay entre nivel educativo y adherencia? (asociativa)",
        ],
        "recomendada": "¿Cómo describen los usuarios las barreras que encuentran? (fenomenológica)",
        "eleccion": "¿Cómo describen los usuarios las barreras que encuentran? (fenomenológica)",
        "respuesta_textual": MARCA + (
            "La segunda, con el «cómo describen». La primera suena igual pero da a "
            "entender que las barreras están ahí y yo las voy a encontrar como "
            "quien encuentra objetos; lo que yo tengo son las palabras de ocho "
            "personas. La tercera es una pregunta cuantitativa y no la puedo "
            "contestar con entrevistas."),
        "cambios_pedidos": [],
        "preguntas_comprension": [
            {"pregunta": "¿Tu estudio tiene hipótesis?",
             "respuesta": MARCA + "Supuestos, no hipótesis a contrastar. El Anexo 2B "
                          "admite «supuestos hipotéticos» en el modelo cualitativo. El "
                          "mío es que parte de lo que se registra como incumplimiento "
                          "es una respuesta razonable a condiciones materiales."},
            {"pregunta": "¿Hasta dónde llegan tus conclusiones?",
             "respuesta": MARCA + "Hasta los usuarios de ese centro, y ni siquiera a "
                          "todos. No puedo generalizar a Lima ni al Perú."},
        ],
    },
    {
        "etapa": "literatura",
        "opciones_presentadas": [
            "Solo antecedentes nacionales",
            "Antecedentes nacionales más estudios cualitativos internacionales",
            "Solo literatura metodológica sobre análisis cualitativo",
        ],
        "recomendada": "Antecedentes nacionales más estudios cualitativos internacionales",
        "eleccion": "Antecedentes nacionales más estudios cualitativos internacionales",
        "respuesta_textual": MARCA + (
            "Las dos cosas. Herrera-Añazco me da el tamaño del problema en el Perú y "
            "Tsiantou me da un estudio cualitativo con el que puedo comparar mis "
            "categorías. Y agrego a Squire porque voy a tener que discutir la "
            "saturación y necesito respaldo para decir que no se alcanzó."),
        "cambios_pedidos": [
            "Comprobar cada DOI en Crossref antes de citarlo",
        ],
        "preguntas_comprension": [
            {"pregunta": "¿Por qué citas un estudio griego en una tesis peruana?",
             "respuesta": MARCA + "Porque es el que más se parece a lo que estoy "
                          "haciendo en método, y eso me permite comparar categorías. "
                          "El contexto es distinto y eso lo digo en la discusión."},
            {"pregunta": "¿Qué hueco llena tu tesis?",
             "respuesta": MARCA + "Para el Perú encontré la magnitud medida pero no "
                          "las razones en palabras de los pacientes de un primer nivel."},
        ],
    },
    {
        "etapa": "proyecto",
        "opciones_presentadas": [
            "Modelo cualitativo del reglamento de la Facultad de Medicina",
            "Modelo cualitativo del Anexo 2B de la UNMSM",
        ],
        "recomendada": "Modelo cualitativo del reglamento de la Facultad de Medicina",
        "eleccion": "Modelo cualitativo del reglamento de la Facultad de Medicina",
        "respuesta_textual": MARCA + (
            "El de mi facultad. Medicina tiene reglamento propio y verificado, con "
            "resolución, y además junta resultados y discusión en un solo capítulo, "
            "que es como están escritas las tesis de mi escuela. Vancouver también "
            "lo pide el reglamento, no es mi preferencia."),
        "cambios_pedidos": [],
        "preguntas_comprension": [
            {"pregunta": "¿Por qué resultados y discusión van juntos?",
             "respuesta": MARCA + "Porque lo dice el modelo cualitativo del reglamento "
                          "de la facultad. En cualitativa tiene sentido: la cita y su "
                          "interpretación se leen mejor juntas."},
            {"pregunta": "¿Qué exige tu facultad antes de ejecutar el proyecto?",
             "respuesta": MARCA + "Comité de Investigación de la escuela, comité de "
                          "ética y resolución decanal. Art. 23."},
        ],
    },
    {
        "etapa": "analizar",
        "opciones_presentadas": [
            "Codificar con 16 códigos en 5 categorías y declarar que no hubo saturación",
            "Agrupar en 3 categorías amplias para que parezca que saturó",
            "Seguir entrevistando antes de analizar",
        ],
        "recomendada": "Codificar con 16 códigos en 5 categorías y declarar que no hubo saturación",
        "eleccion": "Codificar con 16 códigos en 5 categorías y declarar que no hubo saturación",
        "respuesta_textual": MARCA + (
            "Lo declaro. Me ofreciste la opción de juntar códigos en categorías más "
            "grandes para que la curva se viera plana y la rechazo: sería maquillar "
            "el dato. Seguir entrevistando sería lo correcto pero ya se me cerró el "
            "campo, así que lo pongo como limitación y como lo primero que tiene que "
            "hacer quien siga esto."),
        "cambios_pedidos": [
            "Que cada código tenga criterio de exclusión, no solo definición",
            "Que el script falle si una cita del libro no está en su transcripción",
        ],
        "preguntas_comprension": [
            {"pregunta": "¿Qué significa que no se alcanzó la saturación?",
             "respuesta": MARCA + "Que la última entrevista todavía me dio códigos "
                          "nuevos, así que es casi seguro que hay barreras que no "
                          "recogí. No puedo decir que estas sean todas."},
            {"pregunta": "¿Para qué sirve el criterio de exclusión de un código?",
             "respuesta": MARCA + "Para que se pueda auditar por qué un fragmento está "
                          "en un código y no en otro. Sin eso, el libro de códigos es "
                          "una lista de nombres."},
        ],
    },
    {
        "etapa": "redactar",
        "opciones_presentadas": [
            "Tercera persona",
            "Impersonal",
        ],
        "recomendada": "Impersonal",
        "eleccion": "Impersonal",
        "respuesta_textual": MARCA + (
            "Impersonal. El perfil de Medicina admite tercera persona o impersonal, "
            "así que elijo impersonal, que es lo que usa Anales de la Facultad de "
            "Medicina, que es el formato que pide el reglamento para el resumen."),
        "cambios_pedidos": [
            "Que las citas de los participantes vayan textuales, sin arreglarles la gramática",
        ],
        "preguntas_comprension": [
            {"pregunta": "¿Por qué no corregir la gramática de una cita?",
             "respuesta": MARCA + "Porque deja de ser una cita. Y porque el "
                          "verificador compara la cita con la transcripción: si la "
                          "arreglo, ya no coincide y salta el error. Eso me parece "
                          "bien."},
            {"pregunta": "¿Qué no dice tu capítulo de resultados?",
             "respuesta": MARCA + "No dice cuántos pacientes del centro tienen cada "
                          "barrera. Ocho entrevistas no miden frecuencia."},
        ],
    },
]


def main() -> int:
    destino = AQUI / "decisiones"
    if destino.exists():
        shutil.rmtree(destino)
    for datos in DECISIONES:
        ruta_json, _ = registrar({**datos, "aprobado": True, "autor": AUTOR},
                                 dir_decisiones=destino)
        print(f"  {ruta_json.name}")
    print(f"\n  {len(DECISIONES)} decisiones ficticias en {destino.name}/")
    print("  Todas marcadas FICTICIO. Nadie tomó estas decisiones.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
