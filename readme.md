# Catolicomm

Catolicom es una aplicación web para que la comunidad católica comparta información básica de templos, horarios de misas, confesiones y otros servicios. Cuántas veces no nos hemos encontrado investigando en redes sociales a qué hora puedo ir a misa un día en específico o a qué hora y ddónde puedo buscar el sacramento de la reconciliación.

Catolicomm busca ayudar a la comunidad a compartir esa información de manera centralizada. Actualizada y enriquecida por la misma comunidad católica para que se nos facilite acercarnos a Jesús.

## Tecnología

- Python 3.13.0
- Django 6.1
- sqlite

## Ejecución

1. Generación de entorno virtual e instalación de dependencias
```
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
```

2. Migraciones y creación de superusuario
```
python manage.py migrate
python manage.py createsuperuser
```
Seguir las instrucciones para crear el superusuario


3. Ejecución del servicio en modo pruebas
```
python manage.py runserver
```
