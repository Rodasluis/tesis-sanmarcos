# Prompt para Claude Code — Repositorio `tesis-sanmarcos` (v2)

> Copia todo lo que está debajo de la línea en una sesión nueva de Claude Code, dentro de una carpeta vacía con `git init`. Antes, coloca en `normativa/` los documentos de la sección 2 y en `normativa/facultades/<facultad>/` los esquemas de cada facultad que tengas (sección 3).

---

## 1. Rol y objetivo

Eres el arquitecto y desarrollador principal de `tesis-sanmarcos`, un repositorio abierto (licencia MIT) que permite a estudiantes de pregrado de la Universidad Nacional Mayor de San Marcos (UNMSM) elaborar su tesis con Claude Code, desde la idea hasta la sustentación.

El motor es **multifacultad desde el diseño**: la estructura, el estilo de citas, el formato y los requisitos de cada escuela viven en perfiles YAML, no en el código. La versión 1 se valida con tres perfiles de referencia (Economía-FCE, Medicina-FM y un perfil cualitativo), y el resto de facultades se agrega con perfiles sin tocar el motor.

Modelo de trabajo — **ejecución integral por Claude**:

- **Claude Code ejecuta el 100 % del trabajo operativo**: verificación de la instalación, exploración y descarga de datos, afinamiento de ideas, búsqueda y síntesis de literatura, proyecto de tesis, limpieza y análisis, redacción de todos los capítulos, formato, carátula, índices, verificación, generación de los .docx de entrega, formularios del expediente, diapositivas y preparación de la sustentación.
- **El estudiante no escribe ni programa nada fuera del flujo.** Su intervención se limita a tres cosas, todas dentro de la sesión: (a) **decidir** en los puntos de control, (b) **firmar** las declaraciones juradas y (c) **sustentar**.
- **Las decisiones del estudiante son el único bloqueo del flujo.** Son las que sostienen la autoría que el estudiante declara bajo juramento (directiva de originalidad, Anexo 4) y lo que el jurado evaluará en la sustentación. Por eso el flujo automatiza todo lo demás, pero nunca decide por el estudiante.
- **Las ideas de investigación nacen de datos reales**, sean fuentes abiertas o datos que el estudiante recolectó. Nunca se inventan datos, resultados, citas ni requisitos normativos.

No empieces a programar de inmediato. Primero lee `normativa/` y esta especificación. Luego entrégame un **plan de implementación por fases** con la estructura de archivos, las dependencias y los riesgos, y espera mi aprobación.

## 2. Marco normativo general (fuente de verdad)

Lee los documentos (PDF y DOCX) de `normativa/` y extrae los requisitos en `normativa/requisitos.md`, con documento, artículo y página de cada uno. Documentos esperados:

1. Directiva de originalidad y similitud de la UNMSM, RR N.° 000947-2026-R. Requisitos clave:
   - La IA generativa se permite como apoyo, respetando la originalidad. Usarla para alterar documentos o evadir la detección de similitud constituye falta.
   - La tesis debe ser un documento original e inédito.
   - El umbral de similitud permitido es de 0 % a 20 %, medido en Turnitin (PIDS). El indicador de IA de la plataforma no se usa para el certificado.
   - La entrega se hace en **.docx dividido en dos archivos** (art. 13):
     - Archivo 1, "Desarrollo": sin carátula, dedicatorias, listas, referencias ni anexos.
     - Archivo 2, "Protocolo y Complemento": carátula, dedicatorias, agradecimientos, listas de tablas y figuras, bibliografía y anexos.
   - Nombres de archivo: `Apellidos Nombres - Desarrollo Título - Año.docx` y `Apellidos Nombres - Protocolo y Complemento Título - Año.docx`.
   - Las tablas y fórmulas deben estar como texto, no como imágenes.
   - El autor firma una declaración jurada (Anexo 4).
2. Reglamento de Grados y Títulos de la UNMSM (RR 01827-R-17 y sus modificatorias).
3. Directiva general para la tesis y el trabajo de investigación (RR 00744-R-2020). Verifica y extrae, entre otros, el art. 7.2: tesis individual o grupal (hasta tres autores); si es grupal, el problema debe ser complejo o multidisciplinario y cada participante debe tener objetivos definidos.
4. Código de Ética en Investigación de la UNMSM (RR 012648-2023-R).
5. Código Nacional de Integridad Científica del CONCYTEC.
6. Guía de uso de IA generativa para docentes de la UNMSM (RR 008449-2025-R). Busca si existe una guía equivalente para estudiantes; si no la encuentras, regístralo como `[PENDIENTE-NORMATIVA]`.
7. Ley N.° 29733, de Protección de Datos Personales, y su reglamento (para datos recolectados por el estudiante).
8. Reglamento RENATI (SUNEDU) y la directiva de depósito en Cybertesis de la UNMSM (RR 06893-R-18 y modificatoria RR 00584-R-19), para los requisitos de repositorio.

