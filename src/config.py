import os

# Rutas de datos
DATA_DIR = "data"
FILES = {
    'insumos': os.path.join(DATA_DIR, 'insumos.csv'),
    'productos': os.path.join(DATA_DIR, 'productos.csv'),
    'recetas': os.path.join(DATA_DIR, 'recetas.csv'),
    'ventas': os.path.join(DATA_DIR, 'ventas.csv')
}

# Estándares de Ingeniería
ID_PREFIX_PROD = "PROD-"
ID_PREFIX_INS = "INS-"
