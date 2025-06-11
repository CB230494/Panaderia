import sqlite3

# Conexión a la base de datos
def conectar():
    conn = sqlite3.connect("database/panaderia.db")
    cursor = conn.cursor()
    return conn, cursor

# Crear tabla de productos si no existe
def crear_tabla_productos():
    conn, cursor = conectar()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS productos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nombre TEXT NOT NULL,
            unidad TEXT NOT NULL,
            precio_venta REAL NOT NULL,
            costo REAL NOT NULL
        )
    """)
    conn.commit()
    conn.close()

# Agregar producto
def agregar_producto(nombre, unidad, precio_venta, costo):
    conn, cursor = conectar()
    cursor.execute("INSERT INTO productos (nombre, unidad, precio_venta, costo) VALUES (?, ?, ?, ?)",
                   (nombre, unidad, precio_venta, costo))
    conn.commit()
    conn.close()

# Obtener todos los productos
def obtener_productos():
    conn, cursor = conectar()
    cursor.execute("SELECT * FROM productos")
    productos = cursor.fetchall()
    conn.close()
    return productos

# Actualizar producto
def actualizar_producto(id_producto, nombre, unidad, precio_venta, costo):
    conn, cursor = conectar()
    cursor.execute("""
        UPDATE productos SET nombre = ?, unidad = ?, precio_venta = ?, costo = ?
        WHERE id = ?
    """, (nombre, unidad, precio_venta, costo, id_producto))
    conn.commit()
    conn.close()

# Eliminar producto
def eliminar_producto(id_producto):
    conn, cursor = conectar()
    cursor.execute("DELETE FROM productos WHERE id = ?", (id_producto,))
    conn.commit()
    conn.close()

# ===============================
# CRUD PARA INSUMOS
# ===============================

# Crear tabla de insumos si no existe
def crear_tabla_insumos():
    conn, cursor = conectar()
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

# Agregar insumo
def agregar_insumo(nombre, unidad, costo_unitario, cantidad):
    conn, cursor = conectar()
    cursor.execute("INSERT INTO insumos (nombre, unidad, costo_unitario, cantidad) VALUES (?, ?, ?, ?)",
                   (nombre, unidad, costo_unitario, cantidad))
    conn.commit()
    conn.close()

# Obtener insumos
def obtener_insumos():
    conn, cursor = conectar()
    cursor.execute("SELECT * FROM insumos")
    insumos = cursor.fetchall()
    conn.close()
    return insumos

# Actualizar insumo
def actualizar_insumo(id_insumo, nombre, unidad, costo_unitario, cantidad):
    conn, cursor = conectar()
    cursor.execute("""
        UPDATE insumos SET nombre = ?, unidad = ?, costo_unitario = ?, cantidad = ?
        WHERE id = ?
    """, (nombre, unidad, costo_unitario, cantidad, id_insumo))
    conn.commit()
    conn.close()

# Eliminar insumo
def eliminar_insumo(id_insumo):
    conn, cursor = conectar()
    cursor.execute("DELETE FROM insumos WHERE id = ?", (id_insumo,))
    conn.commit()
    conn.close()

# =============================
# TABLAS Y CRUD PARA RECETAS
# =============================

def crear_tabla_recetas():
    conn, cursor = conectar()
    # Tabla principal de recetas
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS recetas (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nombre TEXT NOT NULL,
            instrucciones TEXT
        )
    """)
    # Detalle de insumos usados en cada receta
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

# Agregar receta
def agregar_receta(nombre, instrucciones, insumos_utilizados):
    conn, cursor = conectar()
    cursor.execute("INSERT INTO recetas (nombre, instrucciones) VALUES (?, ?)", (nombre, instrucciones))
    receta_id = cursor.lastrowid  # ID de la nueva receta

    for insumo_id, cantidad in insumos_utilizados:
        cursor.execute("""
            INSERT INTO receta_detalle (receta_id, insumo_id, cantidad)
            VALUES (?, ?, ?)
        """, (receta_id, insumo_id, cantidad))

    conn.commit()
    conn.close()

# Obtener todas las recetas
def obtener_recetas():
    conn, cursor = conectar()
    cursor.execute("SELECT * FROM recetas")
    recetas = cursor.fetchall()
    conn.close()
    return recetas

# Obtener detalle de una receta
def obtener_detalle_receta(receta_id):
    conn, cursor = conectar()
    cursor.execute("""
        SELECT insumos.nombre, receta_detalle.cantidad, insumos.unidad, insumos.costo_unitario
        FROM receta_detalle
        JOIN insumos ON receta_detalle.insumo_id = insumos.id
        WHERE receta_detalle.receta_id = ?
    """, (receta_id,))
    detalles = cursor.fetchall()
    conn.close()
    return detalles

# Eliminar receta (y su detalle)
def eliminar_receta(receta_id):
    conn, cursor = conectar()
    cursor.execute("DELETE FROM receta_detalle WHERE receta_id = ?", (receta_id,))
    cursor.execute("DELETE FROM recetas WHERE id = ?", (receta_id,))
    conn.commit()
    conn.close()

import sqlite3

def crear_tabla_entradas_salidas():
    conn = sqlite3.connect("panaderia.db")
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS entradas_salidas (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            insumo_id INTEGER,
            tipo TEXT,  -- "Entrada", "Salida", "Salida por daño", etc.
            cantidad REAL,
            fecha_hora TEXT,
            motivo TEXT DEFAULT '',
            FOREIGN KEY(insumo_id) REFERENCES insumos(id)
        )
    """)
    conn.commit()
    conn.close()

