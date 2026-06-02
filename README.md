# 🌦️ MeteoApp — Estación Meteorológica Digital con Python

> **¿Qué es esto?** Una aplicación de escritorio que se conecta a internet para traer datos reales del clima y mostrarlos de forma visual. Piensa en ella como una estación meteorológica digital: en vez de leer sensores físicos, lee los datos que ya contiene una página (la API de Open-Meteo) que miden temperatura, humedad, viento y lluvia en cualquier ciudad del mundo.

---

## 🎯 ¿Para qué sirve?

| Puedo hacer… | ¿Cómo lo hace la app? |
|---|---|
| 🔍 **Buscar el clima actual** de cualquier ciudad | Escribe el nombre → la app pregunta a Open-Meteo → muestra temperatura, sensación térmica, humedad, viento y un ícono del clima |
| ❄️🔥 **Cambiar entre °C y °F, km/h y mph** | Un botón toggle convierte al instante todos los valores sin volver a consultar la API |
| 📊 **Ver gráficas de historial** | Elige ciudad + fecha + días → la app descarga datos históricos en ese rango de tiempo → genera gráficas de temperatura y lluvia con matplotlib |
| ⭐ **Guardar ciudades favoritas** | Las ciudades se guardan en un CSV local para acceso rápido |
| 🔔 **Configurar alertas de temperatura** | Define umbrales máximos y mínimos → si la temperatura actual los supera, aparece un banner de alerta |
| 📡 **Funcionar sin internet** (modo offline) | Si la API no responde, la app muestra el último clima consultado desde caché local |
| 🔐 **Iniciar sesión** | Usuarios y contraseñas guardados localmente con hash SHA-256 |

---

## 🧰 Librerías y qué hace cada una

No necesitas instalar nada a mano — el archivo `requirements.txt` se encarga. Pero es importante que entiendas **para qué sirve cada librería**:

| Librería | ¿Qué es? | Rol en la app |
|---|---|---|
| **Flet** `v0.28.3` | Creador de interfaces gráficas con Python | Dibuja los botones, tarjetas, gráficas, diálogos y todo lo que ves en pantalla |
| **Requests** | Mensajero HTTP — va a internet y trae datos | Hace las consultas a la API de Open-Meteo (clima actual, geocodificación, historial) |
| **Pandas** | Manejador de tablas de datos | Lee y escribe los archivos CSV (usuarios, ciudades, historial, caché) y procesa los datos de la API |
| **Matplotlib** | Generador de gráficas científicas | Crea las gráficas de temperatura (líneas) y precipitación (barras) que se ven en el historial |
| **Pillow** | Procesador de imágenes | Dibuja los íconos del clima (sol, nubes, lluvia…) como imágenes PNG en memoria |

### 🌐 ¿Qué es la API de Open-Meteo?

**Open-Meteo** es un servicio gratuito que entrega datos meteorológicos en formato JSON a través de internet. La app usa **tres endpoints** (direcciones URL):

| Endpoint | ¿Qué devuelve? | ¿Cuándo se usa? |
|---|---|---|
| **Geocodificación** | Coordenadas (lat/lon) de una ciudad | Cuando escribes "Bogotá" y la app necesita saber dónde está |
| **Pronóstico** | Clima actual + pronóstico del día | Cuando buscas el clima de una ciudad en la pantalla principal |
| **Archivo histórico** | Datos diarios de días pasados | Cuando consultas el historial de temperatura y lluvia |

> La API es gratuita, no requiere clave, y los datos se actualizan constantemente. Si no hay internet, la app usa los datos guardados en caché.

---

## 🚀 Instalación y ejecución

```bash
# 1. Clonar el repositorio
git clone https://github.com/valenRS/interfaz_grafica_flet.git
cd interfaz_grafica_flet

# 2. Crear y activar entorno virtual
python3 -m venv .venv
source .venv/bin/activate      # Linux/Mac
# .venv\Scripts\activate       # Windows

# 3. Instalar dependencias
python -m pip install --upgrade pip
pip install -r requirements.txt

# 4. Ejecutar la aplicación
python main.py
```

