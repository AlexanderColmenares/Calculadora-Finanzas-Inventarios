import pandas as pd
import numpy as np
import sympy as sp

class FinanceEngine:
    def __init__(self):
        self.tasa_bcv = 36.50  
        self.C, self.m = sp.symbols('C m')
        self.formula_utilidad = self.C * self.m

    def obtener_analisis_completo(self, p):
        try:
            m_val = float(p['margen_ganancia_esperado'])
            c_val = float(p['costo_usd'])
            derivada_f = sp.diff(self.formula_utilidad, self.C)
            # Corrección: Evaluación explícita a float
            sensibilidad = float(derivada_f.evalf(subs={self.m: m_val}))
            return {'utilidad_unitaria': c_val * m_val, 'sensibilidad_utilidad': sensibilidad}
        except:
            return {'utilidad_unitaria': 0.0, 'sensibilidad_utilidad': 0.0}

    def procesar_datos(self, db):
        if db.productos.empty or db.insumos.empty: return pd.DataFrame()
        
        # Producto Punto Matricial para Costos
        ins_map = {id_ins: i for i, id_ins in enumerate(db.insumos['id_insumo'])}
        prod_map = {id_prod: j for j, id_prod in enumerate(db.productos['id_producto'])}
        A = np.zeros((len(db.insumos), len(db.productos)))
        
        for _, row in db.recetas.iterrows():
            if row['id_insumo'] in ins_map and row['id_producto'] in prod_map:
                A[ins_map[row['id_insumo']], prod_map[row['id_producto']]] = row['cantidad_necesaria']
        
        v_costos = db.insumos['costo_usd'].values.astype(float)
        costos_totales = np.dot(v_costos, A)

        resumen = db.productos.copy()
        resumen['costo_usd'] = costos_totales
        resumen['precio_bs'] = (resumen['costo_usd'] * (1 + resumen['margen_ganancia_esperado'])) * self.tasa_bcv
        return resumen

    def obtener_receta_detalle(self, id_prod, db):
        detalles = []
        receta = db.recetas[db.recetas['id_producto'] == id_prod]
        for _, r in receta.iterrows():
            ins = db.insumos[db.insumos['id_insumo'] == r['id_insumo']].iloc[0]
            detalles.append({'nom': ins['nombre'], 'cant': r['cantidad_necesaria'], 'sub': float(r['cantidad_necesaria'] * ins['costo_usd'])})
        return detalles
