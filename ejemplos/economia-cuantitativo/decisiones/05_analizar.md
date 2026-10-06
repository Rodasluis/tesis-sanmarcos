# Decisión 05 — etapa `analizar`

- Registrada: 2026-10-05T22:13:33
- Aprobada por el tesista: **sí**
- Sello: `e1d362605549d4eb…`

> Este archivo lo escribe `registrar_decision.py`. Si lo editas a mano, `verificar_decisiones.py` lo detectará y marcará la decisión como alterada.

## Opciones que se le presentaron

- Solo la especificación con efectos fijos de país y año

- Siete especificaciones, reportando todas, incluidas las que no salieron

- Reportar la que mejor se ajusta a los datos

## Qué decidió el tesista

**Eligió:** Siete especificaciones, reportando todas, incluidas las que no salieron

**En sus palabras:**

> [EJEMPLO FICTICIO] Las siete, todas reportadas. El resultado me salió al revés de mi hipótesis: la correlación es fuerte y positiva, y con efectos de año se va a cero. Lo pongo tal cual. Si escondo las dos que salen significativas sin efectos de año, estoy ocultando justo lo que hace interesante el resultado; y si escondo las cinco nulas, estoy mintiendo.

## Cambios que pidió

- Agrupar los errores estándar por país
- Agregar una especificación en primeras diferencias
- Agregar una especificación sin el Perú, para ver si el resultado depende de un país

## Preguntas de comprensión

No bloquean el avance. Quedan registradas y alimentan `/sustentacion`.

**1. ¿Por qué agrupar los errores estándar por país?**

> [EJEMPLO FICTICIO] Porque las observaciones de un mismo país en años distintos no son independientes. Sin agrupar, los intervalos salen más angostos de lo que deberían.

**2. Tu resultado es nulo. ¿Eso demuestra que la conectividad no sirve?**

> [EJEMPLO FICTICIO] No. El intervalo incluye el cero pero también incluye efectos positivos chicos. Lo que descarto es un efecto del tamaño que sugería la correlación simple, no cualquier efecto.
