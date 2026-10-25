---
name: explorar-datos
description: Encuentra, descarga y describe los datos de la tesis. Cataloga fuentes abiertas o ingiere los datos propios del tesista, con anonimización. Es la etapa 1 del flujo.
disable-model-invocation: true
---

# /explorar-datos — etapa 1

Convierte "quiero investigar algo sobre X" en datos reales en disco, descritos y
listos para preguntar cosas. Sin esto, la etapa 2 solo puede inventar.

## Principio que gobierna esta etapa

**Las ideas nacen de datos que existen.** No propongas una pregunta y luego
busques datos que la respondan: mira qué hay, y de ahí salen preguntas que se
pueden contestar. Una tesis que se atasca es casi siempre una tesis cuyos datos
nunca existieron.

## 1. Marca la etapa

```
uv run python -c "from herramientas import registro_ia; registro_ia.marcar_etapa('explorar-datos')"
```

## 2. Mira el catálogo antes de buscar por tu cuenta

`herramientas/fuentes/catalogo.yaml` tiene 33 fuentes con su estado comprobado.
Léelo y filtra por la facultad del perfil activo.

Cuatro cosas que el catálogo ya sabe y te ahorran tiempo:

- **Solo cuatro fuentes tienen acceso programático**: Banco Mundial, la
  Plataforma Nacional de Datos Abiertos, Cybertesis y el repositorio de OSIPTEL
  (OAI-PMH). Todo lo demás es descarga manual.
- **La API del BCRP no atiende peticiones automáticas.** Devuelve una página
  anti-bot. No insistas: usa el buscador de series de su web.
- **ESCALE y MEF no tienen API.** Son formularios web.
- **No todo lo que se encuesta lo encuesta el INEI.** El INEI aloja encuestas de
  otras entidades —la ENA es del MIDAGRI, ENSUSALUD de SUSALUD— y además los
  reguladores tienen las suyas: ERESTEL de OSIPTEL para telecomunicaciones,
  ERCUE de OSINERGMIN para energía, las encuestas de inclusión financiera de la
  SBS, la Planilla Electrónica del MTPE, los estados financieros de la SMV.
  Para su sector suelen ser mejores que la ENAHO. Míralas antes de concluir que
  no hay datos.
- **Hay microdatos internacionales gratuitos sobre el Perú.** La ENDES es parte
  del programa DHS, con API e indicadores comparables entre países desde 1986.
  Young Lives sigue a las mismas personas desde 2002, que es lo único
  longitudinal que hay. Y el Banco Mundial, IPUMS, LAPOP, Latinobarómetro y las
  Enterprise Surveys cubren al Perú con registro gratuito.

Cuando propongas una fuente privada —GRADE, IEP, IPE, Ipsos, Datum— di que **no
es oficial**. Miden lo que el Estado no mide, pero sin la representatividad de
una encuesta del INEI, y sin ficha técnica no se citan.

Si el catálogo dice `verificar` o `api_bloqueada`, créele. Se comprobó de verdad.

Antes de prometer que una URL funciona:

```
uv run python -m herramientas.fuentes.verificar
```

## 3. Según de dónde vengan los datos

### Fuentes abiertas

1. Propón 2 o 3 fuentes del catálogo que encajen con el tema, diciendo de cada
   una **qué variables trae, con qué desagregación y desde qué año**.
2. Descarga lo que el tesista elija. A `datos/crudos/`, **sin tocar**.
3. Guarda también el diccionario de variables si lo hay.
4. Anota en `datos/crudos/_procedencia.md` la fecha, la URL y los filtros
   exactos que usaste. Los portales corrigen series hacia atrás sin avisar.

### Datos propios del tesista

Encuestas, entrevistas, registros de su trabajo.

1. Pide los archivos tal como estén.
2. **Anonimiza antes de que salgan de `datos/crudos/`.** Sustituye nombres por
   códigos (E-01, E-02…), quita DNI, teléfonos, correos y direcciones. El
   resultado anonimizado va a `datos/procesados/`, y el código que lo hizo a
   `codigo/`.
