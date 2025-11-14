import tkinter as tk
from tkinter import messagebox
from models.product_model import ProductModel
from views.product_view import ProductView
from controllers.movimientos_controllers import MovementController
from models.export_manager import ExportManager


class ProductController:
    def clear_filters(self):
        """Restablece los filtros de la vista y refresca la tabla de productos"""
        if hasattr(self.view, 'clear_filters'):
            self.view.clear_filters()

    def __init__(self, app):
        self.app = app
        self.model = ProductModel()
        self.view = ProductView(frame=None, app=app)
        self.view.set_controller(self)  # Conectar vista con controlador

    def show_inventory(self):
        """Mostrar gestión de inventario"""
        from helpers import clear_frame
        clear_frame(self.app.content_frame)

        title_frame = tk.Frame(self.app.content_frame,
                               bg=self.app.colors["background"])
        title_frame.pack(fill="x", pady=(5, 5))

        tk.Label(title_frame, text="Gestión de Inventario",
                 font=self.app.title_font, bg=self.app.colors["background"]).pack(side="left")

        # Mostrar inventario en un único frame (sin pestañas)
        inventory_frame = tk.Frame(
            self.app.content_frame, bg=self.app.colors["background"])
        inventory_frame.pack(fill="both", expand=True, padx=0, pady=0)

        self.setup_inventory_tab(inventory_frame)

    def setup_inventory_tab(self, frame):
        """Configurar pestaña de inventario"""
        self.view.frame = frame
        self.view.setup_styles()
        self.view.setup_inventory_tab(frame)

        # Cargar datos iniciales
        self.refresh_table()

        # Actualizar combobox de categorías
        categorias = self.model.get_combobox_data("categorias")
        self.view.update_categories_combo(categorias)
        marcas = self.model.get_combobox_data("marcas")
        self.view.update_marcas_combo(marcas)

        # ✅ CONFIGURAR AUTocompletado PARA EL COMBOBOX DE ESTADO
        self.view.estado_combo.set_completion_list(
            ["Todos", "Disponible", "Stock bajo", "Agotado"])

    def refresh_table(self):
        """Refrescar tabla de productos"""
        try:
            inventario_data = self.model.update_product_stock_status()
            formatted_data = self._format_table_data(inventario_data)
            self.view.refresh_table(formatted_data)

            if hasattr(self.app, 'notification_manager'):
                self.app.notification_manager.check_low_stock()

        except Exception as e:
            messagebox.showerror("Error", f"Error al cargar datos: {e}")

    def _format_table_data(self, inventario_data):
        """Formatear datos para la tabla"""
        formatted_data = []
        for item in inventario_data:
            formatted_data.append((
                item[0],  # Nro (id_producto)
                item[2],  # Producto
                item[3] if item[3] else "N/A",  # Marca
                item[4] if item[4] else "N/A",  # Categoría
                item[1],  # Código
                item[5] if item[5] else 0,      # Stock
                item[8] if item[8] is not None else 0,  # Stock (m)
                item[6] if item[6] else "N/A",  # Ubicación
                item[7] if item[7] else "disponible"  # Estado
            ))
        return formatted_data

    def search_products(self):
        """Buscar productos"""
        try:
            search_term = self.view.get_search_term()
            filters = self.view.get_filters()

            extra = " AND (p.nombre ILIKE %s OR p.codigo ILIKE %s)"
            params = [f"%{search_term}%", f"%{search_term}%"]

            if filters['categoria'] != "Todas":
                extra += " AND c.nombre = %s"
                params.append(filters['categoria'])

            if filters['estado'] != "Todos":
                extra += " AND i.estado_stock = %s"
                params.append(filters['estado'].lower(
                ) if filters['estado'] != "Stock bajo" else "stock bajo")

            inventario_data = self.model.get_products(extra, tuple(params))
            formatted_data = self._format_table_data(inventario_data)
            self.view.refresh_table(formatted_data)

        except Exception as e:
            messagebox.showerror("Error", f"Error al buscar productos: {e}")

    def apply_filters(self):
        """Aplicar filtros a la tabla"""
        try:
            filters = self.view.get_filters()

            extra = ""
            params = []

            if filters['categoria'] != "Todas":
                extra += " AND c.nombre = %s"
                params.append(filters['categoria'])

            if filters['estado'] != "Todos":
                extra += " AND i.estado_stock = %s"
                params.append(filters['estado'].lower(
                ) if filters['estado'] != "Stock bajo" else "stock bajo")

            inventario_data = self.model.get_products(extra, tuple(params))
            formatted_data = self._format_table_data(inventario_data)
            self.view.refresh_table(formatted_data)

        except Exception as e:
            messagebox.showerror("Error", f"Error al aplicar filtros: {e}")

    def new_product(self):
        """Crear nuevo producto"""
        self.show_product_form()

    def show_product_form(self, product_id=None, select_nuevo=None):
        """Mostrar formulario de producto"""
        try:
            marcas = self.model.get_combobox_data("marcas")
            categorias = self.model.get_combobox_data("categorias")
            ubicaciones = self.model.get_combobox_data("ubicaciones")

            form_window, entries, buttons, save_btn = self.view.show_product_form(
                product_id)

            # ✅ CONFIGURAR AUTocompletado usando set_completion_list
            entries["Marca:"].set_completion_list([m[1] for m in marcas])
            entries["Categoría:"].set_completion_list(
                [c[1] for c in categorias])
            entries["Ubicación:"].set_completion_list(
                [u[1] for u in ubicaciones])
            entries["Estado:"].set_completion_list(
                ["disponible", "stock bajo", "agotado", "reservado"])

            self._formulario_activo = {
                'window': form_window,
                'entries': entries,
                'product_id': product_id
            }

            # ✅ MODIFICADO: Pasar form_window como parámetro para mantenerla abierta
            for label, btn in buttons.items():
                tabla = {"Marca:": "marcas", "Categoría:": "categorias",
                         "Ubicación:": "ubicaciones"}[label]
                btn.configure(command=lambda t=tabla,
                              pw=form_window: self.add_new_value(t, pw))

            save_btn.configure(command=lambda: self.save_product(
                entries, product_id, marcas, categorias, ubicaciones, form_window))

            def on_close():
                if hasattr(self, '_formulario_activo'):
                    del self._formulario_activo
                form_window.destroy()
            form_window.protocol("WM_DELETE_WINDOW", on_close)

            if product_id:
                self.load_product_data(
                    product_id, entries, marcas, categorias, ubicaciones)

            # Seleccionar automáticamente el nuevo valor si corresponde
            if select_nuevo:
                if 'marcas' in select_nuevo and "Marca:" in entries:
                    entries["Marca:"].set(select_nuevo['marcas'])
                if 'categorias' in select_nuevo and "Categoría:" in entries:
                    entries["Categoría:"].set(select_nuevo['categorias'])
                if 'ubicaciones' in select_nuevo and "Ubicación:" in entries:
                    entries["Ubicación:"].set(select_nuevo['ubicaciones'])

        except Exception as e:
            messagebox.showerror("Error", f"Error al cargar formulario: {e}")

    def load_product_data(self, product_id, entries, marcas, categorias, ubicaciones):
        """Cargar datos de producto en formulario"""
        try:
            producto_data = self.model.get_product_data(product_id)
            if not producto_data:
                raise Exception("Producto no encontrado")

            entries["Código:"].insert(0, producto_data[1])
            entries["Producto:"].insert(0, producto_data[2])

            if producto_data[3]:  # ID marca
                marca_nombre = next(
                    (m[1] for m in marcas if m[0] == producto_data[3]), "")
                entries["Marca:"].set(marca_nombre)

            if producto_data[4]:  # ID categoría
                categoria_nombre = next(
                    (c[1] for c in categorias if c[0] == producto_data[4]), "")
                entries["Categoría:"].set(categoria_nombre)

            if producto_data[5] is not None:  # Stock
                entries["Stock inicial:"].insert(0, producto_data[5])
                # 🔒 BLOQUEAR EL CAMPO DE STOCK EN EDICIÓN
                entries["Stock inicial:"].config(state="disabled")

            # NUEVO: Cargar stock mínimo
            if producto_data[8] is not None:  # Stock mínimo (índice 8)
                entries["Stock mínimo:"].insert(0, producto_data[8])

            if producto_data[7]:  # Estado
                entries["Estado:"].set(producto_data[7])

            if producto_data[6]:  # ID ubicación
                ubicacion_nombre = next(
                    (u[1] for u in ubicaciones if u[0] == producto_data[6]), "")
                entries["Ubicación:"].set(ubicacion_nombre)

        except Exception as e:
            messagebox.showerror("Error", f"Error al cargar datos: {str(e)}")

    def save_product(self, entries, product_id, marcas, categorias, ubicaciones, window):
        """Guardar producto"""
        try:
            # Obtener valores del formulario
            codigo = entries["Código:"].get().strip()
            producto = entries["Producto:"].get().strip()
            marca_nombre = entries["Marca:"].get()
            categoria_nombre = entries["Categoría:"].get()
            ubicacion_nombre = entries["Ubicación:"].get()
            estado = entries["Estado:"].get()
            
            # NUEVO: Obtener stock mínimo
            stock_minimo_txt = entries["Stock mínimo:"].get().strip()
            stock_minimo = 0  # Valor por defecto
            if stock_minimo_txt:
                if not stock_minimo_txt.isdigit() or int(stock_minimo_txt) < 0:
                    messagebox.showerror("Error", "El stock mínimo debe ser un número entero positivo o cero.")
                    return
                stock_minimo = int(stock_minimo_txt)

            # 🔒 OBTENER STOCK DEPENDIENDO SI ES EDICIÓN O NUEVO
            if product_id:
                # En edición, obtener el stock actual de la base de datos
                producto_data = self.model.get_product_data(product_id)
                stock = producto_data[5] if producto_data and producto_data[5] is not None else 0
            else:
                # En nuevo producto, obtener del formulario
                stock_txt = entries["Stock inicial:"].get().strip()
                if not stock_txt:
                    messagebox.showwarning(
                        "Campos requeridos", "El stock inicial es obligatorio para nuevos productos.")
                    return
                if not stock_txt.isdigit() or int(stock_txt) < 0:
                    messagebox.showerror(
                        "Stock inválido", "El stock debe ser un número entero positivo.")
                    return
                stock = int(stock_txt)

            # Validaciones básicas
            if not codigo or not producto:
                messagebox.showwarning(
                    "Campos requeridos", "Código y Producto son campos obligatorios.")
                return

            if not self._validate_product_data(codigo, producto, str(stock) if not product_id else "0"):
                return

            # Obtener IDs de relaciones
            marca_id = self.model.get_id_by_name("marcas", marca_nombre)
            categoria_id = self.model.get_id_by_name("categorias", categoria_nombre)
            ubicacion_id = self.model.get_id_by_name("ubicaciones", ubicacion_nombre)

            # Identificar cuál está inactivo
            errores = []
            if marca_id is None:
                errores.append("Marca")
            if categoria_id is None:
                errores.append("Categoría")
            if ubicacion_id is None and ubicacion_nombre:  # Solo si es obligatorio
                errores.append("Ubicación")

            if errores:
                mensaje = (
                    f"Error: {', '.join(errores)} seleccionada se encuentra inactiva.\n"
                    "Para permitir la edición, por favor actívela en Ajustes."
                )
                messagebox.showerror("Error de relación inactiva", mensaje)
                return

            # Preparar datos para guardar - AGREGADO STOCK_MÍNIMO
            product_data = {
                'codigo': codigo,
                'nombre': producto,
                'marca_id': marca_id,
                'categoria_id': categoria_id,
                'stock': stock,  # 🔒 Usar stock actual en edición, nuevo stock en creación
                'ubicacion_id': ubicacion_id,
                'estado': estado,
                'stock_minimo': stock_minimo  # NUEVO CAMPO
            }

            # Guardar producto
            saved_id = self.model.save_product(product_data, product_id)

            # Registrar movimiento SOLO para nuevos productos
            if not product_id:
                self._register_product_movement(
                    None, saved_id, stock, ubicacion_id)

            messagebox.showinfo("Éxito", "Producto guardado correctamente")
            window.destroy()
            self.refresh_table()

        except Exception as e:
            messagebox.showerror(
                "Error", f"No se pudo guardar el producto: {e}")

    def _validate_product_data(self, codigo, producto, stock_txt):
        """Validar datos del producto - Modificado para edición"""
        if not codigo or not producto:
            messagebox.showwarning(
                "Campos requeridos", "Código y Producto son campos obligatorios.")
            return False

        # 🔒 Solo validar stock para nuevos productos
        if stock_txt != "0":  # En edición pasamos "0" para evitar validación
            if not stock_txt.isdigit() or int(stock_txt) < 0:
                messagebox.showerror(
                    "Stock inválido", "El stock debe ser un número entero positivo.")
                return False

        if not codigo.replace("-", "").isalnum():
            messagebox.showerror(
                "Código inválido", "El código solo debe contener letras, números y guiones.")
            return False

        if not all(c.isalnum() or c.isspace() for c in producto):
            messagebox.showerror(
                "Nombre inválido", "El nombre del producto solo debe contener letras, números y espacios.")
            return False

        return True

    def _register_product_movement(self, product_id, saved_id, stock, ubicacion_id):
        """Registrar movimiento de producto"""
        movement_controller = MovementController(
            None, self.app, create_ui=False)
        current_user = getattr(self.app, 'current_user', None)
        current_user_id = getattr(current_user, 'id', None)

        if product_id:  # Edición
            old_stock = self.model.get_old_stock(product_id)
            # Si old_stock es None, tratarlo como 0
            old_stock = old_stock if old_stock is not None else 0
            stock_diff = stock - old_stock

            if stock_diff != 0:
                movement_type = "Entrada" if stock_diff > 0 else "Salida"
                movement_controller.register_movement(
                    id_producto=product_id,
                    tipo=movement_type,
                    cantidad=abs(stock_diff),
                    id_ubicacion=ubicacion_id,
                    id_responsable=current_user_id,
                    referencia="Edición de stock inicial"  # Corregido - sin tilde
                )
        else:  # Nuevo producto
            try:
                movement_controller.register_movement(
                    id_producto=saved_id,
                    tipo="Entrada",
                    cantidad=stock,
                    id_ubicacion=ubicacion_id,
                    id_responsable=current_user_id,
                    referencia="Producto nuevo"
                )
            except Exception as e:
                messagebox.showwarning(
                    "Advertencia", f"Producto creado pero no se pudo registrar el movimiento: {e}")

    def edit_selected_product(self):
        """Editar producto seleccionado"""
        selected = self.view.get_selected_product()
        if not selected:
            messagebox.showwarning(
                "Advertencia", "Por favor seleccione un producto")
            return

        product_id = selected['tags'][0]
        self.show_product_form(product_id)

    def delete_selected_product(self):
        """Eliminar producto seleccionado"""
        selected = self.view.get_selected_product()
        if not selected:
            messagebox.showwarning(
                "Advertencia", "Por favor seleccione un producto")
            return

        product_id = selected['tags'][0]

        if messagebox.askyesno("Confirmar", "¿Está seguro de marcar este producto como inactivo?"):
            try:
                self.model.delete_product(product_id)
                messagebox.showinfo("Éxito", "Producto marcado como inactivo")
                self.refresh_table()
            except Exception as e:
                messagebox.showerror("Error", f"No se pudo eliminar: {e}")

    def show_add_stock_form(self):
        """Mostrar formulario para agregar stock"""
        selected = self.view.get_selected_product()
        if not selected:
            messagebox.showwarning(
                "Advertencia", "Seleccione un producto primero")
            return

        item_data = selected['values']
        product_id = selected['tags'][0]
        product_name = item_data[1]
        current_stock = item_data[5] if item_data[5] else 0

        form_window, qty_entry, add_btn = self.view.show_add_stock_form(
            product_name, current_stock)
        add_btn.configure(command=lambda: self.add_stock(
            product_id, qty_entry.get(), form_window))

    def add_stock(self, product_id, quantity, window):
        """Agregar stock a producto"""
        try:
            if not quantity.isdigit() or int(quantity) <= 0:
                messagebox.showerror(
                    "Error", "Ingrese una cantidad válida (número positivo)")
                return

            self.model.add_stock(product_id, quantity)

            # Registrar movimiento
            ubicacion_id = self.model.get_ubicacion_id(product_id)
            movement_controller = MovementController(
                None, self.app, create_ui=False)
            current_user = getattr(self.app, 'current_user', None)
            current_user_id = getattr(current_user, 'id', None)
            movement_controller.register_movement(
                id_producto=product_id,
                tipo="Entrada",
                cantidad=int(quantity),
                id_ubicacion=ubicacion_id,
                id_responsable=current_user_id,
                referencia="Entrada de stock"
            )

            messagebox.showinfo("Éxito", "Stock actualizado correctamente")
            window.destroy()
            self.refresh_table()

        except Exception as e:
            messagebox.showerror(
                "Error", f"No se pudo actualizar el stock: {e}")

    def add_new_value(self, table, parent_window=None):
        """Agregar nuevo valor a tabla relacionada"""
        # ✅ MODIFICADO: Pasar parent_window a la vista para mantenerla abierta
        form_window, entry, save_btn = self.view.show_new_value_form(
            table, parent_window)
        save_btn.configure(command=lambda: self.guardar_valor(
            table, entry.get(), form_window, parent_window))

    def guardar_valor(self, table, value, modal_window, parent_window=None):
        """Guardar nuevo valor en tabla relacionada"""
        try:
            if not value:
                messagebox.showwarning(
                    "Advertencia", "El campo no puede estar vacío.")
                return

            # Guardar el nuevo valor
            result = self.model.add_new_value(table, value)
            if result:
                mensajes = {
                    'marcas': 'Marca agregada con éxito',
                    'categorias': 'Categoría agregada con éxito',
                    'ubicaciones': 'Ubicación agregada con éxito'
                }
                messagebox.showinfo("Éxito", mensajes.get(
                    table, "Guardado con éxito"))

                # ✅ SOLO CERRAR LA VENTANA MODAL, NO LA VENTANA PADRE
                modal_window.destroy()

                # ✅ RE-ENFOCAR LA VENTANA PADRE SI EXISTE
                if parent_window:
                    parent_window.focus_set()
                    parent_window.lift()
                    parent_window.attributes('-topmost', True)
                    parent_window.attributes('-topmost', False)

                # Actualizar comboboxes y seleccionar automáticamente el nuevo valor
                self.actualizar_comboboxes_despues_de_agregar(table, result)

        except Exception as e:
            messagebox.showerror("Error", f"No se pudo guardar: {e}")

    def actualizar_comboboxes_despues_de_agregar(self, table, nuevo_valor):
        """Actualizar comboboxes después de agregar un nuevo valor"""
        try:
            # Obtener datos actualizados de la base de datos
            datos_actualizados = self.model.get_combobox_data(table)

            # Actualizar el combobox correspondiente en el formulario actual
            if hasattr(self, '_formulario_activo') and self._formulario_activo:
                entries = self._formulario_activo.get('entries', {})

                if table == 'marcas' and 'Marca:' in entries:
                    entries['Marca:'].set_completion_list(
                        [m[1] for m in datos_actualizados])
                    # Seleccionar automáticamente el nuevo valor
                    entries['Marca:'].set(nuevo_valor[1])

                elif table == 'categorias' and 'Categoría:' in entries:
                    entries['Categoría:'].set_completion_list(
                        [c[1] for c in datos_actualizados])
                    entries['Categoría:'].set(nuevo_valor[1])

                elif table == 'ubicaciones' and 'Ubicación:' in entries:
                    entries['Ubicación:'].set_completion_list(
                        [u[1] for u in datos_actualizados])
                    entries['Ubicación:'].set(nuevo_valor[1])

            # También actualizar los comboboxes de filtros en la vista principal
            if table == 'categorias':
                categorias_actualizadas = self.model.get_combobox_data(
                    "categorias")
                self.view.update_categories_combo(categorias_actualizadas)
            elif table == 'marcas':
                marcas_actualizadas = self.model.get_combobox_data("marcas")
                self.view.update_marcas_combo(marcas_actualizadas)

        except Exception as e:
            print(f"Error al actualizar comboboxes: {e}")

    def export_inventory(self):
        """Exportar inventario a CSV"""
        try:
            # Obtener datos actuales de la tabla
            filtered_data = []
            for item in self.view.tree.get_children():
                row_data = self.view.tree.item(item)['values']
                filtered_data.append(row_data)

            filename, error = ExportManager.export_inventory(filtered_data)

            if error:
                messagebox.showerror("Error", f"Error al exportar: {error}")
            else:
                messagebox.showinfo(
                    "Éxito", f"Inventario exportado en {filename}")

        except Exception as e:
            messagebox.showerror(
                "Error", f"Error al exportar inventario: {str(e)}")

    def refresh_comboboxes(self):
        """Refrescar todos los combobox con datos actualizados"""
        try:
            categorias = self.model.get_combobox_data("categorias")
            self.view.update_categories_combo(categorias)
            marcas = self.model.get_combobox_data("marcas")
            self.view.update_marcas_combo(marcas)
        except Exception as e:
            print(f"Error al refrescar comboboxes: {e}")
