import tkinter as tk
from tkinter import ttk, messagebox
from views.base_view import BaseView


class PurchaseView(BaseView):
    def __init__(self, frame, app):
        super().__init__(frame, app)
        self.controller = None
        self.setup_styles()

    def set_controller(self, controller):
        self.controller = controller

    def setup_requests_tab(self):
        """Configura el contenido de la pestaña de solicitudes"""
        # Frame principal con padding
        main_frame = self.create_main_container(self.frame, padx=10, pady=5)
        main_frame.pack(fill="both", expand=True)
        
        # Frame para botones superiores
        top_button_frame = self.create_section_frame(main_frame)
        top_button_frame.pack(fill="x", pady=5)

        # Botones de acción usando el estilo Accent.TButton
        actions = [
            ("➕ Nueva Solicitud", self.controller.show_purchase_form),
            ("✏️ Editar Estado", self.controller.edit_request_status),
            ("🗑️ Eliminar", self.controller.delete_request),
            ("📤 Exportar", self.controller.export_purchases)
        ]
        
        btn_frame, buttons = self.create_action_buttons(top_button_frame, actions)
        btn_frame.pack(side="left")
        
        # Aplicar estilo de acento al primer botón
        if buttons:
            buttons[0].configure(style="Accent.TButton")

        # Frame para filtros
        filter_frame = self.create_filter_frame(main_frame, "Filtros")
        filter_frame.pack(fill="x", pady=10)

        # Filtro por estado
        status_frame, self.status_var, self.status_combo = self.create_filter_combo(
            filter_frame, 
            "Estado:", 
            ["Todos", "Pendiente", "Aprobado", "Rechazado", "En proceso", "Completado", "Cancelado"],
            "Todos",
            15
        )
        status_frame.pack(side="left", padx=10)

        # Filtro por prioridad
        priority_frame, self.priority_var, self.priority_combo = self.create_filter_combo(
            filter_frame, 
            "Prioridad:", 
            ["Todos", "Alta", "Media", "Baja"],
            "Todos",
            12
        )
        priority_frame.pack(side="left", padx=10)

        # Botón de aplicar filtros
        ttk.Button(
            filter_frame, 
            text="Aplicar Filtros", 
            command=self.apply_filters,
            style="TButton"
        ).pack(side="left", padx=10)

        # Tabla de solicitudes
        columns = ("Nro", "Producto", "Cantidad", "Motivo", "Prioridad", "Proveedor", "Fecha", "Estado")
        column_widths = [80, 150, 80, 150, 100, 150, 100, 120]
        
        table_frame, self.tree = self.create_table(
            main_frame, 
            columns, 
            column_widths, 
            height=15
        )
        table_frame.pack(fill="both", expand=True, pady=10)

    def apply_filters(self):
        """Aplica los filtros seleccionados"""
        status = self.status_var.get()
        priority = self.priority_var.get()
        self.controller.apply_requests_filters(status, priority)

    def get_selected_request(self):
        """Obtiene la solicitud seleccionada en la tabla"""
        return self.get_selected_table_item(self.tree)

    def refresh_table(self, data):
        """Actualiza la tabla con nuevos datos"""
        self.refresh_table_data(self.tree, data)

    def show_purchase_form(self, categories, products, suppliers, on_save_callback):
        """Muestra el formulario para nueva solicitud de compra"""
        window = self.create_modal_window(self.frame, "Nueva Solicitud de Compra", "450x400")
        
        main_frame = self.create_form_frame(window, "Datos de la Solicitud")
        main_frame.pack(fill="both", expand=True, padx=10, pady=5)

        fields_config = [
            ("Categoría:", "combobox", categories),
            ("Producto:", "combobox", products),
            ("Cantidad:", "entry", None),
            ("Motivo:", "combobox", ["Reposición", "Nuevo producto", "Emergencia"]),
            ("Prioridad:", "combobox", ["Baja", "Media", "Alta"]),
            ("Proveedor:", "combobox", suppliers)
        ]
        
        entries = self.create_form_fields(main_frame, fields_config)

        # Botones del formulario
        btn_frame, save_btn, cancel_btn = self.create_form_buttons(window)
        btn_frame.pack(fill="x", pady=10)
        
        save_btn.configure(
            text="Enviar Solicitud",
            command=lambda: self._on_save_purchase_request(entries, window, on_save_callback)
        )
        cancel_btn.configure(command=window.destroy)

        self.center_window(window)
        return window, entries

    def show_edit_status_form(self, request_id, current_status, on_save_callback):
        """Muestra el formulario para editar estado"""
        window = self.create_modal_window(
            self.frame, f"Editar Estado - Solicitud #{request_id}", "320x200"
        )
        
        main_frame = self.create_form_frame(window, "Editar Estado")
        main_frame.pack(fill="both", expand=True, padx=10, pady=5)

        status_var = tk.StringVar(value=current_status)
        status_combo = self.create_form_field(
            main_frame, 
            "Nuevo estado:", 
            "combobox", 
            ["Pendiente", "Aprobado", "Rechazado", "En proceso", "Completado", "Cancelado"], 
            row=0
        )
        status_combo.config(textvariable=status_var)

        # Botones del formulario
        btn_frame, save_btn, cancel_btn = self.create_form_buttons(window)
        btn_frame.pack(fill="x", pady=10)
        
        save_btn.configure(
            command=lambda: self._on_save_status(request_id, current_status, status_var.get(), window, on_save_callback)
        )
        cancel_btn.configure(command=window.destroy)

        self.center_window(window)
        return window, status_var

    def _on_save_purchase_request(self, entries, window, on_save_callback):
        """Maneja el guardado de la solicitud de compra"""
        # Validación básica en la view
        required_fields = ["Producto:", "Cantidad:", "Motivo:", "Prioridad:"]
        for field in required_fields:
            if not entries[field].get():
                self.show_message("Error", f"El campo {field} es obligatorio", "warning")
                return
        
        # Delegar al controller la lógica de negocio
        on_save_callback(entries, window)

    def _on_save_status(self, request_id, current_status, new_status, window, on_save_callback):
        """Maneja el guardado del estado"""
        if new_status == current_status:
            self.show_message("Información", "No se realizaron cambios", "info")
            window.destroy()
            return
        
        on_save_callback(request_id, new_status, window)

    def show_confirmation_dialog(self, title, message):
        """Muestra un diálogo de confirmación"""
        return messagebox.askyesno(title, message)

    def show_message(self, title, message, message_type="info"):
        """Muestra un mensaje al usuario"""
        if message_type == "info":
            messagebox.showinfo(title, message)
        elif message_type == "warning":
            messagebox.showwarning(title, message)
        elif message_type == "error":
            messagebox.showerror(title, message)