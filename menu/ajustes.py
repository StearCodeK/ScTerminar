# ajustes.py (archivo principal simplificado)
from controllers.settings_controller import SettingsController


def show_settings(app):
    """Función para mostrar la configuración desde el menú principal"""
    try:
        settings = SettingsController(app)
        settings.show_settings()
        return settings  # Para mantener la referencia si es necesario
    except Exception as e:
        from tkinter import messagebox
        messagebox.showerror(
            "Error", f"No se pudo cargar la configuración: {str(e)}")
