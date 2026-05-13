# Interfaz Gráfica con Flet

Este repositorio ahora incluye una configuracion minima para evitar problemas de dependencias con Flet.

## Requisitos

- Python 3.10 o superior
- pip actualizado

## Instalacion recomendada

1. Crear entorno virtual:

	python3 -m venv .venv

2. Activar entorno virtual:

	source .venv/bin/activate

3. Actualizar pip:

	python -m pip install --upgrade pip

4. Instalar dependencias del proyecto:

	python -m pip install -r requirements.txt

## Nota importante sobre versiones

La dependencia principal de Flet esta fijada en una version estable para evitar errores por cambios incompatibles en releases nuevas.

Si necesitas migrar a una version mas reciente, actualiza requirements.txt y valida el codigo de la app antes de usarla en produccion.
