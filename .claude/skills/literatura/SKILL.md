---
name: literatura
description: Busca, selecciona y sintetiza la literatura de la tesis, y la deja en Zotero. Es la etapa 3 del flujo.
disable-model-invocation: true
---

# /literatura — etapa 3

Construye el estado de la cuestión. Al terminar hay una biblioteca Zotero
utilizable, una síntesis escrita y unos vacíos identificados.

## La regla que no se negocia

**Solo se cita lo que está en `referencias.bib`.** Si crees recordar un trabajo,
esa sensación no es una fuente: búscalo, compruébalo, agrégalo con aprobación del
tesista, y entonces cítalo.

Una afirmación sin fuente se marca `[VERIFICAR]`. Nunca se rellena con una
referencia "que debe existir". Es el error más caro de todo el flujo, porque el
jurado lo encuentra leyendo, y una referencia inventada hunde la credibilidad de
todo lo demás.

## 1. Marca la etapa y comprueba Zotero

```
uv run python -c "from herramientas import registro_ia; registro_ia.marcar_etapa('literatura')"
uv run python -m herramientas.zotero
```

Si `referencias.bib` no existe o está vacío, para y configúralo:

```
uv run python -m herramientas.zotero --instrucciones
```

Sin eso, nada de esta etapa sirve: no habría dónde guardar lo que encuentres.

## 2. Mira primero lo que ya hay

- La biblioteca Zotero del tesista, si ya tiene algo.
- **Cybertesis**, que tiene API y es la fuente de antecedentes locales:
  ```
  https://cybertesis.unmsm.edu.pe/backend/api/discover/search/objects?query=<tema>
  ```
  Las tesis de su propia escuela importan por dos razones: son los antecedentes
  que el jurado espera ver, y permiten comprobar que el tema no está repetido
  —en Derecho eso se verifica administrativamente al inscribir (art. 25 del
  reglamento de su facultad).
- **ALICIA** para el resto de repositorios peruanos.

## 3. Busca fuera

Por orden de utilidad:

- **OpenAlex** — cobertura amplia, API abierta, sin clave.
- **Crossref** — para resolver y comprobar DOI.
- **PubMed** — obligatorio si el perfil es de salud (Medicina, Farmacia,
  Odontología, Veterinaria, Psicología).
- **SciELO** y **Redalyc** — producción en español y latinoamericana, que suele
  faltar en las bases anglosajonas y que un jurado peruano espera ver.

De cada trabajo necesitas: autores, año, título, publicación, DOI o enlace
estable, y **qué dice que sea relevante para esta tesis**. Sin esa última parte
es una lista, no una revisión.

## 4. Agrega a Zotero solo con aprobación

Presenta lo que encontraste agrupado por tema, con una frase de por qué cada uno
importa. El tesista elige qué entra.

No agregues cosas "por si acaso": una biblioteca con 200 entradas de las que se
citan 30 hace que `verificar_referencias.py` llene el informe de avisos y que
nadie los lea.

## 5. Sintetiza

Escribe en `notas/lecturas/` una síntesis **por temas, no por autores**. Una
revisión que va "Pérez dice… Quispe dice… Torres dice…" no es una revisión: es
un listado.

Organízala así:

- **Qué se sabe**, agrupado por hallazgo.
- **Dónde no hay acuerdo**, con quién sostiene cada posición.
- **Qué no se ha estudiado** — de aquí sale la justificación de la tesis.
- **Cómo lo han medido otros**: variables, instrumentos, diseños. Esto alimenta
  directamente la metodología de `/proyecto`.

Para el Perú y la región, di explícitamente qué evidencia local hay. Si no hay,
eso también es un hallazgo y vale como justificación.

## 6. Comprueba antes de cerrar

```
uv run python -m herramientas.verificar_referencias --detalle
```

Arregla lo que salga: claves que no existen, campos que faltan para el estilo del
perfil, títulos que no coinciden con Crossref, retractaciones.

Si una referencia aparece como **retractada**, quítala. No es un aviso menor: es
evidencia que la propia revista retiró.

## 7. Pide la crítica

Lanza `critico-citas`. Comprueba que cada cita exista, sea pertinente y respalde
de verdad lo que se le atribuye. Esa última parte es la que más falla.

## 8. Punto de decisión

Decisión: **qué lecturas son centrales**.

- Propón 5 a 10 trabajos como núcleo, diciendo qué aporta cada uno a *esta*
  tesis.
- Preguntas de comprensión: qué autor lleva la contraria a tu hipótesis y por
  qué; qué vacío justifica que esta tesis exista.

Registra con etapa `literatura`.

## Qué NO hacer aquí

- No cites nada que no esté en `referencias.bib`.
- No inventes DOI, años ni números de página.
- No atribuyas a un autor una afirmación que no hiciste el esfuerzo de
  comprobar en su texto.
- No llenes la biblioteca para que parezca completa.
