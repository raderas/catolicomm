# Feature Specification: Enlace de Facebook y verificación del templo

**Feature Branch**: `004-templo-facebook-verificado`

**Created**: 2026-09-14

**Status**: **Implemented**

**Input**: User description: "agregar campo a informacion de templos para link a facebook que pueda ser llenado al momento de ingresar un templo o en la edicion. La vista de información del templo debe mostrar el icono de link de facebook y la direccion para que el usuario pueda navegar a la misma. Adicionalmente poner un flag de verificado en la información del templo, todos los templos deben tener el flag sin marcar al crear el templo y por el momento solo un admin de django tendrá el permiso para verificar la información de un templo en la pantalla de información del templo o en la pantalla de edición de servicios (de ser posible utilizar la plantilla reutilizable que ya muestra la información del templo en esas dos pantallas)"

## Clarifications



### Session 2026-09-14

- Q: ¿Qué ocurre con Verificado si alguien edita los datos del templo o sus servicios? → A: La marca vuelve a no verificado para que un administrador la revise y la vuelva a marcar cuando corresponda.
- Q: ¿Cómo se presenta un templo cuya información aún no está verificada? → A: Un asterisco pequeño después del nombre y, al pie de la sección de información, una nota en español de que esos datos aún están sujetos a validación.
- Q: ¿Debe la misma sección advertir sobre cambios en fechas especiales? → A: Sí. Mostrar siempre la nota: «La información y horarios pueden estar sujetos a modificaciones o excepciones en fechas especiales/festividades.»



## User Scenarios & Testing *(mandatory)*



### User Story 1 - Registrar o corregir el enlace de Facebook del templo (Priority: P1)

Un editor autenticado, al dar de alta un templo o al editar uno existente, puede indicar (o dejar vacío) el enlace a la página de Facebook de esa parroquia. El dato se guarda junto con el resto de la ficha; nombre, dirección, alias y foto siguen funcionando igual.

**Why this priority**: Sin un lugar para capturar el enlace en alta y edición, la comunidad no puede descubrir la presencia de la parroquia en Facebook.

**Independent Test**: Un usuario autenticado crea un templo con un enlace de Facebook válido y luego ve ese mismo enlace en la ficha. En un templo existente, cambia o vacía el enlace y confirma el resultado sin alterar el resto de datos de ficha (salvo la verificación, que se revoca si el templo estaba verificado).

**Acceptance Scenarios**:

1. **Given** un editor autenticado en la pantalla de alta, **When** completa los datos obligatorios, indica un enlace de Facebook válido y guarda, **Then** el templo se crea con ese enlace y aparece en la ficha de información.
2. **Given** un editor autenticado en la pantalla de alta, **When** completa los datos obligatorios y guarda **sin** enlace de Facebook, **Then** el templo se crea y la ficha no muestra un enlace de Facebook vacío ni un icono sin destino.
3. **Given** un templo existente no verificado y un editor autenticado en su pantalla de edición, **When** indica o corrige el enlace de Facebook y guarda, **Then** la ficha muestra el valor nuevo; nombre, dirección, alias y foto no cambian.
4. **Given** un templo con enlace de Facebook y un editor autenticado en su pantalla de edición, **When** deja el campo de Facebook vacío y guarda, **Then** el enlace deja de mostrarse en la ficha y el resto de datos de ficha permanece (salvo la verificación, si estaba marcada).
5. **Given** un editor autenticado en alta o edición, **When** intenta guardar un enlace de Facebook que no es una dirección web usable, **Then** ve un mensaje de error en español y el templo no se crea ni se actualiza con ese valor.

---



### User Story 2 - Abrir el Facebook del templo desde su información (Priority: P1)

Un visitante (con o sin sesión) abre la ficha de información de un templo que tiene Facebook. Ve el icono de Facebook junto a la dirección del enlace y puede usarlo para ir a esa página. El mismo bloque de información del templo aparece también en la pantalla de edición de servicios, con el mismo enlace visible.

**Why this priority**: Capturar el enlace no sirve si la comunidad no lo ve ni puede seguirlo. Mostrarlo en el bloque compartido de la ficha evita que el dato quede escondido en el formulario de edición.

**Independent Test**: Con un templo que tiene Facebook, un visitante abre la ficha, reconoce icono y dirección, y al usar el enlace llega a esa página. En un templo sin Facebook, no aparece el enlace.

**Acceptance Scenarios**:

