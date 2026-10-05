---
name: afinar-idea
description: Convierte un interés general en una pregunta de investigación que se pueda contestar con los datos que hay. Es la etapa 2 del flujo.
disable-model-invocation: true
---

# /afinar-idea — etapa 2

De "algo sobre presupuesto municipal" a una pregunta con unidad de análisis,
variables, estrategia y un juicio honesto de si se puede.

Es la etapa que más determina si la tesis se termina.

## 1. Marca la etapa y reúne el material

```
uv run python -c "from herramientas import registro_ia; registro_ia.marcar_etapa('afinar-idea')"
```

Lee antes de proponer nada:

- `decisiones/` — el tema que ya eligió y, sobre todo, **sus palabras**.
- `resultados/` — qué variables hay de verdad, con qué cobertura.
- `notas/ideas/`.
- El perfil activo: si exige hipótesis, con qué enfoques se puede trabajar.

## 2. Propón de 3 a 5 preguntas

Cada una tiene que ser **contestable con los datos que ya están en disco**. Si
necesitas datos que no existen, no es una opción: es un deseo.

De cada pregunta, di:

- **Pregunta**, en una frase, en forma de pregunta.
- **Unidad de análisis**: persona, hogar, distrito, institución educativa, año.
- **Variables o categorías** concretas, con el nombre que tienen en los datos.
- **Muestra o corpus**: cuántas observaciones y de qué años.
- **Estrategia**: qué se compara con qué y cómo.
- **Supuestos**: qué tiene que ser cierto para que el resultado signifique lo
  que parece.
- **Riesgos**: qué podría salir mal.
- **Semáforo de factibilidad**, con criterio explícito:
  - 🟢 los datos están, la estrategia es estándar, se puede hacer en semanas.
  - 🟡 se puede, pero algo hay que resolver: una variable que construir, un
    supuesto discutible, un volumen de limpieza grande.
  - 🔴 falta algo esencial. No lo propongas como viable; propónlo diciendo qué
    falta.

### Según el enfoque del perfil

**Cuantitativo.** Identificación es lo que el jurado va a atacar. Sé explícito
sobre si estás midiendo una asociación o afirmando una causa, y no uses lenguaje
causal para una correlación. Si hay endogeneidad obvia —simultaneidad, variable
omitida, selección—, dilo en los supuestos.

**Cualitativo.** La pregunta define categorías de análisis, no variables. Di
quiénes son los participantes, cómo se llegó a ellos, y cómo sabrás que llegaste
a saturación. Credibilidad y transferibilidad ocupan el lugar de la validez
externa.

**Argumentativo o por obra** (Arte, Literatura, Filosofía). No hay datos ni
metodología empírica: hay un **corpus** y un problema. Propón el corpus —qué
obras, qué edición, por qué esas— y la tesis que se va a defender. El perfil de
Letras tiene este modelo marcado como `solo_de_facto`: se puede usar, y queda
registrado que se aparta del instructivo.

## 3. Comprueba contra la norma

Dos cosas que el perfil impone y conviene mirar ahora:

- **¿Exige hipótesis?** Si es `obligatoria`, la pregunta tiene que admitir una.
  En `economia-fce` la hipótesis va **antes** de los objetivos, al revés que en
  la norma general.
- **El tema debería salir de la relación publicada por la escuela**
  (RR N.° 00744-R-20, §7.2 y §7.1 c-d). Si el tema no figura ahí, la escuela
  puede incluirlo coordinando con un docente. **No bloquees por esto**:
  menciónalo una vez para que no le sorprenda al inscribir el proyecto.

## 4. Pide la crítica

Lanza `critico-identificacion`. En cuantitativa mira supuestos causales y
validez; en cualitativa, rigor y transferibilidad. Hasta tres rondas; si no hay
acuerdo, las dos posturas van al tesista.

## 5. Punto de decisión

La decisión más importante del flujo. Decide: **pregunta, hipótesis si aplica, y
estrategia**.

- Presenta las preguntas con su semáforo. Marca una recomendada y di por qué
  —normalmente: porque es la que se puede terminar.
- Déjale combinar o proponer otra. Si propone algo inviable con los datos que
  hay, dilo claro y ofrece el recorte más cercano que sí funcione.
- Preguntas de comprensión, de las que hace un jurado:
  - ¿Por qué esta pregunta y no la más obvia?
  - Si el resultado sale al revés de lo que esperas, ¿qué significaría?
  - ¿Qué tendría que pasar para que esta pregunta no se pueda responder?

Registra con etapa `afinar-idea`. **Sus palabras textuales.**

## Qué NO hacer aquí

- No propongas una pregunta cuyos datos no hayas visto.
- No escondas un 🔴 detrás de un 🟡 para que la conversación sea agradable.
- No elijas por él. Recomienda y explica; la decisión es suya y la va a defender.
- No uses lenguaje causal si la estrategia solo sostiene una asociación.