Reglas generales:

- Todo requisito que no conste en un documento leído se marca `[PENDIENTE-NORMATIVA]`. No completes vacíos con "prácticas habituales" ni con guías de terceros (blogs, Scribd, Studocu, SlideShare, sitios comerciales). Esas fuentes solo sirven como **pista** para buscar el documento oficial.
- Cuando una norma de facultad contradiga una norma general, prevalece la general y el conflicto se registra en `normativa/conflictos.md`.

## 3. Modelos de estructura por facultad

### 3.1 Qué se sabe hoy (relevamiento preliminar)

La UNMSM tiene 20 facultades y cada una fija su esquema por resolución decanal o directiva propia. El relevamiento preliminar muestra que **no existe un esquema único**: hay al menos seis familias de estructura, y difieren también en estilo de citas, persona gramatical, obligatoriedad de hipótesis y anexos, y requisitos éticos.

| Familia | Fuente identificada | Estado | Rasgos que el motor debe soportar |
|---|---|---|---|
| **A. Diseño FCE (Economía)** | `PAUTAS_PARA_SUSTENTACION_DE_TESIS.docx` (Escuela de Economía) | Documento en mano | Hipótesis **antes** de objetivos; introducción con antecedentes e importancia; esquema capitular tentativo como ítem del proyecto; ítems excluibles con justificación; no exige matriz de consistencia ni cronograma; APA. |
| **B. IMRyD clínico (Medicina)** | Reglamento para la elaboración de tesis de las cinco escuelas de la Facultad de Medicina, **RD N.° 002373-2023-D-FM** (19/06/2023), anexos C, D, E y F | Oficial, verificado en línea | Proyecto cuantitativo en 3 capítulos (problema; marco teórico + hipótesis "si es pertinente" + diseño metodológico con ética y consentimiento; cronograma, presupuesto y recursos **obligatorios**). Informe final cuantitativo en formato Introducción–Métodos–Resultados–Discusión, con resumen en español e inglés según el formato de *Anales de la Facultad de Medicina*. **Referencias en Vancouver**, no APA. Aprobación previa del Comité de Investigación y de un **Comité de Ética**. Vigencia del proyecto: un año (+6 meses por única vez). Sustentación: exposición de 15–20 min, preguntas hasta 20 min, rúbrica de 5 criterios (20 puntos). Jurado de 4 (asesor con voz y sin voto). |
| **C. Cualitativa clínica (Medicina)** | Misma RD, anexos D y E | Oficial, verificado | Referente teórico y metodológico (fenomenológico, etnográfico, teoría fundamentada, investigación-acción, estudio de caso), escenario, participantes, plan de trabajo de campo; informe con "Resultados y discusión" fusionados. |
| **D. Cuantitativa clásica en 4–5 capítulos** | Facultad de Educación, R.D. 1069-D-FE-2017 (solo vista en fuente secundaria) | **Verificar** documento oficial y vigencia | Cap. I planteamiento (fundamentación, formulación, objetivos, justificación, hipótesis, variables); Cap. II marco teórico (antecedentes, bases teóricas, términos básicos); Cap. III metodología (operacionalización, tipo y nivel, diseño, población y muestra, técnicas e instrumentos); Cap. IV procesamiento, contrastación de hipótesis y discusión; conclusiones y recomendaciones. |
| **E. Cualitativa en humanidades y educación** | Educación (misma R.D., fuente secundaria); UPG de Letras, Dictamen N.° 000002-2022-UPG-VDIP-FLCH (posgrado) | Educación: verificar. Letras: oficial, pero **de posgrado** | Pregunta de orientación en lugar de hipótesis; categorías de análisis; corpus u objeto de estudio; trabajo de campo; capítulo de "Análisis"; aspectos éticos como sección propia. |
| **F. Argumentativa o por obra (Filosofía, Literatura, Arte, Escritura creativa)** | UPG de Letras, mismo dictamen | Oficial, de posgrado | Introducción narrativa (problema, objetivos, justificación, limitaciones, estructura); capítulos titulados por contenido, uno por objetivo ("discusión crítica y argumentativa 1, 2, 3"); estado de la cuestión; en escritura creativa, la obra propia va como anexo y se analiza con las categorías del marco. **Sin metodología empírica ni datos.** |
| **G. Mixta** | UPG de Letras, mismo dictamen | Oficial, de posgrado | Metodología con corpus **y** población/muestra; análisis cualitativo y cuantitativo por separado antes de resultados y discusión. |

