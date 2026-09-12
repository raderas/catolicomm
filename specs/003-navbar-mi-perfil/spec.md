# Feature Specification: Navegación de sesión y página Mi perfil

**Feature Branch**: `003-navbar-mi-perfil`

**Created**: 2026-09-11

**Status**: Draft

**Input**: User description: "actualizar navbar de misas/templates/base.html para que muestre link de login si el usuario no ha iniciado sesión, si ya inició sesión mostrar un link de "Mi perfil" con un ícono y agregar la página de mi perfil donde el usuario puede ver su información registrada en el sistema."

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Entrar a iniciar sesión desde la barra de navegación (Priority: P1)

Un visitante que aún no ha iniciado sesión ve, en la barra de navegación de cualquier pantalla del directorio, un enlace para iniciar sesión. Al usarlo, llega a la pantalla de inicio de sesión ya existente. Quien ya tiene sesión no ve ese enlace.

**Why this priority**: Hoy el enlace de acceso está siempre visible y no distingue si hay sesión. Sin un acceso claro y correcto, un visitante no puede identificarse para contribuir al directorio.

**Independent Test**: Un visitante sin sesión abre cualquier pantalla que use la barra común, pulsa el enlace de iniciar sesión y llega a la pantalla de acceso. Tras iniciar sesión, ese enlace ya no aparece.

**Acceptance Scenarios**:

1. **Given** un visitante sin sesión en Inicio, en una ficha de templo o en otra pantalla con la barra común, **When** mira la barra de navegación, **Then** ve un enlace en español para iniciar sesión y no ve el enlace “Mi perfil”.
2. **Given** un visitante sin sesión, **When** pulsa el enlace de iniciar sesión, **Then** llega a la pantalla de acceso existente (usuario y contraseña) y puede identificarse.
3. **Given** un usuario que acaba de iniciar sesión, **When** mira la barra en cualquier pantalla, **Then** el enlace de iniciar sesión ya no está visible.
4. **Given** un visitante sin sesión, **When** usa la barra en un teléfono (menú plegado), **Then** el enlace de iniciar sesión sigue disponible al expandir el menú.

---

### User Story 2 - Abrir Mi perfil desde la barra cuando hay sesión (Priority: P1)

Un usuario que ya inició sesión ve en la barra, en lugar del enlace de acceso, un enlace “Mi perfil” acompañado de un ícono reconocible de persona o cuenta. Al pulsarlo, llega a su página de perfil.

**Why this priority**: Es el camino principal para que una persona identificada confirme quién es en el sistema y llegue a sus datos. Sin este enlace, la página de perfil queda oculta.

**Independent Test**: Un usuario autenticado ve “Mi perfil” con ícono en la barra, pulsa el enlace y llega a su perfil; un visitante sin sesión no ve ese enlace.

**Acceptance Scenarios**:

1. **Given** un usuario autenticado en cualquier pantalla con la barra común, **When** mira la barra, **Then** ve el enlace “Mi perfil” con un ícono y no ve el enlace de iniciar sesión.
2. **Given** un usuario autenticado, **When** pulsa “Mi perfil”, **Then** llega a la página de su perfil.
3. **Given** un visitante sin sesión, **When** mira la barra, **Then** no ve “Mi perfil”.
4. **Given** un usuario autenticado en un teléfono (menú plegado), **When** expande el menú, **Then** “Mi perfil” con su ícono está disponible.

---

### User Story 3 - Consultar la información de la cuenta (Priority: P1)

El usuario autenticado abre Mi perfil y ve, en español y con el mismo aspecto del directorio, los datos de su cuenta registrados en el sistema: identificador de usuario, nombre, apellidos, correo y fecha de alta. No puede ver el perfil de otra persona. Los campos vacíos se indican con claridad; no se muestra la contraseña.

**Why this priority**: Ver los datos registrados es el propósito de la página. Sin esta consulta, el enlace de la barra no entrega valor.

**Independent Test**: Un usuario autenticado abre Mi perfil y reconoce sus propios datos (y el vacío cuando un dato no está cargado); no ve contraseña ni datos de otra cuenta.

**Acceptance Scenarios**:

1. **Given** un usuario autenticado con nombre, apellidos y correo registrados, **When** abre Mi perfil, **Then** ve su identificador de usuario, nombre, apellidos, correo y fecha de alta, todos correspondientes a su cuenta.
2. **Given** un usuario autenticado cuyo nombre, apellidos o correo no están cargados, **When** abre Mi perfil, **Then** esos campos muestran una indicación en español de que no hay dato (no un espacio en blanco confuso).
3. **Given** un usuario autenticado en Mi perfil, **When** consulta la página, **Then** no ve su contraseña ni un secreto equivalente.
4. **Given** un usuario autenticado, **When** está en Mi perfil, **Then** la pantalla está en español, usa el mismo lenguaje visual del directorio (barra, paleta crema/dorado, tipografía de títulos, tarjeta o bloque de contenido) y el enlace “Mi perfil” de la barra se percibe como la sección activa.

