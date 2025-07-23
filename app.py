# === CONEXIÓN A SUPABASE ===
from supabase import create_client
import streamlit as st
import pandas as pd
import unicodedata
from pathlib import Path
from fpdf import FPDF
from datetime import datetime

# Credenciales Supabase
SUPABASE_URL = "https://fuqenmijstetuwhdulax.supabase.co"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImZ1cWVubWlqc3RldHV3aGR1bGF4Iiwicm9sZSI6ImFub24iLCJpYXQiOjE3NTMyODM4MzksImV4cCI6MjA2ODg1OTgzOX0.9JdF70hcLCVCa0-lCd7yoSFKtO72niZbahM-u2ycAVg"
supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

# === FUNCIÓN AUXILIAR PARA LIMPIAR TEXTO ===
def limpiar_texto(texto):
    if not texto:
        return ""
    return unicodedata.normalize("NFKD", str(texto)).encode("ASCII", "ignore").decode("ASCII")

# === GENERAR PDF DE RECETA ===
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

# === CONFIGURACIÓN DE LA APP ===
st.set_page_config(page_title="Panadería Moderna", layout="wide")

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

# === MENÚ LATERAL ===
from streamlit_option_menu import option_menu
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

# === PÁGINA DE INICIO ===
if st.session_state.pagina == "Inicio":
    st.markdown("## 📊 Sistema de Gestión - Panadería Moderna")
    st.markdown("### Selecciona una opción para comenzar:")

    col1, col2, col3 = st.columns(3)
    with col1:
        if st.button("📦 Productos"):
            st.session_state.pagina = "Productos"
            st.rerun()
    with col2:
        if st.button("🚚 Insumos"):
            st.session_state.pagina = "Insumos"
            st.rerun()
    with col3:
        if st.button("📋 Recetas"):
            st.session_state.pagina = "Recetas"
            st.rerun()

    col4, col5, col6 = st.columns(3)
    with col4:
        if st.button("🔄 Entradas/Salidas"):
            st.session_state.pagina = "Entradas/Salidas"
            st.rerun()
    with col5:
        if st.button("💵 Ventas"):
            st.session_state.pagina = "Ventas"
            st.rerun()
    with col6:
        if st.button("📈 Balance"):
            st.session_state.pagina = "Balance"
            st.rerun()
# === PRODUCTOS ===
if st.session_state.pagina == "Productos":
    st.subheader("📦 Gestión de Productos")

    # === AGREGAR NUEVO PRODUCTO ===
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
                supabase.table("productos").insert({
                    "nombre": nombre,
                    "unidad": unidad,
                    "precio_venta": precio_venta,
                    "costo": costo,
                    "stock": stock
                }).execute()
                st.success(f"✅ Producto '{nombre}' agregado correctamente.")
                st.rerun()
            else:
                st.warning("⚠️ Debes completar todos los campos.")

    # === LISTA DE PRODUCTOS ===
    st.markdown("### 📋 Lista de productos")
    datos = supabase.table("productos").select("*").order("id", desc=False).execute()
    productos = datos.data if datos.data else []

    if productos:
        df = pd.DataFrame(productos)
        df["Ganancia (₡)"] = df["precio_venta"] - df["costo"]

        df["precio_venta"] = df["precio_venta"].map(lambda x: f"₡{int(x)}" if x == int(x) else f"₡{x:.2f}")
        df["costo"] = df["costo"].map(lambda x: f"₡{int(x)}" if x == int(x) else f"₡{x:.2f}")
        df["Ganancia (₡)"] = df["Ganancia (₡)"].map(lambda x: f"₡{int(x)}" if x == int(x) else f"₡{x:.2f}")

        def color_stock(val):
            return 'background-color: red; color: white' if val < 5 else ''
        styled_df = df.rename(columns={
            "id": "ID", "nombre": "Nombre", "unidad": "Unidad",
            "precio_venta": "Precio Venta", "costo": "Costo", "stock": "Stock"
        }).style.applymap(color_stock, subset=["Stock"])
        st.dataframe(styled_df, use_container_width=True)

        # === EDITAR O ELIMINAR ===
        st.markdown("### ✏️ Editar o eliminar un producto")
        nombres_disponibles = [p["nombre"] for p in productos]
        seleccion = st.selectbox("Seleccionar producto por nombre", nombres_disponibles)

        seleccionado = next((p for p in productos if p["nombre"] == seleccion), None)
        if seleccionado:
            id_producto = seleccionado["id"]
            with st.form("form_editar_producto"):
                nuevo_nombre = st.text_input("Nombre", value=seleccionado["nombre"])
                nueva_unidad = st.selectbox("Unidad", ["unidad", "porción", "pieza", "queque", "paquete"],
                                            index=["unidad", "porción", "pieza", "queque", "paquete"].index(seleccionado["unidad"]))
                nuevo_precio = st.number_input("Precio de venta (₡)", value=float(seleccionado["precio_venta"]), format="%.2f")
                nuevo_costo = st.number_input("Costo de elaboración (₡)", value=float(seleccionado["costo"]), format="%.2f")
                nuevo_stock = st.number_input("Stock disponible", value=int(seleccionado["stock"]), step=1)

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
                    st.success("✅ Producto actualizado correctamente.")
                    st.rerun()
                if eliminar:
                    supabase.table("productos").delete().eq("id", id_producto).execute()
                    st.success("🗑️ Producto eliminado correctamente.")
                    st.rerun()
    else:
        st.info("ℹ️ No hay productos registrados todavía.")
