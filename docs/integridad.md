# Integridad: qué se puede y qué no, con el artículo que lo dice

Written for: tesistas de la UNMSM que usan este repositorio y necesitan saber
dónde está la línea, y por qué está ahí.

---

Este documento no es una lista de buenas intenciones. Cada prohibición viene con
el documento, el artículo y lo que dice, para que pueda comprobarlo usted mismo.
Lo que no consta en una norma leída está marcado como tal.

Las normas citadas están en `normativa/`, con sus PDF, y el detalle completo con
páginas en [`normativa/requisitos.md`](../normativa/requisitos.md).

## Las tres normas que importan

| Norma | Qué regula |
|---|---|
| **Código de Ética en Investigación de la UNMSM**, RR N.° 012648-2023-R | Honestidad en el manejo de datos, confidencialidad, consentimiento |
| **Directiva de originalidad**, RR N.° 000947-2026-R | Similitud, plagio, faltas del autor, trámite en PIDS |
| **Directiva general de tesis**, RR N.° 00744-R-20 | Estructura del documento (Anexos 2A y 2B) |

## Lo que está prohibido y la herramienta se niega a hacer

Esto no es una preferencia de estilo del repositorio. Son faltas tipificadas.

### Alterar el documento para evadir la detección

> «incorporar párrafos de texto en formato de imagen»
> «incluir caracteres extraños o realizar alteraciones intencionadas en el
> contenido del documento»
>
> — Directiva de originalidad, art. 30 c) y d)

Caen aquí, y la herramienta no lo hará aunque se lo pida:

- Convertir texto, tablas o fórmulas en imágenes.
- Insertar caracteres invisibles, homoglifos o espacios de ancho cero.
- Cambiar letras por caracteres de otro alfabeto que se ven igual.
- Parafrasear con el único objetivo de bajar el porcentaje de similitud.

Lo último merece una aclaración, porque es lo que más se pide. **Reescribir con
sus propias palabras está bien y es lo que hay que hacer.** Lo que no está bien
es reescribir *para que el detector no lo encuentre*, dejando la idea ajena sin
atribuir. La diferencia no está en el texto resultante: está en si la fuente
sigue citada. Si la cita está, parafrasear es trabajo legítimo; si la cita
desaparece en el proceso, es plagio con mejor redacción.

**Lo que sí resuelve el problema**, cuando la similitud sale alta:

1. Citar bien lo que es de otros. Una cita correcta no cuenta como plagio aunque
   suba el porcentaje.
2. Reducir el texto de terceros. Si la mitad del marco teórico son citas
   textuales, el problema no es el detector.
3. Escribir con sus propias ideas las partes que son suyas: el método que usó,
   lo que encontró, lo que concluye.

### Manipular datos, cifras o conclusiones

> «la manipulación de la información, las cifras estadísticas y las conclusiones
> de las investigaciones»
>
> — Código de Ética en Investigación, art. 10 d)

Caen aquí:

- Inventar o simular datos, respuestas o testimonios.
- Imputar valores faltantes sin declararlo.
- Inventar una cita de un participante, o «arreglarle» la gramática hasta que
  deje de ser lo que dijo.
- Reportar solo la especificación que salió significativa y esconder las demás.
- Redondear hasta que un resultado cruce un umbral.
- Afirmar que se alcanzó la saturación cuando no se alcanzó.

El repositorio lo comprueba donde puede: `verificar_cifras.py` marca como error
toda cifra del texto que no exista en `resultados/`, y en investigación
cualitativa comprueba que **cada cita de participante aparezca literalmente** en
una transcripción de `datos/crudos/`.

### Inventar referencias

Esto no está tipificado con esas palabras en ninguna norma, pero es la falta que
un jurado detecta en treinta segundos y la que más daño hace.

Un modelo de lenguaje produce referencias que parecen perfectas —autor
plausible, revista real, año coherente, DOI con el formato correcto— y no
existen. El repositorio trabaja sobre el supuesto de que **la sensación de
recordar una fuente no es una fuente**:

- Solo se citan claves presentes en `referencias.bib`, que exporta Zotero.
- Una afirmación sin fuente se marca `[VERIFICAR]` y no se rellena.
- `verificar_referencias.py --con-red` comprueba contra Crossref, OpenAlex y
  PubMed que cada referencia exista y que el título coincida.

Si ve un `[VERIFICAR]` en su borrador, eso no es un fallo de la herramienta: es
la herramienta diciéndole que ahí falta una fuente de verdad.

