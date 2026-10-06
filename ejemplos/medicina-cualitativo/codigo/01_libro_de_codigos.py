"""Construye el libro de códigos y documenta la saturación.

La codificación la hace la persona, no el script: las categorías y los códigos
de abajo son la lectura de las transcripciones, y eso no se automatiza. Lo que sí
hace el script es lo mecánico y comprobable:

1. **Comprueba que cada cita del libro exista literalmente** en la transcripción
   que dice. Si una cita no aparece, falla. Es la misma regla que después aplica
   `verificar_cifras.py` sobre los capítulos, puesta ya en el análisis.
2. Calcula en qué entrevista apareció cada código por primera vez, que es de
   donde sale la curva de saturación.
3. Escribe todo en `resultados/`, para que los capítulos lo citen sin teclear
   nada a mano.

**La codificación de este ejemplo es ficticia**, como las transcripciones.

Uso:
    uv run python codigo/01_libro_de_codigos.py
"""
from __future__ import annotations

import json
import pathlib
import re
import sys

import pandas as pd
import yaml

AQUI = pathlib.Path(__file__).resolve().parent.parent
CRUDOS = AQUI / "datos" / "crudos"
RESULTADOS = AQUI / "resultados"

PARTICIPANTES = [f"E-0{n}" for n in range(1, 9)]

