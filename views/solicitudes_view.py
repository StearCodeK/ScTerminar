import tkinter as tk
from tkinter import ttk
# ✅ Importar AutocompleteCombobox
from views.base_view import BaseView, AutocompleteCombobox


class SolicitudesView(BaseView):
    def __init__(self, content_frame, app):
        super().__init__(content_frame, app)
        self.controller = None
        self.tree = None
        self.search_var = tk.StringVar()
        self.dept_var = tk.StringVar()
        self.date_from_var = tk.StringVar()
        self.date_to_var = tk.StringVar()

    def set_controller(self, controller):
        """Establecer el controlador para esta vista"""
        self.controller = controller

    def mostrar_interfaz_principal(self):
        """Mostrar la interfaz principal de gestión de solicitudes"""
        # Limpiar frame
        for widget in self.frame.winfo_children():
            widget.destroy()

        # Contenedor principal
        main_container = self.create_main_container(self.frame)
        main_container.pack(fill="both", expand=True, padx=10, pady=5)

        # Título principal
        title_frame = self.create_section_frame(main_container)
        title_frame.pack(fill="x", pady=(0, 10))

        tk.Label(
            title_frame,
            text="Gestión de Solicitudes de Salida",
            font=self.title_font,
            bg=self.bg_color,
            fg=self.fg_color
        ).pack(side="left")

        # Frame para botones de acción
        top_button_frame = self.create_section_frame(main_container)
        top_button_frame.pack(fill="x", pady=(0, 5))

        # Botones de acción
        actions = [
            ("➕ Registrar Entrega", self.controller.mostrar_formulario_nueva_entrega),
            ("🔍 Detalles de Solicitud", self.controller.mostrar_detalles_solicitud),
            ("📤 Exportar", self.controller.export_requests)
        ]
        btn_frame, _ = self.create_action_buttons(top_button_frame, actions)
        btn_frame.pack(side="left")

        # Frame para filtros
        filter_frame = self.create_filter_frame(main_container, "Filtros")
        filter_frame.pack(fill="x", pady=5)

        # Buscador
        tk.Label(
            filter_frame,
            text="Buscar por Referencia:",
            font=self.label_font,
            bg=self.bg_color,
            fg=self.fg_color
        ).pack(side="left", padx=5)

        search_entry = ttk.Entry(
            filter_frame,
            textvariable=self.search_var,
            width=20,
            font=self.entry_font
        )
        search_entry.pack(side="left", padx=5)

        # ✅ CORREGIR: Filtro por departamento usando AutocompleteCombobox
        tk.Label(
            filter_frame,
            text="Departamento:",
            font=self.label_font,
            bg=self.bg_color,
            fg=self.fg_color
        ).pack(side="left", padx=5)

        self.dept_combo = AutocompleteCombobox(  # ✅ Cambiar a AutocompleteCombobox
            filter_frame,
            textvariable=self.dept_var,
            width=15,
            font=self.entry_font
        )
        self.dept_combo.pack(side="left", padx=5)

        # Filtro por fecha
        tk.Label(
            filter_frame,
            text="Desde:",
            font=self.label_font,
            bg=self.bg_color,
            fg=self.fg_color
        ).pack(side="left", padx=5)

        date_from_entry = ttk.Entry(
            filter_frame,
            textvariable=self.date_from_var,
            width=10,
            font=self.entry_font
        )
        date_from_entry.pack(side="left", padx=5)

        tk.Label(
            filter_frame,
            text="Hasta:",
            font=self.label_font,
            bg=self.bg_color,
            fg=self.fg_color
        ).pack(side="left", padx=5)

        date_to_entry = ttk.Entry(
            filter_frame,
            textvariable=self.date_to_var,
            width=10,
            font=self.entry_font
        )
        date_to_entry.pack(side="left", padx=5)

        # Botones de búsqueda
        ttk.Button(
            filter_frame,
            text="🔍 Buscar",
            command=self.controller.buscar_solicitudes
        ).pack(side="left", pady=(0, 8), padx=5)

        ttk.Button(
            filter_frame,
            text="🔄 Limpiar",
            command=self.controller.limpiar_filtros
        ).pack(side="left", pady=(0, 8), padx=5)

        # Tabla principal de solicitudes
        columns = ("Nro", "Fecha", "Departamento",
                   "Solicitante", "Referencia", "Responsable")
        col_widths = [50, 120, 150, 150, 200, 150]

        table_frame, self.tree = self.create_table(
            main_container, columns, col_widths, height=15)
        table_frame.pack(fill="both", expand=True, pady=10)

        return self.tree

    def cargar_departamentos_combo(self, departamentos):
        """Cargar departamentos en el combobox"""
        # ✅ USAR set_completion_list en lugar de asignar directamente los values
        departamentos_list = [d[1] for d in departamentos]
        self.dept_combo.set_completion_list(departamentos_list)

    def actualizar_tabla_solicitudes(self, solicitudes):
        """Actualizar la tabla con las solicitudes"""
        self.tree.delete(*self.tree.get_children())

        for solicitud in solicitudes:
            self.tree.insert("", "end", values=(
                solicitud[0],  # Número secuencial
                solicitud[1],  # fecha
                solicitud[2],  # departamento
                solicitud[3],  # solicitante
                solicitud[4] if solicitud[4] else 'N/A',  # referencia/memo
                solicitud[5],  # responsable
                solicitud[6]   # ID real (oculto)
            ))

    def obtener_filtros(self):
        """Obtener los valores actuales de los filtros"""
        return {
            'search_text': self.search_var.get(),
            'dept_filter': self.dept_var.get(),
            'date_from': self.date_from_var.get(),
            'date_to': self.date_to_var.get()
        }

    def limpiar_filtros(self):
        """Limpiar todos los filtros"""
        self.search_var.set("")
        self.dept_var.set("")
        self.date_from_var.set("")
        self.date_to_var.set("")

    def obtener_solicitud_seleccionada(self):
        """Obtener la solicitud seleccionada en la tabla"""
        return self.get_selected_table_item(self.tree)

    def mostrar_formulario_nueva_entrega(self, departamentos, solicitantes, current_user):
        """Mostrar formulario para nueva entrega"""
        form_window = self.create_modal_window(
            self.app, "Registrar Nueva Entrega", "780x750")

        # Frame principal para datos básicos
        basic_frame = self.create_form_frame(
            form_window, "Datos de la Entrega")
        basic_frame.pack(fill="x", padx=10, pady=5)

        # ✅ CORREGIR: Usar AutocompleteCombobox para todos los combobox
        # Variables para los combobox
        selected_departamento = tk.StringVar()
        selected_solicitante = tk.StringVar()
        selected_category = tk.StringVar()
        selected_product = tk.StringVar()

        # Departamento (AutocompleteCombobox) + botón de agregar
        tk.Label(
            basic_frame,
            text="Departamento:",
            font=self.form_label_font,
            bg=self.bg_color,
            fg=self.fg_color
        ).grid(row=0, column=0, padx=5, pady=5, sticky="e")

        dept_combo = AutocompleteCombobox(  # ✅ Cambiar a AutocompleteCombobox
            basic_frame,
            textvariable=selected_departamento,
            font=self.form_entry_font
        )
        dept_combo.grid(row=0, column=1, padx=5, pady=5, sticky="we", ipady=3)
        dept_combo.set_completion_list([d[1] for d in departamentos])

        ttk.Button(
            basic_frame,
            text="➕",
            width=2,
            command=lambda: self.controller.agregar_departamento(dept_combo)
        ).grid(row=0, column=2, padx=(0, 5))

        # Solicitante (AutocompleteCombobox) + botón de agregar
        tk.Label(
            basic_frame,
            text="Solicitante:",
            font=self.form_label_font,
            bg=self.bg_color,
            fg=self.fg_color
        ).grid(row=1, column=0, padx=5, pady=5, sticky="e")

        sol_combo = AutocompleteCombobox(  # ✅ Cambiar a AutocompleteCombobox
            basic_frame,
            textvariable=selected_solicitante,
            font=self.form_entry_font
        )
        sol_combo.grid(row=1, column=1, padx=5, pady=5, sticky="we", ipady=3)
        sol_combo.set_completion_list(
            [f"{s[1]} ({s[2]})" for s in solicitantes])

        ttk.Button(
            basic_frame,
            text="➕",
            width=2,
            command=lambda: self.controller.agregar_solicitante(
                sol_combo, dept_combo)
        ).grid(row=1, column=2, padx=(0, 5))

        # Responsable de la entrega (label de solo lectura)
        nombre_responsable = self.obtener_nombre_usuario(current_user)
        resp_entrega_label = tk.Label(
            basic_frame,
            text=nombre_responsable,
            font=self.form_entry_font,
            bg=self.bg_color,
            fg=self.fg_color
        )
        resp_entrega_label.grid(row=2, column=1, padx=5, pady=5, sticky="w")
        tk.Label(
            basic_frame,
            text="Responsable Entrega:",
            font=self.form_label_font,
            bg=self.bg_color,
            fg=self.fg_color
        ).grid(row=2, column=0, padx=5, pady=5, sticky="e")

        # Referencia/Memo
        tk.Label(
            basic_frame,
            text="Referencia/Memo:",
            font=self.form_label_font,
            bg=self.bg_color,
            fg=self.fg_color
        ).grid(row=3, column=0, padx=5, pady=5, sticky="e")

        memo_entry = ttk.Entry(basic_frame, font=self.form_entry_font)
        memo_entry.grid(row=3, column=1, padx=5, pady=5, sticky="we", ipady=3)

        # Auto-seleccionar usuario actual como solicitante si existe
        if current_user:
            for i, s in enumerate(solicitantes):
                if s[1] == nombre_responsable:
                    sol_combo.current(i)
                    break

        # Frame para selección de productos
        product_frame = self.create_form_frame(
            form_window, "Selección de Productos")
        product_frame.pack(fill="both", expand=True, padx=10, pady=5)

        # Filtros de productos
        filter_frame = tk.Frame(product_frame, bg=self.bg_color)
        filter_frame.pack(fill="x", pady=5)

        tk.Label(
            filter_frame,
            text="Categoría:",
            font=self.form_label_font,
            bg=self.bg_color,
            fg=self.fg_color
        ).pack(side="left", padx=5)

        category_combo = AutocompleteCombobox(  # ✅ Cambiar a AutocompleteCombobox
            filter_frame,
            textvariable=selected_category,
            font=self.form_entry_font
        )
        category_combo.pack(side="left", padx=5)

        tk.Label(
            filter_frame,
            text="Producto:",
            font=self.form_label_font,
            bg=self.bg_color,
            fg=self.fg_color
        ).pack(side="left", padx=5)

        product_combo = AutocompleteCombobox(  # ✅ Cambiar a AutocompleteCombobox
            filter_frame,
            textvariable=selected_product,
            font=self.form_entry_font
        )
        product_combo.pack(side="left", padx=5)

        # Detalles del producto seleccionado (alineados en una sola fila con grid)
        detail_frame = tk.Frame(product_frame, bg=self.bg_color)
        detail_frame.pack(fill="x", pady=5)

        # Configurar columnas para que se expandan
        for col in range(8):
            detail_frame.columnconfigure(col, weight=1)

        tk.Label(
            detail_frame,
            text="Estado:",
            font=self.form_label_font,
            bg=self.bg_color,
            fg=self.fg_color
        ).grid(row=0, column=0, padx=5, pady=2, sticky="ew")

        estado_label = tk.Label(
            detail_frame,
            text="N/A",
            font=self.form_entry_font,
            bg=self.bg_color,
            fg=self.fg_color
        )
        estado_label.grid(row=0, column=1, padx=5, pady=2, sticky="ew")

        tk.Label(
            detail_frame,
            text="Stock Disponible:",
            font=self.form_label_font,
            bg=self.bg_color,
            fg=self.fg_color
        ).grid(row=0, column=2, padx=5, pady=2, sticky="ew")

        stock_label = tk.Label(
            detail_frame,
            text="0",
            font=self.form_entry_font,
            bg=self.bg_color,
            fg=self.fg_color
        )
        stock_label.grid(row=0, column=3, padx=5, pady=2, sticky="ew")

        tk.Label(
            detail_frame,
            text="Ubicación:",
            font=self.form_label_font,
            bg=self.bg_color,
            fg=self.fg_color
        ).grid(row=0, column=4, padx=5, pady=2, sticky="ew")

        ubicacion_label = tk.Label(
            detail_frame,
            text="N/A",
            font=self.form_entry_font,
            bg=self.bg_color,
            fg=self.fg_color
        )
        ubicacion_label.grid(row=0, column=5, padx=5, pady=2, sticky="ew")

        tk.Label(
            detail_frame,
            text="Cantidad a Entregar:",
            font=self.form_label_font,
            bg=self.bg_color,
            fg=self.fg_color
        ).grid(row=0, column=6, padx=5, pady=2, sticky="ew")

        qty_entry = ttk.Entry(detail_frame, width=5, font=self.form_entry_font)
        qty_entry.grid(row=0, column=7, padx=5, pady=2, sticky="ew")

        # Botones para agregar/quitar productos
        btn_frame = tk.Frame(product_frame, bg=self.bg_color)
        btn_frame.pack(fill="x", pady=5)

        ttk.Button(
            btn_frame,
            text="Agregar Producto",
            command=lambda: self.controller.agregar_producto_form(
                selected_product.get(),
                qty_entry.get(),
                output_tree,
                stock_label,
                ubicacion_label,
                qty_entry
            )
        ).pack(side="left", padx=5)

        ttk.Button(
            btn_frame,
            text="Quitar Producto",
            command=lambda: self.controller.quitar_producto_form(
                output_tree, stock_label)
        ).pack(side="left", padx=5)

        # Tabla de productos a entregar
        columns = ("Producto", "Cantidad", "Ubicación")
        table_frame, output_tree = self.create_table(
            product_frame, columns, [200, 100, 150], height=5)
        table_frame.pack(fill="both", expand=True)

        # Botones finales
        btn_bottom_frame = tk.Frame(form_window, bg=self.bg_color)
        btn_bottom_frame.pack(fill="x", pady=10)

        save_btn = ttk.Button(
            btn_bottom_frame,
            text="Registrar Entrega",
            command=lambda: self.controller.registrar_entrega_form(
                dept_combo, sol_combo, resp_entrega_label, memo_entry,
                output_tree, departamentos, solicitantes, form_window
            )
        )
        save_btn.pack(side="left", padx=10, ipadx=8, ipady=4)

        cancel_btn = ttk.Button(
            btn_bottom_frame,
            text="Cancelar",
            command=form_window.destroy
        )
        cancel_btn.pack(side="right", padx=10, ipadx=8, ipady=4)

        # Centrar ventana

        self.center_window(form_window)

        return {
            'window': form_window,
            'category_combo': category_combo,
            'product_combo': product_combo,
            'estado_label': estado_label,
            'stock_label': stock_label,
            'ubicacion_label': ubicacion_label,
            'output_tree': output_tree,
            'qty_entry': qty_entry,
            'selected_category': selected_category,
            'selected_product': selected_product,
            'selected_departamento': selected_departamento,
            'selected_solicitante': selected_solicitante,
            # Expose the actual combobox widgets so the controller can update them
            'dept_combo': dept_combo,
            'sol_combo': sol_combo
        }

    def actualizar_detalles_producto(self, estado, stock, ubicacion, estado_label, stock_label, ubicacion_label):
        """Actualizar los detalles del producto en la interfaz"""
        estado_label.config(text=estado)
        stock_label.config(text=str(stock))
        ubicacion_label.config(text=ubicacion)

    def cargar_categorias_combo(self, categorias, category_combo):
        """Cargar categorías en el combobox"""
        # ✅ USAR set_completion_list en lugar de asignar directamente los values
        categorias_list = [c[1] for c in categorias]
        category_combo.set_completion_list(categorias_list)

    def cargar_productos_combo(self, productos, product_combo):
        """Cargar productos en el combobox"""
        # ✅ USAR set_completion_list en lugar de asignar directamente los values
        productos_list = [p[1] for p in productos]
        product_combo.set_completion_list(productos_list)

    def mostrar_detalles_solicitud(self, solicitud, productos):
        """Mostrar ventana con detalles de la solicitud"""
        detail_window = self.create_modal_window(
            self.app, f"Detalles de Solicitud - {solicitud[0]}", "600x680")

        # Frame para información básica
        info_frame = self.create_form_frame(
            detail_window, "Información de la Solicitud")
        info_frame.pack(fill="x", padx=10, pady=5)

        # Mostrar información en un formato más organizado
        info_text = self.crear_texto(info_frame, height=8, wrap="word")
        info_text.pack(fill="both", expand=True)

        info_content = f"""
        ID: {solicitud[0]}
        Fecha: {solicitud[1].strftime('%d/%m/%Y %H:%M')}
        Departamento: {solicitud[3]}
        Solicitante: {solicitud[4]} 
        Cédula: {solicitud[5]}
        Responsable Entrega: {solicitud[6]}
        Referencia: {solicitud[2] if solicitud[2] else 'N/A'}
        """
        info_text.insert("1.0", info_content.strip())
        info_text.config(state="disabled")

        # Tabla de productos
        product_frame = self.create_form_frame(
            detail_window, "Productos Entregados")
        product_frame.pack(fill="both", expand=True, padx=10, pady=5)

        columns = ("Código", "Producto", "Cantidad")
        table_frame, detail_tree = self.create_table(
            product_frame, columns, [100, 150, 100], height=10)
        table_frame.pack(fill="both", expand=True)

        # Cargar detalles de productos
        for producto in productos:
            detail_tree.insert("", "end", values=(
                producto[2], producto[0], producto[1]))

        # Botón para cerrar
        ttk.Button(
            detail_window,
            text="Cerrar",
            command=detail_window.destroy
        ).pack(padx=10, pady=10, side="right")

        self.center_window(detail_window)

    def mostrar_formulario_departamento(self):
        """Mostrar formulario para agregar nuevo departamento"""
        ventana = self.create_modal_window(
            self.app, "Agregar Departamento", "350x240")  # Aumenté un poco la altura

        # ✅ AGREGAR: Frame con borde y título
        form_frame = self.create_form_frame(ventana, "Agregar Departamento")
        form_frame.pack(fill="both", expand=True, padx=10, pady=10)

        tk.Label(
            form_frame,  # ✅ Cambiar ventana por form_frame
            text="Nombre del Departamento:",
            font=self.form_label_font,
            bg=self.bg_color,
            fg=self.fg_color
        ).pack(pady=10)

        # ✅ Cambiar ventana por form_frame
        entry = ttk.Entry(form_frame, font=self.form_entry_font)
        entry.pack(pady=5, fill="x", padx=20)

        btn_frame, save_btn, cancel_btn = self.create_form_buttons(
            form_frame)  # ✅ Cambiar ventana por form_frame
        btn_frame.pack(pady=10)

        save_btn.configure(
            text="Guardar",
            command=lambda: self.controller.guardar_departamento(
                entry.get().strip(), ventana)
        )
        cancel_btn.configure(command=ventana.destroy)

        self.center_window(ventana)
        return entry

    def mostrar_formulario_solicitante(self, departamentos, dept_seleccionado):
        """Mostrar formulario para agregar nuevo solicitante"""
        ventana = self.create_modal_window(
            self.app, "Agregar Solicitante", "400x300")  # Aumenté un poco la altura

        # ✅ AGREGAR: Frame con borde y título
        form_frame = self.create_form_frame(ventana, "Agregar Solicitante")
        form_frame.pack(fill="both", expand=True, padx=10, pady=10)

        # Configurar grid para el form_frame
        form_frame.columnconfigure(1, weight=1)

        tk.Label(
            form_frame,  # ✅ Cambiar ventana por form_frame
            text="Cédula:",
            font=self.form_label_font,
            bg=self.bg_color,
            fg=self.fg_color
        ).grid(row=0, column=0, padx=10, pady=10, sticky="e")

        # ✅ Cambiar ventana por form_frame
        cedula_entry = ttk.Entry(form_frame, font=self.form_entry_font)
        cedula_entry.grid(row=0, column=1, padx=10, pady=10, sticky="we")

        tk.Label(
            form_frame,  # ✅ Cambiar ventana por form_frame
            text="Nombre:",
            font=self.form_label_font,
            bg=self.bg_color,
            fg=self.fg_color
        ).grid(row=1, column=0, padx=10, pady=10, sticky="e")

        # ✅ Cambiar ventana por form_frame
        nombre_entry = ttk.Entry(form_frame, font=self.form_entry_font)
        nombre_entry.grid(row=1, column=1, padx=10, pady=10, sticky="we")

        tk.Label(
            form_frame,  # ✅ Cambiar ventana por form_frame
            text="Departamento:",
            font=self.form_label_font,
            bg=self.bg_color,
            fg=self.fg_color
        ).grid(row=2, column=0, padx=10, pady=10, sticky="e")

        dept_combo = AutocompleteCombobox(  # ✅ Cambiar a AutocompleteCombobox
            form_frame,  # ✅ Cambiar ventana por form_frame
            font=self.form_entry_font
        )
        # ✅ Configurar autocompletado
        dept_combo.set_completion_list([d[1] for d in departamentos])
        dept_combo.grid(row=2, column=1, padx=10, pady=10, sticky="we")

        # Preseleccionar departamento si existe
        if dept_seleccionado:
            dept_combo.set(dept_seleccionado)

        btn_frame, save_btn, cancel_btn = self.create_form_buttons(
            form_frame)  # ✅ Cambiar ventana por form_frame
        btn_frame.grid(row=3, columnspan=2, pady=20)

        save_btn.configure(
            text="Guardar",
            command=lambda: self.controller.guardar_solicitante(
                cedula_entry.get().strip(),
                nombre_entry.get().strip(),
                dept_combo.get(),
                ventana
            )
        )
        cancel_btn.configure(command=ventana.destroy)

        self.center_window(ventana)

        return {
            'cedula_entry': cedula_entry,
            'nombre_entry': nombre_entry,
            'dept_combo': dept_combo
        }
