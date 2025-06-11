import streamlit as st
import pandas as pd
from pathlib import Path
from exportar_pdf import generar_pdf_receta  # Asegúrate de tener este archivo en tu proyecto
from database.bd_ingresar import (
    crear_tabla_productos,
    agregar_producto,
    obtener_productos,
    actualizar_producto,
    eliminar_producto,
    crear_tabla_insumos,
    agregar_insumo,
    obtener_insumos,
    actualizar_insumo,
    eliminar_insumo,
    crear_tabla_recetas,
    agregar_receta,
    obtener_recetas,
    obtener_detalle_receta,
    eliminar_receta,
    crear_tabla_entradas_salidas,
    registrar_movimiento_entrada_salida,
    obtener_movimientos_entrada_salida
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
        cantidad_inicial = st.number_input("📦 Cantidad inicial en stock", min_value=0.0)
        submitted = st.form_submit_button("🍞 Agregar")

        if submitted:
            if nombre and unidad:
                agregar_producto(nombre, unidad, precio_venta, costo, cantidad_inicial)
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
        df["Alerta"] = df["Stock"].apply(lambda x: "🔴 Bajo stock" if x < 3 else "")
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
                stock_original = producto[5]
                break

        with st.form("form_editar_producto"):
            nuevo_nombre = st.text_input("🍥 Nombre", value=nombre_original)
            nueva_unidad = st.selectbox("📦 Unidad", ["unidad", "porción", "pieza", "queque", "paquete"],
                                        index=["unidad", "porción", "pieza", "queque", "paquete"].index(unidad_original))
            nuevo_precio = st.number_input("💰 Precio de venta (₡)", value=float(precio_original), format="%.2f")
            nuevo_costo = st.number_input("🧾 Costo de elaboración (₡)", value=float(costo_original), format="%.2f")
            nuevo_stock = st.number_input("📦 Cantidad en stock", value=float(stock_original), min_value=0.0)

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
# 🧂 PESTAÑA DE INSUMOS
# =============================
with tabs[1]:
    st.subheader("🧂 Gestión de Insumos")
    crear_tabla_insumos()

    with st.form("form_insumo"):
        st.markdown("### ➕ Agregar nuevo insumo")
        nombre = st.text_input("Nombre del insumo")
        unidad = st.selectbox("Unidad de medida", ["Gramos", "Kilogramos", "Mililitros", "Litros", "Unidades"])
        cantidad = st.number_input("Cantidad inicial", min_value=0.0, step=0.1)
        costo_unitario = st.number_input("Costo por unidad (₡)", min_value=0.0, step=0.1)

        submitted = st.form_submit_button("💾 Agregar insumo")

        if submitted:
            if nombre and unidad and cantidad >= 0 and costo_unitario >= 0:
                agregar_insumo(nombre, unidad, cantidad, costo_unitario)
                st.success(f"✅ Insumo '{nombre}' agregado correctamente.")
                st.rerun()
            else:
                st.warning("⚠️ Todos los campos deben estar completos y válidos.")

    st.markdown("### 📋 Insumos registrados")
    insumos = obtener_insumos()

    if insumos:
        for insumo in insumos:
            insumo_id, nombre, unidad, cantidad, costo = insumo
            with st.expander(f"🔹 {nombre} — {cantidad} {unidad} — ₡{costo:,.2f} c/u"):
                nuevo_nombre = st.text_input("Editar nombre", value=nombre, key=f"nombre_{insumo_id}")
                nueva_unidad = st.selectbox("Editar unidad", ["Gramos", "Kilogramos", "Mililitros", "Litros", "Unidades"], index=["Gramos", "Kilogramos", "Mililitros", "Litros", "Unidades"].index(unidad), key=f"unidad_{insumo_id}")
                nueva_cantidad = st.number_input("Editar cantidad", value=float(cantidad), min_value=0.0, step=0.1, key=f"cantidad_{insumo_id}")
                nuevo_costo = st.number_input("Editar costo unitario (₡)", value=float(costo), min_value=0.0, step=0.1, key=f"costo_{insumo_id}")

                col1, col2 = st.columns(2)
                with col1:
                    if st.button("💾 Actualizar", key=f"actualizar_{insumo_id}"):
                        actualizar_insumo(insumo_id, nuevo_nombre, nueva_unidad, nueva_cantidad, nuevo_costo)
                        st.success("✅ Insumo actualizado.")
                        st.rerun()
                with col2:
                    if st.button("🗑️ Eliminar", key=f"eliminar_{insumo_id}"):
                        eliminar_insumo(insumo_id)
                        st.success("🗑️ Insumo eliminado.")
                        st.rerun()
    else:
        st.info("ℹ️ No hay insumos registrados aún.")

# =============================
# 📋 PESTAÑA DE RECETAS
# =============================
with tabs[2]:
    st.subheader("📋 Gestión de Recetas")
    crear_tabla_recetas()

    with st.form("form_nueva_receta"):
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

    st.markdown("### 📋 Recetas registradas")
    recetas = obtener_recetas()

    if recetas:
        for receta in recetas:
            receta_id, nombre, instrucciones = receta
            detalles = obtener_detalle_receta(receta_id)
            costo_total = sum(cant * costo for _, cant, _, costo in detalles)

            with st.expander(f"🍰 {nombre} - Costo total: ₡{costo_total:,.2f}"):
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
with tabs[3]:
    st.subheader("📤 Control de Entradas y Salidas de Insumos")
    crear_tabla_entradas_salidas()
    insumos = obtener_insumos()

    if not insumos:
        st.warning("⚠️ No hay insumos registrados. Agrega insumos primero.")
    else:
        with st.form("form_movimiento"):
            st.markdown("### ➕ Registrar entrada o salida")
            insumo_opciones = {f"{i[1]} ({i[2]})": i[0] for i in insumos}
            insumo_seleccionado = st.selectbox("Seleccionar insumo", list(insumo_opciones.keys()))
            tipo = st.radio("Tipo de movimiento", ["Entrada", "Salida"], horizontal=True)
            cantidad = st.number_input("Cantidad", min_value=0.01, step=0.1)
            motivo = st.text_input("Motivo del movimiento")

            submitted = st.form_submit_button("💾 Registrar movimiento")

            if submitted:
                insumo_id = insumo_opciones[insumo_seleccionado]
                registrar_movimiento(insumo_id, tipo, cantidad, motivo)
                st.success(f"✅ {tipo} registrada correctamente.")
                st.rerun()

        st.markdown("### 📋 Historial de movimientos")
        movimientos = obtener_movimientos()

        if movimientos:
            df = pd.DataFrame(movimientos, columns=["ID", "Nombre", "Unidad", "Tipo", "Cantidad", "Motivo", "FechaHora"])
            df["FechaHora"] = pd.to_datetime(df["FechaHora"]).dt.strftime("%Y-%m-%d %H:%M:%S")

            # Mostrar con nombres de unidades legibles
            unidad_legible = {
                "Gramos": "g",
                "Kilogramos": "kg",
                "Mililitros": "ml",
                "Litros": "l",
                "Unidades": "unidad"
            }
            df["Unidad"] = df["Unidad"].map(unidad_legible).fillna(df["Unidad"])

            st.dataframe(df.sort_values("FechaHora", ascending=False), use_container_width=True)
        else:
            st.info("ℹ️ No hay movimientos registrados aún.")

# =============================
# 💰 PESTAÑA DE VENTAS
# =============================
with tabs[4]:
    st.subheader("💰 Registro de Ventas")
    productos = obtener_productos()
    crear_tabla_ventas()

    if not productos:
        st.warning("⚠️ No hay productos registrados. Agrega productos primero.")
    else:
        with st.form("form_venta"):
            st.markdown("### ➕ Registrar venta")
            producto_opciones = {
                f"{p[1]} (Disponibles: {int(p[5])}) - ₡{p[3]:,.2f}": (p[0], p[3], p[5])
                for p in productos
            }
            seleccion = st.selectbox("Seleccionar producto", list(producto_opciones.keys()))
            cantidad_vendida = st.number_input("Cantidad vendida", min_value=1, step=1)

            submitted_venta = st.form_submit_button("💾 Registrar venta")

            if submitted_venta:
                producto_id, precio_unitario, stock_disponible = producto_opciones[seleccion]

                if cantidad_vendida > stock_disponible:
                    st.error(f"❌ No hay suficiente stock disponible. Solo hay {int(stock_disponible)} unidades.")
                else:
                    registrar_venta(producto_id, cantidad_vendida, precio_unitario)
                    actualizar_stock_producto(producto_id, stock_disponible - cantidad_vendida)
                    st.success("✅ Venta registrada correctamente.")
                    st.rerun()

        st.markdown("### 📋 Historial de ventas")
        ventas = obtener_ventas()

        if ventas:
            df = pd.DataFrame(ventas, columns=["ID", "Nombre", "Cantidad", "Precio Unitario", "FechaHora"])
            df["Total (₡)"] = df["Cantidad"] * df["Precio Unitario"]
            df["FechaHora"] = pd.to_datetime(df["FechaHora"]).dt.strftime("%Y-%m-%d %H:%M:%S")
            st.dataframe(df.sort_values("FechaHora", ascending=False), use_container_width=True)
        else:
            st.info("ℹ️ No hay ventas registradas todavía.")

# =============================
# 📊 PESTAÑA DE BALANCE
# =============================
from exportar_pdf import generar_pdf_balance
from io import BytesIO

with tabs[5]:
    st.subheader("📊 Balance General del Negocio")

    # ==== Inventario de Insumos ====
    insumos = obtener_insumos()
    total_inventario = 0
    if insumos:
        df_insumos = pd.DataFrame(insumos, columns=["ID", "Nombre", "Unidad", "Costo Unitario", "Cantidad"])
        df_insumos["Total (CRC)"] = df_insumos["Costo Unitario"] * df_insumos["Cantidad"]
        total_inventario = df_insumos["Total (CRC)"].sum()

        unidad_legible = {
            "kg": "kilogramos",
            "g": "gramos",
            "l": "litros",
            "ml": "mililitros",
            "barra": "barras",
            "unidad": "unidades"
        }
        df_insumos["Unidad"] = df_insumos["Unidad"].map(unidad_legible)

        st.markdown("### 📦 Valor del inventario de insumos")
        st.dataframe(df_insumos[["Nombre", "Unidad", "Cantidad", "Costo Unitario", "Total (CRC)"]], use_container_width=True)
        st.markdown(f"**🔹 Total inventario:** CRC {total_inventario:,.2f}")
    else:
        st.info("ℹ️ No hay insumos registrados.")

    st.divider()

    # ==== Resumen de Ventas ====
    st.markdown("### 💰 Ventas registradas en esta sesión")

    total_ingresos = 0
    total_ganancia = 0
    total_costos = 0
    if "ventas" in st.session_state and st.session_state.ventas:
        df_ventas = pd.DataFrame(st.session_state.ventas)
        st.dataframe(df_ventas, use_container_width=True)

        total_ingresos = df_ventas["Ingreso (₡)"].sum()
        total_ganancia = df_ventas["Ganancia (₡)"].sum()
        total_costos = df_ventas["Costo (₡)"].sum()

        st.markdown(f"- **🟢 Ingresos:** CRC {total_ingresos:,.2f}")
        st.markdown(f"- **🧾 Costos:** CRC {total_costos:,.2f}")
        st.markdown(f"- **📈 Ganancia total:** CRC {total_ganancia:,.2f}")
    else:
        st.info("ℹ️ No hay ventas registradas en esta sesión.")

    st.divider()

    # ==== Comparativo Básico ====
    if insumos and "ventas" in st.session_state and st.session_state.ventas:
        st.markdown("### 📉 Comparativo resumen")
        st.markdown(f"🔸 **Valor actual del inventario:** CRC {total_inventario:,.2f}")
        st.markdown(f"🔸 **Ganancia generada (ventas - costos):** CRC {total_ganancia:,.2f}")
        balance_total = total_ingresos - total_inventario
        st.markdown(f"🔸 **Balance estimado (ingresos - inventario):** CRC {balance_total:,.2f}")

        # Botón para exportar PDF
        if st.button("📄 Generar PDF del balance"):
            pdf = generar_pdf_balance(
                total_inventario,
                total_ingresos,
                total_costos,
                total_ganancia,
                balance_total
            )
            st.download_button(
                label="⬇️ Descargar PDF",
                data=pdf,
                file_name="balance_financiero.pdf",
                mime="application/pdf"
            )


