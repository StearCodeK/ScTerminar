# views/base_view.py
import tkinter as tk
from tkinter import ttk


class AutocompleteCombobox(ttk.Combobox):
    def __init__(self, parent, **kwargs):
        # Remover state="readonly" si está presente para permitir escritura
        if 'state' in kwargs and kwargs['state'] == 'readonly':
            kwargs['state'] = 'normal'
        super().__init__(parent, **kwargs)
        self._completion_list = []
        self._hits = []
        self.position = 0
        self.bind('<KeyRelease>', self._on_keyrelease)
        self.bind('<FocusIn>', self._on_focusin)
        self.bind('<FocusOut>', self._on_focusout)
        self.bind('<Return>', self._on_return)  # <-- Agrega este binding

    def set_completion_list(self, completion_list):
        self._completion_list = sorted(completion_list, key=str.lower)
        self._hits = []
        self.position = 0
        self['values'] = self._completion_list

    def _on_keyrelease(self, event):
        """Manejar la liberación de teclas para el autocompletado"""
        # Ignorar teclas de navegación y control
        if event.keysym in ('Up', 'Down', 'Left', 'Right', 'Return', 'Tab',
                            'Control_L', 'Control_R', 'Shift_L', 'Shift_R'):
            return

        value = self.get().strip().lower()

        if value:
            # Filtrar valores que CONTENGAN el texto (nombre o cédula)
            self._hits = [item for item in self._completion_list
                          if value in item.lower()]
            if not self._hits:
                self['values'] = ["Sin resultado"]
            else:
                self['values'] = self._hits
        else:
            self['values'] = self._completion_list
            self._hits = []

    def _on_return(self, event):
        """Despliega la lista de coincidencias al presionar Enter"""
        self.event_generate('<Down>')

    def _on_focusin(self, event):
        """Al recibir foco, mostrar todos los valores"""
        self['values'] = self._completion_list
        self._hits = []

    def _on_focusout(self, event):
        """Al perder foco, asegurarse de que el valor sea válido"""
        current_value = self.get()
        if current_value == "Sin resultado":
            self.set('')
        elif current_value and current_value not in self._completion_list:
            # Si el valor no está en la lista, limpiarlo
            self.set('')


class AutocompleteComboboxWithScrollbar(ttk.Combobox):
    def __init__(self, parent, **kwargs):
        if 'state' in kwargs and kwargs['state'] == 'readonly':
            kwargs['state'] = 'normal'
        super().__init__(parent, **kwargs)
        self._completion_list = []
        self._hits = []
        self.position = 0
        self.listbox = None
        self.scrollbar = None
        self.bind('<KeyRelease>', self._on_keyrelease)
        self.bind('<FocusIn>', self._on_focusin)
        self.bind('<FocusOut>', self._on_focusout)
        self.bind('<Return>', self._on_return)

    def set_completion_list(self, completion_list):
        self._completion_list = sorted(completion_list, key=str.lower)
        self._hits = []
        self.position = 0
        self['values'] = self._completion_list

    def _on_keyrelease(self, event):
        if event.keysym in ('Up', 'Down', 'Left', 'Right', 'Return', 'Tab',
                            'Control_L', 'Control_R', 'Shift_L', 'Shift_R'):
            return
        value = self.get().strip().lower()
        if value:
            self._hits = [
                item for item in self._completion_list if item.lower().startswith(value)]
            if not self._hits:
                self['values'] = ["Sin resultado"]
                self._show_listbox(["Sin resultado"])
            else:
                self['values'] = self._hits
                self._show_listbox(self._hits)
        else:
            self['values'] = self._completion_list
            self._hits = []
            self._hide_listbox()

    def _show_listbox(self, words):
        self._hide_listbox()
        self.listbox = tk.Listbox(self.master, height=6)
        self.scrollbar = tk.Scrollbar(
            self.master, orient="vertical", command=self.listbox.yview)
        self.listbox.config(yscrollcommand=self.scrollbar.set)
        for w in words:
            self.listbox.insert(tk.END, w)
        x = self.winfo_x()
        y = self.winfo_y() + self.winfo_height()
        self.listbox.place(x=x, y=y, width=self.winfo_width()-15)
        self.scrollbar.place(x=x+self.winfo_width()-15,
                             y=y, width=15, height=108)
        self.listbox.bind("<<ListboxSelect>>", self._select_from_listbox)
        self.listbox.bind("<Right>", self._select_from_listbox)
        self.listbox.bind("<Return>", self._select_from_listbox)
        self.listbox.bind("<Escape>", lambda e: self._hide_listbox())

    def _hide_listbox(self):
        if self.listbox:
            self.listbox.destroy()
            self.listbox = None
        if self.scrollbar:
            self.scrollbar.destroy()
            self.scrollbar = None

    def _select_from_listbox(self, event):
        if self.listbox and self.listbox.curselection():
            value = self.listbox.get(self.listbox.curselection())
            self.set(value)
            self._hide_listbox()
            self.icursor(tk.END)

    def _on_return(self, event):
        self.event_generate('<Down>')

    def _on_focusin(self, event):
        self['values'] = self._completion_list
        self._hits = []

    def _on_focusout(self, event):
        self._hide_listbox()
        current_value = self.get()
        if current_value == "Sin resultado":
            self.set('')
        elif current_value and current_value not in self._completion_list:
            self.set('')


