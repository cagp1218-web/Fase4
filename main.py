from abc import ABC, abstractmethod
from datetime import datetime
import logging
import tkinter as tk
from tkinter import ttk, messagebox


# ---------------------------------------------------------
# 1. CONFIGURACIÓN DEL ARCHIVO DE REGISTRO (LOGS)
# ---------------------------------------------------------

logging.basicConfig(
    filename="software_fj.log",
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    encoding="utf-8"
)

# ---------------------------------------------------------
# 2. EXCEPCIONES PERSONALIZADAS
# ---------------------------------------------------------

class ErrorSistema(Exception):
    """Excepción general del sistema."""
    pass

class DatoInvalidoError(ErrorSistema):
    """Se genera cuando un dato ingresado no es válido."""
    pass

class ServicioNoDisponibleError(ErrorSistema):
    """Se genera cuando un servicio no está disponible."""
    pass

class ReservaError(ErrorSistema):
    """Se genera cuando una reserva no se puede procesar."""
    pass

# ---------------------------------------------------------
# 3. CLASE ABSTRACTA ENTIDAD
# ---------------------------------------------------------

class Entidad(ABC):
    """Representa los elementos generales del sistema."""

    def __init__(self, identificacion):
        if not identificacion or not identificacion.strip():
            raise DatoInvalidoError("La identificación es obligatoria.")
        self._identificacion = identificacion.strip()

    @property
    def identificacion(self):
        return self._identificacion

    @abstractmethod
    def obtener_informacion(self):
        """Cada clase hija debe implementar este método."""
        pass

# ---------------------------------------------------------
# 4. CLASE CLIENTE
# ---------------------------------------------------------

class Cliente(Entidad):
    """Almacena los datos de un cliente con encapsulación."""

    def __init__(self, identificacion, nombre, correo, telefono):
        super().__init__(identificacion)

        if not nombre or len(nombre.strip()) < 2:
            raise DatoInvalidoError("El nombre debe tener mínimo 2 caracteres.")

        if not correo or "@" not in correo or "." not in correo:
            raise DatoInvalidoError("Ingrese un correo electrónico válido.")

        if not telefono or not telefono.strip().isdigit() or len(telefono.strip()) < 7:
            raise DatoInvalidoError("El teléfono debe tener mínimo 7 dígitos.")

        self.__nombre = nombre.strip()
        self.__correo = correo.strip()
        self.__telefono = telefono.strip()

    @property
    def nombre(self):
        return self.__nombre

    def obtener_informacion(self):
        return (
            f"ID: {self.identificacion} | Nombre: {self.__nombre} | "
            f"Correo: {self.__correo} | Teléfono: {self.__telefono}"
        )

# ---------------------------------------------------------
# 5. CLASE ABSTRACTA SERVICIO
# ---------------------------------------------------------

class Servicio(ABC):
    """Clase base para los diferentes servicios de Software FJ."""

    def __init__(self, nombre, precio_base):
        if not nombre or not nombre.strip():
            raise DatoInvalidoError("El nombre del servicio es obligatorio.")

        if not isinstance(precio_base, (int, float)) or precio_base <= 0:
            raise DatoInvalidoError("El precio base debe ser mayor que cero.")

        self.nombre = nombre.strip()
        self.precio_base = float(precio_base)
        self.disponible = True

    @abstractmethod
    def calcular_costo(self, cantidad=1, descuento=0, impuesto=0.19):
        pass

    @abstractmethod
    def describir_servicio(self):
        pass

    @abstractmethod
    def validar_parametros(self, cantidad):
        pass

# ---------------------------------------------------------
# 6. SERVICIOS ESPECIALIZADOS (HERENCIA Y POLIMORFISMO)
# ---------------------------------------------------------

