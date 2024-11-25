import streamlit as st
import pandas as pd
from fpdf import FPDF
import requests

def descargar_usuarios_csv():
    url = "https://raw.githubusercontent.com/Victorcortes-monroy01/Validacion-SAP-saldoscuenta/main/usuarios.csv"
    try:
        response = requests.get(url)
        response.raise_for_status()  # Esto lanza un error si la descarga falla
        with open("usuarios.csv", "wb") as file:
            file.write(response.content)
        print("Archivo usuarios.csv descargado correctamente.")
    except requests.exceptions.RequestException as e:
        print(f"Error al descargar el archivo usuarios.csv: {e}")
        raise

# Descargar el archivo antes de usarlo
descargar_usuarios_csv()

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
    st.query_params.clear()  # Limpiar los parámetros de la URL

# Pantalla de inicio de sesión
def login():
    st.title("Inicio de Sesión")
    usuario = st.text_input("Usuario")
    clave = st.text_input("Clave", type="password")
    if st.button("Ingresar"):
        if validar_credenciales(usuario, clave):
            st.session_state["usuario"] = usuario
            st.query_params.clear()  # Reinicia la URL tras el inicio de sesión
        else:
            st.error("Usuario o clave incorrectos.")

# Función para generar el reporte en PDF
def generar_reporte_pdf(metrica, diferencias, output_pdf):
    pdf = FPDF()
    pdf.set_auto_page_break(auto=True, margin=15)
    pdf.add_page()
    pdf.set_font("Arial", size=12)

    # Título del reporte
    pdf.set_font("Arial", style="B", size=16)
    pdf.cell(200, 10, txt="Reporte de Validación de Saldos SAP", ln=True, align="C")
    pdf.ln(10)

    # Resumen de métricas
    pdf.set_font("Arial", size=12)
    pdf.cell(200, 10, txt="Resumen de Métricas:", ln=True)
    pdf.ln(5)
    pdf.set_font("Arial", size=10)
    for key, value in metrica.items():
        pdf.cell(200, 10, txt=f"{key}: {value}", ln=True)

    pdf.ln(10)

    # Tabla de diferencias
    pdf.set_font("Arial", style="B", size=10)
    pdf.cell(200, 10, txt="Cuentas con Diferencias:", ln=True)
    pdf.ln(5)

    pdf.set_font("Arial", size=8)
    column_widths = [25, 25, 25, 25, 30, 30, 30]
    headers = ["Ledger", "Moneda", "Sociedad", "Cuenta", "Saldo ECC", "Saldo S4", "Diferencia"]

    for col, width in zip(headers, column_widths):
        pdf.cell(width, 10, col, border=1, align="C")
    pdf.ln()

    for _, row in diferencias.iterrows():
        pdf.cell(column_widths[0], 8, str(row["Ledger"]), border=1)
        pdf.cell(column_widths[1], 8, str(row["Moneda"]), border=1)
        pdf.cell(column_widths[2], 8, str(row["Sociedad"]), border=1)
        pdf.cell(column_widths[3], 8, str(row["Cuenta"]), border=1)
        pdf.cell(column_widths[4], 8, f"{row['Saldo_ECC']:.2f}", border=1, align="R")
        pdf.cell(column_widths[5], 8, f"{row['Saldo_S4']:.2f}", border=1, align="R")
        pdf.cell(column_widths[6], 8, f"{row['Diferencia']:.2f}", border=1, align="R")
        pdf.ln()

    pdf.output(output_pdf)
    return output_pdf

# Pantalla principal de la app
def app_principal():
    st.sidebar.title("Menú")
    usuario = st.session_state["usuario"]
    nombre_usuario = credenciales["usernames"][usuario]["name"]
    st.sidebar.write(f"Hola, **{nombre_usuario}** 👋")

    ecc_file = st.sidebar.file_uploader("Sube el archivo SALDOSECC", type=["xlsx"])
    s4_file = st.sidebar.file_uploader("Sube el archivo SALDOSS4", type=["xlsx"])
    tipo_file = st.sidebar.file_uploader("Sube el archivo Tipos de Cuenta", type=["xlsx"])

    if ecc_file and s4_file and tipo_file:
        try:
            ecc_data = pd.read_excel(ecc_file)
            s4_data = pd.read_excel(s4_file)
            tipo_data = pd.read_excel(tipo_file)

            ecc_data.columns = ["Ledger", "Moneda", "Sociedad", "Cuenta", "Saldo_ECC"]
            s4_data.columns = ["Ledger", "Moneda", "Sociedad", "Cuenta", "Saldo_S4"]
            tipo_data.columns = ["Sociedad", "Cuenta", "Tipo_Cuenta"]

            ecc_data = ecc_data.drop_duplicates()
            s4_data = s4_data.drop_duplicates()

            combined = pd.merge(
                ecc_data, s4_data, on=["Ledger", "Moneda", "Sociedad", "Cuenta"], how="outer"
            )

            combined["Saldo_ECC"] = combined["Saldo_ECC"].fillna(0)
            combined["Saldo_S4"] = combined["Saldo_S4"].fillna(0)

            combined["Diferencia"] = combined["Saldo_S4"] - combined["Saldo_ECC"]
            combined = pd.merge(combined, tipo_data, on=["Sociedad", "Cuenta"], how="left")

            solo_en_ecc = combined[(combined["Saldo_ECC"] != 0) & (combined["Saldo_S4"] == 0)]
            solo_en_s4 = combined[(combined["Saldo_S4"] != 0) & (combined["Saldo_ECC"] == 0)]
            cuentas_comunes = combined[(combined["Saldo_ECC"] != 0) & (combined["Saldo_S4"] != 0)]
            diferencias = cuentas_comunes[cuentas_comunes["Diferencia"] != 0]

            metrica = {
                "Total de cuentas procesadas": len(combined),
                "Cuentas únicas en SALDOSECC": len(solo_en_ecc),
                "Cuentas únicas en SALDOSS4": len(solo_en_s4),
                "Cuentas comunes procesadas": len(cuentas_comunes),
                "Cuentas con diferencias": len(diferencias),
                "Porcentaje de diferencias": f"{(len(diferencias) / len(cuentas_comunes) * 100):.2f}%",
            }

            st.subheader("Resumen de Resultados")
            for key, value in metrica.items():
                st.write(f"**{key}:** {value}")

            output_excel = "Saldos_Validados.xlsx"
            with pd.ExcelWriter(output_excel, engine="openpyxl") as writer:
                combined.to_excel(writer, index=False, sheet_name="Consolidado")
                solo_en_ecc.to_excel(writer, index=False, sheet_name="Solo en ECC")
                solo_en_s4.to_excel(writer, index=False, sheet_name="Solo en S4")

            st.download_button(
                label="Descargar Excel Automatizado",
                data=open(output_excel, "rb"),
                file_name="Saldos_Validados.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            )

        except Exception as e:
            st.error(f"Error al procesar los archivos: {e}")

    if st.sidebar.button("Cerrar Sesión"):
        cerrar_sesion()

# Lógica principal de la app
if st.session_state["usuario"] is None:
    login()
else:
    app_principal()
