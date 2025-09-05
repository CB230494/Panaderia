# === IMPORTACIONES BASE ===
import unicodedata
from pathlib import Path
from datetime import datetime
from typing import Optional, List, Dict, Any

import streamlit as st
from streamlit_option_menu import option_menu
import pandas as pd

# === Google Sheets ===
try:
    import gspread
    from gspread.exceptions import WorksheetNotFound
except Exception:
    st.error("Falta el paquete **gspread**. Agrega `gspread` y `google-auth` a tu requirements.txt y vuelve a desplegar.")
    st.stop()

# =========================
# ⚙️ CONFIG: GOOGLE SHEETS
# =========================
SPREADSHEET_URL = "https://docs.google.com/spreadsheets/d/1U3xIrv08284nxZ6XX1H-LmhtuhW7cpnydcYyBc233yU/edit?usp=sharing"

def _get_gspread_client():
    if "gcp_service_account" not in st.secrets:
        st.error(
            "No se encontraron credenciales en **st.secrets['gcp_service_account']**.\n\n"
            "👉 Sube el JSON del Service Account a *Secrets* y **comparte** el Google Sheet con ese correo."
        )
        st.stop()
    try:
        creds_dict = st.secrets["gcp_service_account"]
        return gspread.service_account_from_dict(creds_dict)
    except Exception as e:
        st.error("No se pudieron cargar las credenciales del Service Account. Revisa el JSON en *Secrets*.")
        st.stop()

def _open_sheet():
    """Abre el spreadsheet o detiene la app con un mensaje claro si no hay permisos."""
    gc = _get_gspread_client()
    try:
        return gc.open_by_url(SPREADSHEET_URL)
    except Exception:
        st.error(
            "⚠️ **No se pudo abrir la hoja de cálculo**.\n\n"
            "Posibles causas:\n"
            "1) El **Service Account no tiene acceso** (comparte el archivo con su `client_email`).\n"
            "2) La **URL del Spreadsheet** no es válida.\n\n"
            "Solución: abre el Sheet, pulsa **Compartir** y añade el correo del Service Account como Editor."
        )
        st.stop()

# ====== HELPERS ROBUSTOS (soportan hojas vacías) ======
def _get_ws(name: str, headers: List[str]) -> gspread.Worksheet:
    """
    Obtiene (o crea) la hoja y garantiza que A1 tenga los encabezados.
    Si la hoja existe vacía, los escribe.
    """
    sh = _open_sheet()
    try:
        ws = sh.worksheet(name)
    except WorksheetNotFound:
        ws = sh.add_worksheet(title=name, rows=1000, cols=max(10, len(headers)))
        ws.update("A1", [headers])
        return ws

    current_headers = ws.row_values(1)
    if not current_headers:
        ws.update("A1", [headers])
    elif current_headers != headers:
        ws.resize(rows=max(1000, ws.row_count), cols=max(len(headers), ws.col_count))
        ws.update("A1", [headers])
    return ws

def _overwrite_all(ws: gspread.Worksheet, rows: List[Dict[str, Any]]):
    """Reescribe todo el contenido manteniendo los encabezados."""
    headers = ws.row_values(1)
    if not headers:
        return
    values = [headers] + [[str(r.get(h, "")) for h in headers] for r in rows]
    ws.clear()
    ws.update("A1", values)

def _read(ws: gspread.Worksheet) -> List[Dict[str, Any]]:
    """
    Lee la hoja de forma segura incluso si está vacía.
    Devuelve [] cuando solo hay encabezados o no hay filas.
    """
    try:
        values = ws.get_all_values()
    except Exception:
        return []

    if not values:
        return []
    headers = values[0]
    if not headers:
        return []
    data_rows = values[1:]
    if not data_rows:
        return []

    out: List[Dict[str, Any]] = []
    n = len(headers)
    for row in data_rows:
        if len(row) < n:
            row = row + [""] * (n - len(row))
        elif len(row) > n:
            row = row[:n]
        if all((c is None or str(c).strip() == "") for c in row):
            continue
        out.append({h: row[i] for i, h in enumerate(headers)})
    return out

def _next_id(ws: gspread.Worksheet) -> int:
    data = _read(ws)
    if not data:
        return 1
    try:
        return max(int(float(r.get("ID", 0))) for r in data) + 1
    except Exception:
        return len(data) + 1

def _append_dict(ws: gspread.Worksheet, row_dict: Dict[str, Any]):
    headers = ws.row_values(1)
    row = [row_dict.get(h, "") for h in headers]
    ws.append_row(row, value_input_option="USER_ENTERED")

def _to_float(x, default=0.0):
    try:
        return float(str(x).replace(",", "").strip())
    except Exception:
        return default

# =========================
# 🧾 Definición de hojas
# =========================
WS_PRODUCTOS = ("Productos", ["ID", "Nombre", "Unidad", "Precio Venta", "Costo", "Stock"])
WS_INSUMOS = ("Insumos", ["ID", "Nombre", "Unidad", "Costo Unitario", "Cantidad"])
# Conservamos los nombres internos de hojas
WS_RECETAS = ("Recetas", ["ID", "Nombre", "Instrucciones"])
WS_RECETA_DET = ("Receta_Detalle", ["ID", "RecetaID", "NombreInsumo", "Cantidad", "Unidad"])
WS_MOVIMIENTOS = ("Movimientos", ["ID", "InsumoID", "InsumoNombre", "Tipo", "Cantidad", "FechaHora", "Motivo"])
WS_VENTAS = ("Ventas", ["ID", "Producto", "Unidad", "Cantidad", "Ingreso (₡)", "Costo (₡)", "Ganancia (₡)", "Fecha"])

def ws_productos(): return _get_ws(*WS_PRODUCTOS)
def ws_insumos(): return _get_ws(*WS_INSUMOS)
def ws_recetas(): return _get_ws(*WS_RECETAS)
def ws_receta_det(): return _get_ws(*WS_RECETA_DET)
def ws_movimientos(): return _get_ws(*WS_MOVIMIENTOS)
def ws_ventas(): return _get_ws(*WS_VENTAS)

# =========================
# 🖼️ PDF e imágenes
# =========================
from fpdf import FPDF
from PIL import Image

