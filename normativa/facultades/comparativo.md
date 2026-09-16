# Comparativo de estructuras de tesis por facultad — UNMSM

Entregable de la Fase 0b. Relevamiento del 2026-09-16, sobre las 20 facultades
y sus 66 escuelas profesionales.

## Cómo leer las tablas

Cada celda indica **de dónde sale el dato**, porque no todas las facultades
tienen norma propia:

| Marca | Significado |
|---|---|
| **N** | Consta en una norma verificada, con el PDF en `normativa/facultades/` |
| **G** | Rige la norma **general** de la universidad (Anexo 2B de la RR 00744-R-20) porque la facultad no publica una propia |
| *f* | Solo **observación de facto**: derivado de tesis ya sustentadas en Cybertesis. **No es normativo** |
| — | Sin dato |

Una celda *f* nunca habilita `estado: verificado` en un perfil.

## 1. El hallazgo que reordena el problema

La especificación del encargo partía de que "no existe un esquema único" y de
que cada facultad fija el suyo. Eso es cierto solo a medias. El relevamiento
encontró que **la UNMSM sí tiene una estructura de tesis de pregrado aprobada
por resolución rectoral**: los Anexos 2A y 2B de la RR N.° 00744-R-20, páginas
13 y 14.

- **Anexo 2A** fija los preliminares: carátula, numeración romana en minúsculas,
  resumen y abstract de 200 palabras, 5 palabras clave, acta de sustentación,
  dedicatoria y agradecimiento opcionales, e información complementaria
  (DNI, correo del asesor, grupo de investigación, fuente de financiamiento,
  disciplina OCDE, título en inglés o quechua).
- **Anexo 2B** fija el cuerpo, en dos modelos de siete capítulos.
- **§ 6.3** habilita a cada facultad a aprobar su normativa específica y a
  establecer la estructura del cuerpo de sus documentos.

De ahí que el modelo correcto no sea "cada facultad inventa su esquema", sino
**un piso normativo común que algunas facultades especializan**. La Facultad de
Derecho lo confirma de la manera más explícita: su reglamento no define
capítulos y remite a los Anexos 1, 2, 3A y 3B de la directiva general.

### Anexo 2B — los dos modelos

| Cap. | Modelo 1 (cuantitativa) | Modelo 2 (cualitativa) |
|---|---|---|
| I | Introducción | Introducción |
| II | Revisión de literatura | Revisión de literatura |
| III | Hipótesis y variables | Hipótesis y variables (*HipóT o supuestos hipotéticos*) |
| IV | Materiales y métodos | Materiales y métodos |
| V | Resultados | Resultados |
| VI | Discusión | Discusión |
| VII | Conclusiones y recomendaciones | Conclusiones y recomendaciones |

Diferencias internas relevantes: el modelo cuantitativo trae
`III.3 Operacionalización de las variables` y `IV.5 Análisis estadístico`; el
cualitativo los sustituye por `III.2 Sistemas y categorías de análisis`,
`IV.4 Credibilidad de la investigación`, `IV.5 Sujetos de estudio` y
`IV.7 Análisis de datos`.

## 2. Matriz de secciones de primer nivel

`P` presente · `O` opcional · `A` ausente · `→` fusionada con la siguiente

| Facultad | Fuente | Introd. | Rev. literatura | Hipótesis | Métodos | Resultados | Discusión | Concl. |
|---|---|---|---|---|---|---|---|---|
| **Norma general (Anexo 2B)** | **N** | P | P | P | P | P | P | P |
| Medicina | **N** | P | P | condicional | P | P → | → fusionada | P |
| Letras y CC. Humanas | **N** | P | P | P (cuant.) / A (cual.) | P | P | P (solo cual.) | P |
| Ciencias Económicas | **N** (solo proyecto) | P | P (marco teórico) | P, **antes de objetivos** | P | — | — | — |
| Derecho y Cª Política | **G** | P | P | P | P | P | P | P |
| Farmacia y Bioquímica | *f* | P | P | P | P | P | — | P |
| Ingeniería Industrial | *f* | P | P | P | P | P | — | P |
| Ciencias Administrativas | *f* | P | P | P | P | P | — | P |
| Psicología | *f* | P | P (marco teórico) | — | P (Método) | P | — | — |
| Odontología | *f* | P | P (marco teórico) | — | P | — | — | P |
| Medicina Veterinaria | *f* | P | P (rev. bibliográfica) | — | P | — | P | P |
| FIGMMG | *f* | P | P (marco teórico) | P | P | P | P → | — |
| Ing. Sistemas e Informática | *f* | P | P (**Estado del arte**) | — | — | — | P | — |
| Ing. Electrónica y Eléctrica | *f* | P | P | — | — | — | — | — |
| Ciencias Sociales | *f* | P | P (marco teórico) | P | P | — | — | — |
| Educación | *f* | P | P | — | P | — | — | P |
| Ciencias Contables | *f* | P | P | P | P | — | — | — |
| Ciencias Económicas (informe) | *f* | P | P | P | P | — | — | P |
| Ciencias Biológicas | *f* | — | P | P | P | — | — | — |
| Química e Ing. Química | *f* | P | P | — | P | — | — | — |
| Ciencias Físicas | *f* | P | P | — | — | — | — | — |
| Ciencias Matemáticas | *f* | P | P | — | — | — | — | — |

Las filas *f* con muchas celdas vacías no significan que esas tesis carezcan de
metodología: significan que **el índice cosechado no permitió reconocerla de
forma fiable**, por heterogeneidad de títulos de capítulo o por índices que el
extractor no pudo leer. La cifra exacta de tesis legibles por facultad está en
cada `esquema_de_facto.md`.

