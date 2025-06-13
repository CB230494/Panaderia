import streamlit as st
from streamlit_option_menu import option_menu
import pandas as pd
from pathlib import Path
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
crear_tabla_ventas()

# === INICIO ===
if st.session_state.pagina == "Inicio":
    st.markdown("## 📊 Sistema de Gestión - Panadería Moderna")
    st.markdown("### Selecciona una opción para comenzar:")

    col1, col2, col3 = st.columns(3)
    with col1:
        if st.button("📦 Productos"):
            st.session_state.pagina = "Productos"
            st.rerun()
    with col2:
        if st.button("🚚 Insumos"):
            st.session_state.pagina = "Insumos"
            st.rerun()
    with col3:
        if st.button("📋 Recetas"):
            st.session_state.pagina = "Recetas"
            st.rerun()

    col4, col5, col6 = st.columns(3)
    with col4:
        if st.button("🔄 Entradas/Salidas"):
            st.session_state.pagina = "Entradas/Salidas"
            st.rerun()
    with col5:
        if st.button("💵 Ventas"):
            st.session_state.pagina = "Ventas"
            st.rerun()
    with col6:
        if st.button("📈 Balance"):
            st.session_state.pagina = "Balance"
            st.rerun()
# === PRODUCTOS ===
if st.session_state.pagina == "Productos":
    st.subheader("📦 Gestión de Productos")

    with st.form("form_agregar_producto"):
        st.markdown("### ➕ Agregar nuevo producto")
        nombre = st.text_input("Nombre del producto")
        unidad = st.selectbox("Unidad", ["unidad", "porción", "pieza", "queque", "paquete"])
        precio_venta = st.number_input("Precio de venta (₡)", min_value=0.0, format="%.2f")
        costo = st.number_input("Costo de elaboración (₡)", min_value=0.0, format="%.2f")
        stock = st.number_input("Cantidad en stock", min_value=0, step=1)
        submitted = st.form_submit_button("Agregar")

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

        df["Precio Venta"] = df["Precio Venta"].map(lambda x: f"₡{int(x)}" if x == int(x) else f"₡{x:.2f}")
        df["Costo"] = df["Costo"].map(lambda x: f"₡{int(x)}" if x == int(x) else f"₡{x:.2f}")
        df["Ganancia (₡)"] = df["Ganancia (₡)"].map(lambda x: f"₡{int(x)}" if x == int(x) else f"₡{x:.2f}")

        def color_stock(val):
            return 'background-color: red; color: white' if val < 5 else ''
        styled_df = df.style.applymap(color_stock, subset=["Stock"])
        st.dataframe(styled_df, use_container_width=True)
        st.markdown("### ✏️ Editar o eliminar un producto")
        nombres_disponibles = [producto[1] for producto in productos]
        seleccion = st.selectbox("Seleccionar producto por nombre", nombres_disponibles)

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
            nuevo_nombre = st.text_input("Nombre", value=nombre_original)
            nueva_unidad = st.selectbox("Unidad", ["unidad", "porción", "pieza", "queque", "paquete"],
                                        index=["unidad", "porción", "pieza", "queque", "paquete"].index(unidad_original))
            nuevo_precio = st.number_input("Precio de venta (₡)", value=float(precio_original), format="%.2f")
            nuevo_costo = st.number_input("Costo de elaboración (₡)", value=float(costo_original), format="%.2f")
            nuevo_stock = st.number_input("Stock disponible", value=int(stock_original), step=1)

            col1, col2 = st.columns(2)
            with col1:
                actualizar = st.form_submit_button("Actualizar")
            with col2:
                eliminar = st.form_submit_button("Eliminar")

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

    with st.form("form_agregar_insumo"):
        st.markdown("### ➕ Agregar nuevo insumo")
        nombre_i = st.text_input("Nombre del insumo")
        unidad_i_visible = st.selectbox("Unidad", list(unidades_dict.keys()))
        unidad_i = unidades_dict[unidad_i_visible]
        cantidad = st.number_input("Cantidad adquirida", min_value=0.0)
        costo_total = st.number_input("Costo total (₡)", min_value=0.0, format="%.2f")
        submitted_i = st.form_submit_button("Agregar")

        if submitted_i:
            if nombre_i and unidad_i and cantidad > 0:
                costo_unitario = costo_total / cantidad
                agregar_insumo(nombre_i, unidad_i, costo_unitario, cantidad)

                # Calcular precio por unidad base
                if unidad_i in ["kg", "l"]:
                    costo_base = costo_unitario / 1000
                    unidad_base = "gramo" if unidad_i == "kg" else "mililitro"
                else:
                    costo_base = costo_unitario
                    unidad_base = unidad_i

                st.success(
                    f"✅ '{nombre_i}' agregado correctamente. "
                    f"Cantidad: {cantidad} {unidad_i}, Costo total: ₡{costo_total:.2f}, "
                    f"₡{costo_unitario:.2f} por {unidad_i} → ₡{costo_base:.2f} por {unidad_base}"
                )
                st.rerun()
            else:
                st.warning("⚠️ Debes completar todos los campos y la cantidad debe ser mayor a cero.")

    st.markdown("### 📋 Lista de insumos")
    insumos = obtener_insumos()

    if insumos:
        df_i = pd.DataFrame(insumos, columns=["ID", "Nombre", "Unidad", "Costo Unitario", "Cantidad"])

        unidad_legible = {v: k for k, v in unidades_dict.items()}
        df_i["Unidad Mostrada"] = df_i["Unidad"].map(unidad_legible)

        def calcular_precio_base(row):
            if row["Unidad"] in ["kg", "l"]:
                return row["Costo Unitario"] / 1000
            else:
                return row["Costo Unitario"]

        df_i["₡ por unidad base"] = df_i.apply(calcular_precio_base, axis=1)
        df_i["₡ por unidad base"] = df_i["₡ por unidad base"].map(lambda x: f"₡{x:.2f}")

        df_i["Costo Total (₡)"] = df_i["Costo Unitario"] * df_i["Cantidad"]
        df_i["Costo Total (₡)"] = df_i["Costo Total (₡)"].map(lambda x: f"₡{x:,.2f}")
        df_i["Costo Unitario"] = df_i["Costo Unitario"].map(lambda x: f"₡{x:,.2f}")

        st.dataframe(df_i[["ID", "Nombre", "Unidad Mostrada", "Costo Unitario", "Cantidad", "Costo Total (₡)", "₡ por unidad base"]], use_container_width=True)

        st.markdown("### ✏️ Editar o eliminar un insumo")
        nombres_insumos = [insumo[1] for insumo in insumos]
        seleccion_i = st.selectbox("Seleccionar insumo por nombre", nombres_insumos)

        for insumo in insumos:
            if insumo[1] == seleccion_i:
                id_insumo = insumo[0]
                nombre_original = insumo[1]
                unidad_original = insumo[2]
                costo_unitario_original = insumo[3]
                cantidad_original = insumo[4]
                costo_total_original = costo_unitario_original * cantidad_original
                break

        unidad_visible_original = [k for k, v in unidades_dict.items() if v == unidad_original][0]

        with st.form("form_editar_insumo"):
            nuevo_nombre_i = st.text_input("Nombre", value=nombre_original)
            nueva_unidad_visible = st.selectbox("Unidad", list(unidades_dict.keys()),
                                                index=list(unidades_dict.keys()).index(unidad_visible_original))
            nueva_unidad = unidades_dict[nueva_unidad_visible]
            nueva_cantidad = st.number_input("Cantidad adquirida", value=float(cantidad_original))
            nuevo_costo_total = st.number_input("Costo total (₡)", value=float(costo_total_original), format="%.2f")

            col1, col2 = st.columns(2)
            with col1:
                actualizar_i = st.form_submit_button("Actualizar")
            with col2:
                eliminar_i = st.form_submit_button("Eliminar")

            if actualizar_i and nueva_cantidad > 0:
                nuevo_costo_unitario = nuevo_costo_total / nueva_cantidad
                actualizar_insumo(id_insumo, nuevo_nombre_i, nueva_unidad, nuevo_costo_unitario, nueva_cantidad)
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
if st.session_state.pagina == "Recetas":
    st.subheader("📋 Gestión de Recetas")
    crear_tabla_recetas()

    with st.form("form_nueva_receta"):
        st.markdown("### ➕ Crear nueva receta")

        nombre_receta = st.text_input("📛 Nombre de la receta")
        instrucciones = st.text_area("📖 Instrucciones de preparación")
        imagen_receta = st.file_uploader("📷 Foto del producto final (opcional)", type=["png", "jpg", "jpeg"])

        insumos = obtener_insumos()
        insumo_seleccionado = []

        if not insumos:
            st.warning("⚠️ No hay insumos registrados. Agrega insumos primero.")
        else:
            st.markdown("### 🧺 Seleccionar ingredientes:")
            for insumo in insumos:
                insumo_id, nombre, unidad, _, _ = insumo
                cantidad = st.number_input(f"{nombre} ({unidad})", min_value=0.0, step=0.1, key=f"nuevo_{insumo_id}")
                if cantidad > 0:
                    insumo_seleccionado.append((insumo_id, cantidad))

        submitted_receta = st.form_submit_button("🍽️ Guardar receta")

        if submitted_receta:
            if not nombre_receta or not insumo_seleccionado:
                st.warning("⚠️ Debes ingresar un nombre y al menos un insumo.")
            else:
                agregar_receta(nombre_receta, instrucciones, insumo_seleccionado)
                if imagen_receta:
                    carpeta_imagenes = Path("imagenes_recetas")
                    carpeta_imagenes.mkdir(exist_ok=True)
                    nombre_archivo = f"{nombre_receta.replace(' ', '_')}.jpg"
                    with open(carpeta_imagenes / nombre_archivo, "wb") as f:
                        f.write(imagen_receta.read())
                st.success(f"✅ Receta '{nombre_receta}' guardada correctamente.")
                st.rerun()

    st.markdown("### 📋 Recetas registradas")
    recetas = obtener_recetas()

    if recetas:
        for receta in recetas:
            receta_id, nombre, instrucciones = receta
            detalles = obtener_detalle_receta(receta_id)
            insumos_db = {i[0]: i for i in obtener_insumos()}

            desglose = []
            costo_total = 0

            for nombre_insumo, cantidad, unidad, _ in detalles:
                for insumo in insumos_db.values():
                    if insumo[1] == nombre_insumo:
                        costo_unitario = insumo[3]
                        unidad_insumo = insumo[2]

                        if unidad_insumo in ["kg", "l"]:
                            costo_por_base = costo_unitario / 1000
                            cantidad_en_base = cantidad * 1000 if unidad == unidad_insumo else cantidad
                        else:
                            costo_por_base = costo_unitario
                            cantidad_en_base = cantidad

                        subtotal = cantidad_en_base * costo_por_base
                        costo_total += subtotal

                        desglose.append((nombre_insumo, cantidad, unidad, costo_por_base, subtotal))
                        break

            with st.expander(f"🍰 {nombre} - Costo total: ₡{costo_total:,.2f}"):
                ruta_img = Path("imagenes_recetas") / f"{nombre.replace(' ', '_')}.jpg"
                if ruta_img.exists():
                    st.image(str(ruta_img), caption=f"📷 {nombre}", width=300)

                st.markdown(f"**📝 Instrucciones:** {instrucciones or 'Sin instrucciones.'}")
                st.markdown("**🧾 Ingredientes:**")
                for nombre_i, cant_i, unidad_i, costo_u, subtotal in desglose:
                    st.markdown(
                        f"- {nombre_i} — {cant_i:.2f} {unidad_i} — "
                        f"(₡{costo_u:.2f} c/u → Subtotal: ₡{subtotal:,.2f})"
                    )

                col1, col2 = st.columns(2)
                with col1:
                    if st.button(f"🗑️ Eliminar receta", key=f"eliminar_{receta_id}"):
                        eliminar_receta(receta_id)
                        if ruta_img.exists():
                            ruta_img.unlink()
                        st.success(f"🗑️ Receta '{nombre}' eliminada.")
                        st.rerun()
                with col2:
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

    # Mostrar nombres con unidad legible en el selectbox
    nombres_insumos = [f"{i[1]} ({unidad_legible.get(i[2], i[2])})" for i in insumos]
    insumo_elegido = st.selectbox("🔽 Selecciona el insumo", nombres_insumos)

    index = nombres_insumos.index(insumo_elegido)
    insumo_id, nombre, unidad, costo_unitario, cantidad_actual = insumos[index]
    unidad_visible = unidad_legible.get(unidad, unidad)

    st.markdown(
        f"<div style='font-size:20px; font-weight:bold; color:#ffa500;'>📦 Cantidad disponible: "
        f"{cantidad_actual:.2f} {unidad_visible}</div>", unsafe_allow_html=True
    )

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

    # === HISTORIAL DE MOVIMIENTOS ===
    historial = obtener_historial_movimientos()
    if historial:
        st.markdown("### 📜 Historial de Movimientos")
        df_hist = pd.DataFrame(historial, columns=["ID", "Insumo", "Tipo", "Cantidad", "Fecha y Hora", "Motivo"])
        df_hist["Fecha y Hora"] = pd.to_datetime(df_hist["Fecha y Hora"]).dt.strftime("%d/%m/%Y")
        df_hist["Cantidad"] = df_hist["Cantidad"].apply(lambda x: f"{x:.2f}")
        df_hist = df_hist.drop(columns=["ID"])

        def colorear_tipo(val):
            color = 'green' if val == "Entrada" else 'red'
            return f'color: {color}; font-weight: bold'

        st.dataframe(df_hist.style.applymap(colorear_tipo, subset=["Tipo"]), use_container_width=True)

    # === INSUMOS CON STOCK BAJO ===
    st.markdown("### 🚨 Insumos con stock bajo")
    bajo_stock = [i for i in insumos if i[4] < 3]
    if bajo_stock:
        df_bajo = pd.DataFrame(bajo_stock, columns=["ID", "Nombre", "Unidad", "₡ x unidad", "Cantidad disponible"])
        df_bajo["Unidad"] = df_bajo["Unidad"].map(unidad_legible)  # ✅ Nombre legible
        df_bajo["₡ x unidad"] = df_bajo["₡ x unidad"].apply(lambda x: f"₡{x:,.2f}")
        df_bajo["Cantidad disponible"] = df_bajo["Cantidad disponible"].apply(lambda x: f"{x:.2f}")
        df_bajo = df_bajo.drop(columns=["ID"])
        st.warning("⚠️ Tienes insumos con menos de 3 unidades.")
        st.dataframe(df_bajo.style.highlight_max(axis=0, color="salmon"), use_container_width=True)
    else:
        st.success("✅ Todos los insumos tienen suficiente stock.")




