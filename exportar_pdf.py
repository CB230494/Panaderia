from fpdf import FPDF
from pathlib import Path
import unicodedata

def limpiar_texto(texto):
    if not texto:
        return ""
    # Convierte cualquier texto a string, normaliza, y elimina caracteres no ASCII
    return unicodedata.normalize("NFKD", str(texto)).encode("ASCII", "ignore").decode("ASCII")

def generar_pdf_receta(nombre, instrucciones, ingredientes, costo_total):
    pdf = FPDF()
    pdf.add_page()

    # Imagen si existe
    imagen_path = Path("imagenes_recetas") / f"{limpiar_texto(nombre).replace(' ', '_')}.jpg"
    if imagen_path.exists():
        try:
            pdf.image(str(imagen_path), x=10, y=10, w=40)
            pdf.set_xy(55, 15)
        except:
            pdf.set_y(20)
    else:
        pdf.set_y(20)

    # Título
    pdf.set_font("Arial", "B", 14)
    pdf.cell(0, 10, txt=f"Receta: {limpiar_texto(nombre)}", ln=True)

    pdf.set_font("Arial", "", 12)
    pdf.cell(0, 10, txt=f"Costo total estimado: ₡{costo_total:,.2f}", ln=True)

    # Ingredientes
    pdf.ln(5)
    pdf.set_font("Arial", "B", 12)
    pdf.cell(0, 10, txt="Ingredientes:", ln=True)

    pdf.set_font("Arial", "", 12)
    for nombre_insumo, cantidad, unidad, costo_unitario, subtotal in ingredientes:
        linea = (
            f"- {nombre_insumo}: {cantidad:.2f} {unidad} "
            f"(₡{costo_unitario:.2f} c/u → Subtotal: ₡{subtotal:,.2f})"
        )
        pdf.cell(0, 8, txt=limpiar_texto(linea), ln=True)

    # Instrucciones
    pdf.ln(5)
    pdf.set_font("Arial", "B", 12)
    pdf.cell(0, 10, txt="Instrucciones:", ln=True)

    pdf.set_font("Arial", "", 12)
    texto = instrucciones or "Sin instrucciones."
    for linea in texto.split('\n'):
        pdf.multi_cell(0, 8, limpiar_texto(linea))

    # DEVOLVER BYTES PDF CON ENCUESTA LATIN-1 LIMPIA
    contenido = pdf.output(dest="S")
    try:
        return contenido.encode("latin-1")
    except UnicodeEncodeError:
        # Fallback más seguro si aún hay caracteres raros
        return limpiar_texto(contenido).encode("latin-1", errors="ignore")


