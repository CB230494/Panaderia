import sqlite3
from datetime import datetime

# Conexión a la base de datos
def conectar():
    conn = sqlite3.connect("database/panaderia.db")
    cursor = conn.cursor()
    return conn, cursor

# ------------------- PRODUCTOS -------------------
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

def agregar_producto(nombre, unidad, precio_venta, costo):
    conn, cursor = conectar()
    cursor.execute("INSERT INTO productos (nombre, unidad, precio_venta, costo) VALUES (?, ?, ?, ?)",
                   (nombre, unidad, precio_venta, costo))
    conn.commit()
    conn.close()

def obtener_productos():
    conn, cursor = conectar()
    cursor.execute("SELECT * FROM productos")
    productos = cursor.fetchall()
    conn.close()
    return productos

def actualizar_producto(id_producto, nombre, unidad, precio_venta, costo):
    conn, cursor = conectar()
    cursor.execute("""
        UPDATE productos SET nombre = ?, unidad = ?, precio_venta = ?, costo = ?
        WHERE id = ?
    """, (nombre, unidad, precio_venta, costo, id_producto))
    conn.commit()
    conn.close()

def eliminar_producto(id_producto):
    conn, cursor = conectar()
    cursor.execute("DELETE FROM productos WHERE id = ?", (id_producto,))
    conn.commit()
    conn.close()

# ------------------- INSUMOS -------------------
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

def agregar_insumo(nombre, unidad, costo_unitario, cantidad):
    conn, cursor = conectar()
    cursor.execute("INSERT INTO insumos (nombre, unidad, costo_unitario, cantidad) VALUES (?, ?, ?, ?)",
                   (nombre, unidad, costo_unitario, cantidad))
    conn.commit()
    conn.close()

def obtener_insumos():
    conn, cursor = conectar()
    cursor.execute("SELECT * FROM insumos")
    insumos = cursor.fetchall()
    conn.close()
    return insumos

def actualizar_insumo(id_insumo, nombre, unidad, costo_unitario, cantidad):
    conn, cursor = conectar()
    cursor.execute("""
        UPDATE insumos SET nombre = ?, unidad = ?, costo_unitario = ?, cantidad = ?
        WHERE id = ?
    """, (nombre, unidad, costo_unitario, cantidad, id_insumo))
    conn.commit()
    conn.close()

def eliminar_insumo(id_insumo):
    conn, cursor = conectar()
    cursor.execute("DELETE FROM insumos WHERE id = ?", (id_insumo,))
    conn.commit()
    conn.close()

# ------------------- RECETAS -------------------
def crear_tabla_recetas():
    conn, cursor = conectar()
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
    conn, cursor = conectar()
    cursor.execute("INSERT INTO recetas (nombre, instrucciones) VALUES (?, ?)", (nombre, instrucciones))
    receta_id = cursor.lastrowid
    for insumo_id, cantidad in insumos_utilizados:
        cursor.execute("INSERT INTO receta_detalle (receta_id, insumo_id, cantidad) VALUES (?, ?, ?)",
                       (receta_id, insumo_id, cantidad))
    conn.commit()
    conn.close()

def obtener_recetas():
    conn, cursor = conectar()
    cursor.execute("SELECT * FROM recetas")
    recetas = cursor.fetchall()
    conn.close()
    return recetas

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

def eliminar_receta(receta_id):
    conn, cursor = conectar()
    cursor.execute("DELETE FROM receta_detalle WHERE receta_id = ?", (receta_id,))
    cursor.execute("DELETE FROM recetas WHERE id = ?", (receta_id,))
    conn.commit()
    conn.close()

# ------------------- MOVIMIENTOS -------------------
def crear_tabla_entradas_salidas():
    conn, cursor = conectar()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS entradas_salidas (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            insumo_id INTEGER,
            tipo TEXT,
            cantidad REAL,
            fecha_hora TEXT,
            motivo TEXT DEFAULT '',
            FOREIGN KEY(insumo_id) REFERENCES insumos(id)
        )
    """)
    conn.commit()
    conn.close()

def registrar_movimiento(insumo_id, tipo, cantidad, motivo=""):
    conn, cursor = conectar()
    fecha_hora = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    cursor.execute("""
        INSERT INTO entradas_salidas (insumo_id, tipo, cantidad, fecha_hora, motivo)
        VALUES (?, ?, ?, ?, ?)
    """, (insumo_id, tipo, cantidad, fecha_hora, motivo))
    conn.commit()
    conn.close()

def obtener_movimientos():
    conn, cursor = conectar()
    cursor.execute("""
        SELECT entradas_salidas.id, insumos.nombre, tipo, cantidad, fecha_hora, motivo
        FROM entradas_salidas
        JOIN insumos ON entradas_salidas.insumo_id = insumos.id
        ORDER BY fecha_hora DESC
    """)
    movimientos = cursor.fetchall()
    conn.close()
    return movimientos

# ------------------- VENTAS -------------------
def crear_tabla_ventas():
    conn, cursor = conectar()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS ventas (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            producto_id INTEGER,
            cantidad REAL,
            precio_venta REAL,
            costo REAL,
            fecha TEXT,
            ganancia REAL,
            FOREIGN KEY(producto_id) REFERENCES productos(id)
        )
    """)
    conn.commit()
    conn.close()

def registrar_venta(producto_id, cantidad, precio_venta, costo):
    conn, cursor = conectar()
    fecha = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    ganancia = (precio_venta - costo) * cantidad
    cursor.execute("""
        INSERT INTO ventas (producto_id, cantidad, precio_venta, costo, fecha, ganancia)
        VALUES (?, ?, ?, ?, ?, ?)
    """, (producto_id, cantidad, precio_venta, costo, fecha, ganancia))
    conn.commit()
    conn.close()

def obtener_ventas():
    conn, cursor = conectar()
    cursor.execute("""
        SELECT ventas.id, productos.nombre, productos.unidad, ventas.cantidad, ventas.precio_venta, ventas.costo, ventas.fecha, ventas.ganancia
        FROM ventas
        JOIN productos ON ventas.producto_id = productos.id
        ORDER BY ventas.fecha DESC
    """)
    ventas = cursor.fetchall()
    conn.close()
    return ventas