class BaseView:
    def __init__(self, frame, app):
        self.app = app
        self.frame = frame

        # Fuentes unificadas
        if app:
            self.label_font = getattr(app, 'menu_font', ("Segoe UI", 11))
            self.entry_font = getattr(app, 'tree_font', ("Segoe UI", 10))
            self.button_font = getattr(
                app, 'button_font', ("Segoe UI", 10, "bold"))
            self.title_font = getattr(
                app, 'title_font', ("Segoe UI", 12, "bold"))
            self.form_label_font = getattr(app, 'menu_font', ("Segoe UI", 14))
            self.form_entry_font = getattr(app, 'tree_font', ("Segoe UI", 11))
            self.form_button_font = getattr(
                app, 'button_font', ("Segoe UI", 12, "bold"))
        else:
            # Fallback cuando no se pasa app
            self.label_font = ("Segoe UI", 11)
            self.entry_font = ("Segoe UI", 10)
            self.button_font = ("Segoe UI", 10, "bold")
            self.title_font = ("Segoe UI", 12, "bold")
            self.form_label_font = ("Segoe UI", 14)
            self.form_entry_font = ("Segoe UI", 11)
            self.form_button_font = ("Segoe UI", 12, "bold")

        # Colores
        self.bg_color = app.colors.get(
            "background", "white") if app else "white"
        self.fg_color = app.colors.get("text", "black") if app else "black"
        self.primary_color = app.colors.get(
            "primary", "#007acc") if app else "#007acc"

    # ===== MÉTODOS PARA FRAMES =====

    def create_main_container(self, parent, **kwargs):
        """Crea un contenedor principal"""
        return tk.Frame(parent, bg=self.bg_color, **kwargs)

    def create_section_frame(self, parent, **kwargs):
        """Crea un frame de sección"""
        return tk.Frame(parent, bg=self.bg_color, **kwargs)

    def create_form_frame(self, parent, text="", **kwargs):
        """Crea un frame de formulario con LabelFrame"""
        return tk.LabelFrame(
            parent,
            text=text,
            padx=20,
            pady=20,
            font=self.form_label_font,
            bg=self.bg_color,
            fg=self.fg_color,
            **kwargs
        )

    # ===== MÉTODOS PARA FILTROS =====

    def create_filter_frame(self, parent, title="Filtros"):
        """Crea un frame de filtros estandarizado"""
        if title:
            frame = tk.LabelFrame(
                parent,
                text=title,
                bg=self.bg_color,
                fg=self.fg_color,
                font=self.label_font
            )
        else:
            frame = tk.Frame(parent, bg=self.bg_color)
        return frame

    def create_filter_combo(self, parent, label_text, values, default_value="Todos", width=15):
        """Crea un combo de filtro estandarizado"""
        filter_frame = tk.Frame(parent, bg=self.bg_color)

        tk.Label(filter_frame, text=label_text, font=self.label_font,
                 bg=self.bg_color, fg=self.fg_color).pack(side="left", padx=5)

        var = tk.StringVar(value=default_value)
        combo = AutocompleteCombobox(
            filter_frame,
            textvariable=var,
            width=width,  # ✅ REMOVER state="readonly" para permitir escritura
            font=self.entry_font
        )
        combo.set_completion_list(values)
        combo.pack(side="left", padx=5)

        return filter_frame, var, combo

    # ===== MÉTODOS PARA BOTONES =====

    def create_action_buttons(self, parent, actions):
        """Crea botones de acción estandarizados"""
        btn_frame = tk.Frame(parent, bg=self.bg_color)
        buttons = []

        for text, command in actions:
            btn = ttk.Button(btn_frame, text=text, command=command)
            btn.pack(side="left", padx=2)
            buttons.append(btn)

        return btn_frame, buttons

    def create_form_buttons(self, parent):
        """Crea botones de formulario estandarizados (Guardar/Cancelar)"""
        btn_frame = tk.Frame(parent, bg=self.bg_color)

        save_btn = ttk.Button(btn_frame, text="Guardar", style="TButton")
        save_btn.pack(side="left", padx=10, ipadx=8, ipady=4)

        cancel_btn = ttk.Button(btn_frame, text="Cancelar", style="TButton")
        cancel_btn.pack(side="right", padx=10, ipadx=8, ipady=4)

        return btn_frame, save_btn, cancel_btn

    # ===== MÉTODOS PARA TABLAS =====

    def create_table(self, parent, columns, column_widths=None, height=15):
        """Crea una tabla estandarizada"""
        table_frame = tk.Frame(parent, bg=self.bg_color)

        tree = ttk.Treeview(
            table_frame,
            columns=columns,
            show="headings",
            height=height
        )

        # Configurar columnas
        default_widths = [100] * len(columns)
        widths = column_widths or default_widths

        for col, width in zip(columns, widths):
            tree.heading(col, text=col)
            tree.column(col, width=width, minwidth=50)

        # Scrollbar
        scrollbar = ttk.Scrollbar(
            table_frame,
            orient="vertical",
            command=tree.yview
        )
        tree.configure(yscrollcommand=scrollbar.set)

        tree.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        return table_frame, tree

    # ===== MÉTODOS PARA FORMULARIOS =====

    def create_form_field(self, parent, label, field_type, options=None, row=0):
        """Crea un campo de formulario estandarizado"""
        label_widget = tk.Label(
            parent,
            text=label,
            font=self.form_label_font,
            bg=self.bg_color,
            fg=self.fg_color
        )
        label_widget.grid(row=row, column=0, padx=5, pady=5, sticky="e")

        field_widget = None
        if field_type == "entry":
            field_widget = ttk.Entry(parent, font=self.form_entry_font)
            field_widget.grid(row=row, column=1, padx=5,
                              pady=5, sticky="we", ipady=3)
        elif field_type == "combobox":
            field_widget = AutocompleteCombobox(
                parent,
                values=options or [],
                font=self.form_entry_font  # ✅ REMOVER state="readonly"
            )
            field_widget.set_completion_list(options or [])
            field_widget.grid(row=row, column=1, padx=5,
                              pady=5, sticky="we", ipady=3)
        elif field_type == "text":
            field_widget = tk.Text(
                parent,
                height=4,
                font=self.form_entry_font,
                wrap="word"
            )
            field_widget.grid(row=row, column=1, padx=5, pady=5, sticky="we")

        # Configurar weight para que el campo se expanda
        parent.columnconfigure(1, weight=1)

        return field_widget

    def create_form_fields(self, parent, fields_config):
        """Crea múltiples campos de formulario"""
        entries = {}

        for i, (label, field_type, options) in enumerate(fields_config):
            field_widget = self.create_form_field(
                parent, label, field_type, options, i)
            entries[label] = field_widget

        return entries

    # ===== MÉTODOS PARA VENTANAS =====

    def create_modal_window(self, parent, title, size=None):
        """Crea una ventana modal estandarizada"""
        window = tk.Toplevel(parent)
        window.title(title)
        window.resizable(False, False)
        window.configure(bg=self.bg_color)
        window.grab_set()  # Hacerla modal

        if size:
            window.geometry(size)

        return window

    def center_window(self, window):
        """Centra una ventana en la pantalla"""
        window.update_idletasks()
        w = window.winfo_width()
        h = window.winfo_height()
        ws = window.winfo_screenwidth()
        hs = window.winfo_screenheight()
        x = (ws // 2) - (w // 2)
        y = (hs // 2) - (h // 2)
        window.geometry(f'{w}x{h}+{x}+{y}')

    # ===== MÉTODOS DE UTILIDAD =====

    def setup_styles(self):
        """Aplica estilos comunes al frame"""
        from styles import apply_common_styles
        apply_common_styles(self.frame, self.app, "frame")

    def refresh_table_data(self, tree, data):
        """Actualiza los datos de una tabla"""
        tree.delete(*tree.get_children())
        for row in data:
            tree.insert("", "end", values=row)

    def get_selected_table_item(self, tree):
        """Obtiene el item seleccionado en una tabla"""
        selected_item = tree.selection()
        if not selected_item:
            return None
        return tree.item(selected_item[0], "values")

    def crear_ventana_modal(self, titulo, geometria):
        """Crear una ventana modal"""
        ventana = tk.Toplevel()
        ventana.title(titulo)
        ventana.geometry(geometria)
        ventana.grab_set()  # Hace la ventana modal
        return ventana

    def crear_marco_etiquetado(self, padre, texto):
        """Crear un marco con etiqueta"""
        return tk.LabelFrame(
            padre,
            text=texto,
            padx=10,
            pady=10,
            font=self.label_font,
            bg=self.bg_color,
            fg=self.fg_color
        )

    def crear_texto(self, padre, **kwargs):
        """Crear widget de texto con estilos aplicados"""
        texto = tk.Text(
            padre,
            font=self.entry_font,
            bg=self.bg_color,
            fg=self.fg_color,
            **kwargs
        )
        return texto

    def obtener_nombre_usuario(self, current_user):
        """Obtener nombre del usuario actual (método base)"""
        if not current_user:
            return "N/A (Usuario no identificado)"

        if isinstance(current_user, dict):
            return current_user.get('name', 'N/A')
        else:
            return getattr(current_user, 'nombre_completo',
                           getattr(current_user, 'name', 'N/A'))