> **Requisito:** Python 3.10 o superior. La versión de Flet está fijada en `0.28.3` para evitar cambios incompatibles.

---

## 🏗️ Estructura del proyecto

```
interfaz_grafica_flet/
├── main.py                          ← Punto de entrada y navegación
├── requirements.txt                 ← Dependencias
│
├── utils/                           ← Lógica y datos (sin interfaz)
│   ├── api_client.py                ← Habla con la API de Open-Meteo
│   ├── data_manager.py              ← Lee y escribe archivos CSV
│   ├── settings.py                  ← Unidades globales (°C/°F, km/h/mph)
│   └── chart_generator.py           ← Genera gráficas con matplotlib
│
├── views/                           ← Pantallas de la interfaz
│   ├── login_view.py                ← Inicio de sesión y registro
│   ├── home_view.py                 ← Pantalla principal: clima actual
│   ├── history_view.py             ← Historial meteorológico y gráficas
│   ├── cities_view.py               ← Gestión de ciudades favoritas
│   └── alerts_view.py               ← Configuración de alertas
│
├── data/                            ← Datos persistentes (CSV)
│   ├── usuarios.csv                 ← Cuentas de usuario
│   ├── ciudades.csv                 ← Ciudades favoritas + alertas + caché
│   ├── historial_clima.csv          ← Datos históricos descargados
│   └── cache_clima.csv              ← Último clima consultado (offline)
│
└── assets/charts/                   ← Gráficas generadas (PNG)
```

---

## 🔄 Flujo general del programa

¿Cómo viajan los datos desde que el usuario toca un botón hasta que ve el resultado en pantalla? Aquí está el camino completo:

```
┌─────────────────────────────────────────────────────────────────┐
│                          USUARIO                                 │
│                    (Escribe "Bogotá")                           │
└──────────────────────────┬──────────────────────────────────────┘
                           │
                           ▼
┌──────────────────────────────────────────────────────────────────┐
│  1. VISTA (home_view.py)                                        │
│     _al_buscar_ciudad() recibe el nombre                        │
│                     │                                            │
│                     ▼                                            │
│  2. API CLIENT (api_client.py)                                   │
│     buscar_ciudades("Bogotá")                                   │
│         → requests.get(_URL_GEOCODIFICACION)                    │
│         → La API devuelve: [{name, country, latitude, longitude}]│
│                     │                                            │
│                     ▼                                            │
│     obtener_clima_actual_desde_geo(geo)                          │
│         → requests.get(_URL_PRONOSTICO)                          │
│         → La API devuelve JSON con temperature_2m, humidity...  │
│         → Se traduce a español: temperatura, humedad, viento...  │
│                     │                                            │
│                     ▼                                            │
│  3. VISTA (home_view.py)                                        │
│     _mostrar_clima_en_tarjeta(data)                             │
│         → Muestra: ciudad, temperatura, ícono, máxima, mínima... │
│     _verificar_alerta_clima(data)                               │
│         → Si la temp. supera el umbral → muestra banner rojo    │
│                     │                                            │
│                     ▼                                            │
│  4. DATA MANAGER (data_manager.py)                               │
│     guardar_cache_clima(data, username)                          │
│         → Guarda en cache_clima.csv (para modo offline)          │
│     actualizar_clima_ciudad(username, ciudad, data)               │
│         → Guarda en ciudades.csv (si es favorita)               │
└──────────────────────────────────────────────────────────────────┘
```

### Pasos del flujo de historial

```
┌───────────────────────────────────────────────────────────┐
│  USUARIO selecciona: ciudad + fecha inicio + # días       │
└─────────────────────────┬─────────────────────────────────┘
                          │
                          ▼
┌───────────────────────────────────────────────────────────┐
│  1. ¿Hay datos en caché local (historial_clima.csv)?      │
│     obtener_historial_cache(ciudad, inicio, fin)          │
│             │                     │                         │
│          SÍ (≥90%)           NO o insuficiente             │
│             │                     │                         │
│             ▼                     ▼                         │
│     Usa caché local     obtener_historial() → API          │
│                                    │                        │
│                                    ▼                        │
│                        guardar_historial(df) → CSV         │
└─────────────────────────┬───────────────────────────────────┘
                          │
                          ▼
┌───────────────────────────────────────────────────────────┐
│  2. Generar gráficas                                      │
│     chart_temperatura(df, ciudad) → temperatura_xxx.png    │
│     chart_precipitacion(df, ciudad) → precipitacion_xxx.png│
└─────────────────────────┬───────────────────────────────────┘
                          │
                          ▼
┌───────────────────────────────────────────────────────────┐
│  3. Mostrar en pantalla                                   │
│     Gráficas + estadísticas (promedio máx, mín, lluvia)   │
└───────────────────────────────────────────────────────────┘
```

