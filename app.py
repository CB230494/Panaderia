# === IMPORTACIONES BASE ===
import streamlit as st
from streamlit_option_menu import option_menu
import pandas as pd
from pathlib import Path
from datetime import datetime
from fpdf import FPDF
import unicodedata
from supabase import create_client

# === CONEXIÓN SUPABASE ===
SUPABASE_URL = "https://fuqenmijstetuwhdulax.supabase.co"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImZ1cWVubWlqc3RldHV3aGR1bGF4Iiwicm9sZSI6ImFub24iLCJpYXQiOjE3NTMyODM4MzksImV4cCI6MjA2ODg1OTgzOX0.9JdF70hcLCVCa0-lCd7yoSFKtO72niZbahM-u2ycAVg"
supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

# === CONFIGURACIÓN GENERAL ===
st.set_page_config(page_title="📊 Panadería Moderna", page_icon="🍞", layout="wide")

# === FUNCIÓN: LIMPIAR TEXTO (PDF) ===
def limpiar_texto(texto):
    if not texto:
        return ""
    return unicodedata.normalize("NFKD", str(texto)).encode("ASCII", "ignore").decode("ASCII")

# === FUNCIÓN: GENERAR PDF DE RECETA ===
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
        linea = f"- {nombre_insumo}: {cantidad:.2f} {unidad} (₡{costo_unitario:.2f} → Subtotal: ₡{subtotal:,.2f})"
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

# === INICIALIZAR SESIÓN DE NAVEGACIÓN ===
if "pagina_activa" not in st.session_state:
    st.session_state.pagina_activa = "Inicio"
# === ESTILO PERSONALIZADO PROFESIONAL ===
st.markdown("""
    <style>
        body, .main { background-color: #1c1c1c; color: white; }
        h1, h2, h3 { color: #00e6c3; }
        .stButton>button {
            background-color: #00e6c3 !important;
            color: black !important;
            font-weight: bold;
            font-size: 20px;
            border-radius: 12px;
            padding: 12px 24px;
            border: none;
            box-shadow: 2px 2px 8px rgba(0, 255, 204, 0.3);
            transition: all 0.2s ease-in-out;
        }
        .stButton>button:hover {
            background-color: #00ccb0 !important;
            box-shadow: 4px 4px 12px rgba(0, 255, 204, 0.5);
            transform: scale(1.03);
        }
        .stSelectbox label, .stTextInput label, .stNumberInput label, .stRadio label {
            color: #00e6c3 !important;
            font-weight: bold;
        }
        .stDataFrame { font-size: 18px; }
        .block-container { padding-top: 2rem; }
    </style>
""", unsafe_allow_html=True)

# === MENÚ DE NAVEGACIÓN LATERAL ===
with st.sidebar:
    pagina = option_menu(
        menu_title="Menú Principal 🍞",
        options=["Inicio", "Productos", "Insumos", "Recetas", "Entradas/Salidas", "Ventas", "Balance"],
        icons=["house", "box", "truck", "clipboard", "arrow-left-right", "coin", "bar-chart-line"],
        menu_icon="list",
        default_index=["Inicio", "Productos", "Insumos", "Recetas", "Entradas/Salidas", "Ventas", "Balance"].index(st.session_state.pagina_activa),
        styles={
            "container": {"padding": "5px", "background-color": "#1c1c1c"},
            "icon": {"color": "#00e6c3", "font-size": "20px"},
            "nav-link": {"color": "#ffffff", "font-size": "18px", "text-align": "left", "margin": "2px"},
            "nav-link-selected": {"background-color": "#00e6c3", "color": "#1c1c1c", "font-weight": "bold"},
        }
    )
    st.session_state.pagina_activa = pagina  # Actualizar automáticamente sin doble clic

