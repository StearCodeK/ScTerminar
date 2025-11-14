# views/login_view.py
import tkinter as tk
from tkinter import ttk
from views.base_view import BaseView


class LoginView(BaseView):
    def __init__(self, app, controller):
        # Inicializamos BaseView con el frame de la app
        super().__init__(app, app)
        self.app = app
        self.controller = controller
        self.app_title = "InvUSM - Sistema de Gestión de Inventarios"
        
        # Configurar la ventana principal para el login
        self._setup_login_window()
        
        # Referencia para la imagen del logo
        self._logo_image = None
        
        # Tamaños para el panel centrado
        self.panel_width = 370
        self.panel_height = 540

    def _setup_login_window(self):
        """Configura la ventana para el modo login"""
        # Configurar título de la aplicación
        self.app.title(self.app_title)
        
        # Configurar tamaño mínimo y centrar ventana
        self.app.minsize(370, 540)
        self.app.geometry("390x400")
        self.center_window(self.app)
        
        # Configurar color de fondo
        self.app.configure(bg=self.bg_color)

    def show_login(self):
    
        """Muestra la ventana de login"""
        # Restaurar configuración específica del login
        self.panel_height = 540
        self.app.geometry("390x540")
        self.center_window(self.app)
        
        # Configurar ventana para login
        self._setup_login_window()
        self.clear_frames()

        # Crear panel centrado principal
        main_frame = self._create_centered_panel('login_frame')
        
        # Frame interno para contenido
        inner = tk.Frame(main_frame, bg=self.bg_color)
        inner.pack(fill="both", expand=True, padx=30, pady=30)

        # Logo y título de la aplicación
        self._create_app_header(inner)

        # Campos del formulario
        form_frame = self._create_form_frame(inner)
        self._create_login_form(form_frame)

        # Botones
        self._create_login_buttons(inner)

        # Enlace para recuperar contraseña
        self._create_recovery_link(inner)

    def _create_centered_panel(self, attr_name):
        """Crea un panel centrado con sombra y estilos"""
        frame = tk.Frame(
            self.app, 
            bg=self.bg_color,
            relief="flat",
            bd=0
        )
        frame.place(relx=0.5, rely=0.5, anchor="center", width=self.panel_width, height=self.panel_height)
        setattr(self, attr_name, frame)
        return frame

    def _create_app_header(self, parent):
        """Crea el encabezado con logo y título de la aplicación"""
        # Logo opcional
        logo_path = getattr(self.app, 'logo_path', None)
        if logo_path:
            try:
                self._logo_image = tk.PhotoImage(file=logo_path)
                logo_label = tk.Label(
                    parent, 
                    image=self._logo_image, 
                    bg=self.bg_color
                )
                logo_label.pack(pady=(0, 10))
            except Exception as e:
                print(f"Error cargando logo: {e}")
                self._logo_image = None

        # Título de la aplicación
        title_label = tk.Label(
            parent, 
            text="InvUSM",
            font=self.title_font,
            bg=self.bg_color,
            fg=self.primary_color
        )
        title_label.pack(pady=(0, 5))

        # Subtítulo
        subtitle_label = tk.Label(
            parent, 
            text="Sistema de Gestión de Inventarios",
            font=self.form_label_font,
            bg=self.bg_color,
            fg=self.fg_color
        )
        subtitle_label.pack(pady=(0, 20))

        # Título del formulario
        form_title = tk.Label(
            parent, 
            text="Inicio de Sesión",
            font=self.form_label_font,
            bg=self.bg_color,
            fg=self.fg_color
        )
        form_title.pack(pady=(0, 15))

    def _create_form_frame(self, parent):
        """Crea el frame del formulario"""
        form_frame = tk.Frame(parent, bg=self.bg_color)
        form_frame.pack(fill="x", pady=10)
        return form_frame

    def _create_login_form(self, form_frame):
        """Crea los campos del formulario de login"""
        # Campo Usuario
        user_frame = tk.Frame(form_frame, bg=self.bg_color)
        user_frame.pack(fill="x", pady=8)
        
        tk.Label(
            user_frame, 
            text="Usuario:", 
            font=self.form_label_font,
            bg=self.bg_color,
            fg=self.fg_color,
            width=12
        ).pack(side="left")
        
        self.user_entry = ttk.Entry(
            user_frame, 
            width=25,
            font=self.form_entry_font
        )
        self.user_entry.pack(side="left", fill="x", expand=True, padx=(10, 0))
        self.user_entry.bind('<Return>', lambda e: self.controller.login())

        # Campo Contraseña
        pass_frame = tk.Frame(form_frame, bg=self.bg_color)
        pass_frame.pack(fill="x", pady=8)
        
        tk.Label(
            pass_frame, 
            text="Contraseña:", 
            font=self.form_label_font,
            bg=self.bg_color,
            fg=self.fg_color,
            width=12
        ).pack(side="left")
        
        self.pass_entry = ttk.Entry(
            pass_frame, 
            show="*", 
            width=25,
            font=self.form_entry_font
        )
        self.pass_entry.pack(side="left", fill="x", expand=True, padx=(10, 0))
        self.pass_entry.bind('<Return>', lambda e: self.controller.login())

    def _create_login_buttons(self, parent):
        """Crea los botones de login"""
        btn_frame = tk.Frame(parent, bg=self.bg_color)
        btn_frame.pack(fill="x", pady=20)

        # Botón de login con estilo acentuado
        login_btn = ttk.Button(
            btn_frame, 
            text="Iniciar Sesión", 
            command=self.controller.login,
            style="Accent.TButton"
        )
        login_btn.pack(fill="x", pady=5)

        # Botón de registro
        register_btn = ttk.Button(
            btn_frame, 
            text="Registrarse", 
            command=self.controller.show_register
        )
        register_btn.pack(fill="x", pady=5)

    def _create_recovery_link(self, parent):
        """Crea el enlace para recuperar contraseña"""
        recovery_frame = tk.Frame(parent, bg=self.bg_color)
        recovery_frame.pack(fill="x", pady=10)

        recovery_label = tk.Label(
            recovery_frame, 
            text="¿Olvidó su contraseña?", 
            fg=self.primary_color,
            cursor="hand2", 
            bg=self.bg_color, 
            font=self.entry_font
        )
        recovery_label.pack()
        recovery_label.bind("<Button-1>", lambda e: self.controller.show_password_recovery())

    def show_register(self):
        """Muestra el formulario de registro"""
        self.clear_frames()

        # Ajustar tamaño del panel y ventana SOLO para registro
        self.panel_height = 740
        self.app.geometry("450x670")
        self.center_window(self.app)

        # Crear panel centrado
        main_frame = self._create_centered_panel('register_frame')
        
        # Frame interno para contenido
        inner = tk.Frame(main_frame, bg=self.bg_color)
        inner.pack(fill="both", expand=True, padx=10, pady=80)  # Ya está bien

        # Título
        tk.Label(
            inner, 
            text="Registro de Usuario", 
            font=self.title_font,
            bg=self.bg_color,
            fg=self.primary_color
        ).pack(pady=(0, 0))

        # Campos del formulario
        form_frame = tk.Frame(inner, bg=self.bg_color)
        form_frame.pack(fill="both", expand=True, pady=10)  # <-- Cambia a fill="both", expand=True

        fields = [
            ("Nombre Completo:", "entry"),
            ("Correo Electrónico:", "entry"),
            ("Usuario:", "entry"),
            ("Contraseña:", "entry_show", "*"),
            ("Confirmar Contraseña:", "entry_show", "*"),
            ("Código de Autorización:", "entry")
        ]

        self.register_entries = {}
        for i, (label_text, field_type, *args) in enumerate(fields):
            field_frame = tk.Frame(form_frame, bg=self.bg_color)
            field_frame.pack(fill="x", pady=6)

            tk.Label(
                field_frame, 
                text=label_text, 
                font=self.form_label_font,
                bg=self.bg_color,
                fg=self.fg_color,
                width=16,
                anchor="w",
                wraplength=180
               
            ).pack(side="left")

            if field_type == "entry":
                entry = ttk.Entry(
                    field_frame, 
                    width=25,
                    font=self.form_entry_font
                )
            elif field_type == "entry_show":
                entry = ttk.Entry(
                    field_frame, 
                    show=args[0],
                    width=25,
                    font=self.form_entry_font
                )
            else:
                entry = ttk.Entry(
                    field_frame, 
                    width=25,
                    font=self.form_entry_font
                )

            entry.pack(side="left", fill="x", expand=True, padx=(10, 0))
            self.register_entries[label_text] = entry

        # Botón para solicitar código de autorización
        code_btn_frame = tk.Frame(form_frame, bg=self.bg_color)
        code_btn_frame.pack(fill="x", pady=10)
        
        ttk.Button(
            code_btn_frame, 
            text="Solicitar Código", 
            command=self.controller.send_authorization_code
        ).pack()

        # Botones
        btn_frame = tk.Frame(inner, bg=self.bg_color)
        btn_frame.pack(fill="x", pady=10)

        ttk.Button(
            btn_frame, 
            text="Registrarse", 
            command=self.controller.register_user,
            style="Accent.TButton"
        ).pack(fill="x", pady=5, padx=20)

        ttk.Button(
            btn_frame, 
            text="Volver al Login", 
            command=self.controller.show_login
        ).pack(fill="x", pady=5, padx=20)

    def show_password_recovery(self):
        """Muestra el formulario de recuperación de contraseña"""
        self.clear_frames()

        # Configurar ventana específica para recuperación de contraseña
        self.app.title(f"{self.app_title} - Recuperar Contraseña")
        self.app.minsize(370, 320)  # Reduce el tamaño mínimo
        self.app.geometry("370x450")  # Reduce el tamaño de la ventana
        self.center_window(self.app)

        # Tamaños específicos para el panel de recuperación
        self.panel_height = 420  # Reduce el alto del panel
        self.panel_width = 370

        main_frame = self._create_centered_panel('recovery_frame')
        
        # Frame interno con menos padding para contenido más compacto
        inner = tk.Frame(main_frame, bg=self.bg_color)
        inner.pack(fill="both", expand=True, padx=30, pady=20)  # Reduce pady de 80 a 20

        # Título
        tk.Label(
            inner, 
            text="Recuperar Contraseña", 
            font=self.title_font,
            bg=self.bg_color,
            fg=self.primary_color,
            wraplength=250
            
        ).pack(pady=(0, 10))  # Reduce pady

        # Instrucciones
        tk.Label(
            inner,
            text="Ingrese su correo electrónico para recibir un código de recuperación",
            font=self.entry_font,
            bg=self.bg_color,
            fg=self.fg_color,
            wraplength=300,
            justify="center"
        ).pack(pady=(0, 10))  # Reduce pady

        # Campo de email
        form_frame = tk.Frame(inner, bg=self.bg_color)
        form_frame.pack(fill="x", pady=5)  # Reduce pady

        email_frame = tk.Frame(form_frame, bg=self.bg_color)
        email_frame.pack(fill="x", pady=5)  # Reduce pady

        tk.Label(
            email_frame, 
            text="Correo:", 
            font=self.form_label_font,
            bg=self.bg_color,
            fg=self.fg_color,
            width=10,
            anchor="w"
        ).pack(side="left")

        self.recovery_email_entry = ttk.Entry(
            email_frame, 
            width=20,
            font=self.form_entry_font
        )
        self.recovery_email_entry.pack(side="left", fill="x", expand=True, padx=(10, 0))
        self.recovery_email_entry.bind('<Return>', lambda e: self.controller.send_recovery_code())

        # Botones
        btn_frame = tk.Frame(inner, bg=self.bg_color)
        btn_frame.pack(fill="x", pady=10)  # Reduce pady

        ttk.Button(
            btn_frame, 
            text="Enviar Código", 
            command=self.controller.send_recovery_code,
            style="Accent.TButton"
        ).pack(fill="x", pady=5)

        ttk.Button(
            btn_frame, 
            text="Volver al Login", 
            command=self.controller.show_login
        ).pack(fill="x", pady=5)

    def show_reset_password(self):
        """Muestra el formulario para ingresar el código y nueva contraseña"""
        self.clear_frames()

        # Ajusta tamaño del panel y ventana
        self.panel_height = 320
        self.app.geometry("420x480")
        self.center_window(self.app)
        
         # Tamaños específicos para el panel de recuperación
        self.panel_height = 480  # Reduce el alto del panel
        self.panel_width = 400

        main_frame = self._create_centered_panel('reset_frame')

        inner = tk.Frame(main_frame, bg=self.bg_color)
        inner.pack(fill="both", expand=True, padx=30, pady=20)

        tk.Label(
            inner,
            text="Restablecer Contraseña",
            font=self.title_font,
            bg=self.bg_color,
            fg=self.primary_color,
            wraplength=250
        ).pack(pady=(0, 10))

        form_frame = tk.Frame(inner, bg=self.bg_color)
        form_frame.pack(fill="x", pady=5)

        fields = [
            ("Código de Verificación:", "entry"),
            ("Nueva Contraseña:", "entry_show", "*"),
            ("Confirmar Contraseña:", "entry_show", "*")
        ]

        self.reset_entries = {}
        for label_text, field_type, *args in fields:
            field_frame = tk.Frame(form_frame, bg=self.bg_color)
            field_frame.pack(fill="x", expand=True, pady=6)

            tk.Label(
                field_frame,
                text=label_text,
                font=self.form_label_font,
                bg=self.bg_color,
                fg=self.fg_color,
                width=16,
                anchor="w",
                wraplength=180
            ).pack(side="left")

            if field_type == "entry":
                entry = ttk.Entry(
                    field_frame,
                    width=25,
                    font=self.form_entry_font
                )
            elif field_type == "entry_show":
                entry = ttk.Entry(
                    field_frame,
                    show=args[0],
                    width=25,
                    font=self.form_entry_font
                )
            else:
                entry = ttk.Entry(
                    field_frame,
                    width=25,
                    font=self.form_entry_font
                )

            entry.pack(side="left", fill="x", expand=True, padx=(10, 0))
            self.reset_entries[label_text] = entry

        # Botones
        btn_frame = tk.Frame(inner, bg=self.bg_color)
        btn_frame.pack(fill="x", pady=10)

        ttk.Button(
            btn_frame,
            text="Restablecer Contraseña",
            command=self.controller.reset_password,
            style="Accent.TButton"
        ).pack(fill="x", pady=5)

        ttk.Button(
            btn_frame,
            text="Volver al Login",
            command=self.controller.show_login
        ).pack(fill="x", pady=5)

    def get_login_data(self):
        """Obtiene los datos del formulario de login"""
        return {
            'username': self.user_entry.get().strip(),
            'password': self.pass_entry.get()
        }

    def get_register_data(self):
        """Obtiene los datos del formulario de registro"""
        return {
            'fullname': self.register_entries["Nombre Completo:"].get().strip(),
            'email': self.register_entries["Correo Electrónico:"].get().strip(),
            'username': self.register_entries["Usuario:"].get().strip(),
            'password': self.register_entries["Contraseña:"].get(),
            'confirm_password': self.register_entries["Confirmar Contraseña:"].get(),
            'auth_code': self.register_entries["Código de Autorización:"].get().strip()
        }

    def get_recovery_email(self):
        """Obtiene el email del formulario de recuperación"""
        return self.recovery_email_entry.get().strip()

    def get_reset_data(self):
        """Obtiene los datos del formulario de reset de contraseña"""
        return {
            'code': self.reset_entries["Código de Verificación:"].get().strip(),
            'new_pass': self.reset_entries["Nueva Contraseña:"].get(),
            'confirm_pass': self.reset_entries["Confirmar Contraseña:"].get()
        }

    def clear_frames(self):
        """Limpia los frames de login/registro"""
        frames_to_clear = ['login_frame', 'register_frame', 'recovery_frame', 'reset_frame']
        for frame_name in frames_to_clear:
            if hasattr(self, frame_name):
                getattr(self, frame_name).destroy()
                delattr(self, frame_name)

    def focus_username(self):
        """Enfoca el campo de usuario"""
        if hasattr(self, 'user_entry'):
            self.user_entry.focus_set()

    def focus_password(self):
        """Enfoca el campo de contraseña"""
        if hasattr(self, 'pass_entry'):
            self.pass_entry.focus_set()