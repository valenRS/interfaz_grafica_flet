# Manual de Usuario — MeteoApp

**Dashboard Meteorológico Personal**  
Valentina Rodriguez Sepulveda — 1121789977  
Universidad Tecnológica de Pereira · Interfaz Gráfica con Flet · Mayo 2026

---

## Tabla de contenidos

1. [Descripción de la aplicación](#1-descripción-de-la-aplicación)
2. [Requisitos del sistema](#2-requisitos-del-sistema)
3. [Instalación](#3-instalación)
4. [Ejecución de la aplicación](#4-ejecución-de-la-aplicación)
5. [Guía de uso por ventana](#5-guía-de-uso-por-ventana)
   - [Ventana 1 — Login y Registro](#ventana-1--login-y-registro)
   - [Ventana 2 — Clima actual (Pantalla principal)](#ventana-2--clima-actual-pantalla-principal)
   - [Ventana 3 — Historial meteorológico](#ventana-3--historial-meteorológico)
   - [Ventana 4 — Ciudades favoritas](#ventana-4--ciudades-favoritas)
   - [Ventana 5 — Alertas de temperatura](#ventana-5--alertas-de-temperatura)
6. [Estructura de archivos de datos](#6-estructura-de-archivos-de-datos)
7. [Preguntas frecuentes](#7-preguntas-frecuentes)

---

## 1. Descripción de la aplicación

**MeteoApp** es una aplicación de escritorio desarrollada en Python con la librería [Flet](https://flet.dev/). Permite consultar el clima actual y el historial meteorológico de cualquier ciudad del mundo, gestionar una lista de ciudades favoritas y configurar alertas visuales de temperatura personalizadas.

Los datos provienen de [Open-Meteo](https://open-meteo.com/), una API pública y gratuita que **no requiere registro ni clave de acceso**. Toda la información consultada se guarda localmente en archivos CSV para permitir consultas sin conexión a internet.

---

## 2. Requisitos del sistema

| Requisito | Versión mínima |
|---|---|
| Sistema operativo | Windows 10 / macOS 11 / Ubuntu 20.04 o superior |
| Python | 3.9 o superior |
| Conexión a internet | Requerida para la primera consulta de cada ciudad/período |
| Espacio en disco | ~50 MB (incluyendo el entorno virtual) |

---

## 3. Instalación

### Paso 1 — Clonar o descargar el proyecto

```bash
# Con Git:
git clone <url-del-repositorio>
cd interfaz_grafica_flet

# O descomprimir el archivo .zip descargado y acceder a la carpeta.
```

### Paso 2 — Crear un entorno virtual

```bash
# Linux / macOS
python3 -m venv .venv
source .venv/bin/activate

# Windows (PowerShell)
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

### Paso 3 — Instalar dependencias

```bash
pip install -r requirements.txt
```

Las dependencias que se instalarán son:

| Librería | Versión | Propósito |
|---|---|---|
| flet | 0.28.3 | Framework de la interfaz gráfica |
| pandas | última estable | Lectura y escritura de archivos CSV |
| requests | última estable | Llamadas a la API Open-Meteo |
| matplotlib | última estable | Generación de gráficas |
| Pillow | última estable | Generación de íconos del clima |

### Paso 4 — Verificar la instalación (opcional)

```bash
python -c "import flet, pandas, requests, matplotlib, PIL; print('Todo instalado correctamente.')"
```

---

## 4. Ejecución de la aplicación

Con el entorno virtual activado, desde la carpeta raíz del proyecto:

```bash
python main.py
```

La ventana de la aplicación se abrirá automáticamente (960 × 680 px, redimensionable hasta 800 × 580 px mínimo).

> **Nota:** La primera ejecución puede tardar unos segundos mientras Flet inicializa su motor de renderizado.

---

## 5. Guía de uso por ventana

---

### Ventana 1 — Login y Registro

**Archivo:** `views/login_view.py`

Esta es la primera pantalla que aparece al iniciar MeteoApp.

#### Iniciar sesión

1. Selecciona el radio button **"Iniciar sesión"** (opción por defecto).
2. Ingresa tu **nombre de usuario** en el primer campo.
3. Ingresa tu **contraseña** en el segundo campo. Puedes usar el ícono del ojo para revelarla.
4. Haz clic en el botón **"Ingresar"**.
5. Si las credenciales son correctas, pasarás automáticamente a la pantalla principal.

#### Crear cuenta nueva

1. Selecciona el radio button **"Registrarse"**.
2. Elige un **nombre de usuario** (sin espacios, mínimo 1 carácter).
3. Elige una **contraseña** de al menos 4 caracteres.
4. Haz clic en **"Crear cuenta"**.
5. Si el nombre de usuario no existe, la cuenta se crea y entras directamente a la app.

> **Seguridad:** Las contraseñas nunca se guardan en texto plano. Se almacenan como hashes SHA-256 en `data/usuarios.csv`.

**Mensajes posibles:**

| Mensaje | Significado |
|---|---|
| "Usuario o contraseña incorrectos." | Credenciales inválidas en el login |
| "El usuario ya existe." | Nombre de usuario ya registrado |
| "La contraseña debe tener al menos 4 caracteres." | Contraseña demasiado corta |

---

### Ventana 2 — Clima actual (Pantalla principal)

**Archivo:** `views/home_view.py`

Esta es la pantalla principal de MeteoApp. Desde aquí puedes consultar el clima actual de cualquier ciudad.

#### Buscar el clima de una ciudad

1. Escribe el nombre de la ciudad en el campo de texto (p. ej., `Bogotá`, `Paris`, `Tokyo`).
   - También puedes seleccionarla del **menú desplegable** si ya la tienes guardada como favorita.
2. Haz clic en **"Buscar"** o presiona Enter.
3. La tarjeta de clima mostrará:
   - Temperatura actual (°C) con ícono generado dinámicamente
   - Temperatura máxima / mínima del día
   - Sensación térmica (°C)
   - Velocidad del viento (km/h)
   - Humedad relativa (%)
   - Condición climática (soleado, nublado, lluvia, tormenta, nieve, etc.)

#### Guardar una ciudad como favorita

- Activa el **checkbox "Guardar como favorita"** antes o después de buscar.
- La ciudad aparecerá en el dropdown de favoritas en todas las ventanas de la app.

#### Alertas de temperatura

- Si configuraste umbrales de alerta para la ciudad consultada (en la Ventana 5), y la temperatura actual los supera, aparecerá un **banner naranja** con el mensaje de alerta en la parte inferior de la tarjeta.

#### Navegación

Usa los botones del encabezado para ir a:
- **"Historial"** → Ventana 3
- **"Ciudades"** → Ventana 4
- **"Alertas"** → Ventana 5

---

### Ventana 3 — Historial meteorológico

**Archivo:** `views/history_view.py`

Consulta el historial climático de una ciudad en un rango de fechas y visualízalo en gráficas.

#### Consultar el historial

1. Selecciona la **ciudad** del menú desplegable (solo ciudades guardadas en favoritas).
2. Haz clic en **"Seleccionar fecha de inicio"** para abrir el calendario y elegir la fecha de inicio.
3. Ajusta el **slider "Días a consultar"** (de 7 a 90 días) para definir el período.
   - La fecha de fin se calcula automáticamente: inicio + días seleccionados, con máximo hasta ayer.
4. Haz clic en **"Consultar historial"**.
5. Mientras se carga, aparece un indicador de progreso (círculo giratorio).
6. Una vez completado, se muestran dos gráficas:
   - **Temperatura** (líneas): máxima (roja) y mínima (azul) por día
   - **Precipitación** (barras): lluvia acumulada en mm por día

#### Cache local

- Los datos consultados se guardan automáticamente en `data/historial_clima.csv`.
- Si vuelves a consultar el mismo período de la misma ciudad, la app **no hace una nueva llamada a la API** y usa los datos guardados, lo que permite funcionar sin internet.

---

### Ventana 4 — Ciudades favoritas

**Archivo:** `views/cities_view.py`

Gestiona tu lista personal de ciudades favoritas.

#### Agregar una ciudad

1. Escribe el nombre de la ciudad en el campo de texto.
2. Haz clic en **"Agregar"**.
3. La app verificará las coordenadas geográficas de la ciudad via la API de geocodificación.
4. Si la ciudad es encontrada y no está duplicada, se añade a la lista.

#### Eliminar ciudades

1. Activa el **checkbox** junto a una o varias ciudades que deseas eliminar.
2. Haz clic en el botón rojo **"Eliminar seleccionadas"**.
3. Las ciudades se eliminan de `data/ciudades.csv` y desaparecen de todos los dropdowns.

> **Nota:** El contador en la parte superior muestra cuántas ciudades tienes guardadas.

---

### Ventana 5 — Alertas de temperatura

**Archivo:** `views/alerts_view.py`

Configura umbrales de temperatura para cada ciudad favorita. Cuando consultes el clima actual de esa ciudad en la Ventana 2, recibirás un aviso visual si la temperatura supera los límites configurados.

#### Configurar una alerta

1. Selecciona la **ciudad** del menú desplegable.
2. Ajusta el **slider "Temperatura máxima de alerta"** (rango: −20°C a 50°C).
3. Ajusta el **slider "Temperatura mínima de alerta"** (rango: −20°C a 50°C).
   - Los sliders tienen validación cruzada: la máxima siempre supera a la mínima en al menos 1°C.
4. Activa el **checkbox "Activar alerta para esta ciudad"**.
5. Haz clic en **"Guardar configuración"**.

#### Desactivar una alerta

- Desmarca el checkbox **"Activar alerta para esta ciudad"** y haz clic en **"Guardar configuración"**.
- Los umbrales se borran y la alerta deja de mostrarse en la Ventana 2.

#### Resumen de alertas activas

En la parte inferior de la ventana se muestra una lista de todas las ciudades que tienen alertas configuradas, con sus umbrales máximo y mínimo.

---

## 6. Estructura de archivos de datos

MeteoApp guarda toda su información en la carpeta `data/`. Estos archivos CSV se crean automáticamente al usar la aplicación.

### `data/usuarios.csv`

| Columna | Descripción |
|---|---|
| id | Identificador único del usuario |
| username | Nombre de usuario |
| password_hash | Contraseña cifrada (SHA-256) |
| fecha_registro | Fecha y hora de creación de la cuenta |

### `data/ciudades.csv`

| Columna | Descripción |
|---|---|
| id | Identificador único |
| ciudad | Nombre de la ciudad |
| pais | País |
| latitud | Coordenada geográfica |
| longitud | Coordenada geográfica |
| alerta_max_temp | Umbral de temperatura máxima (°C) o vacío si no hay alerta |
| alerta_min_temp | Umbral de temperatura mínima (°C) o vacío si no hay alerta |

### `data/historial_clima.csv`

| Columna | Descripción |
|---|---|
| id | Identificador del registro |
| ciudad | Nombre de la ciudad |
| fecha | Fecha del registro (YYYY-MM-DD) |
| temp_max | Temperatura máxima del día (°C) |
| temp_min | Temperatura mínima del día (°C) |
| precipitacion | Precipitación acumulada (mm) |
| viento_max | Velocidad máxima del viento (km/h) |

> **Consejo:** Puedes abrir estos archivos con Excel o cualquier editor de texto para revisar o exportar los datos. No los modifiques mientras la aplicación está abierta.

---

## 7. Preguntas frecuentes

**¿Necesito una clave de API para usar MeteoApp?**  
No. Open-Meteo es completamente gratuita y no requiere registro.

**¿Puedo usar la app sin internet?**  
Sí, pero solo para ciudades y períodos que ya hayas consultado antes (los datos quedan en `historial_clima.csv`). La búsqueda de clima actual siempre requiere conexión.

**¿Qué pasa si la ciudad que escribo no aparece?**  
La aplicación usa el servicio de geocodificación de Open-Meteo. Si la ciudad no es encontrada, aparecerá un mensaje de error. Intenta con el nombre en inglés o añade el país (p. ej., `Paris, France`).

**¿Puedo tener múltiples usuarios?**  
Sí. Cada usuario tiene su propia sesión de inicio, pero todos comparten la misma lista de ciudades favoritas y el historial (ya que la app es de uso personal en un equipo).

**¿Cómo elimino todos los datos y empiezo de cero?**  
Elimina o vacía (dejando solo los encabezados) los archivos `data/usuarios.csv`, `data/ciudades.csv` y `data/historial_clima.csv`.

**La app muestra "Error al obtener datos". ¿Qué hago?**  
Verifica tu conexión a internet. Si el problema persiste, la API de Open-Meteo puede estar temporalmente no disponible.

---

*MeteoApp — Proyecto Final · Interfaz Gráfica con Flet · Universidad Tecnológica de Pereira · 2026*