class ReservaSala(Servicio):
    def __init__(self, precio_hora=25000):
        super().__init__("Reserva de sala", precio_hora)

    def validar_parametros(self, cantidad):
        if cantidad <= 0 or cantidad > 12:
            raise DatoInvalidoError("La duración de la sala debe ser de 1 a 12 horas.")

    def calcular_costo(self, cantidad=1, descuento=0, impuesto=0.19):
        self.validar_parametros(cantidad)
        if not 0 <= descuento <= 100 or not 0 <= impuesto <= 1:
            raise DatoInvalidoError("Descuento o impuesto fuera de rango.")
        subtotal = self.precio_base * cantidad
        return subtotal * (1 - descuento / 100) * (1 + impuesto)

    def describir_servicio(self):
        return "Alquiler de sala por horas."

class AlquilerEquipo(Servicio):
    def __init__(self, precio_dia=40000):
        super().__init__("Alquiler de equipos", precio_dia)

    def validar_parametros(self, cantidad):
        if cantidad <= 0 or cantidad > 30:
            raise DatoInvalidoError("El alquiler debe ser de 1 a 30 días.")

    def calcular_costo(self, cantidad=1, descuento=0, impuesto=0.19):
        self.validar_parametros(cantidad)
        if not 0 <= descuento <= 100 or not 0 <= impuesto <= 1:
            raise DatoInvalidoError("Descuento o impuesto fuera de rango.")
        subtotal = self.precio_base * cantidad
        return subtotal * (1 - descuento / 100) * (1 + impuesto)

    def describir_servicio(self):
        return "Alquiler de equipos tecnológicos por días."

class AsesoriaEspecializada(Servicio):
    def __init__(self, precio_hora=60000):
        super().__init__("Asesoría especializada", precio_hora)

    def validar_parametros(self, cantidad):
        if cantidad <= 0 or cantidad > 8:
            raise DatoInvalidoError("La asesoría debe ser de 1 a 8 horas.")

    def calcular_costo(self, cantidad=1, descuento=0, impuesto=0.19):
        self.validar_parametros(cantidad)
        if not 0 <= descuento <= 100 or not 0 <= impuesto <= 1:
            raise DatoInvalidoError("Descuento o impuesto fuera de rango.")
        subtotal = self.precio_base * cantidad
        return subtotal * (1 - descuento / 100) * (1 + impuesto)

    def describir_servicio(self):
        return "Acompañamiento y asesoría especializada."

# ---------------------------------------------------------
# 7. CLASE RESERVA
# ---------------------------------------------------------

class Reserva(Entidad):
    """Relaciona un cliente con un servicio y administra su estado."""

    contador = 0

    def __init__(self, cliente, servicio, duracion, descuento=0):
        Reserva.contador += 1
        super().__init__(f"R-{Reserva.contador:03d}")

        if not isinstance(cliente, Cliente):
            raise DatoInvalidoError("Debe seleccionar un cliente válido.")

        if not isinstance(servicio, Servicio):
            raise DatoInvalidoError("Debe seleccionar un servicio válido.")

        if not servicio.disponible:
            raise ServicioNoDisponibleError("El servicio no está disponible.")

        if not isinstance(duracion, (int, float)) or duracion <= 0:
            raise DatoInvalidoError("La duración debe ser un número mayor que cero.")

        servicio.validar_parametros(duracion)

        self.cliente = cliente
        self.servicio = servicio
        self.duracion = duracion
        self.descuento = descuento
        self.estado = "Pendiente"
        self.fecha = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.costo = 0

    def confirmar(self):
        if self.estado != "Pendiente":
            raise ReservaError("Solo se pueden confirmar reservas pendientes.")

        try:
            self.costo = self.servicio.calcular_costo(
                self.duracion, self.descuento
            )
        except DatoInvalidoError as error:
            logging.exception("Error al calcular el costo de la reserva.")
            raise ReservaError("No fue posible calcular el costo.") from error
        else:
            self.estado = "Confirmada"
            logging.info("Reserva %s confirmada.", self.identificacion)
        finally:
            logging.info("Finalizó el proceso de confirmación de reserva.")

    def cancelar(self):
        if self.estado == "Cancelada":
            raise ReservaError("La reserva ya se encuentra cancelada.")
        if self.estado == "Procesada":
            raise ReservaError("No se puede cancelar una reserva procesada.")

        self.estado = "Cancelada"
        logging.info("Reserva %s cancelada.", self.identificacion)

    def procesar(self):
        if self.estado != "Confirmada":
            raise ReservaError("La reserva debe estar confirmada antes de procesarla.")

        self.estado = "Procesada"
        logging.info("Reserva %s procesada.", self.identificacion)

    def obtener_informacion(self):
        return (
            f"{self.identificacion} | {self.cliente.nombre} | "
            f"{self.servicio.nombre} | Cantidad: {self.duracion} | "
            f"Estado: {self.estado} | Total: ${self.costo:,.0f}"
        )

