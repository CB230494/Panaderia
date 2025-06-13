import streamlit as st
from streamlit_option_menu import option_menu
import pandas as pd
from pathlib import Path
from datetime import datetime  # Para entradas/salidas
from exportar_pdf import generar_pdf_receta
from database.bd_ingresar import (
    crear_tabla_productos, agregar_producto, obtener_productos, actualizar_producto, eliminar_producto,
    crear_tabla_insumos, agregar_insumo, obtener_insumos, actualizar_insumo, eliminar_insumo,
    crear_tabla_recetas, agregar_receta, obtener_recetas, obtener_detalle_receta, eliminar_receta,
    crear_tabla_entradas_salidas, registrar_movimiento, obtener_historial_movimientos
)

# === CONFIGURACIÓN GENERAL ===
st.set_page_config(page_title="Panadería Moderna", layout="wide")

# === INICIALIZAR ESTADO DE NAVEGACIÓN ===
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

# === CREAR TABLAS AL INICIAR ===
crear_tabla_productos()
crear_tabla_insumos()
crear_tabla_recetas()
crear_tabla_entradas_salidas()
# =============================
# 🏠 PÁGINA DE INICIO
# =============================
if st.session_state.pagina == "Inicio":
    st.title("👨‍🍳 Sistema de Gestión - Panadería Moderna")
    st.markdown("""
    Bienvenido al sistema de gestión para tu panadería.  
    Desde aquí puedes controlar tus productos, insumos, recetas, entradas y salidas, ventas y balance.
    
    Usa el menú lateral para navegar entre las diferentes secciones.  
    """)

    st.markdown("---")
    st.markdown("### 🔍 ¿Qué deseas hacer hoy?")

    col1, col2, col3 = st.columns(3)

    with col1:
        if st.button("📦 Ir a Productos"):
            st.session_state.pagina = "Productos"
            st.rerun()
    with col2:
        if st.button("🚚 Ir a Insumos"):
            st.session_state.pagina = "Insumos"
            st.rerun()
    with col3:
        if st.button("📋 Ir a Recetas"):
            st.session_state.pagina = "Recetas"
            st.rerun()
# =============================
# 📦 PESTAÑA DE PRODUCTOS
# =============================
if st.session_state.pagina == "Productos":
    st.subheader("📦 Gestión de Productos")

    with st.form("form_producto"):
        nombre_p = st.text_input("Nombre del producto")
        unidad_p = st.selectbox("Unidad", ["unidad", "paquete", "docena"])
        precio_venta = st.number_input("Precio de venta (₡)", min_value=0.0, format="%.2f")
        costo = st.number_input("Costo (₡)", min_value=0.0, format="%.2f")
        stock = st.number_input("Cantidad en stock", min_value=0)
        submitted_p = st.form_submit_button("Agregar")

        if submitted_p:
            if nombre_p:
                agregar_producto(nombre_p, unidad_p, precio_venta, costo, stock)
                st.success(f"✅ Producto '{nombre_p}' agregado correctamente.")
                st.rerun()
            else:
                st.error("❌ El nombre del producto no puede estar vacío.")

    st.markdown("### 📋 Productos registrados")
    productos = obtener_productos()
    if productos:
        df_productos = pd.DataFrame(productos, columns=["ID", "Nombre", "Unidad", "Precio Venta", "Costo", "Stock"])
        df_productos = df_productos.drop(columns=["ID"])
        st.dataframe(df_productos, use_container_width=True)
    else:
        st.info("📭 No hay productos registrados.")
