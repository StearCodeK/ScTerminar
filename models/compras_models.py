from datetime import datetime
from database import create_connection


class PurchaseModel:
    def __init__(self):
        self.conn = create_connection()
        self.cursor = self.conn.cursor()

    def get_all_requests(self, status_filter="Todos", priority_filter="Todos"):
        """Obtiene todas las solicitudes con filtros opcionales"""
        query = """
            SELECT
                ROW_NUMBER() OVER (ORDER BY fecha DESC) as nro,
                producto, cantidad, motivo, prioridad,
                COALESCE(proveedor, 'N/A'),
                TO_CHAR(fecha, 'DD/MM/YYYY HH24:MI'),
                estado
            FROM solicitudes_compra
        """

        where_clauses = []
        params = []

        if status_filter != "Todos":
            where_clauses.append("estado = %s")
            params.append(status_filter)

        if priority_filter != "Todos":
            where_clauses.append("prioridad = %s")
            params.append(priority_filter)

        if where_clauses:
            query += " WHERE " + " AND ".join(where_clauses)

        query += """
            ORDER BY
                CASE prioridad
                    WHEN 'Alta' THEN 1
                    WHEN 'Media' THEN 2
                    WHEN 'Baja' THEN 3
                END,
                fecha DESC
        """

        self.cursor.execute(query, params)
        return self.cursor.fetchall()

    def create_request(self, data):
        """Crea una nueva solicitud de compra"""
        self.cursor.execute("""
            INSERT INTO solicitudes_compra (
                producto, cantidad, motivo, prioridad, proveedor, fecha, estado
            ) VALUES (%s, %s, %s, %s, %s, %s, %s)
        """, data)
        self.conn.commit()

    def update_request_status(self, request_id, new_status):
        """Actualiza el estado de una solicitud"""
        self.cursor.execute("""
            UPDATE solicitudes_compra 
            SET estado = %s 
            WHERE id = %s
        """, (new_status, request_id))
        self.conn.commit()

    def delete_request(self, request_id):
        """Elimina una solicitud"""
        self.cursor.execute(
            "DELETE FROM solicitudes_compra WHERE id = %s", (request_id,))
        self.conn.commit()

    def get_categories(self):
        """Obtiene todas las categorías"""
        self.cursor.execute("SELECT nombre FROM categorias ORDER BY nombre")
        return [row[0] for row in self.cursor.fetchall()]

    def get_products_by_category(self, category_name):
        """Obtiene productos por categoría"""
        if not category_name or category_name == "Todas":
            self.cursor.execute(
                "SELECT id_producto, nombre FROM productos ORDER BY nombre")
        else:
            self.cursor.execute("""
                SELECT p.id_producto, p.nombre
                FROM productos p
                JOIN categorias c ON p.id_categoria = c.id_categoria
                WHERE c.nombre = %s
                ORDER BY p.nombre
            """, (category_name,))
        return self.cursor.fetchall()

    def get_suppliers(self):
        """Obtiene todos los proveedores"""
        self.cursor.execute(
            "SELECT nombre FROM proveedores WHERE nombre IS NOT NULL ORDER BY nombre")
        return [row[0] for row in self.cursor.fetchall()]

    def get_active_products(self):
        """Obtiene productos activos"""
        self.cursor.execute("""
            SELECT p.id_producto, p.nombre
            FROM productos p
            WHERE p.activo = TRUE
            ORDER BY p.nombre
        """)
        return self.cursor.fetchall()
