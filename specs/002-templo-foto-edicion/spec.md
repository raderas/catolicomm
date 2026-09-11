# Feature Specification: Foto y edición de datos del templo

**Feature Branch**: `002-templo-foto-edicion`

**Created**: 2026-09-11

**Status**: Implemented

**Input**: User description: "agrega funcionalidad para subir una foto del templo en la pagina de creación del templo. Agregar también página y templates para editar un templo existente a nivel de nombre, direccion, alias y/o fotografía."

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Subir una foto al crear un templo (Priority: P1)

Un editor autenticado abre la pantalla de alta de un templo, completa nombre y dirección (y, si aplica, otro nombre conocido), adjunta una fotografía del edificio y guarda. El templo queda registrado con esa imagen para que la comunidad lo reconozca.

**Why this priority**: Sin foto en el alta, el directorio sigue mostrando parroquias sin imagen. Es el momento natural de asociar la fotografía al templo nuevo.

**Independent Test**: Un usuario autenticado crea un templo con nombre, dirección y una foto válida, y luego ve esa misma foto en la ficha pública y en el listado.

**Acceptance Scenarios**:

1. **Given** un editor autenticado en la pantalla de alta, **When** completa nombre y dirección, elige una fotografía válida y guarda, **Then** el templo se crea y esa foto queda asociada de forma permanente.
2. **Given** un editor autenticado en la pantalla de alta, **When** completa nombre y dirección y guarda **sin** fotografía, **Then** el templo se crea y las pantallas públicas muestran el marcador visual de “sin foto” (no una imagen rota).
3. **Given** un editor autenticado en la pantalla de alta, **When** intenta guardar sin nombre o sin dirección, **Then** ve un mensaje de error en español junto al formulario y no se crea el templo.
4. **Given** un editor autenticado en la pantalla de alta, **When** intenta adjuntar un archivo que no es una imagen aceptada, **Then** ve un mensaje de error en español y el templo no se crea con ese archivo.

---

### User Story 2 - Corregir nombre, dirección o alias de un templo existente (Priority: P1)

Un editor autenticado abre la pantalla de edición de un templo ya registrado, cambia uno o más de estos datos (nombre, dirección, otro nombre conocido) y guarda. La comunidad ve de inmediato los datos actualizados; los que no tocó permanecen igual.

**Why this priority**: Los nombres y direcciones cambian o se cargan mal. Sin una pantalla de edición, el directorio no se puede mantener a nivel de ficha, solo de horarios.

**Independent Test**: Con un templo existente, un usuario autenticado cambia solo el nombre (o solo la dirección, o solo el alias), guarda, y confirma el cambio en la ficha pública sin alterar los demás campos.

**Acceptance Scenarios**:

1. **Given** un templo existente y un editor autenticado en su pantalla de edición, **When** modifica el nombre y guarda, **Then** la ficha pública y el listado muestran el nombre nuevo; dirección, alias y foto no cambian.
2. **Given** un templo existente y un editor autenticado en su pantalla de edición, **When** modifica la dirección y/o el alias y guarda, **Then** esos campos se actualizan y el resto permanece.
3. **Given** un editor autenticado en la pantalla de edición, **When** intenta guardar dejando el nombre o la dirección vacíos, **Then** ve un mensaje de error en español y los datos anteriores no se pierden.
4. **Given** un visitante en la ficha pública de un templo, **When** usa el enlace para editar los datos del templo, **Then** (si está autenticado) llega a esa pantalla de edición con los valores actuales ya rellenados.

---

### User Story 3 - Agregar o cambiar la foto de un templo existente (Priority: P1)

El mismo editor, en la pantalla de edición, adjunta una fotografía nueva (si el templo no tenía) o reemplaza la que ya existe, sin verse obligado a reescribir nombre, dirección o alias.

**Why this priority**: Muchos templos ya están dados de alta sin imagen. Poder añadir o sustituir la foto después del alta evita recrear la parroquia.

**Independent Test**: Con un templo con o sin foto, un usuario autenticado guarda solo una imagen nueva y confirma que se muestra en ficha y listado, con el resto de datos intactos.

**Acceptance Scenarios**:

1. **Given** un templo sin fotografía, **When** un editor autenticado adjunta una imagen válida y guarda, **Then** la ficha pública y el listado muestran esa foto.
2. **Given** un templo que ya tiene fotografía, **When** un editor autenticado adjunta otra imagen válida y guarda, **Then** la comunidad ve la foto nueva (no la anterior) en ficha y listado.
3. **Given** un templo con o sin fotografía, **When** un editor autenticado guarda cambios de texto **sin** elegir un archivo nuevo, **Then** la foto (o la ausencia de foto) permanece igual.
4. **Given** un editor autenticado en la pantalla de edición, **When** intenta adjuntar un archivo que no es una imagen aceptada, **Then** ve un mensaje de error en español y la foto anterior (si había) no se pierde.

