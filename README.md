# tesis-sanmarcos

Haz tu tesis de la UNMSM con Claude Code, desde la idea hasta la sustentación.

Está pensado para quienes **ya terminaron la carrera** y tienen la tesis
pendiente: egresados y bachilleres que quieren obtener el título profesional,
muchas veces años después y trabajando a la vez.

No necesitas saber programar. Claude hace el trabajo operativo: busca y descarga
datos, revisa literatura, analiza, redacta los capítulos, da formato y arma los
archivos de entrega. **Tú decides, firmas y sustentas.** Esas tres cosas no las
puede hacer nadie más por ti, y son justamente las que el jurado va a evaluar.

## Puedes empezar hoy

No hay requisitos para arrancar. No te vamos a preguntar si ya tienes el grado de
bachiller, si tu escuela te asignó asesor, en qué año ingresaste ni cuánto tiempo
libre tienes. Escribes `/iniciar` y empiezas.

Los trámites existen —el bachiller, el asesor, la revisión de similitud— y son
reales, pero son asunto tuyo con tu facultad, y este repositorio te los recuerda
**cuando hacen falta**, no antes: el checklist que genera `/entregar` los lista
todos. La tesis se puede empezar a escribir mucho antes de tener el expediente
ordenado, y es mejor así, porque lo difícil es escribirla.

Si llevas tiempo fuera de la universidad, una advertencia útil: el ritmo lo pones
tú. Puedes dejarlo semanas y volver; `/estado` te dice dónde quedaste y qué sigue.

---

## Qué hace y qué no hace

**Sí hace**

- Busca fuentes de datos abiertas peruanas y descarga las que elijas.
- Te propone preguntas de investigación viables con los datos que hay.
- Busca literatura, la sintetiza y detecta vacíos.
- Redacta el proyecto y los capítulos con la estructura exacta que exige tu escuela.
- Verifica que cada cifra del texto salga de un archivo de resultados, y que cada
  cita exista en tu biblioteca de Zotero.
- **Arma tus dos documentos terminados** —el proyecto de tesis y la tesis—
  **en Word y en PDF**, con la carátula oficial y el escudo de la UNMSM, y con
  los nombres de archivo que pide la directiva.
- Prepara diapositivas, guion y un simulacro de sustentación con preguntas.

**No hace**

- No inventa datos, resultados, testimonios ni referencias. Si falta algo, lo dice.
- No decide por ti. Cada etapa se detiene hasta que elijas.
- No hace nada para "bajar el porcentaje de similitud". Eso es falta sancionable
  según la directiva de originalidad, y este repositorio no lo implementa.
- No reemplaza a tu asesor.

---

## Qué tienes al final

Dos documentos, cada uno en los dos formatos que la universidad pide por normas
distintas:

| | Word | PDF |
|---|---|---|
| **Proyecto de tesis** | `entregables/PROYECTO/` | sí |
| **Tesis** | `entregables/TEXTO/`, los dos archivos del art. 13 | sí |

Los dos llevan la **carátula oficial**: el escudo de la UNMSM, tu facultad, tu
escuela, el título, la fórmula «Para optar el Título Profesional de…», tu
nombre, el de tu asesor y el año. El diseño se tomó de tesis reales publicadas
en Cybertesis, no de una plantilla inventada.

**Si abres el archivo de «Desarrollo» y no ves la carátula, está bien.** El
art. 13 parte la tesis en dos: el de Desarrollo lleva el cuerpo y nada más
—«sin carátula […] ni referencias bibliográficas»—, y el de «Protocolo y
Complemento» lleva la carátula, las listas, la bibliografía y los anexos. No es
un capricho: el primero es el que se somete al análisis de similitud, y la
carátula y la bibliografía coinciden con las de cualquier otra tesis, así que
dentro solo servirían para subirte el porcentaje.

El `.docx` es lo que se entrega para la evaluación de originalidad (art. 13 de
la Directiva de originalidad). El **PDF** es lo que exige la directiva de
depósito en Cybertesis (RR N.° 06893-R-18) y lo que vas a imprimir o adjuntar.
Es el mismo documento convertido, no otro: así el PDF que se deposita es
exactamente el `.docx` que se evaluó.

Además, en `entregables/DOCUMENTO/`: el checklist de tu expediente, la
declaración jurada del Anexo 4, la autorización de depósito en Cybertesis con su
licencia, la hoja de metadata complementaria, la declaración de originalidad que
pide el RENATI y —si decides presentarla— la declaración de uso de IA.

---

## Antes de empezar: lo que debes saber

