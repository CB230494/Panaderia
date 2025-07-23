# === app.py - Parte 1 COMPLETA ===

import streamlit as st
from streamlit_option_menu import option_menu
from datetime import datetime
from pathlib import Path
import pandas as pd
from fpdf import FPDF
import unicodedata
from supabase import create_client, Client

# === CONFIGURACIÓN GENERAL ===
st.set_page_config(page_title="Panadería Moderna", layout="wide")

# === CONEXIÓN SUPABASE ===
SUPABASE_URL = "https://fuqenmijstetuwhdulax.supabase.co"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImZ1cWVubWlqc3RldHV3aGR1bGF4Iiwicm9sZSI6ImFub24iLCJpYXQiOjE3NTMyODM4MzksImV4cCI6MjA2ODg1OTgzOX0.9JdF70hcLCVCa0-lCd7yoSFKtO72niZbahM-u2ycAVg"
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

# === CREAR CARPETA DE IMÁGENES SI NO EXISTE ===
Path("imagenes_recetas").mkdir(exist_ok=True)

# === FUNCIÓN PARA LIMPIAR TEXTO PDF ===
def limpiar_texto(texto):
    if not texto:
        return ""
    return unicodedata.normalize("NFKD", str(texto)).encode("ASCII", "ignore").decode("ASCII")

# === GENERADOR DE PDF PARA RECETAS ===
def generar_pdf_receta(nombre, instrucciones, ingredientes, costo_total):
    pdf = FPDF()
    pdf.add_page()

    imagen_path = Path("imagenes_recetas") / f"{limpiar_texto(nombre).replace(' ', '_')}.jpg"
    if imagen_path.exists():
        try:
            pdf.image(str(imagen_path), x=10, y=10, w=40)
            pdf.set_xy(55, 15)
        except:
            pdf.set_y(20)
    else:
        pdf.set_y(20)

    pdf.set_font("Arial", "B", 14)
    pdf.cell(0, 10, txt=f"Receta: {limpiar_texto(nombre)}", ln=True)

    pdf.set_font("Arial", "", 12)
    pdf.cell(0, 10, txt=f"Costo total estimado: ₡{costo_total:,.2f}", ln=True)

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

    pdf.ln(5)
    pdf.set_font("Arial", "B", 12)
    pdf.cell(0, 10, txt="Instrucciones:", ln=True)

    pdf.set_font("Arial", "", 12)
    texto = instrucciones or "Sin instrucciones."
    for linea in texto.split('\n'):
        pdf.multi_cell(0, 8, limpiar_texto(linea))

    contenido = pdf.output(dest="S")
    try:
        return contenido.encode("latin-1")
    except UnicodeEncodeError:
        return limpiar_texto(contenido).encode("latin-1", errors="ignore")

# === ESTADO DE PÁGINA ===
if "pagina" not in st.session_state:
    st.session_state.pagina = "Inicio"

# === ESTILO PERSONALIZADO ===
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
            box-shadow: 4px 4px 10px rgba(0, 255, 204, 0.3);
            transition: all 0.2s ease-in-out;
        }
        .stButton>button:hover {
            background-color: #00e6b8 !important;
            box-shadow: 6px 6px 16px rgba(0, 255, 204, 0.5);
            transform: scale(1.02);
        }
        .stDataFrame th, .stDataFrame td {
            font-size: 18px !important;
        }
        .stSelectbox label, .stTextInput label, .stNumberInput label {
            font-size: 20px !important;
            color: #00ffcc;
        }
    </style>
