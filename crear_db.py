import sqlite3

# Conexión a la base de datos (se crea automáticamente si no existe)
conn = sqlite3.connect("usuarios.db")

# Crear la tabla de usuarios
cursor = conn.cursor()
cursor.execute("""
CREATE TABLE IF NOT EXISTS usuarios (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    nombre TEXT NOT NULL,
    username TEXT NOT NULL UNIQUE,
    password_hash TEXT NOT NULL
)
""")
conn.commit()
conn.close()

print("Base de datos creada exitosamente.")