# ---------------------------------------------------------
# 8. CLASE PRINCIPAL PARA ADMINISTRAR LAS LISTAS
# ---------------------------------------------------------

class SistemaSoftwareFJ:
    """Administra clientes, servicios y reservas en listas internas."""

    def __init__(self):
        self.clientes = []
        self.servicios = [
            ReservaSala(),
            AlquilerEquipo(),
            AsesoriaEspecializada()
        ]
        self.reservas = []

    def registrar_cliente(self, identificacion, nombre, correo, telefono):
        # Evita identificaciones repetidas.
        if any(c.identificacion == identificacion.strip() for c in self.clientes):
            raise DatoInvalidoError("Ya existe un cliente con esa identificación.")

        cliente = Cliente(identificacion, nombre, correo, telefono)
        self.clientes.append(cliente)
        logging.info("Cliente registrado: %s", identificacion)
        return cliente

    def crear_reserva(self, indice_cliente, indice_servicio, duracion, descuento=0):
        try:
            cliente = self.clientes[indice_cliente]
            servicio = self.servicios[indice_servicio]
            reserva = Reserva(cliente, servicio, duracion, descuento)
            reserva.confirmar()
            self.reservas.append(reserva)
            return reserva
        except IndexError as error:
            logging.exception("Se intentó seleccionar un elemento inexistente.")
            raise DatoInvalidoError("Seleccione un cliente y servicio existentes.") from error
        except ErrorSistema:
            logging.exception("No se pudo crear la reserva.")
            raise

    def listar_clientes(self):
        return [cliente.obtener_informacion() for cliente in self.clientes]

    def listar_reservas(self):
        return [reserva.obtener_informacion() for reserva in self.reservas]

# ---------------------------------------------------------
# 9. PRUEBA DE 10 OPERACIONES
# ---------------------------------------------------------

