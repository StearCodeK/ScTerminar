from database import create_connection


class SupplierModel:
    def __init__(self):
        self.conn = create_connection()
        self.cursor = self.conn.cursor()

    def get_all_suppliers(self, category_filter="Todas", rating_filter="Todas", price_filter="Todos"):
        """Obtiene todos los proveedores con filtros opcionales"""
        query = """
            SELECT
                ROW_NUMBER() OVER (ORDER BY p.nombre) as nro,
                p.nombre,
                COALESCE(p.contacto, 'N/A'),
                COALESCE(p.telefono, 'N/A'),
                COALESCE(p.email, 'N/A'),
                CASE
                    WHEN p.valoracion IS NULL THEN 'Sin valoración'
                    WHEN p.valoracion = 1 THEN '1 Estrella'
                    ELSE p.valoracion || ' Estrellas'
                END as valoracion_texto,
                COALESCE(p.manejo_precios, 'N/A'),
                COALESCE(
                    (SELECT STRING_AGG(DISTINCT c.nombre, ', ')
                     FROM (
                         SELECT c.nombre
                         FROM proveedor_categoria pc
                         JOIN categorias c ON pc.id_categoria = c.id_categoria
                         WHERE pc.id_proveedor = p.id_proveedor
                         UNION
                         SELECT DISTINCT c.nombre
                         FROM proveedor_producto pp
                         JOIN productos pr ON pp.id_producto = pr.id_producto
                         JOIN categorias c ON pr.id_categoria = c.id_categoria
                         WHERE pp.id_proveedor = p.id_proveedor
                     ) c
                    ), 'N/A'
                ) as categorias
            FROM proveedores p
        """

        where_clauses = []
        params = []

        if category_filter != "Todas":
            where_clauses.append("""
                EXISTS (
                    SELECT 1 FROM proveedor_categoria pc
                    JOIN categorias c ON pc.id_categoria = c.id_categoria
                    WHERE pc.id_proveedor = p.id_proveedor AND c.nombre = %s
                    UNION
                    SELECT 1 FROM proveedor_producto pp
                    JOIN productos pr ON pp.id_producto = pr.id_producto
                    JOIN categorias c ON pr.id_categoria = c.id_categoria
                    WHERE pp.id_proveedor = p.id_proveedor AND c.nombre = %s
                )
            """)
            params.extend([category_filter, category_filter])

        if rating_filter != "Todas":
            rating_value = int(rating_filter.split()[0])
            where_clauses.append("p.valoracion = %s")
            params.append(rating_value)

        if price_filter != "Todos":
            where_clauses.append("p.manejo_precios = %s")
            params.append(price_filter)

        if where_clauses:
            query += " WHERE " + " AND ".join(where_clauses)

        query += " ORDER BY p.nombre"
        self.cursor.execute(query, params)
        return self.cursor.fetchall()

    def get_supplier_by_name(self, supplier_name):
        """Obtiene un proveedor por nombre"""
        self.cursor.execute("""
            SELECT id_proveedor, nombre, contacto, telefono, email, direccion,
                   redes_sociales, valoracion, manejo_precios, comentarios
            FROM proveedores WHERE nombre = %s
        """, (supplier_name,))
        return self.cursor.fetchone()

    def get_supplier_by_id(self, supplier_id):
        """Obtiene un proveedor por ID"""
        self.cursor.execute("""
            SELECT nombre, contacto, telefono, email, direccion,
                   redes_sociales, valoracion, manejo_precios, comentarios
            FROM proveedores WHERE id_proveedor = %s
        """, (supplier_id,))
        return self.cursor.fetchone()

    def create_supplier(self, data):
        """Crea un nuevo proveedor"""
        self.cursor.execute("""
            INSERT INTO proveedores (
                nombre, contacto, telefono, email, direccion,
                redes_sociales, valoracion, manejo_precios, comentarios
            ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
            RETURNING id_proveedor
        """, data)
        new_id = self.cursor.fetchone()[0]
        self.conn.commit()
        return new_id

    def update_supplier(self, supplier_id, data):
        """Actualiza un proveedor existente"""
        self.cursor.execute("""
            UPDATE proveedores SET
                nombre = %s, contacto = %s, telefono = %s, email = %s,
                direccion = %s, redes_sociales = %s, valoracion = %s,
                manejo_precios = %s, comentarios = %s
            WHERE id_proveedor = %s
        """, data + (supplier_id,))
        self.conn.commit()

    def delete_supplier(self, supplier_name):
        """Elimina un proveedor"""
        self.cursor.execute(
            "DELETE FROM proveedores WHERE nombre = %s", (supplier_name,))
        self.conn.commit()

    def get_supplier_categories(self, supplier_id):
        """Obtiene las categorías de un proveedor"""
        self.cursor.execute("""
            SELECT DISTINCT c.nombre
            FROM (
                SELECT id_categoria FROM proveedor_categoria WHERE id_proveedor = %s
                UNION
                SELECT p.id_categoria FROM proveedor_producto pp
                JOIN productos p ON pp.id_producto = p.id_producto
                WHERE pp.id_proveedor = %s
            ) AS cat_ids
            JOIN categorias c ON cat_ids.id_categoria = c.id_categoria
        """, (supplier_id, supplier_id))
        return [row[0] for row in self.cursor.fetchall()] or ["Ninguna"]

    def get_supplier_products(self, supplier_id):
        """Obtiene los productos de un proveedor"""
        self.cursor.execute("""
            SELECT p.nombre, c.nombre as categoria
            FROM proveedor_producto pp
            JOIN productos p ON pp.id_producto = p.id_producto
            JOIN categorias c ON p.id_categoria = c.id_categoria
            WHERE pp.id_proveedor = %s
            ORDER BY p.nombre
        """, (supplier_id,))
        return self.cursor.fetchall()

    def get_available_products(self, supplier_id):
        """Obtiene productos disponibles para agregar al proveedor"""
        self.cursor.execute("""
            SELECT p.id_producto, p.nombre, c.nombre
            FROM productos p
            JOIN categorias c ON p.id_categoria = c.id_categoria
            WHERE p.activo = TRUE
            AND p.id_producto NOT IN (
                SELECT id_producto FROM proveedor_producto
                WHERE id_proveedor = %s
            )
            ORDER BY p.nombre
        """, (supplier_id,))
        return self.cursor.fetchall()

    def add_product_to_supplier(self, supplier_id, product_id):
        """Agrega un producto al proveedor"""
        self.cursor.execute("""
            INSERT INTO proveedor_producto (id_proveedor, id_producto)
            VALUES (%s, %s)
        """, (supplier_id, product_id))
        self.conn.commit()

    def remove_product_from_supplier(self, supplier_id, product_id):
        """Elimina un producto del proveedor"""
        self.cursor.execute("""
            DELETE FROM proveedor_producto
            WHERE id_proveedor = %s AND id_producto = %s
        """, (supplier_id, product_id))
        self.conn.commit()

    def get_categories(self):
        """Obtiene todas las categorías"""
        self.cursor.execute("SELECT nombre FROM categorias ORDER BY nombre")
        return [row[0] for row in self.cursor.fetchall()]

    def get_product_id_by_name(self, product_name):
        """Obtiene el ID de un producto por nombre"""
        self.cursor.execute(
            "SELECT id_producto FROM productos WHERE nombre = %s", (product_name,))
        result = self.cursor.fetchone()
        return result[0] if result else None

    def set_supplier_category(self, supplier_id, category_name):
        """Asigna (o reemplaza) la categoría principal de un proveedor.

        El método elimina las asociaciones previas en `proveedor_categoria`
        y, si `category_name` es válido, inserta la nueva asociación.
        """
        # Normalizar valores vacíos o placeholders
        if not category_name or category_name in ("N/A", "Todas"):
            # Si no hay categoría válida, solo eliminar asociaciones previas
            self.cursor.execute(
                "DELETE FROM proveedor_categoria WHERE id_proveedor = %s", (supplier_id,))
            # En modo autocommit la operación ya estará aplicada
            return

        # Buscar id_categoria por nombre
        self.cursor.execute(
            "SELECT id_categoria FROM categorias WHERE nombre = %s", (category_name,))
        res = self.cursor.fetchone()
        if not res:
            # No existe la categoría; no hacemos nada
            return

        id_categoria = res[0]

        # Reemplazar asociaciones previas por la nueva
        self.cursor.execute(
            "DELETE FROM proveedor_categoria WHERE id_proveedor = %s", (supplier_id,))

        # Evitar duplicados
        self.cursor.execute(
            "SELECT 1 FROM proveedor_categoria WHERE id_proveedor = %s AND id_categoria = %s",
            (supplier_id, id_categoria)
        )
        if not self.cursor.fetchone():
            self.cursor.execute(
                "INSERT INTO proveedor_categoria (id_proveedor, id_categoria) VALUES (%s, %s)",
                (supplier_id, id_categoria)
            )
