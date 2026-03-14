import os, sys, tty, termios
import pandas as pd
from datetime import datetime
from rich.panel import Panel
from database import Database
from engine import FinanceEngine
from ui import UserInterface

class Controller:
    def __init__(self):
        self.db = Database()
        self.engine = FinanceEngine()
        self.ui = UserInterface()
        self.idx = 0
        self.vista = "inicio"

    def _get_key(self):
        fd = sys.stdin.fileno(); old = termios.tcgetattr(fd)
        try:
            tty.setraw(fd); char = sys.stdin.read(1)
            if char == '\x1b': char += sys.stdin.read(2)
            return char
        finally: termios.tcsetattr(fd, termios.TCSADRAIN, old)

    def ejecutar(self):
        while True:
            df = self.engine.procesar_datos(self.db)
            os.system('clear')
            layout = self.ui.generar_layout(self.vista)
            layout["header"].update(self.ui.generar_header(self.db, self.engine.tasa_bcv, self.vista))

            if self.vista == "inicio" and not df.empty:
                p = df.iloc[self.idx]
                finanzas = self.engine.obtener_analisis_financiero(p, self.db)
                receta = self.engine.obtener_receta_detalle(p['id_producto'], self.db)
                layout["izq"].update(self.ui.generar_tabla_productos(df, self.idx, self.engine.tasa_bcv))
                layout["der"].update(self.ui.panel_analisis(p, finanzas, receta, self.db))
            elif self.vista == "insumos":
                layout["main"].update(self.ui.generar_vista_insumos(self.db))
            elif self.vista == "historial":
                layout["main"].update(self.ui.generar_vista_historial(self.db))

            layout["footer"].update(Panel("[1] Inicio [2] Insumos [3] Historial | [V] Vender [R] Reabastecer | [M] Modificar [C] Crear [T] Tasa | [Q] Salir"))
            self.ui.console.print(layout)

            key = self._get_key()
            if key == 'q': break
            elif key == '1': self.vista = "inicio"
            elif key == '2': self.vista = "insumos"
            elif key == '3': self.vista = "historial"
            elif key == 'v' and self.vista == "inicio": self.registrar_venta(df.iloc[self.idx])
            elif key == 'r': self.gestionar_reabastecimiento()
            elif key == 'm': self.modificar_maestro()
            elif key == 'c': self.crear_nuevo()
            elif key == 't': self.cambiar_tasa()
            elif key == '\x1b[A' and self.vista == "inicio": self.idx = max(0, self.idx - 1)
            elif key == '\x1b[B' and self.vista == "inicio": self.idx = min(len(df)-1, self.idx + 1)

    def gestionar_reabastecimiento(self):
        os.system('clear')
        print("--- GESTIÓN DE STOCK ---")
        print("[1] Comprar Insumo (Almacén) | [2] Surtir Estante (Alm -> Est)")
        opt = input("Seleccione: ")
        try:
            for i, r in self.db.insumos.iterrows(): print(f"[{i}] {r['nombre']} (Alm: {r['stock_almacen']}, Est: {r['stock_estante']})")
            idx = int(input("Índice: "))
            cant = float(input("Cantidad: "))
            if opt == '1':
                self.db.insumos.at[idx, 'stock_almacen'] += cant
            elif opt == '2':
                if self.db.insumos.at[idx, 'stock_almacen'] >= cant:
                    self.db.insumos.at[idx, 'stock_almacen'] -= cant
                    self.db.insumos.at[idx, 'stock_estante'] += cant
            self.db.guardar_todo()
        except: pass

    def modificar_maestro(self):
        os.system('clear')
        print("--- MODIFICAR PARÁMETROS ---")
        print("[1] Costos Insumos | [2] Márgenes Productos | [3] Punto Reorden")
        opt = input("Selección: ")
        try:
            if opt == '1':
                for i, r in self.db.insumos.iterrows(): print(f"[{i}] {r['nombre']} (${r['costo_usd']})")
                idx = int(input("Índice: ")); self.db.insumos.at[idx, 'costo_usd'] = float(input("Nuevo Costo $: "))
            elif opt == '2':
                for i, r in self.db.productos.iterrows(): print(f"[{i}] {r['nombre']} ({r['margen_ganancia_esperado']*100}%)")
                idx = int(input("Índice: ")); self.db.productos.at[idx, 'margen_ganancia_esperado'] = float(input("Nuevo Margen (ej 0.3): "))
            elif opt == '3':
                for i, r in self.db.insumos.iterrows(): print(f"[{i}] {r['nombre']} (PR: {r['punto_reorden']})")
                idx = int(input("Índice: ")); self.db.insumos.at[idx, 'punto_reorden'] = float(input("Nuevo Punto Reorden: "))
            self.db.guardar_todo()
        except: pass

    def crear_nuevo(self):
        os.system('clear')
        print("--- 🏗️ CREAR NUEVOS REGISTROS ---")
        print("[1] Nuevo Insumo | [2] Nuevo Producto")
        opt = input("Selección: ")
        try:
            if opt == '1':
                nombre = input("Nombre del Insumo: ")
                costo = float(input("Costo unitario ($): "))
                reorden = float(input("Punto de Reorden (mínimo): "))
                nuevo_id = f"INS-0{len(self.db.insumos)+1}"
                nuevo = {
                    'id_insumo': nuevo_id, 
                    'nombre': nombre, 
                    'costo_usd': costo, 
                    'stock_almacen': 0, 
                    'stock_estante': 0, 
                    'punto_reorden': reorden
                }
                self.db.insumos = pd.concat([self.db.insumos, pd.DataFrame([nuevo])], ignore_index=True)
                print(f"✅ Insumo {nuevo_id} creado con éxito.")

            elif opt == '2':
                if self.db.insumos.empty:
                    print("❌ No hay insumos registrados. Cree un insumo primero.")
                    os.system('sleep 2'); return

                nombre_p = input("Nombre del Producto: ")
                categoria = input("Categoría (ej: Alimentos): ")
                margen = float(input("Margen de ganancia (ej: 0.30 para 30%): "))
                tipo = input("Tipo (Unitario/Combo): ")
                
                prod_id = f"PROD-0{len(self.db.productos)+1}"
                
                # Definir Receta (Relación de Insumos)
                print("\n--- Definición de Receta ---")
                for i, r in self.db.insumos.iterrows():
                    print(f"[{i}] {r['nombre']}")
                
                indices = input("Ingrese índices de insumos usados (separados por coma, ej: 0,2): ")
                for idx_str in indices.split(','):
                    idx = int(idx_str.strip())
                    cant_n = float(input(f"Cantidad necesaria de {self.db.insumos.at[idx, 'nombre']}: "))
                    nueva_receta = {
                        'id_producto': prod_id,
                        'id_insumo': self.db.insumos.at[idx, 'id_insumo'],
                        'cantidad_necesaria': cant_n
                    }
                    self.db.recetas = pd.concat([self.db.recetas, pd.DataFrame([nueva_receta])], ignore_index=True)

                # Guardar Producto
                nuevo_p = {
                    'id_producto': prod_id, 
                    'nombre': nombre_p, 
                    'categoria': categoria, 
                    'margen_ganancia_esperado': margen, 
                    'tipo': tipo
                }
                self.db.productos = pd.concat([self.db.productos, pd.DataFrame([nuevo_p])], ignore_index=True)
                print(f"✅ Producto {prod_id} y su receta han sido registrados.")

            self.db.guardar_todo()
        except Exception as e:
            print(f"❌ Error en la creación: {e}")
        
        print("\nPresione cualquier tecla para continuar...")
        self._get_key()

    def registrar_venta(self, p):
        os.system('clear')
        try:
            cant = float(input(f"Cantidad de {p['nombre']} vendida: "))
            receta = self.db.recetas[self.db.recetas['id_producto'] == p['id_producto']]
            for _, r in receta.iterrows():
                idx_i = self.db.insumos[self.db.insumos['id_insumo'] == r['id_insumo']].index[0]
                if self.db.insumos.at[idx_i, 'stock_estante'] < (r['cantidad_necesaria'] * cant):
                    print("❌ Error: Stock insuficiente en estante."); os.system('sleep 2'); return
            
            for _, r in receta.iterrows():
                idx_i = self.db.insumos[self.db.insumos['id_insumo'] == r['id_insumo']].index[0]
                self.db.insumos.at[idx_i, 'stock_estante'] -= (r['cantidad_necesaria'] * cant)

            utilidad = (p['precio_sugerido_bs']/self.engine.tasa_bcv - p['costo_reposicion_usd']) * cant
            venta = {'fecha': datetime.now().strftime("%d/%m %H:%M"), 'id_producto': p['id_producto'], 
                     'cantidad': cant, 'utilidad_usd': utilidad, 'costo_en_momento': p['costo_reposicion_usd']}
            self.db.ventas = pd.concat([self.db.ventas, pd.DataFrame([venta])], ignore_index=True)
            self.db.guardar_todo(); print("✅ Venta procesada.")
        except: pass
        os.system('sleep 1')

    def cambiar_tasa(self):
        os.system('clear')
        try: self.engine.tasa_bcv = float(input(f"Tasa actual {self.engine.tasa_bcv}. Nueva: "))
        except: pass

if __name__ == "__main__":
    Controller().ejecutar()
