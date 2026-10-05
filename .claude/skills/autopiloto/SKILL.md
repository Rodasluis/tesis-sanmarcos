---
name: autopiloto
description: Encadena varias etapas seguidas, deteniéndose en cada punto de decisión para que el tesista responda. No decide por él.
disable-model-invocation: true
---

# /autopiloto

Hace seguido todo el trabajo operativo que no requiere decisión, y **se para en
cada punto de decisión**.

## Lo que automatiza y lo que no

Automático: catalogar fuentes, descargar, limpiar, buscar literatura, correr
análisis, redactar borradores, rendir, verificar, generar entregables.

**No automático, nunca:** las once decisiones del flujo. Cada una la toma el
tesista en sesión, con sus palabras.

Esto no es una restricción de diseño que se pueda relajar si hay prisa. Es el
principio 3, y `registrar_decision.py` **se niega** a escribir una decisión sin
`respuesta_textual` y `aprobado: true`. No hay bandera para saltárselo. Si
intentas pasar por alto un punto de decisión, la herramienta falla, y hace bien.

La razón es simple: el tesista va a sustentar esto delante de un jurado que le va
a preguntar por qué eligió lo que eligió. Una decisión que tomó Claude es una
pregunta que no va a saber responder.

## 1. Acuerda el alcance antes de empezar

Dile exactamente **hasta dónde** va a correr y **en qué va a tener que
participar**. Algo así:

> Voy a correr las etapas 1 a 3. Me voy a parar tres veces: para que elijas las
> fuentes, para que elijas la pregunta y para que digas qué lecturas son
> centrales. Cada parada son unos diez minutos. Entre paradas puedo tardar un
> rato largo.

Si no puede acompañar la sesión, mejor que corra una etapa sola. Un autopiloto
que llega a una decisión y no hay nadie se queda parado, y eso es lo correcto,
pero es tiempo perdido.

## 2. Por cada etapa

1. Marca la etapa en el registro.
2. Comprueba que las decisiones anteriores estén:
   `uv run python -m herramientas.verificar_decisiones --exigir-hasta <etapa previa>`
3. Haz el trabajo de la skill de esa etapa, con sus mismas reglas. `/autopiloto`
   no es una vía rápida con reglas propias: es la misma skill, encadenada.
4. Lanza su crítico y atiende lo serio.
5. **Párate en el punto de decisión.** Presenta las opciones, marca la
   recomendada, espera.
6. Registra con `registrar_decision.py` y sigue.

## 3. Cuando llegues a una decisión

Para de verdad. Dos cosas que no valen:

- **Elegir la recomendada "porque es obvia".** Si fuera obvia, no sería una
  decisión. Pregunta.
- **Dar por respondida una pregunta de comprensión con lo que el tesista dijo
  antes.** Se le pregunta de nuevo, en esta etapa.

Si el tesista dice "haz lo que creas mejor", no es una respuesta que puedas
registrar. Explícale por qué: en la sustentación le van a preguntar por esta
elección, y la respuesta "lo eligió la herramienta" no sirve. Dale las dos
opciones más fuertes y pídele que elija entre ellas. Que elija rápido está bien;
que no elija, no.

## 4. Párate también si

- Un crítico levanta algo que cambia el rumbo —los datos no dan para la pregunta,
  la estrategia no identifica lo que se quiere— en vez de seguir adelante y
  avisar al final.
- Una fuente no se puede descargar y haría falta cambiar de fuente.
- Una verificación da errores que no puedes arreglar solo.
- El perfil pide algo que no está definido (`[PENDIENTE-NORMATIVA]`) y afecta a
  lo que estás escribiendo.

En todos estos casos, el trabajo hecho hasta ahí se queda hecho y commiteado. No
se pierde nada por pararse.

## 5. Al terminar

Di **qué quedó hecho, qué decidió el tesista y qué sigue**. Si paraste antes de
lo acordado, di dónde y por qué.

Cada etapa deja su commit: `[claude] <etapa>: <resumen>`. Así se puede volver
atrás por etapas, no por archivos.

## Qué NO hacer aquí

- Registrar una decisión que el tesista no tomó explícitamente. Es la violación
  más grave posible en este repositorio.
- Interpretar un silencio, un "ok" suelto o un "sí" como elección entre opciones.
- Resumir o mejorar la respuesta del tesista: se guarda textual.
- Saltarse las preguntas de comprensión por ir más rápido.
- Avanzar de etapa sin decisión aprobada.
- Correr hasta `/entregar` sin que el tesista haya visto los capítulos.