# =============================
# 🚚 PESTAÑA DE INSUMOS
# =============================
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

    conversiones = {
        "kg": 1000,
        "l": 1000,
        "g": 1,
        "ml": 1,
        "barra": 1,
        "unidad": 1
    }

    with st.form("form_agregar_insumo"):
        st.markdown("### ➕ Agregar nuevo insumo")
        nombre_i = st.text_input("Nombre del insumo")
        unidad_i_visible = st.selectbox("Unidad", list(unidades_dict.keys()))
        unidad_i = unidades_dict[unidad_i_visible]
        costo_total = st.number_input("Costo total (₡)", min_value=0.0, format="%.2f")
        cantidad_total = st.number_input("Cantidad total adquirida", min_value=0.0)
        submitted_i = st.form_submit_button("Agregar")

        if submitted_i:
            if nombre_i and unidad_i and cantidad_total > 0:
                factor = conversiones.get(unidad_i, 1)
                costo_unitario = round(costo_total / (cantidad_total * factor), 4)
                cantidad_guardar = round(cantidad_total * factor, 2)
                agregar_insumo(nombre_i, unidad_i, costo_unitario, cantidad_guardar)
                st.success(f"✅ Insumo '{nombre_i}' agregado correctamente.")
                st.rerun()
            else:
                st.error("❌ Completa todos los campos correctamente.")

    st.markdown("### 📋 Insumos registrados")
    insumos = obtener_insumos()
    if insumos:
        df_insumos = pd.DataFrame(insumos, columns=["ID", "Nombre", "Unidad", "₡ x unidad base", "Cantidad disponible"])
        df_insumos["₡ x unidad base"] = df_insumos["₡ x unidad base"].apply(lambda x: f"{x:,.2f}")
        df_insumos["Cantidad disponible"] = df_insumos["Cantidad disponible"].apply(lambda x: f"{x:,.2f}")
        df_insumos = df_insumos.drop(columns=["ID"])
        st.dataframe(df_insumos, use_container_width=True)
    else:
        st.info("📭 No hay insumos registrados.")
# =============================
# 📋 PESTAÑA DE RECETAS
# =============================
if st.session_state.pagina == "Recetas":
    st.subheader("📋 Gestión de Recetas")

    insumos = obtener_insumos()
    if not insumos:
        st.warning("⚠️ Primero debes registrar insumos.")
        st.stop()

    if "ingredientes_receta" not in st.session_state:
        st.session_state.ingredientes_receta = []

    st.markdown("### ➕ Agregar Ingredientes a la Receta")

    opciones_insumos = [f"{i[1]} ({i[2]})" for i in insumos]
    insumo_seleccionado = st.selectbox("Selecciona insumo", opciones_insumos)
    cantidad_usada = st.number_input("Cantidad a utilizar", min_value=0.0, step=0.1)
    agregar_ingrediente = st.button("Agregar ingrediente")

    if agregar_ingrediente:
        index = opciones_insumos.index(insumo_seleccionado)
        insumo_id, nombre_insumo, unidad, costo_unitario, cantidad_disponible = insumos[index]
        costo_total = round(cantidad_usada * costo_unitario, 4)
        st.session_state.ingredientes_receta.append({
            "nombre": nombre_insumo,
            "cantidad": cantidad_usada,
            "unidad": unidad,
            "costo_unitario": costo_unitario,
            "costo_total": costo_total
        })
        st.success(f"✅ Ingrediente '{nombre_insumo}' agregado.")
        st.rerun()

    if st.session_state.ingredientes_receta:
        st.markdown("### 🧾 Ingredientes agregados")
        df_ingredientes = pd.DataFrame(st.session_state.ingredientes_receta)
        df_ingredientes["costo_unitario"] = df_ingredientes["costo_unitario"].apply(lambda x: f"₡{x:,.2f}")
        df_ingredientes["costo_total"] = df_ingredientes["costo_total"].apply(lambda x: f"₡{x:,.2f}")
        st.dataframe(df_ingredientes, use_container_width=True)

    st.markdown("### 📝 Finalizar Receta")

    nombre_receta = st.text_input("Nombre de la receta")
    instrucciones = st.text_area("Instrucciones")
    guardar_receta = st.button("Guardar Receta")

    if guardar_receta:
        if not nombre_receta:
            st.error("❌ El nombre de la receta es obligatorio.")
        elif not st.session_state.ingredientes_receta:
            st.error("❌ Agrega al menos un ingrediente.")
        else:
            costo_total = sum(item["costo_total"] for item in st.session_state.ingredientes_receta)
            st.success(f"✅ Receta '{nombre_receta}' guardada. Costo estimado total: ₡{costo_total:,.2f}")
            st.session_state.ingredientes_receta = []
            st.rerun()
