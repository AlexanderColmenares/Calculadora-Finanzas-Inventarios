from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.layout import Layout
from rich.columns import Columns
from rich.align import Align
from datetime import datetime

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
            layout["main"].split_row(Layout(name="izq", ratio=1), Layout(name="der", ratio=2))
        return layout

    def generar_header(self, db, tasa, vista):
        # Ganancia del día: Filtrado por fecha actual
        hoy = datetime.now().strftime("%d/%m")
        ganancia_dia = 0.0
        if not db.ventas.empty and 'fecha' in db.ventas.columns:
            # Filtramos ventas que contengan la fecha de hoy en el string
            ventas_hoy = db.ventas[db.ventas['fecha'].str.contains(hoy)]
            ganancia_dia = ventas_hoy['utilidad_usd'].sum()
            
        return Panel(Align.center(f"🏢 BUSINESS INTELLIGENCE | {vista.upper()} | TASA: {tasa} Bs/$ | [bold green]GANANCIA HOY: ${ganancia_dia:.2f}[/bold green]"), style="bold white on blue")

    def generar_tabla_productos(self, df, seleccionado, tasa):
        tabla = Table(title="📦 CATÁLOGO DE PRODUCTOS", expand=True, border_style="cyan")
        tabla.add_column("ID", style="dim")
        tabla.add_column("Producto")
        tabla.add_column("Precio Bs", justify="right", style="bold green")
        tabla.add_column("Precio $", justify="right", style="bold yellow")
        
        for i, (_, r) in enumerate(df.iterrows()):
            estilo = "bold black on cyan" if i == seleccionado else ""
            p_usd = r['precio_sugerido_bs'] / tasa
            tabla.add_row(str(r['id_producto']), r['nombre'], f"{r['precio_sugerido_bs']:.2f}", f"{p_usd:.2f}", style=estilo)
        return tabla

    def panel_analisis(self, p, f, receta, db):
        # Glosario y Métricas Profesionales
        metrics = (
            f"[bold yellow]📊 INDICADORES FINANCIEROS[/bold yellow]\n"
            f"• [bold]Costo Original:[/bold] ${p['costo_reposicion_usd']:.2f} (Base de producción)\n"
            f"• [bold]Utilidad Neta:[/bold] [green]${f['utilidad_unitaria_usd']:.2f}[/green] (Ganancia pura/u)\n"
            f"• [bold]Margen Real:[/bold] {f['margen_real']:.1f}% (Retorno sobre costo)\n\n"
            f"[bold cyan]🔍 ANÁLISIS DINÁMICO[/bold cyan]\n"
            f"• [bold]Punto Equilibrio:[/bold] {f['punto_equilibrio']} uds\n"
            f"  [dim](Ventas necesarias para cubrir costos totales)[/dim]\n"
            f"• [bold]Sensibilidad (dU/dC):[/bold] {f['sensibilidad']:.2f}\n"
            f"  [dim](Si el costo sube $1, tu utilidad baja ${f['sensibilidad']:.2f})[/dim]"
        )

        t_stock = Table(title="🏗️ STATUS DE INVENTARIO", border_style="green", expand=True)
        t_stock.add_column("Componente"); t_stock.add_column("Alm."); t_stock.add_column("Est."); t_stock.add_column("Status")
        
        for item in receta:
            ins = db.insumos[db.insumos['id_insumo'] == item['id']].iloc[0]
            total = ins['stock_almacen'] + ins['stock_estante']
            # Lógica de Reorden descriptiva
            if total <= ins['punto_reorden']:
                status = "[bold red]⚠️ REORDEN[/bold red]"
            elif ins['stock_estante'] <= 5:
                status = "[bold yellow]⬇️ BAJO[/bold yellow]"
            else:
                status = "[bold green]✅ ÓPTIMO[/bold green]"
            
            t_stock.add_row(item['nom'], str(int(ins['stock_almacen'])), str(int(ins['stock_estante'])), status)

        return Panel(Columns([metrics, t_stock]), title=f"INTELIGENCIA: {p['nombre']}", border_style="yellow")

    def generar_vista_insumos(self, db):
        t = Table(title="🏗️ CONTROL DE MATERIA PRIMA (INVERSIÓN TOTAL)", expand=True)
        t.add_column("Nombre"); t.add_column("Costo $"); t.add_column("Almacén"); t.add_column("Estante"); t.add_column("Inversión $", style="bold green")
        for _, r in db.insumos.iterrows():
            # Inversión = (Lo que tienes) x (Lo que te costó)
            inv = (r['stock_almacen'] + r['stock_estante']) * r['costo_usd']
            t.add_row(r['nombre'], f"{r['costo_usd']:.2f}", str(int(r['stock_almacen'])), str(int(r['stock_estante'])), f"${inv:.2f}")
        return Panel(t, border_style="green")

    def generar_vista_historial(self, db):
        t = Table(title="📈 LOG DE OPERACIONES", expand=True)
        t.add_column("Fecha"); t.add_column("Producto"); t.add_column("Cant."); t.add_column("Ganancia $"); t.add_column("Reposición $")
        
        if not db.ventas.empty:
            for _, r in db.ventas.iterrows():
                # Manejo de error para columnas inexistentes
                utilidad = r.get('utilidad_usd', 0.0)
                costo_momento = r.get('costo_en_momento', 0.0)
                nombre = "N/A"
                if not db.productos[db.productos['id_producto'] == r['id_producto']].empty:
                    nombre = db.productos[db.productos['id_producto'] == r['id_producto']]['nombre'].iloc[0]
                
                t.add_row(str(r['fecha']), nombre, str(r['cantidad']), f"${utilidad:.2f}", f"${costo_momento * r['cantidad']:.2f}")
        return Panel(t, border_style="magenta")