#: El libro de códigos. Cada código con su definición, qué incluye, qué excluye,
#: en qué entrevistas apareció y una cita que lo ilustra.
#:
#: El orden de las categorías es el de la presentación en el capítulo de
#: resultados, no el de frecuencia: una categoría que aparece en dos entrevistas
#: puede ser más importante que una que aparece en seis.
LIBRO = {
    "Lo que el cuerpo no avisa": {
        "definicion": "Interpretaciones del participante sobre una enfermedad "
                      "que no produce síntomas, y cómo eso afecta a tomar el "
                      "medicamento.",
        "codigos": {
            "ausencia_de_sintomas": {
                "definicion": "El participante explica el olvido o el abandono "
                              "por no sentir nada.",
                "incluye": "menciones a no sentir dolor o malestar como razón "
                           "para no tomar la pastilla",
                "excluye": "efectos adversos del medicamento, que van en "
                           "`efectos_adversos`",
                "entrevistas": ["E-01", "E-08"],
                "cita": "no me duele nada, entonces se me olvida",
                "de": "E-01",
            },
            "enfermedad_sin_fin": {
                "definicion": "La perspectiva de un tratamiento de por vida "
                              "como ruptura con la identidad de persona sana.",
                "incluye": "expresiones sobre la duración indefinida del "
                           "tratamiento y el paso a ser enfermo",
                "excluye": "quejas sobre la frecuencia de las citas",
                "entrevistas": ["E-01"],
                "cita": "de un día para otro me volví enfermo",
                "de": "E-01",
            },
        },
    },
    "El costo de seguir el tratamiento": {
        "definicion": "Barreras materiales: dinero, disponibilidad del "
                      "medicamento y tiempo de trabajo perdido.",
        "codigos": {
            "costo_directo": {
                "definicion": "El precio del medicamento compite con otros "
                              "gastos del hogar.",
                "incluye": "comparaciones del gasto en pastillas con ingresos u "
                           "otros gastos",
                "excluye": "el costo de transporte o del día de trabajo perdido",
                "entrevistas": ["E-02"],
                "cita": "hay meses que se me va en pastillas lo que gano en dos días de trabajo",
                "de": "E-02",
            },
            "desabastecimiento": {
                "definicion": "El medicamento no está disponible en la farmacia "
                              "del establecimiento.",
                "incluye": "menciones a que no hay stock y a sus consecuencias",
                "excluye": "no conseguir cita, que va en `acceso_al_servicio`",
                "entrevistas": ["E-02"],
                "cita": "cuando he ido tres veces y no hay, ya dejo de ir",
                "de": "E-02",
            },
            "dosis_estirada": {
                "definicion": "Modificación de la dosis por cuenta propia para "
                              "hacer durar el medicamento.",
                "incluye": "partir, espaciar o reservar pastillas por motivo "
                           "económico",
                "excluye": "suspensión por efectos adversos",
                "entrevistas": ["E-02"],
                "cita": "parto la pastilla en dos para que me dure el doble",
                "de": "E-02",
            },
            "jornada_incompatible": {
                "definicion": "El horario de trabajo choca con el horario de la "
                              "toma o con el del establecimiento.",
                "incluye": "menciones al horario laboral, al día de trabajo "
                           "perdido y al horario de atención",
                "excluye": "la espera para conseguir cupo",
                "entrevistas": ["E-04"],
                "cita": "entre perder el día y no tomar la pastilla, pierdo la pastilla",
                "de": "E-04",
            },
        },
    },
    "Lo que se entendió y lo que no": {
        "definicion": "Qué comprendió el participante de su diagnóstico, y qué "
                      "explicaciones propias llenaron los huecos.",
        "codigos": {
            "explicacion_insuficiente": {
                "definicion": "La información recibida no se entendió y no se "
                              "pidió aclaración.",
                "incluye": "lenguaje técnico no comprendido, vergüenza o prisa "
                           "que impiden preguntar",
                "excluye": "la duración de la consulta en sí, que va en "
                           "`consulta_breve`",
                "entrevistas": ["E-03", "E-07"],
                "cita": "me dijo palabras que no entendí y yo no le pregunté",
                "de": "E-03",
            },
            "modelo_propio": {
                "definicion": "Explicación alternativa de la enfermedad "
                              "construida por el participante.",
                "incluye": "atribuciones a los nervios, a emociones o a causas "
                           "puntuales; uso de remedios caseros en sustitución",
                "excluye": "creencias que acompañan al tratamiento sin "
                           "sustituirlo",
                "entrevistas": ["E-03"],
                "cita": "cuando la tomo no tomo la pastilla para no mezclar",
                "de": "E-03",
            },
            "desconoce_consecuencias": {
                "definicion": "El participante no sabe qué riesgo corre si "
                              "abandona el tratamiento.",
                "incluye": "menciones explícitas a no haber recibido esa "
                           "información",
                "excluye": "saberlo y aun así no adherir",
                "entrevistas": ["E-07", "E-08"],
                "cita": "nadie me ha explicado nunca qué me va a pasar si no la tomo",
                "de": "E-07",
            },
        },
    },
    "El trato y el acceso": {
        "definicion": "La experiencia de conseguir y recibir atención, y el "
                      "efecto del vínculo con el personal.",
        "codigos": {
            "acceso_al_servicio": {
                "definicion": "Dificultad para obtener una cita o un cupo.",
                "incluye": "colas, madrugadas, cupos agotados, regresar sin "
                           "atención",
                "excluye": "el horario de atención frente a la jornada laboral",
                "entrevistas": ["E-07"],
                "cita": "vengo a las cuatro de la mañana a hacer cola por un cupo",
                "de": "E-07",
            },
            "consulta_breve": {
                "definicion": "La duración y la discontinuidad de la consulta "
                              "limitan lo que se puede conversar.",
                "incluye": "menciones a la brevedad, a la prisa del personal y "
                           "al cambio de médico entre visitas",
                "excluye": "no entender la explicación recibida",
                "entrevistas": ["E-01", "E-07"],
                "cita": "nunca es el mismo doctor, cada vez es otro",
                "de": "E-01",
            },
            "vinculo_que_retiene": {
                "definicion": "Ser reconocido por el personal como motivo para "
                              "volver.",
                "incluye": "menciones al trato personal, a ser llamado por su "
                           "nombre, a sentir que a alguien le importa",
                "excluye": "el apoyo de la familia",
                "entrevistas": ["E-06"],
                "cita": "siento que a alguien le importa si vengo o no vengo",
                "de": "E-06",
            },
        },
    },
    "Lo que sostiene la adherencia": {
        "definicion": "Elementos que los participantes identifican como razón "
                      "para seguir el tratamiento.",
        "codigos": {
            "apoyo_familiar": {
                "definicion": "Un familiar organiza o recuerda la toma.",
                "incluye": "preparación de la medicación por otra persona, "
                           "recordatorios",
                "excluye": "el vínculo con el personal de salud",
                "entrevistas": ["E-06"],
                "cita": "mi hija me pone las pastillas en una cajita con los días",
                "de": "E-06",
            },
            "miedo_con_cara": {
                "definicion": "Haber visto una complicación en una persona "
                              "cercana como motor de la adherencia.",
                "incluye": "referencias a un caso conocido y a su efecto en la "
                           "conducta",
                "excluye": "advertencias recibidas del personal de salud",
                "entrevistas": ["E-08"],
                "cita": "desde que la vi así no he fallado un solo día",
                "de": "E-08",
            },
            "efectos_adversos": {
                "definicion": "Suspensión del medicamento por molestias "
                              "atribuidas a él.",
                "incluye": "síntomas atribuidos al fármaco y la decisión de "
                           "suspenderlo",
                "excluye": "suspensión por costo o por olvido",
                "entrevistas": ["E-05"],
                "cita": "estaba mejor antes de la pastilla que con la pastilla",
                "de": "E-05",
            },
            "dieta_compartida": {
                "definicion": "La alimentación familiar común dificulta la "
                              "dieta indicada.",
                "incluye": "menciones a cocinar igual para todos",
                "excluye": "el costo de los alimentos",
                "entrevistas": ["E-08"],
                "cita": "yo no voy a cocinar aparte sin sal mientras los demás comen normal",
                "de": "E-08",
            },
        },
    },
}


