# Feature Specification: Crear cuenta, verificar correo y recuperar contraseña

**Feature Branch**: `005-crear-cuenta`

**Created**: 2026-09-14

**Status**: **Implemented**

**Input**: User description: "Agregar boton para crear cuenta en el formulario de login y formularios para ingresar datos de un usuario para generarle una cuenta. Debe pedir un nombre de usuario, un correo de contacto y una contraseña con las características manejadas por django." Amendment: add email verification (account not usable until the contact email is confirmed) and password reset from the login flow.

## User Scenarios & Testing *(mandatory)*



### User Story 1 - Encontrar “Crear cuenta” y “Olvidé mi contraseña” en el acceso (Priority: P1)

Un visitante que aún no tiene cuenta abre la pantalla de iniciar sesión y ve, junto al formulario de acceso, una acción clara en español para crear una cuenta. También ve una acción para recuperar la contraseña si ya tiene cuenta y la olvidó. Al usar “Crear cuenta”, llega a la pantalla donde puede registrar sus datos. Quien ya inició sesión no necesita esas acciones: sigue tratándose como persona identificada.

**Why this priority**: Sin un camino visible desde el acceso, una persona nueva no puede darse de alta y quien olvidó su contraseña no tiene recobro. El formulario de acceso solo sirve si ya hay credenciales vigentes.

**Independent Test**: Un visitante sin sesión abre iniciar sesión, ve “Crear cuenta” y “Olvidé mi contraseña”, pulsa “Crear cuenta” y llega al formulario de alta. El formulario de iniciar sesión existente sigue funcionando para cuentas ya confirmadas.

**Acceptance Scenarios**:

1. **Given** un visitante sin sesión en la pantalla de iniciar sesión, **When** mira la pantalla, **Then** ve un botón o enlace en español para crear una cuenta y otro para recuperar la contraseña, además del formulario habitual de usuario y contraseña.
2. **Given** un visitante sin sesión en iniciar sesión, **When** pulsa “Crear cuenta”, **Then** llega a la pantalla de alta de cuenta (nombre de usuario, correo de contacto y contraseña).
3. **Given** un visitante sin sesión en iniciar sesión, **When** ignora esas acciones e inicia sesión con una cuenta ya confirmada, **Then** el acceso funciona igual que hoy.
4. **Given** una persona que ya tiene sesión, **When** llega a la pantalla de iniciar sesión (por un enlace antiguo o guardado), **Then** no se le muestra el alta ni la recuperación como si fuera visitante; se le trata como persona ya identificada.

---



### User Story 2 - Registrar una cuenta y esperar el correo de confirmación (Priority: P1)

El visitante completa el alta: elige un nombre de usuario, indica un correo de contacto y define una contraseña que cumple las reglas de seguridad ya vigentes en el directorio. Al enviar datos válidos, el sistema crea la cuenta **sin iniciar sesión**, envía un correo de confirmación a esa dirección y muestra una pantalla en español indicando que debe revisar su correo. Hasta confirmar, no puede usar funciones que requieren cuenta (Mi perfil, editar horarios).

**Why this priority**: Es el valor de la función de alta, ahora con la salvaguarda de que el correo de contacto es real antes de conceder escritura en el directorio.

**Independent Test**: Un visitante sin cuenta completa el formulario con datos válidos: se crea la cuenta, llega un correo de confirmación, la persona sigue como visitante y un intento de iniciar sesión con esas credenciales no entra hasta confirmar.

**Acceptance Scenarios**:

1. **Given** un visitante en la pantalla de alta, **When** mira el formulario, **Then** ve campos obligatorios en español para nombre de usuario, correo de contacto y contraseña, y un campo para repetir la contraseña y confirmarla.
2. **Given** un visitante que ingresa un nombre de usuario libre, un correo de contacto con formato válido y una contraseña que cumple las reglas vigentes (y la confirma igual), **When** envía el formulario, **Then** se crea su cuenta, se envía un correo de confirmación a esa dirección y ve una pantalla en español pidiéndole que revise su correo. **Then** no queda identificada (no hay sesión).
3. **Given** una persona que acaba de crear su cuenta y aún no confirma, **When** intenta iniciar sesión con ese nombre de usuario y contraseña, **Then** no entra y ve un mensaje en español de que la cuenta aún no está confirmada.
4. **Given** una persona que acaba de crear su cuenta y aún no confirma, **When** intenta abrir Mi perfil o editar horarios, **Then** se le pide identificarse y, aunque use esas credenciales, no accede a esas funciones hasta confirmar.

