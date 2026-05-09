# Proyecto Kedro de Ajedrez FIDE

## 📁 Visión general
Este repositorio contiene un proyecto **Kedro** para analizar el dataset de ajedrez **FIDE**. El pipeline abarca:
- Ingesta de datos
- Limpieza de datos (límites previamente hardcodeados externalizados a `conf/base/parameters.yml`)
- Transformación de datos y **feature engineering**
- Pipelines opcionales de machine learning (entrenamiento, evaluación, etc.)

El proyecto sigue la rúbrica SCY1101, con **Indicador 4** (sin valores hardcodeados) y **Indicador 5** (transformación parametrizada) ya implementados.

---

## 🛠️ Requisitos previos
- **Windows 10/11** con **WSL 2** instalado (preferiblemente Ubuntu/Debian)
- **Python 3.12** (el entorno virtual utiliza esta versión)
- **Git** (para clonar el repositorio si aún no lo tienes)

> El repositorio ya incluye un entorno virtual pre‑creado en `.venv`. Si prefieres crear uno nuevo, sigue los pasos opcionales más abajo.

---

## 🚀 Inicio rápido (WSL 2)
Abre tu terminal WSL y ejecuta los siguientes comandos:

```bash
# 1️⃣ Navegar al directorio raíz del proyecto (ajusta la ruta si tu clon está en otro sitio)
cd /mnt/c/Users/Magol/Desktop/evaluacion-2-ciencia-de-datos/analisis_y_machine_learning_dataset_fide

# 2️⃣ IMPORTANTE: Activar Python 3.12 con pyenv (paso obligatorio)
#    Esto le dice a pyenv qué versión usar en este directorio
pyenv local 3.12.13

# 3️⃣ Verificar que pip ya funciona
pip --version

# 4️⃣ Activar el entorno virtual del proyecto
source .venv/bin/activate

# 5️⃣ Re‑instalar el proyecto en modo editable (necesario la primera vez o tras cambios en el código)
pip install -e .

# 6️⃣ Listar los pipelines registrados (comprobación rápida)
kedro registry list

# 7️⃣ Ejecutar todo el pipeline (ingesta → limpieza → transformación)
kedro run
```

> **¿Por qué el paso 2️⃣?**  
> El sistema utiliza **pyenv** para gestionar múltiples versiones de Python.  
> Si no se fija la versión, WSL no sabe qué `pip` o `python` usar y devuelve `command not found`.  
> `pyenv local 3.12.13` crea un archivo `.python-version` en el directorio que se lee automáticamente en adelante.

### Ejecutar solo un pipeline
```bash
# Por ejemplo, solo la limpieza de datos
kedro run --pipeline data_cleaning
```

---

## 🎨 Visualizar el pipeline con Kedro Viz
```bash
# Lanzar el visualizador (puerto 4141 por defecto)
kedro viz run
```
Abre un navegador en Windows y visita **`http://localhost:4141`**. Verás un grafo (DAG) con todos los pipelines registrados.

*Si el puerto 4141 está ocupado:* `kedro viz run --port 5000` (o cualquier puerto libre) y abre `http://localhost:<puerto>`.

---

## ⚙️ Configuración – Parámetros
Todas las constantes antes hardcodeadas ahora están en:
```
conf/base/parameters.yml
```
Secciones clave:
```yaml
cleaning:
  iqr_factor: 1.5          # Factor IQR para detección de outliers en rating_standard
  min_yob: 1900            # Año de nacimiento mínimo aceptable
  max_yob: 2015            # Año de nacimiento máximo aceptable

transform:
  expert_threshold: 2000   # Corte ELO para clasificar como "experto"
  base_year: 2021          # Año de referencia para cálculo de edad aproximada
```
Modifica este archivo para ajustar el pipeline sin tocar el código.

---

## 📦 Instalación de dependencias (si necesitas un entorno nuevo)
```bash
# Primero, asegúrate de tener la versión correcta de Python activa con pyenv
pyenv local 3.12.13

# Crear un nuevo entorno virtual
python -m venv .venv
source .venv/bin/activate

# Instalar los paquetes requeridos
pip install -r requirements.txt
```
El archivo `requirements.txt` ya fija `kedro~=1.3.1` y `kedro‑viz==12.3.0`, entre otras dependencias.

---

## 🧪 Pruebas y desarrollo
- **Ejecutar pruebas unitarias** (si existen): `kedro test`
- **Generar notebooks Jupyter**: `kedro notebook`
- **Añadir nuevos nodos/pipelines** – sigue la documentación de Kedro y regístralos en `src/analisis_fide_chess/pipeline_registry.py`.

---

## 📚 Comandos útiles de Kedro
| Comando | Descripción |
|---|---|
| `kedro run` | Ejecuta el pipeline por defecto (todos los pasos en orden) |
| `kedro run --pipeline <nombre>` | Ejecuta un pipeline específico |
| `kedro viz run` | Inicia el servidor interactivo de visualización |
| `kedro catalog list` | Muestra los datasets registrados en el catálogo |
| `kedro notebook` | Lanza un notebook Jupyter con el contexto de Kedro cargado |
| `kedro test` | Ejecuta la suite de pruebas del proyecto |

---

## 🔧 Solución de problemas comunes

| Error | Causa | Solución |
|---|---|---|
| `pip: command not found` | pyenv no tiene una versión de Python activa | Ejecuta `pyenv local 3.12.13` primero |
| `kedro: command not found` | El entorno virtual no está activado | Ejecuta `source .venv/bin/activate` |
| `pyenv: command not found` | pyenv no está instalado | Instálalo con `curl https://pyenv.run \| bash` y recarga la shell |
| `ModuleNotFoundError` al ejecutar kedro | Paquetes no instalados en el venv | Ejecuta `pip install -e .` con el venv activo |
| Kedro Viz no abre en el navegador | El puerto está bloqueado o mal redirigido | Abre manualmente `http://localhost:4141` desde Windows |

---

## 🙋‍♀️ Soporte
Si encuentras problemas:
1. Verifica que estés dentro del entorno WSL y que el entorno virtual esté activo (`pyenv local 3.12.13` → `source .venv/bin/activate`).
2. Revisa los logs que imprime Kedro; suelen indicar archivos faltantes o errores de esquema.
3. Abre una *issue* en el repositorio o contacta al instructor del curso.

---

*¡Feliz análisis!*
