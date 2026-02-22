import pandas as pd
import os

class Database:
    def __init__(self):
        self.path = "data/"
        # Inicializamos con DataFrames vacíos en lugar de None
        # para que el editor no se confunda
        self.insumos = pd.DataFrame()
        self.productos = pd.DataFrame()
        self.recetas = pd.DataFrame()

    def cargar_datos(self):
        try:
            # Agregamos la barra / entre la ruta y el nombre del archivo
            self.insumos = pd.read_csv(f"{self.path}insumos.csv")
            self.productos = pd.read_csv(f"{self.path}productos.csv")
            self.recetas = pd.read_csv(f"{self.path}recetas.csv")
            return True, "Sincronización exitosa."
        except Exception as e:
            return False, f"Error al cargar: {str(e)}"

    def guardar_insumos(self):
        # Ahora el editor sabrá que self.insumos es un DataFrame
        if not self.insumos.empty:
            self.insumos.to_csv(f"{self.path}insumos.csv", index=False)
            return True
        return False
