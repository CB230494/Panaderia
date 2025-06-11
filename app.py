import streamlit as st
import pandas as pd
from exportar_pdf import generar_pdf_receta
from database.bd_ingresar import (
    # Productos
    crear_tabla_productos,
    agregar_producto,
    obtener_productos,
    actualizar_producto,
    eliminar_producto,

    # Insumos
    crear_tabla_insumos,
    agregar_insumo,
    obtener_insumos,
    actualizar_insumo,
    eliminar_insumo,

    # Recetas
    crear_tabla_recetas,
    agregar_receta,
    obtener_recetas,
    obtener_detalle_receta,
    eliminar_receta
)


st.set_page_config(page_title="Panadería Moderna", layout="wide")
st.title("🥐 Sistema de Gestión - Panadería Moderna")

# Crear tablas al iniciar
crear_tabla_productos()
crear_tabla_insumos()

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

        nombres_disponibles = [producto[1] for producto in productos]
        seleccion = st.selectbox("🔽 Seleccionar producto por nombre", nombres_disponibles)

        for producto in productos:
            if producto[1] == seleccion:
                id_producto = producto[0]
                nombre_original = producto[1]
                unidad_original = producto[2]
                precio_original = producto[3]
                costo_original = producto[4]
                break

        with st.form("editar_producto"):
            nuevo_nombre = st.text_input("🍥 Nombre", value=nombre_original)
            nueva_unidad = st.selectbox("📦 Unidad", ["unidad", "porción", "pieza", "queque", "paquete"],
                                        index=["unidad", "porción", "pieza", "queque", "paquete"].index(unidad_original))
            nuevo_precio = st.number_input("💰 Precio de venta (₡)", value=float(precio_original), format="%.2f")
            nuevo_costo = st.number_input("🧾 Costo de elaboración (₡)", value=float(costo_original), format="%.2f")

            col1, col2 = st.columns(2)
            with col1:
                actualizar = st.form_submit_button("✅ Actualizar")
            with col2:
                eliminar = st.form_submit_button("🗑️ Eliminar")

            if actualizar:
                actualizar_producto(id_producto, nuevo_nombre, nueva_unidad, nuevo_precio, nuevo_costo)
                st.success("✅ Producto actualizado correctamente.")
                st.rerun()
            if eliminar:
                eliminar_producto(id_producto)
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

    # Diccionario de unidades
    unidades_dict = {
        "Kilogramo (kg)": "kg",
        "Gramo (g)": "g",
        "Litro (l)": "l",
        "Mililitro (ml)": "ml",
        "Barra": "barra",
        "Unidad": "unidad"
    }

    # --- Formulario para agregar insumo ---
    with st.form("form_insumo"):
        st.markdown("### ➕ Agregar nuevo insumo")
        nombre_i = st.text_input("📛 Nombre del insumo")
        unidad_i_visible = st.selectbox("📐 Unidad", list(unidades_dict.keys()))
        unidad_i = unidades_dict[unidad_i_visible]
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

        # Mostrar unidad con nombre legible
        unidad_legible = {
            "kg": "Kilogramo (kg)",
            "g": "Gramo (g)",
            "l": "Litro (l)",
            "ml": "Mililitro (ml)",
            "barra": "Barra",
            "unidad": "Unidad"
        }
        df_i["Unidad"] = df_i["Unidad"].map(unidad_legible)

        # Calcular total
        df_i["Total (₡)"] = df_i["Costo Unitario"] * df_i["Cantidad"]
        st.dataframe(df_i, use_container_width=True)

        # --- Edición o eliminación ---
        st.markdown("### ✏️ Editar o eliminar un insumo")

        nombres_insumos = [insumo[1] for insumo in insumos]
        seleccion_i = st.selectbox("🔽 Seleccionar insumo por nombre", nombres_insumos)

        for insumo in insumos:
            if insumo[1] == seleccion_i:
                id_insumo = insumo[0]
                nombre_original = insumo[1]
                unidad_original = insumo[2]
                costo_original = insumo[3]
                cantidad_original = insumo[4]
                break

        unidad_visible_original = [k for k, v in unidades_dict.items() if v == unidad_original][0]

        with st.form("editar_insumo"):
            nuevo_nombre_i = st.text_input("📛 Nombre", value=nombre_original)
            nueva_unidad_visible = st.selectbox("📐 Unidad", list(unidades_dict.keys()),
                                                index=list(unidades_dict.keys()).index(unidad_visible_original))
            nueva_unidad = unidades_dict[nueva_unidad_visible]
            nuevo_costo_i = st.number_input("💰 Costo unitario (₡)", value=float(costo_original), format="%.2f")
            nueva_cantidad_i = st.number_input("📥 Cantidad", value=float(cantidad_original))

            col1, col2 = st.columns(2)
            with col1:
                actualizar_i = st.form_submit_button("✅ Actualizar")
            with col2:
                eliminar_i = st.form_submit_button("🗑️ Eliminar")

            if actualizar_i:
                actualizar_insumo(id_insumo, nuevo_nombre_i, nueva_unidad, nuevo_costo_i, nueva_cantidad_i)
                st.success("✅ Insumo actualizado correctamente.")
                st.rerun()
            if eliminar_i:
                eliminar_insumo(id_insumo)
                st.success("🗑️ Insumo eliminado correctamente.")
                st.rerun()
    else:
        st.info("ℹ️ No hay insumos registrados todavía.")