# === INSUMOS ===
if st.session_state.pagina == "Insumos":
    st.subheader("🚚 Gestión de Insumos")

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
                    f"Cantidad: {cantidad} {unidad_i}, Costo total: ₡{costo_total:.2f}, "
                    f"₡{costo_unitario:.2f} por {unidad_i} → ₡{costo_base:.2f} por {unidad_base}"
                )
                st.rerun()
            else:
                st.warning("⚠️ Debes completar todos los campos y la cantidad debe ser mayor a cero.")

    # === LISTA DE INSUMOS ===
    st.markdown("### 📋 Lista de insumos")
    datos = supabase.table("insumos").select("*").order("id", desc=False).execute()
    insumos = datos.data if datos.data else []

    if insumos:
        df_i = pd.DataFrame(insumos)
        unidad_legible = {v: k for k, v in unidades_dict.items()}
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

        st.dataframe(df_i[["id", "nombre", "Unidad Mostrada", "costo_unitario", "cantidad", "Costo Total (₡)", "₡ por unidad base"]]
                     .rename(columns={"id": "ID", "nombre": "Nombre", "costo_unitario": "Costo Unitario", "cantidad": "Cantidad"}),
                     use_container_width=True)

        # === EDITAR/ELIMINAR INSUMO ===
        st.markdown("### ✏️ Editar o eliminar un insumo")
        nombres_insumos = [i["nombre"] for i in insumos]
        seleccion_i = st.selectbox("Seleccionar insumo por nombre", nombres_insumos)

        seleccionado = next((i for i in insumos if i["nombre"] == seleccion_i), None)
        if seleccionado:
            id_insumo = seleccionado["id"]
            costo_unitario_original = float(seleccionado["costo_unitario"])
            cantidad_original = float(seleccionado["cantidad"])
            costo_total_original = costo_unitario_original * cantidad_original
            unidad_visible_original = [k for k, v in unidades_dict.items() if v == seleccionado["unidad"]][0]

            with st.form("form_editar_insumo"):
                nuevo_nombre_i = st.text_input("Nombre", value=seleccionado["nombre"])
                nueva_unidad_visible = st.selectbox("Unidad", list(unidades_dict.keys()),
                                                    index=list(unidades_dict.keys()).index(unidad_visible_original))
                nueva_unidad = unidades_dict[nueva_unidad_visible]
                nueva_cantidad = st.number_input("Cantidad adquirida", value=float(cantidad_original))
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
                        "costo_unitario": nuevo_costo_unitario,
                        "cantidad": nueva_cantidad
                    }).eq("id", id_insumo).execute()
                    st.success("✅ Insumo actualizado correctamente.")
                    st.rerun()

                if eliminar_i:
                    supabase.table("insumos").delete().eq("id", id_insumo).execute()
                    st.success("🗑️ Insumo eliminado correctamente.")
                    st.rerun()
    else:
        st.info("ℹ️ No hay insumos registrados todavía.")
