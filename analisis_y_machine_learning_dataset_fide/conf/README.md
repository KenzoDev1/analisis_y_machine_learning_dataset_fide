# What is this for?

This folder should be used to store configuration files used by Kedro or by separate tools.

This file can be used to provide users with instructions for how to reproduce local configuration with their own credentials. You can edit the file however you like, but you may wish to retain the information below and add your own section in the [Instructions](#Instructions) section.

## Local configuration

The `local` folder should be used for configuration that is either user-specific (e.g. IDE configuration) or protected (e.g. security keys).

> *Note:* Please do not check in any local configuration to version control.

## Base configuration

The `base` folder is for shared configuration, such as non-sensitive and project-related configuration that may be shared across team members.

WARNING: Please do not put access credentials in the base configuration folder.

## Instrucciones (proyecto — docencia)

- **`base/parameters.yml`**: partición train/test, nombres de columnas y targets
  para clasificación y regresión. Es el lugar habitual para *ejercicios guiados*
  (cambiar `test_size`, probar otras columnas de cuotas) sin editar los nodos.
- **`base/catalog.yml`**: nombres de datasets Kedro, rutas a Parquet/JSON/CSV
  y conexión SQLite. Ver comentarios al inicio de cada bloque.
- **Hiperparámetros de scikit-learn** (por ejemplo `n_neighbors`, `C`,
  `n_estimators`): en este repositorio están en el código Python de
  `ml_classification/nodes.py` y `ml_regression/nodes.py` para que la lectura
  del algoritmo y sus números vaya junta; se pueden externalizar a YAML si el
  curso lo pide.
- **No** versionar en Git credenciales ni `conf/local` con secretos; usar
  `local/` solo en máquina personal si hace falta.

Guías del curso: [docs/GUIA_ESTUDIANTES.md](../docs/GUIA_ESTUDIANTES.md) y
[docs/guias/modelos_y_flujo_integrado.md](../docs/guias/modelos_y_flujo_integrado.md).




## Need help?

[Find out more about configuration from the Kedro documentation](https://docs.kedro.org/en/stable/configure/configuration_basics/#configuration).
