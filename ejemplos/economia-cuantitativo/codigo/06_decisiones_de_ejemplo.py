"""Registra las decisiones **ficticias** de este ejemplo.

En una tesis de verdad este script no existe: las decisiones se toman en sesión y
las escribe `registrar_decision.py` con las palabras del tesista. Aquí hace falta
porque un ejemplo completo necesita un historial de decisiones, y la única vía de
escritura en `decisiones/` es esa herramienta —que además exige una respuesta
textual, así que no se puede saltar.

**Todo lo que registra es ficticio y está marcado como tal**: el autor dice
`FICTICIO` y cada respuesta empieza por `[EJEMPLO FICTICIO]`. Nadie tomó estas
decisiones. Están escritas para que se parezcan a lo que diría un tesista, no
para hacerlas pasar por reales.

Uso:
    uv run python codigo/06_decisiones_de_ejemplo.py
"""
from __future__ import annotations

import pathlib
import shutil
import sys

AQUI = pathlib.Path(__file__).resolve().parent.parent
RAIZ_REPO = AQUI.parent.parent
sys.path.insert(0, str(RAIZ_REPO))

from herramientas.registrar_decision import registrar  # noqa: E402

AUTOR = "Tesista de ejemplo (FICTICIO)"
MARCA = "[EJEMPLO FICTICIO] "

# Las opciones elegidas se nombran una sola vez. Aparecen en tres campos
# —`opciones_presentadas`, `recomendada` y `eleccion`— y si se teclean tres
# veces acaban por no coincidir, con lo que la decisión registrada diría que el
# tesista eligió algo que no se le presentó.
TEMA_BM = ("Internet y productividad laboral en América Latina, con datos del "
           "Banco Mundial")
PREGUNTA_ASOCIACION = ("¿Existe asociación entre internet y productividad una "
                       "vez controlados país y año?")

