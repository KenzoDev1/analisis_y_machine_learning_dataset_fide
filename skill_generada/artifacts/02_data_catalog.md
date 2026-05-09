# Data Catalog — Referencia Completa
> Fuente: https://docs.kedro.org/en/1.3.1.post1/catalog-data/data_catalog/

---

## Anatomía de catalog.yml

```yaml
# conf/base/catalog.yml

nombre_dataset:           # ← identificador único en el proyecto
  type: <tipo.Dataset>    # ← clase del dataset (OBLIGATORIO)
  filepath: <ruta>        # ← ruta al archivo (para la mayoría de tipos)
  load_args:              # ← argumentos para carga (pandas kwargs, etc.)
    key: value
  save_args:              # ← argumentos para guardado
    key: value
  credentials: db_creds  # ← referencia a credentials.yml
  versioned: true         # ← activar versionado automático
  layer: raw              # ← capa de datos (documentación/Viz)
  metadata:               # ← metadatos para Kedro Viz
    kedro-viz:
      layer: raw
      preview_args:
        nrows: 5
```

---

## Tipos de Dataset más Comunes

### Datos Tabulares

```yaml
# CSV
ventas_raw:
  type: pandas.CSVDataset
  filepath: data/01_raw/ventas.csv
  load_args:
    sep: ";"
    encoding: "utf-8"
    parse_dates: ["fecha"]
  save_args:
    index: false

# Parquet (recomendado para datos intermedios — más rápido y tipado)
features_for_ml:
  type: pandas.ParquetDataset
  filepath: data/05_model_input/features_for_ml.parquet

# Excel
reporte_excel:
  type: pandas.ExcelDataset
  filepath: data/01_raw/reporte.xlsx
  load_args:
    sheet_name: "Hoja1"

# SQLite / SQL (tabla completa)
matches:
  type: pandas.SQLTableDataset
  credentials: sqlite_creds
  table_name: Match
  load_args:
    index_col: null

# SQL con query
matches_query:
  type: pandas.SQLQueryDataset
  credentials: sqlite_creds
  sql: "SELECT * FROM Match WHERE season = '2015/2016'"
```

### Modelos y Objetos Python

```yaml
# Modelo scikit-learn serializado
trained_classifier:
  type: pickle.PickleDataset
  filepath: data/06_models/classifier.pkl
  backend: pickle  # o joblib

# Múltiples modelos
model_rf:
  type: pickle.PickleDataset
  filepath: data/06_models/random_forest.pkl
```

### JSON y Métricas

```yaml
# Métricas de clasificación
classification_metrics:
  type: json.JSONDataset
  filepath: data/08_reporting/classification_metrics.json

# Parámetros personalizados
experiment_config:
  type: json.JSONDataset
  filepath: data/08_reporting/experiment_config.json
```

### Imágenes y Figuras

```yaml
# Matplotlib figure
confusion_matrix_plot:
  type: matplotlib.MatplotlibWriter
  filepath: data/08_reporting/confusion_matrix.png
  save_args:
    format: png
    dpi: 150
```

### Datasets en Memoria

Los `MemoryDataset` no se declaran en catalog.yml. Se crean automáticamente cuando un output de un nodo es input de otro sin estar en el catálogo. Útil para datos intermedios que no necesitan persistirse.

---

## Dataset Versioning (Control de Versiones)

```yaml
trained_model:
  type: pickle.PickleDataset
  filepath: data/06_models/model.pkl
  versioned: true   # ← activa versionado
```

Con `versioned: true`, Kedro crea subcarpetas con timestamp automático:
```
data/06_models/model.pkl/
├── 2024-01-15T10.30.00.000Z/
│   └── model.pkl
└── 2024-01-16T08.15.00.000Z/
    └── model.pkl
```

Listar versiones disponibles:
```python
ds = catalog._get_dataset("trained_model")
ds.resolve_load_version()     # versión más reciente
ds.resolve_save_version()     # versión a guardar
```

---

## Dataset Factories (Patrones con Wildcards)

Permiten definir múltiples datasets con una sola entrada usando `{placeholder}`:

```yaml
# Patrón genérico para cualquier CSV en raw
"{dataset_name}#csv":
  type: pandas.CSVDataset
  filepath: data/01_raw/{dataset_name}.csv

# Uso en código:
catalog.load("ventas#csv")    # carga data/01_raw/ventas.csv
catalog.load("clientes#csv")  # carga data/01_raw/clientes.csv
```

