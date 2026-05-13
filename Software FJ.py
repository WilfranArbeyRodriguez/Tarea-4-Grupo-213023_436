# ESTUDIANTE: WILFRAN ARBEY RODRIGUEZ HERNANDEZ
# GRUPOI: 213023_436
# PROGRAMA: ECBTI INGENIERÍA DE SISTEMAS
# CODIGO FUENTE: AUTORIA PROPIA


import tkinter as tk
from tkinter import ttk, messagebox
from abc import ABC, abstractmethod
from datetime import datetime
import re

# EXCEPCIONES PERSONALIZADAS Y LOGS
class ErrorSoftware(Exception): """Clase base"""
class ValidacionError(ErrorSoftware): """Errores de datos"""
class ReservaError(ErrorSoftware): """Errores de proceso"""

def registrar_log(mensaje, tipo="INFO"):
    try:
        with open("registro actividad.log", "a", encoding="utf-8") as f:
            fecha = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            f.write(f"[{fecha}] [{tipo}] {mensaje}\n")
    except Exception as e:
        print(f"Error fatal en el sistema de logs: {e}")

# MODELO DE DATOS (POO)
class Entidad(ABC):
    @abstractmethod
    def __str__(self): pass

class Cliente(Entidad):
    def __init__(self, nombre, documento, correo):
        if not nombre.strip() or not documento.strip():
            raise ValidacionError("Nombre y Documento son obligatorios.")
        if not re.match(r"[^@]+@[^@]+\.[^@]+", correo):
            raise ValidacionError(f"Correo '{correo}' no es válido.")
        
        self.__nombre = nombre
        self.__documento = documento
        self.__correo = correo

    @property
    def nombre(self): return self.__nombre
    
    def __str__(self):
        return f"{self.__nombre} (ID: {self.__documento})"

class Servicio(ABC):
    def __init__(self, nombre, precio):
        self.nombre = nombre
        self.precio = float(precio)

    @abstractmethod
    def calcular(self, cant): pass

class ReservaSala(Servicio):
    def calcular(self, h): return self.precio * int(h)

class AlquilerEquipo(Servicio):
    def calcular(self, d): return (self.precio * int(d)) * 1.10

class AsesoriaEspecializada(Servicio):
    def calcular(self, sesiones): return self.precio * int(sesiones)

