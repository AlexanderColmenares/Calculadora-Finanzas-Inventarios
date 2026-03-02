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
        self.vista = "inicio" # inicio, historial, inventario

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
            layout = self.ui.layout_base()
            layout["header"].update(self.ui.generar_header(self.db, self.engine.tasa_bcv))

            if self.vista == "inicio" and not df.empty:
                p = df.iloc[self.idx]
                calc = self.engine.obtener_analisis_completo(p)
                receta = self.engine.obtener_receta_detalle(p['id_producto'], self.db)
                layout["izquierda"].update(self.ui.generar_tabla_productos(df, self.idx))
                layout["derecha"].update(self.ui.panel_analisis(p, calc, receta, self.db))
            
            elif self.vista == "historial":
                layout["main"].update(Panel(str(self.db.ventas.tail(15)), title="HISTORIAL DE VENTAS"))

            layout["footer"].update(Panel("[↑↓] Navegar | [V] Vender | [N] Nuevo | [H] Historial | [T] Tasa | [Q] Salir"))
            self.ui.console.print(layout)

            key = self._get_key()
            if key == 'q': break
            elif key == '\x1b[A': self.idx = max(0, self.idx - 1)
            elif key == '\x1b[B': self.idx = min(len(df)-1, self.idx + 1)
            elif key == 'h': self.vista = "historial" if self.vista != "historial" else "inicio"
            elif key == 't': self.cambiar_tasa()
            elif key == 'n': self.crear_producto()
            elif key == 'v': self.registrar_venta(df.iloc[self.idx])

    def cambiar_tasa(self):
        os.system('clear')
        try:
            nueva = float(input("Ingrese nueva tasa BCV (Bs/$): "))
            self.engine.tasa_bcv = nueva
        except: print("Valor inválido.")

    def crear_producto(self):
        os.system('clear')
        print("--- REGISTRO DE NUEVO PRODUCTO ---")
        try:
            nom = input("Nombre: ")
            margen = float(input("Margen (ej: 0.3 para 30%): "))
            tipo = input("Tipo (Unitario/Combo): ")
            id_p = f"PROD-{len(self.db.productos)+1:02d}"
            
            nueva_fila = pd.DataFrame([{'id_producto': id_p, 'nombre': nom, 'categoria': 'General', 'margen_ganancia_esperado': margen, 'tipo': tipo}])
            self.db.productos = pd.concat([self.db.productos, nueva_fila], ignore_index=True)
            
            print("\nAsignación de Insumos (escriba 'fin' para terminar):")
            while True:
                print(self.db.insumos[['id_insumo', 'nombre']])
                id_i = input("ID del Insumo: ").upper()
                if id_i == 'FIN' or id_i == '': break
                cant = float(input(f"Cantidad de {id_i}: "))
                rec_fila = pd.DataFrame([{'id_producto': id_p, 'id_insumo': id_i, 'cantidad_necesaria': cant}])
                self.db.recetas = pd.concat([self.db.recetas, rec_fila], ignore_index=True)
            
            self.db.guardar_todo()
            print("✅ Guardado con éxito.")
        except Exception as e: print(f"❌ Error: {e}")
        os.system('sleep 2')

    def registrar_venta(self, p):
        os.system('clear')
        try:
            cant = float(input(f"¿Cuántas unidades de {p['nombre']} vendió?: "))
            # Lógica de Descuento de Inventario por Receta
            receta = self.db.recetas[self.db.recetas['id_producto'] == p['id_producto']]
            for _, r in receta.iterrows():
                self.db.insumos.loc[self.db.insumos['id_insumo'] == r['id_insumo'], 'stock_estante'] -= (r['cantidad_necesaria'] * cant)
            
            utilidad = ((p['precio_bs']/self.engine.tasa_bcv) - p['costo_usd']) * cant
            venta = pd.DataFrame([{
                'fecha': datetime.now().strftime("%Y-%m-%d %H:%M"),
                'id_producto': p['id_producto'],
                'cantidad': cant,
                'precio_bs_dia': p['precio_bs'],
                'tasa_dia': self.engine.tasa_bcv,
                'utilidad_usd': utilidad
            }])
            self.db.ventas = pd.concat([self.db.ventas, venta], ignore_index=True)
            self.db.guardar_todo()
            print("✅ Venta y Descuento de Stock procesados.")
        except: print("❌ Error en datos.")
        os.system('sleep 1')

if __name__ == "__main__":
    app = Controller()
    app.ejecutar()
