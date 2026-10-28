---
name: jurado
description: Simula el jurado de la facultad del perfil activo, con observaciones accionables y preguntas reales de sustentación. Es la etapa 7 del flujo.
disable-model-invocation: true
---

# /jurado — etapa 7

Pone la tesis delante de tres lectores hostiles antes de que la lean los de
verdad.

## Para qué sirve y para qué no

Sirve para encontrar las observaciones mientras todavía hay tiempo de atenderlas.

**No predice la calificación y no aprueba nada.** Es una simulación hecha por el
mismo sistema que escribió los borradores, así que comparte sus puntos ciegos: lo
que no se le ocurrió al redactar tampoco se le va a ocurrir al criticar. Dilo al
presentar los resultados, sin rodeos. Un tesista que sale de aquí creyendo que ya
pasó el jurado está peor que antes de entrar.

## 1. Marca la etapa y lee el perfil

```
uv run python -c "from herramientas import registro_ia; registro_ia.marcar_etapa('jurado')"
uv run python -m herramientas.perfiles --mostrar sustentacion
```

Del perfil sacas **cuántos miembros tiene el jurado, cuánto dura la exposición,
cuánto las preguntas, y si hay rúbrica**. Si el perfil dice
`[PENDIENTE-NORMATIVA]`, di que no lo sabemos y simula con la estructura general.
No inventes una composición de jurado.

Medicina (RD N.° 002373-2023-D-FM, arts. 33 y 34) es el caso con todo definido:
cuatro miembros, 15 a 20 minutos de exposición, hasta 20 de preguntas, el asesor
delibera con voz pero sin voto, y una rúbrica de 20 puntos en cinco criterios.
Si el perfil activo la trae, úsala.

## 2. Los tres jurados

Lánzalos **en paralelo**, sobre la tesis completa. Son de solo lectura: observan,
no corrigen.

| Agente | Qué ataca |
|---|---|
| `jurado-metodologico` | diseño, muestra, identificación, supuestos, qué sostiene el resultado |
| `jurado-tematico` | pertinencia, literatura, aporte real, discusión |
| `jurado-formal` | estructura del perfil, citas, formato, normativa, anexos |

Cada uno devuelve observaciones y preguntas. No limes sus críticas al
transmitirlas: el tesista necesita leerlas como se las van a decir.

## 3. Clasifica lo que encontraron

Una lista de treinta observaciones sin jerarquía es inútil. Ordénalas en tres
grupos, y en cada una di **qué cambiar, dónde y cuánto cuesta**:

- **Impide sustentar.** Un resultado que el texto no sostiene, una cita que no
  existe, una cifra que no está en `resultados/`, una sección que el perfil exige
  y no está. Se arregla antes de seguir.
- **Van a preguntarlo.** No está mal, está incompleto o sin defender. Se mejora
  el texto o se prepara la respuesta.
- **Mejora.** Si hay tiempo.

Si dos jurados se contradicen, no elijas por el tesista: muéstrale las dos
posturas y que decida él, porque es él quien va a responder.

## 4. El banco de preguntas

De los tres agentes salen preguntas. Guárdalas en
`resultados/banco_preguntas.yaml`, cada una con:

```yaml
- pregunta: "¿Por qué eligió esta especificación y no la que incluye los controles regionales?"
  de: metodologico
  dificultad: alta
  donde: "capitulos/05-resultados.qmd, tabla 3"
  respuesta_apoyo: "La robustez 2 la incluye; el coeficiente baja de 0.34 a 0.29 y sigue significativo."
  respondida_por_el_tesista: null
```

`respuesta_apoyo` es material de apoyo, **no la respuesta del tesista**. Las
respuestas del tesista se recogen en `/sustentacion` y se registran con sus
palabras.

Añade al banco las preguntas de comprensión de todas las etapas anteriores: están
en `decisiones/`, en `preguntas_comprension`. Las que el tesista contestó flojo
en su momento son las que más probablemente reaparezcan.

## 5. Ensayo de la pregunta incómoda

Elige las tres peores observaciones y pregúntaselas al tesista directamente, como
se las van a preguntar. Sin preparar el terreno.

Si no sabe responder una, eso no es un fracaso del ensayo: es exactamente lo que
el ensayo tenía que encontrar. Anótalo y vuelve a ello en `/sustentacion`.

## 6. Punto de decisión

Decisión: **qué observaciones se atienden y cuáles no, con su razón**.

Una observación que se decide no atender no desaparece: queda registrada con el
motivo, y si el jurado real la levanta, el tesista ya pensó su respuesta. Eso es
mejor que haberla olvidado.

- Presenta la lista clasificada, con costo estimado de cada arreglo.
- Recomienda atender todas las del primer grupo.
- Preguntas de comprensión: cuál de estas observaciones es la más grave y por
  qué; cómo responderías la que decidiste no atender.

Registra con etapa `jurado`.

## Qué NO hacer aquí

- Presentar esto como una aprobación, una nota o un pronóstico de nota.
- Suavizar una observación para no desanimar al tesista.
- Inventar la composición del jurado o una rúbrica que el perfil no trae.
- Atender tú las observaciones de fondo sin decidirlo con el tesista: cambian lo
  que él va a defender.
- Dar por respondida una pregunta que el tesista no respondió.
