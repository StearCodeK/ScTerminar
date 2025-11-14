# [file name]: pedidos.py (modificado)
from tkinter import ttk
import tkinter as tk
from helpers import clear_frame
from controllers.solicitudes_controller import SolicitudesController


def show_requests(app, current_user=None):
    """Muestra la gestión de solicitudes usando el patrón MVC"""
    clear_frame(app.content_frame)

    # Asegurarse de que current_user está disponible
    if current_user is None and hasattr(app, 'current_user'):
        current_user = app.current_user

    # Crear controlador
    controller = SolicitudesController(
        app.content_frame,
        app.colors,
        app.title_font,
        app
    )

    # Configurar usuario actual
    controller.current_user = current_user

    # Mostrar interfaz principal
    controller.mostrar_interfaz_principal()

    # Guardar referencia al controlador en la app
    app.solicitudes_controller = controller
