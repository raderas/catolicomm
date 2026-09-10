# Feature Specification: Editor de servicios del templo

**Feature Branch**: `001-servicios-editor-ui`

**Created**: 2026-09-10

**Status**: Draft

**Input**: User description: "embellece el template misas/templates/misas/edit_servicios.html para que muestre los servicios creados en la parte baja de la pantalla y el formulario para crear nuevos servicios en donde ya está ubicado el form. Sigue los patrones de la pagina index.html con bootstrap. Esta página solo debe estar accesible para usuarios logueados en la aplicación"

## Clarifications

### Session 2026-09-10

- Q: ¿Debe rechazarse un servicio nuevo que duplique o se solape con uno existente del mismo tipo? → A: Sí. Si el editor ingresa un servicio del mismo tipo y la misma hora que uno ya registrado, o si el horario se traslapa con un servicio existente del mismo tipo que tiene hora de fin, el sistema muestra un mensaje y no crea el registro.
- Q: Si un servicio nuevo del mismo tipo empieza justo cuando termina uno existente, ¿se permite o se trata como traslape? → A: Permitir: 10:00–11:00 y 11:00–12:00 del mismo tipo son válidos (solo se tocan en el borde; no es traslape).

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Crear un servicio con el formulario existente (Priority: P1)

Un editor autenticado abre la pantalla de servicios de un templo, completa el formulario que ya aparece en la parte superior (tipo de servicio, día de la semana, hora de inicio y hora de fin) y guarda. El nuevo horario queda registrado para ese templo.

**Why this priority**: Registrar horarios es el propósito de esta pantalla. Sin un formulario usable y coherente con el resto del sitio, no hay valor para la comunidad.

**Independent Test**: Un usuario autenticado puede abrir la pantalla de un templo, enviar un servicio válido y ver confirmación de que se guardó.

**Acceptance Scenarios**:

1. **Given** un usuario autenticado en la pantalla de servicios de un templo, **When** completa tipo, día y horas válidas y guarda, **Then** el servicio queda asociado a ese templo y el formulario queda listo para agregar otro.
2. **Given** un usuario autenticado en esa pantalla, **When** envía el formulario con datos incompletos o inválidos, **Then** ve mensajes de error claros junto al formulario y no se crea un servicio.
3. **Given** un usuario autenticado, **When** abre la pantalla, **Then** el formulario de alta está en la zona superior (debajo de la cabecera del templo), con el mismo lenguaje visual que el directorio de parroquias: tarjetas, paleta crema/dorado, tipografía serif en títulos y acción principal destacada.

---

### User Story 2 - Ver los servicios ya creados debajo del formulario (Priority: P1)

El mismo editor, sin salir de la pantalla, ve en la parte baja todos los servicios ya registrados de ese templo, agrupados de forma que pueda distinguir tipo, día y hora de un vistazo.

**Why this priority**: Hoy el listado es difícil de leer. El editor necesita confirmar qué horarios existen antes y después de agregar uno nuevo.

**Independent Test**: Con un templo que ya tiene varios servicios, un usuario autenticado abre la pantalla y reconoce tipo, día y hora de cada uno en la zona inferior.

**Acceptance Scenarios**:

1. **Given** un templo con servicios de distintos tipos y días, **When** un usuario autenticado abre la pantalla, **Then** esos servicios aparecen debajo del formulario, agrupados por tipo de servicio, con día y hora visibles.
2. **Given** un templo sin servicios, **When** un usuario autenticado abre la pantalla, **Then** la zona inferior muestra un mensaje claro de que aún no hay horarios, no un bloque vacío sin explicación.
3. **Given** un usuario autenticado que acaba de guardar un servicio válido, **When** la pantalla se refresca, **Then** el nuevo horario aparece en el listado inferior sin que el usuario tenga que ir a otra página para confirmarlo.
4. **Given** el directorio público de parroquias como referencia visual, **When** se compara el listado inferior, **Then** usa el mismo tratamiento de tarjetas, bordes suaves, fondo crema y jerarquía tipográfica, no un listado sin estilo.