---



### User Story 3 - Recibir errores claros si el alta no es válida (Priority: P1)

Si falta un dato, el nombre de usuario ya existe, el correo no es un correo válido o la contraseña no cumple las reglas vigentes, el sistema no crea la cuenta, no envía correo y explica el problema en español junto al formulario, sin perder innecesariamente el resto de los datos ingresados (salvo la contraseña, que no se vuelve a mostrar).

**Why this priority**: Un alta que falla en silencio o con un error técnico deja a la persona sin cuenta y sin saber qué corregir. Las reglas de contraseña solo sirven si se comunican.

**Independent Test**: Intentar altas inválidas (usuario duplicado, correo mal escrito, contraseña débil, confirmación distinta, campos vacíos) muestra mensajes en español, no crea cuenta y no envía correo; un reintento con datos válidos sí crea la cuenta y envía el correo de confirmación.

**Acceptance Scenarios**:

1. **Given** un visitante que deja vacío el nombre de usuario, el correo o la contraseña, **When** envía el formulario, **Then** ve un mensaje en español indicando qué falta, no se crea ninguna cuenta y no se envía correo.
2. **Given** un nombre de usuario que ya pertenece a otra cuenta, **When** el visitante intenta usarlo, **Then** ve un mensaje en español de que ese nombre no está disponible y no se crea una segunda cuenta con ese nombre.
3. **Given** un texto que no es un correo (sin “@” o formato inválido), **When** el visitante lo envía como correo de contacto, **Then** ve un mensaje en español y no se crea la cuenta.
4. **Given** una contraseña que no cumple las reglas vigentes (demasiado corta, demasiado parecida al nombre de usuario o al correo, demasiado común, o solo números), **When** el visitante la envía, **Then** ve en español la razón del rechazo y no se crea la cuenta.
5. **Given** una contraseña válida y una confirmación distinta, **When** el visitante envía el formulario, **Then** ve un mensaje en español de que las contraseñas no coinciden y no se crea la cuenta.

---



### User Story 4 - Confirmar el correo y activar la cuenta (Priority: P1)

La persona abre el correo de confirmación, pulsa el enlace y su cuenta queda habilitada. Tras confirmar, queda identificada (sesión iniciada) y puede usar el directorio con esa cuenta: ver Mi perfil (usuario y correo, nunca la contraseña) y las mismas acciones autenticadas que un colaborador ya existente. Si cierra sesión, vuelve a entrar con el mismo nombre de usuario y contraseña.

**Why this priority**: Sin este paso el alta no entrega una cuenta usable. Es el cierre del registro público.

**Independent Test**: Tras un alta válido, seguir el enlace del correo activa la cuenta, inicia sesión y permite Mi perfil y un nuevo inicio de sesión posterior; un enlace inválido o caducado no activa nada.

**Acceptance Scenarios**:

1. **Given** una cuenta recién creada y aún no confirmada, **When** la persona pulsa un enlace de confirmación vigente recibido en su correo de contacto, **Then** la cuenta queda confirmada, queda identificada y puede abrir Mi perfil con el nombre de usuario y el correo registrados (sin ver la contraseña).
2. **Given** una cuenta ya confirmada por ese enlace, **When** cierra sesión y vuelve a iniciar sesión con el mismo nombre de usuario y contraseña, **Then** entra correctamente.
3. **Given** un enlace de confirmación inválido, caducado o ya usado, **When** la persona lo abre, **Then** ve un mensaje en español de que el enlace no es válido, la cuenta no confirmada sigue sin poder usarse y se le ofrece cómo pedir un correo nuevo.
4. **Given** una cuenta creada por un administrador o ya existente antes de esta función, **When** su dueño inicia sesión, **Then** no se le exige este correo de confirmación; sigue pudiendo entrar como hoy.

