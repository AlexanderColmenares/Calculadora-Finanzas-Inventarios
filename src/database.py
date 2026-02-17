import pandas as pd
def cargar_datos(ruta):
    #Esta es la funcion de lectura del csv
   try:
        df = pd.read_csv(ruta)
        return df
   except Exception as e:
        print(f"Error al leer los datos: {e}")
        return None
    