---

### User Story 3 - Solo quienes iniciaron sesión pueden abrir esta pantalla (Priority: P1)

Quien no ha iniciado sesión no ve el formulario ni los horarios de edición. Si intenta abrir la dirección de esta pantalla, se le pide iniciar sesión. Tras autenticarse, llega a la pantalla del templo que quería editar.

**Why this priority**: Los horarios de misa y confesión son datos sensibles para la comunidad; solo personas identificadas deben poder crearlos. El directorio público de consulta no cambia.

**Independent Test**: Un visitante sin sesión no puede ver ni enviar el formulario; un usuario con sesión sí.

**Acceptance Scenarios**:

1. **Given** un visitante sin sesión, **When** intenta abrir la pantalla de servicios de un templo, **Then** no ve el formulario ni el listado de edición y se le pide iniciar sesión.
2. **Given** un visitante sin sesión que fue enviado a iniciar sesión desde esta pantalla, **When** inicia sesión correctamente, **Then** llega a la pantalla de servicios de ese mismo templo.
3. **Given** un usuario autenticado, **When** abre la pantalla de un templo existente, **Then** ve cabecera del templo, formulario de alta y listado de servicios actuales.
4. **Given** un visitante sin sesión en la ficha pública de un templo, **When** usa el enlace para agregar un servicio, **Then** se le pide iniciar sesión en lugar de mostrar el editor.

---

### User Story 4 - Rechazar horarios duplicados o superpuestos del mismo tipo (Priority: P1)

Un editor autenticado intenta guardar un servicio que ya existe en ese templo (mismo tipo y misma hora de inicio, el mismo día) o cuyo intervalo se cruza con otro servicio del mismo tipo que ya tiene hora de fin. Ve un mensaje en el formulario y el horario no se registra.

**Why this priority**: Un directorio con dos misas a la misma hora, o intervalos que se pisan, deja de ser fiable para la comunidad. Bloquear el alta evita datos contradictorios.

**Independent Test**: Con un templo que ya tiene un servicio, un usuario autenticado intenta guardar un duplicado o un intervalo que se cruza y confirma que aparece el mensaje y que el listado inferior no cambia.

**Acceptance Scenarios**:

1. **Given** un templo con un servicio de un tipo, día y hora de inicio ya registrados, **When** un editor autenticado intenta guardar otro del mismo tipo, mismo día y misma hora de inicio, **Then** ve un mensaje de conflicto en la zona del formulario y no se crea un segundo registro.
2. **Given** un templo con un servicio del mismo tipo y día que tiene hora de fin, **When** un editor autenticado intenta guardar un horario cuyo intervalo se cruza con ese (por ejemplo, el existente es 10:00–11:00 y el nuevo empieza a las 10:30), **Then** ve un mensaje de conflicto y no se crea el registro.
3. **Given** un templo con un servicio 10:00–11:00 de un tipo, **When** un editor autenticado guarda otro del mismo tipo 11:00–12:00 el mismo día, **Then** el alta se acepta (coincidir solo en el borde no es traslape).
4. **Given** un templo con un servicio de un tipo a una hora, **When** un editor autenticado guarda un servicio de **otro** tipo en el mismo día y hora, **Then** el alta se acepta (la restricción aplica solo al mismo tipo).
5. **Given** un conflicto de duplicado o traslape, **When** el alta se rechaza, **Then** el listado inferior sigue mostrando exactamente los servicios que ya existían.

---

### Edge Cases

