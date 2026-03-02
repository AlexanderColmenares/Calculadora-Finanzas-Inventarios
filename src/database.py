import pandas as pd
import os

class Database:
    def __init__(self):
        self.path = "data"
        self.insumos = pd.DataFrame()
        self.productos = pd.DataFrame()
        self.recetas = pd.DataFrame()
        self.ventas = pd.DataFrame()
        
        if not os.path.exists(self.path):
            os.makedirs(self.path)
        self.cargar_datos()

    def cargar_datos(self):
        archivos = {
            'insumos': ['id_insumo', 'nombre', 'costo_usd', 'stock_almacen', 'stock_estante', 'punto_reorden'],
            'productos': ['id_producto', 'nombre', 'categoria', 'margen_ganancia_esperado', 'tipo'],
            'recetas': ['id_producto', 'id_insumo', 'cantidad_necesaria'],
            'ventas': ['fecha', 'id_producto', 'cantidad', 'precio_bs_dia', 'tasa_dia', 'utilidad_usd']
        }
        for nombre, columnas in archivos.items():
            file_path = os.path.join(self.path, f"{nombre}.csv")
            if os.path.exists(file_path):
                setattr(self, nombre, pd.read_csv(file_path))
            else:
                setattr(self, nombre, pd.DataFrame(columns=columnas))

    def guardar_todo(self):
        self.insumos.to_csv(os.path.join(self.path, "insumos.csv"), index=False)
        self.productos.to_csv(os.path.join(self.path, "productos.csv"), index=False)
        self.recetas.to_csv(os.path.join(self.path, "recetas.csv"), index=False)
        self.ventas.to_csv(os.path.join(self.path, "ventas.csv"), index=False)
