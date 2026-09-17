# Agendame - Appointment Booking

Agendame es un addon de Odoo para gestionar reservas públicas de citas desde el sitio web, usando el calendario interno de Odoo como fuente de verdad. El módulo permite crear tipos de cita, definir horarios de disponibilidad por día y usuario, y reservar agendamientos desde una página pública sin depender del módulo enterprise de appointments.

## Objetivo del módulo

El flujo principal es:

1. Un visitante entra a la página pública `/agendame`.
2. Elige un tipo de cita activo.
3. Selecciona el profesional asignado.
4. El sistema calcula los horarios disponibles.
5. Completa sus datos personales.
6. Odoo valida la disponibilidad final.
7. Se crea o reutiliza un contacto y se genera el evento de calendario.

El módulo está pensado para trabajo con atención presencial, consultoría, reuniones de ventas, soporte, calls o cualquier flujo de agenda que necesite reservas públicas y calendarización interna.

---

## Funcionalidades principales

- Página pública de reservas accesible desde el website.
- Múltiples tipos de cita con duración, zona horaria, imagen, colores y días visibles.
- Definición de horarios por día de la semana por tipo de agenda.
- Soporte para varios usuarios internos asignados al mismo tipo de cita.
- Cálculo de disponibilidad por profesional.
- Validación de conflictos contra eventos reales de calendario.
- Creación automática de contacto y registro de país y teléfono.
- Generación de evento de calendario con el cliente y el profesional involucrado.
- Integración con CRM para enlazar una oportunidad con un tipo de cita y URL de reserva.
- Agenda por defecto para cada usuario interno nuevo.
- Reglas de seguridad para que cada usuario solo pueda gestionar su propia agenda.
- Soporte para videollamadas con Discuss, Google Meet o Zoom.

---

## Dependencias y justificación

El módulo requiere los siguientes addons oficiales de Odoo para su funcionamiento. A continuación se detalla la razón y el propósito de cada dependencia:

### 1. `base`
- **Usuarios y personal:** Gestiona el modelo `res.users` para asignar profesionales a cada tipo de cita (`staff_user_ids`) y autoprovisionar agendas por defecto a nuevos usuarios internos.
- **Clientes y contactos:** Utiliza `res.partner` y `res.country` para buscar, crear o actualizar automáticamente la ficha del cliente que reserva desde el portal público.
- **Seguridad:** Aplica las reglas y grupos base de Odoo (`base.group_user` y `base.group_system`) para restringir la visualización y edición de agendas.

### 2. `calendar`
- **Fuente de verdad para citas:** Las reservas confirmadas se registran directamente como eventos en `calendar.event`.
- **Herencia de calendario:** Extiende los eventos con estados de la cita (`agendame_status`), tipo de agenda (`agendame_type_id`) y país del cliente.
- **Validación de conflictos:** Consulta en tiempo real los eventos existentes del usuario asignado para bloquear horarios ya ocupados y evitar solapamientos.
- **Videollamadas:** Permite configurar enlaces automáticos de videollamada (Odoo Discuss, Google Meet o Zoom).

### 3. `website`
- **Portal público de reservas:** Provee el motor web y las rutas HTTP (`/agendame`, `/agendame/<id>/slots`, `/agendame/submit`) para que usuarios externos puedan reservar sin necesidad de iniciar sesión (`auth="public"`).
- **Plantillas QWeb:** Renderiza la interfaz interactiva, formularios y diseño responsivo (`agendame_templates.xml`) integrados en el sitio web de la empresa.

### 4. `crm`
- **Integración comercial:** Extiende las oportunidades (`crm.lead`) agregando el tipo de cita (`agendame_type_id`) y la URL de reserva directa (`booking_link`).
- **Aceleración de ventas:** Facilita que los ejecutivos comerciales compartan su enlace de disponibilidad directamente desde la ficha del prospecto o negociación.

