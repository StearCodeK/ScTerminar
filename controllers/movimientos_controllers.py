from models.movimientos_models import MovementModel
from models.export_manager import ExportManager


class MovementController:
    def __init__(self, frame=None, app=None, create_ui=True):
        """Controller de movimientos.

        Args:
            frame: frame donde montar la UI (opcional)
            app: referencia a la app
            create_ui: si False, no crea la interfaz (útil para registrar movimientos programáticamente)
        """
        self.model = MovementModel()
        self.app = app
        self.view = None

        if create_ui and frame:
            self._setup_view(frame)

    def _setup_view(self, frame):
        """Configura la vista (separado para mejor testabilidad)"""
        from views.movimientos_views import MovementView
        self.view = MovementView(frame, self.app)
        self.view.set_controller(self)
        self.view.setup_movements_tab()
        self.refresh_movements_table()

    def refresh_movements_table(self, movement_type="Todos", date_from=None, date_to=None):
        """Actualiza la tabla de movimientos con los filtros aplicados"""
        try:
            data = self.model.get_all_movements(
                movement_type, date_from, date_to)
            # Adaptar los datos para eliminar la columna de ubicación si está presente
            # (por si hay datos antiguos con más columnas)
            data = [row[:5] + row[6:]
                    if len(row) == 8 else row for row in data]
            if self.view:
                self.view.refresh_table(data)
            return data
        except Exception as e:
            if self.view:
                self.view.show_error(
                    f"No se pudieron cargar los movimientos: {e}")
            raise e

    def register_movement(self, id_producto, tipo, cantidad, id_responsable=None, referencia=None):
        """Registra un movimiento en la base de datos (sin ubicación)"""
        try:
            success = self.model.register_movement(
                id_producto, tipo, cantidad, id_responsable, referencia
            )
            if success and self.view:
                self.view.show_success("Movimiento registrado correctamente")
                self.refresh_movements_table()
            return success
        except Exception as e:
            if self.view:
                self.view.show_error(
                    f"No se pudo registrar el movimiento: {e}")
            return False

    def get_product_name(self, product_id):
        """Obtiene el nombre de un producto por ID"""
        return self.model.get_product_name(product_id)

    def export_movements(self):
        """Exportar movimientos a CSV"""
        if not self.view:
            return None, "No hay vista disponible para exportar"

        try:
            # Obtener datos actuales de la vista
            filtered_data = self.view.get_table_data()

            # Usar ExportManager para exportar
            filename, error = ExportManager.export_movements(filtered_data)

            if error:
                self.view.show_error(f"Error al exportar: {error}")
            else:
                self.view.show_success(f"Movimientos exportados en {filename}")

            return filename, error

        except Exception as e:
            error_msg = f"Error al exportar movimientos: {str(e)}"
            if self.view:
                self.view.show_error(error_msg)
            return None, error_msg

    def get_movement_statistics(self, movement_type="Todos", date_from=None, date_to=None):
        """Obtiene estadísticas de movimientos (ejemplo de lógica de negocio pura)"""
        try:
            data = self.model.get_all_movements(
                movement_type, date_from, date_to)
            # Calcular estadísticas
            total_entradas = sum(row[4] for row in data if row[2] == "Entrada")
            total_salidas = sum(row[4] for row in data if row[2] == "Salida")

            return {
                'total_movimientos': len(data),
                'total_entradas': total_entradas,
                'total_salidas': total_salidas,
                'balance': total_entradas - total_salidas
            }
        except Exception as e:
            if self.view:
                self.view.show_error(f"Error al calcular estadísticas: {e}")
            return None