Ejemplo avanzado con capas:
```yaml
"{layer}_{name}":
  type: pandas.ParquetDataset
  filepath: data/{layer}/{name}.parquet
  metadata:
    kedro-viz:
      layer: "{layer}"
```

---

## Datasets Particionados

Para datasets muy grandes divididos en múltiples archivos:

```yaml
# Particiones por fecha
ventas_particionadas:
  type: partitions.PartitionedDataset
  path: data/01_raw/ventas/
  dataset: pandas.CSVDataset
  filename_suffix: ".csv"

# Incremental: solo carga archivos nuevos desde la última ejecución
ventas_incremental:
  type: partitions.IncrementalDataset
  path: data/01_raw/ventas_stream/
  dataset: pandas.CSVDataset
  checkpoint:
    type: kedro_datasets.text.TextDataset
    filepath: data/02_intermediate/ventas_checkpoint.txt
```

Uso en nodo:
```python
def process_partitions(partitioned_input: dict[str, Callable]) -> pd.DataFrame:
    """Carga y combina todas las particiones."""
    dfs = []
    for partition_key, load_fn in partitioned_input.items():
        df = load_fn()  # lazy loading
        df["partition"] = partition_key
        dfs.append(df)
    return pd.concat(dfs, ignore_index=True)
```

---

## Credenciales

```yaml
# conf/local/credentials.yml  ← NUNCA commitear
sqlite_creds:
  con: "sqlite:///data/raw/database.sqlite"

postgres_creds:
  con: "postgresql://user:password@localhost:5432/mydb"

s3_creds:
  key: "AKIAIOSFODNN7EXAMPLE"
  secret: "wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY"

api_creds:
  token: "Bearer abc123..."
```

Referencia en catalog.yml:
```yaml
mi_tabla:
  type: pandas.SQLTableDataset
  credentials: postgres_creds
  table_name: clientes
```

---

## Uso Programático del Catálogo

```python
# En notebooks con Kedro
%load_ext kedro.ipython

# Cargar dataset
df = catalog.load("ventas_raw")

# Guardar dataset
catalog.save("features_for_ml", df_features)

# Listar datasets
catalog.list()

# Ver configuración de un dataset
catalog._get_dataset("ventas_raw")

# Crear catálogo desde código (testing/scripts)
from kedro.io import DataCatalog
from kedro_datasets.pandas import CSVDataset

catalog = DataCatalog({
    "ventas": CSVDataset(filepath="data/ventas.csv")
})
```

---

## Lazy Loading

Por defecto Kedro carga los datos solo cuando los necesita. Para deshabilitar:

```yaml
# conf/base/catalog.yml
_default:
  lazy: false   # carga todos los datasets al inicio (no recomendado en producción)

mi_dataset:
  type: pandas.CSVDataset
  filepath: data/01_raw/data.csv
  lazy: true    # carga solo cuando se llama .load()
```

---

## Referencia de Tipos de Dataset por Categoría

| Categoría | Tipo Kedro | Caso de Uso |
|-----------|-----------|------------|
| CSV | `pandas.CSVDataset` | Datos tabulares simples |
| Parquet | `pandas.ParquetDataset` | Intermedios y model_input |
| Excel | `pandas.ExcelDataset` | Reportes de negocio |
| JSON | `json.JSONDataset` | Métricas, configuración |
| Pickle | `pickle.PickleDataset` | Modelos Python, objetos arbitrarios |
| SQL Table | `pandas.SQLTableDataset` | Tablas de BD relacionales |
| SQL Query | `pandas.SQLQueryDataset` | Queries personalizadas |
| Matplotlib | `matplotlib.MatplotlibWriter` | Figuras y gráficas |
| Spark | `spark.SparkDataset` | Big Data con PySpark |
| S3/GCS/Azure | (filepath con protocolo) | Cloud storage |
| Partitioned | `partitions.PartitionedDataset` | Datasets multi-archivo |
| Incremental | `partitions.IncrementalDataset` | Streaming incremental |
| Memory | `MemoryDataset` (automático) | Datos en RAM |
| Text | `text.TextDataset` | Archivos de texto plano |
| Yaml | `yaml.YAMLDataset` | Configuraciones YAML |
