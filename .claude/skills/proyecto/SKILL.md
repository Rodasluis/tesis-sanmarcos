---
name: proyecto
description: Redacta el proyecto de tesis con las secciones, el orden y las denominaciones exactas del perfil activo, con sus anexos. Es la etapa 4 del flujo.
disable-model-invocation: true
---

# /proyecto — etapa 4

El primer documento que sale del repositorio. Es el que la escuela revisa e
inscribe, así que la estructura importa tanto como el contenido.

## 1. Marca la etapa y comprueba que hay con qué

```
uv run python -c "from herramientas import registro_ia; registro_ia.marcar_etapa('proyecto')"
uv run python -m herramientas.verificar_decisiones --exigir-hasta afinar-idea
```

Si faltan decisiones, **no bloquees en silencio**: dile cuál falta y por qué
hace falta, y resuélvanlo conversando. Un proyecto escrito sobre una pregunta
que nadie eligió es un proyecto que no se puede defender.

## 2. Lee el perfil, literalmente

```
uv run python -c "from herramientas.perfiles import cargar_de, perfil_activo; import pathlib; p=cargar_de(pathlib.Path('.'), perfil_activo()); print(p.get('proyecto'))"
```

El perfil manda sobre tu costumbre. En concreto:

- **Las denominaciones son las de la norma.** Si dice «Definición y planteamiento
  del problema», no escribas «Planteamiento del problema».
- **El orden es el de la norma.** En `economia-fce` la hipótesis va **antes** de
  los objetivos. No lo "corrijas".
- **Los anexos obligatorios son los que dice el perfil, y solo esos.** La guía de
  Economía no pide matriz de consistencia ni cronograma: no los reclames. El
  reglamento de Medicina sí exige cronograma, presupuesto y recursos: ahí son
  obligatorios.

Si el perfil no define secciones de proyecto, usa el orden del informe final
reducido a propuesta, y dilo.

## 3. Escribe

Cada sección sale de lo que ya está decidido y en disco, no de lo que suene bien:

| Sección | De dónde sale |
|---|---|
| Planteamiento del problema | decisión de `/afinar-idea` + vacíos de `/literatura` |
| Objetivos | la pregunta decidida, desagregada |
| Hipótesis | la decisión, si el perfil la exige |
| Marco teórico | síntesis de `notas/lecturas/`, con citas de `referencias.bib` |
| Metodología | datos reales de `resultados/`: muestra, variables, cobertura |
| Cronograma y presupuesto | si el perfil los exige |

Reglas al redactar:

- **Toda cifra sale de `resultados/`** por una expresión de Quarto, nunca
  escrita a mano.
- **Toda afirmación lleva cita** o va marcada `[VERIFICAR]`.
- Persona gramatical y estilo de citas: los del perfil.
- Describe la muestra con los números que tienes, no con los que te gustaría.

Las secciones del proyecto van a **`proyecto/`**, no a `capitulos/`. Son dos
documentos distintos: `proyecto/` es lo que la escuela registra y aprueba, y
`capitulos/` es la tesis. Nombres con número de orden por delante
(`01-planteamiento.qmd`), para que el orden no dependa del nombre.

## 3 bis. Genera el documento

El proyecto no se queda en Markdown: se entrega.

```
uv run python -m herramientas.entregar_proyecto
```

Produce, en `entregables/PROYECTO/`, el **.docx y el PDF** del proyecto, con la
carátula oficial —escudo de la UNMSM, facultad, escuela, título, «PROYECTO DE
TESIS», autor, asesor y año— tomada de las carátulas de las tesis publicadas en
Cybertesis.

El .docx es lo que se entrega y lo que la escuela devuelve con observaciones; el
PDF es lo que se imprime o se adjunta sin que se descoloque nada. Son el mismo
documento.

Los datos de la carátula salen de `entregables/datos_de_entrega.yaml`. Si falta
alguno, la herramienta **avisa y genera igual**: el proyecto sale incompleto y se
completa, no se bloquea.

## 4. Anexos

Según lo que exija el perfil:

- **Consentimiento informado**, si hay personas participantes. Obligatorio en
  Medicina. Debe decir qué se hará con los datos, que se anonimizarán y que la
  participación es voluntaria y revocable (Ley N.° 29733; Código de Ética,
  art. 12).
- **Cronograma y presupuesto**, obligatorios en Medicina.
- **Matriz de consistencia y operacionalización**: recomendados en general,
  obligatorios solo si el perfil lo dice.
- **Instrumentos**: cuestionario o guía de entrevista, si los hay.

Si el perfil exige **comité de ética** —Medicina—, prepara el expediente para
el comité y dile al tesista que ese trámite tarda, para que lo empiece ya.

## 5. Ítems excluidos

Algunos perfiles permiten excluir secciones con justificación. La guía de
Economía lo dice expresamente. Si el tesista quiere excluir algo:

1. Que diga por qué, con sus palabras.
2. Regístralo como decisión.
3. `verificar_estructura.py` lo reconocerá y bajará el error a aviso.

## 6. Comprueba

```
uv run python -m herramientas.verificar_estructura --detalle
uv run python -m herramientas.verificar_referencias
uv run python -m herramientas.verificar_cifras
```

## 7. Pide la crítica

`critico-redaccion` para coherencia entre pregunta, método y objetivos, y para
el estilo del perfil. `critico-perfil` para comprobar que la estructura es
realmente la que la norma exige.

## 8. Punto de decisión

Decisión: **aprobación del proyecto**, con los ítems excluidos y sus
justificaciones.

Preguntas de comprensión: por qué este método y no otro; qué limita lo que vas a
poder concluir.

Registra con etapa `proyecto`.

## Lo que viene después, y conviene decirle

El proyecto se **inscribe en el registro** de la escuela
(RR N.° 00744-R-20, §7.2 d). En algunas facultades tiene **vigencia**: en
Medicina caduca al año, prorrogable seis meses por única vez, y vencido se anula
de oficio. Si el perfil declara vigencia, díselo ahora y deja que `/estado` se lo
recuerde.

## Qué NO hacer aquí

- No cambies el orden ni las denominaciones del perfil porque te parezcan mejor.
- No exijas anexos que el perfil no pide.
- No escribas una metodología que no se corresponde con los datos que hay.
- No condiciones el avance a que alguien externo confirme nada.
