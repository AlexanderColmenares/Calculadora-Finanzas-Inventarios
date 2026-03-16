import sympy as sp
import numpy as np

class AnalyticsEngine:
    def __init__(self):
        # Definimos variables: Costo (C), Margen (m), Tasa (T)
        self.C, self.m, self.T = sp.symbols('C m T')
        # Función de Utilidad en Bolívares: U(C, m, T) = (C * m) * T
        self.u_bs = (self.C * self.m) * self.T

    def calcular_sensibilidad_tasa(self, c_val, m_val):
        """
        Derivada Parcial ∂U/∂T: Mide cuánto varía la utilidad en Bs 
        ante cambios en la tasa del dólar.
        """
        derivada_parcial = sp.diff(self.u_bs, self.T)
        valor = derivada_parcial.evalf(subs={self.C: c_val, self.m: m_val})
        return float(valor)

    def obtener_puntos_criticos(self, ventas_df):
        """Calcula estadísticos para el reporte gráfico."""
        if ventas_df.empty:
            return None
        return {
            'max_venta': ventas_df['utilidad_usd'].max(),
            'min_venta': ventas_df['utilidad_usd'].min(),
            'promedio': ventas_df['utilidad_usd'].mean(),
            'total_ganancia': ventas_df['utilidad_usd'].sum()
        }
