# Requisitos normativos extraídos

Fase 0 de `tesis-sanmarcos`. Cada requisito se extrae de un documento leído, con su artículo y su página.
Lo que no consta en un documento leído se marca `[PENDIENTE-NORMATIVA]` y se lista en la sección 8.

Fecha de extracción: 2026-09-16.

## 0. Cómo leer este documento

- **Página**: se indica `pág. N PDF` (número de página del archivo) y, cuando difieren, `pág. M impresa` (la numeración impresa dentro del documento). Se citan ambas porque los PDF de la UNMSM suelen llevar carátula de resolución antes del anexo.
- **Cita literal**: texto copiado del documento, entre comillas. Cuando el PDF trae erratas o espaciado irregular del OCR original, se transcribe tal cual.
- **ID**: `R-NN`. Las herramientas de `herramientas/` referencian estos IDs.
- **Motor**: qué parte de `tesis-sanmarcos` implementa o verifica el requisito.

## 1. Inventario de documentos leídos

| # | Documento | Norma | Fecha | Archivo local | Capa de texto | Estado |
|---|---|---|---|---|---|---|
| 1 | Directiva de originalidad y similitud de trabajos académicos, de investigación y producción intelectual | RR N.° 000947-2026-R | 29/01/2026 | `RR_000947-2026-R_directiva_originalidad.pdf` | Sí | Verificado |
| 2 | Reglamento General de Grados y Títulos de la UNMSM | RR N.° 01827-R-17 | 11/04/2017 | `Reglamento_General_de_Grados_y_Titulos_UNMSM.pdf` | Sí | Verificado |
| 3 | Directiva general para realizar, presentar y sustentar el TI, la tesis o el TSP — **resolución** | RR N.° 00744-R-20 | 18/02/2020 | `RR_00744-2020-R_directiva_general_tesis.pdf` | Sí | Verificado |
| 3b | La misma directiva — **anexo, 16 folios** (es el texto normativo) | Anexo de RR N.° 00744-R-20 | 18/02/2020 | `RR_00744-2020-R_ANEXO_directiva_general_tesis.pdf` | **No (escaneo)** | Verificado por lectura de imagen |
| 4 | Código de Ética en Investigación de la UNMSM | RR N.° 012648-2023-R | 2023 | `RR_012648-2023-R_codigo_etica_investigacion.pdf` | Sí | Verificado |
| 5 | Código Nacional de Integridad Científica (CONCYTEC) | RP 028-2024 y 035-2024-CONCYTEC-P | 2024 | `CONCYTEC_codigo_integridad_cientifica_portal.pdf` (17 pág.) y `..._gobpe.pdf` (10 pág.) | Sí | **Verificar cuál versión rige** |
| 6 | Guía para el uso de la IA generativa para docentes de la UNMSM | RR N.° 008449-2025-R | 07/07/2025 | `RR_008449-2025-R_guia_IA_generativa_docentes.pdf` | Sí | Verificado |
| 7 | Ley N.° 29733, de Protección de Datos Personales | Ley 29733 | 2011 | `Ley_29733_proteccion_datos_personales.pdf` (El Peruano, **escaneo**) y `Ley_29733_texto_vigente_2025_SMV.pdf` (texto) | Mixto | Verificado |
| 7b | Reglamento de la Ley 29733 | DS N.° 016-2024-JUS | 30/11/2024 | `DS_016-2024-JUS_reglamento_ley_29733.pdf` | Sí | Verificado |
| 8 | Reglamento del RENATI (texto integrado) | RCD 033-2016-SUNEDU/CD, mod. RCD 174-2019-SUNEDU/CD | — | `RENATI_reglamento_texto_integrado_COPIA-TERCEROS.pdf` | Sí | **Copia alojada por un tercero** (ver §8) |
| 9 | Directiva para el depósito de documentos de grados y títulos en Cybertesis | RR N.° 06893-R-18 | 2018 | `RR_06893-R-18_directiva_deposito_cybertesis.pdf` | **No (escaneo)** | Descargado, **sin leer aún** |
| 10 | Protocolo para el depósito en Cybertesis | — | — | `Protocolo_deposito_cybertesis_UNMSM.pdf` | Sí | Verificado |

