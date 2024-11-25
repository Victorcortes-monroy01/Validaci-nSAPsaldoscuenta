import sqlite3

# Conexión a la base de datos
conn = sqlite3.connect("usuarios.db")
cursor = conn.cursor()

# Consultar la tabla de usuarios
cursor.execute("SELECT * FROM usuarios")
usuarios = cursor.fetchall()

print("Usuarios registrados:")
for usuario in usuarios:
    print(usuario)

conn.close()