def _safe_ext(filename: str) -> str:
    ext = Path(filename).suffix.lower()
    return ext if ext in (".jpg", ".jpeg", ".png") else ".png"

def _img_path_for(nombre: str) -> Optional[Path]:
    base = Path("imagenes_recetas")
    for ext in (".jpg", ".jpeg", ".png"):
        p = base / f"{nombre.replace(' ', '_')}{ext}"
        if p.exists():
            return p
    return None

def _latin(s: str) -> str:
    if not s:
        return ""
    return unicodedata.normalize("NFKD", s).encode("latin-1", "ignore").decode("latin-1")

def _prepare_img_for_pdf(src: Path) -> Path:
    tmp_dir = src.parent
    tmp_path = tmp_dir / f"__tmp_pdf_{src.stem}.jpg"
    try:
        with Image.open(src) as im:
            if im.mode not in ("RGB", "L"):
                im = im.convert("RGB")
            im.save(tmp_path, format="JPEG", quality=90)
        return tmp_path
    except Exception:
        return src

def generar_pdf_receta(nombre: str, instrucciones: str, desglose: list, costo_total: float, ruta_img: Optional[Path]) -> bytes:
    CAFE = (141, 90, 58)
    BEIGE = (245, 233, 215)
    BEIGE_SUAVE = (236, 211, 179)
    TEXTO = (35, 35, 35)

    pdf = FPDF("P", "mm", "A4")
    pdf.set_auto_page_break(False)
    pdf.add_page()

    LEFT = 12
    pdf.set_left_margin(LEFT)
    pdf.set_right_margin(12)

    pdf.set_fill_color(*CAFE)
    pdf.rect(0, 0, 210, 40, "F")
    pdf.set_text_color(255, 255, 255)
    pdf.set_font("Helvetica", "B", 22)
    pdf.set_xy(LEFT, 10)
    pdf.cell(0, 10, _latin("Panadería Moderna  Receta"), ln=1)
    pdf.set_font("Helvetica", "", 15)
    pdf.set_xy(LEFT, 23)
    pdf.cell(0, 10, _latin(nombre), ln=1)

    y_table = 48
    tmp_to_delete = None
    if ruta_img and Path(ruta_img).exists():
        try:
            prepared = _prepare_img_for_pdf(ruta_img)
            if prepared != ruta_img:
                tmp_to_delete = prepared
            pdf.image(str(prepared), x=LEFT, y=48, h=55)
            y_table = 48 + 55 + 6
        except Exception:
            y_table = 48

    pdf.set_xy(LEFT, y_table)
    pdf.set_text_color(*TEXTO)
    pdf.set_font("Helvetica", "B", 11)
    pdf.set_fill_color(*BEIGE)
    pdf.set_draw_color(90, 70, 55)

    cols = [86, 35, 33, 32]
    headers = ["Ingrediente", "Cantidad", "Unit.", "Subtotal"]

    pdf.set_x(LEFT)
    for w, hdr in zip(cols, headers):
        pdf.cell(w, 9, _latin(hdr), border=1, align="C", fill=True)
    pdf.ln(9)

    pdf.set_font("Helvetica", "", 10)
    for (nom_i, cant, uni, costo_u, subtotal) in desglose:
        pdf.set_x(LEFT)
        pdf.cell(cols[0], 8, _latin(str(nom_i)), border=1)
        pdf.cell(cols[1], 8, _latin(f"{cant:.2f} {uni}"), border=1, align="C")
        pdf.cell(cols[2], 8, _latin(f"{costo_u:,.2f}"), border=1, align="R")
        pdf.cell(cols[3], 8, _latin(f"{subtotal:,.2f}"), border=1, align="R")
        pdf.ln(8)

    pdf.set_font("Helvetica", "B", 11)
    pdf.set_fill_color(*BEIGE_SUAVE)
    pdf.set_x(LEFT)
    pdf.cell(sum(cols[:-1]), 9, _latin("Costo total"), border=1, align="R", fill=True)
    pdf.cell(cols[-1], 9, _latin(f"{costo_total:,.2f}"), border=1, align="R", fill=True)
    pdf.ln(10)

    pdf.set_font("Helvetica", "B", 12)
    pdf.set_text_color(*CAFE)
    pdf.set_x(LEFT)
    pdf.cell(0, 7, _latin("Instrucciones"), ln=1)
    pdf.set_text_color(*TEXTO)
    pdf.set_font("Helvetica", "", 11)
    pdf.set_x(LEFT)
    pdf.multi_cell(0, 6.2, _latin(instrucciones or "Ninguna"))

    pdf.set_y(-16)
    pdf.set_font("Helvetica", "", 9)
    pdf.set_text_color(120, 120, 120)
    from datetime import datetime as _dt
    pdf.cell(0, 8, _latin(f"Generado el {_dt.now().strftime('%d/%m/%Y')} — Panadería Moderna"), align="C")

    pdf_bytes = pdf.output(dest="S").encode("latin-1")

    if tmp_to_delete and Path(tmp_to_delete).exists():
        try:
            Path(tmp_to_delete).unlink()
        except Exception:
            pass

    return pdf_bytes

# ==============================
# 🎨 ESTILO Y NAVEGACIÓN
# ==============================
st.set_page_config(page_title="Panadería Moderna", layout="wide")

if "pagina" not in st.session_state:
    st.session_state.pagina = "Inicio"

NOMBRE_RECETAS_UI = "Calculadora de gastos y generador de recetas"

st.markdown("""
    <style>
        body, .main { background-color: #121212; color: white; }
        h1, h2, h3 { color: #00ffcc; font-size: 32px; }
        .stButton>button {
            background-color: #00ffcc !important;
            color: black !important;
            font-size: 24px !important;
            font-weight: bold !important;
            padding: 30px 30px;
            border: none;
            border-radius: 16px;
            width: 100%;
        }
        .stButton>button:hover { background-color: #00e6b8 !important; transform: scale(1.02); }
        .stDataFrame th, .stDataFrame td { font-size: 18px !important; }
        .stSelectbox label, .stTextInput label, .stNumberInput label {
            font-size: 20px !important; color: #00ffcc;
        }
    </style>
""", unsafe_allow_html=True)

