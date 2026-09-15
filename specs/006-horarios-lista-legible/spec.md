# Feature Specification: Horarios de servicios como lista legible

**Feature Branch**: `006-horarios-lista-legible`

**Created**: 2026-09-15

**Status**: Draft

**Input**: User description: "las pantallas de detalle de servicios deben mostrar los horarios como una lista separada por comas, sin el formato de corchetes y comilla simple del objeto de python."

## Clarifications

### Session 2026-09-15

- Q: ¿En qué formato se leen las horas y cambia eso lo guardado? → A: Mostrar las horas en formato de 12 horas (AM/PM) solo en la pantalla de consulta. Convertir al mostrar. No cambiar cómo se registra ni se guarda la hora.
- Q: ¿Cómo se escriben la mañana y la tarde junto a cada hora? → A: `8:00 a. m.` / `6:00 p. m.` (español, espacios en el marcador, sin cero a la izquierda).

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Leer los horarios del templo sin notación de programación (Priority: P1)

Una persona que consulta la ficha de un templo abre la sección de horarios de servicios. Para cada tipo de servicio y cada día, ve las horas como una lista en español que se lee de un vistazo (por ejemplo: `8:00 a. m., 10:00 a. m., 6:00 p. m.`), no como un bloque con corchetes, comillas, horario de 24 horas u otra notación de programación.

**Why this priority**: El directorio existe para que la comunidad sepa a qué hora ir a misa o confesión. Si las horas se muestran como un objeto técnico o en 24 horas, el dato deja de ser usable.

**Independent Test**: Con un templo que tiene varios horarios el mismo día, un visitante abre la ficha pública y lee esas horas como texto de 12 horas separado por comas; no aparecen corchetes, comillas ni valores de 24 horas (por ejemplo, no `18:00`).

**Acceptance Scenarios**:

1. **Given** un templo con más de una hora del mismo tipo de servicio el mismo día, **When** un visitante (con o sin sesión) abre la ficha de detalle de ese templo, **Then** esas horas aparecen en una sola lista separada por comas junto al nombre del día, cada una como `h:mm a. m.` o `h:mm p. m.` (por ejemplo `8:00 a. m., 10:00 a. m., 6:00 p. m.`), sin corchetes ni comillas.
2. **Given** un templo con una sola hora de un tipo de servicio en un día, **When** un visitante abre la ficha, **Then** ve esa hora como un único valor de 12 horas (por ejemplo `8:00 a. m.`), sin coma sobrante, sin cero a la izquierda, sin corchetes y sin comillas.
3. **Given** un templo con varios tipos de servicio, **When** un visitante recorre las pestañas o agrupaciones de horarios, **Then** el mismo formato de lista de 12 horas se aplica a todos los tipos; no se inventan, ocultan ni reordenan las horas registradas.

---

### User Story 2 - Confirmar los mismos horarios legibles al editar servicios (Priority: P1)

Un editor autenticado abre la pantalla de servicios del mismo templo y, en el listado de servicios ya registrados, ve las horas del día con el mismo formato de lista de 12 horas separada por comas. Así puede contrastar lo que ve la comunidad con lo que acaba de guardar. El formulario para registrar una hora nueva no cambia cómo se captura ni se guarda el dato.

**Why this priority**: Si la ficha pública se corrige y el listado de edición sigue mostrando notación técnica o 24 horas, el editor no puede verificar de un vistazo que el dato quedó bien.

**Independent Test**: Con el mismo templo del escenario anterior, un usuario autenticado abre la pantalla de servicios y reconoce las mismas horas como lista de 12 horas separada por comas, sin corchetes ni comillas.

**Acceptance Scenarios**:

1. **Given** un templo con varias horas el mismo día y un editor autenticado, **When** abre la pantalla de servicios de ese templo, **Then** el listado inferior muestra esas horas como lista `a. m.` / `p. m.` separada por comas, sin corchetes ni comillas.
2. **Given** un templo sin servicios, **When** un editor autenticado abre esa pantalla, **Then** sigue viendo el mensaje de que aún no hay horarios; no aparece una lista vacía con corchetes.
3. **Given** un visitante en la ficha pública y un editor en la pantalla de servicios del mismo templo, **When** comparan las horas de un mismo día y tipo, **Then** ven las mismas horas en el mismo orden y con el mismo estilo de lista (`a. m.` / `p. m.`, coma y espacio entre cada hora).

---

### Edge Cases