# =============================
# 📤 PESTAÑA DE ENTRADAS Y SALIDAS
# =============================
if st.session_state.pagina == "Entradas/Salidas":
    st.subheader("📤 Registro de Entradas y Salidas de Insumos")

    insumos = obtener_insumos()
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

    nombres_insumos = [f"{i[1]} ({i[2]})" for i in insumos]
    insumo_elegido = st.selectbox("🔽 Selecciona el insumo", nombres_insumos)

    index = nombres_insumos.index(insumo_elegido)
    insumo_id, nombre, unidad, costo_unitario, cantidad_actual = insumos[index]
    unidad_visible = unidad_legible.get(unidad, unidad)

    st.markdown(f"**📦 Cantidad disponible:** {cantidad_actual:.2f} {unidad_visible}")

    tipo_movimiento = st.radio("📌 Tipo de movimiento", ["Entrada", "Salida"], horizontal=True)
    cantidad = st.number_input("📏 Cantidad a registrar", min_value=0.0, step=0.1)
    motivo = st.text_input("✏️ Motivo (opcional)")
    registrar = st.button("💾 Registrar movimiento")

    if registrar:
        if tipo_movimiento == "Salida" and cantidad > cantidad_actual:
            st.error("❌ No hay suficiente stock para realizar la salida.")
        else:
            from datetime import datetime
            fecha_hora = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            registrar_movimiento(insumo_id, tipo_movimiento, cantidad, fecha_hora, motivo)
            st.success(f"✅ {tipo_movimiento} registrada correctamente.")
            st.rerun()

    historial = obtener_historial_movimientos()
    if historial:
        st.markdown("### 📜 Historial de Movimientos")
        df_hist = pd.DataFrame(historial, columns=["ID", "Insumo", "Tipo", "Cantidad", "Fecha y Hora", "Motivo"])
        df_hist = df_hist.drop(columns=["ID"])
        st.dataframe(df_hist, use_container_width=True)

    # Verificación de bajo stock
    st.markdown("### 🚨 Insumos con stock bajo")
    bajo_stock = [i for i in insumos if i[4] < 3]
    if bajo_stock:
        df_bajo = pd.DataFrame(bajo_stock, columns=["ID", "Nombre", "Unidad", "₡ x unidad", "Cantidad disponible"])
        df_bajo["₡ x unidad"] = df_bajo["₡ x unidad"].apply(lambda x: f"{x:,.2f}")
        df_bajo["Cantidad disponible"] = df_bajo["Cantidad disponible"].apply(lambda x: f"{x:,.2f}")
        df_bajo = df_bajo.drop(columns=["ID"])
        st.warning("⚠️ Tienes insumos con menos de 3 unidades.")
        st.dataframe(df_bajo, use_container_width=True)
    else:
        st.success("✅ Todos los insumos tienen suficiente stock.")



