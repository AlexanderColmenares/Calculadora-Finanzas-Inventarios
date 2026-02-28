import pandas as pd
import numpy as np
import sympy as sp

class FinanceEngine:
    def __init__(self):
        self.tasa_bcv = 36.50  # Valor referencial ajustable
        # Configuración simbólica con SymPy para el rigor académico
        self.C, self.m = sp.symbols('C m')
        self.formula_precio = self.C * (1 + self.m)

    def obtener_sensibilidad(self):
        """Calcula dP/dC: cuánto varía el precio ante un cambio en el costo."""
        return sp.diff(self.formula_precio, self.C)

    def procesar_datos(self, db):
        if db.productos.empty or db.insumos.empty or db.recetas.empty:
            return pd.DataFrame()

        # --- LÓGICA DE ÁLGEBRA LINEAL CON NUMPY ---
        # Creamos mapeos para los índices de la matriz
        ins_map = {id_ins: i for i, id_ins in enumerate(db.insumos['id_insumo'])}
        prod_map = {id_prod: j for j, id_prod in enumerate(db.productos['id_producto'])}

        # Matriz de Requerimientos Técnicos A (Insumos x Productos)
        A = np.zeros((len(db.insumos), len(db.productos)))
        for _, row in db.recetas.iterrows():
            if row['id_insumo'] in ins_map and row['id_producto'] in prod_map:
                A[ins_map[row['id_insumo']], prod_map[row['id_producto']]] = row['cantidad_necesaria']

        # Vector de costos unitarios de insumos
        v_costos = db.insumos['costo_usd'].values

        # Cálculo matricial: c = v_costos . A (Suma ponderada de insumos por producto)
        costos_totales = np.dot(v_costos, A)

        # Construcción del DataFrame de salida
        resumen = db.productos.copy()
        resumen['costo_total_usd'] = costos_totales
        resumen['precio_usd'] = resumen['costo_total_usd'] * (1 + resumen['margen_ganancia_esperado'])
        resumen['precio_bs'] = resumen['precio_usd'] * self.tasa_bcv
        
        return resumen