Datos de formato ya confirmados en fuente oficial (solo para su perfil; no los generalices):

- **Letras (UPG)**: APA 7; márgenes 2,5 cm (superior, inferior y derecho) y 3,5 cm (izquierdo); interlineado 1,5; Times New Roman 12; numeración inferior derecha, romanos en la parte preliminar y arábigos desde la introducción; redacción en tercera persona, impersonal **o primera persona plural**; resumen con palabras clave **y líneas de investigación**; maestría 100–120 páginas; la UNMSM no exige versión impresa.
- **Medicina**: umbral Turnitin de 20 % antes de conformar jurado; la tesis puede ser grupal (hasta tres).
- El documento de Letras tiene errores de numeración internos (por ejemplo, "5.1 Resultados" dentro del capítulo 4). Al traducirlo a perfil, normaliza la numeración y registra la corrección en `perfiles/_notas_normalizacion.md`.

### 3.2 Tarea de relevamiento (Fase 0b)

1. Crea `normativa/facultades/indice.yaml` con las 20 facultades y, para cada una, sus escuelas, el documento de estructura (nombre, número de resolución, fecha, URL), el nivel (pregrado o posgrado) y el estado: `verificado`, `verificar`, `solo_fuente_secundaria` o `no_encontrado`. Facultades a cubrir: Medicina; Farmacia y Bioquímica; Odontología; Medicina Veterinaria; Psicología; Ciencias Biológicas; Química e Ingeniería Química; Ciencias Físicas; Ciencias Matemáticas; Ingeniería Geológica, Minera, Metalúrgica y Geográfica; Ingeniería Industrial; Ingeniería Electrónica y Eléctrica; Ingeniería de Sistemas e Informática; Derecho y Ciencia Política; Letras y Ciencias Humanas; Ciencias Sociales; Educación; Ciencias Económicas; Ciencias Contables; Ciencias Administrativas.
2. Busca primero en los sitios oficiales (`*.unmsm.edu.pe`, resoluciones con código de verificación en `spsgd.unmsm.edu.pe`) y en Cybertesis. **Descarga y guarda cada PDF**; no trabajes desde resúmenes.
3. Donde no haya esquema oficial de pregrado, busca tesis sustentadas recientes de esa escuela en Cybertesis (al menos cinco, de los últimos tres años) y deriva el **esquema de facto** en `normativa/facultades/<facultad>/esquema_de_facto.md`, con los enlaces. Un esquema de facto nunca se marca como `verificado`.
4. Entrega `normativa/facultades/comparativo.md`: matriz de secciones por facultad (presente, ausente, opcional, orden), estilo de citas, persona gramatical, hipótesis (obligatoria, condicional, no aplica), anexos obligatorios, comité de ética y formato del resumen.
5. Espera mi revisión antes de crear perfiles distintos de los tres de referencia.

### 3.3 Esquema de perfiles (`perfiles/_esquema.yaml`)

Cada perfil define, como mínimo:

```yaml
id: economia-fce
facultad: Ciencias Económicas
escuela: Economía
nivel: pregrado
familia: A            # A–G de la sección 3.1
enfoques_admitidos: [cuantitativo, cualitativo, mixto]
fuente: {documento: "...", norma: "...", fecha: "...", estado: verificado}
estilo_citas: apa7    # apa7 | vancouver | otro (con CSL en plantillas/)
persona_gramatical: [tercera, impersonal]
formato: {margenes_cm: {...}, fuente: "...", tamano: 12, interlineado: ..., numeracion: {...}}
extension_paginas: null            # o rango, si la norma lo fija
resumen: {idiomas: [es, en], palabras_clave: true, lineas_investigacion: false, formato: null}
hipotesis: obligatoria             # obligatoria | condicional | no_aplica
proyecto:
  secciones: [...]                 # en el orden y con las denominaciones de la norma
informe_final:
  origen: esquema_capitular        # esquema_capitular | plantilla_norma
  secciones: [...]
anexos_obligatorios: [...]
anexos_recomendados: [matriz_consistencia, operacionalizacion, cronograma]
etica: {comite_requerido: false, consentimiento: condicional}
autoria: {max_autores: 3, objetivos_por_autor: true}
vigencia_proyecto_meses: null
sustentacion: {exposicion_min: null, preguntas_min: null, rubrica: null, jurado: null}
```

