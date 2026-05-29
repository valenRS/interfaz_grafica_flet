# Presentación de Propuesta: Proyecto Interfaz Gráfica – FLET

---

## 1. Título del proyecto y la aplicación

**Título del proyecto:** MeteoApp — Dashboard Meteorológico Personal

**Nombre de la aplicación:** MeteoApp

---

## 2. Información General del integrante

| Campo | Información |
|---|---|
| **Nombre completo** | [Valentina Rodriguez Sepulveda] |
| **Código estudiantil** | [1125789977] |
| **Correo institucional** | [valentina.rodriguez6@utp.edu.co] |
| **Fecha de presentación** | 13 de mayo de 2026 |

---

## 3. Descripción general del proyecto

**MeteoApp** es una aplicación de escritorio desarrollada en Python utilizando la librería Flet. Permite a cualquier usuario consultar el clima actual y el historial meteorológico de ciudades de todo el mundo, desde una sola interfaz organizada e intuitiva.

La aplicación obtiene sus datos desde **Open-Meteo** (https://open-meteo.com/), una API pública y completamente gratuita que no requiere registro ni clave de acceso. Los datos se entregan en formato JSON, se procesan con la librería pandas y se visualizan en gráficas generadas con matplotlib.

**Problema que resuelve:** Hoy en día, consultar el historial climático de una ciudad o comparar el clima entre varios lugares implica visitar múltiples sitios web y copiar datos manualmente. MeteoApp centraliza esta información, la almacena de forma persistente en archivos CSV y la presenta de manera visual con gráficas claras y un diseño agradable.

**Contexto de uso:** Aplicación de escritorio de uso personal. El usuario la instala en su computador y la usa localmente sin necesidad de conexión constante a internet (los datos consultados quedan guardados para consulta offline).

---

## 4. Objetivo del proyecto

Desarrollar una aplicación de escritorio funcional, modular y orientada a objetos en Python con Flet, que permita al usuario:

- Registrarse e iniciar sesión de forma segura con contraseña cifrada.
- Consultar el clima actual de cualquier ciudad del mundo en tiempo real.
- Visualizar el historial meteorológico de una ciudad en un rango de fechas, representado mediante gráficas de líneas y barras.
- Gestionar una lista personal de ciudades favoritas para acceso rápido.
- Configurar alertas visuales personalizadas de temperatura por ciudad.
- Conservar de forma permanente el historial de todas las consultas realizadas.

---

## 5. Funciones principales

### 5.1 Sistema de autenticación (Login y Registro)

El usuario puede crear una cuenta nueva o iniciar sesión con una existente. Las contraseñas se almacenan de forma cifrada (hash SHA-256) para mayor seguridad. Esta es la primera ventana que aparece al abrir la aplicación.

**Almacenamiento:** archivo `usuarios.csv`

| Columna | Descripción |
|---|---|
| id | Identificador único del usuario |
| username | Nombre de usuario |
| password_hash | Contraseña cifrada (SHA-256) |
| fecha_registro | Fecha en que se creó la cuenta |

---

### 5.2 Consulta de clima actual (Pantalla principal)

El usuario busca una ciudad escribiéndola en un campo de texto o seleccionándola de su lista de favoritas. La aplicación realiza una petición a la API de Open-Meteo y muestra los siguientes datos en tarjetas visuales:

- Temperatura actual (°C)
- Temperatura máxima y mínima del día
- Sensación térmica
- Velocidad del viento (km/h)
- Humedad relativa (%)
- Condición climática (soleado, nublado, lluvia, etc.) con ícono representativo

El usuario también puede marcar la ciudad como favorita con un checkbox para guardarla en su lista.

---

### 5.3 Historial meteorológico con gráficas

El usuario selecciona una ciudad y un rango de fechas (hasta 3 meses hacia atrás). La aplicación consulta la API histórica de Open-Meteo, procesa los datos con pandas y genera automáticamente **dos gráficas** con matplotlib:

**Gráfica 1 — Temperatura en el tiempo (gráfica de líneas)**
Muestra la temperatura máxima y mínima de cada día dentro del rango seleccionado. Permite identificar tendencias de calor o frío a lo largo del período.

**Gráfica 2 — Precipitación acumulada por día (gráfica de barras)**
Muestra la cantidad de lluvia registrada cada día. Permite identificar épocas de sequía o períodos lluviosos.

Los datos descargados se guardan automáticamente en `historial_clima.csv` para que la próxima vez que se consulte el mismo período, la app no tenga que volver a conectarse a internet.

**Almacenamiento:** archivo `historial_clima.csv`

| Columna | Descripción |
|---|---|
| id | Identificador del registro |
| ciudad | Nombre de la ciudad |
| fecha | Fecha del registro (YYYY-MM-DD) |
| temp_max | Temperatura máxima del día (°C) |
| temp_min | Temperatura mínima del día (°C) |
| precipitacion | Precipitación acumulada (mm) |
| viento_max | Velocidad máxima del viento (km/h) |

---

### 5.4 Gestión de ciudades favoritas

El usuario puede ver, agregar y eliminar ciudades de su lista personal. Las ciudades guardadas aparecen en el menú desplegable de toda la aplicación para un acceso rápido. También se muestra el total de ciudades guardadas.

**Almacenamiento:** archivo `ciudades.csv`

| Columna | Descripción |
|---|---|
| id | Identificador único |
| ciudad | Nombre de la ciudad |
| pais | País al que pertenece |
| latitud | Coordenada geográfica (usada por la API) |
| longitud | Coordenada geográfica (usada por la API) |
| alerta_max_temp | Umbral de temperatura máxima para alerta (°C) |
| alerta_min_temp | Umbral de temperatura mínima para alerta (°C) |

---

### 5.5 Alertas personalizadas de temperatura

El usuario configura para cada ciudad favorita los valores máximo y mínimo de temperatura que considera normales. Si al consultar el clima actual se detecta que la temperatura supera o está por debajo de esos umbrales, la interfaz muestra un aviso visual destacado (cambio de color y mensaje de alerta). La configuración se guarda en `ciudades.csv`.

---

## 6. Librerías a utilizar

| Librería | Propósito específico en la aplicación |
|---|---|
| **Flet** | Framework principal para construir la interfaz gráfica de usuario (GUI) de escritorio con Python |
| **Pandas** | Lectura, escritura, filtrado y procesamiento de los archivos CSV (bases de datos de la aplicación) |
| **requests** | Realizar peticiones HTTP a la API de Open-Meteo para obtener datos del clima en formato JSON |
| **Matplotlib** | Generar las gráficas de temperatura (líneas) y precipitación (barras), exportadas como imágenes PNG e integradas en la interfaz |
| **Pillow (PIL)** | Cargar, redimensionar y mostrar los íconos del clima (sol, nubes, lluvia, nieve, etc.) dentro de la interfaz |

> **Total de librerías adicionales a Flet y Pandas: 3** (requests, matplotlib, Pillow) — cumple el requisito mínimo de la rúbrica.

---

## 7. Audiencia objetivo / usuarios esperados

**¿Quién usaría esta aplicación?**

- Personas que viajan frecuentemente y necesitan comparar el clima de varios destinos.
- Trabajadores en exteriores (construcción, agricultura, eventos) que dependen del clima.
- Estudiantes de geografía, ciencias ambientales o climatología que trabajan con datos históricos.
- Usuarios generales curiosos que quieren llevar un registro del clima de las ciudades que les interesan.

**Perfil técnico del usuario:** No se requieren conocimientos de programación. La interfaz es intuitiva y guiada. Solo es necesario tener Python instalado en el equipo. Está dirigida a usuarios desde 15 años en adelante.

---

## 8. Estructura preliminar del proyecto

### 8.1 Organización de archivos

```
interfaz_grafica_flet/
├── main.py                     # Archivo principal: inicia la app y controla la navegación
├── requirements.txt            # Lista de dependencias del proyecto
├── data/
│   ├── usuarios.csv            # Base de datos 1: cuentas de usuario
│   ├── ciudades.csv            # Base de datos 2: ciudades favoritas y alertas
│   └── historial_clima.csv     # Base de datos 3: historial de consultas meteorológicas
├── assets/
│   ├── charts/                 # Gráficas generadas por matplotlib (archivos PNG)
│   └── icons/                  # Íconos del clima procesados con Pillow
├── views/
│   ├── login_view.py           # Ventana 1: Inicio de sesión y registro
│   ├── home_view.py            # Ventana 2: Pantalla principal (clima actual)
│   ├── history_view.py         # Ventana 3: Historial y gráficas
│   ├── cities_view.py          # Ventana 4: Gestión de ciudades favoritas
│   └── alerts_view.py          # Ventana 5: Configuración de alertas
└── utils/
    ├── api_client.py           # Módulo para comunicarse con Open-Meteo API
    ├── data_manager.py         # Módulo para leer y escribir los archivos CSV
    └── chart_generator.py      # Módulo para generar las gráficas con matplotlib
```

> Cada ventana es una **clase independiente** en su propio archivo Python, cumpliendo el paradigma de **Programación Orientada a Objetos (POO)** y el requisito de modularidad de la rúbrica.

---

### 8.2 Descripción de cada ventana

---

#### Ventana 1 — LoginView (`login_view.py`)
**Propósito:** Autenticación del usuario. Es la primera ventana que aparece al ejecutar la aplicación.

**Componentes gráficos:**
- **Radio buttons** para seleccionar entre "Iniciar sesión" y "Registrarse" (el formulario cambia dinámicamente)
- Campos de texto para ingresar usuario y contraseña
- Botón principal de acción ("Ingresar" o "Crear cuenta")
- Mensaje de error o confirmación según el resultado
- Logo o imagen de la aplicación

**Temática visual:** Fondo azul oscuro (`#1565C0`), texto blanco, botón en celeste brillante. Transmite confianza y seriedad.

---

#### Ventana 2 — HomeView (`home_view.py`)
**Propósito:** Pantalla principal. Muestra el clima actual de la ciudad seleccionada.

**Componentes gráficos:**
- Campo de texto para buscar ciudad
- **Menú desplegable (dropdown)** con ciudades favoritas guardadas
- Tarjetas con los datos del clima (temperatura, viento, humedad, etc.)
- **Ícono del clima** generado con Pillow (sol, nubes, lluvia)
- **Checkbox** "Guardar esta ciudad como favorita"
- Botones de navegación hacia las demás ventanas
- Aviso visual si se supera algún umbral de alerta

**Temática visual:** Azul cielo (`#42A5F5`), tarjetas blancas con sombra suave, íconos coloridos.

---

#### Ventana 3 — HistoryView (`history_view.py`)
**Propósito:** Consulta del historial meteorológico y visualización de gráficas.

**Componentes gráficos:**
- **Menú desplegable** para seleccionar la ciudad
- **Selector de fecha (DatePicker)** para fecha de inicio y fecha de fin
- **Slider** para ajustar el rango de días que se muestra en la gráfica
- Botón "Consultar historial"
- Dos imágenes PNG con las gráficas generadas por matplotlib:
  - Gráfica de líneas: temperatura máxima y mínima
  - Gráfica de barras: precipitación por día
- Indicador de carga mientras se obtienen los datos

**Temática visual:** Azul marino (`#0D47A1`), fondos claros para las gráficas, encabezados en negrita.

---

#### Ventana 4 — CitiesView (`cities_view.py`)
**Propósito:** Gestión de la lista de ciudades favoritas del usuario.

**Componentes gráficos:**
- Lista de ciudades guardadas, cada una con un **checkbox** para seleccionarla
- Botón "Eliminar seleccionadas" (rojo) para borrar las ciudades marcadas
- Campo de texto para agregar una nueva ciudad manualmente
- Botón "Agregar ciudad"
- Contador: "X ciudades guardadas"

**Temática visual:** Celeste claro (`#29B6F6`), filas de ciudad con íconos de ubicación, diseño tipo lista ordenada.

---

#### Ventana 5 — AlertsView (`alerts_view.py`)
**Propósito:** Configurar los umbrales de temperatura para las alertas visuales.

**Componentes gráficos:**
- **Menú desplegable** para seleccionar una ciudad favorita
- **Slider** para definir la temperatura máxima de alerta (ej: 35°C)
- **Slider** para definir la temperatura mínima de alerta (ej: 5°C)
- **Checkbox** "Activar alerta para esta ciudad"
- Botón "Guardar configuración"
- Resumen de alertas activas

**Temática visual:** Consistente con el resto de la app, con íconos de advertencia en amarillo/naranja para mayor claridad.

---

### 8.3 Flujo de navegación

```
[LoginView]
     ↓ (autenticación exitosa)
[HomeView] ←──────────────────────────────┐
     ↓              ↓              ↓       │
[HistoryView]  [CitiesView]  [AlertsView]  │
     └──────────────┴──────────────┘───────┘
          (cada ventana tiene botón "Volver al inicio")
```

> **Regla obligatoria (rúbrica):** Al abrir cualquier ventana, todas las demás se cierran automáticamente. Solo hay una ventana activa en todo momento.

---

### 8.4 Temática visual general

| Elemento | Valor |
|---|---|
| Color primario | Azul cielo `#42A5F5` |
| Color secundario | Azul oscuro `#1565C0` |
| Color de acento | Celeste brillante `#29B6F6` |
| Fondo principal | Blanco `#FFFFFF` / Gris muy claro `#F5F5F5` |
| Tipografía | Roboto (incluida en Flet por defecto) |
| Estilo general | Moderno, limpio, con tarjetas redondeadas y sombras suaves |
