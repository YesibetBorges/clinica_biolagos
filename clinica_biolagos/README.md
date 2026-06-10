# Clinica BioLagos

Proyecto Django para la gestion y solicitud de horas medicas de una clinica.

## Alcance

La aplicacion permite navegar por paginas publicas, solicitar una hora sin iniciar sesion y acceder a un area privada para gestionar pacientes, medicos y citas segun el tipo de usuario.

## Requisitos

- Python 3.10 o superior
- pip
- Git

## Clonacion

```bash
git clone https://github.com/YesibetBorges/clinica_biolagos.git
cd clinica_biolagos
code .
```

## Instalacion

```bash
python -m venv venv
```

Windows:

```bash
venv\Scripts\activate
```

Instalar dependencias:

```bash
pip install -r requirements.txt
```

Aplicar migraciones:

```bash
python manage.py migrate
```

Cargar datos iniciales:

```bash
python setup_inicial.py
```

Ejecutar servidor:

```bash
python manage.py runserver
```

Abrir:

```text
http://127.0.0.1:8000/
```

## Usuarios de prueba

| Rol | Usuario | Contrasena |
| --- | --- | --- |
| Superusuario | admin | admin123 |
| Paciente | yesi | Yesi1234 |
| Doctor | carlos | Carlos1234 |

## Rutas principales

- Inicio publico: `/`
- Nosotros: `/nosotros/`
- Servicios: `/servicios/`
- Contacto: `/contacto/`
- Solicitud publica de hora: `/solicitar-hora/`
- Login: `/cuenta/login/`
- Dashboard privado: `/dashboard/`
- Pacientes: `/pacientes/`
- Citas: `/citas/`
- Medicos: `/medicos/`
- Admin Django: `/admin/`

## Estructura del Proyecto

```text
clinica_biolagos/
├── clinica_app/                # Aplicación principal de lógica de negocio
│   ├── migrations/             # Migraciones de base de datos (Ej: RUT y Bloques)
│   ├── access.py               # Control de acceso y lógica de roles (Admin/Médico/Paciente)
│   ├── forms.py                # Formularios con validación de RUT y gestión de horarios
│   ├── models.py               # Modelos: Especialidad, Medico, Paciente, Cita, BloqueHorario
│   ├── urls.py                 # Rutas internas de la aplicación clínica
│   └── views.py                # Lógica de gestión de citas y CRUD de pacientes/médicos
├── core/                       # Aplicación para la interfaz pública y el Dashboard
│   ├── models.py               # Modelos base de la app core
│   ├── urls.py                 # Rutas de páginas estáticas y dashboard
│   └── views.py                # Vistas de Inicio, Nosotros, Contacto y Dashboard
├── clinica_biolagos/           # Carpeta de configuración global del proyecto
│   ├── settings.py             # Configuración de base de datos, apps y middleware
│   ├── urls.py                 # Enrutador principal del sitio
│   └── wsgi.py / asgi.py       # Interfaces de servidores web
├── templates/                  # Directorio central de plantillas HTML
│   ├── base.html               # Estructura base con Bootstrap 5 y Navbar corporativa
│   ├── clinica_app/            # Plantillas para Citas, Médicos y Pacientes
│   ├── core/                   # Plantillas para Dashboard y páginas públicas
│   └── registration/           # Plantillas para el sistema de Autenticación (Login)
├── manage.py                   # Utilidad de línea de comandos de Django
├── requirements.txt            # Dependencias del proyecto (Django, etc.)
├── setup_inicial.py            # Script para poblar la base de datos con usuarios de prueba
└── test_requisitos.py          # Script de validación de reglas de negocio (RUT y Bloques)
```

## Funcionalidades

- Proyecto Django con dos aplicaciones: `core` y `clinica_app`.
- Sistema de autenticacion con login y logout.
- Base de datos SQLite.
- Vistas publicas para visitantes.
- Area privada protegida con `login_required`.
- Dashboard con permisos diferenciados para superusuario, paciente y doctor.
- Formulario publico para solicitar hora medica.
- Interfaz HTML con Bootstrap, CSS y JavaScript.

## Otras Funcionalidades

