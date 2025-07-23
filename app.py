import streamlit as st
from supabase import create_client, Client
from datetime import datetime
import pandas as pd
from streamlit_option_menu import option_menu

# -----------------------
# CONFIGURACIÓN INICIAL
# -----------------------
st.set_page_config(page_title="Sistema Panadería", layout="wide")
st.markdown("<h1 style='text-align: center;'>🧁 Sistema de Gestión de Panadería</h1>", unsafe_allow_html=True)

# -----------------------
# CONEXIÓN SUPABASE
# -----------------------
url = "https://fuqenmijstetuwhdulax.supabase.co"
key = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImZ1cWVubWlqc3RldHV3aGR1bGF4Iiwicm9sZSI6ImFub24iLCJpYXQiOjE3NTMyODM4MzksImV4cCI6MjA2ODg1OTgzOX0.9JdF70hcLCVCa0-lCd7yoSFKtO72niZbahM-u2ycAVg"
supabase: Client = create_client(url, key)

# -----------------------
# FUNCIONES AUXILIARES
# -----------------------
def obtener_productos():
    return supabase.table("productos").select("*").execute().data

def obtener_insumos():
    return supabase.table("insumos").select("*").execute().data

def obtener_ventas():
    return supabase.table("ventas").select("*").execute().data

def obtener_movimientos():
    return supabase.table("movimientos").select("*").order("fecha", desc=True).limit(50).execute().data

def obtener_recetas():
    return supabase.table("recetas").select("*").order("producto").execute().data

# -----------------------
# MENÚ DE NAVEGACIÓN
# -----------------------
with st.sidebar:
    st.title("📌 Menú Principal")
    seleccion = option_menu(
        menu_title=None,
        options=["Inicio", "Productos", "Insumos", "Recetas", "Ventas", "Balance", "Entradas/Salidas"],
        icons=["house", "box", "truck", "clipboard-data", "cash-coin", "bar-chart", "arrow-left-right"],
        default_index=0
    )
    st.session_state.pagina = seleccion

# =============================
# 🏠 INICIO
# =============================
if st.session_state.pagina == "Inicio":
    st.subheader("📊 Resumen General del Negocio")

    productos = obtener_productos()
    insumos = obtener_insumos()
    ventas = obtener_ventas()

    col1, col2, col3 = st.columns(3)
    col1.metric("📦 Productos registrados", len(productos))
    col2.metric("🧂 Insumos disponibles", len(insumos))
    col3.metric("💰 Ventas totales", len(ventas))

    st.markdown("---")
    st.markdown("Este sistema te permite gestionar productos, insumos, recetas, movimientos de inventario y ventas de manera eficiente. Usa el menú lateral para navegar por las distintas secciones.")
# =============================
# 📦 PESTAÑA DE PRODUCTOS
# =============================
if st.session_state.pagina == "Productos":
    st.subheader("📦 Gestión de Productos")

    with st.expander("➕ Agregar nuevo producto"):
        nombre = st.text_input("Nombre del producto")
        precio_venta = st.number_input("Precio de venta (₡)", min_value=0.01, step=0.1, format="%.2f")
        costo_produccion = st.number_input("Costo de producción (₡)", min_value=0.01, step=0.1, format="%.2f")

        if st.button("Guardar producto"):
            if nombre and precio_venta and costo_produccion:
                supabase.table("productos").insert({
                    "nombre": nombre,
                    "precio_venta": precio_venta,
                    "costo_produccion": costo_produccion
                }).execute()
                st.success("✅ Producto guardado correctamente.")
                st.rerun()
            else:
                st.warning("Por favor, completa todos los campos.")

    st.markdown("### 📋 Lista de Productos")
    productos = obtener_productos()

    if productos:
        for p in productos:
            with st.expander(f"📦 {p['nombre']}"):
                col1, col2 = st.columns(2)
                with col1:
                    nuevo_precio = st.number_input("Precio de venta", value=p["precio_venta"], key=f"precio_{p['id']}")
                with col2:
                    nuevo_costo = st.number_input("Costo de producción", value=p["costo_produccion"], key=f"costo_{p['id']}")

                if st.button("💾 Guardar cambios", key=f"guardar_{p['id']}"):
                    supabase.table("productos").update({
                        "precio_venta": nuevo_precio,
                        "costo_produccion": nuevo_costo
                    }).eq("id", p["id"]).execute()
                    st.success("✅ Producto actualizado.")
                    st.rerun()

                if st.button("🗑️ Eliminar producto", key=f"eliminar_{p['id']}"):
                    supabase.table("productos").delete().eq("id", p["id"]).execute()
                    st.success("🗑️ Producto eliminado.")
                    st.rerun()
    else:
        st.info("No hay productos registrados aún.")
