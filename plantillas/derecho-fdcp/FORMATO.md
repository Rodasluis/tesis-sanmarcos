# Formato aplicado — `derecho-fdcp`

- Facultad: Facultad de Derecho y Ciencia Política
- Estado del perfil: `verificado`
- Fuente del formato: Art. 24 inciso j: «escrito en computadora, en papel tamaño A4, a un espacio simple, tipo de letra Arial 12».

## Valores con los que se generó `referencia.docx`

| Parámetro | Valor |
|---|---|
| Papel | A4 |
| Tipografía | Arial |
| Cuerpo | 12 pt |
| Interlineado | 1.0 |
| Margen superior | 2.5 cm |
| Margen inferior | 2.5 cm |
| Margen izquierdo | 3.0 cm |
| Margen derecho | 2.5 cm |

## Atención: valores que NO vienen de una norma

La norma aplicable a este perfil no fija los siguientes puntos. Se
aplicaron valores operativos para poder maquetar. **No son requisitos**
y conviene confirmarlos con el asesor antes de la entrega:

- márgenes: 2,5 cm salvo el izquierdo, 3,0 cm para encuadernación (valores operativos; la norma no los fija)

## Qué NO resuelve esta plantilla

La numeración en romanos minúsculos de los preliminares y el reinicio en
arábigos desde el cuerpo **no** se configuran aquí: Word los implementa con
saltos de sección, que Quarto no genera. Los aplica
`herramientas/docx_numeracion.py` al final, sobre el `.docx` ya renderizado.

Este archivo se regenera con:

```
uv run python -m herramientas.plantilla_docx --perfil derecho-fdcp
```