- Arquitectura Modular: Proyecto Django estructurado limpiamente con dos aplicaciones funcionales (core y clinica_app).
- Autenticación Completa: Sistema seguro de login y logout integrado.
- Persistencia Local: Uso de base de datos SQLite optimizada para el desarrollo.
- Área Privada Blindada: Protección estricta de vistas operativas mediante el uso de @login_required.
- Roles Diferenciados: Dashboard dinámico con permisos y despliegues visuales específicos para Superusuario, Pacientes y Doctores.
- Reserva Pública: Formulario público adaptativo para la solicitud de horas médicas por parte de pacientes externos.
- Interfaz de Vanguardia: Diseño HTML5 integrado con Bootstrap, estilos CSS personalizados y dinamismo mediante JavaScript.

## Validación de Requisitos Técnicos (Cumplimiento de Rúbrica LPOO2 Ev3)
El diseño y desarrollo del proyecto Clínica BioLagos cumple de manera estricta con la totalidad de los criterios e indicadores de la rúbrica de evaluación:

1. Requisitos de Estructura y Modelos
Proyecto Django con Aplicaciones: Organización arquitectónica impecable basada en la separación de responsabilidades mediante las apps clinica_app y core.

Modelos y Relaciones Avanzadas: Supera el requerimiento mínimo al implementar 5 modelos de datos interconectados en clinica_app/models.py: Especialidad, Medico, Paciente, Cita y BloqueHorario, vinculados de forma lógica mediante relaciones ForeignKey.

Arquitectura MVT: Adhesión rigurosa al estándar de diseño de Django (Modelos, Vistas y Plantillas).

2. Autenticación y Áreas de Acceso
Sistema de Autenticación Integrado: Autenticación de usuarios resuelta mediante el subsistema nativo de Django. Control dinámico en la barra de navegación (base.html) utilizando directrices Jinja ({% if user.is_authenticated %}).

Vistas Públicas Orientadas al Usuario: Disponibilidad de páginas informativas abiertas y acceso libre al formulario crítico de solicitar_hora.

Área Privada con Control de Roles: Seguridad reforzada mediante interceptores @login_required y lógica centralizada en access.py (ej. can_access_paciente, can_access_cita), restringiendo el acceso a datos sensibles según el rol o la propiedad de la cita.

3. Persistencia y Manipulación de Datos
Flujo de Datos y Migraciones: Migraciones debidamente estructuradas y base de datos persistente basada en SQLite.

CRUD Independiente del Panel Administrador: Cumplimiento estricto del requerimiento de desarrollo de flujos. Todo el ciclo de creación, lectura, actualización y borrado (CRUD) se realiza a través de formularios personalizados (PacienteForm, CitaForm, MedicoForm, BloqueHorarioForm) embebidos en la interfaz de usuario web, dejando el /admin/ exclusivamente para tareas operativas de bajo nivel.

4. Validaciones y Errores
Filtros en Backend: Algoritmo de validación de RUT chileno implementando la lógica de verificación por Módulo 11 en las capas de modelos y formularios. Control activo de solapamiento de agendas para evitar colisiones en los bloques horarios.

Filtros en Frontend: Formularios web optimizados mediante controles interactivos de Bootstrap 5 y restricciones semánticas HTML5 (type="date", type="time").

Feedback y Mensajería Activa: Integración nativa del framework de mensajería de Django (messages.success, messages.error), brindando notificaciones en tiempo real al usuario ante operaciones exitosas o fallidas.

5. Interfaz de Usuario (UI/UX)
Maquetación y Estética Profesional: Diseño implementado en base.html con Bootstrap 5, tipografía estilizada vía Google Fonts e iconografía moderna. El dashboard incorpora componentes visuales dinámicos de analítica corporativa (stat-card) y consumo asíncrono de endpoints mediante la API JSON local de horas_disponibles_json.

## Mejoras Futuras
- Implementación de notificaciones automatizadas vía correo electrónico/SMS (Confirmación de citas).
- Módulo de Historial Clínico digital cronológico.
- Integración de pasarela de pagos para consultas particulares.
- Construcción de endpoints mediante API RESTful utilizando Django REST Framework.

## Información del Autor
- Desarrollador: Yesibet Borges Yegres
- Contexto: Proyecto de Evaluación Práctica para la asignatura de LPOO2 (Ingeniería en Informática).
- Licencia: Uso exclusivamente académico y educativo.
