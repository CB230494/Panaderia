import streamlit as st
import pandas as pd
from pathlib import Path
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
    eliminar_receta,

    # Entradas / Salidas
    crear_tabla_entradas_salidas,
    registrar_movimiento,
    obtener_movimientos,

    # Ventas
    crear_tabla_ventas,
    registrar_venta,
    obtener_historial_ventas
)


st.set_page_config(page_title="Panadería Moderna", layout="wide")
st.title("🥐 Sistema de Gestión - Panadería Moderna")

# Crear todas las tablas necesarias
crear_tabla_productos()
crear_tabla_insumos()
crear_tabla_recetas()
crear_tabla_entradas_salidas()
crear_tabla_ventas()

tabs = st.tabs(["🧁 Productos", "📦 Insumos", "📋 Recetas", "📤 Entradas/Salidas", "💰 Ventas", "📊 Balance"])

# =============================
# 🧁 PESTAÑA DE PRODUCTOS
# =============================
with tabs[0]:
    st.subheader("🧁 Gestión de Productos")

    with st.form("form_agregar_producto"):
        st.markdown("### ➕ Agregar nuevo producto")
        nombre = st.text_input("📛 Nombre del producto")
        unidad = st.selectbox("📦 Unidad", ["unidad", "porción", "pieza", "queque", "paquete"])
        precio_venta = st.number_input("💰 Precio de venta (₡)", min_value=0.0, format="%.2f")
        costo = st.number_input("🧾 Costo de elaboración (₡)", min_value=0.0, format="%.2f")
        stock = st.number_input("📦 Cantidad inicial en stock", min_value=0.0, format="%.2f")
        submitted = st.form_submit_button("🍞 Agregar")

        if submitted:
            if nombre and unidad:
                agregar_producto(nombre, unidad, precio_venta, costo, stock)
                st.success(f"✅ Producto '{nombre}' agregado correctamente.")
                st.rerun()
            else:
                st.warning("⚠️ Debes completar todos los campos.")

    st.markdown("### 📋 Lista de productos")
    productos = obtener_productos()

    if productos:
        df = pd.DataFrame(productos, columns=["ID", "Nombre", "Unidad", "Precio Venta", "Costo", "Stock"])
        df["Ganancia (₡)"] = df["Precio Venta"] - df["Costo"]
        st.dataframe(df, use_container_width=True)

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
            nuevo_stock = st.number_input("📦 Cantidad en stock", value=float(stock_original), format="%.2f")

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

    unidades_dict = {
        "Kilogramo (kg)": "kg",
        "Gramo (g)": "g",
        "Litro (l)": "l",
        "Mililitro (ml)": "ml",
        "Barra": "barra",
        "Unidad": "unidad"
    }

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

    st.markdown("### 📋 Lista de insumos")
    insumos = obtener_insumos()

    if insumos:
        df_i = pd.DataFrame(insumos, columns=["ID", "Nombre", "Unidad", "Costo Unitario", "Cantidad"])
        unidad_legible = {v: k for k, v in unidades_dict.items()}
        df_i["Unidad"] = df_i["Unidad"].map(unidad_legible)
        df_i["Total (₡)"] = df_i["Costo Unitario"] * df_i["Cantidad"]

        st.dataframe(df_i, use_container_width=True)

        bajos = df_i[df_i["Cantidad"] < 3]
        if not bajos.empty:
            st.warning("⚠️ Insumos con stock bajo (menos de 3):")
            st.dataframe(bajos[["Nombre", "Cantidad", "Unidad"]], use_container_width=True)

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
# 🧁 PESTAÑA DE RECETAS
# =============================
with tabs[2]:
    st.subheader("🧁 Gestión de Recetas")

    insumos_disponibles = obtener_insumos()
    recetas = obtener_recetas()

    # Mostrar recetas existentes
    if recetas:
        st.markdown("### 📋 Recetas registradas")
        for receta in recetas:
            st.markdown(f"**📌 {receta[1]}**")
            st.markdown(f"📝 Instrucciones: {receta[2]}")
            detalles = obtener_detalle_receta(receta[0])
            total_receta = 0
            for insumo in detalles:
                nombre, cantidad, unidad, costo_unitario = insumo
                subtotal = cantidad * costo_unitario
                total_receta += subtotal
                st.markdown(f"- {nombre}: {cantidad} {unidad} (₡{costo_unitario:.2f} c/u) = ₡{subtotal:.2f}")
            st.markdown(f"**💵 Costo total estimado: ₡{total_receta:.2f}**")
            col_r1, col_r2 = st.columns(2)
            with col_r1:
                if st.button(f"🗑️ Eliminar '{receta[1]}'", key=f"del_{receta[0]}"):
                    eliminar_receta(receta[0])
                    st.success(f"🗑️ Receta '{receta[1]}' eliminada.")
                    st.rerun()
            with col_r2:
                if st.button(f"📄 Generar PDF '{receta[1]}'", key=f"pdf_{receta[0]}"):
                    detalles = obtener_detalle_receta(receta[0])
                    pdf_data = generar_pdf_receta(receta[1], receta[2], detalles)
                    st.download_button(
                        label="⬇️ Descargar PDF",
                        data=pdf_data,
                        file_name=f"{receta[1]}.pdf",
                        mime="application/pdf"
                    )
    else:
        st.info("ℹ️ No hay recetas registradas todavía.")

    st.markdown("---")
    st.markdown("### ➕ Crear nueva receta")

    with st.form("form_receta"):
        nombre_receta = st.text_input("📛 Nombre de la receta")
        instrucciones = st.text_area("📝 Instrucciones")

        seleccionados = []
        st.markdown("📦 Selecciona insumos y cantidades:")
        for insumo in insumos_disponibles:
            cantidad = st.number_input(
                f"{insumo[1]} ({insumo[2]}) - Stock: {insumo[4]}",
                min_value=0.0, step=0.1, key=f"cantidad_{insumo[0]}"
            )
            if cantidad > 0:
                seleccionados.append((insumo[0], cantidad))

        imagen = st.file_uploader("📸 Foto del producto final (opcional)", type=["png", "jpg", "jpeg"])

        submitted = st.form_submit_button("🧁 Guardar receta")
        if submitted:
            if nombre_receta and seleccionados:
                agregar_receta(nombre_receta, instrucciones, seleccionados)
                st.success(f"✅ Receta '{nombre_receta}' guardada correctamente.")
                st.rerun()
            else:
                st.warning("⚠️ Debes ingresar un nombre y al menos un insumo.")