- Templo inexistente: el usuario autenticado no llega a una pantalla de edición vacía o rota; ve una indicación de que el templo no existe.
- Formulario con hora de fin anterior a la de inicio: se muestra error y no se guarda.
- Muchos servicios en un mismo templo: el listado inferior sigue siendo legible (agrupado, no una sola lista plana ilegible).
- Sesión caducada a mitad de completar el formulario: al guardar, se pide iniciar sesión de nuevo y no se crea el servicio.
- Mensajes de éxito o error de validación no deben romper el diseño de la tarjeta del formulario.
- La consulta pública de horarios (listado y ficha del templo) sigue disponible sin iniciar sesión.
- Duplicado exacto (mismo templo, tipo, día y hora de inicio): mensaje de conflicto, sin registro nuevo.
- Traslape con un servicio existente del mismo tipo, mismo día y con hora de fin: mensaje de conflicto, sin registro nuevo. Coincidir solo en el borde (uno termina a las 11:00 y el siguiente empieza a las 11:00) no es traslape y se permite.
- Un servicio de otro tipo en el mismo día y franja no se considera conflicto.
- Un servicio del mismo tipo en **otro** día de la semana no se considera conflicto.
- Si el servicio existente no tiene hora de fin, solo se bloquea la coincidencia de tipo + día + hora de inicio (no hay intervalo contra el que medir traslape).

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: El sistema MUST mostrar, para un templo existente, una pantalla de edición con la cabecera del templo, un formulario de alta de servicio en la zona superior y el listado de servicios ya creados en la zona inferior.
- **FR-002**: El formulario MUST permitir indicar tipo de servicio, día de la semana, hora de inicio y hora de fin, y MUST asociar el nuevo servicio al templo de esa pantalla.
- **FR-003**: Tras un alta válida, el sistema MUST persistir el servicio y MUST mostrar ese horario en el listado inferior de la misma pantalla.
- **FR-004**: Si el formulario no es válido, el sistema MUST mostrar los errores en la zona del formulario y MUST NOT crear el servicio.
- **FR-005**: El listado inferior MUST agrupar los servicios existentes por tipo y MUST mostrar día y hora de cada uno, usando los datos reales del templo (sin inventar ni omitir horarios).
- **FR-006**: Si el templo no tiene servicios, el listado inferior MUST mostrar un estado vacío en español, comprensible para el editor.
- **FR-007**: La pantalla MUST reutilizar el lenguaje visual del directorio de parroquias: tarjetas con sombra suave, bordes discretos, paleta crema/dorado, títulos con jerarquía clara, campos de formulario alineados y un botón de acción principal destacado. MUST NOT introducir otro sistema visual.
- **FR-008**: Toda la copia de esta pantalla MUST estar en español, incluyendo etiquetas, botones, vacíos, éxitos y errores.
- **FR-009**: Visitantes no autenticados MUST NOT poder ver ni enviar esta pantalla. MUST ser redirigidos a iniciar sesión y, tras autenticarse, MUST volver a la pantalla del templo solicitado.
- **FR-010**: Usuarios autenticados MUST poder abrir esta pantalla para cualquier templo existente (en esta iteración no se restringe por parroquia asignada).
- **FR-011**: El directorio público y la ficha pública del templo MUST seguir consultables sin autenticación. Solo la pantalla de alta/edición de servicios queda restringida.
- **FR-012**: El enlace público “Agregar servicio” (o equivalente) MUST respetar FR-009: un visitante sin sesión no alcanza el editor.
- **FR-013**: El sistema MUST rechazar un alta cuando, en el mismo templo, ya existe un servicio del mismo tipo, el mismo día de la semana y la misma hora de inicio. MUST mostrar un mensaje de conflicto en el formulario y MUST NOT crear el registro.
- **FR-014**: El sistema MUST rechazar un alta cuando, en el mismo templo y el mismo día, el intervalo del nuevo servicio se traslapa con un servicio existente del mismo tipo que tiene hora de fin. El intervalo se trata como cerrado en la hora de inicio y abierto en la hora de fin: coincidir solo en el borde (el nuevo empieza exactamente cuando el existente termina, o al revés) MUST permitirse. MUST mostrar un mensaje de conflicto en el formulario cuando sí hay traslape y MUST NOT crear el registro.
- **FR-015**: Los mensajes de FR-013 y FR-014 MUST estar en español, visibles junto al formulario, y MUST dejar el listado inferior sin cambios.