# INTERFAZ GRÁFICA
class AppFJ:
    def __init__(self, root):
        self.root = root
        self.root.title("Software FJ - Gestión de Reservas")
        self.root.geometry("600x500")
        
        self.clientes = []
        self.servicios = [
            ReservaSala("Sala de Juntas", 50000),
            AlquilerEquipo("Proyector HD", 35000),
            AsesoriaEspecializada("Asesoría Técnica", 48000)
        ]
        
        self.menu_principal()

    def limpiar(self):
        for w in self.root.winfo_children(): w.destroy()

    def menu_principal(self):
        self.limpiar()
        tk.Label(self.root, text="SOFTWARE FJ", font=("Arial", 14, "bold")).pack(pady=20)
        
        frame = tk.Frame(self.root)
        frame.pack()

        btns = [
            ("Registrar Cliente", self.win_cliente),
            ("Nueva Reserva", self.win_reserva),
            ("Registro de Actividades (Logs)", self.ver_logs),
            ("Salir", self.root.quit)
        ]

        for t, c in btns:
            tk.Button(frame, text=t, command=c, width=25, pady=10).pack(pady=5)

    def win_cliente(self):
        win = tk.Toplevel(self.root)
        win.title("Nuevo Cliente")
        win.geometry("350x300")

        tk.Label(win, text="Nombre completo:").pack()
        ent_nom = tk.Entry(win); ent_nom.pack()
        
        tk.Label(win, text="Documento de Identidad:").pack()
        ent_doc = tk.Entry(win); ent_doc.pack()

        tk.Label(win, text="Correo Electrónico:").pack()
        ent_eml = tk.Entry(win); ent_eml.pack()

        def guardar():
            try:
                nuevo = Cliente(ent_nom.get(), ent_doc.get(), ent_eml.get())
                self.clientes.append(nuevo)
                messagebox.showinfo("Éxito", "Cliente registrado exitosamente")
                registrar_log(f"CLIENTE REGISTRADO: {nuevo.nombre}")
                win.destroy()
            except ValidacionError as e:
                registrar_log(f"Falla registro: {e}", "ERROR_VALIDACION")
                messagebox.showerror("Error de Datos", str(e))
            except Exception as e:
                registrar_log(f"Error inesperado: {e}", "CRITICO")

        tk.Button(win, text="Registrar", command=guardar, bg="#2ecc71", fg="white").pack(pady=20)

    def win_reserva(self):
        if not self.clientes:
            messagebox.showwarning("Aviso", "No hay clientes registrados.")
            return

        win = tk.Toplevel(self.root)
        win.title("Nueva Reserva")
        win.geometry("400x350")

        tk.Label(win, text="Seleccione el Cliente:").pack()
        cb_cli = ttk.Combobox(win, values=[c.nombre for c in self.clientes], state="readonly")
        cb_cli.pack()

        tk.Label(win, text="Seleccione el Servicio:").pack()
        cb_ser = ttk.Combobox(win, values=[s.nombre for s in self.servicios], state="readonly")
        cb_ser.pack()

        tk.Label(win, text="Cantidad (Horas / Días / Sesiones):").pack()
        ent_cant = tk.Entry(win); ent_cant.pack()

        def procesar():
            nombre_cliente = cb_cli.get()
            nombre_servicio = cb_ser.get()
            cantidad_ingresada = ent_cant.get()
            
            try:
                if cb_cli.current() == -1 or cb_ser.current() == -1:
                    raise ReservaError("Debe seleccionar cliente y servicio.")
                
                serv = self.servicios[cb_ser.current()]
                
                # determinamos la unidad para el log según el tipo de servicio
                if isinstance(serv, ReservaSala): unidad = "hora(s)"
                elif isinstance(serv, AlquilerEquipo): unidad = "día(s)"
                else: unidad = "sesión(es)"
                
                total = serv.calcular(cantidad_ingresada)
                
            except ValueError:
                registrar_log(f"Cantidad inválida '{cantidad_ingresada}' para {nombre_cliente}.", "ERROR_TIPO")
                messagebox.showerror("Error", "La cantidad debe ser un número entero.")
            except ReservaError as e:
                registrar_log(f"Reserva fallida ({nombre_cliente}): {e}", "ERROR_RESERVA")
                messagebox.showwarning("Atención", str(e))
            except Exception as e:
                registrar_log(f"Falla crítica para {nombre_cliente}: {e}", "CRITICO")
                messagebox.showerror("Error", "Error al procesar la reserva.")
            else:
                msg = f"Reserva procesada para {nombre_cliente}\nTotal: ${total:,.0f}"
                messagebox.showinfo("Reserva Exitosa", msg)
                
                # LOG 
                log_msg = f"RESERVA EXITOSA: {nombre_cliente} contrató {cantidad_ingresada} {unidad} en {nombre_servicio} por un valor de ${total:,.0f}"
                registrar_log(log_msg)
                
                win.destroy()

        tk.Button(win, text="Procesar Pago y Reserva", command=procesar).pack(pady=20)

    def ver_logs(self):
        win = tk.Toplevel(self.root)
        win.title("Registro de Logs")
        txt = tk.Text(win, width=90, height=20)
        txt.pack(padx=10, pady=10)
        try:
            with open("registro actividad.log", "r", encoding="utf-8") as f:
                txt.insert("1.0", f.read())
        except FileNotFoundError:
            txt.insert("1.0", "El archivo de log aún no se ha creado.")

if __name__ == "__main__":
    root = tk.Tk()
    AppFJ(root)
    root.mainloop()