Tu tesis es un **documento original e inédito** y tú la declaras bajo juramento
(Directiva de originalidad, RR N.° 000947-2026-R). Este repositorio deja
registrado todo lo que hizo Claude, en `registro/`, y todo lo que decidiste tú,
en `decisiones/`. Ese registro es para que tu asesor vea el proceso completo.

Hay una tensión normativa que conviene que converses con tu asesor antes de
empezar: el Código de Ética de la UNMSM (art. 10 b) prohíbe el apoyo de terceros
que exceda la asesoría de tesis, mientras que la directiva de 2026 admite la IA
generativa "como apoyo, siempre respetando la originalidad". Ninguna norma define
dónde termina el apoyo. Está explicado en `normativa/conflictos.md`, C-01.

---

## Instalación en Windows, paso a paso

Elige una carpeta corta y luego instala cinco cosas. Tarda unos 20 minutos.

### 0. Dónde poner la carpeta de tu tesis

Ponla en una ruta **corta**: `C:\tesis`, o `C:\Users\tu-usuario\tesis`.

No es manía. Los nombres de archivo que exige la directiva llevan tus apellidos,
tus nombres, el título completo de la tesis y el año, así que son largos.
Windows no admite rutas de más de 260 caracteres, y si además la carpeta está en
`Descargas\Mi carpeta de la universidad\Tesis 2026\…`, se cruza el límite.

Las herramientas lo comprueban **antes** de generar nada y te dicen cuántos
caracteres sobran, en lugar de dejarte un documento a medio hacer. Pero es más
cómodo empezar bien.

### 1. Git

Descarga **Git for Windows** de <https://git-scm.com/download/win> y ejecútalo.
Acepta todas las opciones por defecto.

### 2. Python, uv, Quarto y pandoc

Abre **PowerShell** (botón Inicio, escribe `powershell`, Enter) y pega esto:

```powershell
winget install --id Python.Python.3.12 -e --accept-source-agreements --accept-package-agreements
winget install --id astral-sh.uv -e --scope user --accept-package-agreements
winget install --id Posit.Quarto -e --accept-package-agreements
winget install --id JohnMacFarlane.Pandoc -e --accept-package-agreements
winget install --id TheDocumentFoundation.LibreOffice -e --accept-package-agreements
```

LibreOffice es gratuito y aquí se usa solo para una cosa: convertir a PDF los
documentos que ya se generaron en Word. Si no lo instalas, el `.docx` se genera
igual y el PDF queda pendiente con un aviso que te dice cómo obtenerlo.

**Cierra PowerShell y ábrelo de nuevo.** Los programas recién instalados no
aparecen hasta que abres una ventana nueva.

Comprueba que todo quedó bien:

```powershell
git --version
uv --version
quarto --version
pandoc --version
uv run python -m herramientas.pdf --comprobar
```

Si alguno responde "no se reconoce", vuelve a instalarlo.

> **Aviso sobre `python`.** En Windows, escribir `python` a secas suele abrir la
> Microsoft Store en lugar de ejecutar Python. No es un error tuyo. En este
> repositorio nunca escribas `python`: usa siempre `uv run`.

### 3. Zotero y Better BibTeX

Zotero es donde guardarás tus referencias. Sin él, Claude no puede citar nada.

1. Instala Zotero 7 desde <https://www.zotero.org/download/>.
2. Instala el complemento **Better BibTeX**: descarga el archivo `.xpi` de
   <https://retorque.re/zotero-better-bibtex/installation/> y en Zotero ve a
   *Herramientas → Complementos → ⚙ → Install Add-on From File*.
3. Instala también el **conector de Zotero** para tu navegador. Es el botón que
   guarda un artículo con un clic.

Más adelante, `/iniciar` te guiará para configurar la exportación automática a
`referencias.bib`. No lo hagas ahora.

### 4. Claude Code

Sigue las instrucciones de <https://claude.com/claude-code>.

### 5. Enciende el registro

Una vez, en la carpeta de tu tesis:

```powershell
uv run python -m herramientas.instalar_hooks
```

Esto hace dos cosas. Deja un **registro automático** de lo que Claude escribe,
edita y ejecuta, en `registro/registro_ia.jsonl` — de ahí sale la declaración de
uso de IA, y es lo que tu asesor puede mirar para ver el proceso. Y pone una
**protección en git** que impide subir sin querer tus datos crudos o los archivos
de entrega.

Para comprobar que quedó bien:

```powershell
uv run python -m herramientas.instalar_hooks --comprobar
```