---

### User Story 4 - Proteger Mi perfil y permitir cerrar sesión (Priority: P1)

Quien no ha iniciado sesión no puede ver Mi perfil. Si intenta abrirla, se le pide iniciar sesión y, tras identificarse, llega a su perfil. Desde Mi perfil, el usuario puede cerrar sesión y vuelve a navegar como visitante (enlace de iniciar sesión otra vez en la barra).

**Why this priority**: Los datos de cuenta no deben ser públicos. Cerrar sesión es el complemento natural de un estado autenticado en la barra; sin él, la persona no puede dejar de estar identificada desde el directorio.

**Independent Test**: Un visitante sin sesión no ve el perfil y es enviado a iniciar sesión; tras entrar, ve su perfil. Un usuario autenticado cierra sesión desde Mi perfil y deja de ver “Mi perfil” en la barra.

**Acceptance Scenarios**:

1. **Given** un visitante sin sesión, **When** intenta abrir Mi perfil (por enlace directo u otro medio), **Then** no ve los datos de ninguna cuenta y se le pide iniciar sesión.
2. **Given** un visitante sin sesión enviado a iniciar sesión desde Mi perfil, **When** inicia sesión correctamente, **Then** llega a su página de perfil.
3. **Given** un usuario autenticado en Mi perfil, **When** cierra sesión, **Then** deja de estar identificado, no permanece en Mi perfil y la barra vuelve a mostrar el enlace de iniciar sesión (no “Mi perfil”).
4. **Given** dos cuentas distintas, **When** cada una abre Mi perfil, **Then** cada una ve solo sus propios datos.

---

### Edge Cases

- Sesión caducada: si el usuario tenía sesión y esta expira, la barra vuelve a mostrar iniciar sesión; un intento de abrir Mi perfil pide identificarse de nuevo.
- Usuario autenticado que pulsa de nuevo iniciar sesión por un enlace antiguo o guardado: no se le muestra un formulario innecesario como si fuera visitante; se le trata como persona ya identificada (por ejemplo, se le lleva a Mi perfil o a Inicio).
- Campos de nombre, apellidos o correo vacíos: se muestra un vacío explícito en español; no se inventan datos.
- Identificador de usuario y fecha de alta siempre están presentes para una cuenta válida.
- La barra no muestra a la vez “iniciar sesión” y “Mi perfil”.
- Inicio y el resto de enlaces públicos de la barra no cambian de propósito; esta función solo añade el estado de sesión.
- Mi perfil no permite editar datos ni cambiar contraseña en esta iteración.
- Mi perfil no lista templos, horarios ni permisos de administración.
- Tras cerrar sesión, un intento de volver atrás no debe volver a mostrar los datos de la cuenta sin identificarse otra vez.
- En el menú plegado de pantallas pequeñas, los enlaces de sesión se comportan igual que en escritorio.
- Textos de la barra y de Mi perfil no rompen el diseño existente (misma barra, mismos colores y tipografías).

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: En todas las pantallas que usan la barra de navegación común, el sistema MUST mostrar un enlace en español para iniciar sesión si la persona no tiene sesión activa.
- **FR-002**: Ese enlace MUST llevar a la pantalla de inicio de sesión ya existente. MUST NOT apuntar a un destino inexistente o roto.
- **FR-003**: Si la persona tiene sesión activa, el sistema MUST NOT mostrar el enlace de iniciar sesión en la barra.
- **FR-004**: Si la persona tiene sesión activa, la barra MUST mostrar un enlace con el texto “Mi perfil” acompañado de un ícono reconocible de persona o cuenta.
- **FR-005**: Si la persona no tiene sesión activa, la barra MUST NOT mostrar “Mi perfil”.
- **FR-006**: El enlace “Mi perfil” MUST llevar a la página de perfil de la persona autenticada.
- **FR-007**: El sistema MUST ofrecer una página “Mi perfil” donde la persona autenticada vea los datos de su propia cuenta: identificador de usuario, nombre, apellidos, correo electrónico y fecha de alta en el sistema.
- **FR-008**: Si nombre, apellidos o correo no están registrados, la página MUST mostrar una indicación en español de que ese dato no está disponible. MUST NOT dejar el campo en blanco sin explicación ni inventar un valor.
- **FR-009**: La página Mi perfil MUST NOT mostrar la contraseña ni ningún secreto de acceso.
- **FR-010**: La página Mi perfil MUST mostrar únicamente los datos de la cuenta de la persona autenticada. MUST NOT permitir consultar el perfil de otra cuenta.
- **FR-011**: Visitantes sin sesión MUST NOT ver Mi perfil. MUST ser redirigidos a iniciar sesión y, tras autenticarse, MUST volver a Mi perfil.
- **FR-012**: Desde Mi perfil, la persona autenticada MUST poder cerrar sesión. Tras cerrar sesión, MUST dejar de ver datos de cuenta y la barra MUST volver al estado de visitante (enlace de iniciar sesión).
- **FR-013**: El enlace de Inicio y el resto de la navegación pública MUST permanecer. Esta función MUST NOT quitar ni reemplazar Inicio.
- **FR-014**: Toda la copia nueva (barra, título de página, etiquetas de campos, vacíos, acciones de cerrar sesión) MUST estar en español. El enlace de acceso MUST decir “Iniciar sesión”, no “Login”.
- **FR-015**: La página Mi perfil y los cambios de la barra MUST reutilizar el lenguaje visual del directorio: paleta crema/dorado, tipografía de títulos, barra existente e íconos del mismo juego visual. MUST NOT introducir otro sistema visual.
- **FR-016**: En pantallas pequeñas, los enlaces de sesión MUST seguir disponibles dentro del menú desplegable de la barra, con el mismo criterio de visitante frente a persona autenticada.
- **FR-017**: Esta función MUST NOT permitir editar el perfil, cambiar la contraseña, crear cuentas ni alterar templos u horarios.

