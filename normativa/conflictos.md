# Conflictos y tensiones normativas

Registro de contradicciones entre normas, y de tensiones entre la normativa y el diseño de `tesis-sanmarcos`.
Regla general del encargo: cuando una norma de facultad contradice una norma general, **prevalece la general**.

Fecha: 2026-09-16.

---

## C-01 · Apoyo de terceros que excede la asesoría (tensión con el diseño del repositorio)

**Estado:** abierto. Requiere una decisión explícita del estudiante y, idealmente, del asesor.

**Normas en juego**

- *Código de Ética en Investigación de la UNMSM* (RR N.° 012648-2023-R), **art. 10, inciso b**, pág. 6 PDF:
  > "Los investigadores están prohibidos de: […] b) Ofrecer apoyo, orientación u otra forma de participación que exceda las labores de asesoría de tesis que brindan los docentes, por sí o a través de terceros, a favor del tesista."
- *Directiva de originalidad* (RR N.° 000947-2026-R), **art. 5 q**, pág. 7 PDF: la IAG "se usa como apoyo, siempre respetando la originalidad".
- *Directiva de originalidad*, **art. 5 k**, pág. 6 PDF: la tesis es un "documento original e inédito".

**En qué consiste la tensión**

El art. 10 b) está redactado como prohibición dirigida a los investigadores y docentes: prohíbe *ofrecer* apoyo que exceda la asesoría, "por sí o a través de terceros". No es una prohibición dirigida al estudiante ni menciona herramientas de software. La directiva de originalidad, que es posterior (2026) y sí contempla expresamente la IAG, la admite como apoyo.

Aun así, el modelo de trabajo de `tesis-sanmarcos` —Claude ejecuta el 100 % del trabajo operativo, incluida la redacción de todos los capítulos— se apoya en una lectura amplia de "apoyo" que ninguna norma leída confirma ni desmiente para el caso de la IA generativa. Ninguna de las normas leídas define dónde termina el apoyo admisible y dónde empieza la sustitución del autor.

**Lo que el repositorio hace y no hace**

- **No** resuelve la tensión por su cuenta ni la oculta.
- Mantiene el registro completo de decisiones (`decisiones/`) y de acciones de IA (`registro/registro_ia.jsonl`) precisamente para que el estudiante y el asesor puedan ver el alcance real de la participación de Claude y juzgarlo.
- Genera el anexo de declaración de uso de IA como medida voluntaria de transparencia, apoyada en el principio de transparencia del art. 5 del Código de Ética, no porque una norma lo exija (ver `requisitos.md`, P-01).
- `/iniciar` debe mostrar esta tensión al estudiante **antes** de que empiece, y recomendarle conversarla con su asesor.

**Qué haría cambiar esta evaluación:** una norma de la UNMSM que regule expresamente el uso de IA generativa por estudiantes en trabajos conducentes a grado o título. Esa norma se busca en P-02 y aún no existe o no se ha encontrado.

---

## C-02 · Denominación del documento de la Escuela de Economía

**Estado:** resuelto por normalización, registrado.

El archivo `PAUTAS PARA SUSTENTACION DE TESIS.docx` regula, por su contenido, la **estructura del diseño o proyecto de investigación**, no la sustentación. Su propio encabezado dice "ESTRUCTURA DEL DISEÑO Y/O PROYECTO DE INVESTIGACION PARA OPTAR EL TITULO PROFESIONAL DE ECONOMISTA" y se presenta como "una GUIA BREVE".

**Resolución:** el perfil `economia-fce` lo trata como norma del **proyecto**, no de la sustentación. Se anota en `perfiles/_notas_normalizacion.md`.

---

## C-03 · El documento de Economía no acredita rango normativo

**Estado:** abierto.

El documento no contiene número de resolución, fecha, firma ni código de verificación, y él mismo se declara "GUIA BREVE […] en concordancia con el Reglamento General de Grados y Títulos". Por su parte, la directiva general RR 00744-R-20 §6.3 exige que la **facultad apruebe** la normativa específica y establezca la estructura del cuerpo de los documentos, "previa conformidad del Vicerrectorado Académico de Pregrado".

**Consecuencia:** el perfil `economia-fce` no puede llevar `estado: verificado`. Se le asigna `estado: documento_en_mano` y `verificar_perfil.py` impedirá elevarlo a `verificado` mientras no exista en `normativa/facultades/economia/` la resolución que lo aprueba.

---

## C-04 · Numeración interna del documento de posgrado de Letras

**Estado:** pendiente de verificación.

El encargo advierte que el dictamen de la UPG de Letras tiene errores de numeración (por ejemplo, "5.1 Resultados" dentro del capítulo 4) y pide normalizarlos al traducirlo a perfil. Ese documento **no** ha sido leído todavía en esta fase; en su lugar se descargaron dos documentos de **pregrado** de la FLCH (RR 009747-2022-R y la directiva de sustentación de tesis de pregrado), que son jerárquicamente más pertinentes para este repositorio.

**Pendiente:** al construir el perfil de Letras, usar los de pregrado y no el dictamen de posgrado. Registrar aquí cualquier discrepancia que aparezca.

---

## C-05 · Sin conflictos detectados entre normas generales

Hasta donde alcanza la lectura de la Fase 0, no hay contradicción entre la directiva de originalidad (2026), la directiva general de tesis (2020), el Reglamento General de Grados y Títulos (2017) y el Código de Ética (2023). La directiva de originalidad de 2026 deja sin efecto cualquier norma que se le oponga (Disposición Complementaria Final Segunda, pág. 18 PDF), lo que resuelve de antemano los conflictos con directivas de similitud anteriores.