1. **Given** un templo con enlace de Facebook, **When** un visitante abre la ficha de información, **Then** ve el icono de Facebook y la dirección del enlace, y puede navegar a esa página.
2. **Given** un templo con enlace de Facebook, **When** un editor autenticado abre la pantalla de edición de servicios de ese templo, **Then** el mismo bloque de información muestra el icono y la dirección del enlace, igual que en la ficha.
3. **Given** un templo **sin** enlace de Facebook, **When** un visitante abre la ficha (o un editor abre la edición de servicios), **Then** no se muestra icono ni dirección de Facebook.
4. **Given** un visitante en la ficha, **When** usa el enlace de Facebook, **Then** llega a la página indicada sin perder de forma permanente el contexto del directorio (p. ej. la página se abre de modo que puede volver al templo).

---



### User Story 3 - El administrador marca un templo como verificado (Priority: P1)

Un administrador del sitio abre la ficha de información de un templo o la pantalla de edición de servicios y, en el bloque de información del templo, marca (o quita) la verificación. El templo queda verificado de forma visible para la comunidad. Un templo recién creado nunca nace verificado.

**Why this priority**: El directorio es de contribución comunitaria; la marca de verificado es la señal de confianza. Debe poder aplicarse donde ya se consulta la ficha, no en un flujo aparte, y no debe quedar al alcance de cualquier editor.

**Independent Test**: Un administrador marca un templo como verificado desde la ficha y confirma que la marca se ve en la ficha y en la edición de servicios. Quita la marca y confirma que desaparece. Un templo nuevo permanece sin verificar.

**Acceptance Scenarios**:

1. **Given** un templo no verificado y un administrador del sitio en la ficha de información, **When** marca el templo como verificado, **Then** la ficha y la pantalla de edición de servicios muestran de inmediato que está verificado (sin asterisco de pendiente de validación).
2. **Given** un templo no verificado y un administrador del sitio en la pantalla de edición de servicios, **When** marca el templo como verificado, **Then** el resultado es el mismo que si lo hubiera hecho desde la ficha.
3. **Given** un templo verificado y un administrador del sitio en la ficha o en la edición de servicios, **When** quita la verificación, **Then** la marca deja de mostrarse a la comunidad en ambos lugares y reaparece el asterisco con la nota de pendiente de validación.
4. **Given** un editor autenticado que no es administrador, **When** crea un templo, **Then** el templo queda sin verificar aunque el editor intente o desee marcarlo; no hay control de verificación en el alta ni en la edición de datos del templo.
5. **Given** templos ya existentes antes de esta función, **When** un visitante consulta su ficha, **Then** aparecen sin verificar hasta que un administrador los marque.

---



### User Story 4 - Solo el administrador puede verificar; la comunidad sí ve la marca (Priority: P1)

Un editor autenticado que no es administrador, y un visitante sin sesión, ven si el templo está verificado cuando lo está, pero no pueden cambiar ese estado. Si intentan la acción de verificar, no se aplica.

**Why this priority**: Si cualquier editor pudiera auto-verificar, la marca perdería sentido. La consulta pública de la marca sí es parte del valor para la comunidad.

**Independent Test**: Con un templo no verificado, un editor no administrador y un visitante no ven control de verificación (o no pueden usarlo) y el estado no cambia. Con un templo verificado, ambos ven la marca.

**Acceptance Scenarios**:

1. **Given** un editor autenticado que no es administrador, en la ficha o en la edición de servicios, **When** consulta el bloque de información del templo, **Then** no dispone de una acción que marque o quite la verificación.
2. **Given** un visitante sin sesión en la ficha, **When** consulta un templo verificado, **Then** ve la marca de verificado y no puede cambiarla.
3. **Given** un visitante sin sesión en la ficha, **When** consulta un templo no verificado, **Then** no ve una marca de verificado (no se presenta como confirmado).
4. **Given** un editor no administrador que intenta enviar o forzar un cambio de verificación, **When** lo hace, **Then** el estado del templo no cambia.

---



### User Story 5 - Editar ficha o servicios revoca la verificación (Priority: P1)

Cuando un editor (o un administrador) guarda cambios en los datos del templo o en sus servicios, un templo que estaba verificado pasa a no verificado. Un administrador debe volver a marcar la verificación cuando haya revisado la información nueva.

**Why this priority**: Si la ficha o los horarios cambian y la marca permanece, la comunidad creería validada información que ya no coincide con lo revisado.

**Independent Test**: Con un templo verificado, guardar un cambio de ficha (p. ej. Facebook o dirección) o un cambio de servicios deja el templo no verificado en ficha y en edición de servicios, con asterisco y nota de pendiente de validación.

**Acceptance Scenarios**:

1. **Given** un templo verificado, **When** un editor autenticado guarda un cambio en los datos del templo (nombre, dirección, alias, foto o Facebook), **Then** el templo queda no verificado y un administrador puede volver a marcarlo.
2. **Given** un templo verificado, **When** un editor autenticado crea, modifica o elimina un servicio de ese templo, **Then** el templo queda no verificado de la misma forma.
3. **Given** un templo verificado, **When** un administrador del sitio guarda un cambio de ficha o de servicios, **Then** la verificación también se revoca; el administrador MUST volver a marcarla después, no se conserva por el hecho de que quien editó sea administrador.
4. **Given** un templo no verificado, **When** se guarda un cambio de ficha o de servicios, **Then** sigue no verificado.
5. **Given** un intento de guardar ficha o servicios que falla (datos inválidos o sesión caducada), **When** no se aplica el cambio, **Then** el estado de verificación no se altera.

---



### User Story 6 - Avisos de validación pendiente y de fechas especiales (Priority: P1)

En el bloque de información del templo, un templo no verificado muestra un asterisco pequeño después del nombre y, al pie de esa sección, una nota en español de que la información aún está sujeta a validación. En todos los templos, verificados o no, esa misma sección incluye además la nota de excepciones en fechas especiales.

**Why this priority**: La ausencia de la marca “Verificado” no basta: la comunidad necesita un aviso explícito de que esos datos aún se están validando, y una advertencia permanente de que horarios e información pueden variar en festividades.

**Independent Test**: Un visitante abre la ficha de un templo no verificado y ve el asterisco, la nota de validación y la nota de festividades. En un templo verificado ve la marca de verificado y la nota de festividades, sin asterisco ni nota de validación pendiente. Lo mismo en la edición de servicios.

**Acceptance Scenarios**:

1. **Given** un templo no verificado, **When** un visitante abre la ficha (o un editor abre la edición de servicios), **Then** el nombre del templo en el bloque de información lleva un asterisco pequeño y, al pie de esa sección, aparece la nota: «La información de este templo aún está sujeta a validación.»
2. **Given** un templo verificado, **When** un visitante abre la ficha (o un editor abre la edición de servicios), **Then** no hay asterisco después del nombre ni nota de validación pendiente; sí se ve la marca de verificado.
3. **Given** cualquier templo (verificado o no), **When** se muestra el bloque de información, **Then** al pie de la sección aparece también: «La información y horarios pueden estar sujetos a modificaciones o excepciones en fechas especiales/festividades.»
4. **Given** un templo que acaba de pasar de verificado a no verificado por una edición, **When** se vuelve a ver el bloque de información, **Then** el asterisco y la nota de validación pendiente están visibles de inmediato.

---



### Edge Cases

- Enlace de Facebook vacío: está permitido en alta y en edición; no se muestra icono ni dirección.
- Enlace con espacios al inicio o al final: se trata como el mismo enlace sin esos espacios; no se rechaza por espacios incidentales.
- Enlace que no es una dirección web usable (texto libre, esquema inválido): se rechaza con mensaje en español; no se guarda.
- Templo inexistente: quien intente editar datos o verificar no llega a una pantalla vacía o rota; ve que el templo no existe.
- Sesión caducada al guardar el enlace, un servicio o al verificar: se pide iniciar sesión de nuevo y no se aplica el cambio ni se altera la verificación.
- Un editor o un administrador guarda un cambio válido de ficha (incluido Facebook) o de servicios en un templo verificado: la verificación se revoca; solo un administrador puede volver a marcarla.
- Un guardado inválido o cancelado no revoca la verificación.
- Solo marcar o quitar verificación (sin editar ficha ni servicios) no crea, modifica ni borra horarios, ni cambia nombre, dirección, alias, foto o Facebook.
- Templos creados antes de esta función: sin enlace de Facebook y sin verificar (asterisco y nota de validación pendiente visibles).
- El listado de parroquias no está obligado a mostrar Facebook, asterisco, notas ni la marca de verificado en esta iteración; el alcance de visualización es el bloque de información del templo (ficha y edición de servicios).
- Mensajes de éxito o error de verificación y de Facebook no rompen el diseño del bloque de información ni del formulario de alta/edición.



## Requirements *(mandatory)*



### Functional Requirements