---



### User Story 5 - Reenviar el correo de confirmación (Priority: P2)

Quien no recibió el correo, lo perdió o dejó caducar el enlace puede pedir uno nuevo desde la pantalla de “revisa tu correo” y desde el mensaje de acceso de cuenta no confirmada, sin revelar si un nombre de usuario existe.

**Why this priority**: El correo es un punto de fallo frecuente. Sin reenvío, una persona queda atrapada con una cuenta inútil. No sustituye al camino feliz de un solo correo.

**Independent Test**: Pedir reenvío genera un nuevo enlace usable y deja sin efecto el anterior o al menos acepta solo un enlace vigente; la pantalla no dice si el usuario existe.

**Acceptance Scenarios**:

1. **Given** una cuenta aún no confirmada, **When** la persona pide reenviar el correo (desde la pantalla posterior al alta o desde el aviso de acceso), **Then** se envía un nuevo correo de confirmación al correo de contacto de esa cuenta.
2. **Given** un visitante que pide reenvío con un nombre de usuario inexistente o ya confirmado, **When** envía la solicitud, **Then** ve el mismo tipo de mensaje genérico en español (no se revela si la cuenta existe ni su estado) y no se envía un correo a un tercero.
3. **Given** un enlace de confirmación anterior y uno nuevo, **When** la persona usa el nuevo vigente, **Then** la cuenta se confirma. El enlace viejo ya no debe confirmar una cuenta.

---



### User Story 6 - Volver al acceso desde el alta (Priority: P2)

Quien abrió “Crear cuenta” por error, o ya recordó que tiene cuenta, puede volver a la pantalla de iniciar sesión sin completar el alta.

**Why this priority**: Evita dejar a la persona atrapada en el formulario de registro. Es complementario al camino principal, no lo sustituye.

**Independent Test**: Desde la pantalla de alta, un visitante usa una acción en español para volver a iniciar sesión y llega al formulario de acceso existente.

**Acceptance Scenarios**:

1. **Given** un visitante en la pantalla de alta, **When** mira la pantalla, **Then** ve una acción en español para volver a iniciar sesión.
2. **Given** un visitante en la pantalla de alta, **When** pulsa esa acción, **Then** llega a la pantalla de iniciar sesión y no se crea ninguna cuenta.

---



### User Story 7 - Recuperar la contraseña desde el acceso (Priority: P1)

Una persona que olvidó su contraseña, desde iniciar sesión, indica su **nombre de usuario**. Si esa cuenta está confirmada y tiene correo de contacto, recibe un correo con un enlace para elegir una contraseña nueva (mismas reglas de seguridad, con confirmación). Tras guardarla, puede iniciar sesión con la nueva contraseña; la anterior deja de servir. El sistema no revela si el nombre de usuario existe.

**Why this priority**: El alta público no sirve de nada si una persona pierde la contraseña y no hay recobro. Pedir el nombre de usuario (no el correo) respeta que varias cuentas pueden compartir un correo parroquial.

**Independent Test**: Desde login, pedir restablecimiento con un usuario confirmado que tiene correo: llega el enlace, se define una contraseña válida, el acceso antiguo falla y el nuevo entra. Usuarios inexistentes, no confirmados o sin correo ven el mismo mensaje genérico.

**Acceptance Scenarios**:

1. **Given** un visitante sin sesión en iniciar sesión, **When** pulsa “Olvidé mi contraseña”, **Then** llega a un formulario en español que pide el nombre de usuario (el mismo con el que se inicia sesión), no el correo.
2. **Given** una cuenta confirmada con correo de contacto, **When** se solicita el restablecimiento con ese nombre de usuario, **Then** la persona ve un mensaje genérico en español de que, si la cuenta existe, se envió un correo, y recibe un enlace vigente en su correo de contacto.
3. **Given** ese enlace vigente, **When** la persona elige una contraseña que cumple las reglas y la confirma, **Then** la nueva contraseña queda guardada y puede iniciar sesión con ella. La contraseña anterior ya no funciona.
4. **Given** una contraseña nueva que no cumple las reglas o no coincide con su confirmación, **When** la envía, **Then** ve el error en español y la contraseña anterior sigue vigente.
5. **Given** un nombre de usuario inexistente, una cuenta aún no confirmada, o una cuenta sin correo de contacto, **When** se solicita el restablecimiento, **Then** la persona ve el mismo mensaje genérico y no se revela el motivo; no se envía un correo útil a un tercero.
6. **Given** un enlace de restablecimiento inválido, caducado o ya usado, **When** la persona lo abre, **Then** ve un mensaje en español de que el enlace no es válido y la contraseña no cambia.
7. **Given** una persona ya identificada, **When** abre la recuperación por un enlace guardado, **Then** no se le trata como visitante que restablece a ciegas; se le lleva a un destino coherente (por ejemplo Mi perfil).

