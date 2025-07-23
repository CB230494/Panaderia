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
elif opcion == "📦 Productos":
    st.title("📦 Gestión de Productos")

    # Mostrar productos existentes
    st.subheader("Lista de productos registrados")
    productos = supabase.table("productos").select("*").execute().data
    if productos:
        df_productos = pd.DataFrame(productos)
        st.dataframe(df_productos.drop(columns=["id"]), use_container_width=True)
    else:
        st.info("No hay productos registrados.")

    # Formulario para agregar producto
    st.subheader("Agregar nuevo producto")

    with st.form("form_producto"):
        nombre = st.text_input("Nombre del producto")
        unidad = st.selectbox("Unidad de medida", ["kg", "g", "L", "ml", "unidad"])
        precio = st.number_input("Precio de venta", min_value=0.0, step=0.1, format="%.2f")
        costo = st.number_input("Costo", min_value=0.0, step=0.1, format="%.2f")
        stock = st.number_input("Stock inicial", min_value=0.0, step=0.1, format="%.2f")
        guardar = st.form_submit_button("Guardar producto")

        if guardar:
            if nombre and unidad:
                try:
                    supabase.table("productos").insert({
                        "nombre": nombre,
                        "unidad": unidad,
                        "precio_venta": float(precio),
                        "costo": float(costo),
                        "stock": float(stock)
                    }).execute()
                    st.success("Producto guardado correctamente.")
                    st.experimental_rerun()
                except Exception as e:
                    st.error(f"Error al guardar: {e}")
            else:
                st.warning("Por favor complete todos los campos.")

elif opcion == "🚚 Insumos":
    st.title("🚚 Gestión de Insumos")

    # Mostrar insumos existentes
    st.subheader("Lista de insumos registrados")
    insumos = supabase.table("insumos").select("*").execute().data
    if insumos:
        df_insumos = pd.DataFrame(insumos)
        st.dataframe(df_insumos.drop(columns=["id"]), use_container_width=True)
    else:
        st.info("No hay insumos registrados.")

    # Formulario para agregar nuevo insumo
    st.subheader("Agregar nuevo insumo")

    with st.form("form_insumo"):
        nombre_insumo = st.text_input("Nombre del insumo")
        unidad_insumo = st.selectbox("Unidad de medida", ["kg", "g", "L", "ml", "unidad"])
        costo_unitario = st.number_input("Costo unitario", min_value=0.0, step=0.01, format="%.4f")
        cantidad = st.number_input("Cantidad inicial", min_value=0.0, step=0.1, format="%.2f")
        guardar_insumo = st.form_submit_button("Guardar insumo")

        if guardar_insumo:
            if nombre_insumo and unidad_insumo:
                try:
                    supabase.table("insumos").insert({
                        "nombre": nombre_insumo,
                        "unidad": unidad_insumo,
                        "costo_unitario": float(costo_unitario),
                        "cantidad": float(cantidad)
                    }).execute()
                    st.success("Insumo guardado correctamente.")
                    st.experimental_rerun()
                except Exception as e:
                    st.error(f"Error al guardar insumo: {e}")
            else:
                st.warning("Por favor complete todos los campos.")

