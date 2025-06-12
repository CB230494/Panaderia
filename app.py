import streamlit as st
import pandas as pd
from pathlib import Path
from exportar_pdf import generar_pdf_receta  # Asegurate de tener este archivo en tu proyecto
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
    with st.form("form_agregar_producto"):
        st.markdown("### ➕ Agregar nuevo producto")
        nombre = st.text_input("📛 Nombre del producto")
        unidad = st.selectbox("📦 Unidad", ["unidad", "porción", "pieza", "queque", "paquete"])
        precio_venta = st.number_input("💰 Precio de venta (₡)", min_value=0.0, format="%.2f")
        costo = st.number_input("🧾 Costo de elaboración (₡)", min_value=0.0, format="%.2f")
        stock = st.number_input("📦 Cantidad en stock", min_value=0, step=1)
        submitted = st.form_submit_button("🍞 Agregar")

        if submitted:
            if nombre and unidad:
                agregar_producto(nombre, unidad, precio_venta, costo, stock)
                st.success(f"✅ Producto '{nombre}' agregado correctamente.")
                st.rerun()
            else:
                st.warning("⚠️ Debes completar todos los campos.")

    # --- Listado de productos ---
    st.markdown("### 📋 Lista de productos")
    productos = obtener_productos()

    if productos:
        df = pd.DataFrame(productos, columns=["ID", "Nombre", "Unidad", "Precio Venta", "Costo", "Stock"])
        df["Ganancia (₡)"] = df["Precio Venta"] - df["Costo"]

        def color_stock(val):
            color = 'background-color: red; color: white' if val < 5 else ''
            return color

        styled_df = df.style.applymap(color_stock, subset=["Stock"])
        st.dataframe(styled_df, use_container_width=True)

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
                stock_original = producto[5]
                break

        with st.form("form_editar_producto"):
            nuevo_nombre = st.text_input("🍥 Nombre", value=nombre_original)
            nueva_unidad = st.selectbox("📦 Unidad", ["unidad", "porción", "pieza", "queque", "paquete"],
                                        index=["unidad", "porción", "pieza", "queque", "paquete"].index(unidad_original))
            nuevo_precio = st.number_input("💰 Precio de venta (₡)", value=float(precio_original), format="%.2f")
            nuevo_costo = st.number_input("🧾 Costo de elaboración (₡)", value=float(costo_original), format="%.2f")
            nuevo_stock = st.number_input("📦 Stock disponible", value=int(stock_original), step=1)

            col1, col2 = st.columns(2)
            with col1:
                actualizar = st.form_submit_button("✅ Actualizar")
            with col2:
                eliminar = st.form_submit_button("🗑️ Eliminar")

            if actualizar:
                actualizar_producto(id_producto, nuevo_nombre, nueva_unidad, nuevo_precio, nuevo_costo, nuevo_stock)
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
    with st.form("form_agregar_insumo"):
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
        unidad_legible = {v: k for k, v in unidades_dict.items()}
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

        with st.form("form_editar_insumo"):
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

    # ========================
    # ➕ Crear nueva receta
    # ========================
    with st.form("form_nueva_receta"):  # clave única
        st.markdown("### ➕ Crear nueva receta")

        nombre_receta = st.text_input("📛 Nombre de la receta")
        instrucciones = st.text_area("📖 Instrucciones de preparación")
        imagen_receta = st.file_uploader("📷 Foto del producto final (opcional)", type=["png", "jpg", "jpeg"])

        insumos = obtener_insumos()
        if not insumos:
            st.warning("⚠️ No hay insumos registrados. Agrega insumos primero.")
        else:
            st.markdown("### 🧺 Seleccionar ingredientes:")
            insumo_seleccionado = []
            for insumo in insumos:
                insumo_id, nombre, unidad, _, _ = insumo
                cantidad = st.number_input(f"{nombre} ({unidad})", min_value=0.0, step=0.1, key=f"nuevo_{insumo_id}")
                if cantidad > 0:
                    insumo_seleccionado.append((insumo_id, cantidad))

            submitted_receta = st.form_submit_button("🍽️ Guardar receta")

            if submitted_receta:
                if nombre_receta and insumo_seleccionado:
                    agregar_receta(nombre_receta, instrucciones, insumo_seleccionado)

                    # Guardar imagen si fue cargada
                    if imagen_receta:
                        carpeta_imagenes = Path("imagenes_recetas")
                        carpeta_imagenes.mkdir(exist_ok=True)
                        nombre_archivo = f"{nombre_receta.replace(' ', '_')}.jpg"
                        with open(carpeta_imagenes / nombre_archivo, "wb") as f:
                            f.write(imagen_receta.read())

                    st.success(f"✅ Receta '{nombre_receta}' guardada correctamente.")
                    st.rerun()
                else:
                    st.warning("⚠️ Debes ingresar un nombre y al menos un insumo.")

    # ========================
    # 📋 Ver y editar recetas
    # ========================
    st.markdown("### 📋 Recetas registradas")
    recetas = obtener_recetas()

    if recetas:
        for receta in recetas:
            receta_id, nombre, instrucciones = receta
            detalles = obtener_detalle_receta(receta_id)
            costo_total = sum(cant * costo for _, cant, _, costo in detalles)

            with st.expander(f"🍰 {nombre} - Costo total: ₡{costo_total:,.2f}"):
                # Mostrar imagen si existe
                ruta_img = Path("imagenes_recetas") / f"{nombre.replace(' ', '_')}.jpg"
                if ruta_img.exists():
                    st.image(str(ruta_img), caption=f"📷 {nombre}", width=300)

                st.markdown(f"**📝 Instrucciones:** {instrucciones or 'Sin instrucciones.'}")
                st.markdown("**🧾 Ingredientes:**")
                for nombre_insumo, cantidad, unidad, costo_unitario in detalles:
                    st.markdown(f"- {nombre_insumo} — {cantidad} {unidad} — ₡{costo_unitario:,.2f} c/u")

                col1, col2, col3 = st.columns(3)

                with col1:
                    pdf_bytes = generar_pdf_receta(nombre, instrucciones, detalles, costo_total)
                    st.download_button(
                        label="📄 Descargar PDF",
                        data=pdf_bytes,
                        file_name=f"{nombre}.pdf",
                        mime="application/pdf",
                        key=f"pdf_{receta_id}"
                    )

                with col2:
                    eliminar_btn = st.button(f"🗑️ Eliminar receta", key=f"eliminar_{receta_id}")
                    if eliminar_btn:
                        eliminar_receta(receta_id)
                        if ruta_img.exists():
                            ruta_img.unlink()
                        st.success(f"🗑️ Receta '{nombre}' eliminada.")
                        st.rerun()

                with col3:
                    if st.button("✏️ Editar receta", key=f"editar_{receta_id}"):
                        st.session_state[f"editando_{receta_id}"] = True

                # --- Formulario para editar receta ---
                if st.session_state.get(f"editando_{receta_id}", False):
                    with st.form(f"form_edicion_{receta_id}"):
                        nuevo_nombre = st.text_input("📛 Nuevo nombre", value=nombre, key=f"nombre_{receta_id}")
                        nuevas_instrucciones = st.text_area("📖 Nuevas instrucciones", value=instrucciones or "", key=f"inst_{receta_id}")
                        nueva_imagen = st.file_uploader("📷 Nueva imagen (opcional)", type=["jpg", "jpeg", "png"], key=f"img_{receta_id}")

                        nuevos_insumos = []
                        insumos = obtener_insumos()
                        for insumo in insumos:
                            insumo_id, insumo_nombre, unidad, _, _ = insumo
                            cantidad_actual = next((c for n, c, u, _ in detalles if n == insumo_nombre), 0.0)
                            cantidad = st.number_input(
                                f"{insumo_nombre} ({unidad})",
                                value=float(cantidad_actual),
                                min_value=0.0,
                                step=0.1,
                                key=f"insumo_edit_{receta_id}_{insumo_id}"
                            )
                            if cantidad > 0:
                                nuevos_insumos.append((insumo_id, cantidad))

                        guardar = st.form_submit_button("💾 Guardar cambios")

                        if guardar:
                            eliminar_receta(receta_id)
                            agregar_receta(nuevo_nombre, nuevas_instrucciones, nuevos_insumos)

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