---



### Edge Cases

- Nombre de usuario ya existente: mensaje en español, sin cuenta nueva ni correo.
- Nombre de usuario con caracteres no permitidos (solo se aceptan letras, números y los signos `@`, `.`, `+`, `-` y `_`): mensaje en español, sin cuenta nueva.
- Nombre de usuario más largo que el máximo permitido por las cuentas del directorio: mensaje en español, sin cuenta nueva.
- Correo de contacto con formato inválido: mensaje en español, sin cuenta nueva ni correo de confirmación.
- El mismo correo de contacto puede usarse en más de una cuenta (el identificador único es el nombre de usuario); no se bloquea el alta solo por correo repetido. Cada cuenta recibe su propio enlace de confirmación o de restablecimiento.
- Contraseña de menos de 8 caracteres, solo numérica, demasiado común o demasiado parecida al nombre de usuario o al correo: rechazo con la razón en español (alta y restablecimiento).
- Confirmación de contraseña distinta: rechazo, sin cuenta nueva ni cambio de contraseña.
- Campos vacíos o solo espacios: rechazo, sin cuenta nueva.
- Tras un error de alta, el nombre de usuario y el correo se conservan en el formulario; la contraseña y su confirmación no se vuelven a mostrar.
- Persona ya identificada que abre el alta, la confirmación ya hecha, o la recuperación por un enlace antiguo: no se le muestra un formulario de visitante; se le trata como autenticada (por ejemplo, se le lleva a Mi perfil o a Inicio).
- El botón “Crear cuenta” y “Olvidé mi contraseña” no sustituyen ni ocultan “Iniciar sesión”; los tres caminos coexisten para el visitante.
- Hasta confirmar el correo, la cuenta nueva no inicia sesión, no ve Mi perfil y no edita templos ni horarios.
- Enlace de confirmación o de restablecimiento caducado, manipulado o reutilizado: mensaje en español, sin activar ni cambiar contraseña.
- Reenvío de confirmación: no revela si el usuario existe; un enlace nuevo sustituye al anterior.
- Restablecimiento: se pide nombre de usuario, no correo, precisamente porque el correo puede repetirse. Mensaje genérico siempre.
- Cuentas creadas en el panel interno o existentes de antemano siguen activas; no se les exige confirmar correo para seguir entrando. Si no tienen correo de contacto, no pueden usar el restablecimiento por correo.
- Una cuenta no confirmada no restablece contraseña; debe confirmar primero (el mensaje al pedir restablecimiento sigue siendo genérico).
- Esta función no permite crear una cuenta para otra persona desde un panel interno; es un alta de uno mismo desde el acceso público.
- No se piden nombre, apellidos ni otros datos de perfil en el alta; esos campos quedan vacíos y Mi perfil ya indica el vacío.
- La cuenta nueva, una vez confirmada, no tiene permisos de administración interna; es una cuenta de colaborador del directorio.
- Los correos (confirmación y restablecimiento) van en español, no incluyen la contraseña en claro y el enlace apunta solo a esta función.
- Textos de botones, formularios, correos y errores no rompen el diseño existente (misma paleta, tipografía y tipo de tarjeta que el acceso).



## Requirements *(mandatory)*



### Functional Requirements