- **FR-001**: El sistema MUST permitir a un editor autenticado indicar un enlace de Facebook opcional al crear un templo, en la pantalla de alta ya existente.
- **FR-002**: El sistema MUST permitir a un editor autenticado indicar, corregir o vaciar el enlace de Facebook de un templo existente, en la pantalla de edición de datos del templo ya existente.
- **FR-003**: El enlace de Facebook MUST ser opcional. Guardar sin él MUST crear o actualizar el templo sin exigir ese dato.
- **FR-004**: Si el editor indica un valor, el sistema MUST aceptarlo solo cuando sea una dirección web usable. MUST rechazar valores inválidos con un mensaje en español y MUST NOT persistirlos.
- **FR-005**: Un campo no modificado en edición (incluido Facebook) MUST conservar su valor anterior, salvo el estado de verificación cuando aplique FR-018.
- **FR-006**: El bloque de información del templo que ya se muestra en la ficha pública y en la pantalla de edición de servicios MUST mostrar, cuando exista enlace de Facebook, un icono reconocible de Facebook junto a la dirección del enlace.
- **FR-007**: Ese enlace MUST ser accionable: el usuario MUST poder navegar a la página de Facebook indicada.
- **FR-008**: Si el templo no tiene enlace de Facebook, ese bloque MUST NOT mostrar icono ni dirección de Facebook.
- **FR-009**: Cada templo MUST tener un estado de verificación (verificado o no verificado). Al crear un templo, el estado MUST quedar no verificado. Los templos ya existentes MUST quedar no verificados hasta que un administrador los marque.
- **FR-010**: El mismo bloque de información del templo (ficha pública y edición de servicios) MUST mostrar una marca clara de “Verificado” cuando el templo esté verificado, y MUST NOT mostrar esa marca cuando no lo esté.
- **FR-011**: Un administrador del sitio MUST poder marcar o quitar la verificación desde la ficha de información del templo y desde la pantalla de edición de servicios, usando ese mismo bloque de información (no un flujo distinto por pantalla).
- **FR-012**: Editores autenticados que no son administradores del sitio, y visitantes sin sesión, MUST NOT poder marcar ni quitar la verificación. El alta y la edición de datos del templo MUST NOT ofrecer un control para cambiar ese estado.
- **FR-013**: Tras un cambio válido de Facebook, de verificación, o de revocación automática, la ficha y la edición de servicios MUST mostrar de inmediato el valor real (enlace o ausencia; verificado o no; avisos de validación pendientes o no).
- **FR-014**: Visitantes no autenticados MUST poder ver el enlace de Facebook (si existe), la marca de verificado (si aplica) y los avisos de esta función en la ficha, sin iniciar sesión.
- **FR-015**: Toda la copia de esta función MUST estar en español, incluyendo etiquetas, marca de verificado, notas al pie, vacíos, éxitos y errores.
- **FR-016**: El bloque de información y los formularios de alta/edición MUST reutilizar el lenguaje visual del directorio (tarjetas, paleta crema/dorado, tipografía de títulos). MUST NOT introducir otro sistema visual.
- **FR-017**: Esta función MUST NOT eliminar templos. MUST NOT exigir cambios en nombre, dirección, alias o foto para guardar Facebook o la verificación. Marcar o quitar verificación MUST NOT crear, modificar ni borrar horarios de servicio.
- **FR-018**: Tras un guardado válido de datos del templo (nombre, dirección, alias, foto o Facebook) o de un alta, modificación o baja de servicio, si el templo estaba verificado el sistema MUST dejarlo no verificado. Un administrador MUST poder volver a marcarlo después de revisar.
- **FR-019**: Un guardado inválido o no aplicado MUST NOT cambiar el estado de verificación.
- **FR-020**: Si el templo no está verificado, el bloque de información MUST mostrar un asterisco pequeño inmediatamente después del nombre y, al pie de esa sección, la nota: «La información de este templo aún está sujeta a validación.» Si está verificado, MUST NOT mostrar ese asterisco ni esa nota.
- **FR-021**: El bloque de información MUST mostrar siempre, al pie de la sección, la nota: «La información y horarios pueden estar sujetos a modificaciones o excepciones en fechas especiales/festividades.» (tanto en templos verificados como no verificados).



### Key Entities

- **Templo**: Parroquia o iglesia del directorio. Además de nombre, dirección, alias y fotografía, ahora puede tener un enlace opcional a Facebook y un estado de verificación.
- **Enlace de Facebook**: Dirección web opcional de la página o perfil de Facebook de ese templo. Si existe, se muestra con icono y texto en el bloque de información y se puede seguir. Si falta, no se muestra nada.
- **Estado de verificación**: Indicador de si un administrador del sitio ha confirmado la información vigente del templo. Empieza siempre en no verificado. Solo un administrador puede marcarlo. Un cambio válido de ficha o de servicios lo revoca.
- **Editor autenticado**: Persona que ha iniciado sesión y puede crear o editar datos del templo (incluido Facebook) y servicios. No puede verificar. Sus ediciones revocan una verificación existente.
- **Administrador del sitio**: Persona con permiso administrativo ya existente. Puede marcar o quitar la verificación desde la ficha o la edición de servicios. Si edita ficha o servicios, también revoca la verificación y debe volver a marcarla.



