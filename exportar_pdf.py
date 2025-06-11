from fpdf import FPDF

def generar_pdf_receta(nombre, instrucciones, ingredientes, costo_total):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=12)

    pdf.set_title(nombre)

    pdf.set_font("Arial", "B", 14)
    pdf.cell(200, 10, txt=f"Receta: {nombre}", ln=True, align="C")

    pdf.set_font("Arial", "", 12)
    pdf.ln(5)
    pdf.cell(200, 10, txt=f"Costo total estimado: ₡{costo_total:,.2f}", ln=True)

    pdf.ln(5)
    pdf.set_font("Arial", "B", 12)
    pdf.cell(200, 10, txt="Ingredientes:", ln=True)

    pdf.set_font("Arial", "", 12)
    for nombre_insumo, cantidad, unidad, costo_unitario in ingredientes:
        pdf.cell(200, 8, txt=f"- {nombre_insumo}: {cantidad} {unidad} (₡{costo_unitario:,.2f} c/u)", ln=True)

    pdf.ln(5)
    pdf.set_font("Arial", "B", 12)
    pdf.cell(200, 10, txt="Instrucciones:", ln=True)

    pdf.set_font("Arial", "", 12)
    texto = instrucciones or "Sin instrucciones."
    for linea in texto.split('\n'):
        pdf.multi_cell(0, 8, linea)

    return pdf.output(dest='S').encode('latin1')  # Devuelve el contenido como bytes