# === RECETAS ===
if st.session_state.pagina == "Recetas":
    st.subheader("📋 Gestión de Recetas")

    # === CREAR NUEVA RECETA ===
    with st.form("form_nueva_receta"):
        st.markdown("### ➕ Crear nueva receta")
        nombre_receta = st.text_input("📛 Nombre de la receta")
        instrucciones = st.text_area("📖 Instrucciones de preparación")
        imagen_receta = st.file_uploader("📷 Foto del producto final (opcional)", type=["png", "jpg", "jpeg"])

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
                st.warning("⚠️ Debes ingresar un nombre y al menos un insumo.")
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
                    carpeta_imagenes = Path("imagenes_recetas")
                    carpeta_imagenes.mkdir(exist_ok=True)
                    nombre_archivo = f"{nombre_receta.replace(' ', '_')}.jpg"
                    with open(carpeta_imagenes / nombre_archivo, "wb") as f:
                        f.write(imagen_receta.read())

                st.success(f"✅ Receta '{nombre_receta}' guardada correctamente.")
                st.rerun()

    # === MOSTRAR RECETAS ===
    st.markdown("### 📋 Recetas registradas")
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
                nombre_insumo = item["insumos"]["nombre"]
                unidad = item["insumos"]["unidad"]
                costo_unitario = item["insumos"]["costo_unitario"]
                cantidad = item["cantidad"]

                if unidad in ["kg", "l"]:
                    costo_por_base = costo_unitario / 1000
                    cantidad_en_base = cantidad * 1000
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
                    if st.button("🗑️ Eliminar receta", key=f"eliminar_{receta_id}"):
                        supabase.table("detalle_receta").delete().eq("receta_id", receta_id).execute()
                        supabase.table("recetas").delete().eq("id", receta_id).execute()
                        if ruta_img.exists():
                            ruta_img.unlink()
                        st.success(f"🗑️ Receta '{nombre}' eliminada.")
                        st.rerun()
                with col2:
                    if st.button("✏️ Editar receta", key=f"editar_{receta_id}"):
                        st.session_state[f"editando_{receta_id}"] = True

            # FORMULARIO DE EDICIÓN
            if st.session_state.get(f"editando_{receta_id}", False):
                with st.form(f"form_edicion_{receta_id}"):
                    nuevo_nombre = st.text_input("📛 Nuevo nombre", value=nombre, key=f"nombre_{receta_id}")
                    nuevas_instrucciones = st.text_area("📖 Nuevas instrucciones", value=instrucciones or "", key=f"inst_{receta_id}")
                    nueva_imagen = st.file_uploader("📷 Nueva imagen (opcional)", type=["jpg", "jpeg", "png"], key=f"img_{receta_id}")

                    nuevos_insumos = []
                    for insumo in insumos:
                        insumo_id = insumo["id"]
                        nombre_insumo = insumo["nombre"]
                        unidad = insumo["unidad"]
                        cantidad_actual = next((d["cantidad"] for d in detalles if d["insumos"]["nombre"] == nombre_insumo), 0.0)
                        cantidad = st.number_input(
                            f"{nombre_insumo} ({unidad})",
                            value=float(cantidad_actual),
                            min_value=0.0,
                            step=0.1,
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
                        st.rerun()
    else:
        st.info("ℹ️ No hay recetas registradas todavía.")
# === ENTRADAS/SALIDAS ===
if st.session_state.pagina == "Entradas/Salidas":
    st.subheader("📤 Registro de Entradas y Salidas de Insumos")

    insumos = supabase.table("insumos").select("*").execute().data
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

    nombres_insumos = [f"{i['nombre']} ({unidad_legible.get(i['unidad'], i['unidad'])})" for i in insumos]
    insumo_elegido = st.selectbox("🔽 Selecciona el insumo", nombres_insumos)

    index = nombres_insumos.index(insumo_elegido)
    insumo_id = insumos[index]["id"]
    nombre = insumos[index]["nombre"]
    unidad = insumos[index]["unidad"]
    costo_unitario = insumos[index]["costo_unitario"]
    cantidad_actual = insumos[index]["cantidad"]
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
            nueva_cantidad = cantidad_actual + cantidad if tipo_movimiento == "Entrada" else cantidad_actual - cantidad

            # Actualizar insumo
            supabase.table("insumos").update({"cantidad": nueva_cantidad}).eq("id", insumo_id).execute()

            # Registrar movimiento
            supabase.table("movimientos").insert({
                "insumo_id": insumo_id,
                "tipo": tipo_movimiento,
                "cantidad": cantidad,
                "fecha_hora": datetime.now().isoformat(),
                "motivo": motivo
            }).execute()

            st.success(f"✅ {tipo_movimiento} registrada correctamente.")
            st.rerun()

    # === HISTORIAL DE MOVIMIENTOS ===
    historial = supabase.table("movimientos").select("*, insumos(nombre)").order("fecha_hora", desc=True).execute().data
    if historial:
        st.markdown("### 📜 Historial de Movimientos")
        df_hist = pd.DataFrame([{
            "Insumo": h["insumos"]["nombre"],
            "Tipo": h["tipo"],
            "Cantidad": f"{h['cantidad']:.2f}",
            "Fecha y Hora": pd.to_datetime(h["fecha_hora"]).strftime("%d/%m/%Y"),
            "Motivo": h["motivo"] or ""
        } for h in historial])

        def colorear_tipo(val):
            color = 'green' if val == "Entrada" else 'red'
            return f'color: {color}; font-weight: bold'

        st.dataframe(df_hist.style.applymap(colorear_tipo, subset=["Tipo"]), use_container_width=True)

    # === ALERTA DE STOCK BAJO ===
    st.markdown("### 🚨 Insumos con stock bajo")
    bajo_stock = [i for i in insumos if i["cantidad"] < 3]
    if bajo_stock:
        df_bajo = pd.DataFrame(bajo_stock)
        df_bajo["unidad"] = df_bajo["unidad"].map(unidad_legible)
        df_bajo["₡ x unidad"] = df_bajo["costo_unitario"].apply(lambda x: f"₡{x:,.2f}")
        df_bajo["Cantidad disponible"] = df_bajo["cantidad"].apply(lambda x: f"{x:.2f}")
        st.warning("⚠️ Tienes insumos con menos de 3 unidades.")
        st.dataframe(df_bajo[["nombre", "unidad", "₡ x unidad", "Cantidad disponible"]]
                     .rename(columns={"nombre": "Nombre", "unidad": "Unidad"}), use_container_width=True)
    else:
        st.success("✅ Todos los insumos tienen suficiente stock.")
# === VENTAS ===
if st.session_state.pagina == "Ventas":
    st.subheader("💰 Registro de Ventas de Productos")

    productos = supabase.table("productos").select("*").execute().data
    if not productos:
        st.warning("⚠️ No hay productos disponibles. Agrega primero desde la pestaña de Productos.")
    else:
        nombres_productos = [f"{p['nombre']} ({p['unidad']})" for p in productos]
        producto_elegido = st.selectbox("🧁 Selecciona el producto vendido", nombres_productos)

        index = nombres_productos.index(producto_elegido)
        producto = productos[index]
        id_producto = producto["id"]
        nombre = producto["nombre"]
        unidad = producto["unidad"]
        precio_venta = float(producto["precio_venta"])
        costo_unitario = float(producto["costo"])
        stock_disponible = float(producto["stock"])

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

                # Insertar venta
                supabase.table("ventas").insert({
                    "producto": nombre,
                    "unidad": unidad,
                    "cantidad": cantidad_vendida,
                    "ingreso": ingreso_total,
                    "costo": costo_total,
                    "ganancia": ganancia_total,
                    "fecha": fecha_actual
                }).execute()

                # Actualizar stock del producto
                nuevo_stock = stock_disponible - cantidad_vendida
                supabase.table("productos").update({"stock": nuevo_stock}).eq("id", id_producto).execute()

                st.success("✅ Venta registrada correctamente.")
                st.rerun()

    # === HISTORIAL DE VENTAS ===
    ventas = supabase.table("ventas").select("*").order("id", desc=True).execute().data
    if ventas:
        st.markdown("### 📋 Historial de ventas")
        df_ventas = pd.DataFrame(ventas)
        df_ventas["Cantidad"] = df_ventas["cantidad"].apply(lambda x: f"{x:.2f}")
        df_ventas["Ingreso (₡)"] = df_ventas["ingreso"].apply(lambda x: f"₡{x:,.2f}")
        df_ventas["Costo (₡)"] = df_ventas["costo"].apply(lambda x: f"₡{x:,.2f}")
        df_ventas["Ganancia (₡)"] = df_ventas["ganancia"].apply(lambda x: f"₡{x:,.2f}")

        st.dataframe(df_ventas[["producto", "unidad", "Cantidad", "Ingreso (₡)", "Costo (₡)", "Ganancia (₡)", "fecha"]]
                     .rename(columns={"producto": "Producto", "unidad": "Unidad", "fecha": "Fecha"}), use_container_width=True)

        total_ingresos = sum([v["ingreso"] for v in ventas])
        total_ganancias = sum([v["ganancia"] for v in ventas])
        st.markdown(f"**💵 Total ingresos:** ₡{total_ingresos:,.2f}")
        st.markdown(f"**📈 Total ganancias:** ₡{total_ganancias:,.2f}")

        # Producto más vendido
        df_crudo = pd.DataFrame(ventas)
        producto_estrella = df_crudo.groupby("producto")["cantidad"].sum().idxmax()
        cantidad_estrella = df_crudo.groupby("producto")["cantidad"].sum().max()
        st.success(f"🌟 Producto estrella: **{producto_estrella}** con **{cantidad_estrella:.2f}** unidades vendidas")

        # === EDITAR / ELIMINAR VENTA ===
        st.markdown("### ✏️ Editar o eliminar una venta")
        ids_ventas = [f"{v['id']} - {v['producto']} ({v['cantidad']:.2f})" for v in ventas]
        seleccion_id = st.selectbox("Selecciona una venta", ids_ventas)

        venta_id = int(seleccion_id.split(" - ")[0])
        venta = next(v for v in ventas if v["id"] == venta_id)

        nueva_cantidad = st.number_input("Nueva cantidad vendida", min_value=0.1, value=float(venta["cantidad"]), step=0.1)
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

                st.success("✅ Venta actualizada correctamente.")
                st.rerun()

        with col2:
            if st.button("Eliminar venta"):
                supabase.table("ventas").delete().eq("id", venta_id).execute()
                st.success("🗑️ Venta eliminada correctamente.")
                st.rerun()
    else:
        st.info("ℹ️ Aún no hay ventas registradas.")
# === BALANCE ===
if st.session_state.pagina == "Balance":
    st.subheader("📊 Balance General del Negocio")

    st.markdown("### 📅 Selecciona un rango de fechas")
    col1, col2 = st.columns(2)
    with col1:
        fecha_inicio = st.date_input("Desde", value=datetime.today().replace(day=1))
    with col2:
        fecha_fin = st.date_input("Hasta", value=datetime.today())

    # === INVENTARIO DE INSUMOS ===
    insumos = supabase.table("insumos").select("*").execute().data
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

        total_inventario_num = sum([i["costo_unitario"] * i["cantidad"] for i in insumos])

        st.markdown("### 📦 Valor del inventario de insumos")
        st.dataframe(df_insumos[["nombre", "Unidad", "cantidad", "Costo Unitario", "Total (₡)"]]
                     .rename(columns={"nombre": "Nombre", "cantidad": "Cantidad"}), use_container_width=True)
        st.markdown(f"**🔹 Total inventario:** ₡{total_inventario_num:,.2f}")
    else:
        st.info("ℹ️ No hay insumos registrados.")

    st.divider()

    # === VENTAS EN EL PERÍODO ===
    st.markdown("### 💰 Ventas registradas en el período")
    ventas = supabase.table("ventas").select("*").execute().data
    if ventas:
        df_ventas = pd.DataFrame(ventas)
        df_ventas["Fecha"] = pd.to_datetime(df_ventas["fecha"], format="%d/%m/%Y")

        df_filtrado = df_ventas[
            (df_ventas["Fecha"] >= pd.to_datetime(fecha_inicio)) &
            (df_ventas["Fecha"] <= pd.to_datetime(fecha_fin))
        ]

        if not df_filtrado.empty:
            total_ingresos = df_filtrado["ingreso"].sum()
            total_costos = df_filtrado["costo"].sum()
            total_ganancia = df_filtrado["ganancia"].sum()

            df_filtrado["Cantidad"] = df_filtrado["cantidad"].apply(lambda x: f"{x:.2f}")
            df_filtrado["Ingreso (₡)"] = df_filtrado["ingreso"].apply(lambda x: f"₡{x:,.2f}")
            df_filtrado["Costo (₡)"] = df_filtrado["costo"].apply(lambda x: f"₡{x:,.2f}")
            df_filtrado["Ganancia (₡)"] = df_filtrado["ganancia"].apply(lambda x: f"₡{x:,.2f}")
            df_filtrado["Fecha"] = df_filtrado["Fecha"].dt.strftime("%d/%m/%Y")

            st.dataframe(df_filtrado[["producto", "unidad", "Cantidad", "Ingreso (₡)", "Costo (₡)", "Ganancia (₡)", "Fecha"]]
                         .rename(columns={"producto": "Producto", "unidad": "Unidad"}), use_container_width=True)

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

