# Estilos de cita (CSL)

Archivos descargados el **2026-09-16** del proyecto Citation Style Language.
Todos bajo **CC BY-SA 3.0**; la atribución está en `NOTICE.md`.

| Archivo | Estilo | Identificador | Formato | Perfiles que lo usan |
|---|---|---|---|---|
| `apa.csl` | APA Style 7th edition | `zotero.org/styles/apa` | autor-fecha | `letras-flch`, `economia-fce` |
| `vancouver.csl` | NLM/Vancouver: Citing Medicine 2nd edition (citation-sequence) | `zotero.org/styles/nlm-citation-sequence` | numérico | `medicina-fm` |
| `locales-es-ES.xml` | Localización al español | — | — | todos |

## Dos precisiones sobre lo que se descargó

**1. No existe un `apa-es.csl`.** La especificación del proyecto lo pedía con ese
nombre, pero el proyecto CSL no publica una variante española de APA. El español
se obtiene con `apa.csl` **más** el archivo de localización `locales-es-ES.xml`,
que traduce los elementos generados por el estilo ("y", "et al.", "ed.",
"recuperado de", los nombres de los meses). Por eso aquí el archivo se llama
`apa.csl` y el perfil apunta a él.

En el `_quarto.yml` que genera `herramientas/activar_perfil.py` esto se traduce
en dos claves que deben ir juntas:

```yaml
csl: plantillas/csl/apa.csl
lang: es
```

Sin `lang: es`, la bibliografía sale en inglés aunque el texto esté en español.

**2. El estilo Vancouver se sirve hoy bajo el nombre NLM.** La URL
`zotero.org/styles/vancouver` entrega el estilo cuyo identificador interno es
`nlm-citation-sequence`, titulado "NLM/Vancouver: Citing Medicine 2nd edition".
Es el estilo Vancouver vigente, con formato de cita numérico, que es lo que exige
el reglamento de la Facultad de Medicina (RD N.° 002373-2023-D-FM, anexos C a F:
"Referencias bibliográficas según normas de Vancouver"). Se conserva el nombre de
archivo `vancouver.csl` por claridad para el estudiante, y se deja constancia
aquí de que su identificador difiere.

## Cómo actualizarlos

Los estilos CSL cambian. Para rehacer la descarga:

```
https://www.zotero.org/styles/apa
https://www.zotero.org/styles/vancouver
https://raw.githubusercontent.com/citation-style-language/locales/master/locales-es-ES.xml
```

Después de actualizar, corre las pruebas de `tests/` que comparan una
bibliografía de referencia: un cambio de estilo puede alterar la salida sin que
nadie lo note.

## Agregar un estilo para otra facultad

Varios perfiles tienen `estilo_citas: [PENDIENTE-NORMATIVA]` porque ni su
facultad ni la norma general fijan uno; el Anexo 2A de la RR N.° 00744-R-20 dice
que las referencias van "según los estilos de cita-referencia de acuerdo a las
áreas del conocimiento".

Cuando el asesor confirme un estilo:

1. Descarga el `.csl` de `zotero.org/styles/<nombre>` a esta carpeta.
2. Anótalo en la tabla de arriba y en `NOTICE.md` con su licencia.
3. Apunta el perfil a él en su campo `csl:` y cambia `estilo_citas`.
4. Registra la confirmación del asesor como decisión del estudiante.
