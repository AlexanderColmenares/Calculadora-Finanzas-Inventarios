import matplotlib.pyplot as plt
from fpdf import FPDF
import os

class ReportGenerator:
    def __init__(self):
        self.output_path = "reports"
        if not os.path.exists(self.output_path):
            os.makedirs(self.output_path)

    def crear_grafica_tendencia(self, ventas_df, nombre_prod):
        plt.figure(figsize=(8, 4))
        plt.plot(ventas_df['fecha'], ventas_df['utilidad_usd'], marker='o', color='green')
        plt.title(f"Tendencia de Ganancia Real: {nombre_prod}")
        plt.xlabel("Fecha")
        plt.ylabel("Utilidad (USD)")
        plt.grid(True, linestyle='--')
        
        path_img = os.path.join(self.output_path, "temp_graph.png")
        plt.savefig(path_img)
        plt.close()
        return path_img

    def generar_pdf(self, producto_nombre, stats, analisis_mat, path_grafica):
        pdf = FPDF()
        pdf.add_page()
        pdf.set_font("Arial", 'B', 16)
        pdf.cell(200, 10, f"REPORTE DE INGENIERÍA FINANCIERA: {producto_nombre}", ln=True, align='C')
        
        pdf.set_font("Arial", size=12)
        pdf.ln(10)
        pdf.cell(200, 10, f"--- Analisis de Sensibilidad (Derivadas) ---", ln=True)
        pdf.cell(200, 10, f"Impacto por devaluacion (dU/dT): {analisis_mat['sens_tasa']:.4f} Bs por punto", ln=True)
        
        pdf.ln(5)
        pdf.cell(200, 10, f"--- Estadisticas Historicas ---", ln=True)
        pdf.cell(200, 10, f"Ganancia Maxima detectada: ${stats['max_venta']:.2f}", ln=True)
        pdf.cell(200, 10, f"Ganancia Promedio: ${stats['promedio']:.2f}", ln=True)
        
        
        pdf.image(path_grafica, x=10, y=100, w=180)
        
        nombre_archivo = f"Reporte_{producto_nombre.replace(' ', '_')}.pdf"
        pdf.output(os.path.join(self.output_path, nombre_archivo))
        return nombre_archivo
