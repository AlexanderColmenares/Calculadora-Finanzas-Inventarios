from database import Database
from engine import FinanceEngine
import pandas as pd

def ejecutar_sistema():
    print("\n--- 🧮 INICIANDO SISTEMA DE GESTIÓN MATRICIAL ---")
    
    # 1. Inicializar componentes
    db = Database()
    engine = FinanceEngine()
    
    # 2. Cargar datos
    exito, mensaje = db.cargar_datos()
    if not exito:
        print(f"❌ {mensaje}")
        return

    # 3. Entrada de parámetros (Manual)
    try:
        print("\n[CONFIGURACIÓN INICIAL]")
        tasa = float(input("👉 Ingrese la tasa del dólar (BCV/Paralelo): "))
        engine.tasa_bcv = tasa
    except ValueError:
        print("❌ Error: Debe ingresar un número válido para la tasa.")
        return

    # 4. Procesamiento
    print("\n[PROCESANDO MATRICES...]")
    try:
        resultado = engine.procesar_inventario(db)
        
        # 5. Mostrar resultados (Vista previa técnica)
        print("\n" + "="*60)
        print(f"{'PRODUCTO':<20} | {'COSTO $':<10} | {'PRECIO $':<10} | {'PRECIO BS':<10}")
        print("-"*60)
        
        for index, row in resultado.iterrows():
            nombre = row['nombre']
            costo = row['costo_total_usd']
            p_usd = row['precio_venta_usd']
            p_bs = row['precio_bs']
            print(f"{nombre:<20} | {costo:>10.2f} | {p_usd:>10.2f} | {p_bs:>10.2f}")
            
        print("="*60)
        print("✅ Cálculo finalizado con éxito.")
        
    except Exception as e:
        print(f"❌ Error en el motor de cálculo: {e}")

if __name__ == "__main__":
    ejecutar_sistema()
