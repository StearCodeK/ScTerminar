# views/product_view.py
import tkinter as tk
from tkinter import ttk
from views.base_view import BaseView, AutocompleteCombobox


class ProductView(BaseView):
    def __init__(self, frame, app):
        super().__init__(frame, app)
        self.controller = None

    def set_controller(self, controller):
        """Establecer el controlador para esta vista"""
        self.controller = controller

    def setup_inventory_tab(self, frame):
        """Configurar pestaña de inventario"""
        # Frame principal
        main_container = self.create_main_container(frame)
        main_container.pack(fill="both", expand=True, padx=0, pady=0)

        # --- CONTENEDOR HORIZONTAL PARA BOTONES ---
        top_frame = self.create_section_frame(main_container)
        top_frame.pack(fill="x", padx=10, pady=(0, 0))

        # Botones de acción
        actions = [
            ("➕ Nuevo", self.controller.new_product),
            ("✏️ Editar", self.controller.edit_selected_product),
            ("🗑️ Eliminar", self.controller.delete_selected_product),
            ("📥 Agregar Stock", self.controller.show_add_stock_form),
            ("📤 Exportar", self.controller.export_inventory)
        ]
        button_frame, action_buttons = self.create_action_buttons(
            top_frame, actions)
        button_frame.pack(side="left", pady=(0, 5))

        # --- FRAME DE FILTROS ---
        filtros_frame = tk.LabelFrame(
            main_container, text="Filtros", font=self.label_font, bg=self.bg_color, fg=self.fg_color)
        filtros_frame.pack(fill="x", padx=10, pady=(5, 5))

        # --- FILA 1: BUSCADOR ---
        buscador_frame = tk.Frame(filtros_frame, bg=self.bg_color)
        buscador_frame.pack(fill="x", padx=5, pady=(8, 2))
        tk.Label(buscador_frame, text="Buscar por producto:",
                 font=self.label_font, bg=self.bg_color, fg=self.fg_color).pack(side="left", padx=5)
        self.search_entry = ttk.Entry(
            buscador_frame, width=30, font=self.entry_font)
        self.search_entry.pack(side="left", padx=5)
        self.search_entry.bind(
            "<KeyRelease>", lambda e: self.controller.search_products())

        # --- FILA 2: COMBOBOX Y BOTÓN ---
        filtros_inner_frame = tk.Frame(filtros_frame, bg=self.bg_color)
        filtros_inner_frame.pack(fill="x", padx=5, pady=(2, 8))

        # ✅ USAR AutocompleteCombobox EN TODOS LOS FILTROS
        categoria_frame = tk.Frame(filtros_inner_frame, bg=self.bg_color)
        categoria_frame.pack(side="left", padx=5)
        tk.Label(categoria_frame, text="Categoría:", font=self.label_font,
                 bg=self.bg_color, fg=self.fg_color).pack(side="left", padx=5)
        self.categoria_combo = AutocompleteCombobox(
            categoria_frame, width=15, font=self.entry_font)
        self.categoria_combo.pack(side="left", padx=5)
        self.categoria_combo.set("Todas")

        marca_frame = tk.Frame(filtros_inner_frame, bg=self.bg_color)
        marca_frame.pack(side="left", padx=5)
        tk.Label(marca_frame, text="Marca:", font=self.label_font,
                 bg=self.bg_color, fg=self.fg_color).pack(side="left", padx=5)
        self.marca_combo = AutocompleteCombobox(
            marca_frame, width=15, font=self.entry_font)
        self.marca_combo.pack(side="left", padx=5)
        self.marca_combo.set("Todas")

        estado_frame = tk.Frame(filtros_inner_frame, bg=self.bg_color)
        estado_frame.pack(side="left", padx=5)
        tk.Label(estado_frame, text="Estado:", font=self.label_font,
                 bg=self.bg_color, fg=self.fg_color).pack(side="left", padx=5)
        self.estado_combo = AutocompleteCombobox(
            estado_frame, width=15, font=self.entry_font)
        self.estado_combo.pack(side="left", padx=5)
        self.estado_combo.set("Todos")

        # Botón aplicar filtros
        self.apply_btn = ttk.Button(filtros_inner_frame, text="Aplicar Filtros", style="Accent.TButton",
                                    command=self.controller.apply_filters)
        self.apply_btn.pack(side="left", padx=10)

        # Botón limpiar filtros
        self.clear_btn = ttk.Button(filtros_inner_frame, text="Limpiar Filtros", style="TButton",
                                    command=self._clear_filters_action)
        self.clear_btn.pack(side="left", padx=0)

        # --- TABLA ---
        columns = ("Nro", "Producto", "Marca", "Categoría",
                   "Código", "Stock", "Stock (m)", "Ubicación", "Estado")
        col_widths = [50, 150, 100, 100, 80, 60, 70, 80, 80]  # Ajusta el ancho si es necesario

        table_frame, self.tree = self.create_table(
            main_container, columns, col_widths, height=15)
        table_frame.pack(fill="both", expand=True, padx=10, pady=(0, 10))

        return self

    def _clear_filters_action(self):
        """Llama al controlador si tiene clear_filters, si no, limpia localmente."""
        if self.controller and hasattr(self.controller, 'clear_filters'):
            self.controller.clear_filters()
        else:
            self.clear_filters()

    def get_search_term(self):
        """Obtener término de búsqueda"""
        return self.search_entry.get().strip()

    def clear_filters(self):
        """Restablecer filtros a valores por defecto y refrescar tabla"""
        self.search_entry.delete(0, tk.END)
        self.categoria_combo.set("Todas")
        self.marca_combo.set("Todas")
        self.estado_combo.set("Todos")
        if self.controller:
            self.controller.apply_filters()

    def get_filters(self):
        """Obtener valores de filtros"""
        return {
            'categoria': self.categoria_combo.get(),
            'marca': self.marca_combo.get(),
            'estado': self.estado_combo.get()
        }

    def refresh_table(self, data):
        """Refrescar tabla con nuevos datos"""
        self.tree.delete(*self.tree.get_children())
        for i, item in enumerate(data, start=1):
            # Reemplaza el primer elemento por el número de fila
            fila = (i,) + item[1:]
            self.tree.insert("", "end", values=fila, tags=(item[0],))

    def get_selected_product(self):
        """Obtener producto seleccionado"""
        selected_item = self.tree.selection()
        if not selected_item:
            return None
        return self.tree.item(selected_item[0])

    def update_categories_combo(self, categories):
        """Actualizar combobox de categorías SOLO CON ACTIVAS"""
        categorias_list = ["Todas"] + [c[1] for c in categories]
        self.categoria_combo.set_completion_list(categorias_list)

    def update_marcas_combo(self, marcas):
        """Actualizar combobox de marcas SOLO CON ACTIVAS"""
        marcas_list = ["Todas"] + [m[1] for m in marcas]
        self.marca_combo.set_completion_list(marcas_list)

    def show_product_form(self, product_id=None):
        """Mostrar formulario de producto"""
        form_window = self.create_modal_window(
            self.app,
            "Nuevo Producto" if not product_id else "Editar Producto",
            "420x480"  # Aumenté la altura para el nuevo campo
        )

        # Frame principal del formulario
        basic_frame = self.create_form_frame(form_window, "Datos del Producto")
        basic_frame.pack(fill="x", padx=10, pady=5)

        entries = {}
        buttons = {}

        # Configurar grid
        basic_frame.columnconfigure(1, weight=1)

        # Campos del formulario - AGREGADO STOCK MÍNIMO
        fields = [
            ("Código:", "entry", None),
            ("Producto:", "entry", None),
            ("Marca:", "combobox", []),
            ("Categoría:", "combobox", []),
            ("Stock inicial:", "entry", None),
            ("Stock mínimo:", "entry", None),  # NUEVO CAMPO
            ("Ubicación:", "combobox", []),
            ("Estado:", "combobox", ["disponible", "stock bajo", "agotado", "reservado"])
        ]

        for i, (label, field_type, options) in enumerate(fields):
            # Etiqueta
            label_widget = tk.Label(
                basic_frame,
                text=label,
                font=self.form_label_font,
                bg=self.bg_color,
                fg=self.fg_color
            )
            label_widget.grid(row=i, column=0, padx=5, pady=5, sticky="e")

            # Campo
            if field_type == "entry":
                field_widget = ttk.Entry(
                    basic_frame, font=self.form_entry_font)
                field_widget.grid(row=i, column=1, padx=5,
                                pady=5, sticky="we", ipady=3)
            elif field_type == "combobox":
                field_widget = AutocompleteCombobox(
                    basic_frame, font=self.form_entry_font)
                if options:
                    field_widget.set_completion_list(options)
                field_widget.grid(row=i, column=1, padx=5,
                                pady=5, sticky="we", ipady=3)

            entries[label] = field_widget

            # Botones adicionales para marcas, categorías, ubicaciones
            if label in ["Marca:", "Categoría:", "Ubicación:"]:
                btn = ttk.Button(basic_frame, text="➕",
                                width=2, style="TButton")
                btn.grid(row=i, column=2, padx=(0, 5))
                buttons[label] = btn

        # 🔒 BLOQUEAR STOCK INICIAL SI ES EDICIÓN
        if product_id:
            entries["Stock inicial:"].config(state="disabled")
            self.create_tooltip(entries["Stock inicial:"],
                                "El stock inicial no se puede editar. Use 'Agregar Stock' para modificar el inventario.")

        # Botones principales
        btn_frame, save_btn, cancel_btn = self.create_form_buttons(form_window)
        btn_frame.pack(fill="x", pady=10)
        cancel_btn.configure(command=form_window.destroy)

        # Centrar ventana
        self.center_window(form_window)

        return form_window, entries, buttons, save_btn

    def create_tooltip(self, widget, text):
        """Crear un tooltip para un widget"""
        def on_enter(event):
            tooltip = tk.Toplevel()
            tooltip.wm_overrideredirect(True)
            tooltip.wm_geometry(f"+{event.x_root+10}+{event.y_root+10}")
            label = tk.Label(tooltip, text=text,
                             background="yellow", relief="solid", borderwidth=1)
            label.pack()
            widget.tooltip = tooltip

        def on_leave(event):
            if hasattr(widget, 'tooltip'):
                widget.tooltip.destroy()

        widget.bind("<Enter>", on_enter)
        widget.bind("<Leave>", on_leave)

    def show_add_stock_form(self, product_name, current_stock):
        """Mostrar formulario para agregar stock"""
        form_window = self.create_modal_window(
            self.app,
            f"Agregar Stock - {product_name}"
        )

        # Frame principal
        main_frame = self.create_form_frame(form_window, "Agregar Stock")
        main_frame.pack(fill="both", expand=True, padx=16, pady=12)

        # Información del producto
        tk.Label(main_frame, text=f"Producto: {product_name}",
                 font=self.form_label_font, bg=self.bg_color, fg=self.fg_color).pack(anchor="w")
        tk.Label(main_frame, text=f"Stock actual: {current_stock}",
                 font=self.form_label_font, bg=self.bg_color, fg=self.fg_color).pack(anchor="w")
        tk.Label(main_frame, text="Cantidad a agregar:",
                 font=self.form_label_font, bg=self.bg_color, fg=self.fg_color).pack(anchor="w", pady=(10, 0))

        # Campo de cantidad
        qty_entry = ttk.Entry(main_frame, font=self.form_entry_font)
        qty_entry.pack(fill="x", pady=5, ipady=3)

        # Botones
        btn_frame, add_btn, cancel_btn = self.create_form_buttons(main_frame)
        btn_frame.pack(fill="x", pady=15)
        add_btn.configure(text="Agregar")
        cancel_btn.configure(command=form_window.destroy)

        self.center_window(form_window)

        return form_window, qty_entry, add_btn

    def show_new_value_form(self, table, parent_window=None):
        """Mostrar formulario para agregar nuevo valor a tabla relacionada

        Args:
            table: nombre de la tabla (marcas, categorias, ubicaciones)
            parent_window: ventana padre que se mantendrá abierta (opcional)
        """
        # Traducir el nombre de la tabla para el título
        nombres_tabla = {
            'marcas': 'Marca',
            'categorias': 'Categoría',
            'ubicaciones': 'Ubicación'
        }

        nombre_tabla = nombres_tabla.get(table, table.capitalize())

        form_window = self.create_modal_window(
            self.app,
            f"Agregar {nombre_tabla}"
        )

        # Guardar referencia a la ventana padre para mantenerla abierta
        if parent_window:
            form_window.parent_window = parent_window

        # Frame principal
        main_frame = self.create_form_frame(
            form_window, f"Nueva {nombre_tabla}")
        main_frame.pack(fill="both", expand=True)

        # Campo de nombre
        tk.Label(main_frame, text="Nombre:",
                 font=self.form_label_font, bg=self.bg_color, fg=self.fg_color).pack(pady=10)

        entry = ttk.Entry(main_frame, font=self.form_entry_font)
        entry.pack(pady=10, padx=20, fill="x", ipady=3)

        # Enfocar el campo de entrada automáticamente
        entry.focus_set()

        # Botones
        btn_frame, save_btn, cancel_btn = self.create_form_buttons(main_frame)
        btn_frame.pack(pady=10)

        # Configurar comando de Enter para guardar
        entry.bind('<Return>', lambda e: save_btn.invoke())

        # Solo cerrar esta ventana modal, no la ventana padre
        cancel_btn.configure(command=form_window.destroy)

        self.center_window(form_window)

        return form_window, entry, save_btn
