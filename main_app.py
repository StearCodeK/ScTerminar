import tkinter as tk
from tkinter import ttk, messagebox
from styles import setup_styles
from helpers import clear_frame
from menu.dashboard import show_dashboard
from menu.productos import show_inventory
from menu.pedidos import show_requests
from menu.compras import show_purchases
from menu.movimientos import show_movements
from models.notificaciones import NotificationManager
from menu.ajustes import show_settings

# Importar la nueva estructura MVC del login
from views.login_view import LoginView
from controllers.login_controller import LoginController


class ModernInventoryApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Sistema de Inventario - InventarioUSM")
        self.geometry("1280x720")
        self.minsize(1024, 600)

        # Configuración inicial
        self.colors = {
            "primary": "#4f46e5",
            "primary_light": "#6366f1",
            "secondary": "#10b981",
            "background": "#f9fafb",
            "card": "#ffffff",
            "text": "#374151",
            "text_light": "#6b7280",
            "border": "#e5e7eb",
            "hover": "#f3f4f6"
        }

        # Configurar estilos
        setup_styles(self)

        # Configurar grid principal
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)

        # Inicializar MVC del login
        self.login_controller = LoginController(self)
        self.login_view = LoginView(self, self.login_controller)

        # Configurar el administrador de notificaciones
        self.notification_manager = NotificationManager(self)

        # Mostrar login primero
        self.show_login()

    def show_login(self):
        """Muestra la pantalla de login usando la nueva estructura MVC"""
        # Limpiar ventana si ya hay widgets
        for widget in self.winfo_children():
            widget.destroy()

        # Mostrar el login usando la vista
        self.login_view.show_login()

    def show_main_content(self):
        """Muestra la interfaz principal después del login exitoso"""
        # Limpiar ventana
        for widget in self.winfo_children():
            widget.destroy()
            
        self.state('zoomed')  # Maximizar ventana al iniciar sesión

        # Crear widgets principales
        self.create_header()
        self.create_main_menu()
        self.create_status_bar()

        # Verificar notificaciones
        self.notification_manager.check_low_stock()

        # Iniciar el sistema de verificación periódica
        self.after(300000, self.notification_manager.check_low_stock)

        # Mostrar dashboard por defecto
        show_dashboard(self)

    def create_header(self):
        """Crea la barra superior con logo, búsqueda y menú de usuario"""
        header_frame = tk.Frame(self, bg="white", height=70, padx=20)
        header_frame.grid(row=0, column=0, sticky="ew")
        header_frame.grid_columnconfigure(1, weight=1)

        # Logo moderno
        logo_frame = tk.Frame(header_frame, bg="white")
        logo_frame.grid(row=0, column=0, sticky="w")

        tk.Label(logo_frame, text="📦", font=("Segoe UI", 24),
                 bg="white", fg=self.colors["primary"]).pack(side="left")
        tk.Label(logo_frame, text="InventarioUSM", font=self.title_font,
                 bg="white", fg=self.colors["text"]).pack(side="left", padx=10)

        # Frame para elementos del lado derecho (notificaciones y usuario)
        right_frame = tk.Frame(header_frame, bg="white")
        right_frame.grid(row=0, column=2, sticky="e")

        # Campana de notificaciones
        self.bell_icon = tk.Label(right_frame, text="🔔", font=("Segoe UI", 16),
                                  bg="white", cursor="hand2")
        self.bell_icon.pack(side="left", padx=10)
        self.bell_icon.bind(
            "<Button-1>", lambda e: self.notification_manager.show_notifications())

        # Separador
        tk.Frame(right_frame, bg=self.colors["border"], width=1, height=30).pack(
            side="left", padx=5)

        # Menú de usuario
        user_frame = tk.Frame(right_frame, bg="white")
        user_frame.pack(side="left")

        # Avatar circular
        avatar = tk.Canvas(user_frame, width=36, height=36, bg=self.colors["primary"],
                           bd=0, highlightthickness=0)
        avatar.create_oval(2, 2, 34, 34, fill=self.colors["primary_light"])

        # Mostrar inicial del nombre del usuario
        user_initial = "A"  # Default
        if hasattr(self, 'current_user') and self.current_user:
            user_initial = self.current_user.nombre_completo[0].upper()

        avatar.create_text(18, 18, text=user_initial, fill="white",
                           font=("Segoe UI", 12, "bold"))
        avatar.pack(side="left", padx=5)

        # Texto del usuario
        user_name = "Admin"  # Default
        if hasattr(self, 'current_user') and self.current_user:
            user_name = self.current_user.nombre_completo.split()[
                0]  # Primer nombre

        user_menu = tk.Menubutton(user_frame, text=user_name,
                                  font=self.menu_font, bg="white",
                                  fg=self.colors["text"], bd=0,
                                  activebackground=self.colors["hover"])
        user_menu.pack(side="left")

        user_dropdown = tk.Menu(user_menu, tearoff=0,
                                font=self.menu_font,
                                bg="white", fg=self.colors["text"],
                                activebackground=self.colors["hover"],
                                activeforeground=self.colors["primary"])
        user_dropdown.add_command(
            label="👤 Mi perfil", command=self.show_profile)
        user_dropdown.add_separator()
        user_dropdown.add_command(label="🚪 Cerrar sesión",
                                  command=self.logout)
        user_menu.config(menu=user_dropdown)

    def create_main_menu(self):
        """Crea el menú lateral y el área de contenido principal"""
        main_frame = tk.Frame(self, bg=self.colors["background"])
        main_frame.grid(row=1, column=0, sticky="nsew")
        main_frame.grid_columnconfigure(1, weight=1)
        main_frame.grid_rowconfigure(0, weight=1)

        # Menú lateral
        sidebar = tk.Frame(main_frame, bg="white", width=240, bd=0,
                           highlightthickness=0)
        sidebar.grid(row=0, column=0, sticky="ns")
        sidebar.grid_propagate(False)

        # Logo reducido en el menú
        tk.Frame(sidebar, height=20, bg="white").pack()  # Espaciador

        menu_items = [
            ("📊 Dashboard", show_dashboard),
            ("📦 Inventario", show_inventory),
            ("📝 Solicitudes", show_requests),
            ("🛒 Compras", show_purchases),
            ("🔄 Movimientos", show_movements),
            ("⚙️ Ajustes", show_settings)
        ]

        for text, command in menu_items:
            btn = tk.Button(sidebar, text=text, font=self.menu_font,
                            bg="white", fg=self.colors["text"], bd=0,
                            activebackground=self.colors["hover"],
                            activeforeground=self.colors["primary"],
                            command=lambda cmd=command: cmd(self),
                            padx=20, anchor="w")
            btn.pack(fill="x", ipady=10)

            # Efecto hover
            btn.bind("<Enter>", lambda e, b=btn: b.config(
                bg=self.colors["hover"]))
            btn.bind("<Leave>", lambda e, b=btn: b.config(bg="white"))

        # Área de contenido
        self.content_frame = tk.Frame(main_frame, bg=self.colors["background"])
        self.content_frame.grid(
            row=0, column=1, sticky="nsew", padx=10, pady=10)

    def create_status_bar(self):
        """Crea la barra de estado inferior"""
        status_frame = tk.Frame(self, bg="white", height=30)
        status_frame.grid(row=2, column=0, sticky="ew")

        tk.Label(status_frame, text="Sistema de Inventario v2.0",
                 bg="white", fg=self.colors["text_light"], padx=10).pack(side="left")

        tk.Label(status_frame, text="© 2025 Universidad - Todos los derechos reservados",
                 bg="white", fg=self.colors["text_light"], padx=10).pack(side="right")

    def show_profile(self):
        """Muestra el perfil del usuario"""
        clear_frame(self.content_frame)
        title = tk.Label(self.content_frame, text="Mi Perfil",
                         font=self.title_font, bg=self.colors["background"])
        title.pack(pady=20)

        if hasattr(self, 'current_user') and self.current_user:
            user_info = f"""
Nombre: {self.current_user.nombre_completo}
Usuario: {self.current_user.usuario}
Email: {self.current_user.email}
Rol: {self.current_user.rol}
            """
            tk.Label(self.content_frame, text=user_info,
                     bg=self.colors["background"], justify="left").pack()
        else:
            tk.Label(self.content_frame, text="No hay información del usuario disponible",
                     bg=self.colors["background"]).pack()

    def logout(self):
        """Cierra la sesión del usuario usando el controlador"""
        self.login_controller.logout()
        self.destroy()  # <-- Esto cierra la ventana principal
