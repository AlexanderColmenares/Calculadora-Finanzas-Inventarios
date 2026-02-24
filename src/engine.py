import pandas as pd
import numpy as np

class FinanceEngine:
    def __init__(self):
        self.tasa_bcv = 300.17

    def calcular_sensibilidad(self, margen):
        """Derivada parcial dP/dC = (1 + m)"""
        return 1.0 + float(margen)

    def procesar_datos(self, db):
        """
        Calcula costos usando el modelo matricial.
        Operación: C = A.T * Vc (Producto punto de transpuesta por costos)
        """
        if db.productos.empty or db.insumos.empty or db.recetas.empty:
            return pd.DataFrame()

        # 1. Mapeo de índices
        ins_ids = db.insumos['id_insumo'].tolist()
        prod_ids = db.productos['id_producto'].tolist()
        ins_idx = {id_ins: i for i, id_ins in enumerate(ins_ids)}
        prod_idx = {id_prod: j for j, id_prod in enumerate(prod_ids)}

        # 2. Matriz de Coeficientes Técnicos (A)
        A = np.zeros((len(ins_ids), len(prod_ids)))
        for _, row in db.recetas.iterrows():
            if row['id_insumo'] in ins_idx and row['id_producto'] in prod_idx:
                A[ins_idx[row['id_insumo']], prod_idx[row['id_producto']]] = row['cantidad_necesaria']

        # 3. Vector de Costos (Vc)
        vc = db.insumos['costo_usd'].values

        # 4. Cálculo Matricial
        costos_array = np.dot(A.T, vc)

        # 5. DataFrame de salida
        resumen = db.productos.copy()
        resumen['costo_total_usd'] = costos_array
        resumen['precio_usd'] = resumen['costo_total_usd'] * (1 + resumen['margen_ganancia_esperado'])
        resumen['precio_bs'] = resumen['precio_usd'] * self.tasa_bcv
        resumen['nombre_prod'] = resumen['nombre']
        
        return resumen