### 5. `mail`
- **Historial y auditoría (Chatter):** `agendame.type` hereda de `mail.thread` y `mail.activity.mixin`, lo que habilita el chatter para registrar notas, actividades y seguimiento de auditoría en cambios críticos (`tracking=True`).
- **Comunicaciones:** Asegura la integración con el sistema de mensajería para notificar a los participantes de la cita por correo.

---

## Instalación

1. Copia la carpeta `agendame` dentro del addons path de Odoo.
2. Actualiza la lista de addons y busca `Agendame - Appointment Booking`.
3. Instala el módulo.
4. Reinicia el servidor si es necesario.
5. El sistema crea automáticamente una agenda base para cada usuario interno que se cree, si no tiene una ya asociada.

---

## Estructura del módulo

- `__manifest__.py`: metadata del addon y archivos cargados por la instalación.
- `__init__.py`: inicialización del módulo y hooks de instalación.
- `controllers/main.py`: flujo público de reserva y endpoints HTTP.
- `models/appointment_type.py`: modelo principal del tipo de cita y lógica de disponibilidad.
- `models/appointment_slot.py`: horas disponibles por día de la semana.
- `models/calendar_event.py`: extensión del calendario con estados y restricciones de propiedad.
- `models/crm_lead.py`: enlace de reserva y relación con oportunidades.
- `models/res_users.py`: creación de agenda por defecto.
- `security/agendame_security.xml`: reglas de acceso por usuario.
- `views/agendame_type_views.xml`: vistas backend de tipo de cita.
- `views/agendame_templates.xml`: plantillas QWeb del website.
- `views/calendar_event_views.xml`: herencia de la vista del calendario.
- `views/crm_lead_views_inherit.xml`: herencia de oportunidad CRM.
- `tests/test_appointment_booking.py`: pruebas del comportamiento principal.

---

## Modelos principales

### 1) agendame.type

Es el modelo central del sistema. Representa un tipo de cita o agenda.

Campos relevantes:

- `name`: nombre del tipo de cita.
- `appointment_duration`: duración de cada reserva en horas.
- `staff_user_ids`: usuarios internos asignados a esa agenda.
- `slot_ids`: franjas horarias por día de la semana.
- `appointment_tz`: zona horaria de la agenda.
- `event_videocall_source`: origen de videollamada para el evento.
- `image_1920`: imagen del servicio o agenda.
- `color_primary` y `color_secondary`: personalización visual del website.
- `active`: activa o desactiva la agenda.
- `max_schedule_days`: cantidad de días hacia adelante a mostrar.
- `booking_url`: URL pública de reserva calculada automáticamente.

Lógica importante:

- `_create_default_for_user`: crea una agenda base por defecto para cada usuario.
- `_get_appointment_slots`: calcula los horarios disponibles de la agenda.
- `_get_appointment_slots_for_staff`: calcula disponibilidad de un profesional concreto.
- `_is_slot_available_for_staff`: valida si un profesional está libre en una franja específica.
- `_is_offered_slot`: verifica que un horario sea parte del grid ofrecido al usuario público.

### 2) agendame.slot

Representa una franja horaria semanal. Cada registro define:

- `agendame_type_id`: agenda a la que pertenece.
- `weekday`: día de la semana.
- `start_hour`: hora inicio.
- `end_hour`: hora fin.

Se valida que:

- `0 <= start_hour < end_hour <= 24`

Esto evita errores por rangos inválidos que romperían la generación de horarios.

### 3) calendar.event (herencia)

Se extiende el evento nativo del calendario con:

- `agendame_type_id`
- `agendame_status`
- `client_country_id`

Estados soportados:

- `request` — solicitud
- `booked` — reservada
- `attended` — asistió
- `no_show` — no asistió
- `cancelled` — cancelada

Además se aplican restricciones de propiedad para asegurar que un usuario interno no pueda manipular citas ajenas.

