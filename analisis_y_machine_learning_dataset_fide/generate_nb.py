import nbformat as nbf

nb = nbf.v4.new_notebook()

code_cells = [
    '''# Carga de Kedro extension
%load_ext kedro.ipython''',
    '''import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns

# Configuración de visualizaciones
sns.set_theme(style='whitegrid')
plt.rcParams['figure.figsize'] = (10, 6)''',
    '''# Cargar datasets desde Kedro Data Catalog
# Estos datasets están definidos en conf/base/catalog.yml
players = catalog.load('fide_players')
ratings_2019 = catalog.load('fide_ratings_2019')
ratings_2020 = catalog.load('fide_ratings_2020')
ratings_2021 = catalog.load('fide_ratings_2021')''',
    '''# 1. Exploración Inicial (Data Ingestion - AD 1.1)
print(f'Players shape: {players.shape}')
display(players.head())
print(players.info())''',
    '''# Revisión de estadísticas descriptivas
display(players.describe(include='all'))''',
    '''# Verificar valores nulos en el dataset de jugadores
null_counts = players.isnull().sum()
print('Valores nulos en Players:')
print(null_counts[null_counts > 0])''',
    '''# Verificar duplicados
duplicates = players.duplicated().sum()
print(f'Duplicados en Players: {duplicates}')''',
    '''# Explorar ratings de 2021
print(f'Ratings 2021 shape: {ratings_2021.shape}')
display(ratings_2021.head())
print(ratings_2021.info())'''
]

nb['cells'] = [nbf.v4.new_markdown_cell('# Evaluación 1 y 2 - Análisis Exploratorio de Datos (EDA)\nEste notebook cubre la Ingestión y Exploración inicial de los datasets FIDE.')] + [nbf.v4.new_code_cell(code) for code in code_cells]

with open('notebooks/01_exploratory_analysis.ipynb', 'w') as f:
    nbf.write(nb, f)

print('Notebook creado exitosamente.')
