# Documentación de `tesis-sanmarcos`

Written for: quien llega al repositorio y no sabe por dónde empezar a leer.

---

## Si eres tesista

Empieza por el [README principal](../README.md): qué hace, cómo se instala y
cuál es el flujo. Después, estos dos, en este orden:

- **[`integridad.md`](integridad.md)** — qué se puede y qué no, con el artículo
  de la norma que lo dice. Si tienes dudas sobre el porcentaje de similitud,
  sobre parafrasear o sobre la declaración de uso de IA, la respuesta está ahí.
- **[`../normativa/requisitos.md`](../normativa/requisitos.md)** — los
  requisitos con documento, artículo y página. Lo que no está ahí, no lo
  sabemos, y el repositorio lo marca como pendiente en lugar de inventarlo.

## Si eres asesor

- **[`guia_asesores.md`](guia_asesores.md)** — qué puedes comprobar en diez
  minutos y sin instalar nada: el registro de uso de IA, el historial de
  decisiones del tesista y los informes de verificación. Incluye las tres
  preguntas que de verdad distinguen a quien entendió su trabajo.

## Si vas a explicarlo a otros

- **[`guion_video.md`](guion_video.md)** — guion de rodaje del video
  introductorio: nueve minutos, qué se ve en pantalla y qué se dice encima,
  con los capítulos para la descripción. Se graba contra los ejemplos, nunca
  contra una tesis real: en cuanto hay captura de pantalla, lo que esté en
  `datos/crudos/` queda publicado.

## Si quieres mejorar el repositorio

- **[`agregar_facultad.md`](agregar_facultad.md)** — cómo corregir el perfil de
  una escuela o verificarlo cuando aparece el documento normativo. Es la
  contribución más útil que existe: cada resolución que se localiza mejora el
  perfil para todos los tesistas de esa facultad.
- **[`../normativa/conflictos.md`](../normativa/conflictos.md)** — las
  contradicciones conocidas entre normas, con las dos posturas y qué hace el
  repositorio con cada una.
- **[`../NOTICE.md`](../NOTICE.md)** — de dónde viene cada cosa de terceros y
  qué licencia tiene, incluido el escudo de la UNMSM.

## Historia del proyecto

- **[`PLAN_IMPLEMENTACION.md`](PLAN_IMPLEMENTACION.md)** — el plan por fases,
  con lo que cada una encontró. Es donde está escrito **por qué** el
  repositorio es como es: los supuestos del encargo que la lectura de la
  normativa corrigió, y los fallos que aparecieron al construirlo.
- **[`prompt_claude_code_tesis_unmsm.md`](prompt_claude_code_tesis_unmsm.md)** —
  la especificación original. Se conserva como documento de partida; donde
  difiere de lo construido, manda lo construido, y el plan dice por qué.
- **[`repositorios_de_referencia.docx`](repositorios_de_referencia.docx)** — los
  repositorios que se revisaron antes de empezar. Sus licencias están
  verificadas en [`NOTICE.md`](../NOTICE.md); dos de ellos no tienen licencia y
  de esos solo se tomaron ideas.

## Cómo está organizado el código

| Carpeta | Qué hay |
|---|---|
| `herramientas/` | Todo el código. Cada módulo es una herramienta con su `--help` |
| `perfiles/` | Un YAML por facultad. `unmsm-general` es la norma base; los demás heredan |
| `plantillas/` | Plantilla .docx y CSL por perfil, y el escudo en `marca/` |
| `.claude/skills/` | Una por etapa del flujo, más cuatro auxiliares |
| `.claude/agents/` | Pares trabajador–crítico, y los tres jurados simulados |
| `normativa/` | Los PDF de las normas, leídos y citados con artículo y página |
| `ejemplos/` | Dos tesis de demostración que el CI verifica y renderiza |
| `tests/` | Las pruebas. Muchas comprueban reglas de criterio, no solo código |