### 4) crm.lead

Se extiende la oportunidad con:

- `agendame_type_id`
- `booking_link`

Esto permite asociar una oportunidad a un tipo de cita y compartir el enlace de reserva directo desde CRM.

### 5) res.users

Cuando se crea un usuario interno, el módulo intenta crearle una agenda por defecto con:

- horario de lunes a sábado
- rango 10:00 a 18:00
- zona horaria del usuario
- el mismo usuario como único staff

---

## Flujo público de reserva

### 1. Listado de tipos de cita

Endpoint:

- `/agendame`

Muestra los tipos de cita activos para el visitante.

Regla especial:

- Los usuarios internos ven solo sus agendas propias, según las reglas de acceso de Odoo.
- Los visitantes públicos ven los tipos activos disponibles.

### 2. Página de detalle del tipo

Endpoint:

- `/agendame/<int:agendame_type_id>`

En esta vista se construye el formulario con:

- nombre del servicio
- imagen
- descripción visual
- lista de profesionales disponibles
- países latam
- días y meses traducidos al español

### 3. Carga de horarios por profesional

Endpoint:

- `/agendame/<int:agendame_type_id>/slots`

Recibe el `staff_user_id` y devuelve JSON con fechas y horarios disponibles. La lógica usa la agenda del profesional para calcular slots libres en base a:

- franjas semanales configuradas
- zona horaria del tipo de cita
- eventos ya existentes en el calendario
- bloqueos por conflicto de horarios

### 4. Envío final de la reserva

Endpoint:

- `/agendame/submit`

Este POST valida:

- id del tipo de cita
- profesional seleccionado
- nombre y email obligatorios
- país válido cuando viene informado
- fecha enviada
- que el horario no sea pasado
- que el slot pertenezca al grid ofrecido
- que no exista conflicto de disponibilidad final

Antes de confirmar, el sistema ejecuta una validación de bloqueo con un `SELECT ... FOR UPDATE` para prevenir race conditions entre múltiples reservas simultáneas.

### 5. Creación del evento

Si la validación pasa, el sistema:

- busca o crea un partner con email
- actualiza teléfono y país si faltan
- crea un evento de calendario con:
  - nombre de la cita
  - fecha inicio y fin
  - usuario responsable (professional)
  - partner del cliente
  - `agendame_type_id`
  - `agendame_status = booked`
  - `videocall_source` configurado
  - `client_country_id`

---

## Lógica de disponibilidad

La disponibilidad se calcula en dos niveles:

### Nivel 1: disponibilidad general por tipo de cita

Se revisan todas las franjas configuradas para los días activos y se valida si al menos un staff está libre.

### Nivel 2: disponibilidad por profesional

Cuando un usuario selecciona un profesional, el sistema valida únicamente la agenda de ese usuario y bloquea cualquier horario donde el profesional esté ocupado.

La lógica usa búsqueda y comparación de intervalos con eventos de calendario, evitando los errores de disponibilidad por cambios simultáneos en la base de datos.

---

## Seguridad y permisos

El módulo aplica reglas de acceso por usuario:

- Usuarios internos normales (`base.group_user`) solo pueden leer y editar sus propias agendas.
- Administradores (`base.group_system`) tienen acceso total.
- Los usuarios no pueden agendar ni editar citas ajenas.
- La reserva pública se hace con `sudo()` para permitir la creación del evento desde el sitio web sin autenticar al visitante.
- Las restricciones de la herencia de `calendar.event` impiden que un usuario interno modifique citas donde no es el organizador.

Reglas principales:

- `agendame.type`: usuarios internos ven solo agendas donde están en `staff_user_ids`.
- `agendame.slot`: acceso restringido según el tipo de agenda.

---

## Vistas y frontend

El frontend del website está en `views/agendame_templates.xml`.

Incluye:

