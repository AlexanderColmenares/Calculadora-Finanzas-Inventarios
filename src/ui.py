from rich.layout import Layout
from rich.panel import Panel
from rich.table import Table
from rich.console import Console

class UserInterface:
    def __init__(self):
        self.console = Console()
        self.layout = Layout()
        self.layout.split_column(
            Layout(name="header", size=3),
            Layout(name="body", ratio=1),
            Layout(name="footer", size=3)
        )
        self.layout["body"].split_row(
            Layout(name="lista", ratio=1),
            Layout(name="detalle", ratio=2)
        )

    def refrescar(self, tasa, productos, indice, db, engine):
        # 1. Tabla de Selección
        tabla = Table(expand=True, box=None, show_header=True)
        tabla.add_column("Producto", style="cyan")
        
        for i, (_, row) in enumerate(productos.iterrows()):
            # Usamos 'nombre' que es como está en tu productos.csv
            nombre_display = row['nombre']
            estilo = "bold white on blue" if i == indice else ""
            tabla.add_row(nombre_display, style=estilo)
        
        self.layout["lista"].update(Panel(tabla, title="[bold]Catálogo[/bold]", border_style="blue"))

        # 2. Análisis de Insumos y Sensibilidad
        p = productos.iloc[indice]
        receta_p = db.recetas.loc[db.recetas['id_producto'] == p['id_producto']]
        
        detalles_stock = ""
        alerta_critica = False
        
        for _, r in receta_p.iterrows():
            ins = db.insumos.loc[db.insumos['id_insumo'] == r['id_insumo']].iloc[0]
            total = ins['stock_estante'] + ins['stock_almacen']
            color = "red" if total <= ins['punto_reorden'] else "green"
            if total <= ins['punto_reorden']: alerta_critica = True
            
            detalles_stock += f"• {ins['nombre']}: Estante({ins['stock_estante']}) Almacén({ins['stock_almacen']}) [{color}]Total:{total}[/{color}]\n"

        # Cálculo de sensibilidad con SymPy
        derivada = engine.obtener_sensibilidad()
        sens_val = derivada.subs(engine.m, p['margen_ganancia_esperado'])

        info = (f"[bold cyan]DATOS ECONÓMICOS[/bold cyan]\n"
                f"Costo Total: {p['costo_total_usd']:.2f} $ | Venta: [green]{p['precio_bs']:.2f} Bs[/green]\n"
                f"Sensibilidad (SymPy): [yellow]{float(sens_val):.2f}[/yellow]\n\n"
                f"[bold magenta]ESTADO DE INVENTARIO[/bold magenta]\n{detalles_stock}")
        
        borde_color = "red" if alerta_critica else "green"
        self.layout["detalle"].update(Panel(info, title=f"[bold]{p['nombre']}[/bold]", border_style=borde_color))
        self.layout["header"].update(Panel(f"PROYECTO ÁLGEBRA LINEAL | Tasa: {tasa} Bs/$", style="bold white on blue"))
        self.layout["footer"].update(Panel("V: Vender | R: Reponer | T: Cambiar Tasa | Q: Salir", style="bold white"))
        
        self.console.clear()
        self.console.print(self.layout)
