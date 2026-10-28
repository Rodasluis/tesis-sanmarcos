---
name: sustentacion
description: Prepara la defensa — diapositivas, guion, banco de preguntas y ensayo cronometrado, con los tiempos y la rúbrica del perfil activo. Es la etapa 10 del flujo.
disable-model-invocation: true
---

# /sustentacion — etapa 10

Prepara el día. La tesis ya está escrita; lo que falta es que el tesista la
defienda hablando.

## 1. Marca la etapa y lee los tiempos reales

```
uv run python -c "from herramientas import registro_ia; registro_ia.marcar_etapa('sustentacion')"
uv run python -m herramientas.perfiles --mostrar sustentacion
```

Todo lo que sigue depende de esos tiempos. **No asumas veinte minutos.** Si el
perfil dice `[PENDIENTE-NORMATIVA]`, dile al tesista que lo confirme en su
facultad y prepara con un tiempo supuesto, declarado como supuesto.

Donde la norma lo fija, es estricta. Medicina (RD N.° 002373-2023-D-FM, arts. 33 y
34): 15 a 20 minutos de exposición, hasta 20 de preguntas, el asesor delibera con
voz pero sin voto, y la rúbrica reparte 20 puntos así:

| Criterio | Puntos |
|---|---|
| Coherencia entre aspectos metodológicos | 4 |
| Originalidad y validez científica | 3 |
| Fluidez y dominio del tema durante la exposición | 5 |
| Uso de medios y materiales audiovisuales | 3 |
| Solvencia y seguridad al absolver las preguntas | 5 |

Mira dónde están los puntos: **10 de 20 se ganan hablando** —fluidez y
respuestas—, no en el texto. Eso decide cómo se reparte el tiempo de preparación.
Si el perfil activo trae rúbrica, enséñasela al tesista: tiene derecho a saber
con qué lo van a calificar.

La escala general (Reglamento de Grados y Títulos, art. 14): 11 aprueba, 16 a 18
mención honrosa, 19 y 20 máximos honores.

## 2. Diapositivas

Para el tiempo que diga el perfil, no más. Con 15 minutos, unas 12 o 14
diapositivas; con 20, hasta 18. Una diapositiva por minuto es el límite real.

El orden que funciona:

1. Carátula: título, nombre, asesor, facultad.
2. El problema, en una frase y con un dato.
3. La pregunta y los objetivos.
4. Lo que ya se sabía y el hueco que llena esta tesis. Una sola.
5. Método: diseño, datos, muestra.
6. Resultados: **las tablas y figuras que ya están en `resultados/`**, no versiones
   nuevas.
7. Discusión: qué significa y contra qué literatura.
8. Limitaciones. Esta diapositiva se pone porque el jurado la va a preguntar; que
   esté dicha antes es mejor que tener que admitirla después.
9. Conclusiones, una por objetivo.
10. Cierre.

Cada cifra sale de `resultados/`. Una diapositiva es texto de la tesis: el
principio 1 vale igual aquí.

Van en `sustentacion/diapositivas.qmd`, en Quarto, y el PDF o PPTX se renderiza
desde ahí.

## 3. Guion

En `sustentacion/guion.md`, por diapositiva: qué se dice y en cuántos segundos.

Escrito para **leerse en voz alta**. Frases cortas. Sin subordinadas de tres
líneas. Si el tesista tiene que respirar en medio de una frase, la frase está
mal.

Marca las tres frases que no pueden faltar aunque se le vaya el tiempo: la
pregunta, el resultado principal y la conclusión.

## 4. Banco de preguntas

Parte de `resultados/banco_preguntas.yaml`, que dejó `/jurado`. Agrégale:

- Las preguntas de comprensión de todas las etapas, que están en `decisiones/`.
  **Las que el tesista contestó flojo son las más probables.** Están registradas
  textualmente: úsalas.
- Las observaciones de `/jurado` que se decidió **no** atender. Cada una es una
  pregunta esperando.
- Las limitaciones que el propio texto declara.

Agrupa por tipo —método, tema, forma— y marca las cinco más probables.

De cada una, el tesista prepara **su** respuesta. Tú ofreces el material de
apoyo: dónde está el dato en la tesis, qué dice la tabla de robustez. La respuesta
la dice él, con sus palabras, y se guarda con sus palabras.

## 5. Ensayo

Dos rondas, y la primera cronometrada de verdad.

**Primera: la exposición completa**, con el tiempo del perfil corriendo. Después
dile:

- cuánto se pasó o le faltó;
- en qué diapositiva se le fue el tiempo;
- qué dijo que no se entiende sin haber leído la tesis;
- qué cifra dijo mal.

**Segunda: preguntas.** Diez del banco, empezando por las fáciles y subiendo.
Cuando no sepa una, no se la contestes todavía: anótala, acaba la ronda y
repásenlas juntos. Interrumpir para dar la respuesta enseña menos que dejarlo
atascarse.

Tres cosas que se practican aparte, porque son las que más puntos cuestan:

- **"No lo sé" dicho bien.** "Eso no lo midió este estudio; con estos datos no
  puedo afirmarlo" es una respuesta correcta y el jurado la respeta. Inventar una
  respuesta es lo peor que puede pasar en esos veinte minutos.
- **La pregunta que ataca el resultado.** No se defiende subiendo la voz: se
  responde con la tabla de robustez.
- **La pregunta hostil.** A veces el jurado presiona para ver si el tesista
  sostiene lo que escribió. Se sostiene lo que los datos dicen, y se concede lo
  que no.

## 6. Lo práctico

Dilo aunque parezca menor, porque es lo que arruina sustentaciones:

- Llevar las diapositivas en dos formatos y en dos sitios (USB y correo).
- Saber si es presencial o virtual, y probar el equipo antes.
- Llevar la tesis impresa o en pantalla, para buscar un dato si lo piden.
- Saber cuántos miembros tiene el jurado y cómo se les trata.

## 7. Punto de decisión

Decisión: **la versión final de diapositivas y guion**.

- Enséñale las dos cosas y el resultado del ensayo cronometrado.
- Dile sin suavizar qué partes todavía no sostiene bien.
- Preguntas de comprensión: cuál es el resultado principal, en una frase; cuál es
  la limitación más seria y cómo la va a reconocer; qué va a decir si le preguntan
  algo que la tesis no midió.

Registra con etapa `sustentacion`.

## Qué NO hacer aquí

- Prometer una nota, o decir que "ya está listo para aprobar".
- Poner en una diapositiva una cifra que no esté en `resultados/`.
- Escribir respuestas para que el tesista las memorice sin entenderlas: en la
  pregunta de seguimiento se cae.
- Registrar como suya una respuesta que redactaste tú.
- Inventar los tiempos, la composición del jurado o la rúbrica.
- Esconder una limitación para que la exposición quede más redonda.
