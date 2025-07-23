import streamlit as st
from streamlit_option_menu import option_menu
from datetime import datetime
import pandas as pd
from fpdf import FPDF
from PIL import Image
import base64
import os
from supabase import create_client, Client

# =============================
# 🔗 CONEXIÓN A SUPABASE
# =============================
url = "https://fuqenmijstetuwhdulax.supabase.co"
key = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImZ1cWVubWlqc3RldHV3aGR1bGF4Iiwicm9sZSI6ImFub24iLCJpYXQiOjE3NTMyODM4MzksImV4cCI6MjA2ODg1OTgzOX0.9JdF70hcLCVCa0-lCd7yoSFKtO72niZbahM-u2ycAVg"
supabase: Client = create_client(url, key)

# =============================
# 📂 CREAR CARPETAS NECESARIAS
# =============================
os.makedirs("imagenes_recetas", exist_ok=True)

# =============================
# 🔧 CONFIGURACIÓN DE PÁGINA
# =============================
st.set_page_config(page_title="Gestión de Panadería", layout="wide")
st.markdown("<h1 style='text-align: center;'>🧁 Sistema de Gestión de Panadería</h1>", unsafe_allow_html=True)

# =============================
# 📋 MENÚ LATERAL
# =============================
with st.sidebar:
    opcion = option_menu(
        menu_title="Navegación",
        options=["Inicio", "Productos", "Insumos", "Recetas", "Entradas/Salidas", "Ventas", "Balance"],
        icons=["house", "box", "truck", "file-earmark-text", "arrow-left-right", "cash-stack", "bar-chart-line"],
        default_index=0,
        menu_icon="list"
    )
    st.session_state.pagina = opcion

# =============================
# ⚙️ FUNCIONES BASE CON SUPABASE
# =============================
def obtener_productos():
    res = supabase.table("productos").select("*").order("id", desc=True).execute()
    return res.data if res.data else []

def obtener_insumos():
    res = supabase.table("insumos").select("*").order("id", desc=True).execute()
    return res.data if res.data else []

def obtener_ventas():
    res = supabase.table("ventas").select("*").order("id", desc=True).execute()
    return res.data if res.data else []

def actualizar_producto(id, nombre, unidad, precio_venta, costo, stock):
    supabase.table("productos").update({
        "nombre": nombre,
        "unidad": unidad,
        "precio_venta": precio_venta,
        "costo": costo,
        "stock": stock
    }).eq("id", id).execute()
# =============================
# 🏠 PESTAÑA DE INICIO
# =============================
if st.session_state.pagina == "Inicio":
    st.subheader("📊 Panel General")
    st.markdown("Bienvenido al sistema de gestión para tu panadería. Aquí puedes ver un resumen general del negocio.")

    # Cargar métricas
    productos = obtener_productos()
    insumos = obtener_insumos()
    ventas = obtener_ventas()

    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("📦 Productos", len(productos))
    with col2:
        st.metric("🧂 Insumos", len(insumos))
    with col3:
        st.metric("💰 Ventas", len(ventas))

    st.divider()
    st.markdown("Utiliza el menú lateral para registrar productos, administrar insumos, gestionar recetas y visualizar reportes de ventas o balance general.")
# =============================
# 📦 PESTAÑA DE PRODUCTOS
# =============================
if st.session_state.pagina == "Productos":
    st.subheader("📦 Gestión de Productos")

    with st.expander("➕ Agregar nuevo producto"):
        with st.form("form_producto"):
            nombre = st.text_input("Nombre del producto")
            unidad = st.selectbox("Unidad de medida", ["unidad", "gramos", "litros"])
            precio_venta = st.number_input("Precio de venta (₡)", min_value=0.0, format="%.2f")
            costo = st.number_input("Costo estimado (₡)", min_value=0.0, format="%.2f")
            stock = st.number_input("Stock inicial", min_value=0.0, format="%.2f")
            submitted = st.form_submit_button("Guardar producto")
            if submitted:
                supabase.table("productos").insert({
                    "nombre": nombre,
                    "unidad": unidad,
                    "precio_venta": precio_venta,
                    "costo": costo,
                    "stock": stock
                }).execute()
                st.success("✅ Producto agregado correctamente")

    productos = obtener_productos()
    if productos:
        st.markdown("### 📋 Lista de Productos Registrados")
        for prod in productos:
            with st.expander(f"{prod['nombre']} (Stock: {prod['stock']})"):
                nuevo_nombre = st.text_input(f"Nombre:", value=prod["nombre"], key=f"n{prod['id']}")
                nueva_unidad = st.selectbox(f"Unidad:", ["unidad", "gramos", "litros"], index=["unidad", "gramos", "litros"].index(prod["unidad"]), key=f"u{prod['id']}")
                nuevo_precio = st.number_input(f"Precio de venta (₡):", value=prod["precio_venta"], key=f"pv{prod['id']}")
                nuevo_costo = st.number_input(f"Costo estimado (₡):", value=prod["costo"], key=f"co{prod['id']}")
                nuevo_stock = st.number_input(f"Stock disponible:", value=prod["stock"], key=f"st{prod['id']}")

                col1, col2 = st.columns(2)
                with col1:
                    if st.button("💾 Actualizar", key=f"up{prod['id']}"):
                        actualizar_producto(prod["id"], nuevo_nombre, nueva_unidad, nuevo_precio, nuevo_costo, nuevo_stock)
                        st.success("✅ Producto actualizado")
                        st.rerun()
                with col2:
                    if st.button("🗑️ Eliminar", key=f"del{prod['id']}"):
                        supabase.table("productos").delete().eq("id", prod["id"]).execute()
                        st.warning("❌ Producto eliminado")
                        st.rerun()
    else:
        st.info("No hay productos registrados todavía.")
