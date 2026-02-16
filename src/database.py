import pandas as pd
def cargar_datos():
    #Esta es la funcion de lectura del csv
   try:
        df = pd.read_csv("data/inventario.csv")
        return df
   except Exception as e:
        print(f"Error al leer los datos: {e}")
        return None
