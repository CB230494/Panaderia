import streamlit as st
from streamlit_option_menu import option_menu
from supabase import create_client, Client
import pandas as pd
from datetime import date

# Configuración de la página
st.set_page_config(page_title="Sistema de Panadería", layout="wide")
st.markdown("<h1 style='text-align: center;'>🧁 Sistema de Gestión de Panadería</h1>", unsafe_allow_html=True)

# Conexión con Supabase
url = "https://fuqenmijstetuwhdulax.supabase.co"
key = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImZ1cWVubWlqc3RldHV3aGR1bGF4Iiwicm9sZSI6ImFub24iLCJpYXQiOjE3NTMyODM4MzksImV4cCI6MjA2ODg1OTgzOX0.9JdF70hcLCVCa0-lCd7yoSFKtO72niZbahM-u2ycAVg"
supabase: Client = create_client(url, key)

# Menú lateral
with st.sidebar:
    opcion = option_menu(
        "📌 Menú Principal",
        ["🏠 Inicio", "📦 Productos", "🚚 Insumos", "📋 Recetas", "🔁 Entradas/Salidas", "💰 Ventas", "📊 Balance General"],
        icons=["house", "box", "truck", "list", "repeat", "dollar-sign", "bar-chart"],
        menu_icon="cast",
        default_index=0,
        orientation="vertical"
    )

# Página de inicio
if opcion == "🏠 Inicio":
    st.subheader("Bienvenido al sistema de gestión para panaderías")

    # Mostrar métricas generales
    productos = supabase.table("productos").select("*").execute().data
    insumos = supabase.table("insumos").select("*").execute().data
    ventas = supabase.table("ventas").select("*").execute().data

    col1, col2, col3 = st.columns(3)
    col1.metric("Productos", len(productos))
    col2.metric("Insumos", len(insumos))
    col3.metric("Ventas", len(ventas))
elif opcion == "📦 Productos":
    st.title("📦 Gestión de Productos")

    st.subheader("Registrar nuevo producto")
    with st.form("form_producto"):
        nombre = st.text_input("Nombre del producto")
        unidad = st.selectbox("Unidad de medida", ["unidad", "kg", "g", "l", "ml"])
        precio_venta = st.number_input("Precio de venta (₡)", min_value=0.0, step=0.01, format="%.2f")
        costo = st.number_input("Costo unitario (₡)", min_value=0.0, step=0.01, format="%.2f")
        stock = st.number_input("Stock actual", min_value=0.0, step=0.01, format="%.2f")
        guardar = st.form_submit_button("Guardar producto")

        if guardar:
            if nombre and precio_venta > 0:
                try:
                    supabase.table("productos").insert({
                        "nombre": nombre,
                        "unidad": unidad,
                        "precio_venta": precio_venta,
                        "costo": costo,
                        "stock": stock
                    }).execute()
                    st.success("✅ Producto guardado correctamente.")
                    st.experimental_rerun()
                except Exception as e:
                    st.error(f"Error al guardar: {e}")
            else:
                st.warning("Debe completar todos los campos obligatorios.")

    st.divider()
    st.subheader("📋 Lista de productos")
    productos = supabase.table("productos").select("*").execute().data

    if productos:
        df = pd.DataFrame(productos)
        df = df.rename(columns={
            "nombre": "Nombre", "unidad": "Unidad", "precio_venta": "Precio Venta (₡)",
            "costo": "Costo (₡)", "stock": "Stock"
        })
        st.dataframe(df[["Nombre", "Unidad", "Precio Venta (₡)", "Costo (₡)", "Stock"]],
                     use_container_width=True)
    else:
        st.info("No hay productos registrados.")
elif opcion == "🚚 Insumos":
    st.title("🚚 Gestión de Insumos")

    st.subheader("Registrar nuevo insumo")
    with st.form("form_insumo"):
        nombre = st.text_input("Nombre del insumo")
        unidad = st.selectbox("Unidad de medida", ["kg", "g", "l", "ml", "unidad"])
        costo_unitario = st.number_input("Costo unitario (₡)", min_value=0.0, step=0.01, format="%.4f")
        cantidad = st.number_input("Cantidad actual", min_value=0.0, step=0.1, format="%.2f")
        guardar = st.form_submit_button("Guardar insumo")

        if guardar:
            if nombre and costo_unitario > 0:
                try:
                    supabase.table("insumos").insert({
                        "nombre": nombre,
                        "unidad": unidad,
                        "costo_unitario": costo_unitario,
                        "cantidad": cantidad
                    }).execute()
                    st.success("✅ Insumo guardado correctamente.")
                    st.experimental_rerun()
                except Exception as e:
                    st.error(f"Error al guardar: {e}")
            else:
                st.warning("Debe completar todos los campos obligatorios.")

    st.divider()
    st.subheader("📋 Lista de insumos")
    insumos = supabase.table("insumos").select("*").execute().data

    if insumos:
        df = pd.DataFrame(insumos)
        df = df.rename(columns={
            "nombre": "Nombre", "unidad": "Unidad", "costo_unitario": "Costo Unitario (₡)", "cantidad": "Cantidad"
        })
        st.dataframe(df[["Nombre", "Unidad", "Costo Unitario (₡)", "Cantidad"]],
                     use_container_width=True)
    else:
        st.info("No hay insumos registrados.")
