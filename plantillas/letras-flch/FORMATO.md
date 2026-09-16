# Formato aplicado — `letras-flch`

- Facultad: Facultad de Letras y Ciencias Humanas
- Estado del perfil: `verificado`
- Fuente del formato: Anexo 2, incisos 1 a 10

## Valores con los que se generó `referencia.docx`

| Parámetro | Valor |
|---|---|
| Papel | A4 |
| Tipografía | Arial |
| Cuerpo | 12 pt |
| Interlineado | 1.5 |
| Margen superior | 3.0 cm |
| Margen inferior | 2.5 cm |
| Margen izquierdo | 3.0 cm |
| Margen derecho | 2.5 cm |

## Atención: valores que NO vienen de una norma

La norma aplicable a este perfil no fija los siguientes puntos. Se
aplicaron valores operativos para poder maquetar. **No son requisitos**
y conviene confirmarlos con el asesor antes de la entrega:

- papel: A4 (valor operativo)

## Qué NO resuelve esta plantilla

La numeración en romanos minúsculos de los preliminares y el reinicio en
arábigos desde el cuerpo **no** se configuran aquí: Word los implementa con
saltos de sección, que Quarto no genera. Los aplica
`herramientas/docx_numeracion.py` al final, sobre el `.docx` ya renderizado.

Este archivo se regenera con:

```
uv run python -m herramientas.plantilla_docx --perfil letras-flch
```