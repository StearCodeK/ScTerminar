import tkinter as tk
from tkinter import ttk, messagebox
from views.base_view import BaseView


class MovementView(BaseView):
    def __init__(self, frame, app):
        super().__init__(frame, app)
        self.controller = None
        self.setup_styles()

    def set_controller(self, controller):
        self.controller = controller

    def setup_movements_tab(self):
        """Configura la interfaz de movimientos de inventario"""
        # Filtros: usar el método de BaseView para crear frame de filtros
        filter_frame = self.create_filter_frame(self.frame, "Filtros")
        filter_frame.pack(fill="x", padx=10, pady=(0, 5))

        # Filtro por tipo de movimiento
        tk.Label(filter_frame, text="Tipo:",
                 bg=self.bg_color, fg=self.fg_color, font=self.label_font).pack(side="left", padx=5)

        self.type_combo = ttk.Combobox(filter_frame, values=[
            "Todos", "Entrada", "Salida"], state="readonly", font=self.entry_font)
        self.type_combo.set("Todos")
        self.type_combo.pack(side="left", padx=5)

        # Filtro por fecha
        tk.Label(filter_frame, text="Desde:",
                 bg=self.bg_color, fg=self.fg_color, font=self.label_font).pack(side="left", padx=5)

        self.date_from_entry = ttk.Entry(
            filter_frame, width=10, font=self.entry_font)
        self.date_from_entry.pack(side="left", padx=5)

        tk.Label(filter_frame, text="Hasta:",
                 bg=self.bg_color, fg=self.fg_color, font=self.label_font).pack(side="left", padx=5)

        self.date_to_entry = ttk.Entry(
            filter_frame, width=10, font=self.entry_font)
        self.date_to_entry.pack(side="left", padx=5)

        # Botón de aplicar filtros
        ttk.Button(filter_frame, text="Aplicar Filtros",
                   command=self.on_apply_filters).pack(side="left", padx=10)

        ttk.Button(filter_frame, text="📤 Exportar",
                   command=self.on_export).pack(side="left", padx=5)

        # Tabla de movimientos usando el método de BaseView
        columns = ("Nro", "Fecha", "Tipo", "Producto",
                   "Cantidad", "Responsable", "Referencia")
        column_widths = [50, 120, 80, 150, 80, 120, 150]

        table_frame, self.tree = self.create_table(
            self.frame,
            columns,
            column_widths=column_widths,
            height=20
        )
        table_frame.pack(fill="both", expand=True, padx=10, pady=(5, 10))

    def get_filter_values(self):
        """Obtiene los valores actuales de los filtros"""
        return {
            'movement_type': self.type_combo.get(),
            'date_from': self.date_from_entry.get(),
            'date_to': self.date_to_entry.get()
        }

    def on_apply_filters(self):
        """Callback cuando se aplican filtros"""
        if self.controller:
            filters = self.get_filter_values()
            self.controller.refresh_movements_table(**filters)

    def on_export(self):
        """Callback para exportar movimientos"""
        if self.controller:
            self.controller.export_movements()

    def refresh_table(self, data):
        """Actualiza la tabla con nuevos datos"""
        self.refresh_table_data(self.tree, data)

    def get_table_data(self):
        """Obtiene todos los datos actuales de la tabla"""
        data = []
        for item in self.tree.get_children():
            row_data = self.tree.item(item)['values']
            data.append(row_data)
        return data

    def show_error(self, message):
        """Muestra un mensaje de error"""
        messagebox.showerror("Error", message)

    def show_success(self, message):
        """Muestra un mensaje de éxito"""
        messagebox.showinfo("Éxito", message)

    def show_info(self, message):
        """Muestra un mensaje informativo"""
        messagebox.showinfo("Información", message)
