import tkinter as tk
from tkinter import ttk, messagebox
from models.proveedores_models import SupplierModel
from views.proveedores_views import SupplierView
from models.export_manager import ExportManager


class SupplierController:
    def __init__(self, frame, app):
        self.model = SupplierModel()
        self.view = SupplierView(frame, app)
        self.view.set_controller(self)
        self.app = app
        self.setup_ui()

    def setup_ui(self):
        """Configura la interfaz de usuario"""
        self.view.setup_suppliers_tab()
        self.refresh_suppliers_table()

    def refresh_suppliers_table(self, category_filter="Todas", rating_filter="Todas", price_filter="Todos"):
        """Actualiza la tabla de proveedores"""
        try:
            data = self.model.get_all_suppliers(
                category_filter, rating_filter, price_filter)
            self.view.refresh_table(data)
        except Exception as e:
            messagebox.showerror("Error", f"Error al cargar proveedores: {e}")

    def apply_suppliers_filters(self, category, rating, price):
        """Aplica los filtros seleccionados"""
        self.refresh_suppliers_table(category, rating, price)

    def show_supplier_form(self, supplier_id=None):
        """Muestra el formulario para agregar/editar proveedor usando la vista unificada"""
        try:
            # Usar el método de la vista que ya tiene los estilos correctos
            form_window, entries, save_btn = self.view.show_supplier_form(
                self.app, supplier_id)

            # Configurar valores de combobox
            if "Valoración:" in entries:
                entries["Valoración:"]['values'] = [
                    "1 Estrella", "2 Estrellas", "3 Estrellas", "4 Estrellas", "5 Estrellas"]
            if "Precios:" in entries:
                entries["Precios:"]['values'] = ["Bajo", "Medio", "Alto"]
            if "Categorías:" in entries:
                try:
                    categories = self.model.get_categories()
                    # Actualizar el combobox usando su método de autocompletado si existe
                    cat_combo = entries["Categorías:"]
                    if hasattr(cat_combo, 'set_completion_list'):
                        cat_combo.set_completion_list(categories)
                    else:
                        cat_combo['values'] = categories

                    # Intentar seleccionar el primer elemento de forma segura
                    try:
                        cat_combo.current(0)
                    except Exception:
                        if hasattr(cat_combo, 'set') and categories:
                            cat_combo.set(categories[0])
                except Exception as e:
                    messagebox.showerror(
                        "Error", f"No se pudieron cargar categorías: {e}")

            # Si estamos editando, cargamos los datos
            if supplier_id:
                self.load_supplier_data(supplier_id, entries)

                # Conectar botón de gestionar productos si existe
                if "manage_btn" in entries:
                    entries["manage_btn"].configure(
                        command=lambda: self.manage_supplier_products(
                            supplier_id)
                    )

            # Conectar el botón guardar
            save_btn.configure(command=lambda: self.save_supplier(
                entries, form_window, supplier_id))

        except Exception as e:
            messagebox.showerror(
                "Error", f"No se pudo abrir el formulario: {e}")

    def load_supplier_data(self, supplier_id, entries):
        """Carga los datos de un proveedor en el formulario"""
        try:
            # Limpiar todos los campos primero
            for entry in entries.values():
                if isinstance(entry, (ttk.Entry, ttk.Combobox)):
                    entry.delete(0, tk.END)
                elif isinstance(entry, tk.Text):
                    entry.delete("1.0", tk.END)

            # Datos básicos
            data = self.model.get_supplier_by_id(supplier_id)

            if data:
                entries["Nombre:"].insert(0, data[0] or "")
                entries["Contacto:"].insert(0, data[1] or "")
                entries["Teléfono:"].insert(0, data[2] or "")
                entries["Email:"].insert(0, data[3] or "")
                entries["Dirección:"].insert(0, data[4] or "")
                entries["Redes Sociales:"].insert(0, data[5] or "")

                if data[6]:
                    star_text = f"{data[6]} Estrellas" if data[6] > 1 else f"{data[6]} Estrella"
                    if "Valoración:" in entries:
                        try:
                            entries["Valoración:"].set(star_text)
                        except Exception:
                            pass
                # Cargar categoría principal (si existe)
                try:
                    categories = self.model.get_supplier_categories(
                        supplier_id)
                    if categories and categories[0] != "Ninguna":
                        # Intentar setear en el combobox de categorías
                        if "Categorías:" in entries:
                            cat_widget = entries["Categorías:"]
                            try:
                                if hasattr(cat_widget, 'set'):
                                    cat_widget.set(categories[0])
                            except Exception:
                                pass
                except Exception:
                    # No crítico: continuar sin bloquear la carga del formulario
                    pass

                if data[7]:
                    entries["Manejo de Precios:"].set(data[7])

                if data[8]:
                    entries["Comentarios:"].insert("1.0", data[8])

        except Exception as e:
            messagebox.showerror(
                "Error", f"No se pudieron cargar los datos: {e}")

    def save_supplier(self, entries, window, supplier_id=None):
        """Guarda un nuevo proveedor o actualiza uno existente"""
        try:
            # Validación
            if not entries["Nombre:"].get():
                messagebox.showwarning("Error", "El nombre es obligatorio")
                return

            # Preparar datos
            data = (
                entries["Nombre:"].get(),
                entries["Contacto:"].get(),
                entries["Teléfono:"].get(),
                entries["Email:"].get(),
                entries["Dirección:"].get(),
                entries["Redes Sociales:"].get(),
                int(entries["Valoración:"].get().split()[0]
                    ) if entries["Valoración:"].get() else None,
                entries["Manejo de Precios:"].get(),
                entries["Comentarios:"].get("1.0", tk.END).strip(),
            )

            # Guardar en la base de datos
            if supplier_id is None:
                new_id = self.model.create_supplier(data)
                supplier_id = new_id
            else:
                self.model.update_supplier(supplier_id, data)

            # Guardar la categoría seleccionada en la tabla de relaciones
            try:
                if "Categorías:" in entries:
                    selected_cat = ''
                    try:
                        selected_cat = entries["Categorías:"].get()
                    except Exception:
                        # Algunos widgets usan .get(), otros usan .get('') etc.
                        try:
                            selected_cat = entries["Categorías:"].get(0)
                        except Exception:
                            selected_cat = ''

                    if selected_cat:
                        # Delegar al modelo la asociación
                        try:
                            self.model.set_supplier_category(
                                supplier_id, selected_cat)
                        except Exception:
                            # No crítico: si falla la asociación, no cancelamos el flujo principal
                            pass
            except Exception:
                pass

            messagebox.showinfo("Éxito", "Proveedor guardado correctamente")
            window.destroy()
            self.refresh_suppliers_table()

        except Exception as e:
            messagebox.showerror(
                "Error", f"No se pudo guardar el proveedor: {e}")

    def manage_supplier_products(self, supplier_id):
        """Gestiona los productos asociados a un proveedor"""
        if not supplier_id:
            messagebox.showwarning(
                "Advertencia", "Primero debe guardar el proveedor para gestionar productos")
            return

        try:
            import tkinter as tk
            from tkinter import ttk
            # Obtener datos del modelo
            supplier_data = self.model.get_supplier_by_id(supplier_id)
            supplier_name = supplier_data[0]
            available_products = self.model.get_available_products(supplier_id)
            current_products = self.model.get_supplier_products(supplier_id)

            # Formatear datos para la view
            available_products_formatted = [
                f"{p[1]} ({p[2]})" for p in available_products]
            current_products_formatted = [(p[0], p[1])
                                          for p in current_products]

            # Delegar la creación de UI a la View
            products_window, product_combo, tree, btn_frame = self.view.show_supplier_products_management(
                supplier_id, supplier_name, available_products_formatted, current_products_formatted
            )

            # Si los botones no existen, crearlos aquí
            for widget in btn_frame.winfo_children():
                widget.destroy()

            ttk.Button(btn_frame, text="➕ Agregar",
                       command=lambda: self.add_product_to_supplier(supplier_id, product_combo.get(), product_combo, tree)).pack(side="left", padx=5)

            ttk.Button(btn_frame, text="➖ Eliminar Seleccionado",
                       command=lambda: self.remove_product_from_supplier(supplier_id, tree, product_combo)).pack(side="left", padx=5)

            ttk.Button(btn_frame, text="Cerrar",
                       command=products_window.destroy).pack(side="right", padx=5)

        except Exception as e:
            messagebox.showerror(
                "Error", f"No se pudo abrir la gestión de productos: {e}")

    def add_product_to_supplier(self, supplier_id, product_with_category, product_combo, tree):
        """Agrega un producto al proveedor"""
        if not product_with_category:
            messagebox.showwarning(
                "Advertencia", "Seleccione un producto para agregar")
            return

        try:
            # Extraer nombre del producto
            product_name = product_with_category.split(" (")[0]
            product_id = self.model.get_product_id_by_name(product_name)

            if not product_id:
                messagebox.showerror("Error", "No se encontró el producto")
                return

            # Insertar relación en el modelo
            self.model.add_product_to_supplier(supplier_id, product_id)
            messagebox.showinfo("Éxito", "Producto agregado correctamente")

            # Actualizar UI a través de la View
            self._refresh_products_ui(supplier_id, product_combo, tree)

        except Exception as e:
            messagebox.showerror(
                "Error", f"No se pudo agregar el producto: {e}")

    def remove_product_from_supplier(self, supplier_id, tree, product_combo):
        """Elimina un producto del proveedor"""
        selected_item = self.view.get_selected_product_from_tree(tree)
        if not selected_item:
            messagebox.showwarning(
                "Advertencia", "Seleccione un producto para eliminar")
            return

        try:
            product_name = tree.item(selected_item, "values")[0]
            product_id = self.model.get_product_id_by_name(product_name)

            # Eliminar relación del modelo
            self.model.remove_product_from_supplier(supplier_id, product_id)
            messagebox.showinfo("Éxito", "Producto eliminado correctamente")

            # Actualizar UI a través de la View
            self._refresh_products_ui(supplier_id, product_combo, tree)

        except Exception as e:
            messagebox.showerror(
                "Error", f"No se pudo eliminar el producto: {e}")

    def _refresh_products_ui(self, supplier_id, product_combo, tree):
        """Actualiza la UI de productos después de cambios"""
        try:
            available_products = self.model.get_available_products(supplier_id)
            current_products = self.model.get_supplier_products(supplier_id)

            # Actualizar combobox
            product_combo['values'] = [
                f"{p[1]} ({p[2]})" for p in available_products]

            # Actualizar treeview
            self.view.refresh_products_tree(
                tree, [(p[0], p[1]) for p in current_products])

        except Exception as e:
            messagebox.showerror(
                "Error", f"No se pudieron actualizar los datos: {e}")

    def show_supplier_details(self):
        """Muestra los detalles del proveedor seleccionado"""
        selected = self.view.get_selected_supplier()
        if not selected:
            messagebox.showwarning(
                "Advertencia", "Seleccione un proveedor para ver detalles")
            return

        supplier_name = selected[1]
        try:
            supplier_data = self.model.get_supplier_by_name(supplier_name)
            if not supplier_data:
                messagebox.showerror(
                    "Error", "No se encontró el proveedor en la base de datos")
                return

            supplier_id = supplier_data[0]
            categories = self.model.get_supplier_categories(supplier_id)
            products = self.model.get_supplier_products(supplier_id)

            self.view.show_supplier_details_view(
                supplier_data, categories, products)

        except Exception as e:
            messagebox.showerror(
                "Error", f"No se pudieron cargar los detalles: {e}")

    def edit_supplier(self):
        """Permite editar un proveedor seleccionado"""
        selected = self.view.get_selected_supplier()
        if not selected:
            messagebox.showwarning(
                "Advertencia", "Seleccione un proveedor para editar")
            return

        supplier_name = selected[1]
        try:
            supplier_data = self.model.get_supplier_by_name(supplier_name)
            if not supplier_data:
                messagebox.showerror(
                    "Error", "No se encontró el proveedor en la base de datos")
                return

            self.show_supplier_form(supplier_data[0])

        except Exception as e:
            messagebox.showerror(
                "Error", f"No se pudo cargar el proveedor: {e}")

    def delete_supplier(self):
        """Elimina un proveedor seleccionado"""
        selected = self.view.get_selected_supplier()
        if not selected:
            messagebox.showwarning(
                "Advertencia", "Seleccione un proveedor para eliminar")
            return

        supplier_name = selected[1]
        if not messagebox.askyesno("Confirmar", f"¿Está seguro que desea eliminar al proveedor '{supplier_name}'?"):
            return

        try:
            self.model.delete_supplier(supplier_name)
            messagebox.showinfo("Éxito", "Proveedor eliminado correctamente")
            self.refresh_suppliers_table()
        except Exception as e:
            messagebox.showerror(
                "Error", f"No se pudo eliminar el proveedor: {e}")

    def load_categories_combobox(self, combo, add_all_option=False):
        """Carga categorías en un combobox"""
        try:
            categories = self.model.get_categories()
            if add_all_option:
                # Preponer "Todas" para opción de filtro
                categories = ["Todas"] + categories

            # Si el combobox es nuestro AutocompleteCombobox, usar su API para mantener
            # la lista interna de completado; si no, caer al comportamiento estándar.
            if hasattr(combo, 'set_completion_list'):
                combo.set_completion_list(categories)
            else:
                combo['values'] = categories

            # Seleccionar la primera opción de forma segura
            try:
                combo.current(0)
            except Exception:
                if hasattr(combo, 'set') and categories:
                    combo.set(categories[0])
        except Exception as e:
            messagebox.showerror(
                "Error", f"No se pudieron cargar las categorías: {e}")

    def export_suppliers(self):
        """Exportar proveedores a CSV"""
        try:
            # Obtener datos actuales de la tabla
            filtered_data = []
            for item in self.view.tree.get_children():
                row_data = self.view.tree.item(item)['values']
                filtered_data.append(row_data)

            # Usar ExportManager para exportar
            filename, error = ExportManager.export_suppliers(filtered_data)

            if error:
                messagebox.showerror("Error", f"Error al exportar: {error}")
            else:
                messagebox.showinfo(
                    "Éxito", f"Proveedores exportados en {filename}")

        except Exception as e:
            messagebox.showerror(
                "Error", f"Error al exportar proveedores: {str(e)}")