# === PÁGINA DE INICIO ===
if st.session_state.pagina_activa == "Inicio":
    st.title("📊 Sistema de Gestión - Panadería Moderna")
    st.markdown("Bienvenido al panel de control. Elige una sección desde el menú lateral.")

    st.markdown("### Accesos rápidos")
    col1, col2, col3 = st.columns(3)
    with col1:
        if st.button("📦 Ir a Productos"):
            st.session_state.pagina_activa = "Productos"
            st.experimental_rerun()
    with col2:
        if st.button("🚚 Ir a Insumos"):
            st.session_state.pagina_activa = "Insumos"
            st.experimental_rerun()
    with col3:
        if st.button("📋 Ir a Recetas"):
            st.session_state.pagina_activa = "Recetas"
            st.experimental_rerun()

    col4, col5, col6 = st.columns(3)
    with col4:
        if st.button("🔄 Ir a Entradas/Salidas"):
            st.session_state.pagina_activa = "Entradas/Salidas"
            st.experimental_rerun()
    with col5:
        if st.button("💵 Ir a Ventas"):
            st.session_state.pagina_activa = "Ventas"
            st.experimental_rerun()
    with col6:
        if st.button("📈 Ir a Balance"):
            st.session_state.pagina_activa = "Balance"
            st.experimental_rerun()
# === PRODUCTOS ===
if st.session_state.pagina_activa == "Productos":
    st.header("📦 Gestión de Productos")

    with st.form("form_agregar_producto"):
        st.subheader("➕ Agregar nuevo producto")
        nombre = st.text_input("Nombre del producto")
        unidad = st.selectbox("Unidad", ["unidad", "porción", "pieza", "queque", "paquete"])
        precio_venta = st.number_input("Precio de venta (₡)", min_value=0.0, format="%.2f")
        costo = st.number_input("Costo de elaboración (₡)", min_value=0.0, format="%.2f")
        stock = st.number_input("Cantidad en stock", min_value=0, step=1)
        submitted = st.form_submit_button("Agregar")

        if submitted:
            if nombre and unidad:
                supabase.table("productos").insert({
                    "nombre": nombre,
                    "unidad": unidad,
                    "precio_venta": precio_venta,
                    "costo": costo,
                    "stock": stock
                }).execute()
                st.success(f"✅ Producto '{nombre}' agregado correctamente.")
                st.experimental_rerun()
            else:
                st.warning("⚠️ Debes completar todos los campos.")

    st.subheader("📋 Lista de productos")
    datos = supabase.table("productos").select("*").order("id", desc=False).execute()
    productos = datos.data if datos.data else []

    if productos:
        df = pd.DataFrame(productos)
        df["Ganancia"] = df["precio_venta"] - df["costo"]

        df["Precio Venta"] = df["precio_venta"].map(lambda x: f"₡{x:,.2f}")
        df["Costo"] = df["costo"].map(lambda x: f"₡{x:,.2f}")
        df["Ganancia"] = df["Ganancia"].map(lambda x: f"₡{x:,.2f}")

        def estilo_stock(val): return 'background-color: red; color: white' if val < 5 else ''
        styled_df = df.rename(columns={
            "nombre": "Nombre", "unidad": "Unidad", "Precio Venta": "Precio Venta",
            "Costo": "Costo", "stock": "Stock", "Ganancia": "Ganancia"
        }).style.applymap(estilo_stock, subset=["stock"])

        st.dataframe(styled_df, use_container_width=True)

        st.subheader("✏️ Editar o eliminar producto")
        nombres_disponibles = [p["nombre"] for p in productos]
        seleccion = st.selectbox("Selecciona un producto", nombres_disponibles)

        producto = next((p for p in productos if p["nombre"] == seleccion), None)
        if producto:
            id_producto = producto["id"]
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
                    supabase.table("productos").update({
                        "nombre": nuevo_nombre,
                        "unidad": nueva_unidad,
                        "precio_venta": nuevo_precio,
                        "costo": nuevo_costo,
                        "stock": nuevo_stock
                    }).eq("id", id_producto).execute()
                    st.success("✅ Producto actualizado.")
                    st.experimental_rerun()

                if eliminar:
                    supabase.table("productos").delete().eq("id", id_producto).execute()
                    st.success("🗑️ Producto eliminado.")
                    st.experimental_rerun()
    else:
        st.info("ℹ️ No hay productos registrados.")