> Ninguna de las dos cosas puede interrumpirte. El registro, si falla, pierde una
> línea y sigue. La protección de git, si no puede ejecutarse, deja pasar el
> commit con un aviso. Están pensadas para no estorbar nunca.

---

## Primer uso

1. Crea una carpeta para tu tesis y copia este repositorio dentro.
2. Abre PowerShell **en esa carpeta**: ábrela en el Explorador, haz clic derecho
   en un espacio vacío y elige *Abrir en Terminal*.
3. Escribe `claude` y espera a que arranque.
4. Escribe:

```
/iniciar
```

Claude conversa contigo sobre tu tesis: de qué facultad y escuela vienes, qué te
interesa investigar, si ya tienes datos y si la tesis es individual o grupal
(hasta tres autores). Con eso carga el perfil de tu escuela y empiezas.

Son preguntas para entender tu tesis, no para comprobar si puedes hacerla. Si no
sabes algo todavía —el asesor, el enfoque, el tema exacto— dilo y sigue: el flujo
está hecho para ir decidiendo sobre la marcha.

---

## Cómo elegir tu facultad y tu perfil

`/iniciar` lo hace por ti, pero conviene que entiendas qué está pasando.

La UNMSM tiene una estructura de tesis aprobada para toda la universidad: los
Anexos 2A y 2B de la RR N.° 00744-R-20. Cuatro facultades tienen además su propia
norma, más específica:

| Tu facultad | Qué usa |
|---|---|
| Medicina | Su propio reglamento: Vancouver, comité de ética, cronograma y presupuesto obligatorios |
| Letras y Ciencias Humanas | Su propio instructivo: APA 7, márgenes y formato propios |
| Derecho y Ciencia Política | Su reglamento, que remite a la estructura general |
| Ciencias Administrativas | Su directiva propia: cinco capítulos, con la discusión dentro del de resultados |
| Las otras 16 | La estructura general de la universidad |

Si tu escuela no tiene norma propia, **no estás en desventaja**: la estructura
general es norma, no una plantilla inventada.

Nada de esto te detiene. Si el perfil de tu facultad está marcado como no
verificado, el repositorio te lo dice y sigue trabajando; conviene que tu asesor
confirme que es lo que tu escuela espera, pero **no es un requisito para
avanzar** y ninguna etapa queda esperándolo.

---

## El flujo, etapa por etapa

| Comando | Para qué sirve |
|---|---|
| `/iniciar` | Te entrevista y prepara todo |
| `/explorar-datos` | Encuentra y descarga los datos |
| `/afinar-idea` | Convierte tu interés en una pregunta investigable |
| `/literatura` | Busca y ordena lo que ya se ha escrito |
| `/proyecto` | Redacta el proyecto y lo genera en Word y PDF, con carátula |
| `/analizar` | Hace el análisis y prueba su robustez |
| `/redactar <capítulo>` | Escribe cada capítulo |
| `/jurado` | Simula al jurado para encontrar problemas antes que ellos |
| `/verificar` | Revisa citas, cifras, estructura y formato |
| `/entregar` | Genera la tesis en Word y PDF, con carátula, y las declaraciones |
| `/sustentacion` | Diapositivas, guion y ensayo con preguntas |

Además, cuatro comandos que no son etapas:

- **`/estado`** te dice dónde quedaste, qué decidiste y qué toca ahora. Está
  pensado para volver después de semanas sin tocar la tesis, que es lo normal.
- **`/asesor`** prepara el material de la reunión y después convierte sus
  observaciones en cambios. No es una puerta: puedes trabajar sin haber hablado
  con él.
- **`/checkpoint`** guarda el avance y deja escrito lo primero que hay que hacer
  al volver.
- **`/autopiloto`** encadena varias etapas seguidas. Claude hace cada una
  completa y se detiene **solo** en los puntos de decisión, con una opción ya
  recomendada. Nunca registra una decisión que no tomaste: la herramienta que
  escribe las decisiones se niega a hacerlo sin tu respuesta.

Para ver todo de una vez, sin pasar por una etapa:

```
uv run python -m herramientas.verificar_todo --detalle
```

Da un puntaje por componente. **Es un semáforo, no una nota**: un componente que
no tenía nada que revisar no saca 100, sale como pendiente, porque una tesis
vacía no tiene errores y eso no la acerca a estar lista.

---

## Preguntas frecuentes

**¿Puedo usar esto si mi tesis es cualitativa?**
Sí. La estructura general tiene un modelo cualitativo, y Medicina y Letras
también. Las citas de entrevistas se verifican contra las transcripciones.