### Key Entities

- **Cuenta de usuario**: Identidad con la que una persona inicia sesión en el directorio. Datos visibles en esta iteración: identificador de usuario, nombre, apellidos, correo electrónico y fecha de alta. La contraseña existe para autenticar pero no se muestra.
- **Sesión**: Estado de “identificado” o “visitante” que determina qué muestra la barra y si Mi perfil es accesible.
- **Página Mi perfil**: Pantalla de solo consulta de los datos de la cuenta de la persona autenticada, con acción para cerrar sesión.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: En el 100 % de las pantallas con la barra común, un visitante sin sesión ve “Iniciar sesión” y no ve “Mi perfil”; una persona autenticada ve “Mi perfil” con ícono y no ve “Iniciar sesión”.
- **SC-002**: Un visitante sin sesión llega desde la barra a la pantalla de acceso y puede identificarse en menos de un minuto.
- **SC-003**: Una persona autenticada llega desde “Mi perfil” en la barra a sus datos de cuenta en menos de 10 segundos.
- **SC-004**: En el 100 % de las consultas a Mi perfil, la persona ve solo sus propios datos (identificador, nombre, apellidos, correo o vacío explícito, y fecha de alta) y nunca la contraseña.
- **SC-005**: En el 100 % de los intentos, un visitante sin sesión no ve Mi perfil y es invitado a iniciar sesión; tras identificarse, llega a su perfil.
- **SC-006**: Una persona autenticada puede cerrar sesión desde Mi perfil en menos de 15 segundos y, al hacerlo, la barra vuelve a mostrar “Iniciar sesión”.
- **SC-007**: Al menos 9 de cada 10 personas reconocen Mi perfil y la barra actualizada como parte del mismo directorio (misma paleta, barra y tipografía), no como una pantalla desconectada.
- **SC-008**: En el 100 % de los casos, el texto de acceso en la barra está en español (“Iniciar sesión”).

## Assumptions

- Se reutiliza el sistema de cuentas e inicio de sesión ya disponible; esta función no crea un método nuevo de identidad ni un registro público de cuentas.
- La página es de solo lectura: ver datos, no editarlos ni cambiar contraseña. Edición de perfil queda fuera de esta iteración.
- Los datos mostrados son los de la cuenta estándar ya usada para entrar: identificador (el mismo con el que se inicia sesión), nombre, apellidos, correo y fecha de alta. No se añaden campos nuevos (foto de perfil, parroquia asignada, teléfono, etc.).
- Cerrar sesión se ofrece en Mi perfil, no como un segundo enlace permanente en la barra, para no recargar la navegación.
- No se muestran indicadores de administración (si la cuenta puede entrar al panel interno) ni el listado de templos que la persona ha editado.
- El enlace de Inicio se mantiene; el enlace comentado de mapa no se activa.
- “Login” en inglés se reemplaza por “Iniciar sesión” para cumplir la copia en español del producto.
- Cualquier cuenta autenticada (colaboradora o con permisos internos) ve la misma página Mi perfil de consulta.
- La verificación en navegador (escritorio y un ancho de teléfono) es parte del cierre de la función, además de pruebas del camino de barra, perfil protegido y cierre de sesión.
