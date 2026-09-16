# Plan de implementación — `tesis-sanmarcos`

Respuesta a la sección 1 del prompt: plan por fases, estructura de archivos, dependencias y riesgos.
**No he escrito código todavía.** Este documento espera tu aprobación.

Fecha: 2026-09-16

---

## 1. Estado verificado del entorno

Todo lo de esta tabla lo comprobé ejecutando comandos; no es supuesto.

| Elemento | Estado | Detalle |
|---|---|---|
| Carpeta de trabajo | **No vacía, sin git** | Contiene solo `prompt_claude_code_tesis_unmsm.md`. `git rev-parse` falla: no hay repositorio. |
| `normativa/` | **No existe** | Ninguno de los 8 documentos de la sección 2 está presente. |
| `normativa/facultades/` | **No existe** | Ningún esquema de facultad colocado. |
| Git | OK | 2.54.0.windows.1 |
| Python | OK **con matiz** | 3.11.3, accesible solo como `py -3`. El `python` del PATH es el stub de Microsoft Store y no ejecuta nada. |
| `uv` | **Falta** | Requerido por la sección 5. |
| Quarto | **Falta** | Requerido: es el motor de render a .docx. |
| Pandoc | **Falta** | Quarto trae el suyo, pero conviene tenerlo para diagnóstico. |
| Zotero + Better BibTeX | **Falta / no detectado** | Sin él no hay `referencias.bib` ni claves estables. |
| R / Rscript | Falta | No es necesario si el análisis es en Python. |

### Documento de facultad encontrado (fuera de la carpeta)

Encontré y **leí** `C:\Users\rodas\Downloads\Tesis de Educación en pandemia\documentos\PAUTAS PARA SUSTENTACION DE TESIS.docx`.
Su contenido corresponde al documento de la Escuela de Economía descrito en la sección 3.4: índice con Definición y Planteamiento del Problema → Formulación de Hipótesis → Objetivos → Marco Teórico → Metodología → Esquema tentativo → Bibliografía → Anexos; introducción con antecedentes e importancia; permiso explícito de excluir ítems con justificación; bibliografía en orden alfabético según "normas APPA" (así, con esa errata, en el original).

Advertencias sobre ese archivo, relevantes para el perfil:

- Son **37 párrafos**; es una guía breve, no una resolución.
- **No contiene número de resolución, fecha, firma ni código de verificación.** Por eso el perfil `economia-fce` no puede nacer como `estado: verificado` en el sentido del prompt (la sección 14 prohíbe marcar verificado sin norma). Propongo `estado: documento_en_mano` y buscar la resolución decanal que lo respalda.
- El nombre del archivo dice "sustentación", pero el contenido regula el **diseño/proyecto**, no la sustentación. Es una discrepancia que registraré en `perfiles/_notas_normalizacion.md`.
- No indica edición de APA → `[PENDIENTE-NORMATIVA]`, con APA 7 como valor operativo, tal como indica el prompt.

**No encontré** ninguno de los documentos generales (RR 000947-2026-R, RR 01827-R-17, RR 00744-R-2020, RR 012648-2023-R, CONCYTEC, RR 008449-2025-R, Ley 29733, RENATI/Cybertesis) ni la RD N.° 002373-2023-D-FM de Medicina.

---

## 2. Consecuencia: la Fase 0 está bloqueada

La sección 2 exige extraer cada requisito **con documento, artículo y página**. Sin los PDF eso no se puede hacer sin inventar, y la sección 14 lo prohíbe expresamente. Las cifras que el propio prompt menciona (umbral 0–20 %, art. 13, art. 7.2) tampoco puedo darlas por buenas: son precisamente lo que hay que verificar contra el documento.

Tres caminos, y necesito que elijas uno:

