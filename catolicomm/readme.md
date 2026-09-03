# Catolicomm

Catolicom es una aplicación web para que la comunidad católica comparta información básica de templos, horarios de misas y horarios de confesiones. Para poder estar informado al momento de decidir a qué hora y dónde ir a misa o buscar la confesión.

## Tecnología

- Python 3.12.3
- Django 6.1
- sqlite

## Ejecución

Instalación de dependencias
```
pip install -r requirements.txt
source .venv/bin/activate
```

Migraciones y creación de superusuario
```
python manage.py migrate
python manage.py createsuperuser
```
Seguir las instrucciones para crear el superusuario


Ejecución del servicio
```
python manage.py runserver
```