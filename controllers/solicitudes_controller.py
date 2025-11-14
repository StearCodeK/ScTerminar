import tkinter as tk
from tkinter import messagebox
from models.solicitudes_model import SolicitudesModel
from views.solicitudes_view import SolicitudesView
from controllers.movimientos_controllers import MovementController
from models.export_manager import ExportManager


class SolicitudesController:
    def __init__(self, content_frame, *args):
        self.model = SolicitudesModel()

        # Manejar diferentes firmas del constructor
        if len(args) == 1:
            app = args[0]
        elif len(args) == 3:
            _, _, app = args
        else:
            raise TypeError(
                "Invalid constructor arguments for SolicitudesController")

        self.app = app
        self.view = SolicitudesView(content_frame, app)
        self.view.set_controller(self)
        self.current_user = getattr(app, 'current_user', None)
        self.stock_actual = {}
        self.producto_info = {}
        self.current_form_data = None

    def mostrar_interfaz_principal(self):
        """Mostrar la interfaz principal de gestión de solicitudes"""
        tree = self.view.mostrar_interfaz_principal()
        self.cargar_departamentos_combo()
        self.cargar_solicitudes()
        return tree

    def cargar_departamentos_combo(self):
        """Cargar departamentos en el combobox"""
        departamentos = self.model.obtener_departamentos()
        self.view.cargar_departamentos_combo(departamentos)

    def cargar_solicitudes(self):
        """Cargar solicitudes en la tabla"""
        filtros = self.view.obtener_filtros()
        solicitudes = self.model.obtener_solicitudes(filtros)
        self.view.actualizar_tabla_solicitudes(solicitudes)

    def buscar_solicitudes(self):
        """Buscar solicitudes según los filtros"""
        self.cargar_solicitudes()

    def limpiar_filtros(self):
        """Limpiar todos los filtros y recargar la tabla"""
        self.view.limpiar_filtros()
        self.cargar_solicitudes()

    def mostrar_formulario_nueva_entrega(self):
        """Mostrar formulario para nueva entrega"""
        departamentos = self.model.obtener_departamentos()
        solicitantes = self.model.obtener_solicitantes()

        self.current_form_data = self.view.mostrar_formulario_nueva_entrega(
            departamentos, solicitantes, self.current_user
        )

        # ✅ Usar solo categorías en inventario
        categorias = self.model.obtener_categorias_en_inventario()
        self.view.cargar_categorias_combo(
            categorias, self.current_form_data['category_combo'])

        # Configurar eventos
        self.current_form_data['category_combo'].bind(
            "<<ComboboxSelected>>",
            lambda e: self.on_categoria_seleccionada()
        )

        self.current_form_data['product_combo'].bind(
            "<<ComboboxSelected>>",
            lambda e: self.on_producto_seleccionado()
        )

    def on_categoria_seleccionada(self):
        """Manejar la selección de una categoría"""
        if not self.current_form_data:
            return

        categoria_nombre = self.current_form_data['selected_category'].get()
        if not categoria_nombre:
            return

        categorias = self.model.obtener_categorias_en_inventario()
        categoria_id = next(
            (c[0] for c in categorias if c[1] == categoria_nombre), None)

        if categoria_id:
            # ✅ Usar solo productos de inventario
            productos = self.model.obtener_productos_por_categoria_en_inventario(
                categoria_id)
            self.view.cargar_productos_combo(
                productos, self.current_form_data['product_combo'])

    def on_producto_seleccionado(self):
        """Manejar la selección de un producto"""
        if not self.current_form_data:
            return

        producto_nombre = self.current_form_data['selected_product'].get()
        if not producto_nombre:
            return

        detalles = self.model.obtener_detalles_producto(producto_nombre)
        if detalles:
            producto_id, stock, ubicacion, estado = detalles

            self.producto_info[producto_nombre] = {
                'id': producto_id,
                'ubicacion': ubicacion if ubicacion else "N/A",
                'estado': estado if estado else "disponible"
            }

            if producto_nombre in self.stock_actual:
                stock_disponible = self.stock_actual[producto_nombre]
            else:
                stock_disponible = stock
                self.stock_actual[producto_nombre] = stock_disponible

            self.view.actualizar_detalles_producto(
                estado=self.producto_info[producto_nombre]['estado'],
                stock=stock_disponible,
                ubicacion=self.producto_info[producto_nombre]['ubicacion'],
                estado_label=self.current_form_data['estado_label'],
                stock_label=self.current_form_data['stock_label'],
                ubicacion_label=self.current_form_data['ubicacion_label']
            )

    def agregar_producto_form(self, producto_nombre, cantidad, output_tree, stock_label, ubicacion_label, qty_entry):
        """Agregar producto a la lista de entrega desde el formulario"""
        if not producto_nombre:
            messagebox.showwarning("Advertencia", "Seleccione un producto")
            return

        try:
            cantidad = int(cantidad)
            if cantidad <= 0:
                messagebox.showwarning(
                    "Error", "La cantidad debe ser mayor a cero")
                return

            stock_disponible = self.stock_actual.get(producto_nombre, 0)

            if cantidad > stock_disponible:
                messagebox.showwarning(
                    "Error", "No hay suficiente stock disponible")
                return

            # Verificar si el producto ya está en la lista
            for item in output_tree.get_children():
                if output_tree.item(item)["values"][0] == producto_nombre:
                    current_qty = output_tree.item(item)["values"][1]
                    if (current_qty + cantidad) > stock_disponible:
                        messagebox.showwarning(
                            "Error", "No hay suficiente stock disponible")
                        return

                    output_tree.item(item, values=(
                        producto_nombre,
                        current_qty + cantidad,
                        self.producto_info[producto_nombre]['ubicacion']
                    ))

                    self.stock_actual[producto_nombre] = stock_disponible - cantidad
                    stock_label.config(
                        text=str(self.stock_actual[producto_nombre]))
                    qty_entry.delete(0, 'end')
                    return

            # Agregar nuevo producto
            output_tree.insert("", "end", values=(
                producto_nombre,
                cantidad,
                self.producto_info[producto_nombre]['ubicacion']
            ))

            self.stock_actual[producto_nombre] = stock_disponible - cantidad
            stock_label.config(text=str(self.stock_actual[producto_nombre]))
            qty_entry.delete(0, 'end')

        except ValueError:
            messagebox.showwarning("Error", "Ingrese una cantidad válida")

    def quitar_producto_form(self, output_tree, stock_label):
        """Quitar producto de la lista de entrega desde el formulario"""
        selected = output_tree.selection()
        if not selected:
            messagebox.showwarning("Advertencia", "Seleccione un producto")
            return

        producto_nombre = output_tree.item(selected[0])["values"][0]
        cantidad = output_tree.item(selected[0])["values"][1]

        if producto_nombre in self.stock_actual:
            self.stock_actual[producto_nombre] += cantidad

        output_tree.delete(selected[0])

    def registrar_entrega_form(self, dept_combo, sol_combo, resp_entrega_label, memo_entry, output_tree, departamentos, solicitantes, window):
        """Registrar una nueva entrega desde el formulario"""
        # Validaciones básicas
        if not self._validar_campos_basicos(dept_combo, sol_combo, memo_entry, output_tree):
            return

        try:
            id_responsable_entrega = self._obtener_id_usuario_actual()
            if not id_responsable_entrega:
                return

            # Registrar la solicitud
            datos_solicitud = (
                departamentos[dept_combo.current()][0],
                solicitantes[sol_combo.current()][0],
                id_responsable_entrega,
                memo_entry.get().strip()
            )

            solicitud_id = self.model.registrar_solicitud(datos_solicitud)
            if not solicitud_id:
                raise Exception("No se pudo registrar la solicitud")

            # Registrar productos y movimientos
            self._registrar_productos_entrega(
                solicitud_id, output_tree, id_responsable_entrega, memo_entry.get().strip())

            self.model.commit()
            messagebox.showinfo("Éxito", "Entrega registrada correctamente")
            window.destroy()
            self.cargar_solicitudes()

        except Exception as e:
            messagebox.showerror(
                "Error", f"No se pudo registrar la entrega: {e}")
            self.model.rollback()

    def _validar_campos_basicos(self, dept_combo, sol_combo, memo_entry, output_tree):
        """Validar campos básicos del formulario"""
        if dept_combo.current() == -1 or sol_combo.current() == -1:
            messagebox.showwarning(
                "Advertencia", "Complete todos los campos requeridos")
            return False

        if not memo_entry.get().strip():
            messagebox.showwarning(
                "Advertencia", "Ingrese una referencia/memo")
            return False

        if not output_tree.get_children():
            messagebox.showwarning(
                "Advertencia", "Agregue al menos un producto")
            return False

        return True

    def _obtener_id_usuario_actual(self):
        """Obtener ID del usuario actual"""
        if not hasattr(self.app, 'current_user') or not hasattr(self.app.current_user, 'id'):
            messagebox.showerror(
                "Error", "No se pudo identificar al usuario actual")
            return None
        return self.app.current_user.id

    def _registrar_productos_entrega(self, solicitud_id, output_tree, id_responsable_entrega, memo_text):
        """Registrar productos de la entrega"""
        movement_controller = MovementController(
            None, self.app, create_ui=False)

        for item in output_tree.get_children():
            producto_nombre, cantidad, _ = output_tree.item(item)["values"]
            cantidad = int(cantidad)
            producto_id = self.producto_info[producto_nombre]['id']

            # Registrar detalle
            detalle_data = (solicitud_id, producto_id, cantidad)
            self.model.registrar_detalle_solicitud(detalle_data)

            # Actualizar inventario
            self.model.actualizar_inventario(producto_id, cantidad)

            # Registrar movimiento
            movement_controller.register_movement(
                id_producto=producto_id,
                tipo="Salida",
                cantidad=cantidad,
                id_responsable=id_responsable_entrega,
                referencia=f"Solicitud #{memo_text}"
            )

    def mostrar_detalles_solicitud(self):
        """Mostrar detalles de la solicitud seleccionada"""
        solicitud_data = self.view.obtener_solicitud_seleccionada()
        if not solicitud_data or len(solicitud_data) < 7:
            messagebox.showwarning("Advertencia", "Seleccione una solicitud")
            return

        solicitud_id = solicitud_data[6]
        solicitud = self.model.obtener_detalles_solicitud(solicitud_id)
        if not solicitud:
            messagebox.showerror(
                "Error", "No se encontró la solicitud seleccionada")
            return

        productos = self.model.obtener_productos_solicitud(solicitud_id)
        self.view.mostrar_detalles_solicitud(solicitud, productos)

    def agregar_departamento(self, dept_combo):
        """Agregar nuevo departamento"""
        entry = self.view.mostrar_formulario_departamento()
        # El guardado se maneja en guardar_departamento

    def guardar_departamento(self, nombre, window):
        """Guardar nuevo departamento"""
        if not nombre:
            messagebox.showwarning(
                "Advertencia", "El nombre no puede estar vacío")
            return

        nuevo_dept = self.model.agregar_departamento(nombre)
        if nuevo_dept:
            departamentos = self.model.obtener_departamentos()
            # Update main view combobox (filters)
            self.view.cargar_departamentos_combo(departamentos)

            # If the delivery form is open, update its dept combobox in-place
            if self.current_form_data:
                # Update the autocomplete list on the form's dept combobox widget
                if 'dept_combo' in self.current_form_data:
                    try:
                        self.current_form_data['dept_combo'].set_completion_list(
                            [d[1] for d in departamentos])
                    except (AttributeError, TypeError):
                        # Fallback: ignore if widget not available or invalid
                        pass

                # Set the selected value variable so the form shows the new department
                if 'selected_departamento' in self.current_form_data:
                    self.current_form_data['selected_departamento'].set(nombre)

            # Close the add-department modal first — do NOT re-open the delivery form
            try:
                window.destroy()
            except tk.TclError:
                pass

            # Then show info dialog with proper parent so focus returns to the delivery form
            parent = None
            if self.current_form_data and 'window' in self.current_form_data:
                parent = self.current_form_data['window']
            try:
                if parent:
                    messagebox.showinfo(
                        "Éxito", "Departamento agregado con éxito", parent=parent)
                else:
                    messagebox.showinfo(
                        "Éxito", "Departamento agregado con éxito")
            except tk.TclError:
                # If messagebox fails for some reason, ignore — the main change is window order
                pass

    def agregar_solicitante(self, sol_combo, dept_combo):
        """Agregar nuevo solicitante"""
        # sol_combo may be passed by the caller but isn't needed here; keep a reference to avoid unused-arg warnings
        _ = sol_combo
        dept_seleccionado = dept_combo.get()
        self.view.mostrar_formulario_solicitante(
            self.model.obtener_departamentos(), dept_seleccionado
        )

    def guardar_solicitante(self, cedula, nombre, dept_nombre, window):
        """Guardar nuevo solicitante"""
        if not all([cedula, nombre, dept_nombre]):
            messagebox.showwarning(
                "Advertencia", "Todos los campos son requeridos")
            return

        if not cedula.replace("-", "").isdigit():
            messagebox.showwarning(
                "Error", "La cédula debe contener solo números y guiones")
            return

        departamentos = self.model.obtener_departamentos()
        dept_id = next((d[0]
                       for d in departamentos if d[1] == dept_nombre), None)

        if not dept_id:
            messagebox.showerror("Error", "Departamento no válido")
            return

        nuevo_sol = self.model.agregar_solicitante(cedula, nombre, dept_id)
        if nuevo_sol:
            # Recargar solicitantes y actualizar el combobox
            solicitantes = self.model.obtener_solicitantes()
            nombres_solicitantes = [f"{s[1]} ({s[2]})" for s in solicitantes]
            # Update the form's solicitante combobox if present
            if self.current_form_data:
                if 'sol_combo' in self.current_form_data:
                    try:
                        self.current_form_data['sol_combo'].set_completion_list(
                            nombres_solicitantes)
                    except (AttributeError, TypeError):
                        pass

                if 'selected_solicitante' in self.current_form_data:
                    self.current_form_data['selected_solicitante'].set(
                        f"{nombre} ({cedula})")

            # Close the add-solicitante modal first
            try:
                window.destroy()
            except tk.TclError:
                pass

            # Then show info dialog with proper parent so focus returns to the delivery form
            parent = None
            if self.current_form_data and 'window' in self.current_form_data:
                parent = self.current_form_data['window']
            try:
                if parent:
                    messagebox.showinfo(
                        "Éxito", "Solicitante agregado con éxito", parent=parent)
                else:
                    messagebox.showinfo(
                        "Éxito", "Solicitante agregado con éxito")
            except tk.TclError:
                pass

    def export_requests(self):
        """Exportar solicitudes a Excel, una fila por producto solicitado"""
        try:
            filtros = self.view.obtener_filtros()
            solicitudes = self.model.obtener_solicitudes(filtros)
            # solicitudes: [nro, fecha, departamento, solicitante, referencia, responsable_entrega, id_solicitud]
            export_rows = []
            for row in solicitudes:
                nro, fecha, departamento, solicitante, referencia, responsable_entrega, id_solicitud = row
                productos = self.model.obtener_productos_solicitud(
                    id_solicitud)
                # productos: [(nombre, cantidad, codigo)]
                if productos:
                    for prod in productos:
                        nombre_producto, cantidad, _ = prod
                        export_rows.append([
                            nro, fecha, departamento, solicitante, referencia, nombre_producto, cantidad, responsable_entrega
                        ])
                else:
                    # Si no hay productos, dejar vacío
                    export_rows.append([
                        nro, fecha, departamento, solicitante, referencia, '', '', responsable_entrega
                    ])

            headers = [
                "Nro", "Fecha", "Departamento", "Solicitante", "Referencia", "Producto", "Cantidad", "Responsable Entrega"
            ]
            filename, error = ExportManager.export_with_custom_format(
                export_rows, headers, "solicitudes", "Solicitudes")

            if error:
                messagebox.showerror("Error", f"Error al exportar: {error}")
            else:
                messagebox.showinfo(
                    "Éxito", f"Solicitudes exportadas en {filename}")

        except Exception as e:
            messagebox.showerror(
                "Error", f"Error al exportar solicitudes: {str(e)}")

    def cerrar_conexion(self):
        """Cerrar la conexión a la base de datos"""
        self.model.close()