with st.sidebar:
    st.session_state.pagina = option_menu(
        "Navegación",
        ["Inicio", "Productos", "Insumos", NOMBRE_RECETAS_UI, "Entradas/Salidas", "Ventas", "Balance"],
        icons=["house", "archive", "truck", "file-earmark-text", "arrow-left-right", "wallet", "graph-up"],
        menu_icon="list",
        default_index=["Inicio", "Productos", "Insumos", NOMBRE_RECETAS_UI, "Entradas/Salidas", "Ventas", "Balance"].index(st.session_state.pagina),
        styles={
            "container": {"padding": "5px", "background-color": "#121212"},
            "icon": {"color": "#00ffcc", "font-size": "20px"},
            "nav-link": {"color": "#ffffff", "font-size": "18px", "text-align": "left", "margin": "2px"},
            "nav-link-selected": {"background-color": "#00ffcc", "color": "#121212", "font-weight": "bold"},
        }
    )

# =============================
# 🏠 INICIO
# =============================
if st.session_state.pagina == "Inicio":
    st.markdown("## 📊 Sistema de Gestión - Panadería ")
    st.markdown("### Selecciona una opción para comenzar:")

    col1, col2, col3 = st.columns(3)
    with col1:
        if st.button("📦 Productos"): st.session_state.pagina = "Productos"; st.rerun()
    with col2:
        if st.button("🚚 Insumos"): st.session_state.pagina = "Insumos"; st.rerun()
    with col3:
        if st.button("🧮 " + NOMBRE_RECETAS_UI): st.session_state.pagina = NOMBRE_RECETAS_UI; st.rerun()

    col4, col5, col6 = st.columns(3)
    with col4:
        if st.button("🔄 Entradas/Salidas"): st.session_state.pagina = "Entradas/Salidas"; st.rerun()
    with col5:
        if st.button("💵 Ventas"): st.session_state.pagina = "Ventas"; st.rerun()
    with col6:
        if st.button("📈 Balance"): st.session_state.pagina = "Balance"; st.rerun()

# =============================
# 📦 PESTAÑA: PRODUCTOS
# =============================
if st.session_state.pagina == "Productos":
    st.subheader("📦 Gestión de Productos")
    ws_p = ws_productos()

    with st.form("form_agregar_producto"):
        st.markdown("### ➕ Agregar nuevo producto")
        nombre = st.text_input("Nombre del producto")
        unidad = st.selectbox("Unidad", ["unidad", "porción", "pieza", "queque", "paquete"])
        precio_venta = st.number_input("Precio de venta (₡)", min_value=0.0, format="%.2f")
        costo = st.number_input("Costo de elaboración (₡)", min_value=0.0, format="%.2f")
        stock = st.number_input("Cantidad en stock", min_value=0, step=1)
        submitted = st.form_submit_button("Agregar")

        if submitted:
            if nombre and unidad:
                _append_dict(ws_p, {
                    "ID": _next_id(ws_p),
                    "Nombre": nombre,
                    "Unidad": unidad,
                    "Precio Venta": precio_venta,
                    "Costo": costo,
                    "Stock": stock
                })
                st.success(f"✅ Producto '{nombre}' agregado correctamente.")
                st.rerun()
            else:
                st.warning("⚠️ Debes completar todos los campos.")

    st.markdown("### 📋 Lista de productos")
    productos = _read(ws_p)
    if productos:
        df = pd.DataFrame(productos)
        df["Ganancia (₡)"] = df["Precio Venta"].apply(_to_float) - df["Costo"].apply(_to_float)

        def _fmt(x):
            xv = _to_float(x, None)
            if xv is None:
                return x
            return f"₡{int(xv)}" if xv == int(xv) else f"₡{xv:,.2f}"

        for col in ["Precio Venta", "Costo", "Ganancia (₡)"]:
            df[col] = df[col].map(_fmt)

        def color_stock(val):
            v = _to_float(val, 0)
            return 'background-color: red; color: white' if v < 5 else ''
        styled_df = df.style.applymap(color_stock, subset=["Stock"])
        st.dataframe(styled_df, use_container_width=True)

        st.markdown("### ✏️ Editar o eliminar un producto")
        nombres_disponibles = [p["Nombre"] for p in productos]
        if nombres_disponibles:
            seleccion = st.selectbox("Seleccionar producto por nombre", nombres_disponibles)

            prod = next(p for p in productos if p["Nombre"] == seleccion)
            id_producto = int(_to_float(prod["ID"], 0))

            with st.form("form_editar_producto"):
                nuevo_nombre = st.text_input("Nombre", value=prod["Nombre"])
                nueva_unidad = st.selectbox(
                    "Unidad", ["unidad", "porción", "pieza", "queque", "paquete"],
                    index=["unidad", "porción", "pieza", "queque", "paquete"].index(prod["Unidad"])
                )
                nuevo_precio = st.number_input("Precio de venta (₡)", value=_to_float(prod["Precio Venta"]), format="%.2f")
                nuevo_costo = st.number_input("Costo de elaboración (₡)", value=_to_float(prod["Costo"]), format="%.2f")
                nuevo_stock = st.number_input("Stock disponible", value=int(_to_float(prod["Stock"])), step=1)

                col1, col2 = st.columns(2)
                with col1:
                    actualizar = st.form_submit_button("Actualizar")
                with col2:
                    eliminar = st.form_submit_button("Eliminar")

                if actualizar:
                    _update = {
                        "Nombre": nuevo_nombre,
                        "Unidad": nueva_unidad,
                        "Precio Venta": nuevo_precio,
                        "Costo": nuevo_costo,
                        "Stock": int(nuevo_stock)
                    }
                    rows = _read(ws_p)
                    for r in rows:
                        if _to_float(r.get("ID"), -1) == id_producto:
                            r.update(_update)
                            break
                    _overwrite_all(ws_p, rows)
                    st.success("✅ Producto actualizado correctamente.")
                    st.rerun()
                if eliminar:
                    rows = [r for r in _read(ws_p) if _to_float(r.get("ID"), -1) != id_producto]
                    _overwrite_all(ws_p, rows)
                    st.success("🗑️ Producto eliminado correctamente.")
                    st.rerun()
    else:
        st.info("ℹ️ No hay productos registrados todavía.")

