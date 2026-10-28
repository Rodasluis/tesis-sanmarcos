# Agregar o corregir el perfil de una facultad

Written for: quien quiera que el repositorio conozca bien la norma de su escuela
—el tesista, su asesor, o alguien que contribuya al proyecto.

---

Las 20 facultades de la UNMSM ya tienen perfil. Este documento es para dos
casos:

1. **Corregir uno**, porque su escuela pide algo distinto de lo que el perfil
   dice.
2. **Verificar uno**, porque consiguió el documento normativo que faltaba.

El segundo caso es el más valioso. Cuatro facultades tienen norma propia
verificada; las demás heredan la estructura general de la universidad. Cada
resolución que aparece mejora el perfil para todos los tesistas de esa escuela.

## Antes de empezar: qué es un perfil

Un archivo YAML en `perfiles/` que dice, para una facultad: qué estructura tiene
la tesis, cómo se llaman sus secciones y en qué orden, qué estilo de citas se
usa, qué formato, qué exige la sustentación.

Lo que un perfil **no** define, lo **hereda** de `unmsm-general.yaml`, que
implementa los Anexos 2A y 2B de la RR N.° 00744-R-20. Esa es la regla que evita
inventar: un campo que la norma de su facultad no menciona no se rellena con lo
que parezca razonable, se deja sin definir y se hereda.

```
unmsm-general.yaml          <- los Anexos 2A y 2B. Norma de toda la universidad.
    |
    +-- medicina-fm.yaml    <- redefine solo lo que su reglamento cambia
    +-- letras-flch.yaml
    +-- ...
```

## Los tres estados, y por qué importan

El campo `estado` es lo más importante del archivo, porque dice **cuánto se puede
confiar en él**.

| Estado | Qué significa | Qué hace falta para llegar ahí |
|---|---|---|
| `verificado` | La norma propia de la facultad está leída y el documento está en `normativa/` | Un documento con rango normativo y su número de resolución |
| `verificar` | Hay un documento, pero no acredita rango normativo | — |
| `solo_fuente_secundaria` | Lo que sabemos viene de una fuente que no es la norma | — |
| `hereda_general` | La facultad no tiene norma propia conocida; usa la general | — |

Tres cosas que **nunca** habilitan `verificado`, y hay comprobaciones que lo
impiden:

- **Un esquema de facto.** Mirar diez tesis de Cybertesis y ver qué estructura
  usan es material de contraste útil, y no es la norma. El campo
  `esquema_de_facto` existe para eso y la herramienta rechaza el perfil si se usa
  para justificar `verificado`.
- **Un documento de posgrado aplicado a pregrado.** Son reglamentos distintos.
- **Que un asesor lo diga de palabra.** Por bien informado que esté. Si su asesor
  dice que su escuela pide otra cosa, eso **sí** cambia el perfil —ver más
  abajo— pero no lo marca como verificado, porque entonces dejaríamos de poder
  distinguir lo que consta de lo que alguien recordó.

## Caso 1: su escuela pide algo distinto

El más común, y el más fácil. No hace falta documento ni resolución.

Dígaselo a Claude en sesión: «en mi escuela el capítulo se llama Marco teórico,
no Revisión de literatura», o «nos piden Vancouver». Se ajusta el perfil y **queda
registrado como una decisión suya**, con sus palabras, en `decisiones/`.

El perfil no pasa a `verificado` por eso, y usted no tiene que esperar a nadie
para seguir trabajando. Si después aparece el documento, se verifica.

## Caso 2: tiene el documento normativo

Aquí sí se puede llegar a `verificado`, y vale la pena hacerlo bien.

### 1. Compruebe que el documento sirve

Tres preguntas, en orden:

- **¿Tiene número de resolución?** Un «instructivo» o unas «pautas» sin
  resolución pueden ser el documento que la escuela usa en la práctica, y aun así
  no acreditan rango normativo. Eso fue exactamente el caso de la guía de
  Economía: se conserva como documento complementario del perfil, pero el
  perfil hereda la norma general.
- **¿Es de pregrado?** Muchas facultades tienen reglamento de posgrado y es otra
  cosa.
