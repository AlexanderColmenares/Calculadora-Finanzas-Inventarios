from numpy import inexact
from pandas.core.frame import find_common_type
from src.database import cargar_datos
#1
# importamos la función que creamos en el otro archivo o modulo
#importamos solo la funció  n
def test_conexion():
    print("--- INICIANDO PRUEBA DE CONEXIÓN---")
#2
# Llamaos a la función y guardamos el resultado en 'df'
 #ahora le damos argumentos pues ya se modifico
    ruta_archivo = "data/inventario.csv"
    df = cargar_datos(ruta_archivo)

#3
#Verificamos si la carga fue exitosa
    if df is not None:
        print("---¡EXITO! Python encontró y leyo el archivo CSV.---")
        print("\nAqui los datos de tu inventario:\n---------------------------------------------------------------------------------")

        print(df) #Esto imprime la tabla de inventario

        print("---------------------------------------------------------------------------------------")
        print(f"Productos encontrados {len(df)}")         
       
        



        
    else:
         print("ERROR: No se pudieron  cargar datos.")
         print("Revisa que el archivo 'data/inexact.csv' exista y este bien escrito.")
#4
# Ejecutamos prueba de CONEXIÓN
if __name__ == "__main__":
    test_conexion() 
