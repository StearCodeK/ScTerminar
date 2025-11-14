# models/settings_models.py
import psycopg2
from database import create_connection


class SettingsModel:
    def __init__(self):
        self.conn = create_connection()
        self.cursor = self.conn.cursor()

    def get_all_data(self, table_name):
        """Obtiene todos los datos de una tabla (incluyendo inactivos)"""
        try:
            if table_name == "solicitantes":
                query = """
                SELECT s.id_solicitante, s.cedula, s.nombre, d.nombre as departamento,
                    CASE WHEN s.activo THEN 'Sí' ELSE 'No' END as activo
                FROM solicitantes s
                LEFT JOIN departamentos d ON s.id_departamento = d.id_departamento
                """
            elif table_name == "productos":
                query = """
                SELECT p.id_producto, p.codigo, p.nombre, 
                    COALESCE(m.nombre, 'Sin marca') as marca, 
                    COALESCE(c.nombre, 'Sin categoría') as categoria, 
                    p.stock_minimo,
                    CASE WHEN p.activo THEN 'Sí' ELSE 'No' END as activo
                FROM productos p
                LEFT JOIN marcas m ON p.id_marca = m.id_marca AND m.activo = TRUE
                LEFT JOIN categorias c ON p.id_categoria = c.id_categoria AND c.activo = TRUE
                """
            elif table_name == "usuarios":
                query = "SELECT id, nombre_completo, email, usuario, rol, CASE WHEN activo THEN 'Sí' ELSE 'No' END as activo FROM usuarios"
            else:
                # Para tablas maestras simples, agregar columna activo si no existe
                try:
                    self.cursor.execute(f"SELECT column_name FROM information_schema.columns WHERE table_name='{table_name}' AND column_name='activo'")
                    has_activo = self.cursor.fetchone()
                    if has_activo:
                        query = f"SELECT *, CASE WHEN activo THEN 'Sí' ELSE 'No' END as activo FROM {table_name}"
                    else:
                        query = f"SELECT * FROM {table_name}"
                except:
                    query = f"SELECT * FROM {table_name}"

            self.cursor.execute(query)
            return self.cursor.fetchall()
        except Exception as e:
            raise Exception(f"Error al obtener datos: {str(e)}")

    def get_active_data(self, table_name):
        """Obtiene solo los datos activos para combobox"""
        try:
            if table_name == "solicitantes":
                query = """
                SELECT s.id_solicitante, s.cedula, s.nombre, d.nombre as departamento
                FROM solicitantes s
                LEFT JOIN departamentos d ON s.id_departamento = d.id_departamento
                WHERE s.activo = TRUE AND d.activo = TRUE
                """
            elif table_name == "productos":
                query = """
                SELECT p.id_producto, p.codigo, p.nombre, 
                    COALESCE(m.nombre, 'Sin marca') as marca, 
                    COALESCE(c.nombre, 'Sin categoría') as categoria
                FROM productos p
                LEFT JOIN marcas m ON p.id_marca = m.id_marca AND m.activo = TRUE
                LEFT JOIN categorias c ON p.id_categoria = c.id_categoria AND c.activo = TRUE
                WHERE p.activo = TRUE
                """
            elif table_name == "usuarios":
                query = "SELECT id, nombre_completo, email, usuario, rol FROM usuarios WHERE activo = TRUE"
            else:
                # Verificar si la tabla tiene columna activo
                try:
                    self.cursor.execute(f"SELECT column_name FROM information_schema.columns WHERE table_name='{table_name}' AND column_name='activo'")
                    has_activo = self.cursor.fetchone()
                    if has_activo:
                        query = f"SELECT * FROM {table_name} WHERE activo = TRUE"
                    else:
                        query = f"SELECT * FROM {table_name}"
                except:
                    query = f"SELECT * FROM {table_name}"

            self.cursor.execute(query)
            return self.cursor.fetchall()
        except Exception as e:
            raise Exception(f"Error al obtener datos activos: {str(e)}")

    def get_item_by_id(self, table_name, id_column, item_id):
        """Obtiene un item específico por ID"""
        try:
            query = f"SELECT * FROM {table_name} WHERE {id_column} = %s"
            self.cursor.execute(query, (item_id,))
            return self.cursor.fetchone()
        except Exception as e:
            raise Exception(f"Error al obtener item: {str(e)}")

    def get_related_options(self, table_name):
        """Obtiene opciones ACTIVAS para combobox de tablas relacionadas"""
        try:
            # Mapeo de nombres de tablas a columnas ID
            id_column_map = {
                'categoria': 'id_categoria',
                'marca': 'id_marca', 
                'departamento': 'id_departamento',
                'ubicacion': 'id_ubicacion',
                'proveedor': 'id_proveedor',
                'solicitante': 'id_solicitante'
            }
            
            # Determinar la columna ID
            if table_name in id_column_map:
                id_column = id_column_map[table_name]
            elif table_name.endswith('s'):
                id_column = f"id_{table_name[:-1]}"
            else:
                id_column = "id"

            # Verificar si la tabla tiene columna activo
            self.cursor.execute(f"""
                SELECT column_name 
                FROM information_schema.columns 
                WHERE table_name='{table_name}' AND column_name='activo'
            """)
            has_activo = self.cursor.fetchone()
            
            if has_activo:
                query = f"SELECT {id_column}, nombre FROM {table_name} WHERE activo = TRUE ORDER BY nombre"
            else:
                query = f"SELECT {id_column}, nombre FROM {table_name} ORDER BY nombre"
                
            self.cursor.execute(query)
            return self.cursor.fetchall()
        except Exception as e:
            raise Exception(f"Error al obtener opciones para {table_name}: {str(e)}")
        
    def insert_item(self, table_name, columns, values):
        """Inserta un nuevo item"""
        try:
            placeholders = ", ".join(["%s"] * len(values))
            columns_str = ", ".join(columns)
            query = f"INSERT INTO {table_name} ({columns_str}) VALUES ({placeholders})"
            self.cursor.execute(query, values)
            self.conn.commit()
            return True
        except psycopg2.Error as e:
            self.conn.rollback()
            raise Exception(f"No se pudo agregar el ítem: {str(e)}")

    def update_item(self, table_name, id_column, item_id, columns, values):
        """Actualiza un item existente"""
        try:
            set_clause = ", ".join([f"{col} = %s" for col in columns])
            query = f"UPDATE {table_name} SET {set_clause} WHERE {id_column} = %s"
            self.cursor.execute(query, values + [item_id])
            self.conn.commit()
            return True
        except psycopg2.Error as e:
            self.conn.rollback()
            raise Exception(f"No se pudo actualizar el ítem: {str(e)}")

    def soft_delete_item(self, table_name, id_column, item_id):
        """Marca un item como inactivo (eliminación lógica)"""
        try:
            # Verificar si la tabla tiene columna activo
            self.cursor.execute(f"SELECT column_name FROM information_schema.columns WHERE table_name='{table_name}' AND column_name='activo'")
            has_activo = self.cursor.fetchone()
            
            if has_activo:
                query = f"UPDATE {table_name} SET activo = FALSE WHERE {id_column} = %s"
                self.cursor.execute(query, (item_id,))
                self.conn.commit()
                return True
            else:
                # Si no tiene columna activo, no podemos hacer soft delete
                raise Exception("Esta tabla no soporta eliminación lógica. El registro está siendo usado en otras partes del sistema.")
                
        except psycopg2.Error as e:
            self.conn.rollback()
            raise Exception(f"No se pudo desactivar el ítem: {str(e)}")

    def activate_item(self, table_name, id_column, item_id):
        """Reactiva un item previamente desactivado"""
        try:
            # Verificar si la tabla tiene columna activo
            self.cursor.execute(f"SELECT column_name FROM information_schema.columns WHERE table_name='{table_name}' AND column_name='activo'")
            has_activo = self.cursor.fetchone()
            
            if has_activo:
                query = f"UPDATE {table_name} SET activo = TRUE WHERE {id_column} = %s"
                self.cursor.execute(query, (item_id,))
                self.conn.commit()
                return True
            else:
                return False
                
        except psycopg2.Error as e:
            self.conn.rollback()
            raise Exception(f"No se pudo activar el ítem: {str(e)}")

    def delete_item(self, table_name, id_column, item_id):
        """Elimina físicamente un item (solo si no tiene relaciones)"""
        try:
            query = f"DELETE FROM {table_name} WHERE {id_column} = %s"
            self.cursor.execute(query, (item_id,))
            self.conn.commit()
            return True
        except psycopg2.IntegrityError as e:
            self.conn.rollback()
            # Si hay error de integridad referencial, intentar soft delete
            try:
                return self.soft_delete_item(table_name, id_column, item_id)
            except Exception as soft_e:
                raise Exception(f"No se puede eliminar el ítem porque está siendo usado en otras partes del sistema: {str(soft_e)}")
        except psycopg2.Error as e:
            self.conn.rollback()
            raise Exception(f"No se pudo eliminar el ítem: {str(e)}")

    def close_connection(self):
        """Cierra la conexión a la base de datos"""
        if hasattr(self, 'cursor'):
            self.cursor.close()
        if hasattr(self, 'conn'):
            self.conn.close()