- **FR-001**: En la pantalla de iniciar sesión, el sistema MUST mostrar a los visitantes sin sesión un botón o enlace en español para crear una cuenta y otro para recuperar la contraseña (“Olvidé mi contraseña” o equivalente claro).
- **FR-002**: “Crear cuenta” MUST llevar a una pantalla de alta de cuenta. “Olvidé mi contraseña” MUST llevar a la pantalla de restablecimiento. MUST NOT apuntar a destinos inexistentes o rotos.
- **FR-003**: El formulario de iniciar sesión existente MUST seguir disponible y MUST autenticar cuentas **ya confirmadas** (y las cuentas preexistentes que ya podían entrar). MUST NOT autenticar una cuenta aún no confirmada.
- **FR-004**: La pantalla de alta MUST pedir, como datos obligatorios: nombre de usuario, correo de contacto y contraseña, más la confirmación de esa contraseña.
- **FR-005**: El sistema MUST crear la cuenta solo cuando todos los datos obligatorios son válidos.
- **FR-006**: El nombre de usuario MUST ser único. Si ya existe, el sistema MUST rechazar el alta y MUST mostrar un mensaje en español.
- **FR-007**: El nombre de usuario MUST aceptar solo letras, números y los signos `@`, `.`, `+`, `-` y `_`, y MUST respetar la longitud máxima ya usada por las cuentas del directorio. Valores fuera de esas reglas MUST rechazarse con un mensaje en español.
- **FR-008**: El correo de contacto MUST tener formato de correo electrónico válido. Un valor inválido MUST rechazarse con un mensaje en español.
- **FR-009**: El correo de contacto MUST almacenarse en la cuenta para que sea visible después (por ejemplo en Mi perfil) y para enviar confirmación y restablecimiento. MUST NOT ser el identificador de inicio de sesión.
- **FR-010**: La contraseña (alta y restablecimiento) MUST cumplir las reglas de seguridad ya vigentes en el directorio: longitud mínima de 8 caracteres; no ser demasiado parecida al nombre de usuario ni al correo; no ser una contraseña de uso común; no estar formada solo por números.
- **FR-011**: El sistema MUST exigir que la contraseña y su confirmación coincidan en el alta y en el restablecimiento. Si no coinciden, MUST rechazar con un mensaje en español.
- **FR-012**: Si la contraseña no cumple las reglas, el sistema MUST mostrar en español la razón del rechazo y MUST NOT crear la cuenta ni cambiar la contraseña.
- **FR-013**: Tras un alta válida, el sistema MUST NOT iniciar sesión. MUST enviar un correo de confirmación al correo de contacto y MUST mostrar una pantalla en español indicando que hay que revisar el correo.
- **FR-014**: Un intento de iniciar sesión con una cuenta aún no confirmada MUST fallar y MUST mostrar un mensaje en español de que la cuenta no está confirmada, con una vía para reenviar el correo. MUST NOT revelar la contraseña ni otros datos de la cuenta.
- **FR-015**: El sistema MUST NOT mostrar ni devolver la contraseña en claro después de ningún envío (alta, confirmación, restablecimiento, Mi perfil, redisplay de formularios ni cuerpo de correos).
- **FR-016**: Tras un error de validación en el alta, el formulario MUST conservar el nombre de usuario y el correo ingresados para que la persona no los vuelva a escribir.
- **FR-017**: Visitantes sin sesión MUST poder abrir la pantalla de alta y la de restablecimiento. Personas ya identificadas MUST NOT completar un alta nueva ni un restablecimiento de visitante desde esas pantallas.
- **FR-018**: La pantalla de alta MUST ofrecer una acción en español para volver a iniciar sesión sin crear cuenta. Las pantallas de “revisa tu correo”, confirmación fallida y restablecimiento MUST ofrecer volver al acceso cuando corresponda.
- **FR-019**: Toda la copia nueva (botones, títulos, etiquetas, ayuda de contraseña, mensajes de error y textos de correo) MUST estar en español.
- **FR-020**: Las pantallas nuevas y los botones en el acceso MUST reutilizar el lenguaje visual del directorio: paleta crema/dorado, tipografía de títulos y tarjeta o bloque de contenido como el acceso actual. MUST NOT introducir otro sistema visual.
- **FR-021**: Esta función MUST NOT pedir nombre, apellidos, foto ni otros datos de perfil. MUST NOT incluir alta de cuentas ajenas ni verificación por un canal distinto al correo de contacto.
- **FR-022**: Una cuenta creada por este camino, **una vez confirmada**, MUST poder usarse para las mismas acciones autenticadas que una cuenta existente de colaborador (por ejemplo, editar horarios y ver Mi perfil). MUST NOT nacer con permisos de administración interna. MUST NOT poder mutar datos del directorio ni ver Mi perfil mientras no esté confirmada.
- **FR-023**: El correo de confirmación MUST incluir un enlace de un solo uso, con caducidad (del orden de unos días). Pulsar un enlace vigente MUST confirmar la cuenta e iniciar sesión. Un enlace inválido, caducado o ya usado MUST NOT confirmar y MUST explicar el problema en español.
- **FR-024**: El sistema MUST permitir reenviar el correo de confirmación para una cuenta aún no confirmada. MUST NOT revelar si un nombre de usuario existe o ya está confirmado (mensaje genérico). Un reenvío MUST invalidar el enlace anterior o garantizar que solo un enlace vigente confirma.
- **FR-025**: Cuentas preexistentes o creadas en el panel interno MUST seguir pudiendo iniciar sesión sin pasar por esta confirmación de correo.
- **FR-026**: El restablecimiento de contraseña MUST identificarse por **nombre de usuario**, no por correo. Si la cuenta está confirmada y tiene correo de contacto, MUST enviar un enlace de un solo uso y con caducidad a ese correo. En todos los casos (exista o no la cuenta, esté o no confirmada, tenga o no correo) MUST mostrar el mismo mensaje genérico al visitante.
- **FR-027**: Un enlace de restablecimiento vigente MUST permitir definir una contraseña nueva con las mismas reglas y confirmación. Tras guardarla, la contraseña anterior MUST dejar de funcionar y la persona MUST poder iniciar sesión con la nueva. Un enlace inválido, caducado o ya usado MUST NOT cambiar la contraseña.
- **FR-028**: Una cuenta aún no confirmada MUST NOT restablecer contraseña por este camino (el visitante sigue viendo el mensaje genérico).
- **FR-029**: Los correos de confirmación y de restablecimiento MUST ir en español, MUST identificar el directorio y MUST NOT incluir la contraseña ni un enlace que active otra función.