Cada campo lleva su `fuente` (documento, artículo, página) o el valor `[PENDIENTE-NORMATIVA]`. Cada sección puede declarar `opcional_con_justificacion: true`.

### 3.4 Perfiles de referencia de la versión 1

1. **`economia-fce.yaml`** (familia A). Traduce `normativa/PAUTAS_PARA_SUSTENTACION_DE_TESIS.docx` **respetando su orden y denominaciones**:
   - Primera página: datos generales.
   - Introducción: descripción panorámica de los capítulos, **antecedentes** informativos o bibliográficos e **importancia** de la investigación.
   - 1. Definición y planteamiento del problema: 1.1 Identificación, 1.2 Delimitación, 1.3 Formulación y 1.4 Justificación del estudio.
   - 2. Hipótesis: genéricas y específicas (u otra forma según la naturaleza del problema). Va **antes** de los objetivos.
   - 3. Objetivos: concretos, concisos y susceptibles de cuantificarse (metas); de conocimiento y de solución de problemas.
   - 4. Marco teórico: aspectos conceptuales y referenciales.
   - 5. Metodología: 5.1 Consideraciones metodológicas (métodos y técnicas de recopilación, selección y análisis, organizados por etapas o fases).
   - 6. Esquema del proyecto de investigación: esquema capitular tentativo de la tesis, en secuencia lógica con la hipótesis.
   - 7. Bibliografía: orden alfabético, normas APA. La guía no fija la edición; usa APA 7 y márcalo `[PENDIENTE-NORMATIVA]`.
   - 8. Anexos.
   - La guía permite **excluir o ajustar ítems con justificación**; la justificación se registra como decisión del estudiante.
   - La guía **no** exige matriz de consistencia, operacionalización, cronograma ni presupuesto: son anexos recomendados.
   - La guía **no** define el informe final: se construye desde el esquema capitular (ítem 6) aprobado por el estudiante.
2. **`medicina-fm.yaml`** (familias B y C, con `enfoque` elegible). Traduce los anexos C, D, E y F de la RD N.° 002373-2023-D-FM. Estilo Vancouver, comité de ética obligatorio, cronograma y presupuesto obligatorios en el proyecto, rúbrica de sustentación de la norma.
3. **`generico-cualitativo.yaml`** (familia E). Plantilla base para escuelas sin esquema verificado, marcada como `estado: plantilla_no_normativa`; el flujo exige que el asesor la confirme antes de `/proyecto`.

Cuando un estudiante elija una escuela sin perfil verificado, `/iniciar` se lo advierte, le pide el documento de su escuela o la confirmación del asesor y no avanza de la etapa 4 sin ello.

## 4. Principios no negociables (van también al `CLAUDE.md` del repositorio)

1. **Datos reales o nada.** Toda cifra del texto proviene de un archivo en `resultados/` generado por código en `codigo/`. En investigación cualitativa, toda cita de un participante proviene de una transcripción en `datos/crudos/` y toda categoría, de un libro de códigos en `resultados/`. Prohibido simular, imputar sin declararlo o "completar" datos, respuestas o testimonios.
2. **Citas solo desde Zotero.** Solo se citan claves presentes en `referencias.bib`. Las citas textuales llevan página. Una afirmación sin fuente se marca `[VERIFICAR]` y nunca se rellena con una referencia "recordada".
3. **Decisiones del estudiante, en sesión.** Cada etapa cierra con preguntas interactivas al estudiante. Sus respuestas se guardan **textualmente** en `decisiones/` mediante `herramientas/registrar_decision.py`, con fecha y etapa. Claude no inventa, resume ni reescribe respuestas del estudiante, no elige por él y no avanza de etapa sin una decisión aprobada.
4. **Trazabilidad.** Cada acción de Claude se registra y cada borrador va en un commit propio. Las ediciones del estudiante se respetan en las regeneraciones.
5. **Transparencia.** El repositorio genera automáticamente un anexo de declaración de uso de IA a partir del registro, que describe con exactitud el alcance de la participación de Claude.
6. **Sin evasión.** Prohibido parafrasear para bajar la similitud, insertar caracteres, convertir texto en imágenes o cualquier técnica para evadir Turnitin o los detectores.
7. **Idioma y estilo según perfil.** Español formal peruano; la persona gramatical y el estilo de citas los fija el perfil (APA 7 en español por defecto; Vancouver en Medicina).
8. **Protección de datos.** Los datos personales recolectados por el estudiante se anonimizan antes de salir de `datos/crudos/`, nunca se suben al repositorio remoto y su tratamiento se documenta conforme a la Ley N.° 29733 y al consentimiento informado.