---

### User Story 4 - Solo quienes iniciaron sesión pueden crear o editar un templo (Priority: P1)

Quien no ha iniciado sesión no ve ni envía el alta ni la edición de datos del templo. Si intenta abrir esas pantallas, se le pide iniciar sesión. Tras autenticarse, llega a la pantalla que quería. La consulta pública del directorio y de la ficha no cambia.

**Why this priority**: Nombre, dirección y foto son datos de la comunidad; solo personas identificadas deben poder mutarlos. El directorio de consulta sigue abierto.

**Independent Test**: Un visitante sin sesión no puede ver ni enviar alta ni edición; un usuario con sesión sí.

**Acceptance Scenarios**:

1. **Given** un visitante sin sesión, **When** intenta abrir el alta o la edición de un templo, **Then** no ve el formulario y se le pide iniciar sesión.
2. **Given** un visitante sin sesión enviado a iniciar sesión desde el alta o la edición, **When** inicia sesión correctamente, **Then** llega a la misma pantalla que había solicitado.
3. **Given** un usuario autenticado, **When** abre el alta o la edición de un templo existente, **Then** ve el formulario en español, con el mismo lenguaje visual del directorio (tarjetas, paleta crema/dorado, tipografía de títulos).
4. **Given** un visitante sin sesión en el directorio o en la ficha pública, **When** consulta nombre, dirección y foto, **Then** puede verlos sin iniciar sesión.

---

### Edge Cases

- Templo inexistente: el usuario autenticado no llega a una pantalla de edición vacía o rota; ve una indicación de que el templo no existe.
- Sesión caducada a mitad de completar el formulario: al guardar, se pide iniciar sesión de nuevo y no se aplica el cambio.
- Archivo demasiado grande para un uso razonable en el directorio: se rechaza con un mensaje en español y no se guarda.
- Formatos no imagen (documento, vídeo, archivo vacío): se rechazan; no se asocia ningún archivo inválido al templo.
- Alias vacío: está permitido; el templo se guarda o actualiza sin otro nombre conocido.
- Foto opcional en alta y en edición: nunca se exige una imagen para completar la operación de texto.
- Tras un alta o una edición válidas, la consulta pública refleja de inmediato los datos reales (sin inventar foto, nombre o dirección).
- Mensajes de éxito o error no rompen el diseño de la tarjeta del formulario.
- Esta función no elimina un templo ni cambia sus horarios de servicio; eso sigue en las pantallas ya existentes.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: El sistema MUST permitir a un editor autenticado crear un templo indicando nombre, dirección, alias opcional y una fotografía opcional, en la pantalla de alta ya existente.
- **FR-002**: El sistema MUST persistir la fotografía adjuntada en el alta y MUST asociarla a ese templo para consulta pública.
- **FR-003**: El sistema MUST ofrecer una pantalla de edición de un templo existente, con los valores actuales de nombre, dirección, alias y fotografía (si hay) ya visibles o rellenados.
- **FR-004**: En esa pantalla de edición, el editor MUST poder cambiar nombre, dirección, alias y/o fotografía, de forma independiente: un campo no modificado MUST conservar su valor anterior.
- **FR-005**: Nombre y dirección MUST ser obligatorios en alta y en edición. Si faltan, el sistema MUST mostrar error en español y MUST NOT crear ni sobrescribir el templo con datos incompletos.
- **FR-006**: El alias MUST ser opcional (puede quedar vacío) en alta y en edición.
- **FR-007**: La fotografía MUST ser opcional en alta y en edición. Guardar sin elegir archivo MUST crear o actualizar el templo sin exigir imagen y MUST NOT borrar una foto ya existente.
- **FR-008**: Si el editor adjunta una imagen válida en edición, el sistema MUST reemplazar la fotografía anterior (o añadirla si no había).
- **FR-009**: El sistema MUST aceptar solo archivos de imagen habituales para este uso (fotografía de edificio o fachada). MUST rechazar otros tipos de archivo con un mensaje en español y MUST NOT asociarlos al templo.
- **FR-010**: El directorio público y la ficha pública del templo MUST mostrar la fotografía asociada cuando exista, y el marcador visual de “sin foto” cuando no exista. MUST NOT mostrar una imagen rota.
- **FR-011**: Tras un alta o una edición válidas, las pantallas públicas MUST mostrar los datos reales actualizados (nombre, dirección, alias si se usa, y foto o ausencia de foto).
- **FR-012**: La ficha pública MUST ofrecer un enlace hacia la pantalla de edición de datos del templo, análogo al enlace ya existente para agregar servicios.
- **FR-013**: Visitantes no autenticados MUST NOT poder ver ni enviar el alta ni la edición de datos del templo. MUST ser redirigidos a iniciar sesión y, tras autenticarse, MUST volver a la pantalla solicitada.
- **FR-014**: Usuarios autenticados MUST poder abrir el alta y la edición de cualquier templo existente (en esta iteración no se restringe por parroquia asignada).
- **FR-015**: Toda la copia de alta y edición MUST estar en español, incluyendo etiquetas, botones, vacíos, éxitos y errores.
- **FR-016**: Las pantallas de alta y de edición MUST reutilizar el lenguaje visual del directorio de parroquias: tarjetas, paleta crema/dorado, tipografía de títulos y acción principal destacada. MUST NOT introducir otro sistema visual.
- **FR-017**: Esta función MUST NOT eliminar templos ni crear, modificar o borrar horarios de servicio.

