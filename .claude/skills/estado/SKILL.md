---
name: estado
description: Dice en qué etapa va la tesis, qué se decidió hasta ahora y qué toca hacer ahora. Pensada para retomar después de semanas sin trabajar.
disable-model-invocation: true
---

# /estado

Responde tres preguntas: **dónde quedé, qué decidí, y qué sigue.**

## Para quién es esto

Para alguien que trabaja y avanza a ritmo irregular. Entre la última sesión y
esta pueden haber pasado dos semanas o cuatro meses. No se acuerda de lo que
decidió y no tiene por qué.

Así que no resumas el repositorio: **recuérdale su tesis.** La diferencia está en
que lo primero describe archivos y lo segundo le devuelve el hilo.

## 1. Reúne

```
uv run python -c "from herramientas import registro_ia; print(registro_ia.etapa_actual())"
uv run python -m herramientas.verificar_decisiones
uv run python -m herramientas.verificar_todo --rapido
```

Y mira cuándo fue la última vez:

```
git log -5 --date=short --format='%ad %s'
```

## 2. Cuéntaselo así

**Primero, su tesis en dos frases.** El tema y la pregunta, como él las decidió,
sacadas de `decisiones/`. Textuales. Es lo que le devuelve el contexto más rápido
que cualquier lista.

**Después, cuánto tiempo pasó.** "Tu última sesión fue el 14 de marzo, hace cinco
semanas." Sin comentarlo. No es un reproche; es orientación.

**Después, el recorrido.** Qué etapas están cerradas con su decisión y en qué
etapa está:

```
hecho       0 iniciar          tema y enfoque
hecho       1 explorar-datos   ENAHO 2019-2023, módulos 1 y 34
hecho       2 afinar-idea      pregunta y estrategia
AQUÍ        3 literatura       18 fuentes en Zotero, sin decisión registrada
pendiente   4 proyecto
...
```

**Después, qué toca ahora.** Una cosa, concreta, que se pueda hacer hoy. No una
lista de nueve. Si la etapa quedó a medias, di en qué quedó a medias.

**Al final, lo que haya que mirar.** Errores de la verificación, si los hay. Y si
hay algo con fecha —el certificado de similitud vence a los 90 días—, eso va
arriba, no abajo.

## 3. Los trámites son información

Si hay algo administrativo pendiente, se dice como dato: "para el expediente hace
falta X". **Nunca como condición para seguir trabajando.**

Nada de lo que esté pendiente en una secretaría impide avanzar en la tesis. Si te
descubres escribiendo "primero necesitas…", bórralo y escribe qué puede hacer hoy.

## 4. El tablero, si lo quiere ver

```
uv run python -m herramientas.tablero --abrir
```

Un HTML que se abre con doble clic, sin conexión. Útil para mirarlo con el asesor
o para volver en dos meses.

## Tono

Es un profesional que terminó su carrera. Nada de "¡vamos, tú puedes!" ni de
explicarle qué es una tesis. Dale el estado, lo que falta y lo que puede hacer
hoy.

Si lleva mucho tiempo parado, no lo menciones como un problema. Dile dónde quedó
y qué es lo siguiente. Eso es lo que ayuda a volver.

## Qué NO hacer aquí

- Inventar una etapa como cerrada si no tiene decisión registrada.
- Convertir un trámite en un requisito para avanzar.
- Dar una lista de nueve tareas en lugar de la siguiente.
- Reprochar el tiempo que pasó.
