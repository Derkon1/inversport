# main_tkinter.py (en la carpeta 2/, fuera de inver/)
import tkinter as tk
from tkinter import messagebox
from inver.views import AppNomina

PALETTE = {
    'bg_dark': '#0a0e1a',
    'bg_sidebar': '#0f1423',
    'bg_main': '#131a2c',
    'card_bg': '#1a2335',
    'card_hover': '#1f2a40',
    'accent': "#0077ff",
    'accent_hover': '#0077ff',
    'success': '#10b981',
    'warning': '#f59e0b',
    'error': '#ef4444',
    'info': '#3b82f6',
    'text_light': '#f3f4f6',
    'text_gray': '#9ca3af',
    'border': '#1f2937',
    'input_bg': '#0f1423',
}


def iniciar_app_principal():
    """Abre la ventana principal de la aplicación."""
    root_app = tk.Tk()
    app = AppNomina(root_app)
    root_app.mainloop()


def validar_credenciales(login_root, entry_usuario, entry_contrasena):
    """Valida usuario y contraseña, cierra login y abre la app si son correctas."""
    usuario = entry_usuario.get().strip()
    clave = entry_contrasena.get()
    if usuario == 'Admin' and clave == 'Admin':
        login_root.destroy()
        iniciar_app_principal()
    else:
        messagebox.showerror("Acceso denegado", "Usuario o contraseña incorrectos")
        entry_contrasena.delete(0, tk.END)


if __name__ == '__main__':
    # Ventana de inicio de sesión
    login_root = tk.Tk()
    login_root.title('Inicio de sesión')
    login_root.geometry('640x420')
    login_root.resizable(False, False)
    login_root.configure(bg=PALETTE['bg_dark'])

    frame = tk.Frame(login_root, bg=PALETTE['card_bg'], padx=20, pady=20)
    frame.place(relx=0.5, rely=0.5, anchor='center')

    lbl_u = tk.Label(frame, text='Usuario', font=('Segoe UI', 10, 'bold'), bg=PALETTE['card_bg'], fg=PALETTE['text_light'])
    lbl_u.grid(row=0, column=0, sticky='w')
    entry_usuario = tk.Entry(frame, font=('Segoe UI', 12), width=32, bg=PALETTE['input_bg'], fg=PALETTE['text_light'], insertbackground=PALETTE['text_light'], relief='flat')
    entry_usuario.grid(row=1, column=0, pady=(6,12))

    lbl_p = tk.Label(frame, text='Contraseña', font=('Segoe UI', 10, 'bold'), bg=PALETTE['card_bg'], fg=PALETTE['text_light'])
    lbl_p.grid(row=2, column=0, sticky='w')
    entry_contrasena = tk.Entry(frame, font=('Segoe UI', 12), width=32, show='*', bg=PALETTE['input_bg'], fg=PALETTE['text_light'], insertbackground=PALETTE['text_light'], relief='flat')
    entry_contrasena.grid(row=3, column=0, pady=(6,14))

    btn_ingresar = tk.Button(frame, text='Ingresar', font=('Segoe UI', 11), width=28, bg=PALETTE['accent'], fg='white', activebackground=PALETTE['accent_hover'], relief='flat', cursor='hand2', 
                             command=lambda: validar_credenciales(login_root, entry_usuario, entry_contrasena))
    btn_ingresar.grid(row=4, column=0, pady=(4,0))

    login_root.bind('<Return>', lambda e: validar_credenciales(login_root, entry_usuario, entry_contrasena))

    entry_usuario.focus_set()
    login_root.mainloop()