## Lo que la norma sí exige

### Dos archivos .docx, con nombre exacto

> La tesis se presenta en dos archivos .docx, dentro de las carpetas `TEXTO/` y
> `DOCUMENTO/`, con nomenclatura exacta, y las tablas y fórmulas como texto y no
> como imágenes.
>
> — Directiva de originalidad, art. 13 apartado A

El entregable es **.docx**, no PDF. Los genera `/entregar` con los nombres
correctos, para que no haya que recordarlos.

### Similitud entre 0 % y 20 %, medida en PIDS

El umbral es de 0 % a 20 % y lo mide la plataforma PIDS de la universidad.

**Nada de este repositorio mide ese número.** `similitud_interna.py` compara su
texto consigo mismo y con los PDF que tenga en su biblioteca local: sirve para
encontrar párrafos repetidos y fragmentos que copió sin citar, y no tiene acceso
a la base de datos contra la que compara Turnitin. Un informe limpio de esa
herramienta **no anticipa** el resultado de PIDS, y si alguien le dice lo
contrario, le está vendiendo algo.

Dos cosas con fecha:

- **El certificado de similitud vence a los 90 días** (art. 19).
- **Desde la segunda revisión, PIDS cuesta S/ 20.**

### Consentimiento informado y comité de ética

El Código de Ética exige consentimiento informado (art. 12) y confidencialidad
(art. 5). En algunas facultades el comité de ética es obligatorio: en Medicina lo
es, junto con la aprobación del Comité de Investigación de la escuela y la
resolución decanal, antes de ejecutar el proyecto (art. 23 del reglamento de la
facultad, RD N.° 002373-2023-D-FM).

### Protección de datos personales

Ley N.° 29733 y su reglamento, DS N.° 016-2024-JUS. En la práctica, dentro de
este repositorio:

- Los datos personales se anonimizan **antes** de salir de `datos/crudos/`.
- `datos/crudos/` no se versiona y hay una regla de permisos que impide
  escribir en él.
- Un *hook* de git revisa lo que está a punto de subir y lo detiene si encuentra
  indicios de datos personales.

## La declaración de uso de IA

Esta parte hay que decirla con precisión, porque es fácil de exagerar en
cualquiera de las dos direcciones.

**Ninguna norma de la UNMSM que hayamos leído exige declarar el uso de
inteligencia artificial.** Consta así en
[`normativa/requisitos.md`](../normativa/requisitos.md), punto P-01. Si alguien
afirma que es obligatorio, pídale el artículo.

El repositorio genera la declaración de todos modos, desde
`registro/registro_ia.jsonl`, como medida **voluntaria** de transparencia,
apoyada en el principio del art. 5 del Código de Ética. Describe con exactitud en
qué ayudó Claude y en qué no.

**Usted decide si la presenta.** Y vale la pena saber por qué puede convenirle:
el registro muestra que las decisiones fueron suyas y que los datos son reales,
que es precisamente lo que alguien suspicaz querría comprobar.

## El conflicto que no escondemos

Hay una tensión real entre usar asistencia de IA para redactar y la exigencia de
autoría personal de la tesis. Está escrita, con lo que dice cada norma, en
[`normativa/conflictos.md`](../normativa/conflictos.md), conflicto C-01, y
`/iniciar` la muestra al tesista en la primera sesión en lugar de dejarla para el
final.

La postura del repositorio es explícita y no pretende resolver el conflicto por
usted:

**El tesista decide, firma y sustenta.** Claude hace el trabajo operativo
—buscar, descargar, limpiar, estimar, redactar borradores— y el tesista toma cada
decisión, las registra con sus palabras y responde por el resultado. El registro
no existe para probar que escribió cada palabra; existe para que su asesor vea el
proceso y para que usted llegue a la sustentación **habiendo entendido cada
decisión que va a defender**.

Lo que esto no resuelve: si su facultad considera que redactar un borrador con
asistencia es inaceptable, el registro no la va a convencer. Esa conversación es
suya y es mejor tenerla al principio.

## La prueba final, que no es técnica

Antes de entregar, hágase esta pregunta sobre cada parte del documento:

> Si el jurado me pide que explique esto con mis palabras y que diga de dónde
> salió, ¿puedo?

Donde la respuesta sea no, hay trabajo pendiente —leer la fuente, entender el
método, rehacer el párrafo— y ninguna herramienta lo va a hacer por usted. Es la
única verificación que importa de verdad, y es la que el repositorio no puede
correr.
