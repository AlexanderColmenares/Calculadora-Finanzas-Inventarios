import os
import sys
import tty
import termios
from database import Database
from engine import FinanceEngine
from ui import UserInterface

class SistemaGestion:
    def __init__(self):
        self.db = Database()
        self.engine = FinanceEngine()
        self.ui = UserInterface()
        self.db.cargar_datos()
        self.indice = 0

    def get_key(self):
        fd = sys.stdin.fileno()
        old_settings = termios.tcgetattr(fd)
        try:
            tty.setraw(sys.stdin.fileno())
            return sys.stdin.read(1).lower()
        finally:
            termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)

    def ejecutar(self):
        while True:
            df = self.engine.procesar_datos(self.db)
            if df.empty:
                print("Error: No hay datos en data/"); break

            self.ui.refrescar(self.engine.tasa_bcv, df, self.indice, self.db, self.engine)
            tecla = self.get_key()

            if tecla == 'q':
                break
            elif tecla == '\x1b': # Flechas
                sys.stdin.read(1)
                key = sys.stdin.read(1)
                if key == 'A' and self.indice > 0: self.indice -= 1
                elif key == 'B' and self.indice < len(df) - 1: self.indice += 1
            elif tecla == 'm':
                os.system('clear')
                p_id = df.iloc[self.indice]['id_producto']
                nuevo = input(f"Nuevo margen (Ej: 0.3): ")
                try:
                    self.db.productos.loc[self.db.productos['id_producto'] == p_id, 'margen_ganancia_esperado'] = float(nuevo)
                    self.db.productos.to_csv('data/productos.csv', index=False)
                except: pass

if __name__ == "__main__":
    SistemaGestion().ejecutar()