""", unsafe_allow_html=True)

# === MENÚ LATERAL DE NAVEGACIÓN ===
with st.sidebar:
    st.session_state.pagina = option_menu(
        "Navegación",
        ["Inicio", "Productos", "Insumos", "Recetas", "Entradas/Salidas", "Ventas", "Balance"],
        icons=["house", "archive", "truck", "file-earmark-text", "arrow-left-right", "wallet", "graph-up"],
        menu_icon="list",
        default_index=["Inicio", "Productos", "Insumos", "Recetas", "Entradas/Salidas", "Ventas", "Balance"].index(st.session_state.pagina),
        styles={
            "container": {"padding": "5px", "background-color": "#121212"},
            "icon": {"color": "#00ffcc", "font-size": "20px"},
            "nav-link": {"color": "#ffffff", "font-size": "18px", "text-align": "left", "margin": "2px"},
            "nav-link-selected": {"background-color": "#00ffcc", "color": "#121212", "font-weight": "bold"},
        }
    )
# =============================
# 📦 PESTAÑA DE PRODUCTOS
# =============================
if st.session_state.pagina == "Productos":
    st.subheader("📦 Gestión de Productos")

    # === FUNCIONES CON SUPABASE ===
    def agregar_producto(nombre, unidad, precio, costo, stock):
        supabase.table("productos").insert({
            "nombre": nombre,
            "unidad": unidad,
            "precio_venta": precio,
            "costo": costo,
            "stock": stock
        }).execute()

    def obtener_productos():
        res = supabase.table("productos").select("*").order("id", desc=False).execute()
        return res.data if res.data else []

    def actualizar_producto(id_, nombre, unidad, precio, costo, stock):
        supabase.table("productos").update({
            "nombre": nombre,
            "unidad": unidad,
            "precio_venta": precio,
            "costo": costo,
            "stock": stock
        }).eq("id", id_).execute()

    def eliminar_producto(id_):
        supabase.table("productos").delete().eq("id", id_).execute()

    # === FORMULARIO AGREGAR ===
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
                agregar_producto(nombre, unidad, precio_venta, costo, stock)
                st.success(f"✅ Producto '{nombre}' agregado correctamente.")
                st.rerun()
            else:
                st.warning("⚠️ Debes completar todos los campos.")

    # === LISTA DE PRODUCTOS ===
    st.markdown("### 📋 Lista de productos")
    productos = obtener_productos()

    if productos:
        df = pd.DataFrame(productos)
        df["Ganancia (₡)"] = df["precio_venta"] - df["costo"]

        for col in ["precio_venta", "costo", "Ganancia (₡)"]:
            df[col] = df[col].map(lambda x: f"₡{int(x)}" if x == int(x) else f"₡{x:.2f}")

        def color_stock(val):
            return 'background-color: red; color: white' if val < 5 else ''

        styled_df = df.rename(columns={
            "nombre": "Nombre", "unidad": "Unidad", "precio_venta": "Precio Venta",
            "costo": "Costo", "stock": "Stock"
        }).style.applymap(color_stock, subset=["Stock"])

        st.dataframe(styled_df, use_container_width=True)

        # === EDITAR O ELIMINAR ===
        st.markdown("### ✏️ Editar o eliminar un producto")
        seleccion = st.selectbox("Seleccionar producto por nombre", [p["nombre"] for p in productos])

        producto = next(p for p in productos if p["nombre"] == seleccion)

        with st.form("form_editar_producto"):
            nuevo_nombre = st.text_input("Nombre", value=producto["nombre"])
            nueva_unidad = st.selectbox("Unidad", ["unidad", "porción", "pieza", "queque", "paquete"],
                                        index=["unidad", "porción", "pieza", "queque", "paquete"].index(producto["unidad"]))
            nuevo_precio = st.number_input("Precio de venta (₡)", value=float(producto["precio_venta"]), format="%.2f")
            nuevo_costo = st.number_input("Costo de elaboración (₡)", value=float(producto["costo"]), format="%.2f")
            nuevo_stock = st.number_input("Stock disponible", value=int(producto["stock"]), step=1)

            col1, col2 = st.columns(2)
            with col1:
                actualizar = st.form_submit_button("Actualizar")
            with col2:
                eliminar = st.form_submit_button("Eliminar")

            if actualizar:
                actualizar_producto(producto["id"], nuevo_nombre, nueva_unidad, nuevo_precio, nuevo_costo, nuevo_stock)
                st.success("✅ Producto actualizado correctamente.")
                st.rerun()
            if eliminar:
                eliminar_producto(producto["id"])
                st.success("🗑️ Producto eliminado correctamente.")
                st.rerun()
    else:
        st.info("ℹ️ No hay productos registrados todavía.")
# =============================
# 🚚 PESTAÑA DE INSUMOS
# =============================
if st.session_state.pagina == "Insumos":
    st.subheader("🚚 Gestión de Insumos")

    # === Diccionario de unidades legibles ===
    unidades_dict = {
        "Kilogramo (kg)": "kg",
        "Gramo (g)": "g",
        "Litro (l)": "l",
        "Mililitro (ml)": "ml",
        "Barra": "barra",
        "Unidad": "unidad"
    }

    unidad_legible = {v: k for k, v in unidades_dict.items()}

    # === FUNCIONES SUPABASE ===
    def agregar_insumo(nombre, unidad, costo_unitario, cantidad):
        supabase.table("insumos").insert({
            "nombre": nombre,
            "unidad": unidad,
            "costo_unitario": costo_unitario,
            "cantidad": cantidad
        }).execute()

    def obtener_insumos():
        res = supabase.table("insumos").select("*").order("id", desc=False).execute()
        return res.data if res.data else []

    def actualizar_insumo(id_, nombre, unidad, costo_unitario, cantidad):
        supabase.table("insumos").update({
            "nombre": nombre,
            "unidad": unidad,
            "costo_unitario": costo_unitario,
            "cantidad": cantidad
        }).eq("id", id_).execute()

    def eliminar_insumo(id_):
        supabase.table("insumos").delete().eq("id", id_).execute()

    # === FORMULARIO NUEVO INSUMO ===
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
                agregar_insumo(nombre_i, unidad_i, costo_unitario, cantidad)

                # Calcular precio base
                if unidad_i in ["kg", "l"]:
                    costo_base = costo_unitario / 1000
                    unidad_base = "gramo" if unidad_i == "kg" else "mililitro"
                else:
                    costo_base = costo_unitario
                    unidad_base = unidad_i

                st.success(
                    f"✅ '{nombre_i}' agregado correctamente. "
                    f"Cantidad: {cantidad} {unidad_i}, Costo total: ₡{costo_total:.2f}, "
                    f"₡{costo_unitario:.2f} por {unidad_i} → ₡{costo_base:.2f} por {unidad_base}"
                )
                st.rerun()
            else:
                st.warning("⚠️ Debes completar todos los campos y la cantidad debe ser mayor a cero.")

    # === LISTA DE INSUMOS ===
    st.markdown("### 📋 Lista de insumos")
    insumos = obtener_insumos()

    if insumos:
        df_i = pd.DataFrame(insumos)
        df_i["Unidad Mostrada"] = df_i["unidad"].map(unidad_legible)

        def calcular_precio_base(row):
            if row["unidad"] in ["kg", "l"]:
                return row["costo_unitario"] / 1000
            else:
                return row["costo_unitario"]

        df_i["₡ por unidad base"] = df_i.apply(calcular_precio_base, axis=1)
        df_i["₡ por unidad base"] = df_i["₡ por unidad base"].map(lambda x: f"₡{x:.2f}")

        df_i["Costo Total (₡)"] = df_i["costo_unitario"] * df_i["cantidad"]
        df_i["Costo Total (₡)"] = df_i["Costo Total (₡)"].map(lambda x: f"₡{x:,.2f}")
        df_i["costo_unitario"] = df_i["costo_unitario"].map(lambda x: f"₡{x:,.2f}")

        st.dataframe(df_i[["nombre", "Unidad Mostrada", "costo_unitario", "cantidad", "Costo Total (₡)", "₡ por unidad base"]].rename(columns={
            "nombre": "Nombre",
            "costo_unitario": "₡ x unidad",
            "cantidad": "Cantidad"
        }), use_container_width=True)

        # === EDITAR O ELIMINAR ===
        st.markdown("### ✏️ Editar o eliminar un insumo")
        seleccion_i = st.selectbox("Seleccionar insumo por nombre", [i["nombre"] for i in insumos])

        insumo = next(i for i in insumos if i["nombre"] == seleccion_i)
        unidad_visible_original = unidad_legible.get(insumo["unidad"], insumo["unidad"])
        costo_total_original = float(insumo["costo_unitario"]) * float(insumo["cantidad"])

        with st.form("form_editar_insumo"):
            nuevo_nombre_i = st.text_input("Nombre", value=insumo["nombre"])
            nueva_unidad_visible = st.selectbox("Unidad", list(unidades_dict.keys()),
                                                index=list(unidades_dict.keys()).index(unidad_visible_original))
            nueva_unidad = unidades_dict[nueva_unidad_visible]
            nueva_cantidad = st.number_input("Cantidad adquirida", value=float(insumo["cantidad"]))
            nuevo_costo_total = st.number_input("Costo total (₡)", value=costo_total_original, format="%.2f")

            col1, col2 = st.columns(2)
            with col1:
                actualizar_i = st.form_submit_button("Actualizar")
            with col2:
                eliminar_i = st.form_submit_button("Eliminar")

            if actualizar_i and nueva_cantidad > 0:
                nuevo_costo_unitario = nuevo_costo_total / nueva_cantidad
                actualizar_insumo(insumo["id"], nuevo_nombre_i, nueva_unidad, nuevo_costo_unitario, nueva_cantidad)
                st.success("✅ Insumo actualizado correctamente.")
                st.rerun()
            if eliminar_i:
                eliminar_insumo(insumo["id"])
                st.success("🗑️ Insumo eliminado correctamente.")
                st.rerun()
    else:
        st.info("ℹ️ No hay insumos registrados todavía.")
# =============================
# 📋 PESTAÑA DE RECETAS
# =============================
if st.session_state.pagina == "Recetas":
    st.subheader("📋 Gestión de Recetas")

    # === FUNCIONES SUPABASE ===
    def agregar_receta(nombre, instrucciones, insumos):
        # Insertar receta
        res = supabase.table("recetas").insert({
            "nombre": nombre,
            "instrucciones": instrucciones
        }).execute()
        receta_id = res.data[0]["id"]

        # Insertar ingredientes
        for insumo_id, cantidad in insumos:
            supabase.table("detalle_receta").insert({
                "receta_id": receta_id,
                "insumo_id": insumo_id,
                "cantidad": cantidad
            }).execute()

    def obtener_recetas():
        res = supabase.table("recetas").select("*").order("id", desc=False).execute()
        return res.data if res.data else []

    def obtener_detalle_receta(receta_id):
        detalle = supabase.table("detalle_receta").select("cantidad, insumo:insumo_id(nombre, unidad)").eq("receta_id", receta_id).execute()
        return [(d["insumo"]["nombre"], d["cantidad"], d["insumo"]["unidad"]) for d in detalle.data]

    def eliminar_receta(receta_id):
        supabase.table("detalle_receta").delete().eq("receta_id", receta_id).execute()
        supabase.table("recetas").delete().eq("id", receta_id).execute()

    def obtener_insumo_por_nombre(nombre):
        res = supabase.table("insumos").select("*").eq("nombre", nombre).execute()
        return res.data[0] if res.data else None

    insumos = obtener_insumos()

    with st.form("form_nueva_receta"):
        st.markdown("### ➕ Crear nueva receta")

        nombre_receta = st.text_input("📛 Nombre de la receta")
        instrucciones = st.text_area("📖 Instrucciones de preparación")
        imagen_receta = st.file_uploader("📷 Foto del producto final (opcional)", type=["png", "jpg", "jpeg"])

        insumo_seleccionado = []
        if not insumos:
            st.warning("⚠️ No hay insumos registrados. Agrega insumos primero.")
        else:
            st.markdown("### 🧺 Seleccionar ingredientes:")
            for insumo in insumos:
                insumo_id, nombre, unidad = insumo["id"], insumo["nombre"], insumo["unidad"]
                cantidad = st.number_input(f"{nombre} ({unidad})", min_value=0.0, step=0.1, key=f"nuevo_{insumo_id}")
                if cantidad > 0:
                    insumo_seleccionado.append((insumo_id, cantidad))

        submitted_receta = st.form_submit_button("🍽️ Guardar receta")

        if submitted_receta:
            if not nombre_receta or not insumo_seleccionado:
                st.warning("⚠️ Debes ingresar un nombre y al menos un insumo.")
            else:
                agregar_receta(nombre_receta, instrucciones, insumo_seleccionado)
                if imagen_receta:
                    carpeta = Path("imagenes_recetas")
                    nombre_archivo = f"{nombre_receta.replace(' ', '_')}.jpg"
                    with open(carpeta / nombre_archivo, "wb") as f:
                        f.write(imagen_receta.read())
                st.success(f"✅ Receta '{nombre_receta}' guardada correctamente.")
                st.rerun()

    st.markdown("### 📋 Recetas registradas")
    recetas = obtener_recetas()

    if recetas:
        insumos_db = {i["nombre"]: i for i in insumos}
        for receta in recetas:
            receta_id, nombre, instrucciones = receta["id"], receta["nombre"], receta.get("instrucciones", "")
            detalles = obtener_detalle_receta(receta_id)

            desglose = []
            costo_total = 0

            for nombre_insumo, cantidad, unidad in detalles:
                insumo = insumos_db.get(nombre_insumo)
                if not insumo:
                    continue

                costo_unitario = insumo["costo_unitario"]
                unidad_insumo = insumo["unidad"]

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
                ruta_img = Path("imagenes_recetas") / f"{nombre.replace(' ', '_')}.jpg"
                if ruta_img.exists():
                    st.image(str(ruta_img), caption=f"📷 {nombre}", width=300)

                st.markdown(f"**📝 Instrucciones:** {instrucciones or 'Sin instrucciones.'}")
                st.markdown("**🧾 Ingredientes:**")
                for nombre_i, cant_i, unidad_i, costo_u, subtotal in desglose:
                    st.markdown(
                        f"- {nombre_i} — {cant_i:.2f} {unidad_i} — "
                        f"(₡{costo_u:.2f} c/u → Subtotal: ₡{subtotal:,.2f})"
                    )

                col1, col2 = st.columns(2)
                with col1:
                    if st.button(f"🗑️ Eliminar receta", key=f"eliminar_{receta_id}"):
                        eliminar_receta(receta_id)
                        if ruta_img.exists():
                            ruta_img.unlink()
                        st.success(f"🗑️ Receta '{nombre}' eliminada.")
                        st.rerun()
                with col2:
                    if st.button("📤 Exportar PDF", key=f"exportar_{receta_id}"):
                        contenido_pdf = generar_pdf_receta(nombre, instrucciones, desglose, costo_total)
                        st.download_button(
                            label="📥 Descargar PDF",
                            data=contenido_pdf,
                            file_name=f"{nombre.replace(' ', '_')}.pdf",
                            mime="application/pdf"
                        )
    else:
        st.info("ℹ️ No hay recetas registradas todavía.")
# =============================
# 📤 PESTAÑA DE ENTRADAS Y SALIDAS
# =============================
if st.session_state.pagina == "Entradas/Salidas":
    st.subheader("📤 Registro de Entradas y Salidas de Insumos")

    # === FUNCIONES SUPABASE ===
    def registrar_movimiento(insumo_id, tipo, cantidad, fecha_hora, motivo):
        # Guardar movimiento
        supabase.table("movimientos").insert({
            "insumo_id": insumo_id,
            "tipo": tipo,
            "cantidad": cantidad,
            "fecha_hora": fecha_hora,
            "motivo": motivo
        }).execute()

        # Actualizar inventario
        operacion = "+" if tipo == "Entrada" else "-"
        insumo = supabase.table("insumos").select("*").eq("id", insumo_id).execute().data[0]
        nueva_cantidad = insumo["cantidad"] + cantidad if tipo == "Entrada" else insumo["cantidad"] - cantidad
        supabase.table("insumos").update({"cantidad": nueva_cantidad}).eq("id", insumo_id).execute()

    def obtener_historial_movimientos():
        res = supabase.table("movimientos").select("id, cantidad, tipo, fecha_hora, motivo, insumo:insumo_id(nombre)").order("fecha_hora", desc=True).execute()
        return [{
            "ID": m["id"],
            "Insumo": m["insumo"]["nombre"],
            "Tipo": m["tipo"],
            "Cantidad": m["cantidad"],
            "Fecha y Hora": m["fecha_hora"],
            "Motivo": m["motivo"]
        } for m in res.data]

    unidad_legible = {
        "kg": "kilogramos",
        "g": "gramos",
        "l": "litros",
        "ml": "mililitros",
        "barra": "barras",
        "unidad": "unidades"
    }

    insumos = obtener_insumos()
    if not insumos:
        st.warning("⚠️ No hay insumos disponibles. Registra insumos primero.")
        st.stop()

    nombres_insumos = [f"{i['nombre']} ({unidad_legible.get(i['unidad'], i['unidad'])})" for i in insumos]
    insumo_elegido = st.selectbox("🔽 Selecciona el insumo", nombres_insumos)

    index = nombres_insumos.index(insumo_elegido)
    insumo = insumos[index]
    unidad_visible = unidad_legible.get(insumo["unidad"], insumo["unidad"])

    st.markdown(
        f"<div style='font-size:20px; font-weight:bold; color:#ffa500;'>📦 Cantidad disponible: "
        f"{insumo['cantidad']:.2f} {unidad_visible}</div>", unsafe_allow_html=True
    )

    tipo_movimiento = st.radio("📌 Tipo de movimiento", ["Entrada", "Salida"], horizontal=True)
    cantidad = st.number_input("📏 Cantidad a registrar", min_value=0.0, step=0.1)
    motivo = st.text_input("✏️ Motivo (opcional)")
    registrar = st.button("💾 Registrar movimiento")

    if registrar:
        if tipo_movimiento == "Salida" and cantidad > insumo["cantidad"]:
            st.error("❌ No hay suficiente stock para realizar la salida.")
        else:
            fecha_hora = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            registrar_movimiento(insumo["id"], tipo_movimiento, cantidad, fecha_hora, motivo)
            st.success(f"✅ {tipo_movimiento} registrada correctamente.")
            st.rerun()

    # === HISTORIAL DE MOVIMIENTOS ===
    historial = obtener_historial_movimientos()
    if historial:
        st.markdown("### 📜 Historial de Movimientos")
        df_hist = pd.DataFrame(historial)
        df_hist["Fecha y Hora"] = pd.to_datetime(df_hist["Fecha y Hora"]).dt.strftime("%d/%m/%Y")
        df_hist["Cantidad"] = df_hist["Cantidad"].apply(lambda x: f"{x:.2f}")
        df_hist = df_hist.drop(columns=["ID"])

        def colorear_tipo(val):
            color = 'green' if val == "Entrada" else 'red'
            return f'color: {color}; font-weight: bold'

        st.dataframe(df_hist.style.applymap(colorear_tipo, subset=["Tipo"]), use_container_width=True)

    # === INSUMOS CON STOCK BAJO ===
    st.markdown("### 🚨 Insumos con stock bajo")
    bajo_stock = [i for i in insumos if i["cantidad"] < 3]
    if bajo_stock:
        df_bajo = pd.DataFrame(bajo_stock)
        df_bajo["unidad"] = df_bajo["unidad"].map(unidad_legible)
        df_bajo["₡ x unidad"] = df_bajo["costo_unitario"].apply(lambda x: f"₡{x:,.2f}")
        df_bajo["cantidad"] = df_bajo["cantidad"].apply(lambda x: f"{x:.2f}")
        df_bajo = df_bajo.rename(columns={
            "nombre": "Nombre", "unidad": "Unidad", "cantidad": "Cantidad disponible"
        })
        st.warning("⚠️ Tienes insumos con menos de 3 unidades.")
        st.dataframe(df_bajo[["Nombre", "Unidad", "₡ x unidad", "Cantidad disponible"]].style.highlight_max(axis=0, color="salmon"), use_container_width=True)
    else:
        st.success("✅ Todos los insumos tienen suficiente stock.")
# =============================
# 💰 PESTAÑA DE VENTAS
# =============================
if st.session_state.pagina == "Ventas":
    st.subheader("💰 Registro de Ventas de Productos")

    # === FUNCIONES ===
    def registrar_venta_en_db(producto, unidad, cantidad, ingreso, costo, ganancia, fecha):
        supabase.table("ventas").insert({
            "producto": producto,
            "unidad": unidad,
            "cantidad": cantidad,
            "ingreso": ingreso,
            "costo": costo,
            "ganancia": ganancia,
            "fecha": fecha
        }).execute()

    def obtener_ventas():
        res = supabase.table("ventas").select("*").order("fecha", desc=True).execute()
        return res.data if res.data else []

    def actualizar_venta(venta_id, cantidad, ingreso, costo, ganancia):
        supabase.table("ventas").update({
            "cantidad": cantidad,
            "ingreso": ingreso,
            "costo": costo,
            "ganancia": ganancia
        }).eq("id", venta_id).execute()

    def eliminar_venta(venta_id):
        supabase.table("ventas").delete().eq("id", venta_id).execute()

    productos = obtener_productos()
    if not productos:
        st.warning("⚠️ No hay productos disponibles. Agrega primero desde la pestaña de Productos.")
    else:
        nombres_productos = [f"{p['nombre']} ({p['unidad']})" for p in productos]
        producto_elegido = st.selectbox("🧁 Selecciona el producto vendido", nombres_productos)

        index = nombres_productos.index(producto_elegido)
        p = productos[index]

        st.markdown(f"**💵 Precio de venta:** ₡{p['precio_venta']:,.2f}")
        st.markdown(f"**🧾 Costo de elaboración:** ₡{p['costo']:,.2f}")
        st.markdown(f"**📦 Stock disponible:** {p['stock']:.2f} {p['unidad']}")

        cantidad_vendida = st.number_input("📏 Cantidad vendida", min_value=0.0, step=0.1)
        registrar_venta = st.button("💾 Registrar venta")

        if registrar_venta:
            if cantidad_vendida <= 0:
                st.warning("⚠️ Debes ingresar una cantidad mayor a cero.")
            elif cantidad_vendida > p['stock']:
                st.error("❌ No puedes vender más de lo que tienes en stock.")
            else:
                ingreso_total = round(cantidad_vendida * p['precio_venta'], 2)
                costo_total = round(cantidad_vendida * p['costo'], 2)
                ganancia_total = round(ingreso_total - costo_total, 2)
                fecha_actual = datetime.now().strftime("%Y-%m-%d")

                registrar_venta_en_db(p['nombre'], p['unidad'], cantidad_vendida, ingreso_total, costo_total, ganancia_total, fecha_actual)

                # Actualizar stock
                nuevo_stock = p['stock'] - cantidad_vendida
                actualizar_producto(p["id"], p["nombre"], p["unidad"], p["precio_venta"], p["costo"], nuevo_stock)

                st.success("✅ Venta registrada correctamente.")
                st.rerun()

    # === HISTORIAL DE VENTAS ===
    ventas = obtener_ventas()
    if ventas:
        st.markdown("### 📋 Historial de ventas")
        df_ventas = pd.DataFrame(ventas)
        df_ventas["cantidad"] = df_ventas["cantidad"].map(lambda x: f"{x:.2f}")
        df_ventas["ingreso"] = df_ventas["ingreso"].map(lambda x: f"₡{x:,.2f}")
        df_ventas["costo"] = df_ventas["costo"].map(lambda x: f"₡{x:,.2f}")
        df_ventas["ganancia"] = df_ventas["ganancia"].map(lambda x: f"₡{x:,.2f}")
        df_ventas["fecha"] = pd.to_datetime(df_ventas["fecha"]).dt.strftime("%d/%m/%Y")

        st.dataframe(df_ventas.drop(columns=["id"]), use_container_width=True)

        total_ingresos = sum(float(v["ingreso"].replace("₡", "").replace(",", "")) for v in df_ventas.to_dict("records"))
        total_ganancias = sum(float(v["ganancia"].replace("₡", "").replace(",", "")) for v in df_ventas.to_dict("records"))

        st.markdown(f"**💵 Total ingresos:** ₡{total_ingresos:,.2f}")
        st.markdown(f"**📈 Total ganancias:** ₡{total_ganancias:,.2f}")

        # Producto estrella
        df_crudo = pd.DataFrame(ventas)
        producto_estrella = df_crudo.groupby("producto")["cantidad"].sum().idxmax()
        cantidad_estrella = df_crudo.groupby("producto")["cantidad"].sum().max()
        st.success(f"🌟 Producto estrella: **{producto_estrella}** con **{cantidad_estrella:.2f}** unidades vendidas")

        # Editar o eliminar
        st.markdown("### ✏️ Editar o eliminar una venta")
        ids_ventas = [f"{v['id']} - {v['producto']} ({v['cantidad']:.2f})" for v in ventas]
        seleccion_id = st.selectbox("Selecciona una venta", ids_ventas)

        venta_id = int(seleccion_id.split(" - ")[0])
        venta = next(v for v in ventas if v["id"] == venta_id)

        nueva_cantidad = st.number_input("Nueva cantidad vendida", min_value=0.1, value=float(venta["cantidad"]), step=0.1)
        col1, col2 = st.columns(2)
        with col1:
            if st.button("Actualizar venta"):
                p = next(p for p in productos if p["nombre"] == venta["producto"])
                nuevo_ingreso = round(nueva_cantidad * p["precio_venta"], 2)
                nuevo_costo = round(nueva_cantidad * p["costo"], 2)
                nueva_ganancia = round(nuevo_ingreso - nuevo_costo, 2)

                actualizar_venta(venta_id, nueva_cantidad, nuevo_ingreso, nuevo_costo, nueva_ganancia)
                st.success("✅ Venta actualizada correctamente.")
                st.rerun()
        with col2:
            if st.button("Eliminar venta"):
                eliminar_venta(venta_id)
                st.success("🗑️ Venta eliminada correctamente.")
                st.rerun()
    else:
        st.info("ℹ️ Aún no hay ventas registradas.")
# =============================
# 📊 PESTAÑA DE BALANCE
# =============================
if st.session_state.pagina == "Balance":
    st.subheader("📊 Balance General del Negocio")

    st.markdown("### 📅 Selecciona un rango de fechas")
    col1, col2 = st.columns(2)
    with col1:
        fecha_inicio = st.date_input("Desde", value=datetime.today().replace(day=1))
    with col2:
        fecha_fin = st.date_input("Hasta", value=datetime.today())

    # === Inventario de Insumos ===
    insumos = obtener_insumos()
    if insumos:
        df_insumos = pd.DataFrame(insumos)
        unidad_legible = {
            "kg": "kilogramos",
            "g": "gramos",
            "l": "litros",
            "ml": "mililitros",
            "barra": "barras",
            "unidad": "unidades"
        }

        df_insumos["Unidad"] = df_insumos["unidad"].map(unidad_legible)
        df_insumos["Total (₡)"] = df_insumos["costo_unitario"] * df_insumos["cantidad"]
        df_insumos["Costo Unitario"] = df_insumos["costo_unitario"].apply(lambda x: f"₡{x:,.2f}")
        df_insumos["Total (₡)"] = df_insumos["Total (₡)"].apply(lambda x: f"₡{x:,.2f}")
        total_inventario = sum(i["costo_unitario"] * i["cantidad"] for i in insumos)

        st.markdown("### 📦 Valor del inventario de insumos")
        st.dataframe(df_insumos[["nombre", "Unidad", "cantidad", "Costo Unitario", "Total (₡)"]].rename(columns={
            "nombre": "Nombre", "cantidad": "Cantidad"
        }), use_container_width=True)
        st.markdown(f"**🔹 Total inventario:** ₡{total_inventario:,.2f}")
    else:
        st.info("ℹ️ No hay insumos registrados.")

    st.divider()

    # === Ventas filtradas ===
    st.markdown("### 💰 Ventas registradas en el período")
    ventas = obtener_ventas()
    if ventas:
        df_ventas = pd.DataFrame(ventas)
        df_ventas["fecha"] = pd.to_datetime(df_ventas["fecha"])
        df_filtrado = df_ventas[
            (df_ventas["fecha"] >= pd.to_datetime(fecha_inicio)) &
            (df_ventas["fecha"] <= pd.to_datetime(fecha_fin))
        ]

        if not df_filtrado.empty:
            total_ingresos = df_filtrado["ingreso"].sum()
            total_costos = df_filtrado["costo"].sum()
            total_ganancia = df_filtrado["ganancia"].sum()

            df_filtrado["fecha"] = df_filtrado["fecha"].dt.strftime("%d/%m/%Y")
            df_filtrado["cantidad"] = df_filtrado["cantidad"].apply(lambda x: f"{x:.2f}")
            df_filtrado["ingreso"] = df_filtrado["ingreso"].apply(lambda x: f"₡{x:,.2f}")
            df_filtrado["costo"] = df_filtrado["costo"].apply(lambda x: f"₡{x:,.2f}")
            df_filtrado["ganancia"] = df_filtrado["ganancia"].apply(lambda x: f"₡{x:,.2f}")

            st.dataframe(df_filtrado.drop(columns=["id"]), use_container_width=True)
            st.markdown(f"- **🟢 Ingresos:** ₡{total_ingresos:,.2f}")
            st.markdown(f"- **🧾 Costos:** ₡{total_costos:,.2f}")
            st.markdown(f"- **📈 Ganancia total:** ₡{total_ganancia:,.2f}")

            st.divider()
            st.markdown("### 📉 Comparativo resumen")
            st.markdown(f"🔸 **Valor actual del inventario:** ₡{total_inventario:,.2f}")
            st.markdown(f"🔸 **Ganancia generada en período:** ₡{total_ganancia:,.2f}")
            balance_total = total_ingresos - total_inventario
            st.markdown(f"🔸 **Balance estimado (ingresos - inventario):** ₡{balance_total:,.2f}")
        else:
            st.info("ℹ️ No hay ventas registradas en el rango seleccionado.")
    else:
        st.info("ℹ️ No hay ventas registradas.")


