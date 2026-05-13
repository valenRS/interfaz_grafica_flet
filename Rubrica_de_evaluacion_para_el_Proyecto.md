# Rúbrica de Evaluación de Proyecto: Interfaz Gráfica - FLET

## 1. Introducción

El propósito de esta rúbrica es evaluar el desarrollo de una interfaz gráfica de usuario (GUI) que cumpla con principios de diseño, interactividad, modularidad, procesamiento de datos y almacenamiento de información. El proyecto deberá ser implementado en Python utilizando la herramienta FLET, aplicando buenas prácticas de programación estructurada y modular.

## 2. Requisitos y Criterios de Evaluación

### 1. Diseño Visual y Estética General (1.5)

La interfaz debe presentar un diseño atractivo y coherente. Los colores, imágenes, tipografías y formas deben mantener una armonía visual. La disposición de los componentes debe facilitar la interacción y optimizar el uso del espacio disponible. Se evaluará la alineación, espaciado y proporción de los elementos en pantalla. La interfaz debe ser intuitiva, evitando saturación visual.

La aplicación debe proporcionar retroalimentación ante las acciones del usuario, como mensajes de alerta, error o confirmación. También se valoran los indicadores visuales como cambios de color, íconos o cuadros de diálogo que confirmen las acciones.

Se evaluará la implementación funcional de los siguientes elementos:

- Botones de selección: incluir checkboxes y radio buttons.
- Menús desplegables.
- Elementos de fecha y hora.
- Sliders.
- Imágenes
- Colores

Apertura y cierre de ventanas: Configura botones que permitan abrir y cerrar ventanas secundarias para una navegación organizada. Al abrir una nueva ventana las demás deben cerrarse obligatoriamente.

### 2. Almacenamiento de Información (1.0)

La aplicación debe guardar y procesar información utilizando archivos de almacenamiento: CSV, o JSON. Se evaluará el correcto manejo de lectura y escritura de datos, la consistencia de la información y la correcta manipulación mediante la biblioteca pandas u otras funciones nativas de Python. Tenga en cuenta que los datos deben ser almacenados completos y de forma permanente sin que el agregar nueva información elimine la ya existente.

> **Nota:** Tener en cuenta que la interfaz debe tener el almacenamiento de mínimo dos bases de datos.

### 3. Procesamiento de la Información e Implementación de Gráficas (1.0)

La aplicación debe realizar algún tipo de procesamiento de datos (por ejemplo, cálculos, filtros o análisis) y presentar mínimo dos gráficas que representen la información visualmente en la misma interfaz. Las gráficas pueden generarse con librerías como Matplotlib, PyQtGraph o Tkinter Canvas. Se evaluará la coherencia de los datos, la claridad visual y el tipo de gráfico elegido (barras, líneas, pastel, etc.).

> **Nota:** Tener en cuenta que la interfaz debe tener la visualización de mínimo dos gráficas.

### 4. Librerías adicionales (0.5)

Además de Flet y Pandas, utilizar al menos tres librerías adicionales con un propósito específico.

### 5. Requisitos Adicionales y Penalizaciones

El código debe estar estructurado de forma modular y organizada. Cada ventana o módulo de la interfaz debe implementarse en un archivo Python independiente. El archivo principal debe encargarse de inicializar la aplicación y llamar a las interfaces correspondientes. Se deben incluir cabeceras en cada archivo con nombre del autor, descripción y fecha. Se valorará el uso de comentarios, espaciado y buenas prácticas de indentación.

Si el código no es modular y todas las ventanas se encuentran en un mismo archivo, la aplicación se calificará sobre 3.0. Tenga en cuenta lo siguiente:

- El proyecto debe implementarse obligatoriamente utilizando Programación Orientada a Objetos (P.O.O.). Cada ventana debe ser una clase independiente, con sus propios atributos y métodos. Esto garantiza una mejor organización, reutilización y mantenimiento del código.

En caso de que el proyecto no esté desarrollado bajo el paradigma de Programación Orientada a Objetos (P.O.O.), la calificación máxima será de 2.5.

### 6. Manual de usuario (1.0)

Se debe llevar a cabo un documento tipo manual de usuario. En este se debe describir completamente la funcionalidad de la aplicación. Este debe tener las siguientes características:

- Título del Proyecto, autor(es) y fecha de entrega.
- Breve descripción de la aplicación, objetivo y funcionalidad general.
- Librerías utilizadas y tipo de almacenamiento usado.
- Estructura y orden de los códigos: Describir cómo está organizado el proyecto en cuanto a carpetas, clases y módulos.
- Descripción gráfica del funcionamiento paso a paso de la aplicación. Incluir imágenes de la interfaz funcionando.
- Pasos para instalar dependencias y ejecutar el programa.
- Conclusiones y posibles mejoras.

## 3. Entregables

- Carpeta comprimida con todos los archivos del proyecto incluyendo los de almacenamiento (CSV, JSON o TXT).
- Manual de usuario.
