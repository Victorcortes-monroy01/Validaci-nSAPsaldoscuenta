import streamlit as st
import pandas as pd

# Configuración inicial de la app
st.set_page_config(page_title="Validación de Saldos SAP", layout="wide")

# Función para cargar credenciales desde el archivo CSV
def cargar_credenciales_csv():
    usuarios_csv = pd.read_csv("usuarios.csv")  # Cargar el archivo CSV
    credenciales = {
        "usernames": {
            row["usuario"]: {
                "name": row["nombre"],
                "password": row["clave"],
            }
            for _, row in usuarios_csv.iterrows()
        }
    }
    return credenciales

# Cargar credenciales
credenciales = cargar_credenciales_csv()

# Estado de sesión (login)
if "usuario" not in st.session_state:
    st.session_state["usuario"] = None

# Función para validar usuario y contraseña
def validar_credenciales(usuario, clave):
    if usuario in credenciales["usernames"]:
        usuario_data = credenciales["usernames"][usuario]
        return usuario_data["password"] == clave
    return False

# Función para cerrar sesión
def cerrar_sesion():
    st.session_state["usuario"] = None
    st.experimental_rerun()

# Pantalla de inicio de sesión
def login():
    st.title("Inicio de Sesión")
    usuario = st.text_input("Usuario")
    clave = st.text_input("Clave", type="password")
    if st.button("Ingresar"):
        if validar_credenciales(usuario, clave):
            st.session_state["usuario"] = usuario
            st.experimental_rerun()
        else:
            st.error("Usuario o clave incorrectos.")

# Pantalla principal de la app
def app_principal():
    st.sidebar.title("Menú")
    usuario = st.session_state["usuario"]
    nombre_usuario = credenciales["usernames"][usuario]["name"]
    st.sidebar.write(f"Hola, **{nombre_usuario}** 👋")

    menu = st.sidebar.radio("Selecciona una opción", ["Inicio", "Carga de archivos", "Reportes"])
    
    if menu == "Inicio":
        st.title("Validación de Saldos SAP")
        st.write("Bienvenido a la aplicación de validación de saldos.")
    elif menu == "Carga de archivos":
        st.title("Carga de Archivos")
        ecc_file = st.file_uploader("Sube el archivo SALDOSECC", type=["xlsx"])
        s4_file = st.file_uploader("Sube el archivo SALDOSS4", type=["xlsx"])
        tipo_file = st.file_uploader("Sube el archivo Tipos de Cuenta", type=["xlsx"])
        if ecc_file and s4_file and tipo_file:
            st.success("Archivos cargados correctamente.")
    elif menu == "Reportes":
        st.title("Generar Reportes")
        st.write("Esta funcionalidad estará disponible pronto.")
    
    if st.sidebar.button("Cerrar Sesión"):
        cerrar_sesion()

# Lógica principal de la app
if st.session_state["usuario"] is None:
    login()
else:
    app_principal()
