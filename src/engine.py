import numpy as np
import pandas as pd
from sympy import symbols, diff

class FinanceEngine:
    def __init__(self):
        self.tasa_bcv = 1.0  # Valor por defecto

    def procesar_inventario(self, db):
        """
        Calcula costos y precios usando la lógica de matrices.
        """
        # Obtenemos los datos desde el objeto database
        df_insumos = db.insumos
        df_productos = db.productos
        df_recetas = db.recetas

        # 1. Calculamos el costo de producción por producto
        # Combinamos recetas con costos de insumos
        df_unido = df_recetas.merge(df_insumos[['id_insumo', 'costo_usd']], on='id_insumo')
        df_unido['costo_parcial'] = df_unido['cantidad_necesaria'] * df_unido['costo_usd']
        
        # Agrupamos para tener el costo total por producto final
        costos_finales = df_unido.groupby('id_producto')['costo_parcial'].sum().reset_index()
        costos_finales.columns = ['id_producto', 'costo_total_usd']

        # 2. Unimos con la tabla de productos para calcular precio de venta
        resultado = df_productos.merge(costos_finales, on='id_producto')
        
        # Fórmula: Precio = Costo / (1 - Margen)
        resultado['precio_venta_usd'] = resultado['costo_total_usd'] / (1 - resultado['margen_ganancia_esperado'])
        
        # 3. Conversión a Bolívares según la tasa
        resultado['precio_bs'] = resultado['precio_venta_usd'] * self.tasa_bcv
        
        return resultado