- listado de agendas
- tarjeta de tipo de cita
- detalle de agenda y formulario
- selector de profesional
- cargador de horarios mediante AJAX
- bloque de agradecimiento final después de la reserva

La personalización visual se hace con:

- `color_primary`
- `color_secondary`
- `image_1920`

---

## Configuración recomendada

1. Crear un tipo de cita desde `Calendario → Citas → Tipos de Cita`.
2. Asignar al menos un usuario staff.
3. Definir la zona horaria correcta.
4. Configurar la duración del servicio.
5. Crear franjas horarias por día de la semana.
6. Activar la agenda.
7. Compartir la URL pública o la URL del tipo de cita.

### Ejemplo de configuración

- Nombre: Consulta de Ventas
- Duración: 1 hora
- Personal: Ana García
- Zona horaria: America/Santiago
- Días: Lunes a Sábado
- Horario: 09:00 a 18:00
- Videollamada: Google Meet

---

## Casos de uso típicos

- Consultas comerciales
- Citas de soporte
- Reuniones de ventas
- Agendas individuales de profesionales
- Turnos de atención pública
- Toma de entrevistas o onboarding

---

## Troubleshooting

### La página `/agendame` no muestra agendas

Verifica:

- que el tipo de cita esté `Activo`
- que el usuario tenga permisos para ver la agenda
- que el `staff_user_ids` no esté vacío

### Un horario no aparece

Revisa:

- que el slot semanal esté definido correctamente
- que la zona horaria del tipo de cita sea la adecuada
- que exista conflicto con un evento en calendario del profesional
- que la fecha consultada esté dentro de `max_schedule_days`

### La reserva no se confirma

Revisa:

- que el profesional pertenece al staff del tipo de cita
- que el horario aún esté disponible
- que el email esté bien escrito
- que la fecha esté en el formato correcto
- que no se esté intentando reservar un slot pasado

---

## Validaciones

El módulo cuenta con varias validaciones (a través de `@api.constrains`) para asegurar la integridad de la agenda y proteger los datos de cada usuario:

### 1. Franjas Horarias (`agendame.slot`)
- **Coherencia de horario:** Asegura que la hora de inicio sea siempre menor a la hora de fin y que ambas estén dentro del rango de 24 horas (`0 <= inicio < fin <= 24`). Esto evita que un horario configurado de forma incorrecta (como una hora fin menor a la de inicio) rompa el generador de la página pública.

### 2. Tipos de Cita (`agendame.type`)
- **Personal requerido:** Obliga a que toda agenda activa tenga al menos un usuario (staff) asignado para poder funcionar.
- **Restricción de auto-asignación:** Un usuario interno estándar (no administrador) solo puede asignarse a sí mismo como personal de la agenda. Solo los administradores del sistema (`base.group_system`) tienen el permiso de asignar a otros compañeros, previniendo que un empleado manipule la agenda de otro.

### 3. Eventos de Calendario (`calendar.event`)
- **Propiedad del evento:** Si el usuario no es administrador, el sistema valida que solo pueda crear o editar citas donde él mismo sea el organizador.
- **Asistentes limitados:** Se prohíbe que un usuario normal agregue a otras personas (usuarios internos) como asistentes a sus citas. Las citas gestionadas están pensadas exclusivamente para involucrar al profesional y al cliente que reservó.

---

## Buenas prácticas

- Mantén una sola agenda por usuario profesional cuando no necesites múltiples servicios compartidos.
- Usa `appointment_tz` acorde al país o región de atención.
- Define solo los días y horarios reales de operación.
- Evita asignar demasiado personal a un mismo servicio si quiere una lógica más rígida por profesional.
- Valida la disponibilidad en producción con eventos reales y no solo con franjas teóricas.

---

## Licencia

Este addon está licenciado bajo LGPL-3.

---

## Autor

- Victor Bastías Escobar
- Sitio web: https://vicbas.com/addons_odoo.html
- Soporte: contacto@vicbas.com
