# Ejemplo: tesis cualitativa con perfil `medicina-fm`

Proyecto de demostración del flujo cualitativo: transcripciones, libro de
códigos, saturación, citas de participantes trazables y referencias en Vancouver.

**Pregunta:** ¿cómo describen los usuarios de un centro de salud de Lima las
barreras que encuentran para seguir su tratamiento antihipertensivo?

## Las transcripciones son FICTICIAS

**Ninguna de estas entrevistas ocurrió. No hay participantes.** Las ocho
transcripciones se escribieron para que el ejemplo pueda recorrer el flujo
completo sin usar datos de nadie.

Están marcadas tres veces: en el nombre del archivo (`FICTICIA_`), en la primera
línea de cada archivo, y en
`datos/crudos/LEEME_ESTOS_DATOS_SON_FICTICIOS.md`. Hay pruebas del repositorio
que lo comprueban.

El principio 1 de `CLAUDE.md` prohíbe simular datos, y esto no es una excepción:
es material de prueba del propio repositorio, no evidencia de una tesis. Nada de
aquí respalda una afirmación sobre el mundo. Ofrecerle a un tesista
«transcripciones de ejemplo para ir avanzando» sí sería una violación, y de las
graves.

Las referencias, en cambio, **son reales**: cuatro artículos comprobados en
Crossref por su DOI, uno de ellos peruano.

## El resultado incómodo: la saturación no se alcanzó

La octava y última entrevista todavía aportó códigos nuevos. El ejemplo
**declara que no hubo saturación** en el resumen, en las limitaciones, en el
método, en los resultados y en las conclusiones, en lugar de afirmarla.

Está hecho así a propósito. Agrupar los 16 códigos en tres categorías amplias
habría dejado la curva plana y permitido escribir «se alcanzó la saturación», y
esa es exactamente la tentación que el ejemplo tiene que mostrar rechazada. La
decisión está registrada en `decisiones/05_analizar.json`, con la opción
descartada a la vista.

## Cómo volver a hacerlo

Desde esta carpeta:

```
uv run python codigo/00_referencias.py          # bib desde Crossref
uv run python codigo/01_libro_de_codigos.py     # libro, matriz y saturación
uv run python codigo/02_decisiones_de_ejemplo.py
```

`01_libro_de_codigos.py` **falla si una cita del libro no aparece literalmente**
en la transcripción que declara. La codificación la hace la persona —las
categorías y los códigos están escritos en el script— y lo que automatiza es la
comprobación y el cálculo de la saturación.

## Verificarlo y renderizarlo

```
uv run python -m herramientas.preparar_ejemplo medicina-cualitativo
uv run python -m herramientas.verificar_todo --raiz .ejemplos-montados/medicina-cualitativo
QUARTO_PYTHON=.venv/bin/python quarto render .ejemplos-montados/medicina-cualitativo
```

En Windows, `$env:QUARTO_PYTHON = (Resolve-Path ".venv\Scripts\python.exe").Path`.

## Lo que este ejemplo demuestra

- **Cada cita de participante existe en su transcripción.** Se comprueba dos
  veces: en el análisis y después con `verificar_cifras.py`. Una cita
  «arreglada» para que lea mejor deja de coincidir y salta como error.
- **Libro de códigos auditable**: cada código con definición, criterio de
  inclusión y criterio de **exclusión**. El criterio de exclusión es lo que
  permite revisar por qué un fragmento se codificó así y no de otra forma.
- **Saturación documentada, no afirmada.**
- **El enfoque se declara.** El archivo `.enfoque` dice `cualitativo`, y por eso
  las herramientas comprueban el modelo cualitativo del reglamento de Medicina y
  no el cuantitativo.
- **Vancouver**, porque lo exige el perfil: citas numéricas y bibliografía
  ordenada por aparición, aplicadas por `plantillas/csl/vancouver.csl`.
- **Resultados y discusión en un solo capítulo**, que es lo que pide el modelo
  cualitativo del reglamento de la Facultad de Medicina.
- **Lo ético donde corresponde**: consentimiento obligatorio, comité de ética
  obligatorio (art. 23), anonimización antes de que nada salga de
  `datos/crudos/`.
