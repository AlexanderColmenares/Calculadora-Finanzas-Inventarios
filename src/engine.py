import pandas as pd
import numpy as np
import sympy as sp

class FinanceEngine:
    def __init__(self):
        self.tasa_bcv = 420.17
        self.C, self.m = sp.symbols('C m')
        self.formula_utilidad = self.C * self.m

    def procesar_datos(self, db):
        if db.productos.empty or db.insumos.empty: return pd.DataFrame()
        ins_map = {id_ins: i for i, id_ins in enumerate(db.insumos['id_insumo'])}
        prod_map = {id_prod: j for j, id_prod in enumerate(db.productos['id_producto'])}
        A = np.zeros((len(db.insumos), len(db.productos)))
        for _, row in db.recetas.iterrows():
            if row['id_insumo'] in ins_map and row['id_producto'] in prod_map:
                A[ins_map[row['id_insumo']], prod_map[row['id_producto']]] = row['cantidad_necesaria']
        v_costos = db.insumos['costo_usd'].values.astype(float)
        costos_reposicion = np.dot(v_costos, A)
        resumen = db.productos.copy()
        resumen['costo_reposicion_usd'] = costos_reposicion
        resumen['precio_sugerido_bs'] = (resumen['costo_reposicion_usd'] * (1 + resumen['margen_ganancia_esperado'])) * self.tasa_bcv
        return resumen

    def obtener_analisis_financiero(self, p, db):
        m_val = float(p['margen_ganancia_esperado'])
        c_val = float(p['costo_reposicion_usd'])
        sens = float(sp.diff(self.formula_utilidad, self.C).evalf(subs={self.m: m_val}))
        return {
            'utilidad_unitaria_usd': c_val * m_val,
            'margen_real': m_val * 100,
            'punto_equilibrio': int(100 / (c_val * m_val)) if (c_val * m_val) > 0 else 0,
            'sensibilidad': sens
        }

    def obtener_receta_detalle(self, id_prod, db):
        detalles = []
        receta = db.recetas[db.recetas['id_producto'] == id_prod]
        for _, r in receta.iterrows():
            ins = db.insumos[db.insumos['id_insumo'] == r['id_insumo']].iloc[0]
            detalles.append({'nom': ins['nombre'], 'id': ins['id_insumo']})
        return detalles