def ejecutar_pruebas():
    """Ejecuta operaciones correctas e incorrectas y muestra resultados."""

    print("\n========== PRUEBAS DEL SISTEMA SOFTWARE FJ ==========")
    sistema = SistemaSoftwareFJ()

    operaciones = 0

    # Operación 1: registrar cliente válido.
    try:
        cliente1 = sistema.registrar_cliente(
            "1001", "Laura Gómez", "laura@gmail.com", "3001234567"
        )
        print("1. Cliente registrado:", cliente1.nombre)
    except ErrorSistema as error:
        print("1. Error:", error)
    operaciones += 1

    # Operación 2: registrar segundo cliente.
    try:
        cliente2 = sistema.registrar_cliente(
            "1002", "Andrés Pérez", "andres@gmail.com", "3107654321"
        )
        print("2. Cliente registrado:", cliente2.nombre)
    except ErrorSistema as error:
        print("2. Error:", error)
    operaciones += 1

    # Operación 3: intentar registrar cliente con correo inválido.
    try:
        sistema.registrar_cliente("1003", "Pedro Ruiz", "correo_invalido", "3001234567")
    except ErrorSistema as error:
        print("3. Registro inválido controlado:", error)
    operaciones += 1

    # Operación 4: intentar repetir identificación.
    try:
        sistema.registrar_cliente("1001", "Otro Cliente", "otro@gmail.com", "3001234567")
    except ErrorSistema as error:
        print("4. Identificación duplicada controlada:", error)
    operaciones += 1

    # Operación 5: crear reserva de sala.
    try:
        reserva1 = sistema.crear_reserva(0, 0, 2, 10)
        print("5. Reserva creada:", reserva1.obtener_informacion())
    except ErrorSistema as error:
        print("5. Error:", error)
    operaciones += 1

    # Operación 6: crear alquiler de equipo.
    try:
        reserva2 = sistema.crear_reserva(1, 1, 3, 0)
        print("6. Reserva creada:", reserva2.obtener_informacion())
    except ErrorSistema as error:
        print("6. Error:", error)
    operaciones += 1

    # Operación 7: duración inválida.
    try:
        sistema.crear_reserva(0, 0, 0)
    except ErrorSistema as error:
        print("7. Reserva inválida controlada:", error)
    operaciones += 1

    # Operación 8: índice de cliente inexistente.
    try:
        sistema.crear_reserva(20, 0, 1)
    except ErrorSistema as error:
        print("8. Cliente inexistente controlado:", error)
    operaciones += 1

    # Operación 9: procesar una reserva confirmada.
    try:
        reserva1.procesar()
        print("9. Reserva procesada:", reserva1.identificacion)
    except ErrorSistema as error:
        print("9. Error:", error)
    operaciones += 1

    # Operación 10: intentar cancelar una reserva procesada.
    try:
        reserva1.cancelar()
    except ErrorSistema as error:
        logging.exception("Intento de cancelación no permitido.")
        print("10. Cancelación no permitida controlada:", error)
    operaciones += 1

    print(f"\nTotal de operaciones ejecutadas: {operaciones}")
    print("El programa continúa funcionando después de los errores.")
    print("Los eventos y errores se registraron en software_fj.log")
    print("=====================================================\n")

# ---------------------------------------------------------
# 10. INTERFAZ GRÁFICA CON TKINTER
# ---------------------------------------------------------