# =============================
# 💰 PESTAÑA DE VENTAS
# =============================
with tabs[4]:
    st.subheader("💰 Registro de Ventas de Productos")

    productos = obtener_productos()
    if not productos:
        st.warning("⚠️ No hay productos disponibles. Agrega primero desde la pestaña de Productos.")
    else:
        nombres_productos = [f"{p[1]} ({p[2]})" for p in productos]
        producto_elegido = st.selectbox("🧁 Selecciona el producto vendido", nombres_productos)

        index = nombres_productos.index(producto_elegido)
        id_producto, nombre, unidad, precio_venta, costo_unitario = productos[index]

        st.markdown(f"**💵 Precio de venta:** ₡{precio_venta:,.2f}")
        st.markdown(f"**🧾 Costo de elaboración:** ₡{costo_unitario:,.2f}")

        cantidad_vendida = st.number_input("📦 Cantidad vendida", min_value=0.0, step=0.1)
        registrar_venta = st.button("💾 Registrar venta")

        if "ventas" not in st.session_state:
            st.session_state.ventas = []

        if registrar_venta:
            ingreso_total = cantidad_vendida * precio_venta
            costo_total = cantidad_vendida * costo_unitario
            ganancia_total = ingreso_total - costo_total

            st.session_state.ventas.append({
                "Producto": nombre,
                "Unidad": unidad,
                "Cantidad": cantidad_vendida,
                "Ingreso (₡)": ingreso_total,
                "Costo (₡)": costo_total,
                "Ganancia (₡)": ganancia_total
            })

            st.success("✅ Venta registrada correctamente.")
            st.rerun()

    # Mostrar resumen de ventas realizadas en la sesión
    if "ventas" in st.session_state and st.session_state.ventas:
        st.markdown("### 📋 Ventas registradas (sesión actual)")
        df_ventas = pd.DataFrame(st.session_state.ventas)
        st.dataframe(df_ventas, use_container_width=True)

        total_ingresos = df_ventas["Ingreso (₡)"].sum()
        total_ganancias = df_ventas["Ganancia (₡)"].sum()

        st.markdown(f"**💵 Total ingresos:** ₡{total_ingresos:,.2f}")
        st.markdown(f"**📈 Total ganancias:** ₡{total_ganancias:,.2f}")
# =============================
# 📊 PESTAÑA DE BALANCE
# =============================
with tabs[5]:
    st.subheader("📊 Balance General del Negocio")

    # ==== Inventario de Insumos ====
    insumos = obtener_insumos()
    if insumos:
        df_insumos = pd.DataFrame(insumos, columns=["ID", "Nombre", "Unidad", "Costo Unitario", "Cantidad"])
        df_insumos["Total (₡)"] = df_insumos["Costo Unitario"] * df_insumos["Cantidad"]
        total_inventario = df_insumos["Total (₡)"].sum()

        st.markdown("### 📦 Valor del inventario de insumos")
        st.dataframe(df_insumos[["Nombre", "Unidad", "Cantidad", "Costo Unitario", "Total (₡)"]], use_container_width=True)
        st.markdown(f"**🔹 Total inventario:** ₡{total_inventario:,.2f}")
    else:
        st.info("ℹ️ No hay insumos registrados.")

    st.divider()

    # ==== Resumen de Ventas ====
    st.markdown("### 💰 Ventas registradas en esta sesión")

    if "ventas" in st.session_state and st.session_state.ventas:
        df_ventas = pd.DataFrame(st.session_state.ventas)
        st.dataframe(df_ventas, use_container_width=True)

        total_ingresos = df_ventas["Ingreso (₡)"].sum()
        total_ganancia = df_ventas["Ganancia (₡)"].sum()
        total_costos = df_ventas["Costo (₡)"].sum()

        st.markdown(f"- **🟢 Ingresos:** ₡{total_ingresos:,.2f}")
        st.markdown(f"- **🧾 Costos:** ₡{total_costos:,.2f}")
        st.markdown(f"- **📈 Ganancia total:** ₡{total_ganancia:,.2f}")
    else:
        st.info("ℹ️ No hay ventas registradas en esta sesión.")

    st.divider()

    # ==== Comparativo Básico ====
    if insumos and "ventas" in st.session_state and st.session_state.ventas:
        st.markdown("### 📉 Comparativo resumen")
        st.markdown(f"🔸 **Valor actual del inventario:** ₡{total_inventario:,.2f}")
        st.markdown(f"🔸 **Ganancia generada (ventas - costos):** ₡{total_ganancia:,.2f}")
        balance_total = total_ingresos - total_inventario
        st.markdown(f"🔸 **Balance estimado (ingresos - inventario):** ₡{balance_total:,.2f}")


