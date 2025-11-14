from helpers import clear_frame
from tkinter import ttk
import tkinter as tk
from controllers.movimientos_controllers import MovementController


def show_movements(app):
    """Muestra la gestión de movimientos de inventario dentro de una pestaña"""
    clear_frame(app.content_frame)

    # Título con menos espacio
    title_frame = tk.Frame(app.content_frame, bg=app.colors["background"])
    title_frame.pack(fill="x", pady=(5, 10))  # Reducir padding vertical

    tk.Label(title_frame, text="Movimientos de Inventario",
             font=app.title_font, bg=app.colors["background"]).pack(side="left")

    # Frame principal para movimientos
    movements_frame = tk.Frame(app.content_frame, bg=app.colors.get("background", "white"))
    movements_frame.pack(fill="both", expand=True, padx=0, pady=0)  # Eliminar padding

    # Crear el controlador que manejará toda la lógica
    movement_controller = MovementController(movements_frame, app)