Documentos adicionales descargados que no estaban en la lista de la sección 2 del encargo pero resultaron pertinentes:
`RR_008534-2025-R_reglamento_comite_etica.pdf` (Reglamento del Comité de Ética en Investigación) y
`RR_014384-2025-R_directiva_RAIS.pdf` (registro de publicaciones y tesis en el RAIS, exigido por la directiva 00744 §7.1).

## 2. Directiva de originalidad y similitud — RR N.° 000947-2026-R

### R-01 · La tesis es un documento original e inédito
**Art. 5, inciso k** (Definiciones), pág. 6 PDF / pág. 5 impresa.
> "Tesis. Documento original e inédito, expuesto con sustentación pública ante la comunidad académica en general; que pasa por la aprobación de un jurado que evalúa el trabajo de investigación en torno a un área académica determinada, implica el desarrollo del proyecto y su implementación."

**Motor:** premisa de todo el repositorio. `CLAUDE.md`, principios 1 a 3.

### R-02 · La IA generativa se admite como apoyo; usarla para evadir la detección es falta
**Art. 5, inciso q** (Definiciones), pág. 7 PDF / pág. 6 impresa.
> "Inteligencia Artificial Generativa (IAG). Tecnología que produce contenido nuevo a partir de modelos entrenados. En el ámbito académico se usa como apoyo, siempre respetando la originalidad. Su empleo para alterar documentos o evadir la detección de similitud constituye una falta."

**Nota de precisión:** esta es la **única** mención normativa del uso académico de la IAG en la directiva, y está en el artículo de definiciones, no en un artículo de obligaciones. La directiva no fija un procedimiento de declaración de uso de IA. Ver `[PENDIENTE-NORMATIVA] P-01`.

**Motor:** `CLAUDE.md` principio 6 (sin evasión) y `docs/integridad.md`.

### R-03 · Umbral de similitud: 0 % a 20 %
**Art. 23** (Escala de valoración de similitud), pág. 14 PDF / pág. 13 impresa.

| Similitud | Trabajos académicos | Tesis, artículos, libros | TSP |
|---|---|---|---|
| Permitido | 0 % al 20 % | 0 % al 20 % | 0 % al 20 % |
| Observado | Más de 20 % | Más de 20 % | Más de 20 % |

Concordante con el **art. 12, inciso c**, pág. 10 PDF / pág. 9 impresa, que condiciona el depósito de la versión final a un resultado "igual o inferior al veinte por ciento (≤ 20%)".

**Motor:** `similitud_interna.py` **no** mide esto (ver R-12). Solo se informa como dato al tesista.

### R-04 · Entrega en dos archivos .docx
**Art. 13, apartado A** (Condiciones para la evaluación de originalidad — Para tesis y libros), págs. 10-11 PDF / págs. 9-10 impresas.

- **A.1** — formato Ms Word, extensión `.docx`.
- **A.2** — divididos en dos archivos:
  > "a. **Primer archivo**, constituido por el documento de investigación sin carátula, dedicatorias, agradecimientos, lista de figuras, lista de tablas, referencias bibliográficas ni anexos.
  > b. **Segundo archivo**, constituido por la carátula, las dedicatorias, agradecimiento, lista de figuras, lista de tablas, la bibliografía y los anexos (si tuviese)."
- **A.3** — nomenclatura exacta:
  > "(Apellidos y nombres) - Desarrollo (Título del documento de investigación) - (Año).(extensión del archivo)"
  > "(Apellidos y nombres) - Protocolo y Complemento (Titulo del documento de investigación) - (Año).(extensión del archivo)"

  Ejemplos que trae la propia directiva: `Julca Pereda Dante Jorge - Desarrollo Competencia digitales en personas adultas - 2025.docx` y `Julca Pereda Dante Jorge - Protocolo y Complemento Competencia digitales en personas adultas - 2025.docx`.

**Motor:** `entregar.py`. La nomenclatura se genera, no se pide al tesista. Obsérvese que el ejemplo oficial **no** usa guion entre el rótulo y el título.

### R-05 · Estructura de carpetas de entrega
**Art. 13, A.4**, pág. 11 PDF / pág. 10 impresa.
> "a. La carpeta TEXTO debe contener los archivos con extensión docx: primer y segundo archivo.
> b. La carpeta DOCUMENTO debe ser nombrada acorde al tipo de documento de investigación."

