# Importamos las piezas que ya construimos
from src.database import cargar_datos
from src.engine import MotorFinanciero

def ejecutar_sistema():
    print("--- INICIANDO SISTEMA DE GESTIÓN (MVP) ---")
    
    # 1. CARGA: Usamos tu función de database.py
    # Asegúrate de que el nombre del archivo coincida con tu CSV en /data
    ruta_archivo = "data/inventario.csv"
    datos_crudos = cargar_datos(ruta_archivo)
    
    if datos_crudos is not None:
        # 2. CONSTRUCCIÓN: Creamos el objeto Motor y le pasamos el DataFrame
        # Aquí es donde ocurre el __init__ y el self guarda los datos
        motor = MotorFinanciero(datos_crudos)
        
        # 3. PROCESO: El motor ejecuta las 3 funciones base
        print("Calculando costos, ingresos y utilidad...")
        resultado = motor.calcular_funciones_base()
        
        # 4. ANÁLISIS: El motor evalúa la viabilidad (ROI)
        resultado_final = motor.analizar_viabilidad()
        
        # 5. SALIDA: Mostramos los resultados clave por consola
        print("\nRESULTADOS FINANCIEROS:")
        # Solo mostramos las columnas que nos interesan para no saturar la pantalla
        columnas_vista = ['producto', 'costo_total', 'precio_venta', 'utilidad_neta', 'estatus']
        print(resultado_final[columnas_vista])
        
        print("\n--- PROCESO FINALIZADO CON ÉXITO ---")
    else:
        print("No se pudieron cargar los datos. Revisa la ruta del archivo.")

if __name__ == "__main__":
    ejecutar_sistema()