# === INSUMOS ===
if st.session_state.pagina_activa == "Insumos":
    st.header("🚚 Gestión de Insumos")

    unidades_dict = {
        "Kilogramo (kg)": "kg",
        "Gramo (g)": "g",
        "Litro (l)": "l",
        "Mililitro (ml)": "ml",
        "Barra": "barra",
        "Unidad": "unidad"
    }

    with st.form("form_agregar_insumo"):
        st.subheader("➕ Agregar nuevo insumo")
        nombre_i = st.text_input("Nombre del insumo")
        unidad_i_visible = st.selectbox("Unidad", list(unidades_dict.keys()))
        unidad_i = unidades_dict[unidad_i_visible]
        cantidad = st.number_input("Cantidad adquirida", min_value=0.0)
        costo_total = st.number_input("Costo total (₡)", min_value=0.0, format="%.2f")
        submitted_i = st.form_submit_button("Agregar")

        if submitted_i:
            if nombre_i and cantidad > 0 and costo_total > 0:
                costo_unitario = costo_total / cantidad
                supabase.table("insumos").insert({
                    "nombre": nombre_i,
                    "unidad": unidad_i,
                    "costo_unitario": costo_unitario,
                    "cantidad": cantidad
                }).execute()

                if unidad_i in ["kg", "l"]:
                    costo_base = costo_unitario / 1000
                    unidad_base = "gramo" if unidad_i == "kg" else "mililitro"
                else:
                    costo_base = costo_unitario
                    unidad_base = unidad_i

                st.success(
                    f"✅ '{nombre_i}' agregado correctamente. "
                    f"₡{costo_unitario:.2f} por {unidad_i} → ₡{costo_base:.2f} por {unidad_base}"
                )
                st.experimental_rerun()
            else:
                st.warning("⚠️ Completa todos los campos con valores válidos.")

    st.subheader("📋 Lista de insumos")
    datos = supabase.table("insumos").select("*").execute()
    insumos = datos.data if datos.data else []

    if insumos:
        df_i = pd.DataFrame(insumos)
        unidad_legible = {v: k for k, v in unidades_dict.items()}
        df_i["Unidad Mostrada"] = df_i["unidad"].map(unidad_legible)

        def precio_base(row):
            return row["costo_unitario"] / 1000 if row["unidad"] in ["kg", "l"] else row["costo_unitario"]

        df_i["₡ por unidad base"] = df_i.apply(precio_base, axis=1).map(lambda x: f"₡{x:.2f}")
        df_i["Costo Total (₡)"] = (df_i["costo_unitario"] * df_i["cantidad"]).map(lambda x: f"₡{x:,.2f}")
        df_i["Costo Unitario"] = df_i["costo_unitario"].map(lambda x: f"₡{x:,.2f}")

        st.dataframe(df_i.rename(columns={
            "nombre": "Nombre",
            "Unidad Mostrada": "Unidad",
            "Costo Unitario": "₡ x unidad",
            "cantidad": "Cantidad",
            "Costo Total (₡)": "Total",
            "₡ por unidad base": "₡ base"
        })[["Nombre", "Unidad", "₡ x unidad", "Cantidad", "Total", "₡ base"]], use_container_width=True)

        st.subheader("✏️ Editar o eliminar un insumo")
        nombres_insumos = [i["nombre"] for i in insumos]
        seleccion_i = st.selectbox("Seleccionar insumo", nombres_insumos)

        insumo = next(i for i in insumos if i["nombre"] == seleccion_i)
        unidad_visible_original = [k for k, v in unidades_dict.items() if v == insumo["unidad"]][0]
        costo_total_original = float(insumo["costo_unitario"]) * float(insumo["cantidad"])

        with st.form("form_editar_insumo"):
            nuevo_nombre_i = st.text_input("Nombre", value=insumo["nombre"])
            nueva_unidad_visible = st.selectbox("Unidad", list(unidades_dict.keys()),
                                                index=list(unidades_dict.keys()).index(unidad_visible_original))
            nueva_unidad = unidades_dict[nueva_unidad_visible]
            nueva_cantidad = st.number_input("Cantidad adquirida", value=float(insumo["cantidad"]))
            nuevo_costo_total = st.number_input("Costo total (₡)", value=float(costo_total_original), format="%.2f")

            col1, col2 = st.columns(2)
            with col1:
                actualizar_i = st.form_submit_button("Actualizar")
            with col2:
                eliminar_i = st.form_submit_button("Eliminar")

            if actualizar_i and nueva_cantidad > 0:
                nuevo_costo_unitario = nuevo_costo_total / nueva_cantidad
                supabase.table("insumos").update({
                    "nombre": nuevo_nombre_i,
                    "unidad": nueva_unidad,
                    "cantidad": nueva_cantidad,
                    "costo_unitario": nuevo_costo_unitario
                }).eq("id", insumo["id"]).execute()
                st.success("✅ Insumo actualizado.")
                st.experimental_rerun()

            if eliminar_i:
                supabase.table("insumos").delete().eq("id", insumo["id"]).execute()
                st.success("🗑️ Insumo eliminado.")
                st.experimental_rerun()
    else:
        st.info("ℹ️ No hay insumos registrados.")
