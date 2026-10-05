---
name: checkpoint
description: Guarda el avance en un commit propio con el mensaje del repositorio y deja la sesión en un punto del que se pueda volver.
disable-model-invocation: true
---

# /checkpoint

Cierra la sesión de forma que se pueda retomar en seis semanas.

## Por qué existe

Porque las sesiones se interrumpen. Un checkpoint hecho a tiempo es la diferencia
entre volver y seguir, o volver y no saber qué estaba a medias.

## 1. Mira qué cambió

```
git status
git diff --stat
```

Si hay algo en `datos/crudos/` o cualquier cosa con datos personales, **para
aquí**. Eso no se versiona. Comprueba:

```
uv run python -m herramientas.datos_personales <archivo>
```

## 2. Comprueba antes de guardar

```
uv run python -m herramientas.verificar_todo --rapido
```

Si hay errores, dilos. No bloquean el checkpoint —guardar el avance a medias es
mejor que perderlo— pero quedan anotados para la próxima sesión.

## 3. Commit

Uno por etapa o por borrador, con el mensaje del repositorio:

```
[claude] <etapa>: <resumen>
```

El resumen dice **qué quedó distinto**, no qué se hizo. "catalogo: de 19 a 33
fuentes" sirve; "actualizaciones varias" no sirve para nada dentro de dos meses.

Si en la sesión se registró una decisión, el commit la menciona.

## 4. Deja la nota de retorno

Lo más útil del checkpoint. En `registro/retomar.md`, sobrescribiendo:

```markdown
# Dónde quedamos — 2026-03-14

## Etapa
literatura (3 de 10)

## Qué quedó hecho
18 fuentes en Zotero con metadatos completos; la síntesis por discusiones
escrita en borrador.

## Qué quedó a medias
Falta decidir qué lecturas son centrales. Las tres candidatas están en
`registro/literatura_candidatas.md`.

## Lo primero que hay que hacer al volver
Leer esas tres y elegir. Son unos veinte minutos.

## Lo que hay que mirar
`verificar_referencias` da 2 errores: dos citas textuales sin número de página,
en `capitulos/02-literatura.qmd`.
```

Escrita para alguien que no se acuerda de nada. "Lo primero que hay que hacer al
volver" es una sola cosa y se puede hacer en una sesión corta.

## 5. Dilo en una línea

Qué se guardó, en qué commit y qué sigue. El tesista cierra la laptop sabiendo
que no perdió nada.

## Qué NO hacer aquí

- Commitear `datos/crudos/` o datos personales.
- Dejar un mensaje de commit que no diga qué cambió.
- Bloquear el checkpoint porque la verificación da errores.
- Escribir `retomar.md` suponiendo que el tesista recuerda el contexto.
- Hacer `git push` sin que el tesista lo pida.
