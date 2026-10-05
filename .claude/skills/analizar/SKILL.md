---
name: analizar
description: Hace el análisis de la tesis — limpieza, estimaciones y robustez, o codificación y saturación en cualitativa — dejando todo reproducible. Es la etapa 5 del flujo.
disable-model-invocation: true
---

# /analizar — etapa 5

Produce los resultados sobre los que se escribirá la tesis. Todo lo que salga de
aquí tiene que poder rehacerse corriendo el código otra vez.

## La regla que sostiene todo

**Cada número que después aparezca en el texto nace aquí, en un archivo de
`resultados/`, generado por código de `codigo/`.** No hay otra vía.
`verificar_cifras.py` lo comprueba y marca como error cualquier cifra escrita a
mano que no exista en `resultados/`.

## 1. Marca la etapa

```
uv run python -c "from herramientas import registro_ia; registro_ia.marcar_etapa('analizar')"
uv run python -m herramientas.verificar_decisiones --exigir-hasta afinar-idea
```

## 2. Limpieza, con el código a la vista

De `datos/crudos/` nunca se toca nada. Toda transformación:

1. Se escribe como script en `codigo/`, numerado por orden de ejecución
   (`01_limpieza.py`, `02_variables.py`…).
2. Produce un archivo en `datos/procesados/`.
3. Deja constancia de cuántas observaciones entraron y cuántas salieron, y por
   qué se perdieron las que se perdieron.

Esa última parte es la que un jurado pregunta. "Se eliminaron los casos
incompletos" sin decir cuántos ni si se parecían al resto es una respuesta que no
sobrevive.

**Si imputas algo, decláralo.** En el código, en los resultados y en el texto.
Imputar sin decirlo es exactamente lo que el art. 10 d) del Código de Ética llama
manipulación de la información.

## 3A. Si la tesis es cuantitativa

**Estimación principal.** La que responde la pregunta decidida. Nada más.

**Robustez.** Rehaz la estimación cambiando una cosa cada vez: otra definición de
la variable, otro subconjunto, otro método, con y sin controles. Guarda **todas**
las especificaciones que probaste, incluidas las que no salieron.

Eso último no es opcional. Guardar solo lo que funcionó es *p-hacking*, aunque no
se llame así: produce un resultado que parece sólido porque se escondió el resto.
Una tabla de robustez donde el efecto desaparece en una especificación es
información valiosa, y el jurado la respeta mucho más que una tabla perfecta.

**Factores de expansión**: si la encuesta los trae, se usan. Siempre.

**Lenguaje**: si la estrategia sostiene una asociación, se dice asociación. "Está
asociado con" y "causa" no son sinónimos y el jurado lo sabe.

## 3B. Si la tesis es cualitativa

**Libro de códigos** en `resultados/`, en YAML: código, definición, criterio de
inclusión, criterio de exclusión, ejemplo. Es el documento que hace auditable el
análisis.

**Codificación.** Cada cita codificada apunta a su transcripción de
`datos/crudos/`, con identificador del participante y ubicación. Después,
`verificar_cifras.py` comprueba que **cada cita existe literalmente** en una
transcripción. Si no existe, es un error, no un matiz de redacción.

**Saturación.** Documenta cuándo dejaron de aparecer códigos nuevos y con cuántos
participantes. Si no se alcanzó, dilo: es un hallazgo y una limitación, no un
fracaso que haya que disimular.

**Categorías.** Toda categoría sale del libro de códigos. Ninguna se inventa al
escribir porque "ordena mejor el capítulo".

## 4. Resultados reutilizables

En `resultados/`, en formatos que el texto pueda leer: CSV para tablas, JSON o
YAML para valores sueltos que se insertan en el párrafo.

Piensa en cómo se va a citar cada número desde `/redactar`. Un resultado que solo
existe como gráfico PNG no se puede insertar como cifra en una frase.

## 5. Comprueba

```
uv run python -m herramientas.verificar_cifras --detalle
```

## 6. Pide la crítica

- `critico-codigo` en cuantitativa: reproducibilidad, errores, *p-hacking*.
- `critico-codificacion` en cualitativa: consistencia del libro de códigos y
  trazabilidad de cada cita a su transcripción.

Si el crítico dice que el código no es reproducible, no discutas: arréglalo. La
prueba es sencilla —borrar `resultados/`, correr los scripts en orden y ver si
vuelve a salir lo mismo.

## 7. Punto de decisión

Decisión: **la especificación principal y las de robustez**, o **el libro de
códigos final**.

- Presenta la especificación principal y qué cambia en las alternativas.
- Si el resultado es contrario a la hipótesis, **dilo sin suavizarlo**. Un
  resultado negativo bien hecho es una tesis; un resultado maquillado es un
  problema que aparece en la sustentación.
- Preguntas de comprensión: por qué esta especificación y no otra; qué pasaría si
  el supuesto principal no se cumpliera; qué no demuestra este resultado.

Registra con etapa `analizar`.

## Qué NO hacer aquí

- No inventes ni simules datos, ni "para probar el código". Si hace falta un
  ejemplo, que esté marcado como ficticio en el nombre del archivo y dentro.
- No borres las especificaciones que no salieron.
- No redondees hasta que un resultado parezca significativo.
- No escribas una cita de participante que no esté en una transcripción.
- No presentes como causal lo que es correlacional.