- **A — Yo busco y descargo la normativa** de fuentes oficiales (`*.unmsm.edu.pe`, `spsgd.unmsm.edu.pe`, CONCYTEC, SUNEDU) y guardo cada PDF en `normativa/`. Requiere acceso web. Es lo que la sección 3.2 pide de todos modos para el relevamiento.
- **B — Tú colocas los PDF** en `normativa/` y yo arranco la extracción. Más lento para ti, máxima fidelidad.
- **C — Avanzo a Fase 1** (esqueleto, motor, herramientas) con todo requisito normativo marcado `[PENDIENTE-NORMATIVA]`, y la normativa entra después. El motor no depende del contenido de la norma; solo los perfiles.

Mi recomendación: **A + C en paralelo**. La búsqueda de normativa es lenta y con riesgo de no encontrarlo todo; el esqueleto y las herramientas no dependen de ella.

---

## 3. Plan por fases

Cada fase indica entregables, de qué depende, cómo se cierra y qué puede salir mal. Al cerrar cada una: tests, commit, resumen y espera de tu confirmación (sección 13).

### Fase 0 — Normativa general y `requisitos.md`
- **Entregables:** los 8 documentos en `normativa/` (PDF/DOCX originales); `normativa/requisitos.md` con una fila por requisito: documento, artículo, página, texto literal citado y requisito derivado; `normativa/conflictos.md` creado; `normativa/_no_encontrados.md` con lo que no aparezca.
- **Depende de:** la decisión A/B/C de la sección 2 de este plan.
- **Cierre:** cada requisito tiene fuente o está marcado `[PENDIENTE-NORMATIVA]`; ninguno sin una de las dos cosas.
- **Riesgos:** (i) resoluciones no publicadas o tras inicio de sesión; (ii) la RR 000947-2026-R es de 2026 y puede tener modificatorias posteriores — hay que verificar vigencia, no solo existencia; (iii) PDF escaneados sin capa de texto → haría falta OCR, que añade dependencia (tesseract) y riesgo de transcripción errónea.

### Fase 0b — Relevamiento de las 20 facultades
- **Entregables:** `normativa/facultades/indice.yaml` (20 facultades, escuelas, documento, resolución, fecha, URL, nivel, estado); PDF descargados por facultad; `esquema_de_facto.md` donde no haya norma (≥5 tesis de Cybertesis de los últimos 3 años, con enlaces); `normativa/facultades/comparativo.md`.
- **Depende de:** Fase 0 y acceso web.
- **Cierre:** tu revisión. **No creo perfiles nuevos** más allá de los tres de referencia hasta que la apruebes (sección 3.2.5).
- **Riesgos:** es la fase más larga y la de peor relación esfuerzo/certeza. Mi expectativa honesta: bastantes escuelas quedarán en `no_encontrado` o `solo_fuente_secundaria`. Segundo riesgo: confundir norma de posgrado con pregrado (el prompt ya avisa del caso Letras). Tercero: `estado` inflado; lo controla `verificar_perfil.py`, que bloquea `verificado` sin PDF en disco.

### Fase 1 — Esqueleto, perfiles y plantillas
- **Entregables:** árbol de la sección 6; `CLAUDE.md` con los 8 principios; `README.md`; `LICENSE` (MIT); `NOTICE.md`; `pyproject.toml` con `uv`; `perfiles/_esquema.yaml`; `economia-fce.yaml`, `medicina-fm.yaml`, `generico-cualitativo.yaml`; `plantillas/<perfil>/referencia.docx`; `plantillas/csl/apa-es.csl` y `vancouver.csl`; `_quarto.yml` generado desde el perfil activo; integración Zotero → `referencias.bib`.
- **Depende de:** Fases 0 y 0b para el **contenido** de los perfiles; no para el esqueleto.
- **Cierre:** `verificar_perfil.py` (adelantado de la Fase 2) valida los tres perfiles contra el esquema.
- **Riesgos técnicos, los más serios del proyecto:**
  - **Numeración romana en preliminares y arábiga desde la introducción.** Quarto→docx no lo hace de forma nativa; exige saltos de sección de Word. Plan: post-procesar con `python-docx` / manipulación del XML en `entregar.py`. Es trabajo real, no un parámetro de configuración.
  - **Márgenes asimétricos** (p. ej. 3,5 cm izquierdo en Letras) van en la plantilla `referencia.docx`, que hay que construir, no descargar.
  - **CSL:** `apa-es` y `vancouver` vienen del repositorio oficial de CSL (CC BY-SA); hay que verificar licencia y anotarla en `NOTICE.md`.
  - **Zotero MCP:** el prompt pide verificar las instrucciones vigentes de `54yyyu/zotero-mcp` antes de documentarlo. Lo dejaré **opcional**; el camino obligatorio será la auto-exportación de Better BibTeX, que no depende de terceros.

