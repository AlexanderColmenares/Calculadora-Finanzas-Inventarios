import os, sys, tty, termios
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
        fd = sys.stdin.fileno(); old = termios.tcgetattr(fd)
        try:
            tty.setraw(fd); return sys.stdin.read(1).lower()
        finally:
            termios.tcsetattr(fd, termios.TCSADRAIN, old)

    def ejecutar(self):
        while True:
            df = self.engine.procesar_datos(self.db)
            if df.empty: break
            
            self.ui.refrescar(self.engine.tasa_bcv, df, self.indice, self.db, self.engine)
            k = self.get_key()

            if k == 'q': break
            elif k == '\x1b': # Flechas de dirección
                sys.stdin.read(1); key = sys.stdin.read(1)
                if key == 'A' and self.indice > 0: self.indice -= 1
                elif key == 'B' and self.indice < len(df) - 1: self.indice += 1
            
            elif k == 't': # Actualizar Tasa Cambiaria
                os.system('clear')
                try:
                    nueva_tasa = float(input("Ingrese nueva tasa Bs/$ (Ej: 36.5): "))
                    self.engine.tasa_bcv = nueva_tasa
                except: pass
            
            elif k == 'v': # VENTA: Descuenta de estante según la receta completa
                p_id = df.iloc[self.indice]['id_producto']
                receta = self.db.recetas[self.db.recetas['id_producto'] == p_id]
                for _, r in receta.iterrows():
                    self.db.insumos.loc[self.db.insumos['id_insumo'] == r['id_insumo'], 'stock_estante'] -= r['cantidad_necesaria']
                self.db.guardar_insumos()

            elif k == 'r': # REPONER: Mueve de Almacén a Estante
                p_id = df.iloc[self.indice]['id_producto']
                receta = self.db.recetas[self.db.recetas['id_producto'] == p_id]
                for _, r in receta.iterrows():
                    ins_id = r['id_insumo']
                    cant = r['cantidad_necesaria']
                    # Verificamos disponibilidad en almacén
                    idx = self.db.insumos[self.db.insumos['id_insumo'] == ins_id].index[0]
                    if self.db.insumos.at[idx, 'stock_almacen'] >= cant:
                        self.db.insumos.at[idx, 'stock_almacen'] -= cant
                        self.db.insumos.at[idx, 'stock_estante'] += cant
                self.db.guardar_insumos()

if __name__ == "__main__":
    SistemaGestion().ejecutar()
