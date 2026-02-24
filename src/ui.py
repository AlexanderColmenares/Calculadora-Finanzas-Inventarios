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
        # Lista de productos
        tabla = Table(expand=True, box=None, show_header=True)
        tabla.add_column("Producto", style="cyan")
        for i, (_, row) in enumerate(productos.iterrows()):
            estilo = "bold white on blue" if i == indice else ""
            tabla.add_row(row['nombre_prod'], style=estilo)
        self.layout["lista"].update(Panel(tabla, title="[bold]Inventario[/bold]", border_style="blue"))

        # Detalles y Sensibilidad
        p = productos.iloc[indice]
        receta_p = db.recetas.loc[db.recetas['id_producto'] == p['id_producto']]
        if not receta_p.empty:
            ins_id = receta_p['id_insumo'].values[0]
            st = db.insumos.loc[db.insumos['id_insumo'] == ins_id].iloc[0]
            stock_msj = f"Estante: {st['stock_estante']} | Almacén: {st['stock_almacen']}"
            estado = "[bold red]REORDEN[/bold red]" if (st['stock_estante'] + st['stock_almacen']) <= st['punto_reorden'] else "[bold green]OK[/bold green]"
        else:
            stock_msj = "N/A"; estado = "N/A"

        sens = engine.calcular_sensibilidad(p['margen_ganancia_esperado'])
        info = (f"[bold cyan]ÁLGEBRA APLICADA[/bold cyan]\n"
                f"Costo: {p['costo_total_usd']:.2f} $ | Venta: [green]{p['precio_bs']:.2f} Bs[/green]\n"
                f"Sensibilidad: [yellow]{sens:.2f}x[/yellow]\n\n"
                f"[bold magenta]LOGÍSTICA[/bold magenta]\n{stock_msj}\nEstado: {estado}")
        
        self.layout["detalle"].update(Panel(info, title=f"[bold]{p['nombre_prod']}[/bold]", border_style="green"))
        self.layout["header"].update(Panel(f"SISTEMA MATRICIAL | Tasa: {tasa} Bs/$", style="bold white on blue"))
        self.layout["footer"].update(Panel("Flechas: Navegar | M: Margen | Q: Salir", style="bold white"))
        self.console.clear()
        self.console.print(self.layout)