# =============================
# 📋 PESTAÑA DE RECETAS
# =============================
with tabs[2]:
    st.subheader("📋 Gestión de Recetas")
    crear_tabla_recetas()

    # --- Agregar nueva receta ---
    with st.form("form_receta"):
        st.markdown("### ➕ Crear nueva receta")

        nombre_receta = st.text_input("📛 Nombre de la receta")
        instrucciones = st.text_area("📖 Instrucciones de preparación")

        insumos = obtener_insumos()
        if not insumos:
            st.warning("⚠️ No hay insumos registrados. Agrega insumos primero.")
        else:
            st.markdown("### 🧺 Seleccionar ingredientes:")

            insumo_seleccionado = []
            for insumo in insumos:
                insumo_id = insumo[0]
                nombre = insumo[1]
                unidad = insumo[2]
                cantidad = st.number_input(f"{nombre} ({unidad})", min_value=0.0, step=0.1, key=f"insumo_{insumo_id}")
                if cantidad > 0:
                    insumo_seleccionado.append((insumo_id, cantidad))

            submitted_receta = st.form_submit_button("🍽️ Guardar receta")

            if submitted_receta:
                if nombre_receta and insumo_seleccionado:
                    agregar_receta(nombre_receta, instrucciones, insumo_seleccionado)
                    st.success(f"✅ Receta '{nombre_receta}' guardada correctamente.")
                    st.rerun()
                else:
                    st.warning("⚠️ Debes ingresar un nombre y al menos un insumo.")

    # --- Listado de recetas ---
    st.markdown("### 📋 Recetas registradas")
    recetas = obtener_recetas()

    if recetas:
        for receta in recetas:
            receta_id, nombre, instrucciones = receta
            detalles = obtener_detalle_receta(receta_id)

            # Calcular costo total
            costo_total = sum(cant * costo for _, cant, _, costo in detalles)

            with st.expander(f"🍰 {nombre} - Costo total: ₡{costo_total:,.2f}"):
                st.markdown(f"**📝 Instrucciones:** {instrucciones or 'Sin instrucciones.'}")
                st.markdown("**🧾 Ingredientes:**")
                for nombre_insumo, cantidad, unidad, costo_unitario in detalles:
                    st.markdown(f"- {nombre_insumo} — {cantidad} {unidad} — ₡{costo_unitario:,.2f} c/u")

                eliminar_btn = st.button(f"🗑️ Eliminar receta", key=f"eliminar_{receta_id}")
                if eliminar_btn:
                    eliminar_receta(receta_id)
                    st.success(f"🗑️ Receta '{nombre}' eliminada.")
                    st.rerun()
    else:
        st.info("ℹ️ No hay recetas registradas todavía.")