# =============================
# 🚚 PESTAÑA: INSUMOS
# =============================
if st.session_state.pagina == "Insumos":
    st.subheader("🚚 Gestión de Insumos")
    ws_i = ws_insumos()

    unidades_dict = {
        "Kilogramo (kg)": "kg",
        "Gramo (g)": "g",
        "Litro (l)": "l",
        "Mililitro (ml)": "ml",
        "Barra": "barra",
        "Unidad": "unidad"
    }

    with st.form("form_agregar_insumo"):
        st.markdown("### ➕ Agregar nuevo insumo")
        nombre_i = st.text_input("Nombre del insumo")
        unidad_i_visible = st.selectbox("Unidad", list(unidades_dict.keys()))
        unidad_i = unidades_dict[unidad_i_visible]
        cantidad = st.number_input("Cantidad adquirida", min_value=0.0)
        costo_total = st.number_input("Costo total (₡)", min_value=0.0, format="%.2f")
        submitted_i = st.form_submit_button("Agregar")

        if submitted_i:
            if nombre_i and unidad_i and cantidad > 0:
                costo_unitario = costo_total / cantidad
                _append_dict(ws_i, {
                    "ID": _next_id(ws_i),
                    "Nombre": nombre_i,
                    "Unidad": unidad_i,
                    "Costo Unitario": costo_unitario,
                    "Cantidad": cantidad
                })
                # Mensaje de costo base
                if unidad_i in ["kg", "l"]:
                    costo_base = costo_unitario / 1000
                    unidad_base = "gramo" if unidad_i == "kg" else "mililitro"
                else:
                    costo_base = costo_unitario
                    unidad_base = unidad_i
                st.success(
                    f"✅ '{nombre_i}' agregado correctamente. "
                    f"{cantidad} {unidad_i}, Costo total: ₡{costo_total:.2f}, "
                    f"₡{costo_unitario:.2f}/{unidad_i} → ₡{costo_base:.2f} por {unidad_base}"
                )
                st.rerun()
            else:
                st.warning("⚠️ Debes completar todos los campos y la cantidad debe ser mayor a cero.")

    st.markdown("### 📋 Lista de insumos")
    insumos = _read(ws_i)
    if insumos:
        df_i = pd.DataFrame(insumos)
        unidad_legible = {v: k for k, v in unidades_dict.items()}
        df_i["Unidad Mostrada"] = df_i["Unidad"].map(unidad_legible)

        def precio_base(row):
            cu = _to_float(row["Costo Unitario"])
            return cu / 1000 if row["Unidad"] in ["kg", "l"] else cu

        df_i["₡ por unidad base"] = df_i.apply(precio_base, axis=1).map(lambda x: f"₡{float(x):.2f}")
        df_i["Costo Total (₡)"] = (df_i["Costo Unitario"].apply(_to_float) * df_i["Cantidad"].apply(_to_float)).map(lambda x: f"₡{x:,.2f}")
        df_i["Costo Unitario"] = df_i["Costo Unitario"].apply(_to_float).map(lambda x: f"₡{x:,.2f}")

        st.dataframe(df_i[["ID", "Nombre", "Unidad Mostrada", "Costo Unitario", "Cantidad", "Costo Total (₡)", "₡ por unidad base"]],
                     use_container_width=True)

        st.markdown("### ✏️ Editar o eliminar un insumo")
        nombres_insumos = [i["Nombre"] for i in insumos]
        if nombres_insumos:
            seleccion_i = st.selectbox("Seleccionar insumo por nombre", nombres_insumos)

            insumo_sel = next(i for i in insumos if i["Nombre"] == seleccion_i)
            id_insumo = int(_to_float(insumo_sel["ID"]))
            unidad_visible_original = [k for k, v in unidades_dict.items() if v == insumo_sel["Unidad"]][0]

            with st.form("form_editar_insumo"):
                nuevo_nombre_i = st.text_input("Nombre", value=insumo_sel["Nombre"])
                nueva_unidad_visible = st.selectbox("Unidad", list(unidades_dict.keys()),
                                                    index=list(unidades_dict.keys()).index(unidad_visible_original))
                nueva_unidad = unidades_dict[nueva_unidad_visible]
                nueva_cantidad = st.number_input("Cantidad adquirida", value=_to_float(insumo_sel["Cantidad"]))
                costo_total_original = _to_float(insumo_sel["Costo Unitario"]) * _to_float(insumo_sel["Cantidad"])
                nuevo_costo_total = st.number_input("Costo total (₡)", value=float(costo_total_original), format="%.2f")

                col1, col2 = st.columns(2)
                with col1:
                    actualizar_i = st.form_submit_button("Actualizar")
                with col2:
                    eliminar_i = st.form_submit_button("Eliminar")

                if actualizar_i and nueva_cantidad > 0:
                    nuevo_costo_unitario = nuevo_costo_total / nueva_cantidad
                    rows = _read(ws_i)
                    for r in rows:
                        if _to_float(r.get("ID"), -1) == id_insumo:
                            r.update({
                                "Nombre": nuevo_nombre_i,
                                "Unidad": nueva_unidad,
                                "Costo Unitario": nuevo_costo_unitario,
                                "Cantidad": nueva_cantidad
                            })
                            break
                    _overwrite_all(ws_i, rows)
                    st.success("✅ Insumo actualizado correctamente.")
                    st.rerun()
                if eliminar_i:
                    rows = [r for r in _read(ws_i) if _to_float(r.get("ID"), -1) != id_insumo]
                    _overwrite_all(ws_i, rows)
                    st.success("🗑️ Insumo eliminado correctamente.")
                    st.rerun()
    else:
        st.info("ℹ️ No hay insumos registrados todavía.")