# === RECETAS ===
if st.session_state.pagina_activa == "Recetas":
    st.header("📋 Gestión de Recetas")

    # === CREAR NUEVA RECETA ===
    with st.form("form_nueva_receta"):
        st.subheader("➕ Crear nueva receta")
        nombre_receta = st.text_input("📛 Nombre de la receta")
        instrucciones = st.text_area("📖 Instrucciones de preparación")
        imagen_receta = st.file_uploader("📷 Foto del producto final (opcional)", type=["jpg", "jpeg", "png"])

        insumos = supabase.table("insumos").select("*").execute().data
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
                st.warning("⚠️ Ingresa nombre y al menos un ingrediente.")
            else:
                receta_res = supabase.table("recetas").insert({
                    "nombre": nombre_receta,
                    "instrucciones": instrucciones
                }).execute()
                receta_id = receta_res.data[0]["id"]

                for insumo_id, cantidad in insumo_seleccionado:
                    supabase.table("detalle_receta").insert({
                        "receta_id": receta_id,
                        "insumo_id": insumo_id,
                        "cantidad": cantidad
                    }).execute()

                if imagen_receta:
                    Path("imagenes_recetas").mkdir(exist_ok=True)
                    nombre_archivo = f"{nombre_receta.replace(' ', '_')}.jpg"
                    with open(f"imagenes_recetas/{nombre_archivo}", "wb") as f:
                        f.write(imagen_receta.read())

                st.success(f"✅ Receta '{nombre_receta}' guardada correctamente.")
                st.experimental_rerun()

    st.subheader("📚 Recetas registradas")
    recetas = supabase.table("recetas").select("*").execute().data
    if recetas:
        for receta in recetas:
            receta_id = receta["id"]
            nombre = receta["nombre"]
            instrucciones = receta.get("instrucciones", "")

            detalles = supabase.table("detalle_receta").select("*, insumos(nombre,unidad,costo_unitario)").eq("receta_id", receta_id).execute().data

            desglose = []
            costo_total = 0
            for item in detalles:
                insumo = item["insumos"]
                nombre_insumo = insumo["nombre"]
                unidad = insumo["unidad"]
                costo_unitario = insumo["costo_unitario"]
                cantidad = item["cantidad"]

                costo_por_base = costo_unitario / 1000 if unidad in ["kg", "l"] else costo_unitario
                cantidad_en_base = cantidad * 1000 if unidad in ["kg", "l"] else cantidad
                subtotal = cantidad_en_base * costo_por_base
                costo_total += subtotal
                desglose.append((nombre_insumo, cantidad, unidad, costo_por_base, subtotal))

            with st.expander(f"🍰 {nombre} — Costo total estimado: ₡{costo_total:,.2f}"):
                ruta_img = Path("imagenes_recetas") / f"{nombre.replace(' ', '_')}.jpg"
                if ruta_img.exists():
                    st.image(str(ruta_img), caption="📷 Imagen referencial", width=300)

                st.markdown(f"**📖 Instrucciones:**\n{instrucciones or 'Sin instrucciones.'}")
                st.markdown("**🧾 Ingredientes:**")
                for nombre_i, cant_i, unidad_i, costo_u, subtotal in desglose:
                    st.markdown(f"- {nombre_i}: {cant_i:.2f} {unidad_i} → ₡{subtotal:,.2f}")

                col1, col2, col3 = st.columns([1, 1, 2])
                with col1:
                    if st.button("🗑️ Eliminar", key=f"eliminar_{receta_id}"):
                        supabase.table("detalle_receta").delete().eq("receta_id", receta_id).execute()
                        supabase.table("recetas").delete().eq("id", receta_id).execute()
                        if ruta_img.exists():
                            ruta_img.unlink()
                        st.success("🗑️ Receta eliminada.")
                        st.experimental_rerun()
                with col2:
                    if st.button("✏️ Editar", key=f"editar_{receta_id}"):
                        st.session_state[f"editando_{receta_id}"] = True
                with col3:
                    if st.button("📄 Generar PDF", key=f"pdf_{receta_id}"):
                        contenido = generar_pdf_receta(nombre, instrucciones, desglose, costo_total)
                        st.download_button(label="📥 Descargar PDF",
                                           data=contenido,
                                           file_name=f"Receta_{nombre.replace(' ', '_')}.pdf",
                                           mime="application/pdf")

            # === FORMULARIO DE EDICIÓN ===
            if st.session_state.get(f"editando_{receta_id}", False):
                with st.form(f"form_edit_receta_{receta_id}"):
                    nuevo_nombre = st.text_input("📛 Nuevo nombre", value=nombre)
                    nuevas_instrucciones = st.text_area("📖 Nuevas instrucciones", value=instrucciones or "")
                    nueva_imagen = st.file_uploader("📷 Nueva imagen (opcional)", type=["jpg", "jpeg", "png"])

                    nuevos_insumos = []
                    for insumo in insumos:
                        insumo_id = insumo["id"]
                        nombre_i = insumo["nombre"]
                        unidad = insumo["unidad"]
                        cantidad_actual = next((d["cantidad"] for d in detalles if d["insumos"]["nombre"] == nombre_i), 0.0)
                        cantidad = st.number_input(
                            f"{nombre_i} ({unidad})", value=float(cantidad_actual), min_value=0.0, step=0.1,
                            key=f"edit_{receta_id}_{insumo_id}"
                        )
                        if cantidad > 0:
                            nuevos_insumos.append((insumo_id, cantidad))

                    guardar = st.form_submit_button("💾 Guardar cambios")
                    if guardar:
                        supabase.table("detalle_receta").delete().eq("receta_id", receta_id).execute()
                        supabase.table("recetas").update({"nombre": nuevo_nombre, "instrucciones": nuevas_instrucciones}).eq("id", receta_id).execute()
                        for insumo_id, cantidad in nuevos_insumos:
                            supabase.table("detalle_receta").insert({
                                "receta_id": receta_id,
                                "insumo_id": insumo_id,
                                "cantidad": cantidad
                            }).execute()

                        carpeta = Path("imagenes_recetas")
                        viejo = carpeta / f"{nombre.replace(' ', '_')}.jpg"
                        nuevo = carpeta / f"{nuevo_nombre.replace(' ', '_')}.jpg"
                        if nueva_imagen:
                            with open(nuevo, "wb") as f:
                                f.write(nueva_imagen.read())
                        elif viejo.exists() and nombre != nuevo_nombre:
                            viejo.rename(nuevo)

                        st.success("✅ Receta actualizada.")
                        st.session_state[f"editando_{receta_id}"] = False
                        st.experimental_rerun()
    else:
        st.info("ℹ️ No hay recetas registradas aún.")
