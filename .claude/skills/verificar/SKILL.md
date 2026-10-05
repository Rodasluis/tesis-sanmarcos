---
name: verificar
description: Corre todas las comprobaciones sobre la tesis y resume qué falta, con puntaje por componente. Es la etapa 8 del flujo.
disable-model-invocation: true
---

# /verificar — etapa 8

Corre todo lo comprobable y ordena lo que falta.

## 1. Marca la etapa y corre

```
uv run python -c "from herramientas import registro_ia; registro_ia.marcar_etapa('verificar')"
uv run python -m herramientas.verificar_todo --detalle
```

Con red, para comprobar que las referencias existen de verdad en Crossref,
OpenAlex y PubMed:

```
uv run python -m herramientas.verificar_todo --con-red --detalle
```

La corrida con red es la que importa antes de entregar. Sin red, las citas solo
se comprueban contra `referencias.bib`, que puede estar mal.

## 2. Qué mira cada componente

| Componente | Qué comprueba | Error típico |
|---|---|---|
| Perfil y normativa | que el perfil sea coherente y diga sus fuentes | perfil `verificar` sin confirmar |
| Decisiones | una por etapa, aprobada, con el sello intacto | etapa saltada |
| Citas y referencias | que cada cita exista y cada textual tenga página | cita que no está en el `.bib` |
| Cifras | que todo número del texto esté en `resultados/` | cifra escrita a mano |
| Estructura | las secciones que pide el perfil, en su orden | sección faltante |
| Similitud interna | repeticiones y fragmentos sin citar | párrafo copiado de la biblioteca |

## 3. Lo que el puntaje no es

Los umbrales —80 para commit, 85 para pasar de etapa, 90 para entregar— son un
semáforo de este repositorio. **No son una nota, no son normativos y no los pone
la universidad.** Preséntalos así.

Dos cosas que hay que decirle al tesista aunque no pregunte:

**Un componente sin material no vale 100.** Sale como `--`, no entra en el
promedio y bloquea los umbrales. Una tesis vacía no tiene errores; eso no la
acerca a estar lista.

**`similitud_interna.py` no es Turnitin.** Compara el texto consigo mismo y con
los PDF que el tesista tenga en su biblioteca local. El 0 % a 20 % que exige la
Directiva de originalidad (RR N.° 000947-2026-R) se mide en la plataforma PIDS de
la universidad, y **no hay forma de conocer ese número desde aquí**. Un informe
limpio de esta herramienta no anticipa el resultado de PIDS. Dilo cada vez.

## 4. Ordena lo que falta

No vuelques la salida cruda. Agrupa:

1. **Errores**, que impiden entregar. Para cada uno: el archivo, la línea y qué
   hacer concretamente.
2. **Avisos**, que conviene mirar.
3. **Lo que ninguna herramienta puede comprobar** y sigue pendiendo: si la
   pregunta vale la pena, si la discusión es honesta, si las conclusiones se
   sostienen. Para eso están `/jurado` y el asesor.

Ese tercer grupo se nombra siempre. Es donde está lo que de verdad decide una
sustentación, y es justo lo que un informe en verde invita a olvidar.

## 5. Arregla lo arreglable

De los errores, muchos los puedes corregir tú: una página que falta en una cita
textual, una sección fuera de orden, una cifra que hay que insertar desde
`resultados/`.

Dos que **no** se arreglan solos:

- **Una cita que no existe.** No se cambia por otra que sí exista: se quita la
  afirmación o se busca de verdad la fuente, con el tesista, y se agrega a Zotero
  con su aprobación.
- **Una cifra que no está en `resultados/`.** No se escribe el número a mano: se
  vuelve a `/analizar` y se genera.

## 6. Punto de decisión

Decisión: **qué correcciones se hacen antes de entregar**.

- Presenta la lista con el estado de cada componente.
- Recomienda corregir todos los errores. En los avisos, di cuáles valen la pena.
- Preguntas de comprensión: qué significa el número de similitud interna y qué
  **no** significa; qué comprobación de esta lista no la hace ninguna
  herramienta.

Registra con etapa `verificar`.

## Qué NO hacer aquí

- Presentar el puntaje como una nota, una aprobación o un pronóstico de PIDS.
- Decir que la similitud interna "equivale" al reporte de Turnitin.
- Tocar el texto para bajar la similitud: lo prohíbe el art. 30 de la Directiva
  de originalidad y es el principio 6.
- Marcar como verificado algo que no comprobó una herramienta o el tesista.
- Pasar por alto un error porque "el puntaje ya alcanza".