**Motor:** `entregar.py` produce `entregables/TEXTO/` y `entregables/DOCUMENTO/`. **Requisito que el encargo no mencionaba.**

### R-06 · Documento completo; tablas y fórmulas como texto, no como imágenes
**Art. 13, A.6**, pág. 11 PDF / pág. 10 impresa.
> "Los documentos de investigación deben ser documentos completos que contengan todo el texto destinado a ser aprobado. En ningún caso, será válida la evaluación de originalidad aplicada a un segmento o parte de un documento. Las partes textuales, las tablas y las fórmulas (si los hay) deben estar como texto y no como imágenes."

**Motor:** `entregar.py` verifica el `.docx` generado y falla si hay tablas o ecuaciones rasterizadas.

### R-07 · Exclusiones del análisis de similitud
**Art. 14**, pág. 11 PDF / pág. 10 impresa. Se excluyen: referencias bibliográficas; coincidencias sintácticas menores a 20 palabras de uso común frecuente; palabras de la plantilla proporcionada. La directiva precisa que al superar las 20 palabras la PIDS lo marca.

**Motor:** fija el umbral de 20 palabras de `similitud_interna.py`, que ya estaba en el encargo.

### R-08 · Declaración jurada del autor (Anexo 4)
**Art. 15**, pág. 12 PDF / pág. 11 impresa; formato en **Anexo 4**, pág. 22 PDF.

Contenido real del Anexo 4 — importa porque **no es una declaración de originalidad**, sino de autorización:
> "DECLARACIÓN JURADA PARA LA EVALUACIÓN DE DOCUMENTOS CON LA PIDS […] DECLARO BAJO JURAMENTO que autorizo la evaluación de mi documento a través de la Plataforma PIDS de la UNMSM, aceptando los resultados que se consignen en el informe correspondiente, así como las disposiciones, infracciones y sanciones que pudieran derivarse del análisis efectuado conforme a la normativa vigente."

**Motor:** `entregar.py` genera el Anexo 4 con los datos del tesista, listo para firma. **Corrección respecto del encargo:** el encargo describe el Anexo 4 como la declaración jurada de originalidad; en la norma vigente es la autorización para someter el documento a la PIDS.

### R-09 · Documentación que se anexa obligatoriamente al expediente
**Art. 17**, págs. 12-13 PDF / págs. 11-12 impresas.
a) Certificado de Similitud emitido por el responsable de la revisión, con el Reporte de Similitud de la PIDS (Anexos 1, 2 y 3);
b) el último reporte de similitud, que acredite el porcentaje permitido;
c) el historial de análisis y evaluación, si hubo múltiples revisiones.

El **Certificado de Similitud (Anexo 1)** lo firma el **asesor**, no el estudiante, y su vigencia es de **noventa (90) días** desde su emisión (Anexo 1, pág. 19 PDF).

**Motor:** `entregar.py` genera el checklist del expediente y advierte del vencimiento de los 90 días. **La vigencia de 90 días no estaba en el encargo.**

### R-10 · Costo de las revisiones
**Art. 27**, págs. 14-15 PDF / págs. 13-14 impresas. La primera revisión es gratuita; desde la segunda, S/ 20.00 por revisión (código de servicio 201176 del BCP). El estudiante adjunta el comprobante original al expediente y los subadministradores verifican que el número de vouchers coincida con las veces que el asesor usó la PIDS.

**Motor:** `/estado` lo muestra como alerta de costo. **Requisito que el encargo no mencionaba.**

### R-11 · El indicador de IA de la plataforma no vale para el certificado
**Art. 28**, pág. 15 PDF / pág. 14 impresa.
> "El indicador del porcentaje de similitud generado por el componente de Inteligencia Artificial Generativa (IA) de la Plataforma PIDS no será considerado válido para la emisión del Certificado de Similitud. Únicamente se tomará en cuenta el reporte de similitud textual obtenido mediante los parámetros establecidos en la configuración oficial de la PIDS."

**Motor:** `docs/integridad.md`. Nótese que esto **no** autoriza el uso no declarado de IA; solo dice que ese indicador no sirve para certificar.

