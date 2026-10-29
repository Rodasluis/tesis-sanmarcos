# Guion del video de uso de `tesis-sanmarcos`

Guion de rodaje para el video introductorio: **9 minutos**, siete bloques,
pantalla y voz. No hace falta cámara.

Está escrito para grabarse con los **ejemplos** del repositorio, no con una
tesis real. Esa no es una comodidad: es la regla principal del rodaje.

---

## Antes de grabar

### La regla que no se negocia

**Nunca grabes una tesis real.** En cuanto enciendes la captura, lo que se ve
en `datos/crudos/` queda publicado para siempre, y ahí viven transcripciones de
personas. Lo mismo con `entregables/datos_de_entrega.yaml`, que lleva DNI,
correo y domicilio.

Todo lo que este video necesita mostrar está en `ejemplos/`: ocho
transcripciones ficticias, un tesista ficticio y datos públicos del Banco
Mundial. Graba contra eso.

Antes de iniciar la captura, cierra el explorador de archivos y las pestañas
del navegador que no sean parte del video. El repositorio ya tuvo una vez un
correo personal dentro; no lo repitamos en 1080p.

### Lo que hay que tener listo

- Un clon limpio en **`C:\demo`**. Ruta corta a propósito: los nombres de
  archivo que exige el art. 13 son largos, y en Windows el límite de 260
  caracteres aparece antes de lo que uno cree.
- `uv sync --extra analisis` ya corrido, para no grabar la descarga.

  > El README no lo menciona en su sección de instalación: pasa de instalar los
  > programas a `/iniciar`, y `uv run` sincroniza solo lo básico. El extra
  > `analisis` trae el motor Jupyter y `tabulate`, que es lo que hace falta
  > para que Quarto ejecute el código de los capítulos e inserte las cifras.
  > Si grabas el video sin él, el render del bloque 5 falla a cámara.
- Quarto y LibreOffice instalados. Sin LibreOffice no hay PDF, y el PDF es
  medio video.
- Terminal a **18 pt o más**. Nadie va a pausar para leer tu fuente de 11.
- Grabación a 1080p. El contenido es texto: si se comprime, no se lee.

### Qué cortar en edición

Las esperas de `uv sync`, del render de Quarto y de la conversión a PDF. Deja
el primer segundo y el último de cada una para que se entienda que tardan, y
corta el resto. No aceleres la salida de la terminal hasta volverla ilegible.

---

## Bloque 1 — Qué es esto y para quién (0:00 – 0:50)

**En pantalla:** el README en GitHub, quieto en el título.

**Narración:**

> Esto es un repositorio para escribir una tesis de pregrado en San Marcos con
> Claude Code. No es un generador de tesis. Es un acompañante que ejecuta el
> trabajo operativo mientras tú decides, firmas y sustentas.
>
> Está hecho para quien ya terminó la carrera y hace la tesis para titularse.
> Si llevas años fuera de la facultad y avanzas de a ratos, ese es el caso
> para el que se diseñó.
>
> Dos cosas que conviene oír al principio. La primera: no hace falta ningún
> trámite para empezar. No te va a preguntar si ya eres bachiller ni si tienes
> asesor designado. La segunda: no sirve para escribir una tesis sin trabajar.
> Vas a tener que decidir, leer y responder preguntas, y eso es el punto.

**Nota:** no prometas rapidez. Todo el resto del video pierde credibilidad si
este bloque promete un atajo.

---

## Bloque 2 — Instalación (0:50 – 2:20)

