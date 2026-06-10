# Clinica BioLagos

Proyecto Django para la gestion y solicitud de horas medicas de una clinica.

## Alcance

La aplicacion permite navegar por paginas publicas, solicitar una hora sin iniciar sesion y acceder a un area privada para gestionar pacientes, medicos y citas segun el tipo de usuario.

## Requisitos

- Python 3.10 o superior
- pip
- Git

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

## Funcionalidades

- Proyecto Django con dos aplicaciones: `core` y `clinica_app`.
- Sistema de autenticacion con login y logout.
- Base de datos SQLite.
- Vistas publicas para visitantes.
- Area privada protegida con `login_required`.
- Dashboard con permisos diferenciados para superusuario, paciente y doctor.
- Formulario publico para solicitar hora medica.
- Interfaz HTML con Bootstrap, CSS y JavaScript.

## Presentacion sugerida

1. Presentar el problema: una clinica necesita mostrar informacion y gestionar solicitudes de horas.
2. Explicar el alcance: paginas publicas, autenticacion, area privada, pacientes, medicos y citas.
3. Mostrar la navegacion publica: inicio, servicios, contacto y solicitud de hora.
4. Mostrar login y dashboard.
5. Comparar roles: superusuario, paciente Yesi y doctor Carlos.
6. Cerrar con mejoras futuras: notificaciones, historial clinico, pagos o recordatorios.