# === ENTRADAS / SALIDAS ===
if st.session_state.pagina_activa == "Entradas/Salidas":
    st.header("🔄 Registro de Entradas y Salidas")

    insumos = supabase.table("insumos").select("*").execute().data
    if not insumos:
        st.warning("⚠️ No hay insumos disponibles.")
        st.stop()

    unidad_legible = {
        "kg": "kilogramos", "g": "gramos", "l": "litros",
        "ml": "mililitros", "barra": "barras", "unidad": "unidades"
    }

    nombres_insumos = [f"{i['nombre']} ({unidad_legible.get(i['unidad'], i['unidad'])})" for i in insumos]
    insumo_elegido = st.selectbox("🔽 Selecciona un insumo", nombres_insumos)

    index = nombres_insumos.index(insumo_elegido)
    insumo = insumos[index]
    insumo_id = insumo["id"]
    nombre = insumo["nombre"]
    unidad = insumo["unidad"]
    cantidad_actual = float(insumo["cantidad"])
    unidad_visible = unidad_legible.get(unidad, unidad)

    st.markdown(
        f"<div style='font-size:18px; font-weight:bold; color:#ffc107;'>📦 Stock actual: "
        f"{cantidad_actual:.2f} {unidad_visible}</div>", unsafe_allow_html=True
    )

    tipo = st.radio("📌 Tipo de movimiento", ["Entrada", "Salida"], horizontal=True)
    cantidad = st.number_input("📏 Cantidad a registrar", min_value=0.0, step=0.1)
    motivo = st.text_input("✏️ Motivo (opcional)")
    registrar = st.button("💾 Registrar")

    if registrar:
        if tipo == "Salida" and cantidad > cantidad_actual:
            st.error("❌ Stock insuficiente para registrar esta salida.")
        else:
            nueva_cantidad = cantidad_actual + cantidad if tipo == "Entrada" else cantidad_actual - cantidad
            supabase.table("insumos").update({"cantidad": nueva_cantidad}).eq("id", insumo_id).execute()
            supabase.table("movimientos").insert({
                "insumo_id": insumo_id,
                "tipo": tipo,
                "cantidad": cantidad,
                "fecha_hora": datetime.now().isoformat(),
                "motivo": motivo
            }).execute()
            st.success(f"✅ {tipo} registrada correctamente.")
            st.experimental_rerun()

    # === HISTORIAL ===
    st.subheader("📜 Historial de Movimientos")
    historial = supabase.table("movimientos").select("*, insumos(nombre)").order("fecha_hora", desc=True).execute().data
    if historial:
        df_hist = pd.DataFrame([{
            "Insumo": h["insumos"]["nombre"],
            "Tipo": h["tipo"],
            "Cantidad": f"{h['cantidad']:.2f}",
            "Fecha": pd.to_datetime(h["fecha_hora"]).strftime("%d/%m/%Y"),
            "Motivo": h["motivo"] or ""
        } for h in historial])

        def color_tipo(val): return 'color: green' if val == "Entrada" else 'color: red'

        st.dataframe(df_hist.style.applymap(color_tipo, subset=["Tipo"]), use_container_width=True)
    else:
        st.info("ℹ️ No hay movimientos registrados.")

    # === STOCK BAJO ===
    st.subheader("🚨 Alerta de Stock Bajo")
    bajo = [i for i in insumos if float(i["cantidad"]) < 3]
    if bajo:
        df_bajo = pd.DataFrame(bajo)
        df_bajo["Unidad"] = df_bajo["unidad"].map(unidad_legible)
        df_bajo["Cantidad"] = df_bajo["cantidad"].map(lambda x: f"{x:.2f}")
        df_bajo["₡ x unidad"] = df_bajo["costo_unitario"].map(lambda x: f"₡{x:,.2f}")

        st.warning("⚠️ Tienes insumos con menos de 3 unidades.")
        st.dataframe(df_bajo.rename(columns={
            "nombre": "Nombre", "Unidad": "Unidad", "Cantidad": "Cantidad", "₡ x unidad": "₡ x unidad"
        })[["Nombre", "Unidad", "Cantidad", "₡ x unidad"]], use_container_width=True)
    else:
        st.success("✅ Todos los insumos tienen buen stock.")