**¿Y si mi tesis es grupal?**
Hasta tres autores, y cada uno debe tener objetivos definidos. El sistema te lo
pide y lo refleja en los entregables.

**¿Puedo editar lo que Claude escribió?**
Sí, y debes hacerlo. Tus ediciones se respetan cuando se regenera un capítulo.

**¿Esto me garantiza pasar Turnitin?**
No, y desconfía de cualquier cosa que lo prometa. El repositorio tiene una
herramienta que detecta repeticiones internas y fragmentos copiados de tus PDF
sin citar, pero **no mide** el porcentaje oficial. Ese lo calcula la plataforma
PIDS de la universidad, y lo carga tu asesor.

**¿Tengo que declarar que usé IA?**
Ninguna norma de la UNMSM que hayamos podido leer lo exige hoy. El repositorio
genera igualmente un anexo con el detalle de lo que hizo Claude, por
transparencia. Tú decides si lo presentas; conversa con tu asesor.

**¿Y mis datos personales de encuestas o entrevistas?**
Se quedan en tu computadora. `datos/crudos/` está excluido del control de
versiones y hay un bloqueo que impide subirlos por accidente.

---

## Límites y responsabilidad

Claude se equivoca. Por eso el repositorio verifica cada cifra contra los
archivos de resultados y cada cita contra tu biblioteca, y por eso marca
`[VERIFICAR]` lo que no puede comprobar. Nada de eso te libera de leer lo que vas
a firmar.

**La tesis es tuya.** La autoría, la declaración jurada y la sustentación son
tuyas. Este repositorio es una herramienta de trabajo, igual que un procesador de
texto o un gestor de referencias, y te deja un registro auditable para que puedas
explicar cómo llegaste a cada decisión.

---

## Dos ejemplos completos

En `ejemplos/` hay dos tesis de demostración que recorren el flujo entero. Si
quiere ver cómo queda esto antes de empezar con lo suyo, mírelas.

**[`economia-cuantitativo`](ejemplos/economia-cuantitativo/)** — perfil
`economia-fce`, APA 7. Datos **reales** de la API del Banco Mundial: 17 países,
14 años. Pregunta si la penetración de internet se asocia con la productividad
laboral en América Latina.

Lo interesante es cómo termina: la correlación simple es fuerte y positiva, y
con efectos fijos de país y de año **desaparece**. El ejemplo reporta las siete
especificaciones que se probaron, incluidas las dos que salieron significativas
y las cinco que no, y explica por qué un resultado nulo no demuestra que no haya
efecto. Se eligió a propósito el caso difícil.

**[`medicina-cualitativo`](ejemplos/medicina-cualitativo/)** — perfil
`medicina-fm`, Vancouver. Ocho entrevistas **ficticias** sobre barreras para la
adherencia al tratamiento antihipertensivo, libro de códigos con criterios de
inclusión y exclusión, y cada cita de participante comprobada contra su
transcripción.

Aquí lo incómodo es la saturación: la última entrevista todavía aportó códigos
nuevos, así que **no se alcanzó**, y el ejemplo lo declara en el resumen, en el
método, en los resultados y en las conclusiones en lugar de afirmarla.

Las transcripciones de ese ejemplo son ficticias y están marcadas en el nombre
del archivo, dentro de cada archivo y en un LEEME de la carpeta. No hay
participantes.

Para verlos funcionando:

```
uv run python -m herramientas.preparar_ejemplo --todos
uv run python -m herramientas.verificar_todo --raiz .ejemplos-montados/economia-cuantitativo
```

---

## Más documentación

Índice completo en **[`docs/`](docs/README.md)**. Lo más usado:

- **[`docs/integridad.md`](docs/integridad.md)** — qué se puede y qué no, con el
  artículo de la norma que lo dice. Si tiene dudas sobre el porcentaje de
  similitud o sobre la declaración de uso de IA, empiece aquí.
- **[`docs/guia_asesores.md`](docs/guia_asesores.md)** — para su asesor: cómo
  revisar el registro de uso de IA, el historial de decisiones y los informes de
  verificación, en diez minutos y sin instalar nada.
- **[`docs/agregar_facultad.md`](docs/agregar_facultad.md)** — si su escuela pide
  algo distinto de lo que dice su perfil, o si consiguió el documento normativo
  que faltaba.
- **[`normativa/requisitos.md`](normativa/requisitos.md)** — los requisitos con
  documento, artículo y página. Lo que no está ahí, no lo sabemos.

## Licencia

MIT. Ver `LICENSE` y `NOTICE.md`.
