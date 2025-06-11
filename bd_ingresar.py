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