- **¿Está vigente?** Busque si una resolución posterior la derogó.

Si las tres respuestas son sí, siga. Si alguna es no, el perfil puede mejorar
igual, pero su estado será `verificar` y no `verificado`.

### 2. Guarde el documento

En `normativa/facultades/<facultad>/`, con el nombre del archivo indicando la
resolución. El perfil tiene que apuntar a un archivo que exista en disco: hay una
comprobación que falla si no está.

### 3. Escriba el perfil

Copie el de una facultad parecida y **borre todo lo que su norma no diga**. Es la
parte contraintuitiva: un perfil bueno es corto. Si el reglamento de su facultad
solo cambia el estilo de citas y la estructura del informe final, el archivo tiene
esas dos cosas y nada más.

Lo mínimo:

```yaml
id: miescuela-fx
facultad: "Facultad de Algo"
escuelas: ["Escuela Profesional de Algo"]
nivel: pregrado
hereda_de: unmsm-general
estado: verificado

fuente:
  documento: >-
    Reglamento de grados y títulos de la Facultad de Algo
  norma: RR N.° 00000-D-FX-2024
  fecha: 2024-05-20
  pagina: "7-9"
  url: https://...
  archivo_local: normativa/facultades/algo/RR_00000-D-FX-2024.pdf
  estado: verificado

# Y a partir de aquí, SOLO lo que su norma cambia respecto de la general.
estilo_citas: vancouver
csl: plantillas/csl/vancouver.csl
```

Cada campo normativo debe poder responder «¿de dónde sale esto?». La herramienta
lo comprueba: si un campo no resuelve por herencia y tampoco declara fuente,
avisa.

Si el estado no es `verificado`, agregue `advertencias_al_tesista` explicando qué
no sabemos. Así el tesista lo sabe en `/iniciar` y no en la sustentación.

### 4. Compruébelo

```
uv run python -m herramientas.verificar_perfil miescuela-fx
```

Revisa unas veinte cosas: que el YAML sea válido, que el `id` coincida con el
nombre del archivo, que lo declarado como `verificado` tenga documento en disco,
que no se apoye en un esquema de facto ni en una norma de posgrado, que resuelva
algún modelo de informe final.

Y el crítico, que mira si el perfil es **fiel** a la norma que dice representar:

```
# en sesión con Claude
lanza el agente critico-perfil sobre perfiles/miescuela-fx.yaml
```

### 5. La plantilla .docx

Si su facultad tiene formato propio —márgenes, tipografía, interlineado—:

```
uv run python -m herramientas.plantilla_docx --perfil miescuela-fx
```

Genera `plantillas/miescuela-fx/referencia.docx` desde lo que el perfil declara.
Si el perfil no define formato, se hereda y no hace falta plantilla propia.

### 6. Pruébelo de punta a punta

Actívelo y renderice algo:

```
uv run python -m herramientas.activar_perfil miescuela-fx
quarto render
```

Si quiere ver cómo queda un proyecto completo con ese perfil, los dos ejemplos de
`ejemplos/` sirven de molde.

## Qué no hacer

Casi todo lo que puede ir mal en un perfil es una variante de rellenar un hueco:

- **Inventar un campo** porque el perfil parece incompleto. Si la norma no lo
  dice, se hereda; y si no hay nada que heredar, se marca
  `[PENDIENTE-NORMATIVA]`, que es información y no un defecto.
- **Copiar los campos de otra facultad** para que no queden vacíos. Dos
  facultades distintas tienen normas distintas.
- **Marcar `verificado`** sin el documento en disco.
- **Usar `esquema_de_facto`** para justificar una decisión de estructura. Es
  material de contraste.
- **Mezclar la práctica con la norma.** Si su escuela hace algo que el reglamento
  no dice, eso va en `esquema_de_facto` o en una decisión registrada, no en el
  campo normativo.

## Si contribuye al repositorio

Un commit por perfil, con el documento normativo incluido, y en el mensaje: qué
facultad, qué resolución, qué campos cambian respecto de la general y qué quedó
en `[PENDIENTE-NORMATIVA]`.

Si el documento tiene licencia o condiciones de redistribución, anótelas en
`NOTICE.md`.