### R-12 · Faltas del autor
**Art. 30**, pág. 16 PDF / pág. 15 impresa. Son faltas, entre otras:
> "a. Presentar un manuscrito ajeno como propio, omitiendo la correspondiente cita parentética u otra forma de referencia bibliográfica […]
> c. Incorporar párrafos de texto en formato de imagen, con el propósito de evadir los mecanismos de detección de similitud de la Plataforma.
> d. Incluir caracteres extraños o realizar alteraciones intencionadas en el contenido del documento, con el fin de evitar la detección de similitud por parte de la PIDS, constituyéndose en una práctica fraudulenta."

**Motor:** prohibición dura. Ninguna herramienta del repositorio puede implementar c) ni d). `CLAUDE.md` principio 6.

## 3. Directiva general RR N.° 00744-R-20 (anexo de 16 folios)

Documento escaneado; leído por rasterización de páginas. Las páginas citadas son las impresas ("Página N de 16"), que coinciden con las del PDF.

### R-13 · La estructura del documento la fija cada facultad
**§ 6.3 Normatividad específica a cargo de la facultad**, pág. 6.
> "La facultad aprueba la normativa específica, considerando las características y disciplinas eje de la carrera, los GI y sus líneas de investigación vinculadas a los ODS, que dan soporte académico científico a la carrera, para la realización, elaboración y sustentación del TI, T y TSP, previa conformidad del Vicerrectorado Académico de Pregrado.
> También debe establecer **la estructura del cuerpo de los documentos** correspondientes al TI, TT y TSP, para los fines de elaboración, evaluación y sustentación."

**Motor:** este es el **fundamento normativo del diseño multifacultad por perfiles**. Confirma que no existe ni debe existir un esquema único, y que el perfil de cada escuela debe remitirse a su norma de facultad. Es la justificación de `perfiles/` y de que `verificar_perfil.py` exija fuente.

### R-14 · Tesis individual o grupal, máximo tres autores
**§ 7.2 Tesis (T) — Realización, incisos a) y b)**, pág. 7.
> "a) La T puede ser individual o grupal (máximo tres), compartiéndose las responsabilidades de la elaboración.
> b) Si la T es grupal, la EP verificará que el proyecto esté orientado a solucionar un problema complejo o de carácter multidisciplinario y que se hayan asignado objetivos definidos a cada participante."

**Motor:** `perfiles/*.yaml` campo `autoria`; `/iniciar` pregunta autoría; `entregar.py` lista autores y objetivos por autor.

### R-15 · Ruta del proyecto de tesis
**§ 7.2 — Realización, incisos c) a f)**, pág. 7. El estudiante elabora el proyecto de T, que **se revisa según la normativa específica** y **debe inscribirse en el registro correspondiente**; luego lo ejecuta con acompañamiento del asesor y elabora el informe con conformidad del asesor.

**Motor:** `/proyecto` cierra con "proyecto listo para inscripción"; `/estado` recuerda la inscripción.

### R-16 · Presentación y sustentación
**§ 7.2 — Presentación y Sustentación**, pág. 7. El informe de tesis "deberá ser certificada como original"; la EP designa al jurado; la sustentación es en acto público; la calificación se rige por el **art. 14 del Reglamento General de Grados y Títulos**; consta en acta suscrita por el jurado. La tesis y los documentos requeridos se depositan en el Repositorio Institucional.

### R-17 · El estudiante solo puede ser asesorado por el docente cuya propuesta eligió
**§ 5 Responsabilidades — Estudiante o egresado**, pág. 5.
> "El estudiante solo podrá ser asesorado por el docente cuya propuesta de investigación haya elegido para realizar su TI o TT. De ninguna manera tomará propuesta de investigación y solicitará la asesoría de otro docente de la facultad o de otras facultades de la universidad."

**Motor:** `/iniciar` registra al asesor; `/asesor` no admite comentarios de un segundo asesor sin advertencia.

### R-18 · El tema se elige de la relación publicada por la escuela
**§ 7.2 — Realización, inciso a) del segundo bloque**, pág. 7, y **§ 7.1 c) y d)**, pág. 6. El estudiante selecciona un tema de la relación publicada por la EP en la web de la facultad; si su tema no figura, coordina previamente con un docente para incluirlo, siempre que esté dentro de las líneas de investigación de la facultad y sea acorde a los ODS.