# =============================
# 🧂 PESTAÑA DE INSUMOS
# =============================
if st.session_state.pagina == "Insumos":
    st.subheader("🧂 Gestión de Insumos")

    with st.expander("➕ Agregar nuevo insumo"):
        nombre_insumo = st.text_input("Nombre del insumo")
        unidad = st.text_input("Unidad de medida (ej: kg, L, unidades)")
        cantidad = st.number_input("Cantidad inicial", min_value=0.00, step=0.1, format="%.2f")

        if st.button("Guardar insumo"):
            if nombre_insumo and unidad:
                supabase.table("insumos").insert({
                    "nombre": nombre_insumo,
                    "unidad": unidad,
                    "cantidad": cantidad
                }).execute()
                st.success("✅ Insumo guardado correctamente.")
                st.rerun()
            else:
                st.warning("Por favor, completa todos los campos.")

    st.markdown("### 📋 Lista de Insumos")
    insumos = obtener_insumos()

    if insumos:
        for i in insumos:
            with st.expander(f"🧂 {i['nombre']}"):
                col1, col2 = st.columns(2)
                with col1:
                    nueva_unidad = st.text_input("Unidad de medida", value=i["unidad"], key=f"unidad_{i['id']}")
                with col2:
                    nueva_cantidad = st.number_input("Cantidad disponible", value=i["cantidad"], key=f"cantidad_{i['id']}")

                if st.button("💾 Guardar cambios", key=f"guardar_insumo_{i['id']}"):
                    supabase.table("insumos").update({
                        "unidad": nueva_unidad,
                        "cantidad": nueva_cantidad
                    }).eq("id", i["id"]).execute()
                    st.success("✅ Insumo actualizado.")
                    st.rerun()

                if st.button("🗑️ Eliminar insumo", key=f"eliminar_insumo_{i['id']}"):
                    supabase.table("insumos").delete().eq("id", i["id"]).execute()
                    st.success("🗑️ Insumo eliminado.")
                    st.rerun()
    else:
        st.info("No hay insumos registrados aún.")
# =============================
# 📄 PESTAÑA DE RECETAS
# =============================
if st.session_state.pagina == "Recetas":
    st.subheader("📄 Recetario de Productos")

    productos = obtener_productos()
    insumos = obtener_insumos()

    if not productos or not insumos:
        st.warning("Debés tener productos e insumos registrados para usar esta sección.")
        st.stop()

    with st.expander("➕ Agregar ingrediente a receta"):
        producto_nombres = [p["nombre"] for p in productos]
        insumo_nombres = [i["nombre"] for i in insumos]

        producto_seleccionado = st.selectbox("Producto", producto_nombres)
        insumo_seleccionado = st.selectbox("Insumo", insumo_nombres)
        cantidad_necesaria = st.number_input("Cantidad necesaria", min_value=0.01, step=0.1)

        if st.button("Agregar a receta"):
            producto = next(p for p in productos if p["nombre"] == producto_seleccionado)
            insumo = next(i for i in insumos if i["nombre"] == insumo_seleccionado)

            supabase.table("recetas").insert({
                "producto_id": producto["id"],
                "producto": producto["nombre"],
                "insumo_id": insumo["id"],
                "insumo": insumo["nombre"],
                "cantidad": cantidad_necesaria
            }).execute()

            st.success("✅ Ingrediente agregado a la receta.")
            st.rerun()

    st.markdown("### 📋 Recetas registradas")
    recetas = obtener_recetas()

    if recetas:
        df = pd.DataFrame(recetas)
        for producto in df["producto"].unique():
            st.markdown(f"#### 🧁 {producto}")
            sub_df = df[df["producto"] == producto][["insumo", "cantidad"]].rename(columns={
                "insumo": "Ingrediente",
                "cantidad": "Cantidad"
            })
            st.dataframe(sub_df, use_container_width=True)
    else:
        st.info("Aún no hay recetas registradas.")
# =============================
# 💰 PESTAÑA DE VENTAS
# =============================
if st.session_state.pagina == "Ventas":
    st.subheader("💰 Registro de Ventas")

    productos = obtener_productos()
    if not productos:
        st.info("Debes registrar productos antes de registrar ventas.")
        st.stop()

    producto_nombres = [p["nombre"] for p in productos]
    producto_seleccionado = st.selectbox("Selecciona un producto", producto_nombres)
    cantidad = st.number_input("Cantidad vendida", min_value=0.01, step=0.1, format="%.2f")
    fecha_venta = st.date_input("Fecha de la venta", value=datetime.today())

    if st.button("Registrar venta"):
        producto = next(p for p in productos if p["nombre"] == producto_seleccionado)
        ingreso = producto["precio_venta"] * cantidad
        costo = producto["costo_produccion"] * cantidad
        ganancia = ingreso - costo

        supabase.table("ventas").insert({
            "producto_id": producto["id"],
            "producto": producto["nombre"],
            "cantidad": cantidad,
            "ingreso": ingreso,
            "costo": costo,
            "ganancia": ganancia,
            "fecha": fecha_venta.isoformat()
        }).execute()

        st.success("✅ Venta registrada correctamente.")
        st.rerun()

    st.markdown("### 📋 Historial de Ventas")
    ventas = obtener_ventas()
    if ventas:
        df = pd.DataFrame(ventas)
        df["fecha"] = pd.to_datetime(df["fecha"]).dt.strftime("%d/%m/%Y")
        df["ingreso"] = df["ingreso"].apply(lambda x: f"₡{x:,.2f}")
        df["costo"] = df["costo"].apply(lambda x: f"₡{x:,.2f}")
        df["ganancia"] = df["ganancia"].apply(lambda x: f"₡{x:,.2f}")
        df["cantidad"] = df["cantidad"].apply(lambda x: f"{x:.2f}")

        st.dataframe(df[["fecha", "producto", "cantidad", "ingreso", "costo", "ganancia"]].rename(columns={
            "fecha": "Fecha", "producto": "Producto", "cantidad": "Cantidad", "ingreso": "Ingreso",
            "costo": "Costo", "ganancia": "Ganancia"
        }), use_container_width=True)
    else:
        st.info("No hay ventas registradas aún.")
