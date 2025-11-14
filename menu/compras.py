from helpers import clear_frame
from tkinter import ttk
import tkinter as tk
from controllers.compras_controllers import PurchaseController
from controllers.proveedores_controllers import SupplierController


def show_purchases(app):
    """Muestra la gestión de compras con pestañas principales"""
    clear_frame(app.content_frame)

    # Título
    title_frame = tk.Frame(app.content_frame, bg=app.colors["background"])
    title_frame.pack(fill="x", pady=(0, 20))

    tk.Label(title_frame, text="Gestión de Compras",
             font=app.title_font, bg=app.colors["background"]).pack(side="left")

    # Notebook (pestañas)
    notebook = ttk.Notebook(app.content_frame)
    notebook.pack(fill="both", expand=True, padx=20, pady=10)

    # Pestaña de solicitudes
    requests_frame = tk.Frame(notebook, bg="white")
    notebook.add(requests_frame, text="📋 Compras")
    purchase_controller = PurchaseController(requests_frame, app)

    # Pestaña de proveedores
    suppliers_frame = tk.Frame(notebook, bg="white")
    notebook.add(suppliers_frame, text="👥 Proveedores")
    supplier_controller = SupplierController(suppliers_frame, app)