**Motor:** `/afinar-idea` debe preguntar por la línea de investigación y advertir que la pregunta elegida requiere estar en la relación de la EP o coordinarse para incluirla. **Restricción que el encargo no contemplaba y que condiciona la etapa 2.**

### R-26 · Estructura general de la tesis para título (Anexo 2A)
**Anexo 2A**, pág. 13 de 16. Añadido en la Fase 0b.

Fija las tres partes del documento y el contenido de los preliminares:

- **Identificación y preliminares**, con numeración **en romanos minúsculos** (el propio anexo ejemplifica "iv, v, vi"). Carátula con escudo de la universidad, facultad, escuela profesional, título de la tesis, la fórmula "Tesis para optar al título profesional de …", nombres y apellidos del bachiller, nombres y apellidos del asesor, y fecha (mes y año). Luego: resumen/abstract de **200 palabras**, palabras clave/keywords (**5 palabras**), acta de sustentación, dedicatoria **(opcional)** y agradecimiento **(opcional)**.
- **Información complementaria**: DNI del bachiller, correo institucional del asesor, grupo de investigación, fuente de financiamiento, disciplina de la OCDE y título en inglés o en quechua "de ser necesario".
- **Cuerpo**: remite al Anexo 2B.
- **Bibliografía y anexos**: > "Las referencias según los estilos de cita-referencia de acuerdo a las áreas del conocimiento."

**Motor:** define la carátula y los preliminares que genera `entregar.py` para **todas** las facultades. La última frase es la base normativa de que el estilo de citas viva en el perfil y no en el motor.

### R-27 · Estructura del cuerpo de la tesis (Anexo 2B)
**Anexo 2B**, pág. 14 de 16. Añadido en la Fase 0b. Dos modelos de siete capítulos:

| Cap. | Modelo 1 (cuantitativa) | Modelo 2 (cualitativa) |
|---|---|---|
| I | Introducción | Introducción |
| II | Revisión de literatura | Revisión de literatura |
| III | Hipótesis y variables | Hipótesis y variables (*HipóT o supuestos hipotéticos*) |
| IV | Materiales y métodos | Materiales y métodos |
| V | Resultados | Resultados |
| VI | Discusión | Discusión |
| VII | Conclusiones y recomendaciones | Conclusiones y recomendaciones |

Se diferencian en el detalle: el modelo 1 incluye `III.3 Operacionalización de las variables` y `IV.5 Análisis estadístico`; el modelo 2 los sustituye por `III.2 Sistemas y categorías de análisis`, `IV.4 Credibilidad de la investigación`, `IV.5 Sujetos de estudio` y `IV.7 Análisis de datos`.

**Motor:** es el **piso normativo** de la estructura. Un perfil de facultad especializa este esquema al amparo del §6.3 (R-13); una facultad sin norma propia lo hereda tal cual. Esto sustituye la idea de una "plantilla no normativa" para las escuelas sin documento.

### R-28 · Estructuras del trabajo de investigación para bachiller (Anexo 1)
**Anexo 1**, págs. 9 a 12 de 16. El TI tiene extensión de **10 000 a 20 000 palabras (20 a 50 páginas)** y cuatro modelos de cuerpo, según la naturaleza del trabajo: **1B documental**, **1C empírica**, **1D teórica o ensayo** y **1E técnica, tecnológica o innovación**.

**Motor:** fuera del alcance de la versión 1, que se centra en la tesis para título. Se registra para no perderlo.

## 4. Reglamento General de Grados y Títulos — RR N.° 01827-R-17

### R-19 · Escala de calificación
**Art. 14**, modificado por la RR N.° 00744-R-20 (pág. 1-2 de la resolución):
> "0 a 10 Desaprobado / 11 a 15 Aprobado / 16 a 18 Aprobado con mención honrosa / 19 y 20 Aprobado con máximos honores"

**Motor:** rúbrica de `/sustentacion` y simulación del jurado.