class AplicacionSoftwareFJ:
    def __init__(self, ventana):
        self.sistema = SistemaSoftwareFJ()
        self.ventana = ventana
        self.ventana.title("Software FJ - Gestión de clientes y reservas")
        self.ventana.geometry("900x650")
        self.ventana.minsize(780, 570)

        self.crear_interfaz()

    def crear_interfaz(self):
        titulo = ttk.Label(
            self.ventana,
            text="SISTEMA INTEGRAL SOFTWARE FJ",
            font=("Arial", 17, "bold")
        )
        titulo.pack(pady=12)

        subtitulo = ttk.Label(
            self.ventana,
            text="Gestión de clientes, servicios y reservas",
            font=("Arial", 10)
        )
        subtitulo.pack(pady=2)

        # Sección para registrar clientes.
        marco_cliente = ttk.LabelFrame(
            self.ventana, text="Registro de clientes", padding=10
        )
        marco_cliente.pack(fill="x", padx=15, pady=8)

        self.identificacion = self.crear_campo(marco_cliente, "Identificación:", 0)
        self.nombre = self.crear_campo(marco_cliente, "Nombre completo:", 1)
        self.correo = self.crear_campo(marco_cliente, "Correo electrónico:", 2)
        self.telefono = self.crear_campo(marco_cliente, "Teléfono:", 3)

        ttk.Button(
            marco_cliente,
            text="Registrar cliente",
            command=self.registrar_cliente
        ).grid(row=4, column=0, columnspan=2, pady=8)

        # Sección para crear reservas.
        marco_reserva = ttk.LabelFrame(
            self.ventana, text="Crear reserva", padding=10
        )
        marco_reserva.pack(fill="x", padx=15, pady=8)

        ttk.Label(marco_reserva, text="Cliente:").grid(
            row=0, column=0, padx=5, pady=5, sticky="w"
        )
        self.combo_cliente = ttk.Combobox(
            marco_reserva, state="readonly", width=30
        )
        self.combo_cliente.grid(row=0, column=1, padx=5, pady=5)

        ttk.Label(marco_reserva, text="Servicio:").grid(
            row=1, column=0, padx=5, pady=5, sticky="w"
        )
        self.combo_servicio = ttk.Combobox(
            marco_reserva,
            state="readonly",
            width=30,
            values=[servicio.nombre for servicio in self.sistema.servicios]
        )
        self.combo_servicio.grid(row=1, column=1, padx=5, pady=5)
        self.combo_servicio.current(0)

        ttk.Label(marco_reserva, text="Duración (horas o días):").grid(
            row=2, column=0, padx=5, pady=5, sticky="w"
        )
        self.duracion = ttk.Entry(marco_reserva, width=33)
        self.duracion.grid(row=2, column=1, padx=5, pady=5)

        ttk.Label(marco_reserva, text="Descuento (%):").grid(
            row=3, column=0, padx=5, pady=5, sticky="w"
        )
        self.descuento = ttk.Entry(marco_reserva, width=33)
        self.descuento.insert(0, "0")
        self.descuento.grid(row=3, column=1, padx=5, pady=5)

        ttk.Button(
            marco_reserva,
            text="Crear y confirmar reserva",
            command=self.crear_reserva
        ).grid(row=4, column=0, columnspan=2, pady=8)

        # Tabla para mostrar las reservas.
        marco_tabla = ttk.LabelFrame(
            self.ventana, text="Reservas registradas", padding=10
        )
        marco_tabla.pack(fill="both", expand=True, padx=15, pady=8)

        columnas = ("codigo", "cliente", "servicio", "cantidad", "estado", "total")
        self.tabla = ttk.Treeview(
            marco_tabla, columns=columnas, show="headings", height=8
        )

        encabezados = {
            "codigo": "Código",
            "cliente": "Cliente",
            "servicio": "Servicio",
            "cantidad": "Duración",
            "estado": "Estado",
            "total": "Total"
        }

        for columna, texto in encabezados.items():
            self.tabla.heading(columna, text=texto)
            self.tabla.column(columna, width=125, anchor="center")

        self.tabla.pack(fill="both", expand=True)

        marco_botones = ttk.Frame(self.ventana)
        marco_botones.pack(pady=8)

        ttk.Button(
            marco_botones,
            text="Cancelar reserva seleccionada",
            command=self.cancelar_reserva
        ).pack(side="left", padx=5)

        ttk.Button(
            marco_botones,
            text="Procesar reserva seleccionada",
            command=self.procesar_reserva
        ).pack(side="left", padx=5)

        ttk.Button(
            marco_botones,
            text="Ejecutar 10 pruebas",
            command=self.pruebas
        ).pack(side="left", padx=5)

    def crear_campo(self, marco, texto, fila):
        ttk.Label(marco, text=texto).grid(
            row=fila, column=0, padx=5, pady=4, sticky="w"
        )
        campo = ttk.Entry(marco, width=35)
        campo.grid(row=fila, column=1, padx=5, pady=4)
        return campo

    def registrar_cliente(self):
        try:
            cliente = self.sistema.registrar_cliente(
                self.identificacion.get(),
                self.nombre.get(),
                self.correo.get(),
                self.telefono.get()
            )
        except ErrorSistema as error:
            logging.exception("Error al registrar cliente.")
            messagebox.showerror("Error de registro", str(error))
        except Exception as error:
            logging.exception("Error inesperado al registrar cliente.")
            messagebox.showerror("Error inesperado", str(error))
        else:
            self.actualizar_clientes()
            messagebox.showinfo(
                "Registro exitoso",
                f"El cliente {cliente.nombre} fue registrado correctamente."
            )
            self.identificacion.delete(0, tk.END)
            self.nombre.delete(0, tk.END)
            self.correo.delete(0, tk.END)
            self.telefono.delete(0, tk.END)
        finally:
            logging.info("Finalizó el intento de registro de cliente.")

    def actualizar_clientes(self):
        self.combo_cliente["values"] = [
            f"{cliente.identificacion} - {cliente.nombre}"
            for cliente in self.sistema.clientes
        ]
        if self.sistema.clientes:
            self.combo_cliente.current(0)

    def crear_reserva(self):
        try:
            if self.combo_cliente.current() == -1:
                raise DatoInvalidoError("Primero debe registrar y seleccionar un cliente.")

            if self.combo_servicio.current() == -1:
                raise DatoInvalidoError("Debe seleccionar un servicio.")

            cantidad = float(self.duracion.get())
            descuento = float(self.descuento.get())

            if not 0 <= descuento <= 100:
                raise DatoInvalidoError("El descuento debe estar entre 0 y 100.")

            reserva = self.sistema.crear_reserva(
                self.combo_cliente.current(),
                self.combo_servicio.current(),
                cantidad,
                descuento
            )

        except ValueError as error:
            logging.exception("Se ingresó un valor numérico incorrecto.")
            messagebox.showerror(
                "Dato inválido", "La duración y el descuento deben ser números."
            )
        except ErrorSistema as error:
            logging.exception("Error al crear reserva.")
            messagebox.showerror("No se pudo crear la reserva", str(error))
        except Exception as error:
            logging.exception("Error inesperado al crear reserva.")
            messagebox.showerror("Error inesperado", str(error))
        else:
            self.actualizar_tabla()
            messagebox.showinfo(
                "Reserva confirmada",
                f"Código: {reserva.identificacion}\n"
                f"Servicio: {reserva.servicio.nombre}\n"
                f"Total con impuesto: ${reserva.costo:,.0f}"
            )
            self.duracion.delete(0, tk.END)
            self.descuento.delete(0, tk.END)
            self.descuento.insert(0, "0")
        finally:
            logging.info("Finalizó el intento de creación de reserva.")

    def obtener_reserva_seleccionada(self):
        seleccion = self.tabla.selection()
        if not seleccion:
            raise ReservaError("Seleccione una reserva de la tabla.")

        codigo = self.tabla.item(seleccion[0], "values")[0]
        for reserva in self.sistema.reservas:
            if reserva.identificacion == codigo:
                return reserva

        raise ReservaError("No se encontró la reserva seleccionada.")

    def cancelar_reserva(self):
        try:
            reserva = self.obtener_reserva_seleccionada()
            reserva.cancelar()
        except ErrorSistema as error:
            logging.exception("No fue posible cancelar la reserva.")
            messagebox.showerror("Error", str(error))
        else:
            self.actualizar_tabla()
            messagebox.showinfo("Reserva", "La reserva fue cancelada.")
        finally:
            logging.info("Finalizó el intento de cancelación.")

    def procesar_reserva(self):
        try:
            reserva = self.obtener_reserva_seleccionada()
            reserva.procesar()
        except ErrorSistema as error:
            logging.exception("No fue posible procesar la reserva.")
            messagebox.showerror("Error", str(error))
        else:
            self.actualizar_tabla()
            messagebox.showinfo("Reserva", "La reserva fue procesada correctamente.")
        finally:
            logging.info("Finalizó el intento de procesamiento.")

    def actualizar_tabla(self):
        for elemento in self.tabla.get_children():
            self.tabla.delete(elemento)

        for reserva in self.sistema.reservas:
            self.tabla.insert(
                "",
                tk.END,
                values=(
                    reserva.identificacion,
                    reserva.cliente.nombre,
                    reserva.servicio.nombre,
                    reserva.duracion,
                    reserva.estado,
                    f"${reserva.costo:,.0f}"
                )
            )

    def pruebas(self):
        ejecutar_pruebas()
        messagebox.showinfo(
            "Pruebas ejecutadas",
            "Se ejecutaron 10 operaciones de prueba.\n"
            "Consulte la terminal y el archivo software_fj.log."
        )

# ---------------------------------------------------------
# 11. INICIO DEL PROGRAMA
# ---------------------------------------------------------

if __name__ == "__main__":
    try:
        ventana_principal = tk.Tk()
        aplicacion = AplicacionSoftwareFJ(ventana_principal)
        ventana_principal.mainloop()
    except Exception as error:
        logging.exception("Error crítico al iniciar la aplicación.")
        print("No fue posible iniciar la aplicación:", error)


















