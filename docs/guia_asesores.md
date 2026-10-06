# Guía para asesores

Written for: asesores de tesis de la UNMSM que reciben un trabajo hecho con este
repositorio y quieren saber qué están revisando.

---

Su asesorado usó `tesis-sanmarcos`, un repositorio que acompaña la elaboración de
una tesis con Claude Code. Esta guía le dice **qué puede comprobar y en diez
minutos**, sin instalar nada y sin aprender a programar.

Lo primero, porque suele ser la pregunta: el repositorio no escribe la tesis por
nadie. Produce borradores a partir de decisiones que el tesista tomó y de datos
que existen en disco, y deja constancia de ambas cosas. Qué tan buena sea la
tesis sigue dependiendo de él y de usted.

## Lo que este repositorio no le ahorra

Nada de lo que sigue sustituye su criterio. Las herramientas comprueban cosas
mecánicas: que una cita exista, que una cifra venga de un archivo, que las
secciones sean las que su escuela pide. **Ninguna sabe si la pregunta de
investigación vale la pena, si el marco teórico es el adecuado o si las
conclusiones se sostienen.** Eso es exactamente lo que queda para usted.

Si un informe del repositorio dice «sin errores», significa que esas
comprobaciones no encontraron nada. No significa aprobado, y el propio informe lo
dice en esas palabras.

## Cuatro cosas que puede mirar sin instalar nada

Son archivos de texto. Se abren con cualquier editor, o en GitHub si el tesista
le compartió el repositorio.

### 1. `decisiones/` — qué decidió él y con qué palabras

Un archivo `.md` por etapa, legible. Cada uno trae:

- **las opciones que se le presentaron** y cuál se le recomendó;
- **cuál eligió**;
- **su respuesta textual**, con sus propias palabras, sin resumir;
- los cambios que pidió;
- **dos o tres preguntas de comprensión tipo jurado, con sus respuestas**.

Eso último es lo más útil para usted. Las respuestas a esas preguntas muestran si
entendió lo que decidió. Una respuesta pobre en la etapa 2 es una señal temprana,
y es mejor leerla ahora que oírla en la sustentación.

Los archivos están **sellados con un hash**. Si alguien edita una decisión
después de registrarla, la herramienta de verificación lo detecta. No es a prueba
de todo —quien quiera falsificar el registro puede hacerlo— pero sí detecta el
retoque casual.

### 2. `registro/registro_ia.jsonl` — qué hizo Claude

Una línea por acción: fecha, etapa, herramienta, archivo tocado. Permite ver
**qué partes del texto se redactaron con asistencia y cuándo**.

Si quiere el resumen en prosa en lugar del registro crudo, el repositorio genera
un anexo de declaración de uso de IA en `entregables/DOCUMENTO/`. Conviene que
sepa una cosa: **ninguna norma de la UNMSM que hayamos leído exige esa
declaración.** Es una medida voluntaria de transparencia, apoyada en el
principio del art. 5 del Código de Ética. Si usted cree que debe presentarse,
dígalo; si cree que no, tampoco pasa nada por omitirla.

### 3. `registro/verificacion_global.json` y los `.md` del mismo directorio

El resultado de las comprobaciones automáticas, con un puntaje por componente.
Los puntajes son un semáforo de este repositorio, **no una nota y no algo que
ponga la universidad**.

Un detalle que importa al leerlos: un componente que no tuvo nada que revisar
no saca 100, sale como pendiente. Una tesis vacía no tiene errores, y el
repositorio se niega a presentar eso como si estuviera bien.

### 4. `resultados/` — de dónde sale cada cifra

Toda cifra del texto tiene que existir en un archivo de `resultados/`, generado
por código de `codigo/`. Si ve un número en el documento, puede buscarlo ahí.

Si no está, no es un descuido de formato: la herramienta `verificar_cifras.py` lo
marca como error. En tesis cualitativas hace lo mismo con las citas de los
participantes, comprobando que cada una **aparezca literalmente** en una
transcripción.

## Si quiere correr las comprobaciones usted mismo