def _transcripciones() -> dict[str, str]:
    textos = {}
    for codigo in PARTICIPANTES:
        ruta = CRUDOS / f"FICTICIA_entrevista_{codigo}.txt"
        textos[codigo] = re.sub(r"\s+", " ",
                                ruta.read_text(encoding="utf8")).lower()
    return textos


def comprobar_citas(transcripciones: dict[str, str]) -> list[str]:
    """Cada cita del libro tiene que estar, literal, en su transcripción."""
    problemas = []
    for categoria, datos in LIBRO.items():
        for nombre, codigo in datos["codigos"].items():
            aguja = re.sub(r"\s+", " ", codigo["cita"]).lower()
            fuente = transcripciones.get(codigo["de"], "")
            if aguja not in fuente:
                problemas.append(
                    f"{categoria} / {nombre}: la cita no aparece en "
                    f"{codigo['de']}: {codigo['cita']!r}")
            for entrevista in codigo["entrevistas"]:
                if entrevista not in transcripciones:
                    problemas.append(
                        f"{categoria} / {nombre}: declara la entrevista "
                        f"{entrevista}, que no existe")
    return problemas


def main() -> int:
    RESULTADOS.mkdir(parents=True, exist_ok=True)
    transcripciones = _transcripciones()

    problemas = comprobar_citas(transcripciones)
    if problemas:
        print("No se escribió nada. Hay citas que no están en su transcripción:",
              file=sys.stderr)
        for p in problemas:
            print(f"  - {p}", file=sys.stderr)
        return 1

    # 1. El libro de códigos, tal cual, para que sea auditable.
    (RESULTADOS / "libro_de_codigos.yaml").write_text(
        yaml.safe_dump(LIBRO, allow_unicode=True, sort_keys=False, width=88),
        encoding="utf8")

    # 2. Matriz código × entrevista.
    todos = [(cat, nom, cod) for cat, d in LIBRO.items()
             for nom, cod in d["codigos"].items()]
    matriz = pd.DataFrame(
        [{"categoria": cat, "codigo": nom,
          **{p: int(p in cod["entrevistas"]) for p in PARTICIPANTES}}
         for cat, nom, cod in todos])
    matriz["entrevistas"] = matriz[PARTICIPANTES].sum(axis=1)
    matriz.to_csv(RESULTADOS / "matriz_codigos.csv", index=False)

    # 3. Saturación: cuántos códigos nuevos aporta cada entrevista.
    vistos: set[str] = set()
    filas = []
    for n, participante in enumerate(PARTICIPANTES, 1):
        nuevos = [nom for _, nom, cod in todos
                  if participante in cod["entrevistas"] and nom not in vistos]
        vistos.update(nuevos)
        filas.append({"orden": n, "entrevista": participante,
                      "codigos_nuevos": len(nuevos),
                      "acumulado": len(vistos),
                      "cuales": "; ".join(nuevos)})
    saturacion = pd.DataFrame(filas)
    saturacion.to_csv(RESULTADOS / "saturacion.csv", index=False)

    ultima_con_nuevos = int(saturacion.loc[saturacion["codigos_nuevos"] > 0,
                                           "orden"].max())
    contexto = {
        "participantes": len(PARTICIPANTES),
        "categorias": len(LIBRO),
        "codigos": len(todos),
        "entrevistas_sin_codigos_nuevos": len(PARTICIPANTES) - ultima_con_nuevos,
        "ultima_entrevista_con_codigo_nuevo": ultima_con_nuevos,
        "saturacion_alcanzada": bool(len(PARTICIPANTES) - ultima_con_nuevos >= 2),
        "datos": "FICTICIOS: transcripciones y codificación de prueba",
    }
    (RESULTADOS / "contexto.json").write_text(
        json.dumps(contexto, ensure_ascii=False, indent=1), encoding="utf8")

    print(f"  {contexto['codigos']} códigos en {contexto['categorias']} categorías")
    print("  todas las citas comprobadas contra su transcripción")
    print(f"  último código nuevo en la entrevista "
          f"{ultima_con_nuevos} de {len(PARTICIPANTES)}")
    print(f"  saturación: "
          f"{'sí' if contexto['saturacion_alcanzada'] else 'no se puede sostener'}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