## 5. Stack técnico

- **Python** con `uv` y `pyproject.toml`, compatible con Windows, macOS y Linux. Prioriza Windows.
- **Quarto** como fuente (`.qmd`), con salida a **.docx** usando una plantilla de referencia **por perfil** (`plantillas/<perfil>/referencia.docx`), con márgenes, fuente, interlineado y numeración tomados del perfil. PDF opcional.
- **Zotero + Better BibTeX**, con auto-exportación a `referencias.bib` y claves estables.
- **Zotero MCP** opcional (por ejemplo, `54yyyu/zotero-mcp`). Verifica las instrucciones vigentes en su repositorio antes de documentarlas.
- **CSL** en `plantillas/csl/`: `apa-es.csl` y `vancouver.csl` como mínimo, seleccionados por el perfil.
- **Análisis cualitativo**: codificación asistida en Python con libro de códigos en YAML y exportación compatible con herramientas QDA (por ejemplo, formato REFI-QDA si es viable; verifícalo).
- **Git**, más GitHub Actions para CI.

## 6. Estructura del repositorio

```
tesis-sanmarcos/
├── CLAUDE.md                     # reglas permanentes (sección 4) + flujo
├── README.md                     # guía para estudiantes (español, paso a paso)
├── LICENSE                       # MIT
├── NOTICE.md                     # atribuciones
├── pyproject.toml
├── _quarto.yml                   # generado desde el perfil activo
├── referencias.bib
├── normativa/
│   ├── requisitos.md
│   ├── conflictos.md
│   └── facultades/               # indice.yaml, comparativo.md, <facultad>/...
├── perfiles/                     # _esquema.yaml, economia-fce.yaml, medicina-fm.yaml, generico-cualitativo.yaml
├── plantillas/                   # <perfil>/referencia.docx, csl/, caratulas, declaraciones, formularios
├── decisiones/                   # solo vía registrar_decision.py
│   └── _plantillas/
├── notas/                        # ideas, asesor, lecturas
├── datos/
│   ├── crudos/                   # inmutables; datos personales fuera de git
│   ├── procesados/
│   └── diccionarios/
├── codigo/
├── resultados/
├── capitulos/                    # generados desde el perfil y el esquema capitular aprobado
├── entregables/
├── registro/
├── herramientas/
├── tests/
├── .claude/
│   ├── settings.json
│   ├── agents/
│   ├── skills/
│   └── hooks/
└── ejemplos/
    ├── economia-cuantitativo/
    └── medicina-cualitativo/
```

Los nombres de archivo de `capitulos/` **no están fijos**: los genera `/proyecto` a partir del perfil y del esquema capitular aprobado.

## 7. Flujo por etapas, con puntos de control del estudiante

Todo ocurre dentro de Claude Code. Cada etapa es un comando (skill) y cierra con un **punto de decisión en sesión**:

1. Claude presenta opciones con ventajas, riesgos y factibilidad, y marca **una como recomendada** con su razón.
2. El estudiante elige, pide cambios o propone una alternativa; Claude itera hasta que apruebe.
3. Claude hace de 2 a 3 **preguntas de comprensión tipo jurado** sobre la decisión. No bloquean el avance, quedan registradas y alimentan `/sustentacion`.
4. `registrar_decision.py` guarda en `decisiones/NN_etapa.json` y `.md` la opción elegida, las respuestas textuales, los cambios pedidos, las preguntas de comprensión con sus respuestas y `aprobado: true`.

El registro no pretende probar que el estudiante escribió cada palabra. Su objetivo es que el asesor vea el proceso completo y que el estudiante llegue a la sustentación habiendo tomado y entendido cada decisión.

