from rich.console import Console
from rich.layout import Layout
from rich.panel import Panel
from rich.table import Table
from rich.columns import Columns
from rich.align import Align

class UserInterface:
    def __init__(self):
        self.console = Console()

    def generar_layout(self, vista="inicio"):
        layout = Layout()
        layout.split_column(
            Layout(name="header", size=3),
            Layout(name="main", ratio=1),
            Layout(name="footer", size=3)
        )
        if vista == "inicio":
            layout["main"].split_row(
                Layout(name="izquierda", ratio=1),
                Layout(name="derecha", ratio=2)
            )
        return layout

    def generar_header(self, db, tasa, vista):
        utilidad = db.ventas['utilidad_usd'].sum() if not db.ventas.empty else 0.0
        return Panel(Align.center(f"MODO: {vista.upper()} | Tasa: {tasa} Bs/$ | Ganancia Total: ${utilidad:.2f}"), style="bold white on blue")

    def generar_tabla_productos(self, df, seleccionado):
        tabla = Table(title="CATÁLOGO DE PRODUCTOS", expand=True, border_style="cyan")
        tabla.add_column("ID", justify="center")
        tabla.add_column("Producto")
        for i, (_, r) in enumerate(df.iterrows()):
            estilo = "bold black on cyan" if i == seleccionado else ""
            tabla.add_row(str(r['id_producto']), r['nombre'], style=estilo)
        return tabla

    def panel_analisis(self, p, calc, receta_detallada, db):
        info_finanzas = (
            f"[bold cyan]ANÁLISIS TÉCNICO[/bold cyan]\n"
            f"• Costo: ${p['costo_usd']:.2f}\n"
            f"• Margen: {p['margen_ganancia_esperado']*100:.1f}%\n"
            f"• Precio: [bold green]{p['precio_bs']:.2f} Bs[/bold green]\n"
            f"• Sensibilidad: [bold yellow]{calc['sensibilidad_utilidad']:.4f}[/bold yellow]"
        )

        t_inv = Table(title="STOCK DE COMPONENTES", border_style="green", expand=True)
        t_inv.add_column("Insumo")
        t_inv.add_column("Stock")
        t_inv.add_column("Status")
        
        for item in receta_detallada:
            ins_data = db.insumos[db.insumos['nombre'] == item['nom']].iloc[0]
            # Alerta dinámica: si el stock es menor al punto de reorden
            alerta = "[bold red]CRÍTICO[/bold red]" if ins_data['stock_almacen'] <= ins_data['punto_reorden'] else "[green]OK[/green]"
            t_inv.add_row(item['nom'], str(ins_data['stock_almacen']), alerta)

        return Panel(Columns([info_finanzas, t_inv]), title=f"FICHA: {p['nombre']}", border_style="yellow")

    def generar_vista_insumos(self, db):
        tabla = Table(title="INVENTARIO DE MATERIA PRIMA", expand=True)
        tabla.add_column("ID"); tabla.add_column("Nombre"); tabla.add_column("Costo $"); tabla.add_column("Stock"); tabla.add_column("Estado")
        for _, r in db.insumos.iterrows():
            status = "[bold red]REORDEN[/bold red]" if r['stock_almacen'] <= r['punto_reorden'] else "[green]ÓPTIMO[/green]"
            tabla.add_row(r['id_insumo'], r['nombre'], f"{r['costo_usd']:.2f}", f"{r['stock_almacen']}", status)
        return Panel(tabla, border_style="green")

    def generar_vista_historial(self, db):
        if db.ventas.empty: return Panel(Align.center("\nNo hay registros."), title="HISTORIAL")
        tabla = Table(expand=True)
        tabla.add_column("Fecha"); tabla.add_column("Producto"); tabla.add_column("Cant"); tabla.add_column("Utilidad $")
        for _, r in db.ventas.tail(15).iterrows():
            tabla.add_row(str(r['fecha']), str(r['id_producto']), str(r['cantidad']), f"${r['utilidad_usd']:.2f}")
        return Panel(tabla, title="ÚLTIMAS VENTAS", border_style="magenta")
