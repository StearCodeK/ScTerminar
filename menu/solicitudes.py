from helpers import clear_frame
from tkinter import ttk
import tkinter as tk
from controllers.solicitudes_controller import SolicitudesController


def show_solicitudes(app):
    """Muestra la gestión de solicitudes dentro de una pestaña"""
    clear_frame(app.content_frame)

    # Título
    title_frame = tk.Frame(app.content_frame, bg=app.colors["background"])
    title_frame.pack(fill="x", pady=(0, 20))

    tk.Label(title_frame, text="Solicitudes",
             font=app.title_font, bg=app.colors["background"]).pack(side="left")

   
