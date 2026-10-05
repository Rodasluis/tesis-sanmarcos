---
name: redactar
description: Redacta un capítulo de la tesis desde las decisiones registradas, los archivos de resultados/ y referencias.bib. Recibe el capítulo como argumento. Es la etapa 6 del flujo.
disable-model-invocation: true
---

# /redactar <capítulo> — etapa 6

Escribe un capítulo. Uno por invocación, porque un capítulo se revisa entero o
no se revisa.

## De dónde sale cada frase

Un capítulo de este repositorio se escribe desde **tres fuentes y ninguna más**:

| Lo que vas a escribir | De dónde sale | Si no está ahí |
|---|---|---|
| Qué se investigó y por qué así | `decisiones/` | no lo decidas tú: pregunta |
| Cada cifra, tabla y cita de participante | `resultados/` | no la escribas |
| Cada afirmación sobre lo que otros dicen | `referencias.bib` | `[VERIFICAR]` |

Tu memoria no es una fuente. Si al escribir "varios estudios señalan que…"
sientes que sabes cuáles, esa sensación no es una cita. Escribe `[VERIFICAR]`
y sigue.

## 1. Marca la etapa y comprueba que haya con qué

```
uv run python -c "from herramientas import registro_ia; registro_ia.marcar_etapa('redactar')"
uv run python -m herramientas.verificar_decisiones --exigir-hasta analizar
```

Si faltan decisiones, dilo y ofrece volver a la etapa que falta. No escribas un
capítulo encima de decisiones que nadie tomó: todo lo que escribas así habrá que
rehacerlo.

## 2. Resuelve qué capítulo es

El argumento puede venir como número romano, como número o como nombre. Mapea
contra las secciones del **perfil activo**, no contra esta lista:

```
uv run python -m herramientas.perfiles --mostrar informe_final
```

En el perfil base (Anexo 2B de la RR N.° 00744-R-20) son siete:

| # | Capítulo | Qué contiene de verdad |
|---|---|---|
| I | Introducción | el problema, los objetivos, la importancia, los límites |
| II | Revisión de literatura | marco teórico, antecedentes, bases, términos |
| III | Hipótesis y variables | hipótesis, variables, operacionalización |
| IV | Materiales y métodos | diseño, población y muestra, instrumentos, análisis |
| V | Resultados | lo que salió, sin interpretarlo |
| VI | Discusión | qué significa, contra la literatura |
| VII | Conclusiones y recomendaciones | lo que se responde y lo que no |

Si el perfil activo cambia el nombre, el número o el orden, **manda el perfil**.
Un capítulo con el título que tú recuerdas y no el que pide la facultad es una
observación del jurado garantizada.

Escribe en `capitulos/NN-nombre.qmd`, con el número de orden por delante para
que el render no dependa del nombre.

## 3. La frontera entre resultados y discusión

Es la que más se cruza y la más fácil de arreglar antes de que la cruce el
jurado.

- **En V no se interpreta.** "El coeficiente es 0.34 (p = 0.02)" va en V.
  "Esto sugiere que el programa funcionó" va en VI.
- **En VI no aparecen cifras nuevas.** Si en la discusión hay un número que no
  estaba en V, o es un error o falta en V.

## 4. Cómo se escribe cada tipo de capítulo

**I — Introducción.** Del problema a la pregunta, no al revés. La importancia es
concreta: a quién le sirve y para qué decisión. Las limitaciones van aquí y
vuelven en VII, y son las reales: las que `/explorar-datos` ya encontró.

**II — Revisión de literatura.** No es una lista de resúmenes. Se organiza por
discusiones: quién sostiene qué, quién lo contradice, qué quedó sin resolver —y
ese hueco es el de esta tesis. Cada párrafo con su cita; cada cita textual con su
número de página.

**III — Hipótesis y variables.** La hipótesis sale de la decisión de
`/afinar-idea`, textual. La operacionalización dice, de cada variable, cómo se
mide **en los datos que existen**, con el nombre de la variable en el archivo.

**IV — Materiales y métodos.** Tiene que permitir que otro lo repita. Población y
muestra con números y criterios de inclusión y exclusión. Si hubo faltantes o
exclusiones, cuántas y por qué. Si hay factor de expansión, se declara su uso. Y
lo ético: consentimiento, anonimización, comité si corresponde.

**V — Resultados.** Cada cifra se lee de `resultados/`. Cada tabla y cada figura
tienen número, título y la nota de qué muestra y de dónde sale. Se reportan los
resultados contrarios a la hipótesis igual que los demás.

**VI — Discusión.** Tres movimientos: qué encontramos, cómo encaja con lo que ya
se sabía (con citas), y qué debilita nuestra conclusión. Esto último es el párrafo
que separa una tesis seria de un informe. Si la estrategia sostiene una
asociación, se dice asociación.

**VII — Conclusiones y recomendaciones.** Una conclusión por objetivo, y ninguna
más. Las recomendaciones se dirigen a alguien concreto y se desprenden de lo que
se encontró, no de lo que al tesista le parece.

## 5. Las cifras se insertan, no se copian

Un número escrito a mano en el texto queda huérfano: cuando el análisis cambie,
el texto mentirá y nadie lo notará. Insértalos desde `resultados/`:

```markdown
```{r}
#| echo: false
resultados$efecto_principal
```
```

`verificar_cifras.py` marca como **error** toda cifra del texto que no exista en
`resultados/`. No es una formalidad: es el principio 1.

## 6. Estilo

Lo fija el **perfil activo**, no tu costumbre:

- **Persona gramatical**: la del perfil. Si dice `[PENDIENTE-NORMATIVA]`,
  pregúntale al tesista y registra su respuesta como decisión.
- **Estilo de citas**: el del perfil. Igual con `[PENDIENTE-NORMATIVA]`.
- Español formal peruano. Frases que se puedan leer en voz alta en la
  sustentación, porque ahí van a leerse.

## 7. Respeta lo que el tesista escribió

Antes de regenerar un capítulo, mira si tiene ediciones a mano (`git diff`,
historial). **Las ediciones del tesista se conservan.** Si tu versión nueva
choca con una suya, no la sobrescribas: muéstrale las dos y que él elija.

Es su tesis y la va a defender con su nombre. Pisarle una frase que escribió
porque la tuya suena mejor es el error más fácil de cometer aquí.

## 8. Render y crítica

```
uv run python -m herramientas.activar_perfil
quarto render
```

Lanza `critico-redaccion`: comprueba trazabilidad de cifras y citas, el salto de
resultados a discusión, y las conclusiones que el texto no sostiene.

## 9. Punto de decisión

Decisión: **el capítulo queda aprobado, o con qué cambios**.

- Resume qué dice el capítulo y de qué decisión y qué resultados sale cada parte.
- Señala tú mismo sus puntos débiles. Es mejor que los encuentre el tesista ahora
  que el jurado después.
- Preguntas de comprensión: que explique con sus palabras la parte más técnica
  del capítulo; qué pasa si el supuesto principal no se cumple; qué **no** dice
  este capítulo.

Registra con etapa `redactar`, indicando el capítulo en la elección.

## Qué NO hacer aquí

- Inventar una cita, un autor, un año o una página.
- Escribir una cifra que no esté en `resultados/`.
- Escribir una cita de participante que no esté literalmente en una
  transcripción.
- Rellenar un `[VERIFICAR]` con una fuente recordada.
- Interpretar en V o traer cifras nuevas en VI.
- Concluir más de lo que los resultados sostienen.
- Sobrescribir las ediciones del tesista.
