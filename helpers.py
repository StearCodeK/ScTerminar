from tkinter import ttk
import tkinter as tk
import smtplib
from email.mime.text import MIMEText



def clear_frame(frame):
    """Limpia todos los widgets de un frame"""
    for widget in frame.winfo_children():
        widget.destroy()


def create_scrollable_frame(parent):
    """Crea un frame con scrollbar"""
    canvas = tk.Canvas(parent)
    scrollbar = ttk.Scrollbar(parent, orient="vertical", command=canvas.yview)
    scrollable_frame = tk.Frame(canvas)

    scrollable_frame.bind("<Configure>", lambda e: canvas.configure(
        scrollregion=canvas.bbox("all")))
    canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
    canvas.configure(yscrollcommand=scrollbar.set)

    return canvas, scrollbar, scrollable_frame


def center_window(window):
    """Centrar una ventana en la pantalla"""
    window.update_idletasks()
    width = window.winfo_width()
    height = window.winfo_height()
    x = (window.winfo_screenwidth() // 2) - (width // 2)
    y = (window.winfo_screenheight() // 2) - (height // 2)
    window.geometry(f'{width}x{height}+{x}+{y}')


def send_email(to_email, subject, body):
    # Configura tus credenciales aquí
    smtp_server = "smtp.gmail.com"
    smtp_port = 587
    sender_email = "marijo.m.h.1011@gmail.com"
    sender_password = "ahsv mxsk jico zxhs"  # Usa contraseña de aplicación

    msg = MIMEText(body)
    msg["Subject"] = subject
    msg["From"] = sender_email
    msg["To"] = to_email

    try:
        server = smtplib.SMTP(smtp_server, smtp_port)
        server.starttls()
        server.login(sender_email, sender_password)
        server.sendmail(sender_email, to_email, msg.as_string())
        server.quit()
        return True
    except Exception as e:
        print(f"Error enviando correo: {e}")
        return False