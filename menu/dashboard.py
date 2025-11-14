from tkinter import ttk
import tkinter as tk
from helpers import clear_frame
from database import create_connection
from datetime import datetime
from views.base_view import BaseView

# Conexión a PostgreSQL
conn = create_connection()
cursor = conn.cursor()


class DashboardView(BaseView):
    def __init__(self, frame, app):
        super().__init__(frame, app)
        self.setup_styles()

    def show_dashboard(self):
        """Muestra el panel de control principal con datos actualizados"""
        clear_frame(self.frame)

        # Encabezado con usuario y fecha
        header_frame = self.create_main_container(self.frame)
        header_frame.pack(fill="x", pady=(0, 10))

        # Saludo a la izquierda
        usuario = self.obtener_nombre_usuario(self.app.current_user)
        tk.Label(header_frame, text=f"Bienvenido {usuario}",
                 font=self.app.title_font, bg=self.bg_color, fg=self.fg_color, 
                 anchor="w").pack(side="left", padx=10)

        # Fecha a la derecha
        fecha_actual = datetime.now().strftime("%d/%m/%Y")
        tk.Label(header_frame, text=fecha_actual,
                 font=self.app.menu_font, bg=self.bg_color, fg=self.fg_color, 
                 anchor="e").pack(side="right", padx=10)

        # Tarjetas resumen con datos reales
        cards_frame = self.create_main_container(self.frame)
        cards_frame.pack(fill="x", pady=10)

        # Obtener datos para las tarjetas
        card_data = get_dashboard_card_data()

        cards = [
            ("Productos", card_data["total_productos"], self.primary_color),
            ("Stock bajo", card_data["stock_bajo"], "#ef4444"),
            ("Solicitudes", card_data["solicitudes_hoy"], self.app.colors.get("secondary", "#f59e0b")),
            ("Compras", card_data["compras_hoy"], "#f59e0b")
        ]

        for i, (title, value, color) in enumerate(cards):
            card = self._create_card(cards_frame, title, value, color)
            card.grid(row=0, column=i, padx=10, sticky="nsew")
            cards_frame.grid_columnconfigure(i, weight=1)

        # Gráficos y contenido adicional con datos reales
        self._create_dashboard_content()

    def _create_card(self, parent, title, value, color):
        """Crea una tarjeta de estadística"""
        card = tk.Frame(parent, bg="white", bd=0, highlightthickness=0,
                        highlightbackground="#e5e7eb", relief="solid", 
                        padx=20, pady=15)
        
        tk.Label(card, text=title, bg="white", fg=self.app.colors.get("text_light", "#6b7280"),
                 font=self.app.menu_font).pack(anchor="w")
        tk.Label(card, text=str(value), bg="white", fg=color,
                 font=("Segoe UI", 24, "bold")).pack(anchor="w", pady=(5, 0))
        
        return card

    def _create_dashboard_content(self):
        """Crea el contenido adicional del dashboard con datos reales"""
        content_row = self.create_main_container(self.frame)
        content_row.pack(fill="both", expand=True, pady=10)

        # Gráfico izquierdo - Movimientos recientes
        chart_frame = self._create_content_card(content_row)
        chart_frame.pack(side="left", fill="both", expand=True, padx=(0, 10))

        tk.Label(chart_frame, text="Movimientos Recientes",
                 font=self.app.subtitle_font, bg="white", fg=self.fg_color).pack(anchor="w", padx=20, pady=15)

        # Obtener últimos movimientos
        movimientos = get_recent_movements()

        # Crear un frame para mostrar los movimientos como lista
        movimientos_frame = tk.Frame(chart_frame, bg="white")
        movimientos_frame.pack(fill="both", expand=True, padx=20, pady=(0, 20))

        # Mostrar solo los 5 más recientes
        for i, mov in enumerate(movimientos[:5]):
            tk.Label(movimientos_frame,
                     text=f"{mov['fecha']} - {mov['tipo']} - {mov['producto']} ({mov['cantidad']})",
                     bg="white", fg=self.fg_color, font=self.entry_font, anchor="w").pack(fill="x", pady=2)

        # Tabla derecha - Productos con stock bajo (datos reales)
        table_frame = self._create_content_card(content_row)
        table_frame.pack(side="right", fill="both", expand=True)

        tk.Label(table_frame, text="Productos con Stock Bajo",
                 font=self.app.subtitle_font, bg="white", fg=self.fg_color).pack(anchor="w", padx=20, pady=15)

        columns = ("Producto", "Stock", "Mínimo", "Diferencia")
        column_widths = [150, 80, 80, 80]
        
        table_container, tree = self.create_table(table_frame, columns, column_widths, height=8)
        table_container.pack(fill="both", expand=True, padx=20, pady=(0, 20))

        # Obtener productos con stock bajo
        low_stock_products = get_low_stock_products()

        for product in low_stock_products:
            diferencia = product['stock_minimo'] - product['stock_actual'] if product['stock_actual'] < product['stock_minimo'] else 0
            tree.insert("", "end", values=(
                product['nombre'],
                product['stock_actual'],
                product['stock_minimo'],
                diferencia
            ))

    def _create_content_card(self, parent):
        """Crea una tarjeta de contenido para gráficos/tablas"""
        return tk.Frame(parent, bg="white", bd=0, highlightthickness=0,
                       highlightbackground="#e5e7eb", relief="solid")