| # | Comando | Qué hace Claude | Qué decide el estudiante |
|---|---------|-----------------|--------------------------|
| 0 | `/iniciar` | Entrevista (facultad, escuela, enfoque, intereses, datos, asesor, plazos, autoría individual o grupal), carga el perfil, verifica la instalación y advierte si el perfil no está verificado. | Tema general, enfoque y restricciones. |
| 1 | `/explorar-datos` | Cataloga y descarga fuentes abiertas o ingiere los datos del estudiante (incluidas transcripciones). Genera diccionario, descriptivos, cobertura y calidad; anonimiza datos personales. | Qué fuentes usar. |
| 2 | `/afinar-idea` | Propone de 3 a 5 preguntas con variables o categorías disponibles, unidad de análisis, muestra o corpus, estrategia empírica o analítica, supuestos, riesgos y semáforo de factibilidad. En familia F, propone problemas argumentativos y corpus en lugar de datos. | Elige, combina o ajusta; aprueba la pregunta, la hipótesis (si el perfil la exige) y la estrategia. |
| 3 | `/literatura` | Busca en Zotero y bases abiertas (OpenAlex, Crossref, Semantic Scholar; PubMed si el perfil es de salud), sintetiza y detecta vacíos. Solo agrega a Zotero con aprobación. | Qué lecturas son centrales. |
| 4 | `/proyecto` | Redacta el proyecto con las secciones, el orden y las denominaciones exactas del perfil, incluido el esquema capitular si aplica, y los anexos obligatorios (cronograma, presupuesto, consentimiento, etc.). Si el perfil exige comité de ética, prepara el expediente para el comité. | Aprobación, ítems excluidos con justificación y comentarios del asesor. |
| 5 | `/analizar` | Limpieza, variables, estimaciones y robustez; o codificación, categorías y saturación en investigación cualitativa. Registra las especificaciones probadas, sin *p-hacking*. | Especificación principal y robustez, o libro de códigos final. |
| 6 | `/redactar <capitulo>` | Redacta cada capítulo con base en decisiones, notas, `resultados/` y `referencias.bib`, con la persona gramatical y el estilo del perfil. Respeta los párrafos que el estudiante editó. | Revisión y edición del capítulo. |
| 7 | `/jurado` | Simula el jurado con la composición del perfil (metodológico, temático y de forma). Observaciones SUBSANABLE, DE FONDO o FORMAL, cada una con "qué me haría cambiar de opinión". | Qué observaciones atender y cómo. |
| 8 | `/verificar` | Corre todas las herramientas de la sección 9 y el puntaje global. | Correcciones finales. |
| 9 | `/entregar` | Genera los dos .docx de la directiva, la declaración de uso de IA, las declaraciones juradas y los formularios del expediente del perfil (por ejemplo, solicitud de asesor), listos para firma. | Conformidad final y firma. |
| 10 | `/sustentacion` | Diapositivas, guion ajustado al tiempo del perfil, banco de preguntas y simulación interactiva calificada con la rúbrica del perfil. | Ensayo y ajustes. |

Comandos auxiliares:

- `/autopiloto`: encadena las etapas de principio a fin. Claude ejecuta todo el trabajo de cada etapa sin pedir instrucciones intermedias y se detiene **solo** en cada punto de decisión, donde muestra la opción recomendada preseleccionada; el estudiante la confirma, la cambia o pide ajustes. Las preguntas de comprensión se agrupan al final de cada etapa. El autopiloto nunca registra una decisión sin respuesta explícita del estudiante.
- `/estado`: tablero con avance, decisiones pendientes y alertas (incluida la vigencia del proyecto si el perfil la fija).
- `/asesor`: incorpora comentarios del asesor en `notas/asesor/` y propone cambios.
- `/checkpoint`: resume la sesión y el avance.

### Fuentes abiertas a catalogar en `/explorar-datos`

Crea `herramientas/fuentes/catalogo.yaml` con nombre, URL, tipo de acceso (API, descarga o manual), frecuencia, desagregación, **facultades para las que es pertinente** y notas de uso. Incluye como mínimo:

- INEI Microdatos: ENAHO, ENDES, ENAPRES, EPEN, Censos y ENE.
- BCRP: API de series estadísticas.
- MEF: Consulta Amigable y datos de transparencia económica.
- MINEDU: ESCALE, Censo Escolar y evaluaciones ECE/ENLA.
- Plataforma Nacional de Datos Abiertos (datosabiertos.gob.pe).
- OSCE/OECE y SEACE (contrataciones públicas).
- SUNEDU, MINSA/SUSALUD, RENIEC (estadísticas agregadas) y repositorios del INS.
- Banco Mundial (WDI), CEPALSTAT y FMI.
- Para humanidades: Cybertesis, repositorios de la Biblioteca Nacional del Perú y archivos digitales (como corpus, no como datos estadísticos).

Implementa descargadores solo donde exista acceso programático estable. Para el resto, genera instrucciones de descarga manual. **Verifica cada URL y endpoint antes de incluirlo**; si uno no responde, déjalo como "verificar".

## 8. Agentes (pares trabajador-crítico)

Toma como inspiración el diseño de `hugosantanna/clo-author` (MIT), sin hacer fork y con atribución en `NOTICE.md`. Los críticos **no pueden editar archivos**. Los trabajadores no se autoevalúan. Si tras 3 rondas no hay acuerdo, se escala al estudiante.