# =============================
# 💰 PESTAÑA DE VENTAS
# =============================
if st.session_state.pagina == "Ventas":
    from datetime import datetime
    st.subheader("💰 Registro de Ventas de Productos")

    productos = obtener_productos()
    if not productos:
        st.warning("⚠️ No hay productos disponibles. Agrega primero desde la pestaña de Productos.")
    else:
        nombres_productos = [f"{p[1]} ({p[2]})" for p in productos]
        producto_elegido = st.selectbox("🧁 Selecciona el producto vendido", nombres_productos)

        index = nombres_productos.index(producto_elegido)
        id_producto, nombre, unidad, precio_venta, costo_unitario, _ = productos[index]

        st.markdown(f"**💵 Precio de venta:** ₡{precio_venta:,.2f}")
        st.markdown(f"**🧾 Costo de elaboración:** ₡{costo_unitario:,.2f}")

        cantidad_vendida = st.number_input("📦 Cantidad vendida", min_value=0.0, step=0.1)
        registrar_venta = st.button("💾 Registrar venta")

        if registrar_venta and cantidad_vendida > 0:
            ingreso_total = round(cantidad_vendida * precio_venta, 2)
            costo_total = round(cantidad_vendida * costo_unitario, 2)
            ganancia_total = round(ingreso_total - costo_total, 2)
            fecha_actual = datetime.now().strftime("%d/%m/%Y")

            registrar_venta_en_db(nombre, unidad, cantidad_vendida, ingreso_total, costo_total, ganancia_total, fecha_actual)
            st.success("✅ Venta registrada correctamente.")
            st.rerun()

    # Mostrar resumen de ventas desde base de datos
    ventas = obtener_ventas()
    if ventas:
        st.markdown("### 📋 Historial de ventas")
        df_ventas = pd.DataFrame(ventas, columns=["ID", "Producto", "Unidad", "Cantidad", "Ingreso (₡)", "Costo (₡)", "Ganancia (₡)", "Fecha"])
        df_ventas["Cantidad"] = df_ventas["Cantidad"].apply(lambda x: f"{x:.2f}")
        df_ventas["Ingreso (₡)"] = df_ventas["Ingreso (₡)"].apply(lambda x: f"₡{x:,.2f}")
        df_ventas["Costo (₡)"] = df_ventas["Costo (₡)"].apply(lambda x: f"₡{x:,.2f}")
        df_ventas["Ganancia (₡)"] = df_ventas["Ganancia (₡)"].apply(lambda x: f"₡{x:,.2f}")

        st.dataframe(df_ventas.drop(columns=["ID"]), use_container_width=True)

        total_ingresos = sum([v[4] for v in ventas])
        total_ganancias = sum([v[6] for v in ventas])

        st.markdown(f"**💵 Total ingresos:** ₡{total_ingresos:,.2f}")
        st.markdown(f"**📈 Total ganancias:** ₡{total_ganancias:,.2f}")

        st.markdown("### ✏️ Editar o eliminar una venta")

        ids_ventas = [f"{v[0]} - {v[1]} ({v[3]:.2f})" for v in ventas]
        seleccion_id = st.selectbox("Selecciona una venta", ids_ventas)

        venta_id = int(seleccion_id.split(" - ")[0])
        venta = next(v for v in ventas if v[0] == venta_id)

        nueva_cantidad = st.number_input("Nueva cantidad vendida", min_value=0.1, value=float(venta[3]), step=0.1)
        col1, col2 = st.columns(2)
        with col1:
            if st.button("Actualizar venta"):
                nuevo_ingreso = round(nueva_cantidad * float(precio_venta), 2)
                nuevo_costo = round(nueva_cantidad * float(costo_unitario), 2)
                nueva_ganancia = round(nuevo_ingreso - nuevo_costo, 2)

                actualizar_venta(venta_id, nueva_cantidad, nuevo_ingreso, nuevo_costo, nueva_ganancia)
                st.success("✅ Venta actualizada correctamente.")
                st.rerun()
        with col2:
            if st.button("Eliminar venta"):
                eliminar_venta(venta_id)
                st.success("🗑️ Venta eliminada correctamente.")
                st.rerun()
    else:
        st.info("ℹ️ Aún no hay ventas registradas.")

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