# Funciones de datos (mantenidas para compatibilidad)
def get_dashboard_card_data():
    """Obtiene los datos para las tarjetas del dashboard"""
    data = {
        "total_productos": 0,
        "stock_bajo": 0,
        "solicitudes_hoy": 0,
        "compras_hoy": 0
    }

    today = datetime.now().date()

    try:
        # Total de productos activos en inventario
        cursor.execute("""
            SELECT COUNT(DISTINCT p.id_producto) 
            FROM productos p
            JOIN inventario i ON p.id_producto = i.id_producto
            WHERE p.activo = TRUE
        """)
        data["total_productos"] = cursor.fetchone()[0]

        # Total de productos con stock bajo (sin repetir)
        cursor.execute("""
            SELECT COUNT(DISTINCT p.id_producto)
            FROM productos p
            JOIN inventario i ON p.id_producto = i.id_producto
            WHERE p.activo = TRUE
            AND i.stock <= COALESCE(p.stock_minimo, 0)
            AND i.stock > 0
        """)
        data["stock_bajo"] = cursor.fetchone()[0]

        # Solicitudes realizadas hoy
        cursor.execute("""
            SELECT COUNT(*) 
            FROM solicitudes 
            WHERE DATE(fecha_solicitud) = %s
        """, (today,))
        data["solicitudes_hoy"] = cursor.fetchone()[0]

        # Compras pendientes
        cursor.execute("""
            SELECT COUNT(*) 
            FROM solicitudes_compra 
            WHERE estado = 'Pendiente'
        """)
        data["compras_hoy"] = cursor.fetchone()[0]

    except Exception as e:
        print(f"Error al obtener datos del dashboard: {e}")
        conn.rollback()

    return data


def get_recent_movements():
    """Obtiene los últimos movimientos de inventario"""
    try:
        cursor.execute("""
            SELECT 
                m.tipo,
                p.nombre as producto,
                m.cantidad,
                TO_CHAR(m.fecha, 'DD/MM/YYYY HH24:MI') as fecha
            FROM movimientos m
            JOIN productos p ON m.id_producto = p.id_producto
            ORDER BY m.fecha DESC
            LIMIT 10
        """)

        movimientos = []
        for row in cursor.fetchall():
            movimientos.append({
                "tipo": row[0],
                "producto": row[1],
                "cantidad": row[2],
                "fecha": row[3]
            })

        return movimientos

    except Exception as e:
        print(f"Error al obtener movimientos recientes: {e}")
        conn.rollback()
        return []


def get_low_stock_products():
    """Obtiene productos con stock bajo según el stock mínimo configurado por producto"""
    try:
        cursor.execute("""
            SELECT 
                p.nombre,
                i.stock as stock_actual,
                COALESCE(p.stock_minimo, 0) as stock_minimo
            FROM productos p
            JOIN inventario i ON p.id_producto = i.id_producto
            WHERE p.activo = TRUE
              AND i.stock <= COALESCE(p.stock_minimo, 0)
            ORDER BY i.stock ASC
            LIMIT 10
        """)

        productos = []
        for row in cursor.fetchall():
            productos.append({
                "nombre": row[0],
                "stock_actual": row[1],
                "stock_minimo": row[2]
            })

        return productos

    except Exception as e:
        print(f"Error al obtener productos con stock bajo: {e}")
        conn.rollback()
        return []


# Función de compatibilidad para la app existente
def show_dashboard(app):
    """Función de compatibilidad para mostrar el dashboard"""
    dashboard_view = DashboardView(app.content_frame, app)
    dashboard_view.show_dashboard()
    return dashboard_view