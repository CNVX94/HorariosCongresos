# Horarios Try - Sistema de Agendamiento

Este es un proyecto construido con Django diseñado para gestionar congresos, días, espacios (slots) y charlas (talks). Proporciona un panel de administración para administrar la disponibilidad de horarios y permite pre-crear y asignar charlas de manera eficiente.

## Requisitos Previos

- Python 3.x
- pip, virtualenv (recomendado)
- Django 4.2 o superior

## Instalación y Configuración

Sigue estos pasos para poner el proyecto en marcha en tu máquina local:

### 1. Clonar el repositorio

Si el proyecto está en un repositorio Git:
```bash
git clone <url-del-repositorio>
cd HorariosTry
```

### 2. Crear un entorno virtual

Es buena práctica usar un entorno virtual para aislar las dependencias:
```bash
python -m venv venv
```

Activa el entorno virtual:
- En Linux / macOS:
```bash
source venv/bin/activate
```
- En Windows:
```bash
venv\Scripts\activate
```

### 3. Instalar las dependencias

Instala los paquetes necesarios. Como es un proyecto Django estándar, puedes usar un archivo `requirements.txt` si se provee. Si no, instala Django manualmente:
```bash
pip install django==4.2
```
*(Asegúrate de instalar cualquier otra dependencia como Pillow u otras librerías requiridas agregándolas mediante `pip install`).*

### 4. Aplicar las migraciones de la base de datos

Ejecuta las migraciones para crear las tablas necesarias en la base de datos SQLite predeterminada:
```bash
python manage.py makemigrations
python manage.py migrate
```

### 5. Crear un superusuario (opcional)

Si deseas acceder al panel de administración de Django (`/admin/`), crea un usuario administrador:
```bash
python manage.py createsuperuser
```
Luego sigue las instrucciones en la pantalla para iterar por un nombre de usuario, correo y contraseña.

### 6. Ejecutar el servidor de desarrollo

Inicia el servidor local:
```bash
python manage.py runserver
```

El proyecto estará disponible en [http://127.0.0.1:8000/](http://127.0.0.1:8000/).
Para acceder al panel de administración visita: [http://127.0.0.1:8000/admin/](http://127.0.0.1:8000/admin/)


---