import psycopg2
from psycopg2 import OperationalError
from tkinter import messagebox
import threading


def create_connection():
    """Crea y retorna una conexión a PostgreSQL"""
    try:
        conn = psycopg2.connect(
            host="localhost",
            database="inventario_usm",  # Nombre de tu BD
            user="postgres",            # Tu usuario
            password="123456789",   # Tu contraseña
            port="5432"
        )
        # Evitar que una excepción deje la conexión en un estado abortado
        # y simplificar la gestión de commits en una aplicación de escritorio.
        # Al activar autocommit, cada operación se confirma inmediatamente.
        conn.autocommit = True
        return conn
    except OperationalError as e:
        messagebox.showerror("Error de conexión",
                             f"No se pudo conectar a PostgreSQL: {e}")
        return None