**En pantalla:** PowerShell en `C:\`, teclear en vivo:

```
git clone https://github.com/Rodasluis/tesis-sanmarcos.git demo
cd demo
uv sync --extra analisis
uv run python -m herramientas.instalar_hooks
```

**Narración:**

> Clonas, entras y sincronizas. `uv` se encarga de Python y de las
> dependencias; no hace falta instalar nada a mano.
>
> La última línea instala un registro: a partir de ahí, cada archivo que Claude
> escriba y cada comando que corra queda anotado. Sirve para que después puedas
> mostrarle a tu asesor qué hizo la máquina y qué hiciste tú.

**Dos cosas que decir a cámara, cortas y claras:**

> Ponlo en una ruta corta. `C:\tesis` sirve; el escritorio dentro de una
> carpeta con tu nombre completo y el año, no.
>
> Y si vas a usarlo para tu tesis de verdad, lo primero después de clonar es
> `git remote remove origin`. Esa carpeta va a tener tus datos crudos, y
> mientras apunte al repositorio público está a un comando de publicarlos.

**En pantalla:** `uv run python -m herramientas.instalar_hooks --comprobar`,
mostrando las cinco filas en verde.

---

## Bloque 3 — El perfil de tu escuela (2:20 – 3:30)

**En pantalla:** la tabla de facultades del README; luego
`normativa/requisitos.md`, bajando despacio por una entrada cualquiera.

**Narración:**

> La universidad tiene una estructura de tesis aprobada para todas las
> facultades: los anexos de la resolución 00744 del 2020. Cuatro facultades
> tienen además norma propia, más específica: Medicina, Letras, Derecho y
> Ciencias Administrativas. Las otras dieciséis usan la general.
>
> Eso está escrito en archivos de perfil, uno por escuela, con el documento,
> el artículo y la página de donde sale cada regla. Si una regla no consta con
> su fuente, el repositorio dice que no la sabe en lugar de inventarla.
>
> Que tu facultad use la norma general no es un vacío. Es norma de verdad, y es
> la que rige si tu escuela no publicó otra.

**Nota:** no cites de memoria plazos ni porcentajes a cámara. Si necesitas uno,
muéstralo en `normativa/requisitos.md` en pantalla. Lo único que conviene decir
del umbral de similitud es que lo mide la universidad en su plataforma y que
está entre 0 y 20 %.

---

## Bloque 4 — `/iniciar` y el punto de decisión (3:30 – 5:10)

**En pantalla:** `claude` arrancando en `C:\demo`, y después `/iniciar`.

**Narración:**

> Abres Claude Code en la carpeta y escribes `/iniciar`. Te va a preguntar de
> qué facultad vienes, qué te interesa investigar y si ya tienes datos. Son
> preguntas para entender tu tesis, no para comprobar si puedes hacerla.
>
> Al final de cada etapa viene lo que el repositorio llama un punto de
> decisión. Claude te pone opciones con sus ventajas y sus riesgos, marca una
> como recomendada y te dice por qué. Eliges tú.

**En pantalla:** abrir `ejemplos/medicina-cualitativo/decisiones/02_afinar-idea.md`
y detenerse en el bloque «En sus palabras».

**Narración:**

> Y esto es lo que se guarda: tu respuesta, textual. No un resumen que Claude
> haya hecho de lo que dijiste. Con fecha, con la etapa, con las opciones que
> se te presentaron y con las que descartaste.
>
> Después vienen dos o tres preguntas de comprensión, del tipo que te hace un
> jurado. No bloquean nada. Quedan guardadas y reaparecen cuando prepares la
> sustentación, que es cuando te van a servir.

**Nota:** las decisiones de los ejemplos están marcadas `FICTICIO` en el autor
y en cada respuesta. Dilo al pasar: nadie las tomó.

---

## Bloque 5 — Lo que sale al final (5:10 – 6:40)

**En pantalla:** `uv run python -m herramientas.entregar --raiz .ejemplos-montados/economia-cuantitativo --detalle`
y después el contenido de `entregables/TEXTO/`.

**Narración:**

> La entrega son dos archivos de Word con nombres exactos, más sus PDF. No es
> un capricho del repositorio: lo manda el artículo 13 de la directiva de
> originalidad.

**En pantalla:** abrir el archivo de **Protocolo y Complemento** en Word,
primera página.

**Narración:**

> Este lleva la carátula, con el escudo de la universidad, y al final la
> bibliografía.

**En pantalla:** abrir el de **Desarrollo**, primera página, y bajar al final.

**Narración:**

> Y este no lleva ninguna de las dos cosas, y eso es a propósito. El de
> Desarrollo es el que se somete al análisis de similitud. La carátula y la
> bibliografía son texto que no escribiste tú y que coincide con el de
> cualquier otra tesis de la universidad: dentro de este archivo solo servirían
> para subirte el porcentaje. La norma los saca de aquí y los pone en el otro.

**Narración, cerrando el bloque:**

> El PDF no se maqueta aparte: se obtiene convirtiendo este mismo Word. Son dos
> trámites sobre el mismo documento, así que tienen que ser el mismo documento.

---

## Bloque 6 — Lo que este repositorio no hace (6:40 – 8:10)

Este es el bloque que distingue al video de los mil tutoriales de «escribe tu
tesis con IA». Grábalo despacio.

**En pantalla:** `ejemplos/medicina-cualitativo/capitulos/03-metodo.qmd`, en la
tabla de saturación, y después el resumen donde dice que no se alcanzó.

**Narración:**

> Mira este ejemplo. Son ocho entrevistas, y la octava todavía aportó códigos
> nuevos: la saturación no se alcanzó. El ejemplo lo declara así, en el
> resumen, en las limitaciones, en el método y en las conclusiones.
>
> Se podía haber maquillado. Agrupando los dieciséis códigos en tres categorías
> amplias, la curva quedaba plana y se podía escribir «se alcanzó la
> saturación». El repositorio está hecho para no hacer eso. Si un dato falta,
> dice que falta.

**Narración, sin apoyo en pantalla o con el README en la sección de límites:**

> Tres cosas más, para que nadie se lleve una sorpresa en la sustentación.
>
> Hay un comando que simula al jurado. No es una nota ni un pronóstico de nota:
> es el mismo sistema que escribió el borrador haciéndole preguntas, así que
> comparte sus puntos ciegos. Lo que no se le ocurrió al redactar, no se le
> ocurre al criticar.
>
> Hay una herramienta que mide repeticiones internas. No es Turnitin ni es la
> plataforma de la universidad, y no hay que presentarla como si lo fuera.
> Quien corre esa comprobación es tu escuela.
>
> Y el repositorio genera un anexo que declara qué parte del trabajo hizo la
> IA. Eso es voluntario: ninguna norma de San Marcos que hayamos leído lo
> exige. Está ahí porque es honesto, no porque sea un requisito.

---

## Bloque 7 — Cierre (8:10 – 9:00)

**En pantalla:** la tabla de etapas del README, de `/iniciar` a
`/sustentacion`.

**Narración:**

> Son once etapas, de la idea a la sustentación. Cada una cierra completa, con
> su decisión guardada, porque entre una sesión y la siguiente pueden pasar
> semanas y hay que poder volver.
>
> Lo que la máquina no hace es lo importante: no decide por ti, no firma y no
> sustenta. El texto lo vas a defender tú con tu nombre, y cada cosa que no
> entiendas es una pregunta que no vas a saber responder.
>
> El repositorio es libre, con licencia MIT, y el enlace está en la
> descripción. Si tu escuela te pide algo distinto de lo que trae, se ajusta y
> queda registrado como tu decisión.

---

## Capítulos para la descripción de YouTube

```
0:00  Qué es y para quién
0:50  Instalación
2:20  El perfil de tu escuela
3:30  /iniciar y el punto de decisión
5:10  Los dos .docx que exige la norma
6:40  Lo que no hace: jurado, similitud y datos
8:10  Cierre
```

## Título y descripción sugeridos

**Título:** `Tesis de pregrado UNMSM con Claude Code: cómo funciona el
repositorio tesis-sanmarcos`

**Descripción, primer párrafo:**

> Repositorio libre para elaborar una tesis de pregrado de la UNMSM con Claude
> Code, de la idea a la sustentación: estructura según la norma de tu facultad,
> decisiones registradas con tus propias palabras, y la entrega en los dos
> .docx que exige el art. 13 de la directiva de originalidad, con sus PDF. No
> escribe la tesis por ti y no evade los controles de originalidad.

---

## Si el video se regraba

Lo que suele quedar desactualizado, en orden: los nombres de los comandos, la
tabla de facultades con norma propia, y cualquier cifra normativa. Antes de
regrabar, contrasta los tres contra `normativa/requisitos.md` y la tabla de
etapas del README, que son las fuentes, y no contra la versión anterior del
video.
