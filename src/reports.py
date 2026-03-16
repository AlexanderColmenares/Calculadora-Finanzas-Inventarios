import matplotlib.pyplot as plt
from fpdf import FPDF
import os

class ReportGenerator:
    def __init__(self):
        self.output_path = "reports"
        if not os.path.exists(self.output_path): os.makedirs(self.output_path)

    def generar_grafica_profesional(self, historial, metrics, nombre_prod):
        plt.style.use('ggplot') # Estilo más visual
        fig, ax = plt.subplots(figsize=(10, 5))
        
        # Línea de tendencia
        ax.plot(historial['fecha'], historial['utilidad_usd'], color='#2ecc71', label='Utilidad Real ($)', linewidth=2)
        ax.fill_between(historial['fecha'], historial['utilidad_usd'], alpha=0.2, color='#2ecc71')
        
        # Marcar Máximo y Mínimo con puntos exactos
        ax.scatter(metrics['max_fecha'], metrics['max_val'], color='blue', s=100, label=f"Máx: ${metrics['max_val']:.2f}")
        ax.annotate(f" Máximo", (metrics['max_fecha'], metrics['max_val']), fontweight='bold')
        
        ax.scatter(metrics['min_fecha'], metrics['min_val'], color='red', s=100, label=f"Mín: ${metrics['min_val']:.2f}")
        
        ax.set_title(f"COMPORTAMIENTO FINANCIERO: {nombre_prod}", fontsize=14, pad=20)
        ax.set_ylabel("Ganancia en Dólares ($)")
        ax.legend()
        plt.xticks(rotation=45)
        plt.tight_layout()
        
        path_img = os.path.join(self.output_path, "report_viz.png")
        plt.savefig(path_img, dpi=150)
        plt.close()
        return path_img

    def generar_pdf_avanzado(self, p, metrics, path_img):
        pdf = FPDF()
        pdf.add_page()
        
        # Encabezado "Canaima Style" / Universitario
        pdf.set_fill_color(40, 40, 40)
        pdf.rect(0, 0, 210, 40, 'F')
        pdf.set_text_color(255, 255, 255)
        pdf.set_font("Arial", 'B', 20)
        pdf.cell(190, 20, "AUDITORÍA DE RENDIMIENTO", ln=True, align='C')
        pdf.set_font("Arial", size=10)
        pdf.cell(190, 5, f"Producto: {p['nombre']} | ID: {p['id_producto']}", ln=True, align='C')
        
        pdf.ln(20)
        pdf.set_text_color(0, 0, 0)
        
        # --- TABLA DE INDICADORES ---
        pdf.set_font("Arial", 'B', 12)
        pdf.cell(95, 10, "Métrica de Sensibilidad", border=1)
        pdf.cell(95, 10, "Valor Resultante", border=1, ln=True)
        
        pdf.set_font("Arial", size=11)
        data = [
            ["Derivada Parcial (dU/dT)", f"{metrics['sens_tasa']:.4f} Bs/pt"],
            ["Utilidad Total Acumuladan en ganancias", f"${metrics['total_usd']:.2f}"],
            ["Ganancia Promedio por Venta", f"${metrics['promedio']:.2f}"],
            ["Punto de Equilibrio Crítico(Minimo necesario de ventas)", f"{int(metrics['pe_unidades'])} unidades"],
        ]
        for row in data:
            pdf.cell(95, 10, row[0], border=1)
            pdf.cell(95, 10, row[1], border=1, ln=True)

        # --- GRÁFICA ---
        pdf.ln(10)
        pdf.image(path_img, x=10, y=pdf.get_y(), w=190)
        
        # --- EXPLICACIÓN TÉCNICA ---
        pdf.set_y(pdf.get_y() + 105)
        pdf.set_font("Arial", 'I', 10)
        explicacion = (f"Interpretación: La derivada parcial indica que por cada bolívar que aumente la tasa oficial, "
                       f"su utilidad en cuenta aumentará {metrics['sens_tasa']:.2f} bolívares. El mejor desempeño fue el "
                       f"{metrics['max_fecha']} con ${metrics['max_val']:.2f}.")
        pdf.multi_cell(190, 5, explicacion)

        nombre_pdf = f"Auditoria_{p['id_producto']}.pdf"
        pdf.output(os.path.join(self.output_path, nombre_pdf))
        return nombre_pdf