# ==============================================================
# 🧮 PESTAÑA: CALCULADORA DE GASTOS Y GENERADOR DE RECETAS
# ==============================================================
if st.session_state.pagina == NOMBRE_RECETAS_UI:
    st.subheader("🧮 Calculadora de gastos y generador de recetas")
    ws_r = ws_recetas()
    ws_rd = ws_receta_det()
    ws_i = ws_insumos()

    with st.form("form_nueva_receta"):
        st.markdown("### ➕ Crear nueva receta")
        nombre_receta = st.text_input("📛 Nombre de la receta")
        instrucciones = st.text_area("📖 Instrucciones de preparación")
        imagen_receta = st.file_uploader("📷 Foto del producto final (opcional)", type=["png", "jpg", "jpeg"])

        insumos = _read(ws_i)
        insumo_seleccionado = []

        if not insumos:
            st.warning("⚠️ No hay insumos registrados. Agrega insumos primero.")
        else:
            st.markdown("### 🧺 Seleccionar ingredientes:")
            for insumo in insumos:
                insumo_id = int(_to_float(insumo["ID"]))
                nombre = insumo["Nombre"]
                unidad = insumo["Unidad"]
                cantidad = st.number_input(f"{nombre} ({unidad})", min_value=0.0, step=0.1, key=f"nuevo_{insumo_id}")
                if cantidad > 0:
                    insumo_seleccionado.append((insumo_id, nombre, cantidad, unidad))

        submitted_receta = st.form_submit_button("🍽️ Guardar receta")

        if submitted_receta:
            if not nombre_receta or not insumo_seleccionado:
                st.warning("⚠️ Debes ingresar un nombre y al menos un insumo.")
            else:
                rid = _next_id(ws_r)
                _append_dict(ws_r, {"ID": rid, "Nombre": nombre_receta, "Instrucciones": instrucciones})
                for _, nombre_i, cant, uni in insumo_seleccionado:
                    _append_dict(ws_rd, {
                        "ID": _next_id(ws_rd),
                        "RecetaID": rid,
                        "NombreInsumo": nombre_i,
                        "Cantidad": cant,
                        "Unidad": uni
                    })
                if imagen_receta:
                    carpeta_imagenes = Path("imagenes_recetas"); carpeta_imagenes.mkdir(exist_ok=True)
                    ext = _safe_ext(imagen_receta.name)
                    nombre_archivo = f"{nombre_receta.replace(' ', '_')}{ext}"
                    with open(carpeta_imagenes / nombre_archivo, "wb") as f:
                        f.write(imagen_receta.read())
                st.success(f"✅ Receta '{nombre_receta}' guardada correctamente.")
                st.rerun()

    st.markdown("### 📋 Recetas registradas")
    recetas = _read(ws_r)
    detalles_all = _read(ws_rd)
    insumos_db_list = _read(ws_i)
    insumos_db = {i["Nombre"]: i for i in insumos_db_list}

    if recetas:
        for receta in recetas:
            receta_id = int(_to_float(receta["ID"]))
            nombre = receta["Nombre"]
            instrucciones = receta.get("Instrucciones", "")

            detalles = [d for d in detalles_all if _to_float(d["RecetaID"]) == receta_id]

            desglose = []
            costo_total = 0.0
            for det in detalles:
                nombre_insumo = det["NombreInsumo"]
                cantidad = _to_float(det["Cantidad"])
                unidad = det["Unidad"]

                insumo_info = insumos_db.get(nombre_insumo)
                if not insumo_info:
                    continue
                costo_unitario = _to_float(insumo_info["Costo Unitario"])
                unidad_insumo = insumo_info["Unidad"]

                if unidad_insumo in ["kg", "l"]:
                    costo_por_base = costo_unitario / 1000
                    cantidad_en_base = cantidad * 1000 if unidad == unidad_insumo else cantidad
                else:
                    costo_por_base = costo_unitario
                    cantidad_en_base = cantidad

                subtotal = cantidad_en_base * costo_por_base
                costo_total += subtotal
                desglose.append((nombre_insumo, cantidad, unidad, costo_por_base, subtotal))

            with st.expander(f"🍰 {nombre} - Costo total: ₡{costo_total:,.2f}"):
                ruta_img = _img_path_for(nombre)
                if ruta_img and ruta_img.exists():
                    st.image(str(ruta_img), caption=f"📷 {nombre}", width=300)

                st.markdown(f"**📝 Instrucciones:** {instrucciones or 'Sin instrucciones.'}")
                st.markdown("**🧾 Ingredientes:**")
                for nombre_i, cant_i, unidad_i, costo_u, subtotal in desglose:
                    st.markdown(
                        f"- {nombre_i} — {cant_i:.2f} {unidad_i} — "
                        f"(₡{costo_u:.2f} c/u → Subtotal: ₡{subtotal:,.2f})"
                    )

                # PDF
                try:
                    pdf_bytes = generar_pdf_receta(
                        nombre=nombre,
                        instrucciones=instrucciones or "",
                        desglose=desglose,
                        costo_total=costo_total,
                        ruta_img=ruta_img if ruta_img and ruta_img.exists() else None
                    )
                    st.download_button(
                        label="📥 Descargar receta (PDF)",
                        data=pdf_bytes,
                        file_name=f"Receta_{nombre.replace(' ', '_')}.pdf",
                        mime="application/pdf",
                        use_container_width=True
                    )
                except Exception as e:
                    st.error(f"⚠️ No se pudo generar el PDF: {e}")

                col1, col2 = st.columns(2)
                with col1:
                    if st.button(f"🗑️ Eliminar receta", key=f"eliminar_{receta_id}"):
                        # Elimina maestro
                        rows_r = [r for r in _read(ws_r) if _to_float(r["ID"]) != receta_id]
                        _overwrite_all(ws_r, rows_r)
                        # Elimina detalle
                        det_kept = [d for d in _read(ws_rd) if _to_float(d["RecetaID"]) != receta_id]
                        _overwrite_all(ws_rd, det_kept)
                        # Borra imagen si existe
                        base = Path("imagenes_recetas")
                        for ext in (".jpg", ".jpeg", ".png"):
                            p = base / f"{nombre.replace(' ', '_')}{ext}"
                            if p.exists():
                                p.unlink()
                        st.success(f"🗑️ Receta '{nombre}' eliminada.")
                        st.rerun()
                with col2:
                    if st.button("✏️ Editar receta", key=f"editar_{receta_id}"):
                        st.session_state[f"editando_{receta_id}"] = True

            if st.session_state.get(f"editando_{receta_id}", False):
                with st.form(f"form_edicion_{receta_id}"):
                    nuevo_nombre = st.text_input("📛 Nuevo nombre", value=nombre, key=f"nombre_{receta_id}")
                    nuevas_instrucciones = st.text_area("📖 Nuevas instrucciones", value=instrucciones or "", key=f"inst_{receta_id}")
                    nueva_imagen = st.file_uploader("📷 Nueva imagen (opcional)", type=["jpg", "jpeg", "png"], key=f"img_{receta_id}")

                    nuevos_insumos = []
                    for insumo in insumos_db_list:
                        insumo_nombre = insumo["Nombre"]
                        unidad = insumo["Unidad"]
                        actual = next((_to_float(d["Cantidad"]) for d in detalles if d["NombreInsumo"] == insumo_nombre), 0.0)
                        cantidad = st.number_input(
                            f"{insumo_nombre} ({unidad})",
                            value=float(actual),
                            min_value=0.0, step=0.1,
                            key=f"insumo_edit_{receta_id}_{insumo_nombre}"
                        )
                        if cantidad > 0:
                            nuevos_insumos.append((insumo_nombre, cantidad, unidad))

                    guardar = st.form_submit_button("💾 Guardar cambios")
                    if guardar:
                        # Actualiza maestro
                        rows_r = _read(ws_r)
                        for r in rows_r:
                            if _to_float(r["ID"]) == receta_id:
                                r["Nombre"] = nuevo_nombre
                                r["Instrucciones"] = nuevas_instrucciones
                                break
                        _overwrite_all(ws_r, rows_r)

                        # Reemplaza detalle
                        det_otros = [d for d in _read(ws_rd) if _to_float(d["RecetaID"]) != receta_id]
                        for nom_i, cant, uni in nuevos_insumos:
                            det_otros.append({
                                "ID": "",  # se re-enumerará
                                "RecetaID": receta_id,
                                "NombreInsumo": nom_i,
                                "Cantidad": cant,
                                "Unidad": uni
                            })
                        # Reasignar IDs de detalle
                        rows_final = []
                        for r in det_otros:
                            if not str(r.get("ID", "")).strip():
                                r["ID"] = len(rows_final) + 1
                            rows_final.append(r)
                        _overwrite_all(ws_receta_det(), rows_final)

                        # Imagen
                        carpeta = Path("imagenes_recetas"); carpeta.mkdir(exist_ok=True)
                        if nueva_imagen:
                            for ext in (".jpg", ".jpeg", ".png"):
                                viejo = carpeta / f"{nombre.replace(' ', '_')}{ext}"
                                if viejo.exists():
                                    viejo.unlink()
                            ext = _safe_ext(nueva_imagen.name)
                            nuevo = carpeta / f"{nuevo_nombre.replace(' ', '_')}{ext}"
                            with open(nuevo, "wb") as f:
                                f.write(nueva_imagen.read())
                        else:
                            viejo_existente = _img_path_for(nombre)
                            if viejo_existente and nombre != nuevo_nombre:
                                nuevo = viejo_existente.with_name(f"{nuevo_nombre.replace(' ', '_')}{viejo_existente.suffix}")
                                viejo_existente.rename(nuevo)

                        st.success("✅ Receta actualizada.")
                        st.session_state[f"editando_{receta_id}"] = False
                        st.rerun()
    else:
        st.info("ℹ️ No hay recetas registradas todavía.")

