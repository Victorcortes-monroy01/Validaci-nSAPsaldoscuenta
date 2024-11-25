import sqlite3
import bcrypt
import pandas as pd
from streamlit_authenticator import Authenticate

# Crear datos de prueba para la base de datos SQLite
def crear_base_datos():
    conn = sqlite3.connect("usuarios.db")
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

    # Crear usuario de prueba
    nombre = "Admin"
    username = "admin"
    password = "password123"
    password_hash = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

    try:
        cursor.execute("INSERT INTO usuarios (nombre, username, password_hash) VALUES (?, ?, ?)",
                       (nombre, username, password_hash))
        conn.commit()
        print(f"Usuario '{username}' creado correctamente.")
    except sqlite3.IntegrityError:
        print(f"Usuario '{username}' ya existe.")
    
    conn.close()

# Función para cargar credenciales desde la base de datos
def cargar_credenciales():
    conn = sqlite3.connect("usuarios.db")
    cursor = conn.cursor()
    cursor.execute("SELECT nombre, username, password_hash FROM usuarios")
    data = cursor.fetchall()
    conn.close()

    # Construir estructura de credenciales
    credenciales = {
        "usernames": {
            row[1]: {
                "name": row[0],
                "password": row[2]
            }
            for row in data
        }
    }
    return credenciales

# Probar autenticación
def probar_autenticacion():
    credenciales = cargar_credenciales()

    # Crear autenticador con credenciales
    authenticator = Authenticate(
        credentials=credenciales,
        cookie_name="validacion_saldos",
        key="llave_secreta",
        cookie_expiry_days=7,
    )

    username = "admin"
    password = "password123"

    # Validar credenciales
    if username in credenciales["usernames"]:
        hash_password = credenciales["usernames"][username]["password"]
        if bcrypt.checkpw(password.encode('utf-8'), hash_password.encode('utf-8')):
            print(f"Autenticación exitosa para '{username}'.")
        else:
            print(f"Fallo de autenticación para '{username}'.")
    else:
        print(f"Usuario '{username}' no encontrado.")

# Probar procesamiento de datos
def probar_procesamiento():
    # Leer archivos de prueba
    ecc_data = pd.DataFrame({
        "Ledger": ["L1", "L2"],
        "Moneda": ["USD", "EUR"],
        "Sociedad": ["S1", "S2"],
        "Cuenta": ["C1", "C2"],
        "Saldo_ECC": [1000, 2000],
    })

    s4_data = pd.DataFrame({
        "Ledger": ["L1", "L2"],
        "Moneda": ["USD", "EUR"],
        "Sociedad": ["S1", "S2"],
        "Cuenta": ["C1", "C2"],
        "Saldo_S4": [1100, 2100],
    })

    tipo_data = pd.DataFrame({
        "Sociedad": ["S1", "S2"],
        "Cuenta": ["C1", "C2"],
        "Tipo_Cuenta": ["Activo", "Pasivo"],
    })

    # Merge y procesamiento
    combined = pd.merge(ecc_data, s4_data, on=["Ledger", "Moneda", "Sociedad", "Cuenta"], how="outer")
    combined = pd.merge(combined, tipo_data, on=["Sociedad", "Cuenta"], how="left")

    combined["Diferencia"] = combined["Saldo_S4"] - combined["Saldo_ECC"]
    print("\nDatos Procesados:")
    print(combined)

# Ejecutar pruebas
if __name__ == "__main__":
    print("=== Creando Base de Datos ===")
    crear_base_datos()

    print("\n=== Probando Autenticación ===")
    probar_autenticacion()

    print("\n=== Probando Procesamiento de Datos ===")
    probar_procesamiento()
