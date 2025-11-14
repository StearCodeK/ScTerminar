import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime
from models.compras_models import PurchaseModel
from views.compras_views import PurchaseView
from models.export_manager import ExportManager


class PurchaseController:
    def __init__(self, frame, app):
        self.model = PurchaseModel()
        self.view = PurchaseView(frame, app)
        self.view.set_controller(self)
        self.app = app
        self.setup_ui()

    def setup_ui(self):
        """Configura la interfaz de usuario"""
        self.view.setup_requests_tab()
        self.refresh_requests_table()

    def refresh_requests_table(self, status_filter="Todos", priority_filter="Todos"):
        """Actualiza la tabla de solicitudes"""
        try:
            data = self.model.get_all_requests(status_filter, priority_filter)
            self.view.refresh_table(data)
        except Exception as e:
            self.view.show_message("Error", f"Error al cargar solicitudes: {e}", "error")

    def apply_requests_filters(self, status, priority):
        """Aplica los filtros seleccionados"""
        self.refresh_requests_table(status, priority)

    def show_purchase_form(self):
        """Muestra el formulario para nueva solicitud de compra"""
        try:
            # Obtener datos del modelo
            categories = self.model.get_categories()
            products = [p[1] for p in self.model.get_active_products()]
            suppliers = self.model.get_suppliers()
            
            # Delegar a la view la creación del formulario
            self.view.show_purchase_form(
                categories, 
                products, 
                suppliers, 
                self.save_purchase_request
            )
        except Exception as e:
            self.view.show_message("Error", f"No se pudo cargar el formulario: {e}", "error")

    def save_purchase_request(self, entries, window):
        """Guarda una nueva solicitud de compra"""
        try:
            # Validación de cantidad
            try:
                cantidad = int(entries["Cantidad:"].get())
            except ValueError:
                self.view.show_message("Error", "La cantidad debe ser un número válido", "error")
                return

            # Preparar datos para el modelo
            data = (
                entries["Producto:"].get(),
                cantidad,
                entries["Motivo:"].get(),
                entries["Prioridad:"].get(),
                entries["Proveedor:"].get() if entries["Proveedor:"].get() else None,
                datetime.now(),
                "Pendiente"
            )

            # Guardar en el modelo
            self.model.create_request(data)
            
            self.view.show_message("Éxito", "Solicitud registrada correctamente", "info")
            window.destroy()
            self.refresh_requests_table()

        except Exception as e:
            self.view.show_message("Error", f"No se pudo guardar la solicitud: {e}", "error")

    def delete_request(self):
        """Elimina una solicitud seleccionada"""
        selected = self.view.get_selected_request()
        if not selected:
            self.view.show_message("Advertencia", "Seleccione una solicitud para eliminar", "warning")
            return

        request_id = selected[0]
        if not self.view.show_confirmation_dialog(
            "Confirmar", 
            f"¿Está seguro que desea eliminar la solicitud #{request_id}?"
        ):
            return

        try:
            self.model.delete_request(request_id)
            self.view.show_message("Éxito", "Solicitud eliminada correctamente", "info")
            self.refresh_requests_table()
        except Exception as e:
            self.view.show_message("Error", f"No se pudo eliminar la solicitud: {e}", "error")

    def edit_request_status(self):
        """Permite editar el estado de una solicitud seleccionada"""
        selected = self.view.get_selected_request()
        if not selected:
            self.view.show_message("Advertencia", "Seleccione una solicitud para editar", "warning")
            return

        request_id = selected[0]
        current_status = selected[7]

        # Delegar a la view la creación del formulario
        self.view.show_edit_status_form(
            request_id, 
            current_status, 
            self.update_request_status
        )

    def update_request_status(self, request_id, new_status, window):
        """Actualiza el estado de una solicitud"""
        try:
            self.model.update_request_status(request_id, new_status)
            self.view.show_message("Éxito", "Estado actualizado correctamente", "info")
            self.refresh_requests_table()
            window.destroy()
        except Exception as e:
            self.view.show_message("Error", f"No se pudo actualizar el estado: {e}", "error")

    def filter_products_by_category(self, category_name):
        """Filtra los productos según la categoría seleccionada"""
        try:
            products = self.model.get_products_by_category(
                category_name if category_name and category_name != "Todas" else None
            )
            return [p[1] for p in products]
        except Exception as e:
            self.view.show_message("Error", f"No se pudieron filtrar los productos: {e}", "error")
            return []

    def export_purchases(self):
        """Exportar solicitudes de compra a CSV"""
        try:
            # Obtener datos actuales de la tabla
            filtered_data = []
            for item in self.view.tree.get_children():
                row_data = self.view.tree.item(item)['values']
                filtered_data.append(row_data)

            # Usar ExportManager para exportar
            filename, error = ExportManager.export_purchases(filtered_data)

            if error:
                self.view.show_message("Error", f"Error al exportar: {error}", "error")
            else:
                self.view.show_message("Éxito", f"Solicitudes exportadas en {filename}", "info")

        except Exception as e:
            self.view.show_message("Error", f"Error al exportar solicitudes: {str(e)}", "error")