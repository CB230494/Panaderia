import streamlit as st
import pandas as pd
from bd_ingresar import (
    crear_tabla_productos,
    agregar_producto,
    obtener_productos,
    actualizar_producto,
    eliminar_producto
)

st.set_page_config(page_title="Panadería Moderna", layout="wide")
st.title("🥐 Sistema de Gestión - Panadería Moderna")

# Crear tabla al cargar
crear_tabla_productos()

# Tabs del menú superior
tabs = st.tabs(["🧁 Productos", "📦 Insumos", "📋 Recetas", "📤 Entradas/Salidas", "💰 Ventas", "📊 Balance"])

# =============================
# 🧁 PESTAÑA DE PRODUCTOS
# =============================
with tabs[0]:
    st.subheader("🧁 Gestión de Productos")

    # --- Formulario para agregar producto ---
    with st.form("form_producto"):
        st.markdown("### ➕ Agregar nuevo producto")
        nombre = st.text_input("📛 Nombre del producto")
        unidad = st.selectbox("📦 Unidad", ["unidad", "porción", "pieza", "queque", "paquete"])
        precio_venta = st.number_input("💰 Precio de venta (₡)", min_value=0.0, format="%.2f")
        costo = st.number_input("🧾 Costo de elaboración (₡)", min_value=0.0, format="%.2f")
        submitted = st.form_submit_button("🍞 Agregar")

        if submitted:
            if nombre and unidad:
                agregar_producto(nombre, unidad, precio_venta, costo)
                st.success(f"✅ Producto '{nombre}' agregado correctamente.")
                st.rerun()
            else:
                st.warning("⚠️ Debes completar todos los campos.")

    # --- Listado de productos ---
    st.markdown("### 📋 Lista de productos")
    productos = obtener_productos()

    if productos:
        df = pd.DataFrame(productos, columns=["ID", "Nombre", "Unidad", "Precio Venta", "Costo"])
        df["Ganancia (₡)"] = df["Precio Venta"] - df["Costo"]
        st.dataframe(df, use_container_width=True)

        # --- Edición o eliminación ---
        st.markdown("### ✏️ Editar o eliminar un producto")
        seleccion = st.selectbox("🔽 Seleccionar producto por nombre", df["Nombre"])
        seleccionado = df[df["Nombre"] == seleccion].iloc[0]

        with st.form("editar_producto"):
            nuevo_nombre = st.text_input("📛 Nombre", value=seleccionado["Nombre"])
            nueva_unidad = st.selectbox("📦 Unidad", ["unidad", "porción", "pieza", "queque", "paquete"],
                                         index=["unidad", "porción", "pieza", "queque", "paquete"].index(seleccionado["Unidad"]))
            nuevo_precio = st.number_input("💰 Precio de venta (₡)", value=float(seleccionado["Precio Venta"]), format="%.2f")
            nuevo_costo = st.number_input("🧾 Costo de elaboración (₡)", value=float(seleccionado["Costo"]), format="%.2f")

            col1, col2 = st.columns(2)
            with col1:
                actualizar = st.form_submit_button("✅ Actualizar")
            with col2:
                eliminar = st.form_submit_button("🗑️ Eliminar")

            if actualizar:
                actualizar_producto(seleccionado["ID"], nuevo_nombre, nueva_unidad, nuevo_precio, nuevo_costo)
                st.success("✅ Producto actualizado correctamente.")
                st.rerun()
            if eliminar:
                eliminar_producto(seleccionado["ID"])
                st.success("🗑️ Producto eliminado correctamente.")
                st.rerun()
    else:
        st.info("ℹ️ No hay productos registrados todavía.")