### Key Entities

- **Cuenta de usuario**: Identidad con la que una persona inicia sesión. En el alta se registran nombre de usuario (identificador único de acceso), correo de contacto y contraseña. Tras el alta queda **pendiente de confirmación**; tras el enlace de correo queda **confirmada** y usable. Nombre y apellidos no se piden aquí y pueden quedar vacíos.
- **Sesión**: Estado de “identificado” o “visitante”. El alta válido no crea sesión. La confirmación vigente sí. El restablecimiento no exige estar identificado para pedir el correo.
- **Pantalla de alta**: Formulario público, en español, para crear la propia cuenta desde el flujo de acceso. No es un panel para dar de alta a terceros.
- **Correo de confirmación**: Mensaje al correo de contacto con un enlace de un solo uso para activar la cuenta.
- **Restablecimiento de contraseña**: Flujo público desde el acceso, claveado por nombre de usuario, que envía un enlace de un solo uso para definir una contraseña nueva.



## Success Criteria *(mandatory)*



### Measurable Outcomes

- **SC-001**: El 100 % de los visitantes sin sesión ven “Crear cuenta” y “Olvidé mi contraseña” en la pantalla de iniciar sesión y pueden llegar al formulario de alta o al de restablecimiento en menos de 15 segundos.
- **SC-002**: Una persona nueva puede completar un alta válida (usuario, correo y contraseña conforme a las reglas) en menos de 2 minutos y entiende, en esa misma visita, que debe revisar su correo.
- **SC-003**: En el 100 % de los intentos con nombre de usuario duplicado, correo inválido, campos vacíos, contraseña que no cumple las reglas o confirmación distinta, no se crea cuenta, no se envía correo de confirmación y la persona ve un mensaje en español que indica el problema.
- **SC-004**: En el 100 % de los altas válidos, la persona **no** queda identificada hasta confirmar; el 100 % de los intentos de iniciar sesión antes de confirmar fallan con un aviso en español.
- **SC-005**: En el 100 % de los casos, la contraseña no se muestra en claro tras el envío, en Mi perfil ni en los correos.
- **SC-006**: Al menos 9 de cada 10 personas reconocen las pantallas de alta, confirmación y restablecimiento como parte del mismo directorio (misma paleta, tipografía y tipo de tarjeta), no como pantallas desconectadas.
- **SC-007**: En el 100 % de la copia nueva (pantallas y correos), el texto está en español (incluido “Crear cuenta” y “Olvidé mi contraseña”, no “Sign up”, “Register” ni “Forgot password”).
- **SC-008**: Tras pulsar un enlace de confirmación vigente, en el 100 % de los casos la cuenta queda usable en esa misma visita (sesión iniciada, Mi perfil y acciones de colaborador) sin que un administrador la active a mano.
- **SC-009**: En el 100 % de los enlaces de confirmación o restablecimiento inválidos, caducados o ya usados, no se activa la cuenta ni se cambia la contraseña, y la persona ve un mensaje en español.
- **SC-010**: Una persona con cuenta confirmada y correo puede completar el restablecimiento (pedir correo, abrir enlace, guardar contraseña válida) en menos de 3 minutos y entrar con la nueva contraseña; la anterior deja de servir.
- **SC-011**: En el 100 % de las solicitudes de restablecimiento o de reenvío, el mensaje al visitante no revela si el nombre de usuario existe, está confirmado o tiene correo.



