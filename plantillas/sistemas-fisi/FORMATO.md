# Formato aplicado — `sistemas-fisi`

- Facultad: Facultad de Ingeniería de Sistemas e Informática
- Estado del perfil: `hereda_general`
- Fuente del formato: (sin documento propio de facultad localizado en el relevamiento de la Fase 0b)

## Valores con los que se generó `referencia.docx`

| Parámetro | Valor |
|---|---|
| Papel | A4 |
| Tipografía | Times New Roman |
| Cuerpo | 12 pt |
| Interlineado | 1.5 |
| Margen superior | 2.5 cm |
| Margen inferior | 2.5 cm |
| Margen izquierdo | 3.0 cm |
| Margen derecho | 2.5 cm |

## Atención: valores que NO vienen de una norma

La norma aplicable a este perfil no fija los siguientes puntos. Se
aplicaron valores operativos para poder maquetar. **No son requisitos.**
Si tu escuela pide otra cosa, se cambia en el perfil y se vuelve a
generar la plantilla:

- tipografía: Times New Roman (valor operativo; la norma no la fija)
- cuerpo: 12 pt (valor operativo)
- interlineado: 1.5 (valor operativo)
- márgenes: 2,5 cm salvo el izquierdo, 3,0 cm para encuadernación (valores operativos; la norma no los fija)
- papel: A4 (valor operativo)

## Qué NO resuelve esta plantilla

La numeración en romanos minúsculos de los preliminares y el reinicio en
arábigos desde el cuerpo **no** se configuran aquí: Word los implementa con
saltos de sección, que Quarto no genera. Los aplica
`herramientas/docx_numeracion.py` al final, sobre el `.docx` ya renderizado.

Este archivo se regenera con:

```
uv run python -m herramientas.plantilla_docx --perfil sistemas-fisi
```