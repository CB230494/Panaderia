import streamlit as st
import pandas as pd
from bd_ingresar import (
    crear_tabla_productos,
    agregar_producto,
    obtener_productos,
    actualizar_producto,
    eliminar_producto,
    crear_tabla_insumos,
    agregar_insumo,
    obtener_insumos,
    actualizar_insumo,
    eliminar_insumo
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

# =============================
# 📦 PESTAÑA DE INSUMOS
# =============================
with tabs[1]:
    st.subheader("📦 Gestión de Insumos")
    crear_tabla_insumos()

    # --- Formulario para agregar insumo ---
    with st.form("form_insumo"):
        st.markdown("### ➕ Agregar nuevo insumo")
        nombre_i = st.text_input("📛 Nombre del insumo")
        unidad_i = st.selectbox("📐 Unidad", ["kg", "g", "l", "ml", "barra", "unidad"])
        costo_unitario = st.number_input("💰 Costo unitario (₡)", min_value=0.0, format="%.2f")
        cantidad = st.number_input("📥 Cantidad inicial", min_value=0.0)
        submitted_i = st.form_submit_button("📦 Agregar")

        if submitted_i:
            if nombre_i and unidad_i:
                agregar_insumo(nombre_i, unidad_i, costo_unitario, cantidad)
                st.success(f"✅ Insumo '{nombre_i}' agregado correctamente.")
                st.rerun()
            else:
                st.warning("⚠️ Debes completar todos los campos.")

    # --- Listado de insumos ---
    st.markdown("### 📋 Lista de insumos")
    insumos = obtener_insumos()

    if insumos:
        df_i = pd.DataFrame(insumos, columns=["ID", "Nombre", "Unidad", "Costo Unitario", "Cantidad"])
        df_i["Total (₡)"] = df_i["Costo Unitario"] * df_i["Cantidad"]
        st.dataframe(df_i, use_container_width=True)

        # --- Edición o eliminación ---
        st.markdown("### ✏️ Editar o eliminar un insumo")
        seleccion_i = st.selectbox("🔽 Seleccionar insumo por nombre", df_i["Nombre"])
        seleccionado_i = df_i[df_i["Nombre"] == seleccion_i].iloc[0]

        with st.form("editar_insumo"):
            nuevo_nombre_i = st.text_input("📛 Nombre", value=seleccionado_i["Nombre"])
            nueva_unidad_i = st.selectbox("📐 Unidad", ["kg", "g", "l", "ml", "barra", "unidad"],
                                           index=["kg", "g", "l", "ml", "barra", "unidad"].index(seleccionado_i["Unidad"]))
            nuevo_costo_i = st.number_input("💰 Costo unitario (₡)", value=float(seleccionado_i["Costo Unitario"]), format="%.2f")
            nueva_cantidad_i = st.number_input("📥 Cantidad", value=float(seleccionado_i["Cantidad"]))

            col1, col2 = st.columns(2)
            with col1:
                actualizar_i = st.form_submit_button("✅ Actualizar")
            with col2:
                eliminar_i = st.form_submit_button("🗑️ Eliminar")

            if actualizar_i:
                actualizar_insumo(seleccionado_i["ID"], nuevo_nombre_i, nueva_unidad_i, nuevo_costo_i, nueva_cantidad_i)
                st.success("✅ Insumo actualizado correctamente.")
                st.rerun()
            if eliminar_i:
                eliminar_insumo(seleccionado_i["ID"])
                st.success("🗑️ Insumo eliminado correctamente.")
                st.rerun()
    else:
        st.info("ℹ️ No hay insumos registrados todavía.")