| Trabajador | Crítico |
|---|---|
| explorador-datos | critico-datos (calidad, sesgos de muestra, factibilidad, anonimización) |
| afinador-ideas | critico-identificacion (supuestos causales y validez; en cualitativa, rigor y transferibilidad) |
| bibliotecario | critico-citas (existencia, pertinencia, respaldo real) |
| analista | critico-codigo (reproducibilidad, errores, *p-hacking*) |
| codificador-cualitativo | critico-codificacion (consistencia del libro de códigos, citas trazables a transcripciones) |
| redactor | critico-redaccion (coherencia pregunta–método–resultados, estilo del perfil, normativa) |
| normativo | critico-perfil (fidelidad del perfil a la norma de la facultad, fuentes y estados) |
| — | jurado-metodologico, jurado-tematico, jurado-formal |
| orquestador | verificador (corre herramientas y puntajes) |

Puntajes de calidad (0 a 100) por componente. Commit con 80 o más, paso de etapa con 85 o más y entrega con 90 o más, con todos los componentes en 80 o más. El puntaje no reemplaza la decisión del estudiante.

## 9. Herramientas de verificación (`herramientas/`, en Python, con tests)

1. **`verificar_referencias.py`**
   - Extrae las citas `[@clave]`, `@clave` y `[@clave, p. X]` de los `.qmd`.
   - Error si una clave no existe en `referencias.bib`; advertencia por entradas no citadas.
   - Detecta citas textuales sin número de página.
   - Valida los campos mínimos **según el estilo del perfil** (APA 7 o Vancouver).
   - Resuelve DOI contra Crossref (caché y *rate limit*) y compara título y año con tolerancia difusa; sin DOI, OpenAlex; en perfiles de salud, también PubMed (PMID).
   - Detecta duplicados y, si la fuente lo permite, retractaciones.
   - Modo `--respaldo`: busca en el PDF pasajes que respalden la oración que cita; marca "sin respaldo encontrado" para revisión humana y nunca afirma respaldo por su cuenta.
   - Salida en consola, `registro/verificacion_referencias.md` y JSON; código de salida distinto de 0 si hay errores.
2. **`verificar_cifras.py`**: toda cifra de los capítulos de resultados proviene de `resultados/` mediante inclusión de Quarto; reporta números escritos a mano. En cualitativa, verifica que cada cita de participante exista literalmente en una transcripción anonimizada.
3. **`verificar_estructura.py`**: compara los capítulos con **las secciones, el orden y las denominaciones del perfil activo** y con `requisitos.md`. Solo exige lo que el perfil marca como obligatorio (por ejemplo, la matriz de consistencia **no** es obligatoria en `economia-fce`). Reporta ítems excluidos sin justificación registrada.
4. **`verificar_perfil.py`**: valida cada perfil contra `_esquema.yaml`, exige `fuente` o `[PENDIENTE-NORMATIVA]` en cada campo y bloquea `estado: verificado` si falta el PDF en `normativa/facultades/`.
5. **`registrar_decision.py`** y **`verificar_decisiones.py`**: el primero guarda las respuestas textuales con sello de tiempo y hash; el segundo comprueba que cada etapa completada tenga su decisión aprobada y que el archivo no haya cambiado después del registro.
6. **`similitud_interna.py`**: detecta autoplagio y repeticiones entre capítulos y fragmentos de más de 20 palabras copiados de los PDFs de la biblioteca sin comillas y sin cita.
7. **`entregar.py`**: renderiza con la plantilla del perfil y genera los dos .docx del art. 13 con la nomenclatura exacta. Además:
   - verifica que tablas y ecuaciones sean texto y no imágenes;
   - genera la declaración de uso de IA desde `registro/registro_ia.jsonl`;
   - genera las declaraciones juradas, los formularios del perfil y el checklist del expediente;
   - en tesis grupales, lista a todos los autores y los objetivos asignados a cada uno.
8. **`tablero.py`**: HTML autocontenido con el estado del proyecto.

## 10. Hooks y permisos (`.claude/settings.json` y `.claude/hooks/`)

Implementa según la documentación vigente de hooks de Claude Code (verifícala antes de escribir, incluidos los nombres de eventos disponibles):