### Key Entities

- **Templo**: Parroquia o iglesia del directorio, identificada por nombre y dirección, con un alias opcional (otro nombre conocido) y una fotografía opcional de su edificio o fachada.
- **Fotografía del templo**: Imagen asociada a un templo, visible en el listado y en la ficha pública. Puede faltar; si existe, es única (una foto vigente por templo).
- **Editor autenticado**: Persona que ha iniciado sesión y por ello puede crear templos y editar nombre, dirección, alias y foto. En esta iteración no se modela pertenencia a una parroquia concreta.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: Un editor autenticado puede dar de alta un templo con foto válida y ver esa foto en la ficha pública en menos de dos minutos.
- **SC-002**: Un editor autenticado puede corregir nombre, dirección o alias de un templo existente y ver el cambio en la ficha pública en menos de un minuto, sin rehacer los campos que no quería tocar.
- **SC-003**: Un editor autenticado puede añadir o reemplazar la foto de un templo existente en menos de un minuto, sin verse obligado a reescribir nombre ni dirección.
- **SC-004**: En el 100 % de los intentos, un visitante sin sesión no ve ni envía el alta ni la edición, y es invitado a iniciar sesión antes de continuar.
- **SC-005**: En el 100 % de las fichas y tarjetas del listado, o se ve la foto real del templo o el marcador de “sin foto”; ninguna muestra una imagen rota.
- **SC-006**: En el 100 % de los intentos de adjuntar un archivo que no es imagen aceptada, el editor ve un mensaje de error y los datos previos del templo (incluido, si había, la foto) permanecen.
- **SC-007**: Al menos 9 de cada 10 editores reconocen las pantallas de alta y edición como parte del mismo directorio (misma paleta, tarjetas y tipografía), no como un formulario desconectado.

## Assumptions

- Se reutiliza el sistema de cuentas ya disponible; esta función no inventa un nuevo método de identidad.
- Cualquier usuario autenticado puede crear templos y editar los datos de cualquier templo. La restricción por parroquia de la constitución (un editor no cambia registros de otra parroquia) queda fuera de esta iteración; hará falta un vínculo usuario–templo en un trabajo posterior.
- La fotografía se sube como archivo desde el dispositivo del editor, no como enlace a una imagen externa.
- Una sola foto vigente por templo es suficiente; no hay galería ni recorte avanzado en esta iteración.
- No entra en alcance quitar una foto existente sin sustituirla por otra (solo añadir, conservar o reemplazar).
- Nombre y dirección siguen siendo los campos indispensables de la ficha; el alias es el “otro nombre conocido” que el dominio ya contempla.
- El alta de templo ya existe; esta función añade la foto y alinea el acceso autenticado. La edición de ficha (nombre, dirección, alias y foto) es una pantalla nueva.
- El enlace desde la ficha pública hacia la edición se añade de forma similar al de “Agregar servicio”.
- Los horarios de misa y demás servicios no se editan en estas pantallas; siguen en la pantalla de servicios ya especificada.
- Las pantallas públicas de listado y ficha ya contemplan mostrar una foto o un marcador; esta función alimenta esa imagen real.
- Formatos aceptados: imágenes de uso cotidiano (por ejemplo las que produce un teléfono). Un tope de tamaño razonable evita archivos que no sirven para el directorio.
- La verificación en navegador (o el sustituto más cercano) es parte del cierre de la función, además de pruebas del camino crítico de alta y edición de templo.