### Fase 2 — Herramientas de verificación + tests
- **Entregables:** las 8 herramientas de la sección 9 en `herramientas/`, cada una con tests en `tests/`.
- **Depende de:** Fase 1 (esquema de perfiles y estructura de carpetas).
- **Cierre:** `pytest` en verde, incluidos los casos adversos de la sección 11.
- **Riesgos:**
  - **Crossref / OpenAlex / PubMed:** límites de tasa y caídas. Mitigación: caché en disco, backoff y un modo `--sin-red` que degrada a advertencia en vez de error, para que el CI no dependa de la red.
  - **`--respaldo`** (buscar en el PDF el pasaje que respalda la cita) es la función con mayor riesgo de falso negativo. La diseño para que **solo** marque "sin respaldo encontrado" y nunca afirme respaldo, tal como exige el prompt.
  - **`similitud_interna.py` no sustituye a Turnitin** y no puede estimar el porcentaje oficial. Lo documentaré explícitamente para que nadie lo lea como un "voy 12 %".
  - `verificar_cifras.py` depende de que los resultados se inserten por inclusión de Quarto; si el estudiante pega un número a mano, se reporta. Es lo buscado, pero generará fricción real de uso.

### Fase 3 — Hooks, registro de IA y protección de datos
- **Entregables:** `.claude/settings.json`; hooks `PreToolUse`, `PostToolUse`, `Stop`/`SessionEnd`; hook de control de etapa; `.gitignore` y hook de pre-commit que bloquea datos personales; `registro/registro_ia.jsonl`.
- **Depende de:** Fase 2 (`verificar_decisiones.py`).
- **Riesgos:** los nombres y el contrato de los eventos de hooks **hay que verificarlos contra la documentación vigente** antes de escribirlos (el prompt lo exige). Un hook mal formado puede bloquear la sesión del estudiante; por eso todos fallarán "abierto" salvo los tres que deben fallar "cerrado": escritura en `decisiones/`, escritura en `datos/crudos/` y commit con datos personales.

### Fase 4 — Skills y agentes, etapas 0–5
`/iniciar`, `/explorar-datos`, `/afinar-idea`, `/literatura`, `/proyecto`, `/analizar`, con sus pares trabajador-crítico.
- **Riesgos:** `herramientas/fuentes/catalogo.yaml` exige **verificar cada URL y endpoint**; los de INEI y MEF cambian con frecuencia y varios no tienen API estable → quedarán como descarga manual documentada. Los umbrales 80/85/90 son juicio de un modelo, no una medición: los documentaré como semáforo orientativo, nunca como sustituto de la decisión del estudiante.

### Fase 5 — Skills y agentes, etapas 6–10
`/redactar`, `/jurado`, `/verificar`, `/entregar`, `/sustentacion`, `/autopiloto`, más `/estado`, `/asesor`, `/checkpoint`.
- **Riesgos:** `/entregar` concentra toda la complejidad de Word (los dos archivos del art. 13, nomenclatura exacta, tablas y fórmulas como texto). `/autopiloto` es el punto donde es más fácil violar el principio 3 (registrar una decisión no tomada): lo implemento de modo que `registrar_decision.py` **exija** una respuesta explícita y falle si no la hay.