## Success Criteria *(mandatory)*



### Measurable Outcomes

- **SC-001**: Un editor autenticado puede dar de alta un templo con enlace de Facebook válido y ver icono más dirección en la ficha en menos de dos minutos.
- **SC-002**: Un editor autenticado puede añadir, corregir o quitar el Facebook de un templo existente en menos de un minuto, sin rehacer nombre, dirección ni foto.
- **SC-003**: En el 100 % de las fichas (y de las pantallas de edición de servicios) de templos con Facebook, se ve el icono y la dirección, y el enlace lleva a esa página; en el 100 % de los que no tienen Facebook, no aparece el enlace.
- **SC-004**: Un administrador del sitio puede marcar un templo como verificado desde la ficha o desde la edición de servicios en menos de 30 segundos, y la marca se ve en ambos lugares.
- **SC-005**: En el 100 % de los templos recién creados (y de los ya existentes al activar la función), el estado inicial es no verificado.
- **SC-006**: En el 100 % de los intentos, un editor que no es administrador y un visitante sin sesión no consiguen cambiar la verificación por la acción de marcar o quitar.
- **SC-007**: Al menos 9 de cada 10 visitantes reconocen el icono de Facebook, la marca de verificado (o el asterisco de pendiente) y las notas al pie como parte de la misma ficha del directorio (mismo bloque de información, misma paleta), no como elementos ajenos.
- **SC-008**: En el 100 % de los guardados válidos de ficha o de servicios sobre un templo verificado, el estado pasa a no verificado y el asterisco más la nota de validación pendiente son visibles en ficha y edición de servicios.
- **SC-009**: En el 100 % de las fichas y ediciones de servicios de templos no verificados se ve el asterisco después del nombre y la nota de validación pendiente; en el 100 % de los verificados no se ven. En el 100 % de ambos casos se ve la nota de fechas especiales/festividades.



## Assumptions

- El enlace de Facebook es un campo más de la ficha, opcional, al mismo nivel de captura que el alias: se llena en alta y en edición de datos del templo, no en la pantalla de horarios.
- Una sola dirección de Facebook por templo es suficiente; no hay otras redes sociales en esta iteración.
- Una dirección web usable significa un enlace que un visitante puede abrir en el navegador (página o perfil de Facebook). No se exige validar que la página exista en Facebook ni que pertenezca a esa parroquia.
- Al seguir el enlace, la página de Facebook se abre de modo que el visitante puede volver al directorio (p. ej. en otra pestaña).
- La visualización de Facebook, de la marca de verificado, del asterisco y de las notas al pie se concentra en el bloque de información del templo que ya se reutiliza en la ficha pública y en la edición de servicios. El listado de parroquias queda fuera de esta iteración.
- “Administrador del sitio” es quien ya tiene acceso administrativo al producto (personal de administración), no un rol nuevo de parroquia. En esta iteración no se modela un permiso de verificación para editores de parroquia.
- El administrador verifica o desverifica en las pantallas de la aplicación que ya muestran ese bloque (ficha y edición de servicios), no en un formulario de alta/edición de datos del templo.
- Cualquier guardado válido de ficha o de servicios (alta, cambio o baja de un horario) revoca la verificación, aunque quien guarde sea administrador. No hay excepción por “el mismo administrador acaba de editar”.
- La nota de fechas especiales se muestra siempre; no depende del estado de verificación. La nota de validación pendiente y el asterisco solo aparecen si el templo no está verificado.
- El texto de validación pendiente queda fijado como «La información de este templo aún está sujeta a validación.» El asterisco después del nombre es el mismo signo que introduce esa nota.
- Cualquier usuario autenticado sigue pudiendo editar el Facebook de cualquier templo, igual que hoy edita nombre y dirección. La restricción por parroquia asignada sigue fuera de esta iteración.
- Se reutiliza el sistema de cuentas y de alta/edición de templo y de servicios ya disponible.
- La verificación en navegador (o el sustituto más cercano) es parte del cierre de la función, además de pruebas del camino crítico de ficha, alta/edición, servicios y cambio de verificación.

