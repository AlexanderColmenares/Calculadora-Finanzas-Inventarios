import sympy as sp
import numpy as np

class AnalyticsEngine:
    def __init__(self):
        self.C, self.m, self.T = sp.symbols('C m T')
        self.u_bs = (self.C * self.m) * self.T

    def calcular_metricas_avanzadas(self, historial, p):
        if historial.empty: return None
        
        # 1. Derivada Parcial (Sensibilidad a la Tasa)
        m_val = float(p['margen_ganancia_esperado'])
        c_val = float(p['costo_reposicion_usd'])
        # dU/dT = C * m
        sens_tasa = c_val * m_val
        
        # 2. Puntos Críticos Reales
        max_v = historial.loc[historial['utilidad_usd'].idxmax()]
        min_v = historial.loc[historial['utilidad_usd'].idxmin()]
        
        # 3. Punto de Equilibrio Matemático
        # Se calcula donde la Utilidad Cubre un Costo Fijo Estimado (ej. $100 de gastos operativos)
        gastos_fijos_est = 100.0 
        pe_unidades = gastos_fijos_est / (c_val * m_val) if (c_val * m_val) > 0 else 0

        return {
            'sens_tasa': sens_tasa,
            'max_val': max_v['utilidad_usd'],
            'max_fecha': max_v['fecha'],
            'min_val': min_v['utilidad_usd'],
            'min_fecha': min_v['fecha'],
            'promedio': historial['utilidad_usd'].mean(),
            'total_usd': historial['utilidad_usd'].sum(),
            'pe_unidades': pe_unidades
        }