# =============================
# 📤 PESTAÑA: ENTRADAS/SALIDAS
# =============================
if st.session_state.pagina == "Entradas/Salidas":
    st.subheader("📤 Registro de Entradas y Salidas de Insumos")
    ws_i = ws_insumos()
    ws_m = ws_movimientos()

    insumos = _read(ws_i)
    if not insumos:
        st.warning("⚠️ No hay insumos disponibles. Registra insumos primero.")
        st.stop()

    unidad_legible = {
        "kg": "kilogramos",
        "g": "gramos",
        "l": "litros",
        "ml": "mililitros",
        "barra": "barras",
        "unidad": "unidades"
    }

    nombres_insumos = [f"{i['Nombre']} ({unidad_legible.get(i['Unidad'], i['Unidad'])})" for i in insumos]
    insumo_elegido = st.selectbox("🔽 Selecciona el insumo", nombres_insumos)

    index = nombres_insumos.index(insumo_elegido)
    insumo_sel = insumos[index]
    insumo_id = int(_to_float(insumo_sel["ID"]))
    nombre = insumo_sel["Nombre"]
    unidad = insumo_sel["Unidad"]
    cantidad_actual = _to_float(insumo_sel["Cantidad"])
    unidad_visible = unidad_legible.get(unidad, unidad)

    st.markdown(
        f"<div style='font-size:20px; font-weight:bold; color:#ffa500;'>📦 Cantidad disponible: "
        f"{cantidad_actual:.2f} {unidad_visible}</div>", unsafe_allow_html=True
    )

    tipo_movimiento = st.radio("📌 Tipo de movimiento", ["Entrada", "Salida"], horizontal=True)
    cantidad = st.number_input("📏 Cantidad a registrar", min_value=0.0, step=0.1)
    motivo = st.text_input("✏️ Motivo (opcional)")
    registrar = st.button("💾 Registrar movimiento")

    if registrar:
        if tipo_movimiento == "Salida" and cantidad > cantidad_actual:
            st.error("❌ No hay suficiente stock para realizar la salida.")
        else:
            fecha_hora = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            _append_dict(ws_m, {
                "ID": _next_id(ws_m),
                "InsumoID": insumo_id,
                "InsumoNombre": nombre,
                "Tipo": tipo_movimiento,
                "Cantidad": cantidad,
                "FechaHora": fecha_hora,
                "Motivo": motivo
            })
            # Actualiza stock del insumo
            nuevo_stock = cantidad_actual + cantidad if tipo_movimiento == "Entrada" else cantidad_actual - cantidad
            rows = _read(ws_i)
            for r in rows:
                if _to_float(r.get("ID")) == insumo_id:
                    r["Cantidad"] = nuevo_stock
                    break
            _overwrite_all(ws_i, rows)
            st.success("✅ Movimiento registrado correctamente.")
            st.rerun()

    # Historial
    historial = _read(ws_m)
    if historial:
        st.markdown("### 📜 Historial de Movimientos")
        df_hist = pd.DataFrame(historial)
        if not df_hist.empty:
            df_hist["Fecha y Hora"] = pd.to_datetime(df_hist["FechaHora"]).dt.strftime("%d/%m/%Y")
            df_hist["Cantidad"] = df_hist["Cantidad"].apply(_to_float).apply(lambda x: f"{x:.2f}")
            df_hist = df_hist.rename(columns={"InsumoNombre": "Insumo"})
            df_hist = df_hist[["Insumo", "Tipo", "Cantidad", "Fecha y Hora", "Motivo"]]

            def colorear_tipo(val):
                color = 'green' if val == "Entrada" else 'red'
                return f'color: {color}; font-weight: bold'

            st.dataframe(df_hist.style.applymap(colorear_tipo, subset=["Tipo"]), use_container_width=True)

    # Stock bajo
    st.markdown("### 🚨 Insumos con stock bajo")
    bajo_stock = [i for i in _read(ws_i) if _to_float(i["Cantidad"]) < 3]
    if bajo_stock:
        df_bajo = pd.DataFrame(bajo_stock)
        df_bajo["Unidad"] = df_bajo["Unidad"].map(unidad_legible)
        df_bajo["₡ x unidad"] = df_bajo["Costo Unitario"].apply(_to_float).apply(lambda x: f"₡{x:,.2f}")
        df_bajo["Cantidad disponible"] = df_bajo["Cantidad"].apply(_to_float).apply(lambda x: f"{x:.2f}")
        df_bajo = df_bajo.rename(columns={"Nombre": "Insumo"})
        st.warning("⚠️ Tienes insumos con menos de 3 unidades.")
        st.dataframe(df_bajo[["Insumo", "Unidad", "₡ x unidad", "Cantidad disponible"]], use_container_width=True)
    else:
        st.success("✅ Todos los insumos tienen suficiente stock.")