# =============================
# 🚚 PESTAÑA DE INSUMOS
# =============================
if st.session_state.pagina == "Insumos":
    st.subheader("🚚 Gestión de Insumos")

    with st.expander("➕ Agregar nuevo insumo"):
        with st.form("form_insumo"):
            nombre = st.text_input("Nombre del insumo")
            unidad = st.selectbox("Unidad de medida", ["unidad", "gramos", "litros"])
            costo_unitario = st.number_input("Costo unitario (₡)", min_value=0.0, format="%.4f")
            cantidad = st.number_input("Cantidad inicial", min_value=0.0, format="%.2f")
            submitted = st.form_submit_button("Guardar insumo")
            if submitted:
                supabase.table("insumos").insert({
                    "nombre": nombre,
                    "unidad": unidad,
                    "costo_unitario": costo_unitario,
                    "cantidad": cantidad
                }).execute()
                st.success("✅ Insumo agregado correctamente")

    insumos = obtener_insumos()
    if insumos:
        st.markdown("### 📋 Lista de Insumos Registrados")
        for ins in insumos:
            with st.expander(f"{ins['nombre']} (Cantidad: {ins['cantidad']})"):
                nuevo_nombre = st.text_input(f"Nombre:", value=ins["nombre"], key=f"in{ins['id']}")
                nueva_unidad = st.selectbox(f"Unidad:", ["unidad", "gramos", "litros"], index=["unidad", "gramos", "litros"].index(ins["unidad"]), key=f"ui{ins['id']}")
                nuevo_costo = st.number_input(f"Costo unitario (₡):", value=ins["costo_unitario"], key=f"cu{ins['id']}")
                nueva_cantidad = st.number_input(f"Cantidad:", value=ins["cantidad"], key=f"ca{ins['id']}")

                col1, col2 = st.columns(2)
                with col1:
                    if st.button("💾 Actualizar", key=f"upin{ins['id']}"):
                        supabase.table("insumos").update({
                            "nombre": nuevo_nombre,
                            "unidad": nueva_unidad,
                            "costo_unitario": nuevo_costo,
                            "cantidad": nueva_cantidad
                        }).eq("id", ins["id"]).execute()
                        st.success("✅ Insumo actualizado")
                        st.rerun()
                with col2:
                    if st.button("🗑️ Eliminar", key=f"delin{ins['id']}"):
                        supabase.table("insumos").delete().eq("id", ins["id"]).execute()
                        st.warning("❌ Insumo eliminado")
                        st.rerun()
    else:
        st.info("No hay insumos registrados todavía.")