## 3. Estilo de citas

| Facultad | Estilo | Fuente |
|---|---|---|
| Norma general | "según los estilos de cita-referencia **de acuerdo a las áreas del conocimiento**" | **N** — Anexo 2A, pág. 13 |
| Medicina | **Vancouver** | **N** — RD 002373-2023-D-FM |
| Letras y CC. Humanas | **APA 7.ª ed.** | **N** — RD 000057-2021-D-FLCH, §9 |
| Ciencias Económicas | "normas APPA" *(sic)*, edición no precisada | **N** parcial — guía de la EP |
| Resto | — | Sin norma propia; el perfil debe preguntarlo al asesor |

La norma general **no impone un estilo único**, y eso es exactamente lo que
justifica que el estilo viva en el perfil y no en el motor.

## 4. Formato

| Facultad | Fuente tipográfica | Tamaño | Interlineado | Papel | Fuente del dato |
|---|---|---|---|---|---|
| Letras y CC. Humanas | Arial o Times New Roman | 12 | 1,5 (referencias a espacio simple) | — | **N** |
| Derecho y Cª Política | Arial | 12 | simple | A4 | **N** |
| Resto | — | — | — | — | Sin dato |

Los preliminares en **números romanos minúsculos** son regla general del
Anexo 2A y aplican a todas las facultades. Es el requisito de formato más caro
de implementar y ya está señalado como riesgo técnico en el plan.

## 5. Resumen, hipótesis, ética y autoría

| Aspecto | Qué rige | Fuente |
|---|---|---|
| Resumen | Español e inglés, 200 palabras, 5 palabras clave | **N** general, Anexo 2A |
| Línea de investigación en el resumen | Exigida en Letras | **N** — RD 000057-2021-D-FLCH |
| Hipótesis | Capítulo III del Anexo 2B en ambos modelos; en Medicina "si es pertinente"; en Economía va **antes** de los objetivos | **N** |
| Comité de ética | Obligatorio en Medicina. Odontología tiene comité institucional propio (reglamento 2025). La UNMSM tiene además su Comité de Ética en Investigación (RR 008534-2025-R) | **N** |
| Autoría | Individual o grupal, máximo tres, con objetivos definidos por participante si es grupal | **N** general, §7.2 a) y b) |
| Consentimiento informado | Exigible cuando hay sujetos humanos, por Código de Ética y Ley 29733 | **N** |

## 6. Familias de estructura, revisadas

La especificación proponía siete familias (A–G). El relevamiento las confirma
solo en parte y sugiere esta lectura:

| Familia propuesta | Veredicto del relevamiento |
|---|---|
| **A. Diseño FCE (Economía)** | **Confirmada**, pero acotada: solo regula el **proyecto**. El informe final de Economía se rige por el Anexo 2B. |
| **B. IMRyD clínico (Medicina)** | **Confirmada** con norma verificada. |
| **C. Cualitativa clínica (Medicina)** | **Confirmada** con norma verificada. |
| **D. Cuantitativa clásica en 4–5 capítulos** | **No confirmada como familia propia.** Lo que se observa es el Anexo 2B de siete capítulos. La R.D. 1069-D-FE-2017 de Educación no pudo localizarse. |
| **E. Cualitativa en humanidades y educación** | **Confirmada**, ahora con fuente de **pregrado** (Letras, RD 000057-2021), no de posgrado. |
| **F. Argumentativa o por obra** | **Confirmada de facto** en Letras: las tesis de Arte y Literatura titulan sus capítulos por contenido, sin metodología empírica. Sin norma que la describa explícitamente. |
| **G. Mixta** | **No observada** en la muestra de pregrado. |

Propuesta para la Fase 1: reemplazar el esquema de siete familias por
**una norma general más especializaciones documentadas**. Es más fiel a lo que
dicen los documentos y hace que una facultad sin norma propia no necesite una
"plantilla no normativa" inventada, sino que herede el Anexo 2B.

## 7. Qué queda pendiente

1. **R.D. 1069-D-FE-2017 (Educación)**: no localizada. Sigue como
   `solo_fuente_secundaria`.
2. **Resolución que aprueba la guía de Economía**: no localizada. El perfil
   `economia-fce` no puede ser `verificado` sin ella.
3. **Resolución decanal que aprueba el Reglamento de Grados y Títulos de Derecho**:
   el PDF está firmado pero no se identificó su RD.
4. **15 facultades sin documento de estructura propio.** Antes de crear un
   perfil para cualquiera de ellas hace falta el documento de la escuela o la
   confirmación de un asesor de esa escuela, tal como exige la especificación.
5. **Esquemas de facto de calidad desigual.** De 100 tesis cosechadas, 91
   dieron índice legible; en Medicina Veterinaria solo 2 de 5. Los esquemas de
   Ciencias Biológicas, Físicas y Matemáticas son poco concluyentes y no deben
   usarse para derivar perfiles.

## 8. Método, para poder repetirlo

Las tesis se obtuvieron de Cybertesis por su API DSpace 7.6.2
(`https://cybertesis.unmsm.edu.pe/backend/api`), tomando solo colecciones
`Tesis EP …` de escuelas profesionales —nunca de unidades de posgrado—,
ordenadas por fecha de depósito descendente y filtradas desde 2023. De cada
tesis se descargó el PDF, se extrajo el texto de las primeras 25 páginas, se
localizó el encabezado de índice y se normalizaron los títulos de capítulo.
Los PDF **no** se conservan en el repositorio: cada `esquema_de_facto.md`
guarda el enlace permanente al ítem en Cybertesis.
