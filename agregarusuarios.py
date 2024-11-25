import bcrypt
import sqlite3

# Conexión a la base de datos SQLite
conn = sqlite3.connect("usuarios.db")
cursor = conn.cursor()

# Crear la tabla si no existe
cursor.execute("""
CREATE TABLE IF NOT EXISTS usuarios (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    nombre TEXT NOT NULL,
    username TEXT NOT NULL UNIQUE,
    password_hash TEXT NOT NULL
)
""")
conn.commit()

# Datos del nuevo usuario
nombre = "Admin"
username = "admin"
password = "password123"

# Generar hash de la contraseña con bcrypt
password_hash = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

# Insertar el nuevo usuario
try:
    cursor.execute("INSERT INTO usuarios (nombre, username, password_hash) VALUES (?, ?, ?)",
                   (nombre, username, password_hash))
    conn.commit()
    print(f"Usuario '{username}' agregado exitosamente.")
except sqlite3.IntegrityError:
    print(f"El usuario '{username}' ya existe.")

conn.close()