Hace falta [uv](https://docs.astral.sh/uv/) instalado. Después, en la carpeta del
proyecto:

```
uv run python -m herramientas.verificar_todo --con-red --detalle
```

`--con-red` consulta Crossref, OpenAlex y PubMed para comprobar que las
referencias existan de verdad. Tarda más y es la corrida que importa antes de
dar una conformidad.

Para ver el estado en una sola página, sin leer archivos:

```
uv run python -m herramientas.tablero --abrir
```

Abre un HTML autocontenido, sin conexión, con la etapa en curso, las decisiones
registradas y lo que está bloqueando la entrega.

## Las tres preguntas que de verdad distinguen

Si solo tiene diez minutos, estas tres hacen el trabajo.

**«Enséñame de dónde sale esta cifra.»** Debería poder llevarle al archivo de
`resultados/` y al script de `codigo/` que lo produjo. Si no puede, el número no
tiene respaldo.

**«¿Por qué elegiste esta especificación y no otra?»** La respuesta está, o
debería estar, en `decisiones/`. Y en `resultados/` deberían estar **todas** las
especificaciones que se probaron, incluidas las que no salieron. Una tabla de
robustez donde todo funciona es sospechosa.

**«¿Qué no demuestra tu tesis?»** Es la pregunta que separa a quien entendió su
trabajo de quien lo administró. La respuesta debería aparecer también en el
capítulo de discusión.

## Cuando usted pide un cambio

El tesista tiene un comando, `/asesor`, que recoge sus observaciones y las
clasifica: las de forma se aplican, las de fondo se le presentan a él como
decisión —porque cambian lo que va a defender— y queda registrado qué se hizo
con cada una.

Dos advertencias honestas sobre eso.

**El repositorio no le va a esperar.** Nada del flujo queda condicionado a que
usted confirme algo: el tesista avanza y sus observaciones se incorporan cuando
llegan. Fue una decisión deliberada, porque la alternativa era que una tesis se
detuviera semanas esperando una reunión.

**Hay cosas que no va a hacer aunque usted las pida.** Si pide parafrasear para
bajar el porcentaje de similitud, o convertir una tabla en imagen, el repositorio
se niega y le cita el artículo: la Directiva de originalidad
(RR N.° 000947-2026-R), art. 30 c) y d), tipifica las dos cosas como falta del
autor. Le ofrecerá lo que sí resuelve el problema —citar mejor, reescribir,
reducir texto de terceros—. No es una rigidez del programa: es que la falta la
comete el tesista, no la herramienta.

## Si su escuela pide algo distinto

El repositorio trae un perfil por facultad, en `perfiles/`. Cuatro facultades
tienen norma propia verificada; las demás heredan la estructura general de la
universidad, que son los Anexos 2A y 2B de la RR N.° 00744-R-20 y es norma de
verdad, no una plantilla inventada.

Si su escuela exige otra cosa —otro orden, otra denominación, otro estilo de
citas—, **usted es quien mejor lo sabe**. Dígalo y se ajusta el perfil; queda
registrado como una decisión del tesista. Lo que el repositorio no hará es marcar
ese perfil como `verificado` sin el documento que lo respalde, porque entonces
dejaría de poder distinguir lo que consta de lo que alguien recordó.

Si tiene a mano la resolución o la guía de su escuela, compartirla mejora el
perfil para todos los tesistas de esa facultad. Cómo se agrega está en
[`agregar_facultad.md`](agregar_facultad.md).

## Lo que conviene que sepa sobre los trámites

Dos cosas con fecha, que suelen tomar por sorpresa:

- **El certificado de similitud vence a los 90 días** (art. 19 de la Directiva de
  originalidad). Si se vence antes de la sustentación, hay que repetir el
  trámite.
- **Desde la segunda revisión, la evaluación en PIDS cuesta S/ 20.** Vale la pena
  que la primera salga bien.

Y una aclaración técnica: el umbral de similitud es de 0 % a 20 % y se mide en la
plataforma PIDS de la universidad. El repositorio tiene una herramienta que
detecta repeticiones internas y fragmentos sin citar, pero **no estima ese
porcentaje y no lo anticipa**. Si el tesista le dice que «ya pasó el filtro de
similitud», eso no existe: lo mide PIDS y nada de aquí lo sustituye.
