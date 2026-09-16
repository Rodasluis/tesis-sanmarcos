# NOTICE — atribuciones y verificación de licencias

`tesis-sanmarcos` se publica bajo licencia MIT. Este archivo registra el origen de todo lo que
proviene de terceros y el resultado de verificar su licencia **antes** de reutilizarlo.

Licencias verificadas el **2026-09-16** consultando la API de GitHub y, cuando hizo falta, el
archivo `LICENSE` del propio repositorio. Una licencia puede cambiar: si vas a reutilizar código,
vuelve a comprobarla.

## 1. Repositorios de referencia

| Repositorio | Licencia verificada | Qué se puede hacer |
|---|---|---|
| [`hugosantanna/clo-author`](https://github.com/hugosantanna/clo-author) | **Ninguna** — no hay archivo de licencia en el repositorio | **Solo ideas de diseño. No se copia código.** |
| [`mronkko/claude-academic-research`](https://github.com/mronkko/claude-academic-research) | MIT | Reutilizable con atribución |
| [`Pekosann/thesis-pipeline`](https://github.com/Pekosann/thesis-pipeline) | MIT (el `LICENSE` es MIT; GitHub lo clasifica como `NOASSERTION` porque el archivo incorpora avisos de terceros) | Reutilizable con atribución, conservando también los avisos de su `NOTICE.md` |
| [`ccam80/thesis-writer`](https://github.com/ccam80/thesis-writer) | **Ninguna** — no hay archivo de licencia en el repositorio | **Solo ideas de diseño. No se copia código.** |
| [`ambarja/template-tesis-unmsm-geografica`](https://github.com/ambarja/template-tesis-unmsm-geografica) | CC0-1.0 (dedicación al dominio público) | Reutilizable sin condiciones; se atribuye por cortesía. Ver la salvedad del §1.1 |
| [`54yyyu/zotero-mcp`](https://github.com/54yyyu/zotero-mcp) | MIT | Integración opcional; se documenta, no se copia |

### Corrección respecto de la especificación del encargo

La especificación describe `hugosantanna/clo-author` como MIT. **No lo es**: a la fecha de
verificación el repositorio no declara licencia alguna ni contiene archivo `LICENSE`, lo que en
derecho de autor significa que todos los derechos quedan reservados. En consecuencia:

- de `clo-author` se toma **únicamente la arquitectura conceptual** de pares trabajador-crítico,
  puntajes de calidad y simulación de revisión, que son ideas y no expresión protegida;
- **no** se copia, adapta ni traduce ninguno de sus archivos, prompts, plantillas ni scripts;
- lo mismo se aplica a `ccam80/thesis-writer`, que tampoco declara licencia.

Si en el futuro cualquiera de los dos adopta una licencia permisiva, podrá revisarse esta decisión.

### 1.1 Salvedad sobre `template-tesis-unmsm-geografica`

La dedicación CC0 cubre la obra del autor del repositorio, no necesariamente lo que este
**empaqueta** de terceros. El repositorio incluye la extensión Quarto `nmfs-opensci/titlepage` y
tipografías Qualitype con su propio `COPYING-QUALITYPE`. De ese repositorio se toma:

- la **estructura** de `plan-de-tesis-unmsm.qmd` y `tesis-unmsm.qmd` como referencia de cómo se
  organiza una tesis sanmarquina en Quarto;
- **no** se toma la extensión LaTeX de portada ni las tipografías empaquetadas, porque
  `tesis-sanmarcos` produce `.docx` y no los necesita.

El escudo de la UNMSM es un signo distintivo de la universidad. Se usa en la carátula de la tesis
porque la propia carátula institucional lo exige, no como parte de la licencia del repositorio.

## 2. Qué se toma de cada uno y qué no

### `hugosantanna/clo-author` — ideas, sin código
**Se toma:** el patrón de par trabajador-crítico con crítico sin permiso de escritura; la noción de
puntaje de calidad por componente como semáforo; la idea de simular revisión por pares antes de la
entrega, que aquí se convierte en `/jurado`.
**No se toma:** su orientación a artículos de revista en inglés, su salida LaTeX, su supuesto de R
como lenguaje de análisis, ni sus perfiles de revistas. Aquí el destino es una tesis de pregrado en
español, en `.docx`, con perfiles de facultad en lugar de perfiles de revista.

### `mronkko/claude-academic-research` — MIT
**Se toma:** la regla de que toda cita nace anclada a Zotero, con clave de Better BibTeX y consulta
verificable contra la fuente, y la eliminación de afirmaciones sin respaldo. Es el antecedente
directo del principio 2 de `CLAUDE.md` y de `verificar_referencias.py`.
**Se adapta:** todo el flujo pasa al español y a los perfiles de facultad de la UNMSM.
**Pendiente de verificar:** el encargo menciona un endpoint local de Better BibTeX por JSON-RPC en
`localhost:23119`. Se comprobará contra la documentación vigente de Better BibTeX antes de
escribir código que dependa de él; hasta entonces, el camino obligatorio será la auto-exportación
del `.bib` a disco, que no depende de que Zotero esté abierto.

### `Pekosann/thesis-pipeline` — MIT
**Se toma:** el esquema de capítulos en Markdown con citas de Zotero, la redacción en paralelo con
subagentes y su verificador de citas como punto de partida de `verificar_referencias.py`.
**Se adapta:** su compilación con Pandoc apunta a un documento único; aquí la salida debe ser el
`.docx` **dividido en dos archivos** del art. 13 de la RR 000947-2026-R, con la nomenclatura y la
estructura de carpetas `TEXTO/` y `DOCUMENTO/` que esa norma fija. Si se reutiliza código, se
conservan su aviso de copyright y los avisos de su `NOTICE.md`.

### `ccam80/thesis-writer` — ideas, sin código
**Se toma:** la idea de aprobar un plan de capítulo antes de redactarlo y la de restringir las citas
a la biblioteca Zotero del usuario. Es el antecedente de los puntos de decisión en sesión.
**No se toma:** su supuesto de que el usuario redacta en colaboración. Aquí Claude redacta y el
estudiante decide, revisa y aprueba.

### `ambarja/template-tesis-unmsm-geografica` — CC0-1.0
**Se toma:** la estructura de plan de tesis y de tesis de la UNMSM en Quarto, y los elementos de
forma sanmarquinos como referencia para las carátulas.
**No se toma:** su salida LaTeX/PDF ni el esquema de Ingeniería Geográfica. Ese esquema, además,
solo sería válido para un perfil de esa escuela y únicamente si se acredita la norma que lo
respalda; un repositorio de plantilla **no** es fuente normativa (ver `normativa/requisitos.md`).

### `54yyyu/zotero-mcp` — MIT
**Se toma:** se documenta como integración **opcional** para búsqueda en la biblioteca y lectura de
anotaciones de PDF en el modo `--respaldo` de `verificar_referencias.py`.
**Condición:** el repositorio debe funcionar completo sin él. Sus instrucciones de instalación se
verificarán contra su documentación vigente antes de documentarlas.

## 3. Otros componentes de terceros

| Componente | Origen | Licencia | Estado |
|---|---|---|---|
| Estilos CSL (`apa-es`, `vancouver`) | repositorio oficial de CSL | CC BY-SA 3.0 | Pendiente de incorporar en Fase 1 |
| Quarto | Posit | MIT | Dependencia externa, no se redistribuye |
| Pandoc | John MacFarlane | GPL-2.0-or-later | Dependencia externa, no se redistribuye |

## 4. Documentos normativos

Los PDF de `normativa/` son normas de la UNMSM, del CONCYTEC, de la SUNEDU y del Estado peruano.
Se conservan como documentos de referencia, con su fuente registrada en `normativa/requisitos.md`.
No forman parte del software ni se cubren con la licencia MIT de este repositorio.
