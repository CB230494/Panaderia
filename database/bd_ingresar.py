import sqlite3

# ========== CONEXIÓN ==========
def get_connection():
    return sqlite3.connect("panaderia.db", check_same_thread=False)

# ========== PRODUCTOS ==========
def crear_tabla_productos():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS productos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nombre TEXT NOT NULL,
            unidad TEXT NOT NULL,
            precio_venta REAL NOT NULL,
            costo REAL NOT NULL,
            stock INTEGER DEFAULT 0
        )
    """)
    conn.commit()
    conn.close()

def agregar_producto(nombre, unidad, precio_venta, costo, stock=0):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("INSERT INTO productos (nombre, unidad, precio_venta, costo, stock) VALUES (?, ?, ?, ?, ?)",
                   (nombre, unidad, precio_venta, costo, stock))
    conn.commit()
    conn.close()

def obtener_productos():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT id, nombre, unidad, precio_venta, costo, stock FROM productos")
    productos = cursor.fetchall()
    conn.close()
    return productos

def actualizar_producto(id_producto, nombre, unidad, precio_venta, costo, stock):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        UPDATE productos SET nombre = ?, unidad = ?, precio_venta = ?, costo = ?, stock = ?
        WHERE id = ?
    """, (nombre, unidad, precio_venta, costo, stock, id_producto))
    conn.commit()
    conn.close()

def eliminar_producto(id_producto):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM productos WHERE id = ?", (id_producto,))
    conn.commit()
    conn.close()


# ========== INSUMOS ==========
def crear_tabla_insumos():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS insumos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nombre TEXT NOT NULL,
            unidad TEXT NOT NULL,
            costo_unitario REAL NOT NULL,
            cantidad REAL NOT NULL
        )
    """)
    conn.commit()
    conn.close()

def agregar_insumo(nombre, unidad, costo_unitario, cantidad):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("INSERT INTO insumos (nombre, unidad, costo_unitario, cantidad) VALUES (?, ?, ?, ?)",
                   (nombre, unidad, costo_unitario, cantidad))
    conn.commit()
    conn.close()

def obtener_insumos():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT id, nombre, unidad, costo_unitario, cantidad FROM insumos")
    insumos = cursor.fetchall()
    conn.close()
    return insumos

def actualizar_insumo(id_insumo, nombre, unidad, costo_unitario, cantidad):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        UPDATE insumos SET nombre = ?, unidad = ?, costo_unitario = ?, cantidad = ?
        WHERE id = ?
    """, (nombre, unidad, costo_unitario, cantidad, id_insumo))
    conn.commit()
    conn.close()

def eliminar_insumo(id_insumo):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM insumos WHERE id = ?", (id_insumo,))
    conn.commit()
    conn.close()

# ========== RECETAS ==========
def crear_tabla_recetas():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS recetas (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nombre TEXT NOT NULL,
            instrucciones TEXT
        )
    """)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS receta_detalle (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            receta_id INTEGER,
            insumo_id INTEGER,
            cantidad REAL,
            FOREIGN KEY (receta_id) REFERENCES recetas(id),
            FOREIGN KEY (insumo_id) REFERENCES insumos(id)
        )
    """)
    conn.commit()
    conn.close()

def agregar_receta(nombre, instrucciones, insumos_utilizados):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("INSERT INTO recetas (nombre, instrucciones) VALUES (?, ?)", (nombre, instrucciones))
    receta_id = cursor.lastrowid
    for insumo_id, cantidad in insumos_utilizados:
        cursor.execute("""
            INSERT INTO receta_detalle (receta_id, insumo_id, cantidad)
            VALUES (?, ?, ?)
        """, (receta_id, insumo_id, cantidad))
    conn.commit()
    conn.close()

def obtener_recetas():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT id, nombre, instrucciones FROM recetas")
    recetas = cursor.fetchall()
    conn.close()
    return recetas

def obtener_detalle_receta(receta_id):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT insumos.nombre, receta_detalle.cantidad, insumos.unidad, insumos.costo_unitario
        FROM receta_detalle
        JOIN insumos ON receta_detalle.insumo_id = insumos.id
        WHERE receta_detalle.receta_id = ?
    """, (receta_id,))
    detalles = cursor.fetchall()
    conn.close()
    return detalles

def eliminar_receta(receta_id):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM receta_detalle WHERE receta_id = ?", (receta_id,))
    cursor.execute("DELETE FROM recetas WHERE id = ?", (receta_id,))
    conn.commit()
    conn.close()

# ========== ENTRADAS Y SALIDAS ==========
def crear_tabla_entradas_salidas():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS entradas_salidas (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            insumo_id INTEGER,
            tipo TEXT NOT NULL,
            cantidad REAL NOT NULL,
            fecha_hora TEXT NOT NULL,
            motivo TEXT,
            FOREIGN KEY(insumo_id) REFERENCES insumos(id)
        )
    """)
    conn.commit()
    conn.close()

def registrar_movimiento(insumo_id, tipo, cantidad, fecha_hora, motivo):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO entradas_salidas (insumo_id, tipo, cantidad, fecha_hora, motivo)
        VALUES (?, ?, ?, ?, ?)
    """, (insumo_id, tipo, cantidad, fecha_hora, motivo))
    if tipo.lower().startswith("entrada"):
        cursor.execute("UPDATE insumos SET cantidad = cantidad + ? WHERE id = ?", (cantidad, insumo_id))
    else:
        cursor.execute("UPDATE insumos SET cantidad = cantidad - ? WHERE id = ?", (cantidad, insumo_id))
    conn.commit()
    conn.close()

def obtener_historial_movimientos():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT entradas_salidas.id, insumos.nombre, entradas_salidas.tipo,
               entradas_salidas.cantidad, entradas_salidas.fecha_hora, entradas_salidas.motivo
        FROM entradas_salidas
        JOIN insumos ON entradas_salidas.insumo_id = insumos.id
        ORDER BY entradas_salidas.fecha_hora DESC
    """)
    historial = cursor.fetchall()
    conn.close()
    return historial

# ========== VENTAS ==========
def crear_tabla_ventas():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS ventas (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            producto TEXT NOT NULL,
            unidad TEXT,
            cantidad REAL NOT NULL,
            ingreso REAL NOT NULL,
            costo REAL NOT NULL,
            ganancia REAL NOT NULL,
            fecha TEXT NOT NULL
        )
    """)
    conn.commit()
    conn.close()

def registrar_venta_en_db(producto, unidad, cantidad, ingreso, costo, ganancia, fecha):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO ventas (producto, unidad, cantidad, ingreso, costo, ganancia, fecha)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    """, (producto, unidad, cantidad, ingreso, costo, ganancia, fecha))
    conn.commit()
    conn.close()

def obtener_ventas():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT id, producto, unidad, cantidad, ingreso, costo, ganancia, fecha
        FROM ventas
        ORDER BY fecha DESC
    """)
    ventas = cursor.fetchall()
    conn.close()
    return ventas

def eliminar_venta(id_venta):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM ventas WHERE id = ?", (id_venta,))
    conn.commit()
    conn.close()

def actualizar_venta(id_venta, cantidad, ingreso, costo, ganancia):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        UPDATE ventas
        SET cantidad = ?, ingreso = ?, costo = ?, ganancia = ?
        WHERE id = ?
    """, (cantidad, ingreso, costo, ganancia, id_venta))
    conn.commit()
    conn.close()

