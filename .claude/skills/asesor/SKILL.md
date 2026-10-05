---
name: asesor
description: Prepara material para la reunión con el asesor y convierte sus observaciones en cambios y decisiones registradas.
disable-model-invocation: true
---

# /asesor

Dos usos: antes de ver al asesor, y después.

## Lo que esta skill no hace

**No convierte al asesor en una puerta.** Nada del flujo queda condicionado a que
un asesor confirme nada. El asesor es quien firma y acompaña la tesis, y su
criterio pesa más que cualquier cosa que diga este repositorio; pero el tesista
puede trabajar hoy, sin haber hablado con él.

Si el tesista no tiene asesor designado todavía, esta skill sigue sirviendo: el
material que prepara es el mismo que necesitará cuando lo tenga.

## Antes de la reunión

El asesor tiene poco tiempo. Lo que necesita es **qué cambió y qué hay que
decidir**, no la tesis completa otra vez.

Prepara en `registro/para_el_asesor.md`:

1. **En qué etapa va**, en dos líneas.
2. **Qué se hizo desde la última reunión.** Si está en el registro, con fechas.
3. **Las decisiones tomadas**, cada una en una línea: qué se eligió y por qué.
   Salen de `decisiones/`, textuales.
4. **Las preguntas concretas que se le quieren hacer.** Tres o cuatro, cada una
   con las opciones que el tesista ya consideró y hacia dónde se inclina. Una
   pregunta abierta —"¿qué le parece?"— desperdicia la reunión; una pregunta con
   opciones la aprovecha.
5. **Lo que está marcado `[VERIFICAR]` o `[PENDIENTE-NORMATIVA]`** y que el asesor
   puede resolver de memoria en diez segundos: el estilo de citas de la facultad,
   la persona gramatical, si el comité de ética hace falta en este caso.
6. **Lo que no cuadra**, si hay algo: un resultado contrario a la hipótesis, una
   limitación seria, una fuente que no se pudo conseguir. Esto va en el material,
   no se descubre en la reunión.

Si el perfil de la facultad no está `verificado`, inclúyelo entre las preguntas.
El asesor es la persona que mejor sabe qué pide su escuela, y lo que diga puede
mejorar el perfil para todos.

## Después de la reunión

1. Pídele las observaciones **como se las dijeron**. Si las anotó, mejor; si las
   cuenta, recógelas sin interpretarlas.
2. Clasifícalas:
   - **cambios de forma**: se hacen y se muestran;
   - **cambios de fondo** —la pregunta, la estrategia, la estructura—: se
     presentan como punto de decisión, porque cambian lo que el tesista va a
     defender;
   - **cosas que contradicen lo que dice el perfil o la normativa**: ver abajo.
3. Haz los cambios de forma. Lleva los de fondo a decisión.

## Cuando el asesor contradice lo que dice este repositorio

Pasa, y no siempre tiene la razón el repositorio.

- Si el asesor pide algo que **la normativa prohíbe** —parafrasear para bajar la
  similitud, poner una tabla como imagen—, dilo con su artículo y ofrece la
  alternativa que sí resuelve el problema. Eso no se hace aunque lo pida un
  asesor.
- Si pide algo que **la normativa no exige pero tampoco prohíbe**, se hace. Es su
  criterio y su firma.
- Si pide algo que **contradice el perfil**, probablemente el perfil esté
  incompleto: él conoce su escuela. Anótalo como fuente a verificar en
  `normativa/requisitos.md`, dilo al tesista, y sigue lo que dijo el asesor.
  Pero no marques el perfil como `verificado` por eso: hace falta el documento.

En los tres casos, lo que se hizo y por qué queda registrado.

## Registro

Si de la reunión sale una decisión de fondo, se registra como cualquier otra, con
la respuesta textual del tesista. **La observación del asesor no es la decisión**:
la decisión es qué hace el tesista con ella.

## Qué NO hacer aquí

- Condicionar el avance a que el asesor confirme algo.
- Registrar una observación del asesor como si fuera una decisión del tesista.
- Marcar un perfil como `verificado` porque el asesor lo dijo de palabra.
- Hacer algo que la normativa prohíbe porque lo pidió el asesor.
- Reinterpretar lo que dijo el asesor para que encaje con lo ya escrito.