### Key Entities

- **Templo**: Parroquia o iglesia cuyos horarios se editan; identificado en la cabecera de la pantalla.
- **Servicio**: Horario de un tipo concreto (misa, confesión u otro tipo ya definido) en un día y franja horaria, siempre ligado a un templo. En un mismo templo, no pueden coexistir dos servicios del mismo tipo con la misma hora de inicio el mismo día, ni intervalos del mismo tipo que se pisen (coincidir solo en el borde está permitido) cuando el existente tiene hora de fin.
- **Editor autenticado**: Persona que ha iniciado sesión y por ello puede crear servicios. En esta iteración no se modela pertenencia a una parroquia concreta.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: Un editor autenticado puede registrar un horario válido y verlo en el listado inferior en menos de un minuto, sin ir a otra pantalla para confirmarlo.
- **SC-002**: En el 100 % de los intentos, un visitante sin sesión no ve el contenido del editor y es invitado a iniciar sesión antes de continuar.
- **SC-003**: Un editor puede identificar tipo, día y hora de cada servicio existente en menos de 10 segundos al mirar la zona inferior (incluido el caso de varios tipos).
- **SC-004**: Al menos 9 de cada 10 editores reconocen la pantalla como parte del mismo directorio (misma paleta, tarjetas y tipografía que el listado de parroquias), no como un formulario desconectado.
- **SC-005**: Un templo sin servicios muestra un mensaje de vacío; ninguno de esos casos deja la zona inferior en blanco sin explicación.
- **SC-006**: La consulta pública de horarios no requiere iniciar sesión y sigue mostrando los datos reales del templo.
- **SC-007**: En el 100 % de los intentos de alta duplicada (mismo tipo, día y hora de inicio) o de traslape con un servicio del mismo tipo que tiene hora de fin, el editor ve un mensaje de conflicto y no aparece un registro nuevo en el listado.

## Assumptions

- Se reutiliza el sistema de cuentas ya disponible en la aplicación; esta función no inventa un nuevo método de identidad (correo mágico, redes sociales, etc.).
- Cualquier usuario autenticado puede editar servicios de cualquier templo. La restricción por parroquia de la constitución (un editor no cambia registros de otra parroquia) queda fuera de esta iteración; hará falta un vínculo usuario–templo en un trabajo posterior.
- No entra en alcance eliminar ni modificar un servicio ya creado; solo listarlo y crear nuevos. El comentario de “botones para eliminar” en el diseño actual no forma parte de esta especificación.
- El formulario de alta permanece donde ya está (zona superior, bajo la cabecera del templo); el cambio es de presentación y de listado inferior, no de reubicar el alta a otra página.
- Los tipos de servicio, días y formato de hora son los que el dominio ya usa; no se agregan tipos nuevos.
- El enlace desde la ficha pública del templo hacia esta pantalla se mantiene; el control de acceso cubre a quien no ha iniciado sesión.
- La verificación en navegador (o el sustituto más cercano) es parte del cierre de la función, además de pruebas del camino crítico de horarios.
- La comparación de duplicado y traslape es por templo, tipo de servicio y día de la semana. Tipos distintos pueden compartir día y hora.
- “Misma hora” en el duplicado significa la misma hora de inicio.
- El control de traslape solo aplica contra servicios existentes que tienen hora de fin; si el existente no la tiene, solo rige la regla de duplicado de hora de inicio.
- Dos servicios del mismo tipo que solo se tocan en el borde (fin de uno = inicio del otro) son válidos; el traslape exige que los intervalos se pisen en algún momento interior.