# =============================
# 📄 PESTAÑA DE RECETAS
# =============================
elif opcion == "📋 Recetas":
    st.title("📋 Gestión de Recetas")

    # Mostrar recetas existentes
    st.subheader("Recetas registradas")
    recetas = supabase.table("recetas").select("*").execute().data

    if recetas:
        df_recetas = pd.DataFrame(recetas)
        st.dataframe(df_recetas.drop(columns=["id"]), use_container_width=True)
    else:
        st.info("No hay recetas registradas.")

    st.divider()

    # Formulario para agregar receta
    st.subheader("Agregar nueva receta")
    with st.form("form_receta"):
        nombre_receta = st.text_input("Nombre de la receta")
        instrucciones = st.text_area("Instrucciones")
        insumos_disponibles = supabase.table("insumos").select("id,nombre,unidad").execute().data

        if insumos_disponibles:
            seleccionados = []
            for insumo in insumos_disponibles:
                cantidad = st.number_input(f"{insumo['nombre']} ({insumo['unidad']})", min_value=0.0, step=0.1, format="%.2f", key=insumo['id'])
                if cantidad > 0:
                    seleccionados.append({
                        "insumo_id": insumo["id"],
                        "cantidad": cantidad
                    })
        else:
            st.warning("No hay insumos registrados para asociar.")

        guardar_receta = st.form_submit_button("Guardar receta")

        if guardar_receta:
            if nombre_receta:
                try:
                    receta_insert = supabase.table("recetas").insert({
                        "nombre": nombre_receta,
                        "instrucciones": instrucciones
                    }).execute()
                    receta_id = receta_insert.data[0]["id"]

                    # Insertar insumos asociados
                    for item in seleccionados:
                        supabase.table("detalle_receta").insert({
                            "receta_id": receta_id,
                            "insumo_id": item["insumo_id"],
                            "cantidad": item["cantidad"]
                        }).execute()

                    st.success("Receta guardada correctamente.")
                    st.experimental_rerun()
                except Exception as e:
                    st.error(f"Error al guardar receta: {e}")
            else:
                st.warning("El nombre de la receta es obligatorio.")

# =============================
# 💰 PESTAÑA DE VENTAS
# =============================
elif opcion == "💰 Ventas":
    st.title("💰 Registro de Ventas")

    productos = supabase.table("productos").select("*").execute().data
    if not productos:
        st.warning("Primero debes registrar productos.")
        st.stop()

    productos_dict = {p["nombre"]: p for p in productos}
    nombre_producto = st.selectbox("Selecciona un producto", list(productos_dict.keys()))
    cantidad_vendida = st.number_input("Cantidad vendida", min_value=0.01, step=0.1, format="%.2f")
    fecha_venta = st.date_input("Fecha de la venta")

    if st.button("Registrar venta"):
        producto = productos_dict[nombre_producto]
        ingreso = float(producto["precio_venta"]) * cantidad_vendida
        costo = float(producto["costo"]) * cantidad_vendida
        ganancia = ingreso - costo

        try:
            supabase.table("ventas").insert({
                "producto": producto["nombre"],
                "unidad": producto["unidad"],
                "cantidad": cantidad_vendida,
                "ingreso": ingreso,
                "costo": costo,
                "ganancia": ganancia,
                "fecha": fecha_venta.isoformat()
            }).execute()

            st.success("✅ Venta registrada correctamente.")
            st.experimental_rerun()
        except Exception as e:
            st.error(f"Error al registrar venta: {e}")

    st.markdown("### 📋 Historial de Ventas")
    ventas = supabase.table("ventas").select("*").order("fecha", desc=True).execute().data

    if ventas:
        df = pd.DataFrame(ventas)
        df["fecha"] = pd.to_datetime(df["fecha"]).dt.strftime("%d/%m/%Y")
        df = df.rename(columns={
            "producto": "Producto", "unidad": "Unidad", "cantidad": "Cantidad",
            "ingreso": "Ingreso (₡)", "costo": "Costo (₡)", "ganancia": "Ganancia (₡)", "fecha": "Fecha"
        })
        st.dataframe(df[["Fecha", "Producto", "Unidad", "Cantidad", "Ingreso (₡)", "Costo (₡)", "Ganancia (₡)"]],
                     use_container_width=True)
    else:
        st.info("No hay ventas registradas aún.")