# =============================
# 📦 PESTAÑA DE ENTRADAS / SALIDAS
# =============================
with tabs[3]:
    st.subheader("📦 Control de Entradas y Salidas de Insumos")
    crear_tabla_entradas_salidas()

    insumos = obtener_insumos()

    if not insumos:
        st.warning("⚠️ No hay insumos registrados.")
    else:
        with st.form("form_movimiento"):
            st.markdown("### ➕ Registrar Movimiento de Insumo")

            insumo_dict = {f"{i[1]} ({i[2]}) - Stock: {i[4]}": i[0] for i in insumos}
            insumo_nombre = st.selectbox("📦 Selecciona el insumo", list(insumo_dict.keys()))
            insumo_id = insumo_dict[insumo_nombre]

            tipo = st.selectbox("🔁 Tipo de movimiento", ["Entrada", "Salida", "Salida por daño"])
            cantidad = st.number_input("🔢 Cantidad", min_value=0.1, step=0.1)
            motivo = ""
            if tipo != "Entrada":
                motivo = st.text_input("✍️ Motivo de la salida")

            submit = st.form_submit_button("✅ Registrar movimiento")
            if submit:
                registrar_movimiento(insumo_id, tipo, cantidad, motivo)
                st.success("✅ Movimiento registrado correctamente.")
                st.rerun()

    # Mostrar historial
    st.markdown("---")
    st.markdown("### 🕓 Historial de movimientos")
    historial = obtener_historial_movimientos()

    if historial.empty:
        st.info("ℹ️ No hay movimientos registrados.")
    else:
        st.dataframe(historial)
