from rich.console import Console
from rich.layout import Layout
from rich.panel import Panel
from rich.table import Table
from rich.columns import Columns
from rich.align import Align

class UserInterface:
    def __init__(self):
        self.console = Console()

    def layout_base(self):
        layout = Layout()
        layout.split_column(
            Layout(name="header", size=3),
            Layout(name="main", ratio=1),
            Layout(name="footer", size=3)
        )
        layout["main"].split_row(
            Layout(name="izquierda", ratio=1),
            Layout(name="derecha", ratio=2)
        )
        return layout

    def generar_header(self, db, tasa):
        utilidad = db.ventas['utilidad_usd'].sum() if not db.ventas.empty else 0.0
        return Panel(Align.center(f"[bold white]SISTEMA JGH V2.0[/bold white] | [bold yellow]Tasa: {tasa} Bs/$[/bold yellow] | [bold green]Utilidad Acumulada: ${utilidad:.2f}[/bold green]"), style="blue")

    def generar_tabla_productos(self, df, seleccionado):
        tabla = Table(expand=True, border_style="cyan", show_header=True)
        tabla.add_column("ID", justify="center", style="dim")
        tabla.add_column("Producto")
        for i, (_, r) in enumerate(df.iterrows()):
            estilo = "bold black on cyan" if i == seleccionado else ""
            tabla.add_row(str(r['id_producto']), r['nombre'], style=estilo)
        return tabla

    def panel_analisis(self, p, calc, receta_detallada, db):
        # Bloque de Finanzas
        info_finanzas = (
            f"[bold cyan]ANÁLISIS DE COSTOS Y PRECIOS[/bold cyan]\n"
            f"• Costo Producción: [bold]${p['costo_usd']:.2f}[/bold]\n"
            f"• Margen Aplicado:  [bold]{p['margen_ganancia_esperado']*100:.1f}%[/bold]\n"
            f"• Precio Sugerido:  [bold green]{p['precio_bs']:.2f} Bs[/bold green]\n"
            f"• Sensibilidad dU/dC: [bold yellow]{calc['sensibilidad_utilidad']:.4f}[/bold yellow]\n"
            f"  (Indica impacto del costo en la utilidad)\n"
        )

        # Bloque de Composición (Matriz A)
        t_rec = Table(title="[bold]ESTRUCTURA DE INSUMOS (MATRIZ A)[/bold]", border_style="magenta", expand=True)
        t_rec.add_column("Insumo")
        t_rec.add_column("Cant.", justify="right")
        t_rec.add_column("Subtotal $", justify="right")
        for item in receta_detallada:
            t_rec.add_row(item['nom'], f"{item['cant']}", f"{item['sub']:.2f}")

        # Bloque de Inventario (Doble Ubicación)
        t_inv = Table(title="[bold]ESTADO DE INVENTARIO[/bold]", border_style="green", expand=True)
        t_inv.add_column("Insumo")
        t_inv.add_column("Almacén")
        t_inv.add_column("Estante")
        t_inv.add_column("Status")
        
        for item in receta_detallada:
            # Buscamos el stock real en la DB
            ins_data = db.insumos[db.insumos['nombre'] == item['nom']].iloc[0]
            status = "[red]CRÍTICO[/red]" if ins_data['stock_almacen'] <= ins_data['punto_reorden'] else "[green]ÓPTIMO[/green]"
            t_inv.add_row(item['nom'], str(ins_data['stock_almacen']), str(ins_data['stock_estante']), status)

        return Panel(
            Columns([info_finanzas, t_rec, t_inv]),
            title=f"[bold yellow]FICHA TÉCNICA: {p['nombre']}[/bold yellow]",
            border_style="yellow"
        )