# =============================
# 📊 PESTAÑA DE BALANCE GENERAL
# =============================
elif opcion == "📊 Balance General":
    st.title("📊 Balance General del Negocio")

    ventas = supabase.table("ventas").select("*").execute().data

    if ventas:
        df = pd.DataFrame(ventas)
        df["fecha"] = pd.to_datetime(df["fecha"])

        total_ingreso = df["ingreso"].sum()
        total_costo = df["costo"].sum()
        total_ganancia = df["ganancia"].sum()

        col1, col2, col3 = st.columns(3)
        col1.metric("💰 Ingresos totales", f"₡{total_ingreso:,.2f}")
        col2.metric("💸 Costos totales", f"₡{total_costo:,.2f}")
        col3.metric("📈 Ganancia neta", f"₡{total_ganancia:,.2f}")

        st.markdown("### 📅 Resumen por día")
        df["fecha_str"] = df["fecha"].dt.strftime("%d/%m/%Y")
        resumen_diario = df.groupby("fecha_str")[["ingreso", "costo", "ganancia"]].sum().reset_index()
        resumen_diario = resumen_diario.rename(columns={
            "fecha_str": "Fecha",
            "ingreso": "Ingreso (₡)",
            "costo": "Costo (₡)",
            "ganancia": "Ganancia (₡)"
        })

        st.dataframe(resumen_diario, use_container_width=True)
    else:
        st.info("No hay ventas registradas aún para calcular el balance.")

# =============================
# 🔁 PESTAÑA DE ENTRADAS/SALIDAS
# =============================
elif opcion == "🔁 Entradas/Salidas":
    st.title("🔁 Registro de Entradas y Salidas")

    insumos = supabase.table("insumos").select("*").execute().data
    if not insumos:
        st.warning("Primero debés registrar insumos.")
        st.stop()

    nombres_insumos = {i["nombre"]: i for i in insumos}

    with st.form("form_movimiento"):
        tipo = st.selectbox("Tipo de movimiento", ["Entrada", "Salida"])
        insumo_nombre = st.selectbox("Selecciona un insumo", list(nombres_insumos.keys()))
        cantidad = st.number_input("Cantidad", min_value=0.01, step=0.1, format="%.2f")
        motivo = st.text_input("Motivo del movimiento (opcional)")
        registrar = st.form_submit_button("Registrar movimiento")

        if registrar:
            insumo = nombres_insumos[insumo_nombre]
            cantidad_actual = float(insumo["cantidad"])
            nueva_cantidad = cantidad_actual + cantidad if tipo == "Entrada" else cantidad_actual - cantidad

            if nueva_cantidad < 0:
                st.error("❌ No hay suficiente stock para esta salida.")
            else:
                try:
                    # Actualiza stock
                    supabase.table("insumos").update({"cantidad": nueva_cantidad}).eq("id", insumo["id"]).execute()

                    # Registra movimiento
                    supabase.table("movimientos").insert({
                        "insumo_id": insumo["id"],
                        "tipo": tipo,
                        "cantidad": cantidad,
                        "motivo": motivo
                    }).execute()

                    st.success("✅ Movimiento registrado correctamente.")
                    st.experimental_rerun()
                except Exception as e:
                    st.error(f"Error al registrar: {e}")

    st.markdown("### 📋 Historial reciente")
    movimientos = supabase.table("movimientos").select("*").order("fecha_hora", desc=True).limit(50).execute().data

    if movimientos:
        id_a_nombre = {i["id"]: i["nombre"] for i in insumos}
        df_mov = pd.DataFrame(movimientos)
        df_mov["Insumo"] = df_mov["insumo_id"].map(id_a_nombre)
        df_mov["Fecha"] = pd.to_datetime(df_mov["fecha_hora"]).dt.strftime("%d/%m/%Y %H:%M")
        st.dataframe(df_mov[["Fecha", "Insumo", "tipo", "cantidad", "motivo"]].rename(columns={
            "tipo": "Tipo", "cantidad": "Cantidad", "motivo": "Motivo"
        }), use_container_width=True)
    else:
        st.info("No hay movimientos registrados.")