# =============================
# 📋 PESTAÑA DE RECETAS
# =============================
if st.session_state.pagina == "Recetas":
    st.subheader("📋 Gestión de Recetas")

    # === FUNCIONES RECETAS ===
    def agregar_receta(nombre, instrucciones, insumos):
        res = supabase.table("recetas").insert({
            "nombre": nombre,
            "instrucciones": instrucciones
        }).execute()
        receta_id = res.data[0]["id"]
        for insumo_id, cantidad in insumos:
            supabase.table("detalle_receta").insert({
                "receta_id": receta_id,
                "insumo_id": insumo_id,
                "cantidad": cantidad
            }).execute()

    def obtener_recetas():
        res = supabase.table("recetas").select("*").order("id", desc=True).execute()
        return res.data

    def obtener_detalle_receta(receta_id):
        res = supabase.table("detalle_receta").select("cantidad, insumo:insumo_id(nombre, unidad, costo_unitario)").eq("receta_id", receta_id).execute()
        return res.data

    def eliminar_receta(receta_id):
        supabase.table("detalle_receta").delete().eq("receta_id", receta_id).execute()
        supabase.table("recetas").delete().eq("id", receta_id).execute()

    # === FORMULARIO NUEVA RECETA ===
    with st.expander("➕ Crear nueva receta"):
        with st.form("form_receta"):
            nombre_receta = st.text_input("Nombre de la receta")
            instrucciones = st.text_area("Instrucciones de preparación")
            imagen = st.file_uploader("📷 Imagen del producto (opcional)", type=["jpg", "jpeg", "png"])
            ingredientes = []
            st.markdown("### Selección de insumos:")
            for ins in obtener_insumos():
                cantidad = st.number_input(f"{ins['nombre']} ({ins['unidad']})", min_value=0.0, step=0.1, key=f"insumo_{ins['id']}")
                if cantidad > 0:
                    ingredientes.append((ins["id"], cantidad))
            guardar = st.form_submit_button("Guardar receta")

            if guardar:
                if not nombre_receta or not ingredientes:
                    st.error("Debes ingresar un nombre y al menos un insumo.")
                else:
                    agregar_receta(nombre_receta, instrucciones, ingredientes)
                    if imagen:
                        path = f"imagenes_recetas/{nombre_receta.replace(' ', '_')}.jpg"
                        with open(path, "wb") as f:
                            f.write(imagen.read())
                    st.success("✅ Receta guardada correctamente.")
                    st.rerun()

    # === LISTA DE RECETAS ===
    recetas = obtener_recetas()
    if recetas:
        for receta in recetas:
            detalles = obtener_detalle_receta(receta["id"])
            total = 0
            desglose = []
            for item in detalles:
                nombre = item["insumo"]["nombre"]
                unidad = item["insumo"]["unidad"]
                costo_unitario = item["insumo"]["costo_unitario"]
                cantidad = item["cantidad"]
                subtotal = cantidad * (costo_unitario / 1000) if unidad in ["kg", "l"] else cantidad * costo_unitario
                total += subtotal
                desglose.append((nombre, cantidad, unidad, costo_unitario, subtotal))

            with st.expander(f"🍰 {receta['nombre']} — Costo: ₡{total:,.2f}"):
                ruta = f"imagenes_recetas/{receta['nombre'].replace(' ', '_')}.jpg"
                if os.path.exists(ruta):
                    st.image(ruta, width=300)

                st.markdown(f"**📝 Instrucciones:** {receta.get('instrucciones') or 'Sin instrucciones.'}")
                st.markdown("**🧾 Ingredientes:**")
                for d in desglose:
                    st.markdown(f"- {d[0]}: {d[1]:.2f} {d[2]} (₡{d[3]:.2f} → Subtotal: ₡{d[4]:.2f})")

                col1, col2 = st.columns(2)
                with col1:
                    if st.button(f"🗑️ Eliminar", key=f"delrec{receta['id']}"):
                        eliminar_receta(receta["id"])
                        if os.path.exists(ruta):
                            os.remove(ruta)
                        st.warning("Receta eliminada.")
                        st.rerun()
                with col2:
                    if st.button(f"📤 Exportar PDF", key=f"pdf{receta['id']}"):
                        from io import BytesIO
                        from fpdf import FPDF

                        pdf = FPDF()
                        pdf.add_page()
                        pdf.set_font("Arial", "B", 14)
                        pdf.cell(0, 10, f"Receta: {receta['nombre']}", ln=True)

                        pdf.set_font("Arial", "", 12)
                        pdf.cell(0, 10, f"Costo estimado: ₡{total:,.2f}", ln=True)
                        pdf.ln(5)
                        pdf.set_font("Arial", "B", 12)
                        pdf.cell(0, 10, "Ingredientes:", ln=True)
                        pdf.set_font("Arial", "", 12)
                        for d in desglose:
                            linea = f"- {d[0]}: {d[1]:.2f} {d[2]} → Subtotal: ₡{d[4]:,.2f}"
                            pdf.cell(0, 8, linea, ln=True)
                        pdf.ln(5)
                        pdf.set_font("Arial", "B", 12)
                        pdf.cell(0, 10, "Instrucciones:", ln=True)
                        pdf.set_font("Arial", "", 12)
                        for linea in (receta.get("instrucciones") or "Sin instrucciones").split("\n"):
                            pdf.multi_cell(0, 8, linea)

                        buffer = BytesIO()
                        pdf.output(buffer)
                        st.download_button("📥 Descargar PDF", data=buffer.getvalue(), file_name=f"{receta['nombre']}.pdf", mime="application/pdf")
    else:
        st.info("No hay recetas registradas todavía.")