# =============================
# 💰 PESTAÑA DE VENTAS
# =============================
with tabs[4]:
    st.subheader("💰 Registro de Ventas")
    crear_tabla_ventas()

    productos = obtener_productos()

    if not productos:
        st.warning("⚠️ No hay productos registrados.")
    else:
        with st.form("form_venta"):
            st.markdown("### ➕ Registrar nueva venta")

            producto_dict = {f"{p[1]} ({p[2]}) - Stock: {p[5]}": p[0] for p in productos}
            producto_nombre = st.selectbox("🧁 Selecciona el producto", list(producto_dict.keys()))
            producto_id = producto_dict[producto_nombre]

            cantidad = st.number_input("🔢 Cantidad vendida", min_value=1, step=1)
            submit = st.form_submit_button("✅ Registrar venta")

            if submit:
                producto = [p for p in productos if p[0] == producto_id][0]
                stock_disponible = producto[5]
                precio_venta = producto[3]

                if cantidad <= stock_disponible:
                    registrar_venta(producto_id, cantidad, precio_venta)
                    st.success("✅ Venta registrada correctamente.")
                    st.rerun()
                else:
                    st.error(f"❌ No hay suficiente stock. Solo hay {stock_disponible} unidades disponibles.")

    # Mostrar historial
    st.markdown("---")
    st.markdown("### 🧾 Historial de ventas")
    ventas = obtener_historial_ventas()

    if ventas.empty:
        st.info("ℹ️ No hay ventas registradas.")
    else:
        st.dataframe(ventas)
# =============================
# 📊 PESTAÑA DE BALANCE
# =============================
from datetime import datetime
from fpdf import FPDF

