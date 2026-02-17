import pandas as pd

class MotorFinanciero:
    def __init__(self, dataframe):
        # self es la referencia al objeto mismo para almacenar los datos
        self.df = dataframe

    def calcular_funciones_base(self):
        # 1. Función de Costo Total (Suma de egresos directos)
        self.df['costo_total'] = self.df['costo_base'] + self.df['costos_produccion'] + self.df['logistica']
        
        # 2. Función de Ingreso (Precio de venta según el margen)
        # El precio de venta es Costo Total multiplicado por (1 + margen)
        self.df['precio_venta'] = self.df['costo_total'] * (1 + self.df['margen'])
        
        # 3. Función de Utilidad (Ganancia neta por unidad vendida)
        self.df['utilidad_neta'] = self.df['precio_venta'] - self.df['costo_total']
        
        return self.df

    def analizar_viabilidad(self):
        # Calculamos el ROI (Retorno de Inversión) para determinar si es negocio
        # ROI = (Utilidad / Costo) * 100
        self.df['roi'] = (self.df['utilidad_neta'] / self.df['costo_total']) * 100
        
        # Generamos un estatus basado en el ROI
        def categorizar(valor):
            if valor < 10: return "INVIABLE"
            if valor < 20: return "RIESGO"
            return "VIABLE"
            
        self.df['estatus'] = self.df['roi'].apply(categorizar)
        return self.df
