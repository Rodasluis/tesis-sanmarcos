# Estas transcripciones son FICTICIAS

**Ninguna de estas entrevistas ocurrió. No hay participantes. No hay personas
detrás de estos códigos.** Se escribieron para que el ejemplo
`medicina-cualitativo` pueda recorrer el flujo completo —codificar, documentar
saturación, citar a un participante y que `verificar_cifras.py` compruebe que la
cita existe en la transcripción— sin usar datos de nadie.

## Cómo están marcadas

Tres marcas, para que no se puedan confundir con datos reales ni por descuido:

1. **En el nombre del archivo**: todas empiezan por `FICTICIA_`.
2. **Dentro de cada archivo**: la primera línea dice `TRANSCRIPCIÓN FICTICIA`.
3. **En este archivo**, que vive en la misma carpeta.

Hay una prueba del repositorio que lo comprueba: si alguien agregara aquí una
transcripción sin esas marcas, los tests fallan.

## Por qué el repositorio permite esto aquí y en ningún otro sitio

El principio 1 de `CLAUDE.md` prohíbe simular datos. Esto no es una excepción al
principio: es material de prueba del propio repositorio, no evidencia de una
tesis. La diferencia está en que **nada de aquí respalda una afirmación sobre el
mundo**. El ejemplo no concluye nada sobre pacientes hipertensivos del Perú;
demuestra cómo funcionan las herramientas.

Si estuviera escribiendo tu tesis y te ofreciera «unas transcripciones de
ejemplo para ir avanzando mientras consigues las tuyas», eso sí sería una
violación del principio 1, y de las graves.

## En una tesis real

Aquí irían tus transcripciones, y **no se versionan**: `datos/crudos/` está
fuera del control de versiones y hay una regla de permisos que impide escribir en
él. Antes de que cualquier cosa salga de esta carpeta se anonimiza
—`herramientas/datos_personales.py` lo comprueba— y el consentimiento informado
va como anexo del proyecto.

El Comité de Ética en Investigación es obligatorio en Medicina (art. 23 del
reglamento de la facultad, RR N.° 00170-D-FM-2024).