- Un día con una sola hora no debe mostrar coma, corchetes ni comillas.
- Un día con muchas horas debe listarlas todas, separadas por coma y espacio, sin omitir ninguna.
- Un templo sin servicios no debe mostrar una lista vacía con corchetes; la ficha y el editor conservan su estado vacío actual.
- Las horas mostradas deben coincidir con las registradas (ninguna inventada, ninguna silenciosamente omitida); solo cambia la forma de escribirlas en pantalla.
- Mediodía (12:00) se lee como `12:00 p. m.`; medianoche (00:00) se lee como `12:00 a. m.`.
- Las horas de 1 a 9 se leen sin cero a la izquierda (`8:00 a. m.`, no `08:00 a. m.`). Los minutos siempre llevan dos dígitos (`8:00 a. m.`, no `8:0 a. m.`).
- No se usan marcadores en inglés (`AM` / `PM`) ni formas compactas (`a.m.` sin espacios).
- El listado de parroquias (tarjetas con “próxima misa”) no forma parte de esta corrección.
- Cómo se captura o se guarda la hora al crear o editar un servicio no cambia.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: En la ficha de detalle de un templo, las horas de un mismo día y tipo de servicio MUST mostrarse como una lista de texto de 12 horas separada por comas (con un espacio después de cada coma).
- **FR-002**: En la pantalla de servicios registrados de un templo, las horas de un mismo día MUST mostrarse con el mismo formato de lista de 12 horas separada por comas.
- **FR-003**: Esa lista MUST NOT incluir corchetes, comillas, horario de 24 horas ni otra notación de programación alrededor de las horas o del conjunto.
- **FR-004**: Un día con una sola hora MUST mostrar solo esa hora en 12 horas, sin separador sobrante.
- **FR-005**: El conjunto de horas mostradas para un día y tipo MUST ser exactamente el conjunto de horas registradas para ese día y tipo, en el mismo orden en que ya se presentan hoy.
- **FR-006**: El agrupado existente por tipo de servicio y por día de la semana MUST permanecer; esta funcionalidad no cambia nombres de días ni tipos de servicio, solo cómo se escriben las horas al consultarlas.
- **FR-007**: Las pantallas públicas de consulta de horarios MUST seguir siendo accesibles sin iniciar sesión.
- **FR-008**: Cada hora en esas listas MUST mostrarse en reloj de 12 horas con marcador español `a. m.` o `p. m.` (espacios en el marcador), sin cero a la izquierda en la hora (`8:00 a. m.`, `12:00 p. m.`, `6:00 p. m.`), convertida solo al presentar la pantalla. MUST NOT usar `AM`/`PM` en inglés ni horario de 24 horas.
- **FR-009**: Cómo se registra y se guarda la hora MUST permanecer igual; esta funcionalidad MUST NOT alterar el valor almacenado ni exigir un cambio de captura en el formulario de alta.

### Key Entities

- **Templo**: Parroquia cuya ficha y pantalla de servicios muestran horarios.
- **Servicio**: Un horario concreto (tipo, día, hora). Varios servicios del mismo tipo y día se leen juntos como una lista de horas. La hora se guarda como hasta ahora; la lista de consulta solo cambia la forma de leerla.
- **Lista de horas del día**: Las horas de inicio de esos servicios, presentadas a la persona como texto `h:mm a. m.` / `h:mm p. m.` separado por comas.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: En un templo de ejemplo con al menos tres horas el mismo día (incluida al menos una de tarde), un visitante identifica todas las horas en menos de 5 segundos sin interpretar corchetes, comillas ni horario de 24 horas.
- **SC-002**: El 100 % de las horas registradas para un día y tipo aparecen en la lista de esa ficha; ninguna se omite ni se inventa.
- **SC-003**: En una revisión de las pantallas de detalle de servicios (ficha pública y listado de edición), el 100 % de las filas de día muestran horas como lista `a. m.` / `p. m.` separada por comas y el 0 % muestran corchetes, comillas de delimitación, `AM`/`PM` en inglés o valores de 24 horas.
- **SC-004**: Un día con una sola hora se lee como un único valor (por ejemplo `8:00 a. m.`, sin coma final ni cero a la izquierda) en ambas pantallas.
- **SC-005**: Tras mostrar y consultar una ficha, la hora registrada del servicio sigue siendo la misma que antes de abrir la pantalla (el almacenamiento no cambia).

## Assumptions

- El separador visible es coma seguida de un espacio (convención habitual en español).
- El reloj de 12 horas usa marcadores en español `a. m.` y `p. m.` (Ortografía de la lengua española), sin cero a la izquierda en la hora (`8:00 a. m.`, no `08:00 a. m.`).
- El orden de las horas dentro de un día es el orden que ya usa el directorio; no se pide un reordenamiento nuevo (por ejemplo, no se exige ordenar de mañana a noche si hoy no se hace).
- El listado de parroquias (tarjetas con próxima misa y enlace a “ver todos los servicios”) queda fuera de alcance: no muestra la lista por día.
- No se agregan, editan ni borran servicios en esta funcionalidad; solo cambia la forma de leer las horas ya guardadas.
- No se introducen campos nuevos ni se cambia el significado de tipo de servicio o día de la semana.
- El formulario para indicar hora de inicio o de fin al crear un servicio queda fuera de este cambio de presentación.