# =============================
# 💰 PESTAÑA DE VENTAS
# =============================
if st.session_state.pagina == "Ventas":
    st.subheader("💰 Registro de Ventas")

    # === FUNCIONES AUXILIARES ===
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
        st.warning("⚠️ No hay productos disponibles.")
    else:
        nombres_productos = [f"{p['nombre']} ({p['unidad']})" for p in productos]
        seleccionado = st.selectbox("Selecciona el producto vendido", nombres_productos)
        prod = next(p for p in productos if f"{p['nombre']} ({p['unidad']})" == seleccionado)

        st.markdown(f"💵 Precio de venta: ₡{prod['precio_venta']:.2f}")
        st.markdown(f"🧾 Costo de elaboración: ₡{prod['costo']:.2f}")
        st.markdown(f"📦 Stock actual: {prod['stock']:.2f} {prod['unidad']}")

        cantidad = st.number_input("Cantidad vendida", min_value=0.0, step=0.1)
        if st.button("💾 Registrar venta"):
            if cantidad <= 0:
                st.error("⚠️ Ingresa una cantidad válida.")
            elif cantidad > prod['stock']:
                st.error("❌ No hay suficiente stock disponible.")
            else:
                ingreso = round(cantidad * prod["precio_venta"], 2)
                costo = round(cantidad * prod["costo"], 2)
                ganancia = ingreso - costo
                fecha = datetime.now().strftime("%Y-%m-%d")
                registrar_venta_en_db(prod["nombre"], prod["unidad"], cantidad, ingreso, costo, ganancia, fecha)
                actualizar_producto(prod["id"], prod["nombre"], prod["unidad"], prod["precio_venta"], prod["costo"], prod["stock"] - cantidad)
                st.success("✅ Venta registrada correctamente.")
                st.rerun()

    # === HISTORIAL DE VENTAS ===
    ventas = obtener_ventas()
    if ventas:
        st.markdown("### 📋 Historial de Ventas")
        df = pd.DataFrame(ventas)
        df["fecha"] = pd.to_datetime(df["fecha"]).dt.strftime("%d/%m/%Y")
        df["ingreso"] = df["ingreso"].map(lambda x: f"₡{x:,.2f}")
        df["costo"] = df["costo"].map(lambda x: f"₡{x:,.2f}")
        df["ganancia"] = df["ganancia"].map(lambda x: f"₡{x:,.2f}")
        df["cantidad"] = df["cantidad"].map(lambda x: f"{x:.2f}")
        st.dataframe(df.drop(columns=["id"]), use_container_width=True)

        total_ingresos = sum(float(v["ingreso"].replace("₡", "").replace(",", "")) for v in ventas)
        total_ganancia = sum(float(v["ganancia"].replace("₡", "").replace(",", "")) for v in ventas)

        st.markdown(f"**Total ingresos:** ₡{total_ingresos:,.2f}")
        st.markdown(f"**Total ganancia:** ₡{total_ganancia:,.2f}")

        st.markdown("### ✏️ Editar o eliminar una venta")
        seleccion = st.selectbox("Selecciona una venta por ID", [f"{v['id']} - {v['producto']}" for v in ventas])
        venta_id = int(seleccion.split(" - ")[0])
        venta = next(v for v in ventas if v["id"] == venta_id)

        nueva_cantidad = st.number_input("Nueva cantidad vendida", value=float(venta["cantidad"]), min_value=0.1, step=0.1, key="editcantidad")

        col1, col2 = st.columns(2)
        with col1:
            if st.button("Actualizar venta"):
                producto = next(p for p in productos if p["nombre"] == venta["producto"])
                nuevo_ingreso = round(nueva_cantidad * producto["precio_venta"], 2)
                nuevo_costo = round(nueva_cantidad * producto["costo"], 2)
                nueva_ganancia = nuevo_ingreso - nuevo_costo
                actualizar_venta(venta_id, nueva_cantidad, nuevo_ingreso, nuevo_costo, nueva_ganancia)
                st.success("✅ Venta actualizada.")
                st.rerun()
        with col2:
            if st.button("Eliminar venta"):
                eliminar_venta(venta_id)
                st.warning("🗑️ Venta eliminada.")
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
            "kg": "kilogramos", "g": "gramos", "l": "litros", "ml": "mililitros",
            "barra": "barras", "unidad": "unidades", "gramos": "gramos", "litros": "litros"
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