with tabs[5]:
    st.subheader("📊 Balance General del Negocio")

    # Cargar datos
    insumos = obtener_insumos()
    productos = obtener_productos()
    historial = obtener_movimientos()
    ventas = obtener_ventas()

    unidades_legibles = {
        "kg": "kilogramos",
        "g": "gramos",
        "l": "litros",
        "ml": "mililitros",
        "barra": "barras",
        "unidad": "unidades",
        "paquete": "paquetes",
        "pieza": "piezas",
        "porción": "porciones",
        "queque": "queques"
    }

    # --- Valor del inventario de insumos ---
    if insumos:
        st.markdown("### 📦 Valor del Inventario de Insumos")
        df_insumos = pd.DataFrame(insumos, columns=["ID", "Nombre", "Unidad", "Costo Unitario", "Cantidad"])
        df_insumos["Unidad"] = df_insumos["Unidad"].map(unidades_legibles)
        df_insumos["Total (₡)"] = df_insumos["Costo Unitario"] * df_insumos["Cantidad"]
        total_insumos = df_insumos["Total (₡)"].sum()
        st.dataframe(df_insumos[["Nombre", "Unidad", "Cantidad", "Costo Unitario", "Total (₡)"]], use_container_width=True)
        st.markdown(f"**📌 Total inventario insumos:** ₡{total_insumos:,.2f}")
    else:
        total_insumos = 0
        st.info("ℹ️ No hay insumos registrados.")

    st.divider()

    # --- Ventas registradas ---
    st.markdown("### 💰 Resumen de Ventas")

    if ventas:
        df_ventas = pd.DataFrame(ventas, columns=["ID", "Producto", "Unidad", "Cantidad", "Precio Venta", "Costo", "Fecha", "Ganancia"])
        df_ventas["Fecha"] = pd.to_datetime(df_ventas["Fecha"])
        total_ingresos = (df_ventas["Cantidad"] * df_ventas["Precio Venta"]).sum()
        total_ganancias = df_ventas["Ganancia"].sum()
        total_costos = df_ventas["Cantidad"] * df_ventas["Costo"]
        st.dataframe(df_ventas[["Producto", "Cantidad", "Precio Venta", "Costo", "Fecha", "Ganancia"]], use_container_width=True)

        st.markdown(f"**💵 Total ingresos:** ₡{total_ingresos:,.2f}")
        st.markdown(f"**🧾 Total costos:** ₡{total_costos.sum():,.2f}")
        st.markdown(f"**📈 Ganancia neta:** ₡{total_ganancias:,.2f}")
    else:
        total_ingresos = total_ganancias = 0
        st.info("ℹ️ No hay ventas registradas.")

    st.divider()

    # --- Historial de entradas y salidas ---
    st.markdown("### 🧾 Historial de Entradas y Salidas")
    if historial:
        df_historial = pd.DataFrame(historial, columns=["ID", "Insumo", "Tipo", "Cantidad", "Fecha y Hora", "Motivo"])
        st.dataframe(df_historial[["Insumo", "Tipo", "Cantidad", "Fecha y Hora", "Motivo"]], use_container_width=True)
    else:
        st.info("ℹ️ No hay movimientos registrados.")

    st.divider()

    # --- PDF de balance ---
    def generar_pdf_balance(insumos, ventas, historial):
        pdf = FPDF()
        pdf.add_page()
        pdf.set_font("Arial", "B", 14)
        pdf.cell(0, 10, "Balance General - Panadería Moderna", ln=True, align="C")
        pdf.ln(5)

        pdf.set_font("Arial", "", 12)
        pdf.cell(0, 10, f"Generado: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}", ln=True)
        pdf.ln(5)

        # Inventario
        pdf.set_font("Arial", "B", 12)
        pdf.cell(0, 10, "📦 Inventario de Insumos:", ln=True)
        pdf.set_font("Arial", "", 11)
        for insumo in insumos:
            nombre, unidad, costo, cantidad = insumo[1], unidades_legibles[insumo[2]], insumo[3], insumo[4]
            total = costo * cantidad
            pdf.cell(0, 8, f"- {nombre} ({unidad}): {cantidad} x ₡{costo:,.2f} = ₡{total:,.2f}", ln=True)

        pdf.ln(4)
        pdf.set_font("Arial", "B", 12)
        pdf.cell(0, 10, "💰 Ventas Realizadas:", ln=True)
        pdf.set_font("Arial", "", 11)
        for venta in ventas:
            nombre, cantidad, precio, fecha = venta[1], venta[3], venta[4], venta[6]
            total = cantidad * precio
            pdf.cell(0, 8, f"- {nombre}: {cantidad} x ₡{precio:,.2f} = ₡{total:,.2f} ({fecha})", ln=True)

        pdf.ln(4)
        pdf.set_font("Arial", "B", 12)
        pdf.cell(0, 10, "📦 Historial de Movimientos:", ln=True)
        pdf.set_font("Arial", "", 11)
        for mov in historial:
            insumo, tipo, cantidad, fecha, motivo = mov[1], mov[2], mov[3], mov[4], mov[5]
            motivo_str = f" ({motivo})" if motivo else ""
            pdf.cell(0, 8, f"- {fecha}: {tipo} de {cantidad} de {insumo}{motivo_str}", ln=True)

        pdf.ln(10)
        pdf.set_font("Arial", "B", 12)
        pdf.cell(0, 10, f"🔸 Total inventario: ₡{total_insumos:,.2f}", ln=True)
        pdf.cell(0, 10, f"🔸 Total ingresos: ₡{total_ingresos:,.2f}", ln=True)
        pdf.cell(0, 10, f"🔸 Ganancia neta: ₡{total_ganancias:,.2f}", ln=True)

        return pdf.output(dest="S").encode("latin-1", errors="replace")

    pdf_bytes = generar_pdf_balance(insumos, ventas, historial)

    st.download_button(
        label="📥 Descargar Balance en PDF",
        data=pdf_bytes,
        file_name="balance_general.pdf",
        mime="application/pdf"
    )




