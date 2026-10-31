# `video/` — el video de los pasos

Written for: quien quiera regenerar o corregir el video que va en el README.

Composición de [HyperFrames](https://hyperframes.heygen.com): HTML con
animaciones seekables que se renderiza a MP4 con Chrome headless y FFmpeg, en
local. Dura 1:48 y cubre los siete bloques de `docs/guion_video.md`, en
lenguaje llano y sobre una ventana dibujada que recrea una aplicación de
escritorio.

```
npx hyperframes check                     # lint, layout, contraste, movimiento
npx hyperframes snapshot --at 14,32,62    # PNG de esos segundos, para mirarlos
npx hyperframes render                    # MP4 en renders/
```

Requiere Node 22+ y FFmpeg (`winget install Gyan.FFmpeg.Essentials`).

> **`render` termina con código 0 aunque no genere nada.** Si FFmpeg no está en
> el PATH, imprime «FFmpeg is required to encode video», sale bien y no deja
> archivo. Comprueba siempre que el `.mp4` exista antes de darlo por hecho.
> En Windows, winget deja los ejecutables en
> `%LOCALAPPDATA%\Microsoft\WinGet\Links`, y el PATH no cambia en las
> terminales que ya estaban abiertas.

## Qué es: una recreación con contenido real

La ventana —barra de título, lateral con los comandos, paneles de chat y de
terminal— es dibujada, y el video lo dice en una esquina durante todo el
metraje. Lo que aparece **dentro** de esa ventana no se inventó:

- Las salidas de `instalar_hooks --comprobar`, `/verificar` y `/entregar` son
  las que imprimieron las herramientas sobre el ejemplo
  `medicina-cualitativo`, línea por línea. Lo único alterado es la ruta local
  del intérprete, abreviada con «…».
- Los nombres de los dos .docx son los que produjo `entregar.py` para ese
  ejemplo, completos.
- Las tres opciones de `/iniciar` y la respuesta del tesista son las de
  `ejemplos/medicina-cualitativo/decisiones/00_iniciar.md`, marcadas
  `FICTICIO` allí. La respuesta corta previa («Medicina Humana… ocho
  entrevistas») resume datos del mismo ejemplo; es la única línea del tesista
  que no es cita literal.
- Los archivos que «se generan» en la escena de etapas son los que existen en
  `ejemplos/medicina-cualitativo/`, con sus nombres reales.

Lo que no hay: salidas inventadas, cifras que ninguna herramienta produjo, ni
el escudo de la UNMSM. El escudo va en la carátula de una tesis porque la norma
lo pide ahí; en un video de un repositorio independiente lo haría parecer
institucional.

## El silencio es deliberado

`check` avisa `film_silent`. Se mantiene: una pista musical es material de
terceros con su licencia, y la narración correcta ya está escrita, bloque por
bloque, en `docs/guion_video.md`. Quien lo doble con su voz o con un TTS tiene
el texto; la pista se agrega como un `<audio>` y se vuelve a renderizar.

## Estructura

| Archivo | Qué muestra | Entra en |
|---|---|---|
| `compositions/inicio.html` | título y una frase | 0 s |
| `compositions/instalar.html` | terminal: clonar, `uv sync`, `instalar_hooks --comprobar` | 7 s |
| `compositions/iniciar.html` | chat: `/iniciar`, tres opciones, la decisión guardada | 22 s |
| `compositions/etapas.html` | cinco comandos y los archivos que generan | 42 s |
| `compositions/entrega.html` | terminal: `/verificar` y `/entregar` con sus salidas | 66 s |
| `compositions/limites.html` | lo que no hace, en tres frases | 88 s |
| `compositions/cierre.html` | cierre y URL | 101 s |

`index.html` es la raíz: la paleta, las fuentes, la ventana dibujada y los
siete hosts. Cada escena va en su archivo, dentro de `<template>`, con su
línea de tiempo registrada en `window.__timelines`.

## Cómo llega al README

GitHub recorta el autoplay de los `<video>` en Markdown, así que el README
incrusta una **imagen animada** con `<img>`, como hace el propio repositorio de
HyperFrames, y enlaza el MP4 debajo. Las dos se generan desde `renders/`:

```
ffmpeg -i renders/<render>.mp4 -vf "fps=12,scale=960:-1" -loop 0 -quality 60 tesis-sanmarcos.webp
cp renders/<render>.mp4 tesis-sanmarcos.mp4
```

Los dos archivos de la raíz de `video/` sí se versionan, con nombre estable;
`renders/` y `.hyperframes/` no. Se vuelven a commitear cuando el video cambie
de verdad, no en cada prueba: cada versión queda en el historial de git para
siempre.

## Si cambias el repositorio, revisa el video

Lo que queda desactualizado primero: la URL en `cierre.html` e `instalar.html`,
los comandos del lateral en `index.html`, las salidas de `/verificar` y
`/entregar` en `entrega.html` si cambian los informes, y los nombres de archivo
del ejemplo en `etapas.html`. Todo tiene su fuente en el repositorio;
contrástalo contra ella, no contra la versión anterior del video.

## Sobre `AGENTS.md`

Lo escribió `hyperframes init` y es la guía del proveedor para agentes. Se
conserva tal cual. El mismo comando dejó un `CLAUDE.md` idéntico, y ese se
quitó: un archivo de instrucciones de un tercero dentro de este repositorio se
cargaría como si fueran las reglas del proyecto, y las reglas del proyecto son
las del `CLAUDE.md` de la raíz.