3. Comprueba lo que quedó:
   ```
   uv run python -m herramientas.datos_personales datos/procesados/*
   ```
4. Si hay personas entrevistadas, el consentimiento informado es un anexo del
   proyecto. Pregúntale si ya lo tiene; si no, lo preparan en `/proyecto`.

**Dile estas tres cosas al tesista**, una vez, cuando aparezcan datos de
personas. No bloquean nada; se las decimos porque la ley es más exigente de lo
que casi nadie supone (`normativa/requisitos.md`, R-28):

- **Poner códigos no es anonimizar si guarda la tabla de equivalencias.** El
  art. 41.1 del reglamento llama a eso *disociación* y dice que es reversible:
  el dato sigue siendo personal. Pregúntale si va a necesitar volver al nombre;
  si no, que no cree la tabla, y si ya existe, que la destruya cuando deje de
  hacerle falta.
- **Con ocho o diez entrevistas en un solo sitio, el nombre no es lo único que
  identifica.** El oficio, la edad exacta, el barrio y la composición familiar,
  juntos, pueden señalar a una persona. La ley lo llama identificable
  «indirectamente a partir de la combinación de datos». Al citar en el texto,
  quita el detalle que no aporte al argumento.
- **Si toca salud, vida afectiva o familiar, hábitos íntimos o afiliación
  sindical, son datos sensibles y el consentimiento va por escrito y firmado**
  (art. 8), y es el tesista quien tiene que poder probarlo (art. 9).

No puedes escribir en `datos/crudos/`: hay una regla de permisos que lo impide.
Es deliberado. Para poner archivos ahí, dile al tesista que los copie él, o
hazlo con Bash y déjalo dicho.

## 4. Describe lo que hay

Escribe código en `codigo/` que produzca, en `resultados/`:

- **Diccionario de variables**: nombre, tipo, qué mide, cuántos faltantes.
- **Descriptivos**: n, media, mediana, desviación, mínimo y máximo de las
  numéricas; frecuencias de las categóricas.
- **Cobertura**: qué años, qué ámbito geográfico, qué unidades.
- **Calidad**: faltantes por variable, valores imposibles, duplicados.

Si la encuesta trae **factor de expansión**, úsalo y dilo. Un promedio sin
ponderar de la ENAHO no describe al Perú; describe a la muestra. Es lo que más
veces desarma un jurado.

## 5. Di la verdad sobre lo que encontraste

Esta es la parte que más importa y la más fácil de suavizar. Si los datos no dan
para lo que el tesista quería, **dilo ahora**, cuando cambiar de rumbo cuesta una
tarde y no seis meses.

Concretamente, avisa si:

- la muestra es demasiado pequeña para lo que quiere mirar;
- la variable clave no está, o está solo en algunos años;
- la desagregación no llega a su unidad de análisis (quiere distritos y los datos
  son regionales);
- hay tantos faltantes que cualquier resultado sería frágil.

## 6. Pide la crítica

Lanza el agente `critico-datos`. Revisa calidad, sesgos de muestra, factibilidad
y anonimización. Si levanta algo serio, arréglalo antes del punto de decisión.
Si tras tres rondas no hay acuerdo, llévalo al tesista con las dos posturas.

## 7. Punto de decisión

Decisión: **qué fuentes se usan**.

- Presenta cada opción con lo que permite y lo que impide.
- Marca una recomendada, con su razón.
- Preguntas de comprensión: de dónde salen estos datos y quién los recolectó;
  qué no se puede responder con ellos.

Registra con etapa `explorar-datos`.

## Qué NO hacer aquí

- No simules datos "de ejemplo" para enseñar cómo quedaría. Si no hay datos, no
  hay nada que enseñar.
- No imputes faltantes sin decirlo y sin que sea una decisión registrada.
- No subas nada de `datos/crudos/` al remoto.
- No describas una fuente que no descargaste.