# =============================
# 📊 PESTAÑA DE BALANCE GENERAL
# =============================
if st.session_state.pagina == "Balance":
    st.subheader("📊 Balance General del Negocio")

    ventas = obtener_ventas()

    if ventas:
        df = pd.DataFrame(ventas)
        df["fecha"] = pd.to_datetime(df["fecha"])

        ingreso_total = df["ingreso"].sum()
        costo_total = df["costo"].sum()
        ganancia_total = df["ganancia"].sum()

        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("💰 Ingresos Totales", f"₡{ingreso_total:,.2f}")
        with col2:
            st.metric("💸 Costos Totales", f"₡{costo_total:,.2f}")
        with col3:
            st.metric("📈 Ganancia Neta", f"₡{ganancia_total:,.2f}")

        st.markdown("### 📅 Ventas por Fecha")
        df["fecha_str"] = df["fecha"].dt.strftime("%d/%m/%Y")
        resumen = df.groupby("fecha_str")[["ingreso", "costo", "ganancia"]].sum().reset_index()
        resumen = resumen.rename(columns={
            "fecha_str": "Fecha",
            "ingreso": "Ingreso (₡)",
            "costo": "Costo (₡)",
            "ganancia": "Ganancia (₡)"
        })

        st.dataframe(resumen, use_container_width=True)
    else:
        st.info("No hay ventas registradas aún para calcular el balance.")
# =============================
# 🔁 PESTAÑA DE ENTRADAS/SALIDAS
# =============================
if st.session_state.pagina == "Entradas/Salidas":
    st.subheader("🔁 Registro de Entradas y Salidas de Insumos")

    insumos = obtener_insumos()
    if not insumos:
        st.info("No hay insumos registrados aún.")
        st.stop()

    tipo_mov = st.selectbox("Tipo de movimiento", ["Entrada", "Salida"])
    insumo_nombres = [i["nombre"] for i in insumos]
    insumo_seleccionado = st.selectbox("Selecciona un insumo", insumo_nombres)
    cantidad = st.number_input("Cantidad", min_value=0.01, step=0.1, format="%.2f")
    fecha = st.date_input("Fecha del movimiento", value=datetime.today())

    if st.button("Registrar movimiento"):
        insumo = next(i for i in insumos if i["nombre"] == insumo_seleccionado)
        nueva_cantidad = (
            insumo["cantidad"] + cantidad if tipo_mov == "Entrada"
            else insumo["cantidad"] - cantidad
        )

        if nueva_cantidad < 0:
            st.error("❌ No hay suficiente cantidad para realizar esta salida.")
        else:
            # Actualizar cantidad del insumo
            supabase.table("insumos").update({"cantidad": nueva_cantidad}).eq("id", insumo["id"]).execute()

            # Registrar movimiento
            supabase.table("movimientos").insert({
                "insumo_id": insumo["id"],
                "tipo": tipo_mov,
                "cantidad": cantidad,
                "fecha": fecha.isoformat()
            }).execute()

            st.success("✅ Movimiento registrado exitosamente.")
            st.rerun()

    # Mostrar historial reciente de movimientos
    st.markdown("### 📋 Historial reciente de movimientos")
    movs = obtener_movimientos()
    if movs:
        df_mov = pd.DataFrame(movs)
        df_mov["fecha"] = pd.to_datetime(df_mov["fecha"]).dt.strftime("%d/%m/%Y")
        id_to_nombre = {i["id"]: i["nombre"] for i in insumos}
        df_mov["insumo"] = df_mov["insumo_id"].map(id_to_nombre)
        df_mov = df_mov.rename(columns={
            "fecha": "Fecha",
            "tipo": "Tipo",
            "cantidad": "Cantidad",
            "insumo": "Insumo"
        })
        st.dataframe(df_mov[["Fecha", "Insumo", "Tipo", "Cantidad"]], use_container_width=True)
    else:
        st.info("No hay movimientos registrados aún.")