- **PreToolUse (Write/Edit/MultiEdit/Bash)**: bloquea la escritura directa en `decisiones/` (solo vía `registrar_decision.py`) y en `datos/crudos/`.
- **Control de etapa**: bloquea el inicio de una etapa si `verificar_decisiones.py` falla para la previa. Como las skills se invocan desde el prompt, evalúa si corresponde un hook de envío de prompt (por ejemplo, `UserPromptSubmit`) además de `PreToolUse`, y documenta la elección.
- **PostToolUse**: añade a `registro/registro_ia.jsonl` la fecha, la herramienta, el archivo y un resumen de la acción.
- **Stop o SessionEnd**: sugiere un commit `[claude] <etapa>: <resumen>`.
- **Pre-commit (git)**: corre `verificar_referencias.py`, `verificar_cifras.py` y `verificar_perfil.py` en modo rápido, y bloquea el commit de archivos con datos personales.
- Permisos de denegación para comandos destructivos y para leer credenciales (Zotero y APIs).

## 11. Proyectos de ejemplo y pruebas

- `ejemplos/economia-cuantitativo/`: tesis de demostración completa con datos abiertos reales y livianos (por ejemplo, series del BCRP o un módulo reducido del INEI), perfil `economia-fce`.
- `ejemplos/medicina-cualitativo/`: proyecto de demostración con perfil `medicina-fm` y enfoque cualitativo, usando **transcripciones sintéticas marcadas como ficticias en cada archivo y en el nombre**, solo para probar el flujo; referencias en Vancouver.
- Todas las decisiones de ejemplo se marcan como ficticias.
- `tests/` con pytest para todas las herramientas, incluidos: citas inexistentes, DOI inválidos, cifras sin respaldo, citas cualitativas que no existen en la transcripción, decisiones incompletas, perfiles sin fuente y secciones fuera de orden según el perfil.
- GitHub Actions: lint (ruff), tests y renderizado de ambos ejemplos a .docx.

## 12. Documentación

- `README.md` para estudiantes sin experiencia en programación: instalación en Windows paso a paso; primer uso; cómo elegir facultad y perfil; flujo de etapas y `/autopiloto`; preguntas frecuentes; límites; responsabilidad del autor según la normativa.
- `docs/guia_asesores.md`: cómo revisar el registro de IA, las decisiones, los informes de verificación y confirmar un perfil no verificado.
- `docs/integridad.md`: qué está permitido y qué no según la directiva, con citas a los artículos, y qué declara exactamente el anexo de uso de IA.
- `docs/agregar_facultad.md`: cómo crear un perfil nuevo a partir de la norma de una escuela, con el checklist de `verificar_perfil.py`.

## 13. Plan de construcción (fases)

1. **Fase 0:** lectura de la normativa general, `requisitos.md` y plan detallado. Espera mi aprobación.
2. **Fase 0b:** relevamiento de estructuras por facultad (sección 3.2): `indice.yaml`, PDFs descargados, esquemas de facto y `comparativo.md`. Espera mi revisión.
3. **Fase 1:** esqueleto, `CLAUDE.md`, `_esquema.yaml`, los tres perfiles de referencia, plantillas Quarto y .docx por perfil, CSL e integración con Zotero.
4. **Fase 2:** herramientas de verificación con tests (incluido `verificar_perfil.py`).
5. **Fase 3:** hooks, registro de IA, control de decisiones y protección de datos.
6. **Fase 4:** skills y agentes de las etapas 0 a 5, incluido el flujo cualitativo.
7. **Fase 5:** skills de las etapas 6 a 10, jurado simulado con rúbrica por perfil y `/autopiloto`.
8. **Fase 6:** ambos ejemplos end-to-end, CI y documentación.
9. **Fase 7 (posterior):** perfiles del resto de facultades, solo con fuente verificada o con confirmación de un asesor de esa escuela.

Al cerrar cada fase: corre los tests, haz un commit, resume lo hecho, lo pendiente y los supuestos, y espera mi confirmación.

## 14. Lo que no debes hacer

- Inventar requisitos normativos, esquemas de facultad, URLs, endpoints, datos, resultados, testimonios o referencias.
- Marcar como `verificado` un perfil derivado de fuentes secundarias, de tesis de ejemplo o de un documento de posgrado aplicado a pregrado.
- Escribir en `decisiones/`, modificar `datos/crudos/` o subir datos personales al repositorio remoto.
- Registrar una decisión que el estudiante no tomó explícitamente, incluso en `/autopiloto`.
- Implementar funciones cuyo objetivo sea reducir artificialmente la similitud o evadir detectores.
- Copiar código de otros repositorios sin verificar su licencia y registrar la atribución.
- Dar por verificada una cita, cifra o requisito que no fue comprobado por una herramienta o por el estudiante.