---

## 🔑 Variables físicas que mide la app

La app consulta sensores meteorológicos reales a través de la API. Estas son las variables que mide y de dónde provienen:

| Variable física | Clave en la API de Open-Meteo | Unidad | ¿Dónde se ve en la app? |
|---|---|---|---|
| Temperatura del aire | `temperature_2m` | °C / °F | Pantalla principal, historial |
| Sensación térmica | `apparent_temperature` | °C / °F | Pantalla principal |
| Humedad relativa | `relative_humidity_2m` | % | Pantalla principal |
| Velocidad del viento | `wind_speed_10m` | km/h / mph | Pantalla principal |
| Temperatura máxima diaria | `temperature_2m_max` | °C / °F | Pantalla principal, historial |
| Temperatura mínima diaria | `temperature_2m_min` | °C / °F | Pantalla principal, historial |
| Precipitación acumulada | `precipitation_sum` | mm | Historial (gráfica) |
| Velocidad máxima del viento | `wind_speed_10m_max` | km/h | Historial (CSV) |
| Código del clima | `weathercode` | Código WMO | Ícono en pantalla principal |

> **¿Por qué "2m" y "10m"?** Los estándares meteorológicos mundiales miden la temperatura a 2 metros del suelo (altura de un termómetro) y el viento a 10 metros (altura de una estación meteorológica).

---

## 🔒 Autenticación

- Las contraseñas se guardan como **hash SHA-256** — nunca en texto plano
- Los datos de sesión se pierden al cerrar la app (no hay token persistente)
- Cada usuario tiene sus propias ciudades favoritas

---

## ⚠️ Manejo de errores

La app distingue entre tres tipos de fallas de red:

| Error | Causa | Qué hace la app |
|---|---|---|
| `Timeout` | La API no responde en 10 segundos | Muestra "Sin conexión" y busca en caché local |
| `ConnectionError` | No hay internet | Muestra "Sin conexión" y busca en caché local |
| `HTTPError` | La API respondió con error (404, 500…) | Muestra "Ciudad no encontrada" |
| CSV corrupto | Archivo de datos malformado | Crea un CSV vacío y continúa |

---

## 📐 Unidades de medida

La app permite cambiar entre sistemas de unidades **en tiempo real** (sin volver a consultar la API):

| Magnitud | Unidad por defecto | Unidad alternativa | Fórmula de conversión |
|---|---|---|---|
| Temperatura | °C | °F | `F = C × 9/5 + 32` |
| Velocidad | km/h | mph | `mph = km/h × 0.621371` |

Las preferencias se mantienen en memoria (`settings.py`) mientras la app esté abierta y se reinician al cerrar.

---

## 📁 Datos persistentes

Todos los datos se guardan en archivos CSV dentro de la carpeta `data/`. **No se usa base de datos SQL** — solo pandas leyendo y escribiendo CSVs:

| Archivo | Columnas principales | ¿Para qué? |
|---|---|---|
| `usuarios.csv` | id, username, password_hash, fecha_registro | Cuentas de usuario |
| `ciudades.csv` | id, username, ciudad, lat, lon, alertas, caché clima | Favoritas + alertas + último clima |
| `historial_clima.csv` | id, ciudad, fecha, temp_max, temp_min, precipitación, viento | Caché de datos históricos |
| `cache_clima.csv` | ciudad, temperatura, humedad… | Caché para modo offline |

> Los archivos CSV se crean automáticamente si no existen. El historial se purga automáticamente si tiene más de 365 días.

---

> **Autora:** Valentina Rodriguez Sepulveda — 1125789977