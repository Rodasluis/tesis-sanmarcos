# Ejemplo: tesis cuantitativa con perfil `economia-fce`

Una tesis de demostración que recorre el flujo completo, desde la descarga de los
datos hasta los capítulos renderizados.

**Pregunta:** ¿existe asociación entre la penetración de internet y la
productividad laboral en América Latina, 2010–2023, una vez controlados los
factores propios de cada país y los choques comunes a la región?

## Qué es real y qué es ficticio

Esto es lo primero que hay que saber de este ejemplo.

| | |
|---|---|
| **Los datos son reales** | API del Banco Mundial, 17 países, 14 años, 238 observaciones país-año. Se bajan con `codigo/01_descarga.py`. |
| **Las referencias son reales** | Cinco artículos comprobados en Crossref por su DOI. Ninguna se escribió de memoria. |
| **Los resultados son reales** | Salen de correr el código. No se retocó ninguno. |
| **El tesista es ficticio** | Las decisiones de `decisiones/` están marcadas `FICTICIO` y firmadas por «Tesista de ejemplo». Nadie las tomó. |

## El resultado, que no es el que la hipótesis esperaba

La correlación simple entre internet y productividad es fuerte y positiva. Con
efectos fijos de país y de año **desaparece**: el coeficiente cambia de signo y
deja de ser distinto de cero, y se mantiene así en las cuatro especificaciones
alternativas.

Se eligió a propósito un ejemplo que **contradice su propia hipótesis**. Es el
caso difícil: el que tienta a cambiar la pregunta para que encaje con el
resultado, o a reportar solo la especificación que salió significativa. Este
ejemplo muestra qué hacer en su lugar —reportar las siete, explicar de dónde
viene la caída, y decir que un resultado nulo no demuestra que no haya efecto—
porque es ahí donde el repositorio sirve de algo.

## Cómo volver a hacerlo todo

Desde esta carpeta, en orden:

```
uv run python codigo/00_referencias.py          # bib desde Crossref
uv run python codigo/01_descarga.py             # datos del Banco Mundial
uv run python codigo/02_limpieza.py             # panel país-año
uv run python codigo/03_descriptivos.py         # descriptivos y cobertura
uv run python codigo/04_estimacion.py           # siete especificaciones
uv run python codigo/05_figuras.py              # tres figuras
uv run python codigo/06_decisiones_de_ejemplo.py
```

Borra `resultados/` antes y comprueba que vuelve a salir lo mismo. Eso es lo que
un jurado puede pedir y lo que `critico-codigo` comprueba.

Las cifras del Banco Mundial se revisan hacia atrás sin avisar, así que una
descarga nueva puede no coincidir con la de `datos/crudos/_procedencia.md`. La
fecha de descarga es parte del dato.

## Verificarlo y renderizarlo

El ejemplo guarda solo lo suyo: no lleva copia de `perfiles/` ni de
`plantillas/`, para que no se queden viejas. Se monta como proyecto completo
desde la raíz del repositorio:

```
uv run python -m herramientas.preparar_ejemplo economia-cuantitativo
uv run python -m herramientas.verificar_todo --raiz .ejemplos-montados/economia-cuantitativo
```

Para renderizar hacen falta Quarto y el extra de análisis, y Quarto tiene que
usar el Python del proyecto:

```
uv sync --extra analisis
QUARTO_PYTHON=.venv/bin/python quarto render .ejemplos-montados/economia-cuantitativo
```

En Windows, `$env:QUARTO_PYTHON = (Resolve-Path ".venv\Scripts\python.exe").Path`.
Sin eso Quarto usa el Python del sistema, que no tiene las dependencias.

## Lo que este ejemplo demuestra

- **Ninguna cifra escrita a mano.** Todas se insertan desde `resultados/` con
  expresiones de Quarto, así que el texto no puede desincronizarse del análisis.
- **Procedencia anotada**: fecha, URL e indicadores exactos en
  `datos/crudos/_procedencia.md`.
- **Flujo de muestra explícito**, con los faltantes por variable, en vez de «se
  eliminaron los casos incompletos».
- **Las siete especificaciones reportadas**, incluidas las que debilitan la
  hipótesis, cada una con su razón escrita en el código.
- **Un resultado nulo dicho sin maquillaje**, y la distinción entre «no
  encontramos efecto» y «demostramos que no hay efecto».
- **El perfil no verificado no bloquea nada.** `economia-fce` está en estado
  `verificar`; el ejemplo lo dice, usa la estructura del Anexo 2B y sigue.
