from tkinter import ttk, messagebox
import tkinter as tk
from database import create_connection
from helpers import clear_frame
from views.base_view import BaseView

# Conexión a PostgreSQL
conn = create_connection()
cursor = conn.cursor()


class NotificationManager(BaseView):
    def __init__(self, app):
        # Inicializamos BaseView sin frame específico ya que es un manager
        super().__init__(None, app)
        self.app = app
        self.notification_count = 0
        self.notifications = []

    def check_low_stock(self):
        """Verifica productos con stock bajo y actualiza las notificaciones"""
        try:
            cursor.execute("""
                SELECT p.id_producto, p.nombre, i.stock, c.nombre as categoria, p.stock_minimo
                FROM productos p
                JOIN inventario i ON p.id_producto = i.id_producto
                LEFT JOIN categorias c ON p.id_categoria = c.id_categoria
                WHERE p.activo = TRUE
                  AND i.stock <= COALESCE(p.stock_minimo, 0)
                ORDER BY i.stock ASC
            """)
            low_stock_items = cursor.fetchall()

            self.notifications = []
            for item in low_stock_items:
                self.notifications.append({
                    'id': item[0],
                    'product': item[1],
                    'stock': item[2],
                    'category': item[3] or 'Sin categoría',
                    'stock_minimo': item[4] if item[4] is not None else 0
                })

            self.notification_count = len(self.notifications)
            self.update_bell_icon()

        except Exception as e:
            print(f"Error al verificar stock bajo: {e}")
            conn.rollback()
        finally:
            # Programar la próxima verificación en 5 minutos (300000 ms)
            self.app.after(300000, self.check_low_stock)

    def update_bell_icon(self):
        """Actualiza el ícono de la campana con el contador de notificaciones"""
        if hasattr(self.app, 'bell_icon'):
            if self.notification_count > 0:
                self.app.bell_icon.config(
                    text=f"🔔 ({self.notification_count})", 
                    fg="red",
                    bg=self.bg_color,
                    font=self.button_font
                )
            else:
                self.app.bell_icon.config(
                    text="🔔", 
                    fg=self.fg_color,
                    bg=self.bg_color,
                    font=self.button_font
                )

    def show_notifications(self):
        """Muestra el menú de notificaciones con estilos aplicados"""
        if not hasattr(self.app, 'notification_menu'):
            self.app.notification_menu = tk.Menu(
                self.app, 
                tearoff=0,
                bg=self.bg_color,
                fg=self.fg_color,
                font=self.entry_font,
                relief="solid",
                borderwidth=1
            )

        # Limpiar menú anterior
        self.app.notification_menu.delete(0, tk.END)

        if self.notification_count == 0:
            self.app.notification_menu.add_command(
                label="No hay notificaciones",
                state=tk.DISABLED,
                background=self.bg_color,
                foreground=self.fg_color,
                font=self.entry_font
            )
        else:
            self.app.notification_menu.add_command(
                label=f"Tienes {self.notification_count} notificaciones",
                state=tk.DISABLED,
                background=self.bg_color,
                foreground=self.primary_color,
                font=self.label_font
            )
            self.app.notification_menu.add_separator()

            for notification in self.notifications:
                text = f"{notification['product']} - Stock: {notification['stock']} ({notification['category']})"
                self.app.notification_menu.add_command(
                    label=text,
                    command=lambda n=notification: self.show_product_detail(n['id']),
                    background=self.bg_color,
                    foreground=self.fg_color,
                    font=self.entry_font,
                    activebackground=self.primary_color,
                    activeforeground="white"
                )

            self.app.notification_menu.add_separator()
            self.app.notification_menu.add_command(
                label="Marcar todas como leídas",
                command=self.mark_all_as_read,
                background=self.bg_color,
                foreground=self.primary_color,
                font=self.button_font,
                activebackground=self.primary_color,
                activeforeground="white"
            )

        # Mostrar el menú
        try:
            self.app.notification_menu.tk_popup(
                self.app.winfo_pointerx(),
                self.app.winfo_pointery()
            )
        finally:
            self.app.notification_menu.grab_release()

    def show_product_detail(self, product_id):
        """Muestra los detalles del producto con stock bajo"""
        from menu.productos import show_inventory, edit_selected_product
        show_inventory(self.app)

        # Buscar el producto en el treeview y seleccionarlo
        tree = None
        for widget in self.app.content_frame.winfo_children():
            if isinstance(widget, ttk.Treeview):
                tree = widget
                break

        if tree:
            for child in tree.get_children():
                if tree.item(child, 'tags')[0] == str(product_id):
                    tree.selection_set(child)
                    tree.focus(child)
                    tree.see(child)
                    
                    # Resaltar la fila seleccionada
                    tree.tag_configure('selected', background=self.primary_color)
                    tree.item(child, tags=('selected',))
                    break

    def mark_all_as_read(self):
        """Marca todas las notificaciones como leídas (no las elimina, solo actualiza el contador)"""
        self.notification_count = 0
        self.update_bell_icon()
        
    def create_notification_bell(self, parent):
        """Crea el ícono de campana de notificaciones con estilos"""
        bell_icon = tk.Label(
            parent,
            text="🔔",
            cursor="hand2",
            bg=self.bg_color,
            fg=self.fg_color,
            font=self.button_font,
            padx=10
        )
        bell_icon.bind("<Button-1>", lambda e: self.show_notifications())
        return bell_icon

    def show_notification_toast(self, message, notification_type="info"):
        """Muestra una notificación toast temporal"""
        toast = tk.Toplevel(self.app)
        toast.wm_overrideredirect(True)
        toast.wm_geometry("+%d+%d" % (self.app.winfo_screenwidth() - 300, 50))
        
        # Configurar colores según el tipo
        if notification_type == "warning":
            bg_color = "#fef3c7"
            fg_color = "#92400e"
            border_color = "#f59e0b"
        elif notification_type == "error":
            bg_color = "#fee2e2"
            fg_color = "#991b1b"
            border_color = "#ef4444"
        else:  # info
            bg_color = self.bg_color
            fg_color = self.fg_color
            border_color = self.primary_color
        
        toast_frame = tk.Frame(
            toast,
            bg=bg_color,
            relief="solid",
            borderwidth=1,
            highlightbackground=border_color
        )
        toast_frame.pack(fill="both", expand=True, padx=5, pady=5)
        
        tk.Label(
            toast_frame,
            text=message,
            bg=bg_color,
            fg=fg_color,
            font=self.entry_font,
            wraplength=250
        ).pack(padx=10, pady=10)
        
        # Auto-cerrar después de 3 segundos
        toast.after(3000, toast.destroy)

    def get_notification_stats(self):
        """Obtiene estadísticas de notificaciones"""
        return {
            'total': self.notification_count,
            'low_stock': len([n for n in self.notifications if n['stock'] < 5]),
            'out_of_stock': len([n for n in self.notifications if n['stock'] == 0]),
            'notifications': self.notifications
        }