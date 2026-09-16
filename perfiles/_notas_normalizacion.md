# Notas de normalización de los perfiles

Registro de toda diferencia entre lo que dice literalmente un documento normativo
y lo que quedó escrito en el perfil YAML. Existe para que nadie tenga que
adivinar por qué el perfil no coincide palabra por palabra con su fuente.

Regla: **nunca se corrige el contenido de una norma, solo su forma** (numeración
rota, erratas tipográficas evidentes, inconsistencias de rotulación). Cuando la
diferencia afecta al fondo, no se normaliza: se registra en
`normativa/conflictos.md`.

---

## letras-flch

**Fuente:** RD N.° 000057-2021-D-FLCH, §7.1.

1. **Numeración saltada en el capítulo II.** El instructivo enumera `2.1`, `2.3`,
   `2.4`, sin `2.2`, en ambos modelos.
   *Normalización:* se renumeró de forma corrida a `2.1`, `2.2`, `2.3`. El
   contenido y el orden se mantienen intactos.

2. **Rótulo de conclusiones.** Tras el capítulo V (o VI en el modelo cualitativo)
   el instructivo escribe `V. CONCLUSIONES Y RECOMENDACIONES`, reutilizando el
   romano `V`.
   *Normalización:* se trató como sección final **sin número de capítulo**, igual
   que `REFERENCIAS BIBLIOGRÁFICAS` y `ANEXOS`. Es lo que hace el propio
   Anexo 2B de la norma general, que numera las conclusiones como capítulo VII
   solo porque allí sí forman parte de la secuencia.

3. **Errata tipográfica.** El modelo cualitativo rotula el capítulo IV como
   `MÉTODOLOGÍA`.
   *Normalización:* `METODOLOGÍA`.

4. **Modelo argumentativo.** Las tesis de Arte y Literatura observadas en
   Cybertesis titulan sus capítulos por contenido y no llevan metodología
   empírica. El instructivo **no contempla** ese modelo.
   *Decisión:* se incluyó en el perfil como `estado: solo_de_facto`, con
   advertencia expresa de que requiere confirmación escrita del asesor. No se
   presenta como si la norma lo respaldara.

---

## economia-fce

**Fuente:** archivo `PAUTAS PARA SUSTENTACION DE TESIS.docx`.

1. **Título del archivo contra su contenido.** El nombre anuncia "sustentación",
   pero el documento regula la estructura del **diseño o proyecto**.
   *Normalización:* el perfil lo trata como norma del proyecto. Registrado
   también en `normativa/conflictos.md`, C-02.

2. **"NORMAS APPA".** El documento escribe `APPA`, con doble P, y no indica
   edición ni año.
   *Normalización:* se interpretó como APA y se adoptó APA 7 como valor
   operativo, marcando la edición exigida como `[PENDIENTE-NORMATIVA]`. La
   errata se transcribe literalmente en el campo `estilo_citas_fuente` para que
   quede constancia.

3. **Ítems sin numerar en el cuerpo.** El índice del documento numera del 1 al 8,
   pero el desarrollo posterior usa encabezados en mayúsculas sin número, y el
   ítem 8 aparece pegado como `8Anexos-`.
   *Normalización:* se conservó la numeración del índice (1 a 8) y se limpió el
   rótulo a `Anexos`.

4. **Ausencia de informe final.** La guía no define el informe final.
   *Decisión:* el perfil no lo inventa. Declara `informe_final.origen:
   esquema_capitular` heredando la estructura del Anexo 2B, y advierte que si el
   esquema capitular aprobado se aparta del Anexo 2B, prevalece el Anexo 2B.

---

## unmsm-general

**Fuente:** RR N.° 00744-R-20, Anexos 2A y 2B.

1. **"HipóT".** El anexo abrevia así "hipótesis" en varios lugares
   (`III.1 HipóT`, `IV.1 Enfoque de la investigación (HipóT inductiva)`).
   *Normalización:* se transcribió literalmente en el YAML, porque cambiarlo
   podría ocultar que la fuente es un escaneo con esa abreviatura. La
   interpretación como "hipótesis" queda anotada aquí.

2. **PDF sin capa de texto.** El anexo de 16 folios es un escaneo. Se leyó
   rasterizando sus páginas a imagen.
   *Consecuencia:* las transcripciones de este documento no provienen de
   extracción automática de texto, sino de lectura. Si aparece una versión con
   capa de texto, conviene contrastarlas.

3. **Modelo cualitativo con capítulo de hipótesis.** El Anexo 2B mantiene
   `III. HIPÓTESIS Y VARIABLES` también en el modelo cualitativo, algo poco
   habitual en metodología cualitativa.
   *Decisión:* se respeta tal cual. El campo `hipotesis` del perfil base vale
   `obligatoria` porque eso es lo que dice la norma, y son los perfiles de
   facultad los que lo relajan cuando su propia norma lo permite (Medicina:
   `condicional`).

---

## medicina-fm

**Fuente:** RD N.° 002373-2023-D-FM, anexos C, D, E y F.

1. **Capítulos sin título propio.** Los anexos C y D rotulan `CAPITULO I`,
   `CAPITULO II`, `CAPITULO III` sin darles nombre, y listan su contenido con
   viñetas.
   *Normalización:* el perfil conserva los rótulos sin título y guarda las
   viñetas en `items`, en vez de inventar nombres de capítulo.

2. **Numeración interna del articulado.** El reglamento salta de `33.2` a `30.3`
   dentro del artículo 33 (sustentación).
   *Normalización:* se leyó como `33.3`, que es lo que corresponde por posición.
   No afecta a ningún campo del perfil; se registra por transparencia.

3. **Remisión al formato de *Anales*.** Los anexos E y F exigen que el resumen
   siga el formato de la Revista Anales de la Facultad de Medicina, sin
   reproducirlo.
   *Decisión:* `resumen.formato` recoge la remisión literal y los campos
   numéricos quedan en `[PENDIENTE-NORMATIVA]`. El repositorio **no** inventa
   el formato de la revista.

---

## derecho-fdcp

**Fuente:** Reglamento General de Grados y Títulos de la FDCP, ratificado por
RR N.° 007301-2022-R.

1. **Sin estructura capitular propia.** El reglamento es procedimental y remite
   al Anexo 2 de la directiva general.
   *Decisión:* el perfil no define `informe_final.modelos`; declara
   `origen: herencia`. No es un vacío del perfil, es lo que manda la norma.

2. **Interlineado simple.** El art. 24 j) exige espacio simple, frente al 1,5
   habitual en otras facultades.
   *Decisión:* se transcribe tal cual, sin "corregirlo" hacia la práctica común.

---

## Perfiles generados por herencia (16 facultades)

No hay normalización que registrar: no se transcribió ninguna norma de facultad,
porque no se localizó ninguna. Estos perfiles declaran explícitamente que heredan
`unmsm-general` y adjuntan, marcada como no normativa, la observación de tesis
depositadas en Cybertesis.

Punto a vigilar: la observación de facto de **Ciencias Biológicas**, **Ciencias
Físicas** y **Ciencias Matemáticas** resultó poco concluyente (índices muy
heterogéneos o no legibles). En esos tres perfiles la sección
`observacion_de_facto` tiene poco valor informativo y no debe usarse para
justificar ninguna decisión de estructura.
