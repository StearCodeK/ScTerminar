import tkinter as tk
from tkinter import ttk
from views.base_view import BaseView


class SupplierView(BaseView):
    def __init__(self, frame, app):
        super().__init__(frame, app)
        self.controller = None

    def set_controller(self, controller):
        self.controller = controller

    def setup_suppliers_tab(self):
        """Configura el contenido de la pestaña de proveedores"""
        # Limpiar frame
        for widget in self.frame.winfo_children():
            widget.destroy()

        # Contenedor principal
        main_container = self.create_main_container(self.frame)
        main_container.pack(fill="both", expand=True, padx=10, pady=5)

        # Botones de acciones
        actions = [
            ("➕ Nuevo Proveedor", self.controller.show_supplier_form),
            ("✏️ Editar", self.controller.edit_supplier),
            ("🔍 Detalles", self.controller.show_supplier_details),
            ("🗑️ Eliminar", self.controller.delete_supplier),
            ("📤 Exportar", self.controller.export_suppliers)
        ]
        btn_frame, _ = self.create_action_buttons(main_container, actions)
        btn_frame.pack(fill="x", pady=5)

        # Frame para filtros
        filter_frame = self.create_filter_frame(main_container, "Filtros")
        filter_frame.pack(fill="x", pady=5)

        # Filtro por categoría
        category_frame, self.category_var, self.category_combo = self.create_filter_combo(
            filter_frame,
            "Categoría:",
            [],
            "Todas",
            15
        )
        category_frame.pack(side="left", padx=5)

        # Filtro por valoración
        rating_frame, self.rating_var, self.rating_combo = self.create_filter_combo(
            filter_frame,
            "Valoración:",
            ["Todas", "1 Estrella", "2 Estrellas",
                "3 Estrellas", "4 Estrellas", "5 Estrellas"],
            "Todas",
            12
        )
        rating_frame.pack(side="left", padx=5)

        # Filtro por manejo de precios
        price_frame, self.price_var, self.price_combo = self.create_filter_combo(
            filter_frame,
            "Precios:",
            ["Todos", "Bajo", "Medio", "Alto"],
            "Todos",
            10
        )
        price_frame.pack(side="left", padx=5)

        # Botón de aplicar filtros
        ttk.Button(
            filter_frame,
            text="Aplicar Filtros",
            command=self.apply_filters
        ).pack(side="left", padx=10)

        # Tabla de proveedores
        columns = ("Nro", "Nombre", "Contacto", "Teléfono",
                   "Email", "Valoración", "Precios", "Categorías")
        column_widths = [50, 120, 120, 100, 150, 80, 80, 120]

        table_frame, self.tree = self.create_table(
            main_container,
            columns,
            column_widths,
            height=15
        )
        table_frame.pack(fill="both", expand=True, pady=10)

        # Cargar datos iniciales
        self.controller.load_categories_combobox(
            self.category_combo, add_all_option=True)

    def apply_filters(self):
        """Aplica los filtros seleccionados"""
        category = self.category_var.get()
        rating = self.rating_var.get()
        price = self.price_var.get()
        self.controller.apply_suppliers_filters(category, rating, price)

    def get_selected_supplier(self):
        """Obtiene el proveedor seleccionado en la tabla"""
        return self.get_selected_table_item(self.tree)

    def refresh_table(self, data):
        """Actualiza la tabla con nuevos datos"""
        self.refresh_table_data(self.tree, data)

    def show_supplier_form(self, app, supplier_id=None):
        """Formulario para nuevo proveedor o edición"""
        title = "Nuevo Proveedor" if not supplier_id else "Editar Proveedor"
        form_window = self.create_modal_window(app, title, "600x700")

        # Frame principal del formulario
        main_frame = self.create_form_frame(form_window, "Datos del Proveedor")
        main_frame.pack(fill="both", padx=10, pady=5)

        # Configuración de campos del formulario
        fields_config = [
            ("Nombre:", "entry", None),
            ("Contacto:", "entry", None),
            ("Teléfono:", "entry", None),
            ("Email:", "entry", None),
            ("Dirección:", "entry", None),
            ("Redes Sociales:", "entry", None),
            ("Valoración:", "combobox", [
             "1 Estrella", "2 Estrellas", "3 Estrellas", "4 Estrellas", "5 Estrellas"]),
            ("Manejo de Precios:", "combobox", ["Bajo", "Medio", "Alto"]),
            ("Categorías:", "combobox", None),
        ]

        # Crear campos del formulario
        entries = self.create_form_fields(main_frame, fields_config)

        # Frame para comentarios
        comments_frame = self.create_form_frame(form_window, "Comentarios")
        comments_frame.pack(fill="x", padx=10, pady=5)

        comments_text = self.crear_texto(comments_frame, height=4, wrap="word")
        comments_text.pack(fill="both", expand=True, padx=5, pady=5)
        entries["Comentarios:"] = comments_text

        # Botones del formulario
        btn_frame, save_btn, cancel_btn = self.create_form_buttons(form_window)
        btn_frame.pack(fill="x", pady=10)
        cancel_btn.configure(command=form_window.destroy)

        # Botón para gestionar productos (solo si es edición)
        if supplier_id:
            manage_btn = ttk.Button(
                btn_frame, text="📦 Gestionar Productos", style="TButton")
            manage_btn.pack(side="left", padx=10, ipadx=8, ipady=4)
            entries["manage_btn"] = manage_btn

        # Centrar ventana
        self.center_window(form_window)

        return form_window, entries, save_btn

    def show_supplier_details_view(self, supplier_data, categories, products):
        """Muestra la ventana de detalles del proveedor"""
        supplier_name = supplier_data[1] if supplier_data and len(
            supplier_data) > 1 else "Proveedor"
        detail_window = self.create_modal_window(
            self.frame,
            f"Detalles del Proveedor: {supplier_name}",
            "650x650"
        )

        # Frame principal
        main_frame = self.create_form_frame(
            detail_window, "Información del Proveedor")
        main_frame.pack(fill="both", expand=True, padx=10, pady=10)

        # Información del proveedor
        labels = [
            "Nombre:", "Contacto:", "Teléfono:", "Email:",
            "Dirección:", "Redes Sociales:", "Valoración:",
            "Manejo de Precios:", "Categorías:", "Comentarios:"
        ]

        for i, label in enumerate(labels[:9]):
            # Etiqueta
            tk.Label(
                main_frame,
                text=label,
                font=self.form_label_font,
                bg=self.bg_color,
                fg=self.fg_color
            ).grid(row=i, column=0, sticky="e", padx=5, pady=2)

            # Valor
            value = self._get_supplier_field_value(
                supplier_data, i, categories)
            tk.Label(
                main_frame,
                text=value,
                font=self.form_entry_font,
                bg=self.bg_color,
                fg=self.fg_color
            ).grid(row=i, column=1, sticky="w", pady=2)

        # Comentarios
        self._create_comments_section(main_frame, supplier_data, 9)

        # Productos
        self._create_products_section(main_frame, products, 10)

        # Botón cerrar
        ttk.Button(
            main_frame,
            text="Cerrar",
            command=detail_window.destroy,
            style="TButton"
        ).grid(row=11, column=1, pady=20, sticky="e")

        # Centrar ventana
        self.center_window(detail_window)

    def show_supplier_products_management(self, supplier_id, supplier_name, available_products, current_products):
        """Muestra la ventana de gestión de productos del proveedor"""
        products_window = self.create_modal_window(
            self.frame,
            f"Gestionar Productos: {supplier_name}",
            "600x500"
        )

        # Frame principal
        main_frame = self.create_form_frame(
            products_window, "Gestión de Productos")
        main_frame.pack(fill="both", expand=True, padx=10, pady=10)

        # Proveedor actual
        tk.Label(main_frame, text=f"Proveedor: {supplier_name}",
                 font=self.form_label_font, bg=self.bg_color, fg=self.fg_color).pack(pady=(0, 10))

        # Frame para agregar productos
        add_frame = tk.Frame(main_frame, bg=self.bg_color)
        add_frame.pack(fill="x", pady=10)

        tk.Label(add_frame, text="Agregar producto:",
                 font=self.form_label_font, bg=self.bg_color, fg=self.fg_color).pack(side="left", padx=5)

        # Combobox para productos disponibles
        product_combo = ttk.Combobox(
            add_frame, state="readonly", width=30, font=self.form_entry_font)
        product_combo.pack(side="left", padx=5)
        product_combo['values'] = available_products

        # Lista de productos actuales
        tk.Label(main_frame, text="Productos asociados:",
                 font=self.form_label_font, bg=self.bg_color, fg=self.fg_color).pack(anchor="w", pady=(10, 5))

        tree_frame = tk.Frame(main_frame, bg=self.bg_color)
        tree_frame.pack(fill="both", expand=True)

        tree = ttk.Treeview(tree_frame, columns=(
            "Producto", "Categoría"), show="headings", height=10)
        tree.heading("Producto", text="Producto")
        tree.heading("Categoría", text="Categoría")
        tree.column("Producto", width=200)
        tree.column("Categoría", width=150)
        tree.pack(side="left", fill="both", expand=True)

        scrollbar = ttk.Scrollbar(
            tree_frame, orient="vertical", command=tree.yview)
        tree.configure(yscrollcommand=scrollbar.set)
        scrollbar.pack(side="right", fill="y")

        # Cargar productos actuales
        for product, category in current_products:
            tree.insert("", "end", values=(product, category))

        # Frame para botones
        btn_frame = tk.Frame(main_frame, bg=self.bg_color)
        btn_frame.pack(fill="x", pady=10)

        # Centrar ventana
        self.center_window(products_window)

        return products_window, product_combo, tree, btn_frame

    def get_selected_product_from_tree(self, tree):
        """Obtiene el producto seleccionado en el treeview"""
        selected = tree.selection()
        return selected[0] if selected else None

    def refresh_products_tree(self, tree, products):
        """Actualiza el treeview de productos"""
        tree.delete(*tree.get_children())
        for product, category in products:
            tree.insert("", "end", values=(product, category))

    def _get_supplier_field_value(self, supplier_data, index, categories):
        """Obtiene el valor formateado de un campo del proveedor"""
        if not supplier_data or index + 1 >= len(supplier_data):
            return "N/A"

        if index == 6:  # Valoración
            rating = supplier_data[7]
            if rating is not None:
                return f"{rating} Estrella{'s' if rating > 1 else ''}"
            return "N/A"
        elif index == 8:  # Categorías
            return ", ".join(categories) if categories else "N/A"
        else:
            return supplier_data[index + 1] if supplier_data[index + 1] else "N/A"

    def _create_comments_section(self, parent, supplier_data, row):
        """Crea la sección de comentarios"""
        tk.Label(
            parent,
            text="Comentarios:",
            font=self.form_label_font,
            bg=self.bg_color,
            fg=self.fg_color
        ).grid(row=row, column=0, sticky="ne", padx=5, pady=2)

        comments_text = tk.Text(
            parent,
            height=5,
            width=50,
            wrap="word",
            font=self.form_entry_font,
            bg=self.bg_color,
            fg=self.fg_color
        )
        comments_text.insert("1.0", supplier_data[9] if supplier_data and len(
            supplier_data) > 9 and supplier_data[9] else "Ninguno")
        comments_text.config(state="disabled")
        comments_text.grid(row=row, column=1, sticky="w", pady=2)

    def _create_products_section(self, parent, products, row):
        """Crea la sección de productos"""
        tk.Label(
            parent,
            text="Productos:",
            font=self.form_label_font,
            bg=self.bg_color,
            fg=self.fg_color
        ).grid(row=row, column=0, sticky="ne", padx=5, pady=5)

        if products:
            products_frame = tk.Frame(parent, bg=self.bg_color)
            products_frame.grid(row=row, column=1, sticky="w")

            for j, (product, category) in enumerate(products):
                tk.Label(
                    products_frame,
                    text=f"• {product} ({category})",
                    font=self.form_entry_font,
                    bg=self.bg_color,
                    fg=self.fg_color
                ).grid(row=j, column=0, sticky="w")
        else:
            tk.Label(
                parent,
                text="Ningún producto asociado",
                font=self.form_entry_font,
                bg=self.bg_color,
                fg=self.fg_color
            ).grid(row=row, column=1, sticky="w")
