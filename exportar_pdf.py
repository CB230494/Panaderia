from fpdf import FPDF
from pathlib import Path

def generar_pdf_receta(nombre, instrucciones, ingredientes, costo_total):
    pdf = FPDF()
    pdf.add_page()

    # Agregar imagen si existe
    imagen_path = Path("imagenes_recetas") / f"{nombre.replace(' ', '_')}.jpg"
    if imagen_path.exists():
        try:
            pdf.image(str(imagen_path), x=10, y=10, w=40)
            pdf.set_xy(55, 15)
        except:
            pdf.set_y(20)
    else:
        pdf.set_y(20)

    # Título de la receta
    pdf.set_font("Arial", "B", 14)
    pdf.cell(0, 10, txt=f"Receta: {nombre}", ln=True)

    # Costo total
    pdf.set_font("Arial", "", 12)
    pdf.cell(0, 10, txt=f"Costo total estimado: ₡{costo_total:,.2f}", ln=True)

    # Ingredientes
    pdf.ln(5)
    pdf.set_font("Arial", "B", 12)
    pdf.cell(0, 10, txt="Ingredientes:", ln=True)

    pdf.set_font("Arial", "", 12)
    for nombre_insumo, cantidad, unidad, costo_unitario in ingredientes:
        linea = f"- {nombre_insumo}: {cantidad} {unidad} (₡{costo_unitario:,.2f})"
        pdf.cell(0, 8, txt=linea.encode('latin-1', errors='replace').decode('latin-1'), ln=True)

    # Instrucciones
    pdf.ln(5)
    pdf.set_font("Arial", "B", 12)
    pdf.cell(0, 10, txt="Instrucciones:", ln=True)

    pdf.set_font("Arial", "", 12)
    texto = instrucciones or "Sin instrucciones."
    for linea in texto.split('\n'):
        linea_segura = linea.encode('latin-1', errors='replace').decode('latin-1')
        pdf.multi_cell(0, 8, linea_segura)

    # Devuelve el PDF como bytes
    return pdf.output(dest="S").encode("latin-1", errors="replace")
