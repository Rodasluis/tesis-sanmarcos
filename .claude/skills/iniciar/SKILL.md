---
name: iniciar
description: Arranca el trabajo de tesis. Conversa sobre el tema, carga el perfil de la escuela y deja el repositorio listo. Es la etapa 0 del flujo.
disable-model-invocation: true
---

# /iniciar — etapa 0

Primera conversación con el tesista. Al terminar, el repositorio queda
configurado y hay una decisión registrada sobre el tema y el enfoque.

## Antes que nada: esto es una conversación, no un trámite

La persona que escribe `/iniciar` **ya terminó su carrera**. No es un alumno
matriculado: es un egresado o bachiller que tiene la tesis pendiente, que
probablemente trabaja y que puede llevar años fuera de la universidad.

No preguntes si tiene el grado de bachiller, si le asignaron asesor, en qué año
ingresó ni cuánto tiempo libre tiene. **Nada de eso condiciona nada.** Si hace
falta para algo concreto más adelante, se pregunta ahí.

Habla como se habla con un profesional que vuelve a algo que dejó pendiente.
Sin tono docente.

## 1. Comprueba la instalación, en silencio

Corre esto y **solo menciona lo que falte**:

```
uv run python -m herramientas.instalar_hooks --comprobar
uv run python -m herramientas.zotero --sin-red
quarto --version
```

Si falta Quarto o el hook no está instalado, dilo en una línea y ofrece
arreglarlo. Si `referencias.bib` está vacío, no es un problema todavía: lo será
en `/literatura`. Menciónalo una vez y sigue.

## 2. Conversa sobre la tesis

Lo que necesitas saber para empezar, en este orden:

1. **Facultad y escuela.** Es lo único imprescindible: determina el perfil.
2. **Qué le interesa investigar.** Acepta respuestas vagas: "algo de
   presupuesto municipal" basta para arrancar. Afinarlo es la etapa 2.
3. **Si ya tiene datos**, propios o de una fuente que conozca.
4. **Si la tesis es individual o grupal.** Hasta tres autores
   (RR N.° 00744-R-20, §7.2 a). Si es grupal, cada participante necesita
   objetivos definidos —inciso b—, pero eso se resuelve en `/proyecto`, no ahora.

Si no sabe algo, sigue adelante. Una tesis empieza muchas veces con "quiero
hacer algo sobre educación rural" y eso es suficiente.

## 3. Carga el perfil

```
uv run python -m herramientas.activar_perfil --listar
uv run python -m herramientas.activar_perfil <id>
```

Luego **cuéntale qué significa su perfil**, en dos o tres frases, sin jerga:

- Si está `verificado`: su escuela tiene reglamento propio. Dile qué le exige en
  concreto —estilo de citas, si hay comité de ética, si el proyecto caduca—.
- Si no lo está: su escuela no publica un esquema propio, así que rige la
  estructura general de la universidad, que es norma de verdad, no una plantilla
  que nos inventamos. **Dilo una vez y sigue.** No pidas que nadie lo confirme.

Si el perfil deja el estilo de citas en `[PENDIENTE-NORMATIVA]`, dilo ahora:
elegirlo tarde obliga a rehacer citas.

## 4. Enséñale la tensión del art. 10 b)

Esto no se esconde. Una sola vez, breve, sin dramatizar:

> El Código de Ética de la UNMSM (RR N.° 012648-2023-R, art. 10 b) prohíbe el
> apoyo de terceros que exceda la asesoría de tesis. La Directiva de
> originalidad, que es posterior, admite la IA generativa "como apoyo, siempre
> respetando la originalidad" (art. 5 q). Ninguna norma define dónde termina una
> cosa y empieza la otra.
>
> Por eso este repositorio registra todo lo que hago y todo lo que decides tú:
> para que el proceso se pueda mirar. Está explicado en
> `normativa/conflictos.md`, C-01.

Es información para que decida con los ojos abiertos. **No es una advertencia
que tenga que aceptar para continuar.**

## 5. Prepara el terreno

```
uv run python -c "from herramientas import registro_ia; registro_ia.marcar_etapa('iniciar')"
```

Escribe en `notas/ideas/` lo que te contó, con sus palabras. Eso alimenta la
etapa 2.

## 6. Punto de decisión

Sigue la forma de `CLAUDE.md` §5. Aquí la decisión es **el tema general y el
enfoque**:

- Presenta 2 o 3 recortes posibles de lo que te contó, con lo que cada uno
  exigiría en datos y en tiempo. Marca uno como recomendado y di por qué.
- Si trajo un tema cerrado, no inventes alternativas: confirma que lo entendiste
  y registra eso.
- Preguntas de comprensión: por qué ese tema importa, y qué esperaría encontrar.

Registra con `registrar_decision.py`, etapa `iniciar`. **Con sus palabras
textuales**, no con un resumen tuyo.

## Qué NO hacer aquí

- No pidas documentos ni comprobantes de nada.
- No prometas que la tesis pasará Turnitin.
- No elijas el tema por él, ni siquiera si lo que propone parece difícil. Dile
  qué lo hace difícil y deja que decida.
- No avances a `/explorar-datos` sin la decisión registrada.