DECISIONES = [
    {
        "etapa": "iniciar",
        "opciones_presentadas": [
            "Brecha digital y productividad en el Perú, con datos de la ENAHO",
            TEMA_BM,
            "Efecto del programa de banda ancha rural, con datos del MTC",
        ],
        "recomendada": TEMA_BM,
        "eleccion": TEMA_BM,
        "respuesta_textual": MARCA + (
            "Me quedo con la segunda. La primera me interesa más pero procesar "
            "varios años de ENAHO con los módulos cruzados me va a tomar meses y "
            "trabajo todo el día. La tercera depende de que el MTC me entregue "
            "datos por transparencia y no quiero quedarme esperando. La del Banco "
            "Mundial la puedo bajar hoy."),
        "cambios_pedidos": [
            "Que el periodo llegue hasta el último año disponible, no hasta 2019",
        ],
        "preguntas_comprension": [
            {"pregunta": "¿Qué estás midiendo exactamente cuando dices productividad?",
             "respuesta": MARCA + "El PBI dividido entre la gente que trabaja. No es "
                          "productividad total de factores, eso descuenta el capital y "
                          "yo no lo estoy descontando."},
            {"pregunta": "¿Por qué comparar países y no regiones del Perú?",
             "respuesta": MARCA + "Porque la serie comparable entre países existe y "
                          "está lista. Para regiones tendría que armarla yo."},
        ],
    },
    {
        "etapa": "explorar-datos",
        "opciones_presentadas": [
            "Solo indicadores del Banco Mundial (WDI)",
            "Banco Mundial más ERESTEL de OSIPTEL para el Perú",
            "Banco Mundial más Enterprise Surveys",
        ],
        "recomendada": "Solo indicadores del Banco Mundial (WDI)",
        "eleccion": "Solo indicadores del Banco Mundial (WDI)",
        "respuesta_textual": MARCA + (
            "Solo Banco Mundial. ERESTEL me la mostraste y es mejor que la ENAHO "
            "para telecomunicaciones, pero es solo del Perú y mi pregunta es "
            "comparativa; si la meto, cambio de pregunta. La dejo anotada como "
            "recomendación para quien siga esto."),
        "cambios_pedidos": [
            "Agregar desempleo y gasto en educación como controles",
            "Anotar la fecha de descarga porque el Banco Mundial revisa series hacia atrás",
        ],
        "preguntas_comprension": [
            {"pregunta": "¿De dónde salen estos datos y quién los recolectó?",
             "respuesta": MARCA + "El Banco Mundial los compila, pero no los levanta: "
                          "vienen de los institutos de estadística de cada país y, para "
                          "internet, de la Unión Internacional de Telecomunicaciones."},
            {"pregunta": "¿Qué no puedes responder con estos datos?",
             "respuesta": MARCA + "Nada sobre empresas ni sobre personas, y nada sobre "
                          "para qué usan internet. Solo sé qué porcentaje lo usa."},
        ],
    },
    {
        "etapa": "afinar-idea",
        "opciones_presentadas": [
            "¿Cuánto crece la productividad cuando crece el internet? (efecto causal)",
            PREGUNTA_ASOCIACION,
            "¿Qué países aprovechan mejor su conectividad? (eficiencia relativa)",
        ],
        "recomendada": PREGUNTA_ASOCIACION,
        "eleccion": PREGUNTA_ASOCIACION,
        "respuesta_textual": MARCA + (
            "La segunda. La primera la quería yo, pero me explicaste que sin un "
            "instrumento no puedo decir «efecto» y no tengo instrumento. Prefiero "
            "contestar bien una pregunta más chica que contestar mal la grande. La "
            "hipótesis la dejo en positivo, como dice la literatura, y si sale al "
            "revés lo pongo."),
        "cambios_pedidos": [
            "Dejar la hipótesis en la dirección que predice la literatura, no en la que yo espero",
        ],
        "preguntas_comprension": [
            {"pregunta": "Si el coeficiente sale positivo, ¿puedes decir que el "
                         "internet elevó la productividad?",
             "respuesta": MARCA + "No. Puedo decir que están asociados descontando país "
                          "y año. Un país más productivo también puede pagar más internet "
                          "y yo no puedo separar eso."},
            {"pregunta": "¿Para qué sirven los efectos fijos de año?",
             "respuesta": MARCA + "Para quitar lo que le pasó a toda la región el mismo "
                          "año. Si no, cualquier par de series que suben juntas sale "
                          "correlacionado."},
        ],
    },
    {
        "etapa": "literatura",
        "opciones_presentadas": [
            "Centrar la revisión en la literatura a favor del efecto agregado",
            "Organizar la revisión como una discusión entre hallazgos opuestos",
            "Centrar la revisión en la paradoja de la productividad",
        ],
        "recomendada": "Organizar la revisión como una discusión entre hallazgos opuestos",
        "eleccion": "Organizar la revisión como una discusión entre hallazgos opuestos",
        "respuesta_textual": MARCA + (
            "Como discusión. Czernich y compañía encuentran efecto, Maurseth no, y "
            "mi capítulo II tiene que dejar claro que eso está abierto. Si solo cito "
            "a los que encuentran efecto y después mi resultado sale nulo, el jurado "
            "me va a preguntar por qué no cité al que coincide conmigo."),
        "cambios_pedidos": [
            "Incluir a Maurseth 2018, que es el antecedente más cercano",
            "Comprobar cada DOI en Crossref antes de agregarlo a la bibliografía",
        ],
        "preguntas_comprension": [
            {"pregunta": "¿Cuál es el hueco que llena tu tesis?",
             "respuesta": MARCA + "Que para América Latina no encontré una medición que "
                          "separe la variación entre países de la variación dentro de "
                          "cada país. Czernich lo hace para la OCDE."},
            {"pregunta": "¿Por qué Czernich encuentra efecto y tú no?",
             "respuesta": MARCA + "Ellos usan variables instrumentales y yo no, y su "
                          "muestra es de países de la OCDE. Esa diferencia favorece a "
                          "su diseño, no al mío."},
        ],
    },
    {
        "etapa": "proyecto",
        "opciones_presentadas": [
            "Estructura del Anexo 2B de la UNMSM (modelo cuantitativo)",
            "Estructura de la guía de la Facultad de Ciencias Económicas",
        ],
        "recomendada": "Estructura del Anexo 2B de la UNMSM (modelo cuantitativo)",
        "eleccion": "Estructura del Anexo 2B de la UNMSM (modelo cuantitativo)",
        "respuesta_textual": MARCA + (
            "El Anexo 2B. Me dijiste que la guía de la facultad regula el proyecto y "
            "no el informe final, y que el perfil de Economía está marcado como «por "
            "verificar» porque el documento no tiene resolución. Me parece bien usar "
            "la norma general, que sí es norma. Lo voy a comentar con mi asesora en "
            "la próxima reunión, pero no me quedo esperando para avanzar."),
        "cambios_pedidos": [],
        "preguntas_comprension": [
            {"pregunta": "¿De dónde sale la estructura que estás usando?",
             "respuesta": MARCA + "Del Anexo 2B de la RR 00744-R-20, que es la directiva "
                          "general de la universidad y aplica a todas las facultades."},
            {"pregunta": "¿Qué pasa si tu escuela pide otra cosa?",
             "respuesta": MARCA + "Se ajusta el perfil y queda registrado como una "
                          "decisión mía. No hay que rehacer el contenido, solo el orden."},
        ],
    },
    {
        "etapa": "analizar",
        "opciones_presentadas": [
            "Solo la especificación con efectos fijos de país y año",
            "Siete especificaciones, reportando todas, incluidas las que no salieron",
            "Reportar la que mejor se ajusta a los datos",
        ],
        "recomendada": "Siete especificaciones, reportando todas, incluidas las que no salieron",
        "eleccion": "Siete especificaciones, reportando todas, incluidas las que no salieron",
        "respuesta_textual": MARCA + (
            "Las siete, todas reportadas. El resultado me salió al revés de mi "
            "hipótesis: la correlación es fuerte y positiva, y con efectos de año se "
            "va a cero. Lo pongo tal cual. Si escondo las dos que salen "
            "significativas sin efectos de año, estoy ocultando justo lo que hace "
            "interesante el resultado; y si escondo las cinco nulas, estoy mintiendo."),
        "cambios_pedidos": [
            "Agrupar los errores estándar por país",
            "Agregar una especificación en primeras diferencias",
            "Agregar una especificación sin el Perú, para ver si el resultado depende de un país",
        ],
        "preguntas_comprension": [
            {"pregunta": "¿Por qué agrupar los errores estándar por país?",
             "respuesta": MARCA + "Porque las observaciones de un mismo país en años "
                          "distintos no son independientes. Sin agrupar, los intervalos "
                          "salen más angostos de lo que deberían."},
            {"pregunta": "Tu resultado es nulo. ¿Eso demuestra que la conectividad no sirve?",
             "respuesta": MARCA + "No. El intervalo incluye el cero pero también incluye "
                          "efectos positivos chicos. Lo que descarto es un efecto del "
                          "tamaño que sugería la correlación simple, no cualquier efecto."},
        ],
    },
    {
        "etapa": "redactar",
        "opciones_presentadas": [
            "Primera persona del plural («estimamos», «encontramos»)",
            "Impersonal («se estima», «se encuentra»)",
            "Primera persona del singular («estimo», «encuentro»)",
        ],
        "recomendada": "Impersonal («se estima», «se encuentra»)",
        "eleccion": "Impersonal («se estima», «se encuentra»)",
        "respuesta_textual": MARCA + (
            "Impersonal. El perfil de Economía no fija la persona gramatical —sale "
            "como pendiente de normativa— así que lo decido yo: impersonal, que es "
            "como están escritas las tesis que vi en Cybertesis de mi escuela. Soy "
            "autor único, así que el plural me suena raro."),
        "cambios_pedidos": [
            "Que ninguna cifra se escriba a mano: todas insertadas desde resultados/",
            "Que el capítulo de resultados no interprete nada",
        ],
        "preguntas_comprension": [
            {"pregunta": "¿Por qué el capítulo de resultados no puede interpretar?",
             "respuesta": MARCA + "Porque interpretar es el trabajo de la discusión. Si "
                          "mezclo, el jurado no puede distinguir qué encontré de qué "
                          "creo que significa."},
            {"pregunta": "¿Qué NO dice tu capítulo de resultados?",
             "respuesta": MARCA + "No dice que el internet no sirva, y no dice nada sobre "
                          "empresas ni personas. Son promedios de países."},
        ],
    },
]


def main() -> int:
    destino = AQUI / "decisiones"
    if destino.exists():
        shutil.rmtree(destino)

    for datos in DECISIONES:
        datos = {**datos, "aprobado": True, "autor": AUTOR}
        ruta_json, _ = registrar(datos, dir_decisiones=destino)
        print(f"  {ruta_json.name}")

    print(f"\n  {len(DECISIONES)} decisiones ficticias en {destino.name}/")
    print("  Todas marcadas FICTICIO. Nadie tomó estas decisiones.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
