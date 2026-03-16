import os, sys
import pandas as pd
from datetime import datetime
from rich.panel import Panel
from database import Database
from engine import FinanceEngine
from ui import UserInterface
from analytics import AnalyticsEngine
from reports import ReportGenerator

# --- LÓGICA DE PORTABILIDAD DE SISTEMA ---
if os.name == 'nt':
    import msvcrt
else:
    import tty, termios

class Controller:
    def __init__(self):
        self.db = Database()
        self.engine = FinanceEngine()
        self.ui = UserInterface()
        self.idx = 0
        self.vista = "inicio"
        self.analytics = AnalyticsEngine()
        self.reporter = ReportGenerator()

    def _get_key(self):
        """Captura teclado sin interrumpir el flujo, compatible con Windows y Linux."""
        if os.name == 'nt':
            char = msvcrt.getch()
            if char in [b'\x00', b'\xe0']:
                tecla = msvcrt.getch()
                if tecla == b'H': return '\x1b[A' # Arriba
                if tecla == b'P': return '\x1b[B' # Abajo
            try:
                return char.decode('utf-8').lower()
            except:
                return ''
        else:
            fd = sys.stdin.fileno()
            old = termios.tcgetattr(fd)
            try:
                tty.setraw(fd)
                char = sys.stdin.read(1)
                if char == '\x1b':
                    char += sys.stdin.read(2)
                return char
            finally:
                termios.tcsetattr(fd, termios.TCSADRAIN, old)

    def ejecutar(self):
        while True:
            df = self.engine.procesar_datos(self.db)
            # Limpieza profesional para evitar encimamiento en Windows
            self.ui.console.clear()
            
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
            elif key == 'k' and self.vista == "inicio": self.generar_reporte_avanzado(p)
            elif key == '\x1b[A' and self.vista == "inicio": self.idx = max(0, self.idx - 1)
            elif key == '\x1b[B' and self.vista == "inicio": self.idx = min(len(df)-1, self.idx + 1)

    def registrar_venta(self, p):
        self.ui.console.clear()
        print("\n" + "="*40 + "\n   🛒 REGISTRAR VENTA\n" + "="*40)
        try:
            cant = float(input(f"Cantidad de {p['nombre']} vendida: "))
            receta = self.db.recetas[self.db.recetas['id_producto'] == p['id_producto']]
            
            # Verificación de stock
            for _, r in receta.iterrows():
                idx_i = self.db.insumos[self.db.insumos['id_insumo'] == r['id_insumo']].index[0]
                if self.db.insumos.at[idx_i, 'stock_estante'] < (r['cantidad_necesaria'] * cant):
                    print("❌ Error: Stock insuficiente en estante.")
                    self._get_key(); return
            
            # Descontar stock
            for _, r in receta.iterrows():
                idx_i = self.db.insumos[self.db.insumos['id_insumo'] == r['id_insumo']].index[0]
                self.db.insumos.at[idx_i, 'stock_estante'] -= (r['cantidad_necesaria'] * cant)

            utilidad = (p['precio_sugerido_bs']/self.engine.tasa_bcv - p['costo_reposicion_usd']) * cant
            venta = {
                'fecha': datetime.now().strftime("%d/%m %H:%M"), 
                'id_producto': p['id_producto'], 
                'cantidad': cant, 
                'utilidad_usd': utilidad, 
                'costo_en_momento': p['costo_reposicion_usd']
            }
            self.db.ventas = pd.concat([self.db.ventas, pd.DataFrame([venta])], ignore_index=True)
            self.db.guardar_todo()
            print("✅ Venta procesada exitosamente.")
        except Exception as e: 
            print(f"❌ Error en la entrada: {e}")
        print("\nPresione cualquier tecla para continuar...")
        self._get_key()

    def gestionar_reabastecimiento(self):
        self.ui.console.clear()
        print("\n" + "="*40 + "\n   🏗️ GESTIÓN DE STOCK\n" + "="*40)
        print("[1] Comprar Insumo (Almacén) | [2] Surtir Estante (Alm -> Est)")
        opt = input("Seleccione: ")
        try:
            print("\nInsumos:")
            for i, r in self.db.insumos.iterrows(): 
                print(f"[{i}] {r['nombre']} (Alm: {r['stock_almacen']}, Est: {r['stock_estante']})")
            idx = int(input("\nÍndice del insumo: "))
            cant = float(input("Cantidad: "))
            if opt == '1':
                self.db.insumos.at[idx, 'stock_almacen'] += cant
                print("✅ Almacén actualizado.")
            elif opt == '2':
                if self.db.insumos.at[idx, 'stock_almacen'] >= cant:
                    self.db.insumos.at[idx, 'stock_almacen'] -= cant
                    self.db.insumos.at[idx, 'stock_estante'] += cant
                    print("✅ Estante surtido.")
                else: print("❌ Insuficiente en Almacén.")
            self.db.guardar_todo()
        except: print("❌ Error en la operación.")
        print("\nPresione cualquier tecla...")
        self._get_key()

    def modificar_maestro(self):
        self.ui.console.clear()
        print("\n" + "="*40 + "\n   ⚙️ MODIFICAR PARÁMETROS\n" + "="*40)
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
            print("✅ Cambios guardados.")
        except: print("❌ Error al modificar.")
        print("\nPresione cualquier tecla...")
        self._get_key()

    def crear_nuevo(self):
        self.ui.console.clear()
        print("\n" + "="*40 + "\n   🏗️ CREAR NUEVOS REGISTROS\n" + "="*40)
        print("[1] Nuevo Insumo | [2] Nuevo Producto")
        opt = input("Selección: ")
        try:
            if opt == '1':
                nombre = input("Nombre: ")
                costo = float(input("Costo $: "))
                reorden = float(input("Punto Reorden: "))
                nuevo = {'id_insumo': f"INS-0{len(self.db.insumos)+1}", 'nombre': nombre, 'costo_usd': costo, 
                         'stock_almacen': 0, 'stock_estante': 0, 'punto_reorden': reorden}
                self.db.insumos = pd.concat([self.db.insumos, pd.DataFrame([nuevo])], ignore_index=True)
                print("✅ Insumo creado.")
            elif opt == '2':
                nombre_p = input("Nombre del Producto: ")
                categoria = input("Categoría: ")
                margen = float(input("Margen (ej: 0.30): "))
                prod_id = f"PROD-0{len(self.db.productos)+1}"
                
                print("\n--- Definición de Receta ---")
                for i, r in self.db.insumos.iterrows(): print(f"[{i}] {r['nombre']}")
                indices = input("Índices de insumos usados (ej: 0,2): ")
                for idx_str in indices.split(','):
                    idx = int(idx_str.strip())
                    cant_n = float(input(f"Cantidad de {self.db.insumos.at[idx, 'nombre']}: "))
                    nueva_receta = {'id_producto': prod_id, 'id_insumo': self.db.insumos.at[idx, 'id_insumo'], 'cantidad_necesaria': cant_n}
                    self.db.recetas = pd.concat([self.db.recetas, pd.DataFrame([nueva_receta])], ignore_index=True)

                nuevo_p = {'id_producto': prod_id, 'nombre': nombre_p, 'categoria': categoria, 'margen_ganancia_esperado': margen, 'tipo': 'Unitario'}
                self.db.productos = pd.concat([self.db.productos, pd.DataFrame([nuevo_p])], ignore_index=True)
                print("✅ Producto y receta creados.")
            self.db.guardar_todo()
        except Exception as e: print(f"❌ Error: {e}")
        print("\nPresione cualquier tecla...")
        self._get_key()

    def cambiar_tasa(self):
        self.ui.console.clear()
        try: 
            nueva = float(input(f"Tasa actual {self.engine.tasa_bcv} Bs/$. Nueva tasa: "))
            self.engine.tasa_bcv = nueva
            print("✅ Tasa actualizada.")
        except: pass
        print("\nPresione cualquier tecla...")
        self._get_key()

    def generar_reporte_avanzado(self, p):
        # 1. Obtener datos históricos del producto
        historial = self.db.ventas[self.db.ventas['id_producto'] == p['id_producto']]
        if historial.empty:
            print("No hay ventas para este producto aún.")
            return

        # 2. Cálculos de ingeniería
        stats = self.analytics.obtener_puntos_criticos(historial)
        sens_tasa = self.analytics.calcular_sensibilidad_tasa(p['costo_reposicion_usd'], p['margen_ganancia_esperado'])
        
        # 3. Generar PDF
        grafica = self.reporter.crear_grafica_tendencia(historial, p['nombre'])
        pdf = self.reporter.generar_pdf(p['nombre'], stats, {'sens_tasa': sens_tasa}, grafica)
        
        print(f"✅ Reporte generado: {pdf}")
        input("Presione Enter para continuar...")

if __name__ == "__main__":
    Controller().ejecutar()
