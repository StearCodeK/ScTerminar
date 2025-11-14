# views/settings_views.py
import tkinter as tk
from tkinter import ttk, messagebox
from views.base_view import BaseView
from helpers import clear_frame


class SettingsView(BaseView):
    def __init__(self, app):
        super().__init__(None, app)
        self.selected_item_data = None
        self.current_tree = None

    def show_settings(self):
        """Muestra la interfaz de configuración del sistema"""
        clear_frame(self.app.content_frame)
        
        # Contenedor principal
        main_container = self.create_main_container(self.app.content_frame)
        main_container.pack(fill="both", expand=True, padx=10, pady=10)

        # Título
        title_frame = self.create_section_frame(main_container)
        title_frame.pack(fill="x", pady=(0, 20))

        tk.Label(
            title_frame, 
            text="Configuración del Sistema",
            font=self.title_font, 
            bg=self.bg_color, 
            fg=self.fg_color
        ).pack(side="left")

        # Notebook (pestañas)
        notebook = ttk.Notebook(main_container)
        notebook.pack(fill="both", expand=True, padx=10, pady=10)

        return notebook

    def create_settings_tab(self, notebook, tab_config):
        """Crea una pestaña completa para administrar configuraciones"""
        # Frame para la pestaña
        tab_frame = self.create_main_container(notebook)
        notebook.add(tab_frame, text=tab_config["tab_name"])

        # Frame para botones de acción
        button_frame = self.create_section_frame(tab_frame)
        button_frame.pack(fill="x", padx=10, pady=5)

        # Tabla de datos
        table_frame, tree = self.create_table(
            tab_frame, 
            tab_config["display_columns"], 
            column_widths=tab_config.get("column_widths"), 
            height=15
        )
        table_frame.pack(fill="both", expand=True, padx=10, pady=10)

        # Configurar selección
        tree.bind("<<TreeviewSelect>>", lambda event: self.on_tree_select(event, tree))
        self.current_tree = tree

        return tree, button_frame

    def create_settings_buttons(self, parent, tab_key, on_add, on_edit, on_delete, on_activate, on_refresh):
        """Crea los botones de acción para una pestaña de settings"""
        # Frame para botones
        button_frame = tk.Frame(parent, bg=self.bg_color)
        button_frame.pack(fill="x", pady=5)
        
        actions = [
            ("➕ Agregar", lambda: on_add(tab_key)),
            ("✏️ Editar", lambda: on_edit(tab_key)),
            ("🚫 Desactivar", lambda: on_delete(tab_key)),  # Cambiado de "Eliminar"
            ("✅ Activar", lambda: on_activate(tab_key)),   # Nuevo botón
            ("🔄 Refrescar", lambda: on_refresh(tab_key))
        ]
        
        for text, command in actions:
            btn = ttk.Button(
                button_frame,
                text=text,
                command=command
            )
            btn.pack(side="left", padx=5)
            
        return button_frame

    def on_tree_select(self, event, tree):
        """Maneja la selección de items en el Treeview"""
        selected_item = tree.focus()
        if selected_item:
            self.selected_item_data = tree.item(selected_item)["values"]

    def load_table_data(self, tree, data):
        """Carga datos en el Treeview"""
        self.refresh_table_data(tree, data)

    def create_settings_dialog(self, title, fields_config, current_data=None):
        """Crea un diálogo para agregar/editar items en settings"""
        dialog = self.create_modal_window(self.app, title, "400x400")
        
        # Frame principal del formulario
        main_frame = self.create_form_frame(dialog, "Datos")
        main_frame.pack(fill="both", expand=True, padx=10, pady=10)

        entries = {}
        entry_vars = {}

        for i, (field_name, field_type, options) in enumerate(fields_config):
            label = self._get_field_label(field_name)
            
            if field_type == "checkbox":
                var = tk.BooleanVar()
                # Establecer valor actual si existe
                if current_data and i < len(current_data):
                    var.set(bool(current_data[i]))
                check = self._create_checkbox_field(main_frame, label, var, i)
                entries[field_name] = check
                entry_vars[field_name] = var
                
            elif field_type == "combobox":
                combo, var = self._create_combobox_field(main_frame, label, options, i)
                entries[field_name] = combo
                entry_vars[field_name] = var
                
                # Establecer valor actual si existe
                if current_data and i < len(current_data) and current_data[i]:
                    var.set(str(current_data[i]))
                    
            else:  # entry por defecto
                entry, var = self._create_entry_field(main_frame, label, i)
                entries[field_name] = entry
                entry_vars[field_name] = var
                
                # Establecer valor actual si existe
                if current_data and i < len(current_data):
                    var.set(str(current_data[i]) if current_data[i] is not None else "")

        # Botones del formulario
        btn_frame = tk.Frame(dialog, bg=self.bg_color)
        btn_frame.pack(fill="x", pady=10, padx=20)
        
        save_btn = ttk.Button(btn_frame, text="Guardar", style="Accent.TButton")
        save_btn.pack(side="right", padx=5)
        
        cancel_btn = ttk.Button(btn_frame, text="Cancelar")
        cancel_btn.pack(side="right", padx=5)
        cancel_btn.configure(command=dialog.destroy)

        # Centrar ventana
        self.center_window(dialog)

        return dialog, entries, entry_vars, save_btn

    def _get_field_label(self, field_name):
        """Obtiene la etiqueta formateada para un campo"""
        if field_name.startswith("id_"):
            return f"{field_name[3:].capitalize()}:"
        return f"{field_name.capitalize()}:"

    def _create_checkbox_field(self, parent, label, var, row):
        """Crea un campo checkbox"""
        label_widget = tk.Label(
            parent, 
            text=label, 
            font=self.form_label_font, 
            bg=self.bg_color, 
            fg=self.fg_color
        )
        label_widget.grid(row=row, column=0, padx=5, pady=5, sticky="e")
        
        check = tk.Checkbutton(parent, variable=var, bg=self.bg_color)
        check.grid(row=row, column=1, padx=5, pady=5, sticky="w")
        
        return check

    def _create_combobox_field(self, parent, label, options, row):
        """Crea un campo combobox"""
        label_widget = tk.Label(
            parent, 
            text=label, 
            font=self.form_label_font, 
            bg=self.bg_color, 
            fg=self.fg_color
        )
        label_widget.grid(row=row, column=0, padx=5, pady=5, sticky="e")
        
        combo = ttk.Combobox(parent, values=options or [])
        combo.grid(row=row, column=1, padx=5, pady=5, sticky="ew")
        
        var = tk.StringVar()
        combo.configure(textvariable=var)
        return combo, var

    def _create_entry_field(self, parent, label, row):
        """Crea un campo de entrada de texto"""
        label_widget = tk.Label(
            parent, 
            text=label, 
            font=self.form_label_font, 
            bg=self.bg_color, 
            fg=self.fg_color
        )
        label_widget.grid(row=row, column=0, padx=5, pady=5, sticky="e")
        
        entry = ttk.Entry(parent)
        entry.grid(row=row, column=1, padx=5, pady=5, sticky="ew")
        
        var = tk.StringVar()
        entry.configure(textvariable=var)
        return entry, var

    def get_form_values(self, fields_config, entry_vars):
        """Obtiene los valores del formulario procesados"""
        values = {}
        for field_name, field_type, _ in fields_config:
            if field_name in entry_vars:
                var = entry_vars[field_name]
                if field_type == "checkbox":
                    values[field_name] = var.get()
                else:
                    values[field_name] = var.get().strip()
        return values

    def show_message(self, title, message, message_type="info"):
        """Muestra mensajes al usuario"""
        if message_type == "info":
            messagebox.showinfo(title, message)
        elif message_type == "warning":
            messagebox.showwarning(title, message)
        elif message_type == "error":
            messagebox.showerror(title, message)

    def ask_confirmation(self, title, message):
        """Pide confirmación al usuario"""
        return messagebox.askyesno(title, message)

    def get_selected_item_data(self):
        """Obtiene los datos del ítem seleccionado"""
        return self.selected_item_data

    def clear_selection(self):
        """Limpia la selección actual"""
        self.selected_item_data = None