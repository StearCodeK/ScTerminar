# controllers/settings_controller.py
import tkinter as tk
from tkinter import ttk
from models.settings_models import SettingsModel
from views.settings_views import SettingsView


class SettingsController:
    def __init__(self, app):
        self.app = app
        self.model = SettingsModel()
        self.view = SettingsView(app)
        self.trees = {}  # <--- Agrega esto

        # Configuración de las pestañas - AGREGAR COLUMNA ACTIVO
        self.tabs_config = {
            "categorias": {
                "tab_name": "📦 Categorías",
                "table_name": "categorias",
                "fields_config": [
                    ("nombre", "entry", None),
                    ("activo", "checkbox", None)
                ],
                "display_columns": ["ID", "Nombre", "Activo"],
                "column_widths": [50, 200, 60],
                "id_column": "id_categoria"
            },
            "departamentos": {
                "tab_name": "🏢 Departamentos",
                "table_name": "departamentos",
                "fields_config": [
                    ("nombre", "entry", None),
                    ("activo", "checkbox", None)
                ],
                "display_columns": ["ID", "Nombre", "Activo"],
                "column_widths": [50, 200, 60],
                "id_column": "id_departamento"
            },
            "ubicaciones": {
                "tab_name": "📍 Ubicaciones",
                "table_name": "ubicaciones",
                "fields_config": [
                    ("nombre", "entry", None),
                    ("activo", "checkbox", None)
                ],
                "display_columns": ["ID", "Nombre", "Activo"],
                "column_widths": [50, 200, 60],
                "id_column": "id_ubicacion"
            },
            "marcas": {
                "tab_name": "🏷️ Marcas",
                "table_name": "marcas",
                "fields_config": [
                    ("nombre", "entry", None),
                    ("activo", "checkbox", None)
                ],
                "display_columns": ["ID", "Nombre", "Activo"],
                "column_widths": [50, 200, 60],
                "id_column": "id_marca"
            },
            "solicitantes": {
                "tab_name": "🙋 Solicitantes",
                "table_name": "solicitantes",
                "fields_config": [
                    ("cedula", "entry", None),
                    ("nombre", "entry", None),
                    ("id_departamento", "combobox", []),
                    ("activo", "checkbox", None)
                ],
                "display_columns": ["ID", "Cédula", "Nombre", "Departamento", "Activo"],
                "column_widths": [50, 100, 150, 120, 60],
                "id_column": "id_solicitante"
            },
            "proveedores": {
                "tab_name": "👥 Proveedores",
                "table_name": "proveedores",
                "fields_config": [
                    ("nombre", "entry", None),
                    ("contacto", "entry", None),
                    ("telefono", "entry", None),
                    ("email", "entry", None),
                    ("direccion", "entry", None),
                    ("activo", "checkbox", None)
                ],
                "display_columns": ["ID", "Nombre", "Contacto", "Teléfono", "Email", "Activo"],
                "column_widths": [50, 120, 120, 100, 150, 60],
                "id_column": "id_proveedor"
            },
            "usuarios": {
                "tab_name": "👤 Usuarios",
                "table_name": "usuarios",
                "fields_config": [
                    ("nombre_completo", "entry", None),
                    ("email", "entry", None),
                    ("usuario", "entry", None),
                    ("rol", "combobox", ["admin", "usuario"]),
                    ("activo", "checkbox", None)
                ],
                "display_columns": ["ID", "Nombre", "Email", "Usuario", "Rol", "Activo"],
                "column_widths": [50, 120, 150, 100, 80, 60],
                "id_column": "id"
            },
            "productos": {
                "tab_name": "📦 Productos",
                "table_name": "productos",
                "fields_config": [
                    ("codigo", "entry", None),
                    ("nombre", "entry", None),
                    ("id_marca", "combobox", []),
                    ("id_categoria", "combobox", []),
                    ("stock_minimo", "entry", None),  # NUEVO CAMPO
                    ("activo", "checkbox", None)
                ],
                "display_columns": ["ID", "Código", "Nombre", "Marca", "Categoría", "Stock (m)", "Activo"],
                "column_widths": [50, 80, 150, 100, 100, 80, 60],
                "id_column": "id_producto"
            }
        }
    def show_settings(self):
        """Muestra la interfaz de configuración"""
        notebook = self.view.show_settings()

        # Crear todas las pestañas
        for tab_key, config in self.tabs_config.items():
            self._create_tab(notebook, tab_key, config)

    def _create_tab(self, notebook, tab_key, config):
        """Crea una pestaña específica"""
        tree, button_frame = self.view.create_settings_tab(notebook, config)
        self.trees[tab_key] = tree  # <--- Guarda el tree por tab_key

        # Crear botones en la View con funcionalidad extendida
        self.view.create_settings_buttons(
            button_frame, 
            tab_key,
            self.add_item_dialog,
            self.edit_item_dialog,
            self.delete_item,
            self.activate_item,  # Nuevo botón para activar
            self.refresh_tab
        )

        # Cargar datos iniciales
        self.refresh_tab(tab_key)

    def refresh_tab(self, tab_key):
        """Refresca los datos de una pestaña"""
        try:
            config = self.tabs_config[tab_key]
            data = self.model.get_all_data(config["table_name"])
            tree = self.trees.get(tab_key)  # <--- Usa el tree correcto
            self.view.load_table_data(tree, data)
        except Exception as e:
            self.view.show_message(
                "Error", f"Error al cargar datos: {str(e)}", "error")

    def add_item_dialog(self, tab_key):
        """Muestra diálogo para agregar un nuevo ítem"""
        config = self.tabs_config[tab_key]
        
        # Preparar campos para relaciones
        fields_config = self._prepare_fields_config(config["fields_config"])
        
        # Crear diálogo en la View
        dialog, entries, entry_vars, save_btn = self.view.create_settings_dialog(
            f"Agregar {config['tab_name']}", 
            fields_config
        )

        # Configurar opciones para combobox de relaciones
        self._setup_relation_comboboxes(entries, fields_config)

        def save_item():
            try:
                # Obtener valores del formulario desde la View
                values = self.view.get_form_values(fields_config, entry_vars)
                
                # Validar campos requeridos
                self._validate_required_fields(values, config["fields_config"])
                
                # Preparar datos para inserción
                columns = [field[0] for field in config["fields_config"]]
                values_list = [values[field[0]] for field in config["fields_config"]]
                
                # Insertar en la base de datos
                self.model.insert_item(config["table_name"], columns, values_list)
                
                self.view.show_message("Éxito", "Ítem agregado correctamente", "info")
                dialog.destroy()
                self.refresh_tab(tab_key)
                
            except Exception as e:
                self.view.show_message("Error", str(e), "error")

        # Conectar el botón guardar
        save_btn.configure(command=save_item)

    def edit_item_dialog(self, tab_key):
        """Muestra diálogo para editar un ítem existente"""
        selected_data = self.view.get_selected_item_data()
        if not selected_data:
            self.view.show_message(
                "Advertencia", "Por favor seleccione un ítem para editar", "warning")
            return

        config = self.tabs_config[tab_key]
        selected_id = selected_data[0]

        try:
            # Obtener datos actuales del modelo
            current_data = self.model.get_item_by_id(
                config["table_name"], config["id_column"], selected_id)
            if not current_data:
                self.view.show_message("Error", "No se encontró el ítem seleccionado", "error")
                return

            # Preparar campos y datos actuales
            fields_config = self._prepare_fields_config(config["fields_config"])
            current_values = current_data[1:1+len(config["fields_config"])]

            # Crear diálogo en la View
            dialog, entries, entry_vars, save_btn = self.view.create_settings_dialog(
                f"Editar {config['tab_name']}", 
                fields_config, 
                current_values
            )

            # Configurar opciones para combobox de relaciones
            self._setup_relation_comboboxes(entries, fields_config, current_values)

            def update_item():
                try:
                    # Obtener valores del formulario desde la View
                    values = self.view.get_form_values(fields_config, entry_vars)
                    
                    # Validar campos requeridos
                    self._validate_required_fields(values, config["fields_config"])
                    
                    # Preparar datos para actualización
                    columns = [field[0] for field in config["fields_config"]]
                    values_list = [values[field[0]] for field in config["fields_config"]]
                    
                    # Actualizar en la base de datos
                    self.model.update_item(
                        config["table_name"], config["id_column"], selected_id, 
                        columns, values_list
                    )
                    
                    self.view.show_message("Éxito", "Ítem actualizado correctamente", "info")
                    dialog.destroy()
                    self.refresh_tab(tab_key)
                    
                except Exception as e:
                    self.view.show_message("Error", str(e), "error")

            # Conectar el botón guardar
            save_btn.configure(command=update_item)

        except Exception as e:
            self.view.show_message("Error", f"Error al cargar datos: {str(e)}", "error")

    def delete_item(self, tab_key):
        """Elimina/desactiva un ítem seleccionado"""
        selected_data = self.view.get_selected_item_data()
        if not selected_data:
            self.view.show_message(
                "Advertencia", "Por favor seleccione un ítem para eliminar", "warning")
            return

        config = self.tabs_config[tab_key]
        selected_id = selected_data[0]
        item_name = selected_data[1] if len(selected_data) > 1 else selected_id

        if self.view.ask_confirmation(
            "Confirmar desactivación",
            f"¿Está seguro que desea desactivar '{item_name}'?\n\n"
            f"✅ El ítem ya no aparecerá en los combobox\n"
            f"📋 Se mantendrá en registros históricos\n"
            f"🔄 Podrá reactivarlo más tarde si es necesario"
        ):
            try:
                # Intentar eliminación lógica primero
                self.model.soft_delete_item(config["table_name"], config["id_column"], selected_id)
                self.view.show_message("Éxito", "Ítem desactivado correctamente. Ya no aparecerá en los combobox.", "info")
                self.refresh_tab(tab_key)
                
                # Notificar al controlador de productos para refrescar combobox
                self._notify_product_controller()
                
            except Exception as e:
                self.view.show_message("Error", str(e), "error")
                
    def _notify_product_controller(self):
        """Notificar al controlador de productos para refrescar combobox"""
        try:
            # Buscar el controlador de productos en la app
            if hasattr(self.app, 'product_controller'):
                self.app.product_controller.refresh_comboboxes()
        except Exception as e:
            print(f"Error al notificar controlador de productos: {e}")
                    
    def activate_item(self, tab_key):
        """Reactiva un ítem previamente desactivado"""
        selected_data = self.view.get_selected_item_data()
        if not selected_data:
            self.view.show_message(
                "Advertencia", "Por favor seleccione un ítem para activar", "warning")
            return

        config = self.tabs_config[tab_key]
        selected_id = selected_data[0]
        item_name = selected_data[1] if len(selected_data) > 1 else selected_id

        if self.view.ask_confirmation(
            "Confirmar activación",
            f"¿Está seguro que desea activar '{item_name}'?\n\n"
            f"✅ El ítem volverá a aparecer en los combobox"
        ):
            try:
                success = self.model.activate_item(config["table_name"], config["id_column"], selected_id)
                if success:
                    self.view.show_message("Éxito", "Ítem activado correctamente. Ahora aparecerá en los combobox.", "info")
                    self.refresh_tab(tab_key)
                    
                    # Notificar al controlador de productos para refrescar combobox
                    self._notify_product_controller()
                    
                else:
                    self.view.show_message("Error", "No se pudo activar el ítem", "error")
            except Exception as e:
                self.view.show_message("Error", str(e), "error")

    def _prepare_fields_config(self, fields_config):
        """Prepara la configuración de campos para el diálogo"""
        prepared_config = []
        for field_name, field_type, options in fields_config:
            if field_name.startswith("id_"):
                # Para campos de relación, usar combobox
                prepared_config.append((field_name, "combobox", []))
            else:
                prepared_config.append((field_name, field_type, options))
        return prepared_config

    def _setup_relation_comboboxes(self, entries, fields_config, current_values=None):
        """Configura los combobox para campos de relación"""
        for i, (field_name, field_type, _) in enumerate(fields_config):
            if field_name.startswith("id_") and field_name in entries:
                related_table = field_name[3:]  # Remueve "id_" del inicio
                try:
                    options = self.model.get_related_options(related_table)
                    
                    # Crear diccionario para mostrar nombres en lugar de IDs
                    options_dict = {str(row[0]): row[1] for row in options}
                    display_values = [f"{id} - {name}" for id, name in options]
                    
                    # Configurar valores del combobox (mostrar ID - Nombre)
                    entries[field_name]["values"] = display_values
                    
                    # Establecer valor actual si existe
                    if current_values and i < len(current_values) and current_values[i]:
                        current_id = str(current_values[i])
                        current_name = options_dict.get(current_id, '')
                        display_text = f"{current_id} - {current_name}" if current_name else current_id
                        entries[field_name].set(display_text)
                    
                except Exception as e:
                    self.view.show_message(
                        "Error", f"Error al cargar {related_table}: {str(e)}", "error")

    def _validate_required_fields(self, values, fields_config):
        """Valida los campos requeridos"""
        optional_fields = ["contacto", "telefono", "email", "direccion", "activo"]
        
        for field_name, field_type, _ in fields_config:
            if field_name not in optional_fields and not values.get(field_name):
                raise Exception(f"El campo {field_name} es requerido")

    def close_connections(self):
        """Cierra las conexiones"""
        self.model.close_connection()