### R-20 · Papel del asesor
**Art. 7**, pág. 7 PDF.
> "El asesor de los trabajos de investigación y de las tesis es designado por el Director de la Escuela Profesional y acompaña al asesorado en los aspectos temáticos y metodológicos, garantizando la calidad académica de la investigación la cual debe contribuir a la solución de problemas de personas, la sociedad y el ambiente."

## 5. Código de Ética en Investigación — RR N.° 012648-2023-R

### R-21 · Principios aplicables
**Art. 5**, págs. 5-6 PDF. Probidad, veracidad, imparcialidad, **transparencia**, independencia, responsabilidad, respeto y confidencialidad. Sobre transparencia:
> "Todas las acciones y procesos de investigación son auditables y se desarrollan de modo tal que cada uno de sus pasos sea verificable y al acceso de cualquier miembro de la comunidad académica, con el solo resguardo de la identidad de los sujetos de investigación."

**Motor:** es el fundamento ético de `decisiones/` y `registro/`: un proceso auditable paso a paso. Es la mejor justificación normativa del registro de IA, aunque este no sea exigido por ninguna norma (ver P-01).

### R-22 · Confidencialidad de los sujetos
**Art. 5 — Confidencialidad**, pág. 6 PDF: la información no se divulga sin consentimiento de la persona.
**Art. 12** (pág. 7 PDF): "No coartar la libertad de la persona y aplicar el consentimiento informado ante la toma de […]".

**Motor:** anonimización obligatoria en `/explorar-datos`; consentimiento informado como anexo cuando hay sujetos humanos.

### R-23 · Prohibiciones de los investigadores
**Art. 10**, pág. 6 PDF.
> "b) Ofrecer apoyo, orientación u otra forma de participación **que exceda las labores de asesoría de tesis** que brindan los docentes, por sí o a través de terceros, a favor del tesista.
> c) Incluir como autor o coautor (es) a persona (s) que no han participado en la investigación.
> d) La manipulación de la información, las cifras estadísticas y las conclusiones de las investigaciones."

**Motor:** d) es el fundamento del principio "datos reales o nada" y de `verificar_cifras.py`.
**b) merece una advertencia explícita** y está desarrollada en `conflictos.md`: la norma prohíbe el apoyo de terceros que exceda la asesoría. El repositorio debe hacer esto visible al tesista y al asesor, no ocultarlo.

## 6. Protección de datos — Ley N.° 29733 y DS N.° 016-2024-JUS

### R-24 · Marco aplicable a los datos que el tesista recolecte
El Código de Ética remite expresamente a la Ley 29733 en su base legal (pág. 4 PDF). El reglamento vigente es el **DS 016-2024-JUS** (30/11/2024), que derogó el DS 003-2013-JUS y entró en vigor el 30/03/2025.

**Motor:** `datos/crudos/` fuera de git; anonimización antes de salir de `datos/crudos/`; consentimiento informado documentado. La extracción artículo por artículo de los 135 artículos del reglamento se hará al implementar la Fase 3 y no antes, porque solo aplica a proyectos con datos personales.
**Estado:** parcial — `[PENDIENTE-NORMATIVA] P-05`.

## 7. Repositorio: RENATI y Cybertesis

### R-25 · Depósito en el repositorio institucional
Exigido por la directiva 00744 §7.2 (R-16) y por el Protocolo de depósito en Cybertesis. La directiva RR 06893-R-18 está descargada pero es un **escaneo sin capa de texto** y aún no ha sido leída, de modo que sus requisitos concretos (metadatos, formatos, plazos, licencia) están **pendientes**: `[PENDIENTE-NORMATIVA] P-04`.

## 8. Pendientes y salvedades