# === VENTAS ===
if st.session_state.pagina_activa == "Ventas":
    st.header("💵 Registro de Ventas")

    productos = supabase.table("productos").select("*").execute().data
    if not productos:
        st.warning("⚠️ No hay productos registrados.")
        st.stop()

    nombres_productos = [f"{p['nombre']} ({p['unidad']})" for p in productos]
    seleccionado = st.selectbox("🧁 Selecciona producto vendido", nombres_productos)

    index = nombres_productos.index(seleccionado)
    p = productos[index]
    id_producto = p["id"]
    nombre = p["nombre"]
    unidad = p["unidad"]
    precio_venta = float(p["precio_venta"])
    costo_unitario = float(p["costo"])
    stock_actual = float(p["stock"])

    st.markdown(f"**💵 Precio de venta:** ₡{precio_venta:,.2f}")
    st.markdown(f"**🧾 Costo de elaboración:** ₡{costo_unitario:,.2f}")
    st.markdown(f"**📦 Stock disponible:** {stock_actual:.2f} {unidad}")

    cantidad_vendida = st.number_input("📏 Cantidad vendida", min_value=0.0, step=0.1)
    registrar_venta = st.button("💾 Registrar venta")

    if registrar_venta:
        if cantidad_vendida <= 0:
            st.warning("⚠️ Ingresa una cantidad válida.")
        elif cantidad_vendida > stock_actual:
            st.error("❌ No puedes vender más de lo que tienes en stock.")
        else:
            ingreso = round(cantidad_vendida * precio_venta, 2)
            costo = round(cantidad_vendida * costo_unitario, 2)
            ganancia = round(ingreso - costo, 2)
            fecha = datetime.now().strftime("%d/%m/%Y")

            supabase.table("ventas").insert({
                "producto": nombre,
                "unidad": unidad,
                "cantidad": cantidad_vendida,
                "ingreso": ingreso,
                "costo": costo,
                "ganancia": ganancia,
                "fecha": fecha
            }).execute()

            nuevo_stock = stock_actual - cantidad_vendida
            supabase.table("productos").update({"stock": nuevo_stock}).eq("id", id_producto).execute()

            st.success("✅ Venta registrada correctamente.")
            st.experimental_rerun()

    # === HISTORIAL DE VENTAS ===
    st.subheader("📋 Historial de Ventas")
    ventas = supabase.table("ventas").select("*").order("id", desc=True).execute().data
    if ventas:
        df = pd.DataFrame(ventas)
        df["Cantidad"] = df["cantidad"].apply(lambda x: f"{x:.2f}")
        df["Ingreso (₡)"] = df["ingreso"].apply(lambda x: f"₡{x:,.2f}")
        df["Costo (₡)"] = df["costo"].apply(lambda x: f"₡{x:,.2f}")
        df["Ganancia (₡)"] = df["ganancia"].apply(lambda x: f"₡{x:,.2f}")

        st.dataframe(df.rename(columns={
            "producto": "Producto", "unidad": "Unidad", "fecha": "Fecha"
        })[["Producto", "Unidad", "Cantidad", "Ingreso (₡)", "Costo (₡)", "Ganancia (₡)", "Fecha"]], use_container_width=True)

        total_ingresos = sum([v["ingreso"] for v in ventas])
        total_ganancias = sum([v["ganancia"] for v in ventas])
        st.markdown(f"**💰 Total Ingresos:** ₡{total_ingresos:,.2f}")
        st.markdown(f"**📈 Total Ganancias:** ₡{total_ganancias:,.2f}")

        # Producto estrella
        df_crudo = pd.DataFrame(ventas)
        estrella = df_crudo.groupby("producto")["cantidad"].sum().idxmax()
        top = df_crudo.groupby("producto")["cantidad"].sum().max()
        st.success(f"🌟 Producto más vendido: **{estrella}** con **{top:.2f}** unidades")

        # === EDITAR/ELIMINAR ===
        st.subheader("✏️ Editar o eliminar venta")
        opciones = [f"{v['id']} - {v['producto']} ({v['cantidad']:.2f})" for v in ventas]
        seleccion_id = st.selectbox("Selecciona una venta", opciones)
        venta_id = int(seleccion_id.split(" - ")[0])
        venta = next(v for v in ventas if v["id"] == venta_id)

        nueva_cantidad = st.number_input("Nueva cantidad vendida", value=float(venta["cantidad"]), min_value=0.1, step=0.1)
        col1, col2 = st.columns(2)
        with col1:
            if st.button("Actualizar venta"):
                nuevo_ingreso = round(nueva_cantidad * precio_venta, 2)
                nuevo_costo = round(nueva_cantidad * costo_unitario, 2)
                nueva_ganancia = round(nuevo_ingreso - nuevo_costo, 2)
                supabase.table("ventas").update({
                    "cantidad": nueva_cantidad,
                    "ingreso": nuevo_ingreso,
                    "costo": nuevo_costo,
                    "ganancia": nueva_ganancia
                }).eq("id", venta_id).execute()
                st.success("✅ Venta actualizada.")
                st.experimental_rerun()
        with col2:
            if st.button("Eliminar venta"):
                supabase.table("ventas").delete().eq("id", venta_id).execute()
                st.success("🗑️ Venta eliminada.")
                st.experimental_rerun()
    else:
        st.info("ℹ️ No hay ventas registradas.")
