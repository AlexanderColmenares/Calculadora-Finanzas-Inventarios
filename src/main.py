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

            if self.vista == "inicio":
                if not df.empty:
                    p = df.iloc[self.idx]
                    calc = self.engine.obtener_analisis_completo(p)
                    receta = self.engine.obtener_receta_detalle(p['id_producto'], self.db)
                    layout["izquierda"].update(self.ui.generar_tabla_productos(df, self.idx))
                    layout["derecha"].update(self.ui.panel_analisis(p, calc, receta, self.db))
            elif self.vista == "insumos":
                layout["main"].update(self.ui.generar_vista_insumos(self.db))
            elif self.vista == "historial":
                layout["main"].update(self.ui.generar_vista_historial(self.db))

            layout["footer"].update(Panel("[1] Inicio | [2] Insumos | [3] Historial | [I] +Insumo | [V] Vender | [T] Tasa | [Q] Salir"))
            self.ui.console.print(layout)

            key = self._get_key()
            if key == 'q': break
            elif key == '1': self.vista = "inicio"
            elif key == '2': self.vista = "insumos"
            elif key == '3': self.vista = "historial"
            elif key == 'i': self.crear_insumo()
            elif key == 't': self.cambiar_tasa()
            elif key == 'v' and self.vista == "inicio": self.registrar_venta(df.iloc[self.idx])
            elif key == '\x1b[A' and self.vista == "inicio": self.idx = max(0, self.idx - 1)
            elif key == '\x1b[B' and self.vista == "inicio": self.idx = min(len(df)-1, self.idx + 1)

    def crear_insumo(self):
        os.system('clear')
        try:
            print("--- REGISTRO DE INSUMO ---")
            nom = input("Nombre: ")
            costo = float(input("Costo USD: "))
            stock = int(input("Stock: "))
            id_i = f"INS-{len(self.db.insumos)+1:02d}"
            nuevo = pd.DataFrame([{'id_insumo': id_i, 'nombre': nom, 'costo_usd': costo, 'stock_almacen': stock, 'stock_estante': 0, 'punto_reorden': 5}])
            self.db.insumos = pd.concat([self.db.insumos, nuevo], ignore_index=True)
            self.db.guardar_todo()
            print("✅ Insumo guardado.")
        except: print("❌ Datos erróneos.")
        os.system('sleep 1')

    def registrar_venta(self, p):
        os.system('clear')
        try:
            cant = float(input(f"Cantidad de {p['nombre']}: "))
            utilidad = ((p['precio_bs']/self.engine.tasa_bcv) - p['costo_usd']) * cant
            venta = pd.DataFrame([{'fecha': datetime.now().strftime("%H:%M"), 'id_producto': p['id_producto'], 'cantidad': cant, 'utilidad_usd': utilidad}])
            self.db.ventas = pd.concat([self.db.ventas, venta], ignore_index=True)
            self.db.guardar_todo()
            print("✅ Venta registrada.")
        except: pass
        os.system('sleep 1')

    def cambiar_tasa(self):
        os.system('clear')
        try:
            self.engine.tasa_bcv = float(input("Nueva tasa: "))
        except: pass

if __name__ == "__main__":
    Controller().ejecutar()