# =============================
# 📤 PESTAÑA DE ENTRADAS/SALIDAS
# =============================
from datetime import datetime

with tabs[3]:
    st.subheader("📤 Registro de Entradas y Salidas de Insumos")

    # Diccionario para mostrar nombres completos de unidad
    unidad_legible = {
        "kg": "kilogramos",
        "g": "gramos",
        "l": "litros",
        "ml": "mililitros",
        "barra": "barras",
        "unidad": "unidades"
    }

    # Obtener insumos actuales
    insumos = obtener_insumos()
    if not insumos:
        st.warning("⚠️ No hay insumos disponibles. Agrega primero desde la pestaña de Insumos.")
    else:
        # Selección del insumo
        nombres_insumos = [f"{insumo[1]} ({insumo[2]})" for insumo in insumos]
        insumo_elegido = st.selectbox("🔽 Selecciona el insumo", nombres_insumos)

        index = nombres_insumos.index(insumo_elegido)
        insumo_id, nombre, unidad, costo_unitario, cantidad_actual = insumos[index]
        unidad_visible = unidad_legible.get(unidad, unidad)

        st.markdown(f"**📦 Cantidad disponible:** {cantidad_actual} {unidad_visible}")

        # Formulario de movimiento
        tipo_movimiento = st.radio("📌 Tipo de movimiento", ["Entrada", "Salida"])
        cantidad = st.number_input("📏 Cantidad a registrar", min_value=0.0, step=0.1)
        registrar = st.button("💾 Registrar movimiento")

        # Inicializar lista si no existe
        if "movimientos" not in st.session_state:
            st.session_state.movimientos = []

        if registrar:
            if tipo_movimiento == "Entrada":
                nueva_cantidad = cantidad_actual + cantidad
            else:
                if cantidad > cantidad_actual:
                    st.error("❌ No se puede realizar la salida. Cantidad insuficiente.")
                    st.stop()
                nueva_cantidad = cantidad_actual - cantidad

            # Actualizar insumo
            actualizar_insumo(insumo_id, nombre, unidad, costo_unitario, nueva_cantidad)

            # Guardar movimiento
            st.session_state.movimientos.append({
                "Fecha y hora": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "Insumo": nombre,
                "Unidad": unidad_visible,
                "Tipo": tipo_movimiento,
                "Cantidad": cantidad
            })

            st.success(f"✅ {tipo_movimiento} registrada exitosamente.")
            st.rerun()

    # Mostrar tabla de movimientos
    if "movimientos" in st.session_state and st.session_state.movimientos:
        st.markdown("### 📊 Movimientos registrados (solo esta sesión)")
        df_mov = pd.DataFrame(st.session_state.movimientos)
        st.dataframe(df_mov, use_container_width=True)
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


