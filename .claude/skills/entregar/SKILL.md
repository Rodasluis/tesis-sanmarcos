---
name: entregar
description: Genera los dos .docx con la nomenclatura exacta del art. 13, las declaraciones y el checklist del expediente. Es la etapa 9 del flujo.
disable-model-invocation: true
---

# /entregar — etapa 9

Convierte la tesis en los archivos que la facultad acepta, con los nombres y las
carpetas que exige la norma.

## Lo que la norma pide, literalmente

La Directiva de originalidad (RR N.° 000947-2026-R), art. 13 apartado A, pide
**dos archivos .docx** con nombres exactos, en dos carpetas:

```
entregables/
  TEXTO/
    Apellidos Nombres - Desarrollo Título - Año.docx
    Apellidos Nombres - Protocolo y Complemento Título - Año.docx
  DOCUMENTO/
    checklist_expediente.md
    declaracion_jurada_pids.md
    declaracion_uso_de_ia.md
```

Tres cosas que se olvidan y devuelven el expediente:

- **El entregable es .docx.** El PDF no sirve, aunque se vea mejor.
- **Las tablas y las fórmulas van como texto**, no como imágenes. Una tabla
  pegada como captura es, además, la falta del art. 30 c).
- **Los nombres son los de arriba**, con los apellidos del bachiller y el título
  tal como aparece en la carátula.

## 1. Marca la etapa y comprueba antes de generar

```
uv run python -c "from herramientas import registro_ia; registro_ia.marcar_etapa('entregar')"
uv run python -m herramientas.entregar --comprobar
```

`--comprobar` revisa sin escribir nada: que estén los datos de entrega, que el
.docx no tenga tablas como imagen, que la numeración de páginas esté bien.
Córrelo primero, siempre.

Si faltan los datos del tesista, se completan en
`entregables/datos_de_entrega.yaml`. Los nombres de archivo salen de ahí tal
cual, así que se escriben como deben aparecer: con tildes, con los dos
apellidos, con el título completo.

## 2. Genera

```
uv run python -m herramientas.entregar
```

Hace cuatro cosas: reparte los capítulos entre los dos .docx, los renderiza con
la plantilla del perfil activo, arregla la numeración —romanos en preliminares,
árabigos desde la introducción, que es lo que pide el Anexo 2A— y escribe las
declaraciones y el checklist.

## 3. Mira los .docx de verdad

Ábrelos. El render puede salir sin error y quedar mal, y esto es lo último que
pasa antes de que lo lea un jurado. Comprueba:

- La carátula tiene todo lo que pide el perfil: escudo, facultad, escuela, la
  fórmula "Tesis para optar al título profesional de…", el nombre del bachiller y
  el del asesor, mes y año.
- La numeración cambia de romanos a árabigos **en la introducción**, no antes ni
  después.
- El resumen y el abstract no pasan de 200 palabras, y hay 5 palabras clave y 5
  keywords.
- Las tablas son tablas. Las fórmulas son texto.
- La bibliografía trae solo lo citado en el texto, que es lo que dice el Anexo 2B.

## 4. Las dos declaraciones no son lo mismo

**La declaración jurada del Anexo 4 sí es un requisito.** Es la autorización para
evaluar la tesis en PIDS, y va en el expediente.

**La declaración de uso de IA no la exige ninguna norma leída** (está en
`normativa/requisitos.md`, P-01). Se genera desde `registro/registro_ia.jsonl`
como medida voluntaria de transparencia, apoyada en el art. 5 del Código de
Ética. Dísela al tesista así: existe, describe con exactitud en qué ayudó Claude,
y **él decide si la presenta**. No le digas que tiene que entregarla.

## 5. El checklist del expediente

`DOCUMENTO/checklist_expediente.md` lista los trámites de la facultad del perfil
activo. Es **información**, no una puerta: el tesista llegó hasta aquí sin que
nadie le pidiera un papel y así se queda.

Lo que sí hay que avisarle, porque tiene fecha:

- **El certificado de similitud vence a los 90 días** (art. 19). Si se vence, hay
  que repetir el trámite.
- **Desde la segunda revisión, PIDS cuesta S/ 20.** Vale la pena que la primera
  salga bien.
- El umbral es **0 % a 20 %**, medido en PIDS. Nada de lo que corre en este
  repositorio mide ese número.

Si el perfil no está `verificado`, dilo aquí: los requisitos pueden diferir y el
checklist es lo mejor que tenemos, no la verdad oficial. La fuente de verdad es
la secretaría de su facultad.

## 6. Punto de decisión

Decisión: **conformidad con lo que se va a entregar**.

- Enséñale las rutas de los dos .docx y las declaraciones.
- Dile explícitamente qué va a firmar y qué no es obligatorio.
- Preguntas de comprensión: en qué formato se entrega y por qué no PDF; qué pasa
  si el certificado de similitud vence.

Registra con etapa `entregar`.

## Qué NO hacer aquí

- Presentar la declaración de uso de IA como un requisito.
- Convertir una tabla o una fórmula en imagen para que "entre mejor". Es la falta
  del art. 30 c).
- Inventar un requisito de la facultad que no esté en `normativa/requisitos.md`.
- Decir que la tesis "pasa" el umbral de similitud. No lo sabemos.
- Firmar o declarar nada por el tesista.