elif opcion == "📋 Recetas":
    st.title("📋 Gestión de Recetas")

    st.subheader("Crear nueva receta")
    with st.form("form_receta"):
        nombre_receta = st.text_input("Nombre de la receta")
        instrucciones = st.text_area("Instrucciones")
        guardar_receta = st.form_submit_button("Guardar receta")

        if guardar_receta:
            if nombre_receta:
                try:
                    supabase.table("recetas").insert({
                        "nombre": nombre_receta,
                        "instrucciones": instrucciones
                    }).execute()
                    st.success("✅ Receta guardada correctamente.")
                    st.experimental_rerun()
                except Exception as e:
                    st.error(f"Error al guardar la receta: {e}")
            else:
                st.warning("Debe indicar el nombre de la receta.")

    st.divider()
    st.subheader("📋 Lista de recetas")
    recetas = supabase.table("recetas").select("*").execute().data

    if recetas:
        receta_dict = {r["nombre"]: r["id"] for r in recetas}
        receta_seleccionada = st.selectbox("Selecciona una receta para ver sus detalles", list(receta_dict.keys()))

        receta_id = receta_dict[receta_seleccionada]
        detalle = supabase.table("detalle_receta").select("*, insumos(nombre, unidad)").eq("receta_id", receta_id).execute().data

        if detalle:
            detalle_df = pd.DataFrame([{
                "Insumo": d["insumos"]["nombre"],
                "Unidad": d["insumos"]["unidad"],
                "Cantidad": d["cantidad"]
            } for d in detalle])
            st.dataframe(detalle_df, use_container_width=True)
        else:
            st.info("Esta receta aún no tiene insumos asignados.")
    else:
        st.info("No hay recetas registradas.")
elif opcion == "🔁 Entradas/Salidas":
    st.title("🔁 Registro de Entradas y Salidas de Insumos")

    insumos = supabase.table("insumos").select("id, nombre").execute().data
    if not insumos:
        st.warning("Primero debes registrar insumos.")
    else:
        insumo_dict = {i["nombre"]: i["id"] for i in insumos}

        with st.form("form_movimiento"):
            tipo = st.radio("Tipo de movimiento", ["Entrada", "Salida"], horizontal=True)
            insumo_nombre = st.selectbox("Selecciona el insumo", list(insumo_dict.keys()))
            cantidad = st.number_input("Cantidad", min_value=0.01, step=0.1, format="%.2f")
            motivo = st.text_input("Motivo del movimiento (opcional)")
            registrar = st.form_submit_button("Registrar movimiento")

            if registrar:
                insumo_id = insumo_dict[insumo_nombre]

                # Consultar cantidad actual
                actual = supabase.table("insumos").select("cantidad").eq("id", insumo_id).single().execute().data["cantidad"]
                nueva_cantidad = actual + cantidad if tipo == "Entrada" else actual - cantidad

                if nueva_cantidad < 0:
                    st.error("❌ No hay suficiente stock para realizar la salida.")
                else:
                    try:
                        supabase.table("movimientos").insert({
                            "insumo_id": insumo_id,
                            "tipo": tipo,
                            "cantidad": cantidad,
                            "motivo": motivo
                        }).execute()

                        supabase.table("insumos").update({"cantidad": nueva_cantidad}).eq("id", insumo_id).execute()
                        st.success("✅ Movimiento registrado correctamente.")
                        st.experimental_rerun()
                    except Exception as e:
                        st.error(f"Error: {e}")

    st.divider()
    st.subheader("📋 Historial de movimientos")
    movimientos = supabase.table("movimientos").select("*, insumos(nombre)").order("fecha_hora", desc=True).limit(20).execute().data

    if movimientos:
        df = pd.DataFrame([{
            "Fecha y hora": m["fecha_hora"],
            "Insumo": m["insumos"]["nombre"],
            "Tipo": m["tipo"],
            "Cantidad": m["cantidad"],
            "Motivo": m["motivo"]
        } for m in movimientos])
        st.dataframe(df, use_container_width=True)
    else:
        st.info("No hay movimientos registrados.")
elif opcion == "💰 Ventas":
    st.title("💰 Registro de Ventas")

    productos = supabase.table("productos").select("*").execute().data
    if not productos:
        st.warning("Primero debes registrar productos.")
    else:
        producto_dict = {p["nombre"]: p for p in productos}
        nombre_producto = st.selectbox("Selecciona un producto", list(producto_dict.keys()))
        cantidad_vendida = st.number_input("Cantidad vendida", min_value=0.01, step=0.1, format="%.2f")
        fecha_venta = st.date_input("Fecha de la venta", value=date.today())

        if st.button("Registrar venta"):
            producto = producto_dict[nombre_producto]
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

    st.divider()
    st.subheader("📋 Historial de Ventas")
    ventas = supabase.table("ventas").select("*").order("fecha", desc=True).execute().data

    if ventas:
        df = pd.DataFrame(ventas)
        df["fecha"] = pd.to_datetime(df["fecha"]).dt.strftime("%d/%m/%Y")
        df = df.rename(columns={
            "fecha": "Fecha", "producto": "Producto", "unidad": "Unidad", "cantidad": "Cantidad",
            "ingreso": "Ingreso (₡)", "costo": "Costo (₡)", "ganancia": "Ganancia (₡)"
        })
        st.dataframe(df[["Fecha", "Producto", "Unidad", "Cantidad", "Ingreso (₡)", "Costo (₡)", "Ganancia (₡)"]],
                     use_container_width=True)
    else:
        st.info("No hay ventas registradas.")
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
        col1.metric("💰 Ingreso total", f"₡{total_ingreso:,.2f}")
        col2.metric("💸 Costo total", f"₡{total_costo:,.2f}")
        col3.metric("📈 Ganancia neta", f"₡{total_ganancia:,.2f}")

        st.markdown("### 📅 Resumen por fecha")
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
        st.info("No hay ventas registradas para mostrar el balance.")