# =============================
# 💰 PESTAÑA: VENTAS
# =============================
if st.session_state.pagina == "Ventas":
    st.subheader("💰 Registro de Ventas de Productos")
    ws_p = ws_productos()
    ws_v = ws_ventas()

    productos = _read(ws_p)
    if not productos:
        st.warning("⚠️ No hay productos disponibles. Agrega primero desde la pestaña de Productos.")
    else:
        nombres_productos = [f"{p['Nombre']} ({p['Unidad']})" for p in productos]
        producto_elegido = st.selectbox("🧁 Selecciona el producto vendido", nombres_productos)

        index = nombres_productos.index(producto_elegido)
        prod = productos[index]
        id_producto = int(_to_float(prod["ID"]))
        nombre = prod["Nombre"]
        unidad = prod["Unidad"]
        precio_venta = _to_float(prod["Precio Venta"])
        costo_unitario = _to_float(prod["Costo"])
        stock_disponible = _to_float(prod["Stock"])

        st.markdown(f"**💵 Precio de venta:** ₡{precio_venta:,.2f}")
        st.markdown(f"**🧾 Costo de elaboración:** ₡{costo_unitario:,.2f}")
        st.markdown(f"**📦 Stock disponible:** {stock_disponible:.2f} {unidad}")

        cantidad_vendida = st.number_input("📏 Cantidad vendida", min_value=0.0, step=0.1)
        registrar_venta = st.button("💾 Registrar venta")

        if registrar_venta:
            if cantidad_vendida <= 0:
                st.warning("⚠️ Debes ingresar una cantidad mayor a cero.")
            elif cantidad_vendida > stock_disponible:
                st.error("❌ No puedes vender más de lo que tienes en stock.")
            else:
                ingreso_total = round(cantidad_vendida * precio_venta, 2)
                costo_total = round(cantidad_vendida * costo_unitario, 2)
                ganancia_total = round(ingreso_total - costo_total, 2)
                fecha_actual = datetime.now().strftime("%d/%m/%Y")

                _append_dict(ws_v, {
                    "ID": _next_id(ws_v),
                    "Producto": nombre,
                    "Unidad": unidad,
                    "Cantidad": cantidad_vendida,
                    "Ingreso (₡)": ingreso_total,
                    "Costo (₡)": costo_total,
                    "Ganancia (₡)": ganancia_total,
                    "Fecha": fecha_actual
                })

                # Actualiza stock del producto
                rows = _read(ws_p)
                for r in rows:
                    if _to_float(r.get("ID")) == id_producto:
                        r["Stock"] = stock_disponible - cantidad_vendida
                        break
                _overwrite_all(ws_p, rows)

                st.success("✅ Venta registrada correctamente.")
                st.rerun()

    ventas = _read(ws_v)
    if ventas:
        st.markdown("### 📋 Historial de ventas")
        df_ventas = pd.DataFrame(ventas)
        if not df_ventas.empty:
            df_ventas["Cantidad"] = df_ventas["Cantidad"].apply(_to_float).apply(lambda x: f"{x:.2f}")
            for c in ["Ingreso (₡)", "Costo (₡)", "Ganancia (₡)"]:
                df_ventas[c] = df_ventas[c].apply(_to_float).apply(lambda x: f"₡{x:,.2f}")
            st.dataframe(df_ventas.drop(columns=["ID"]), use_container_width=True)

            total_ingresos = sum(_to_float(v["Ingreso (₡)"]) for v in ventas)
            total_ganancias = sum(_to_float(v["Ganancia (₡)"]) for v in ventas)

            st.markdown(f"**💵 Total ingresos:** ₡{total_ingresos:,.2f}")
            st.markdown(f"**📈 Total ganancias:** ₡{total_ganancias:,.2f}")

            # Producto estrella
            df_crudo = pd.DataFrame(ventas)
            df_crudo["Cantidad"] = df_crudo["Cantidad"].apply(_to_float)
            if not df_crudo.empty:
                producto_estrella = df_crudo.groupby("Producto")["Cantidad"].sum().idxmax()
                cantidad_estrella = df_crudo.groupby("Producto")["Cantidad"].sum().max()
                st.success(f"🌟 Producto estrella: **{producto_estrella}** con **{cantidad_estrella:.2f}** unidades vendidas")

            # Editar/eliminar
            st.markdown("### ✏️ Editar o eliminar una venta")
            ids_ventas = [f"{int(_to_float(v['ID']))} - {v['Producto']} ({_to_float(v['Cantidad']):.2f})" for v in ventas]
            seleccion_id = st.selectbox("Selecciona una venta", ids_ventas)

            venta_id = int(seleccion_id.split(" - ")[0])
            venta = next(v for v in ventas if int(_to_float(v["ID"])) == venta_id)

            nueva_cantidad = st.number_input("Nueva cantidad vendida", min_value=0.1, value=_to_float(venta["Cantidad"]), step=0.1)
            col1, col2 = st.columns(2)
            with col1:
                if st.button("Actualizar venta"):
                    # Recalcula con precio/costo actuales del producto (si existe)
                    prod_match = next((p for p in _read(ws_productos()) if p["Nombre"] == venta["Producto"]), None)
                    if prod_match:
                        precio_venta = _to_float(prod_match["Precio Venta"])
                        costo_unitario = _to_float(prod_match["Costo"])
                    else:
                        precio_venta = _to_float(venta["Ingreso (₡)"]) / max(_to_float(venta["Cantidad"]), 1e-9)
                        costo_unitario = _to_float(venta["Costo (₡)"]) / max(_to_float(venta["Cantidad"]), 1e-9)

                    nuevo_ingreso = round(nueva_cantidad * precio_venta, 2)
                    nuevo_costo = round(nueva_cantidad * costo_unitario, 2)
                    nueva_ganancia = round(nuevo_ingreso - nuevo_costo, 2)

                    rows_v = _read(ws_v)
                    for r in rows_v:
                        if int(_to_float(r["ID"])) == venta_id:
                            r["Cantidad"] = nueva_cantidad
                            r["Ingreso (₡)"] = nuevo_ingreso
                            r["Costo (₡)"] = nuevo_costo
                            r["Ganancia (₡)"] = nueva_ganancia
                            break
                    _overwrite_all(ws_v, rows_v)
                    st.success("✅ Venta actualizada correctamente.")
                    st.rerun()
            with col2:
                if st.button("Eliminar venta"):
                    rows_v = [r for r in _read(ws_v) if int(_to_float(r["ID"])) != venta_id]
                    _overwrite_all(ws_v, rows_v)
                    st.success("🗑️ Venta eliminada correctamente.")
                    st.rerun()
    else:
        st.info("ℹ️ Aún no hay ventas registradas.")