### Fase 6 — Ejemplos end-to-end, CI y documentación
Los dos ejemplos, GitHub Actions (ruff + pytest + render de ambos ejemplos a .docx) y `docs/`.
- **Riesgos:** el CI necesita Quarto y pandoc en el runner (existe acción oficial de Quarto). Las transcripciones sintéticas de Medicina deben estar marcadas como ficticias **en el nombre del archivo y dentro de cada archivo**, para que nunca puedan confundirse con datos reales.

### Fase 7 — Resto de facultades
Solo con fuente verificada o confirmación de un asesor de esa escuela. Posterior a todo lo demás.

---

## 4. Estructura de archivos objetivo

La de la sección 6 del prompt, sin cambios, más estas adiciones que el texto implica pero no lista:

```
docs/                     # guia_asesores.md, integridad.md, agregar_facultad.md (sección 12)
.github/workflows/ci.yml  # sección 11
.gitignore                # datos/crudos/, *.env, credenciales
normativa/_no_encontrados.md
perfiles/_notas_normalizacion.md
herramientas/fuentes/catalogo.yaml
```

Los nombres de `capitulos/` los genera `/proyecto` desde el perfil y el esquema capitular aprobado; no se fijan aquí.

---

## 5. Dependencias

**Instalar antes de la Fase 1:** `uv`, Quarto, Zotero + Better BibTeX. (`winget` está disponible; puedo hacerlo yo si lo autorizas.)

**Ya presente:** Git 2.54, Python 3.11.3 (vía `py -3`).

**Python:** pyyaml, python-docx, requests, pandas, pytest, ruff; jinja2 para plantillas; rapidfuzz para comparación difusa de títulos; pypdf o pdfplumber para `--respaldo`.

**Servicios externos:** Crossref, OpenAlex, Semantic Scholar, PubMed. Todos con caché y modo sin red.

**Atribución obligatoria en `NOTICE.md`:** inspiración de diseño en `hugosantanna/clo-author` (MIT, sin fork) y las licencias de los CSL.

---

## 6. Riesgos transversales

| Riesgo | Impacto | Mitigación |
|---|---|---|
| La normativa no aparece completa | Perfiles con huecos | `[PENDIENTE-NORMATIVA]` visible en el documento generado, no silencioso |
| Perfil marcado `verificado` sin respaldo | Falla el principio central del repositorio | `verificar_perfil.py` bloquea `verificado` si no existe el PDF en disco |
| Word: numeración y secciones | `/entregar` no cumple el formato | Post-proceso con `python-docx`; probarlo en Fase 1, no en Fase 5 |
| Turnitin no es accesible | Falsa sensación de cumplimiento | Documentar que `similitud_interna.py` **no** estima el porcentaje oficial |
| APIs caídas o con límite de tasa | CI rojo, flujo detenido | Caché, backoff, modo `--sin-red` |
| Datos personales subidos al repositorio | Incumple la Ley 29733 | `.gitignore` + hook de pre-commit que bloquea el commit |
| `/autopiloto` registra decisiones no tomadas | Rompe la autoría declarada bajo juramento | Respuesta explícita obligatoria; sin ella, error |
| Alcance total muy grande | Entrega parcial | Cierre por fases con tests y commit; cada fase deja algo utilizable |

---

## 7. Lo que necesito de ti

1. **Aprobación de este plan** (sección 1 del prompt: no empiezo a programar sin ella).
2. **Cómo obtengo la normativa:** camino A, B o C de la sección 2.
3. **Dónde vive el repositorio:** `git init` aquí mismo, o en una subcarpeta `tesis-sanmarcos/`.
4. **Si instalo** `uv`, Quarto y pandoc con `winget`.
5. **Si uso el `PAUTAS PARA SUSTENTACION DE TESIS.docx`** que encontré en otra carpeta de Descargas como fuente del perfil `economia-fce` (copiándolo a `normativa/`, sin mover el original).