| ID | Asunto | Estado |
|---|---|---|
| **P-01** | **Declaración de uso de IA por el tesista.** Ninguna de las normas leídas exige declarar el uso de IA generativa en una tesis, ni fija un formato. La RR 008449-2025-R es una guía **pedagógica para docentes** (planificación de clases, evaluación, ejemplos de prompts); no regula la redacción de tesis por estudiantes ni establece obligación de declarar. | `[PENDIENTE-NORMATIVA]`. El anexo de declaración de uso de IA que genera el repositorio es una **medida voluntaria de transparencia**, apoyada en el principio de transparencia del Código de Ética (R-21), **no** un requisito normativo. Debe presentarse así al tesista. |
| **P-02** | **Guía de IA generativa para estudiantes de la UNMSM.** Buscada; no encontrada. | `[PENDIENTE-NORMATIVA]`, conforme a lo previsto en el encargo. |
| **P-03** | **Versión vigente del Código Nacional de Integridad Científica.** Hay dos PDF con distinta extensión (10 y 17 páginas) y dos resoluciones (RP 028-2024 y RP 035-2024-CONCYTEC-P, esta última modificatoria). | Verificar cuál es el texto vigente antes de citar artículos. |
| **P-04** | **Directiva de depósito en Cybertesis (RR 06893-R-18) y su modificatoria RR 00584-R-19.** La primera está descargada como escaneo sin capa de texto; la segunda no se ha localizado. | Pendiente de lectura por imagen y de búsqueda. |
| **P-05** | **Obligaciones concretas del DS 016-2024-JUS** aplicables a una tesis con datos personales. | Pendiente para la Fase 3. |
| **P-06** | **Reglamento del RENATI.** El texto integrado se obtuvo de una copia alojada por la Universidad Nacional de San Agustín, porque el enlace oficial de SUNEDU redirige a gob.pe, que bloquea la descarga automatizada desde este equipo. | No se citará artículo del RENATI hasta contrastarlo con el PDF oficial. |
| **P-07** | **Edición de APA que exige la Escuela de Economía.** Su guía dice "normas APPA" sin precisar edición ni año. | `[PENDIENTE-NORMATIVA]`; el perfil usará APA 7 como valor operativo, marcado. |

## 9. Requisitos que el encargo daba por ciertos y que la lectura corrigió o precisó

1. **Anexo 4** no es la declaración jurada de originalidad, sino la **autorización para someter el documento a la PIDS** y aceptar sus resultados y sanciones (R-08).
2. **El art. 13 no es "la entrega"** en general: es el artículo de *condiciones para la evaluación de originalidad*. Los dos archivos .docx son el insumo de la evaluación de similitud, y por eso además existe la estructura de carpetas TEXTO/DOCUMENTO del art. 13 A.4 (R-05), que el encargo no recogía.
3. **La regla sobre IA generativa está en el artículo de definiciones** (art. 5 q), no en un artículo de obligaciones (R-02).
4. **Requisitos no previstos en el encargo:** vigencia de 90 días del certificado de similitud (R-09), costo de S/ 20 desde la segunda revisión (R-10), obligación de elegir el tema de la relación publicada por la escuela (R-18) y registro en el sistema RAIS (directiva 00744 §7.1).
5. **El fundamento normativo del diseño por perfiles existe y es explícito:** §6.3 de la directiva 00744 (R-13).
6. **La RR 00744-R-20 declara un alcance por año de ingreso.** En sus considerandos dice que se aprueba "con la finalidad de establecer las normas y los procedimientos que regirán a los estudiantes que ingresaron a partir del año 2016 o se han incorporado a los planes de estudios del año de referencia". El régimen aplicable a quienes ingresaron antes de 2016 y no migraron de plan **no se localizó**.

   **Decisión tomada:** el repositorio aplica los Anexos 2A y 2B a todo el mundo, sin preguntar el año de ingreso. La razón es de diseño, no normativa: empezar la tesis no debe depender de un trámite ni de una entrevista de admisibilidad (ver `CLAUDE.md`, «Empezar no requiere permiso»). El dato queda anotado aquí para que nadie lo descubra tarde, y porque si un tesista de una promoción anterior encuentra una discrepancia con lo que le pide su escuela, esta es la explicación probable.

7. **Sí existe una estructura de tesis aprobada para toda la UNMSM** (R-26, R-27). La premisa del encargo de que "no existe un esquema único" es cierta solo en cuanto a las especializaciones de facultad: hay un piso común, los Anexos 2A y 2B de la RR 00744-R-20. Se detectó en la Fase 0b, al leer las páginas escaneadas del anexo de la directiva que en la Fase 0 habían quedado sin revisar. Consecuencia de diseño: el perfil `generico-cualitativo` deja de ser una "plantilla no normativa" y pasa a ser un perfil **verificado** derivado del Anexo 2B, modelo 2.
