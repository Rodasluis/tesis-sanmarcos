# `video/` — el video de los pasos

Written for: quien quiera regenerar o corregir el video introductorio.

Composición de [HyperFrames](https://hyperframes.heygen.com): HTML con
animaciones seekables que se renderiza a MP4 con Chrome headless y FFmpeg, en
local. Dura 2:03 y cubre los siete bloques de `docs/guion_video.md`.

```
npx hyperframes check      # lint, layout, contraste, movimiento
npx hyperframes snapshot --at 22,58,96   # PNG de esos segundos, para mirarlos
npx hyperframes render     # MP4 a .hyperframes/
```

Requiere Node 22+ y FFmpeg (`winget install Gyan.FFmpeg.Essentials`).

> **`render` termina con código 0 aunque no genere nada.** Si FFmpeg no está en
> el PATH, imprime «FFmpeg is required to encode video», sale bien y no deja
> archivo. Comprueba siempre que el `.mp4` exista antes de darlo por hecho.
> En Windows, winget deja los ejecutables en
> `%LOCALAPPDATA%\Microsoft\WinGet\Links`, y el PATH no cambia en las
> terminales que ya estaban abiertas.

## Qué es y qué no es

**Es una ilustración de los pasos, no una captura de pantalla.** Esa distinción
manda sobre todo lo demás y explica cada decisión del diseño:

- Nada imita una ventana de Word ni una terminal. Los comandos se ven como
  tipografía monoespaciada sobre el fondo, no dentro de un marco que finja ser
  una consola.
- **Ninguna salida de comando aparece en el video.** No se ve lo que imprime
  `entregar.py`, porque eso solo se puede mostrar de verdad grabando una
  ejecución de verdad. Para eso está el screencast de `docs/guion_video.md`.
- Todo string que sale en pantalla viene del repositorio: los comandos existen,
  el patrón de nombre de archivo es el que produce `entregar.py`, las cifras de
  perfiles salen de `perfiles/` y las de saturación de
  `ejemplos/medicina-cualitativo/resultados/saturacion.csv`.
- La gráfica de saturación lleva impreso **«ejemplo del repositorio ·
  transcripciones ficticias»**, porque esos datos son material de prueba y
  presentarlos como investigación sería justo lo que el principio 1 prohíbe.

No lleva el escudo de la UNMSM. El escudo va en la carátula de una tesis porque
la norma lo pide ahí; ponerlo en un video de un repositorio de terceros lo haría
parecer institucional, y no lo es.

## El silencio es deliberado

`check` avisa `film_silent`: un video de más de 15 s sin pista de audio. Se
mantiene así a propósito, por dos razones:

1. Una pista musical es material de terceros con su licencia, y entraría en
   `NOTICE.md` como cualquier otra cosa. No vale la pena para esto.
2. La narración correcta de este video ya está escrita, bloque por bloque, en
   `docs/guion_video.md`. Quien lo doble con su voz o con un TTS tiene el texto;
   la pista se agrega como un `<audio>` y se vuelve a renderizar.

## Estructura

| Archivo | Bloque del guion | Entra en |
|---|---|---|
| `compositions/situacion.html` | 1 — qué es y para quién | 0 s |
| `compositions/instalacion.html` | 2 — instalación | 13 s |
| `compositions/perfil.html` | 3 — el perfil de tu escuela | 33 s |
| `compositions/flujo.html` | 4 — `/iniciar` y el punto de decisión | 49 s |
| `compositions/entrega.html` | 5 — los dos .docx del art. 13 | 69 s |
| `compositions/limites.html` | 6 — lo que no hace | 89 s |
| `compositions/cierre.html` | 7 — cierre | 110 s |

`index.html` es la raíz: la paleta, las fuentes y los siete hosts. Cada escena
va en su archivo, dentro de `<template>`, con su propia línea de tiempo
registrada en `window.__timelines`.

## Si cambias el repositorio, revisa el video

Lo que queda desactualizado primero, en orden: la URL del repositorio en
`cierre.html` e `instalacion.html`, el número de perfiles que heredan la norma
general en `perfil.html`, los once comandos de `flujo.html`, y la resolución
citada en `entrega.html`. Todo eso tiene su fuente en el repositorio; contrástalo
contra ella y no contra la versión anterior del video.

## Sobre `AGENTS.md`

Lo escribió `hyperframes init` y es la guía del proveedor para agentes: los
comandos, el contrato de render y sus reglas. Se conserva tal cual.

El mismo comando dejó también un `CLAUDE.md` idéntico en esta carpeta, y ese se
quitó. Un archivo de instrucciones de un tercero dentro de este repositorio se
cargaría como si fueran las reglas del proyecto, y las reglas del proyecto son
las del `CLAUDE.md` de la raíz. El contenido no se perdió: es el mismo que
`AGENTS.md`.
