from database import create_connection


class SolicitudesModel:
    def __init__(self):
        self.conn = create_connection()
        self.cursor = self.conn.cursor()

    def obtener_departamentos(self):
        """Obtener todos los departamentos"""
        try:
            self.cursor.execute(
                "SELECT id_departamento, nombre FROM departamentos ORDER BY nombre")
            return self.cursor.fetchall()
        except Exception as e:
            print(f"Error al obtener departamentos: {e}")
            return []

    def obtener_solicitantes(self):
        """Obtener todos los solicitantes"""
        try:
            self.cursor.execute(
                "SELECT id_solicitante, nombre, cedula FROM solicitantes")
            return self.cursor.fetchall()
        except Exception as e:
            print(f"Error al obtener solicitantes: {e}")
            return []

    def obtener_categorias(self):
        """Obtener todas las categorías"""
        try:
            self.cursor.execute("SELECT id_categoria, nombre FROM categorias")
            return self.cursor.fetchall()
        except Exception as e:
            print(f"Error al obtener categorías: {e}")
            return []

    def obtener_categorias_en_inventario(self):
        """Obtener categorías solo de productos presentes en inventario y activos"""
        try:
            self.cursor.execute("""
                SELECT DISTINCT c.id_categoria, c.nombre
                FROM categorias c
                JOIN productos p ON p.id_categoria = c.id_categoria
                JOIN inventario i ON i.id_producto = p.id_producto
                WHERE p.activo = TRUE
                ORDER BY c.nombre
            """)
            return self.cursor.fetchall()
        except Exception as e:
            print(f"Error al obtener categorías de inventario: {e}")
            return []

    def obtener_productos_por_categoria_en_inventario(self, categoria_id):
        """Obtener productos por categoría solo si están en inventario y activos"""
        try:
            self.cursor.execute("""
                SELECT p.id_producto, p.nombre
                FROM productos p
                JOIN inventario i ON i.id_producto = p.id_producto
                WHERE p.id_categoria = %s AND p.activo = TRUE
                ORDER BY p.nombre
            """, (categoria_id,))
            return self.cursor.fetchall()
        except Exception as e:
            print(f"Error al obtener productos de inventario: {e}")
            return []

    def obtener_detalles_producto(self, producto_identificador):
        """Obtener detalles de un producto específico.
        Acepta tanto nombre como id (o cadenas que contengan el id)."""
        try:
            # Normalizar entrada
            # Si es int o string numérico -> buscar por id
            if isinstance(producto_identificador, int) or (isinstance(producto_identificador, str) and producto_identificador.isdigit()):
                product_id = int(producto_identificador)
                self.cursor.execute("""
                    SELECT 
                        p.id_producto,
                        COALESCE(i.stock, 0) AS stock,
                        COALESCE(u.nombre, 'N/A') AS ubicacion,
                        COALESCE(i.estado_stock, 'disponible') AS estado_stock
                    FROM productos p
                    LEFT JOIN inventario i ON p.id_producto = i.id_producto
                    LEFT JOIN ubicaciones u ON i.id_ubicacion = u.id_ubicacion
                    WHERE p.id_producto = %s
                """, (product_id,))
                return self.cursor.fetchone()

            # Si la cadena tiene un número (por ejemplo representación de tupla), intentar extraer id
            if isinstance(producto_identificador, str):
                import re
                m = re.search(r'\b(\d+)\b', producto_identificador)
                if m:
                    product_id = int(m.group(1))
                    self.cursor.execute("""
                        SELECT 
                            p.id_producto,
                            COALESCE(i.stock, 0) AS stock,
                            COALESCE(u.nombre, 'N/A') AS ubicacion,
                            COALESCE(i.estado_stock, 'disponible') AS estado_stock
                        FROM productos p
                        LEFT JOIN inventario i ON p.id_producto = i.id_producto
                        LEFT JOIN ubicaciones u ON i.id_ubicacion = u.id_ubicacion
                        WHERE p.id_producto = %s
                    """, (product_id,))
                    result = self.cursor.fetchone()
                    if result:
                        return result

                # Si no se obtuvo id, buscar por nombre (case-insensitive)
                nombre = producto_identificador.strip()
                self.cursor.execute("""
                    SELECT 
                        p.id_producto,
                        COALESCE(i.stock, 0) AS stock,
                        COALESCE(u.nombre, 'N/A') AS ubicacion,
                        COALESCE(i.estado_stock, 'disponible') AS estado_stock
                    FROM productos p
                    LEFT JOIN inventario i ON p.id_producto = i.id_producto
                    LEFT JOIN ubicaciones u ON i.id_ubicacion = u.id_ubicacion
                    WHERE p.nombre ILIKE %s
                    LIMIT 1
                """, (nombre,))
                return self.cursor.fetchone()

            return None
        except Exception as e:
            print(f"Error al obtener detalles del producto: {e}")
            return None

    def obtener_solicitudes(self, filtros=None):
        """Obtener solicitudes con filtros opcionales"""
        try:
            query = """
            SELECT 
                ROW_NUMBER() OVER (ORDER BY s.fecha_solicitud DESC) as nro,
                TO_CHAR(s.fecha_solicitud, 'DD/MM/YYYY HH24:MI') as fecha,
                d.nombre AS departamento,
                sol.nombre AS solicitante,
                s.comentario AS referencia,
                u.nombre_completo AS responsable_entrega,
                s.id_solicitud
            FROM solicitudes s
            JOIN departamentos d ON s.id_departamento = d.id_departamento
            JOIN solicitantes sol ON s.id_solicitante = sol.id_solicitante
            JOIN usuarios u ON s.id_responsable_entrega = u.id
            WHERE 1=1
            """

            params = []

            if filtros:
                if filtros.get('search_text'):
                    query += " AND s.comentario ILIKE %s"
                    params.append(f"%{filtros['search_text']}%")

                if filtros.get('dept_filter'):
                    query += " AND d.nombre = %s"
                    params.append(filtros['dept_filter'])

                if filtros.get('date_from'):
                    query += " AND s.fecha_solicitud >= %s"
                    params.append(filtros['date_from'])

                if filtros.get('date_to'):
                    query += " AND s.fecha_solicitud <= %s"
                    params.append(filtros['date_to'])

            query += " ORDER BY s.fecha_solicitud DESC LIMIT 100"

            self.cursor.execute(query, params)
            return self.cursor.fetchall()
        except Exception as e:
            print(f"Error al obtener solicitudes: {e}")
            return []

    def registrar_solicitud(self, datos_solicitud):
        """Registrar una nueva solicitud"""
        try:
            self.cursor.execute("""
                INSERT INTO solicitudes 
                (id_departamento, id_solicitante, id_responsable_entrega, comentario)
                VALUES (%s, %s, %s, %s)
                RETURNING id_solicitud
            """, datos_solicitud)
            return self.cursor.fetchone()[0]
        except Exception as e:
            print(f"Error al registrar solicitud: {e}")
            self.conn.rollback()
            return None

    def registrar_detalle_solicitud(self, detalle_data):
        """Registrar detalle de solicitud"""
        try:
            self.cursor.execute("""
                INSERT INTO detalle_solicitud 
                (id_solicitud, id_producto, cantidad)
                VALUES (%s, %s, %s)
            """, detalle_data)
        except Exception as e:
            print(f"Error al registrar detalle de solicitud: {e}")
            self.conn.rollback()

    def actualizar_inventario(self, producto_id, cantidad):
        """Actualizar inventario después de una salida"""
        try:
            self.cursor.execute("""
                UPDATE inventario 
                SET stock = stock - %s
                WHERE id_producto = %s
            """, (cantidad, producto_id))
        except Exception as e:
            print(f"Error al actualizar inventario: {e}")
            self.conn.rollback()

    def obtener_detalles_solicitud(self, solicitud_id):
        """Obtener detalles completos de una solicitud"""
        try:
            self.cursor.execute("""
                SELECT 
                    s.id_solicitud,
                    s.fecha_solicitud,
                    s.comentario,
                    d.nombre AS departamento,
                    sol.nombre AS solicitante,
                    sol.cedula,
                    u.nombre_completo AS responsable_entrega
                FROM solicitudes s
                JOIN departamentos d ON s.id_departamento = d.id_departamento
                JOIN solicitantes sol ON s.id_solicitante = sol.id_solicitante
                JOIN usuarios u ON s.id_responsable_entrega = u.id
                WHERE s.id_solicitud = %s
            """, (solicitud_id,))
            return self.cursor.fetchone()
        except Exception as e:
            print(f"Error al obtener detalles de solicitud: {e}")
            return None

    def obtener_productos_solicitud(self, solicitud_id):
        """Obtener productos de una solicitud"""
        try:
            self.cursor.execute("""
                SELECT 
                    p.nombre,
                    ds.cantidad,
                    p.codigo
                FROM detalle_solicitud ds
                JOIN productos p ON ds.id_producto = p.id_producto
                WHERE ds.id_solicitud = %s
            """, (solicitud_id,))
            return self.cursor.fetchall()
        except Exception as e:
            print(f"Error al obtener productos de solicitud: {e}")
            return []

    def agregar_departamento(self, nombre):
        """Agregar nuevo departamento"""
        try:
            self.cursor.execute(
                "INSERT INTO departamentos (nombre) VALUES (%s) RETURNING id_departamento, nombre",
                (nombre,)
            )
            self.conn.commit()
            return self.cursor.fetchone()
        except Exception as e:
            print(f"Error al agregar departamento: {e}")
            self.conn.rollback()
            return None

    def agregar_solicitante(self, cedula, nombre, id_departamento):
        """Agregar nuevo solicitante"""
        try:
            self.cursor.execute(
                """INSERT INTO solicitantes 
                (cedula, nombre, id_departamento) 
                VALUES (%s, %s, %s) 
                RETURNING id_solicitante, nombre""",
                (cedula, nombre, id_departamento)
            )
            self.conn.commit()
            return self.cursor.fetchone()
        except Exception as e:
            print(f"Error al agregar solicitante: {e}")
            self.conn.rollback()
            return None

    def commit(self):
        """Confirmar transacción"""
        self.conn.commit()

    def rollback(self):
        """Revertir transacción"""
        self.conn.rollback()

    def close(self):
        """Cerrar conexión"""
        self.cursor.close()
        self.conn.close()