# =============================
# 📊 PESTAÑA: BALANCE
# =============================
if st.session_state.pagina == "Balance":
    st.subheader("📊 Balance General del Negocio")

    st.markdown("### 📅 Selecciona un rango de fechas")
    col1, col2 = st.columns(2)
    with col1:
        fecha_inicio = st.date_input("Desde", value=datetime.today().replace(day=1))
    with col2:
        fecha_fin = st.date_input("Hasta", value=datetime.today())

    # Inventario (insumos)
    insumos = _read(ws_insumos())
    if insumos:
        df_insumos = pd.DataFrame(insumos)
        unidad_legible = {
            "kg": "kilogramos", "g": "gramos", "l": "litros",
            "ml": "mililitros", "barra": "barras", "unidad": "unidades"
        }
        df_insumos["Unidad"] = df_insumos["Unidad"].map(unidad_legible)
        df_insumos["Total (₡)"] = df_insumos["Costo Unitario"].apply(_to_float) * df_insumos["Cantidad"].apply(_to_float)
        df_insumos["Costo Unitario"] = df_insumos["Costo Unitario"].apply(_to_float).apply(lambda x: f"₡{x:,.2f}")
        df_insumos["Total (₡)"] = df_insumos["Total (₡)"].apply(_to_float).apply(lambda x: f"₡{x:,.2f}")

        total_inventario_num = sum(_to_float(i["Costo Unitario"]) * _to_float(i["Cantidad"]) for i in insumos)

        st.markdown("### 📦 Valor del inventario de insumos")
        st.dataframe(df_insumos[["Nombre", "Unidad", "Cantidad", "Costo Unitario", "Total (₡)"]], use_container_width=True)
        st.markdown(f"**🔹 Total inventario:** ₡{total_inventario_num:,.2f}")
    else:
        total_inventario_num = 0.0
        st.info("ℹ️ No hay insumos registrados.")

    st.divider()

    # Ventas en el periodo
    ventas = _read(ws_ventas())
    st.markdown("### 💰 Ventas registradas en el período")
    if ventas:
        df_ventas = pd.DataFrame(ventas)
        if not df_ventas.empty:
            df_ventas["Fecha"] = pd.to_datetime(df_ventas["Fecha"], format="%d/%m/%Y", errors="coerce")

            df_ventas_filtrado = df_ventas[
                (df_ventas["Fecha"] >= pd.to_datetime(fecha_inicio)) &
                (df_ventas["Fecha"] <= pd.to_datetime(fecha_fin))
            ]

            if not df_ventas_filtrado.empty:
                total_ingresos = df_ventas_filtrado["Ingreso (₡)"].apply(_to_float).sum()
                total_costos = df_ventas_filtrado["Costo (₡)"].apply(_to_float).sum()
                total_ganancia = df_ventas_filtrado["Ganancia (₡)"].apply(_to_float).sum()

                df_ventas_filtrado["Cantidad"] = df_ventas_filtrado["Cantidad"].apply(_to_float).apply(lambda x: f"{x:.2f}")
                for c in ["Ingreso (₡)", "Costo (₡)", "Ganancia (₡)"]:
                    df_ventas_filtrado[c] = df_ventas_filtrado[c].apply(_to_float).apply(lambda x: f"₡{x:,.2f}")
                df_ventas_filtrado["Fecha"] = df_ventas_filtrado["Fecha"].dt.strftime("%d/%m/%Y")

                st.dataframe(df_ventas_filtrado.drop(columns=["ID"]), use_container_width=True)

                st.markdown(f"- **🟢 Ingresos:** ₡{total_ingresos:,.2f}")
                st.markdown(f"- **🧾 Costos:** ₡{total_costos:,.2f}")
                st.markdown(f"- **📈 Ganancia total:** ₡{total_ganancia:,.2f}")

                st.divider()
                st.markdown("### 📉 Comparativo resumen")
                st.markdown(f"🔸 **Valor actual del inventario:** ₡{total_inventario_num:,.2f}")
                st.markdown(f"🔸 **Ganancia generada en período:** ₡{total_ganancia:,.2f}")
                balance_total = total_ingresos - total_inventario_num
                st.markdown(f"🔸 **Balance estimado (ingresos - inventario):** ₡{balance_total:,.2f}")
            else:
                st.info("ℹ️ No hay ventas registradas en el rango seleccionado.")
    else:
        st.info("ℹ️ No hay ventas registradas.")