# === BALANCE GENERAL ===
if st.session_state.pagina_activa == "Balance":
    st.header("📈 Balance General")

    # === PRODUCTOS ===
    productos = supabase.table("productos").select("*").execute().data
    ventas = supabase.table("ventas").select("*").execute().data
    insumos = supabase.table("insumos").select("*").execute().data

    total_stock = sum([float(p["stock"]) * float(p["precio_venta"]) for p in productos])
    total_ganancias = sum([float(v["ganancia"]) for v in ventas])
    total_ingresos = sum([float(v["ingreso"]) for v in ventas])
    total_costos = sum([float(v["costo"]) for v in ventas])
    total_insumos_actual = sum([float(i["cantidad"]) * float(i["costo_unitario"]) for i in insumos])

    st.subheader("🔍 Resumen")
    col1, col2 = st.columns(2)
    with col1:
        st.metric("💵 Ingresos por ventas", f"₡{total_ingresos:,.2f}")
        st.metric("📦 Valor de productos en stock", f"₡{total_stock:,.2f}")
    with col2:
        st.metric("🧾 Costo total insumos actuales", f"₡{total_insumos_actual:,.2f}")
        st.metric("📈 Ganancia neta", f"₡{total_ganancias:,.2f}")

    # === TABLA DETALLADA: VENTAS ===
    st.subheader("📋 Detalle de ventas")
    if ventas:
        df_ventas = pd.DataFrame(ventas)
        df_ventas["Ingreso (₡)"] = df_ventas["ingreso"].map(lambda x: f"₡{x:,.2f}")
        df_ventas["Ganancia (₡)"] = df_ventas["ganancia"].map(lambda x: f"₡{x:,.2f}")
        df_ventas["Costo (₡)"] = df_ventas["costo"].map(lambda x: f"₡{x:,.2f}")
        df_ventas["Cantidad"] = df_ventas["cantidad"].map(lambda x: f"{x:.2f}")

        st.dataframe(df_ventas.rename(columns={
            "producto": "Producto", "unidad": "Unidad", "fecha": "Fecha"
        })[["Producto", "Unidad", "Cantidad", "Ingreso (₡)", "Costo (₡)", "Ganancia (₡)", "Fecha"]],
        use_container_width=True)
    else:
        st.info("ℹ️ No hay datos de ventas disponibles.")

    # === TABLA DETALLADA: INSUMOS ===
    st.subheader("📋 Detalle de insumos actuales")
    if insumos:
        df_insumos = pd.DataFrame(insumos)
        df_insumos["Total (₡)"] = (df_insumos["cantidad"] * df_insumos["costo_unitario"]).map(lambda x: f"₡{x:,.2f}")
        df_insumos["₡ x unidad"] = df_insumos["costo_unitario"].map(lambda x: f"₡{x:,.2f}")
        df_insumos["Cantidad"] = df_insumos["cantidad"].map(lambda x: f"{x:.2f}")
        unidad_legible = {"kg": "kilogramos", "g": "gramos", "l": "litros", "ml": "mililitros", "barra": "barras", "unidad": "unidades"}
        df_insumos["Unidad"] = df_insumos["unidad"].map(unidad_legible)

        st.dataframe(df_insumos.rename(columns={
            "nombre": "Insumo", "Unidad": "Unidad", "₡ x unidad": "Costo Unitario", "Cantidad": "Cantidad", "Total (₡)": "Valor Total"
        })[["Insumo", "Unidad", "Costo Unitario", "Cantidad", "Valor Total"]], use_container_width=True)
    else:
        st.info("ℹ️ No hay datos de insumos.")