## Assumptions

- El alta es de auto-registro público desde el acceso: la persona crea su propia cuenta. No es un flujo para que un administrador genere cuentas ajenas.
- Se reutilizan las cuentas y el inicio de sesión ya existentes; no se introduce otro método de identidad (redes sociales, correo como usuario de acceso, etc.).
- Las reglas de contraseña son las ya vigentes en el producto: mínimo 8 caracteres, no demasiado parecida a los datos personales del formulario, no común y no solo numérica. Pedir confirmación de contraseña es parte del alta y del restablecimiento para evitar errores de tipeo.
- El nombre de usuario es el identificador de acceso (el mismo con el que se inicia sesión). El correo es de contacto y el canal para confirmar y restablecer; no sustituye al nombre de usuario.
- El correo de contacto no tiene que ser único entre cuentas (una parroquia podría compartir un correo). La unicidad se exige en el nombre de usuario. Por eso el restablecimiento se pide por nombre de usuario, no por correo.
- Tras un alta válido la cuenta existe pero **no** hay sesión hasta confirmar el correo. Tras un enlace de confirmación vigente, la persona queda identificada (mismo destino coherente que un inicio de sesión exitoso: Mi perfil).
- Los enlaces de confirmación y restablecimiento caducan en unos días y son de un solo uso. Un reenvío deja sin efecto el enlace anterior.
- Cuentas ya existentes o creadas en el panel interno no se bloquean ni se les pide confirmar correo para seguir entrando.
- Nombre y apellidos quedan fuera del formulario de alta; Mi perfil ya muestra un vacío explícito cuando no están cargados.
- La cuenta nueva, una vez confirmada, es de colaborador, no de administración interna.
- Cambio de contraseña estando identificado (desde Mi perfil) y edición de perfil quedan fuera de esta iteración; el recobro cubierto es el de visitante que olvidó la contraseña.
- Los enlaces “Crear cuenta” y “Olvidé mi contraseña” no se añaden a la barra de navegación; viven en la pantalla de iniciar sesión.
- El envío real de correo en el entorno de uso es un prerrequisito operativo; en desarrollo el producto puede mostrar o registrar el correo sin un buzón externo, pero el visitante siempre ve el mismo flujo (“revisa tu correo”).
- La verificación en navegador (escritorio y un ancho de teléfono) es parte del cierre de la función, además de pruebas de alta, correo de confirmación, bloqueo previo, confirmación, reenvío, restablecimiento y acceso con las nuevas credenciales.

