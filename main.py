from sistema import AlquilerEquipo, Asesoria, GestorSistema, ReservaSala, Servicio
from sistema.excepciones import SoftwareFJError  # Excepción base del sistema
from sistema.logger import ARCHIVO_LOG, log  # Logger y ruta del archivo de logs

# Contadores globales para el resumen final
exitosas = 0
fallidas = 0


def ejecutar(numero, descripcion, operacion):
    """
    Ejecuta una operación de forma segura. Cualquier error se muestra,
    se registra en el log y el programa CONTINÚA con la siguiente.
    """
    # Permite modificar los contadores globales
    global exitosas, fallidas
    # Encabezado de la operación
    print(f"\n--- Operación {numero:02d}: {descripcion}")
    try:
        # Ejecuta la función recibida
        resultado = operacion()
    except SoftwareFJError as error:
        # Error controlado del sistema
        fallidas += 1
        print(f"    ✗ ERROR CONTROLADO {error}")
        # Si el error fue encadenado, se muestra también la causa original
        if error.__cause__ is not None:
            print(f"      ↳ Causa original: {type(error.__cause__).__name__}: {error.__cause__}")
        log.warning(f"Operación {numero:02d} fallida de forma controlada: {error}")
    except Exception as error:  # noqa: BLE001 - red de seguridad final
        # Error inesperado: también se captura para que el sistema no se detenga
        fallidas += 1
        print(f"    ✗ ERROR DE PYTHON CAPTURADO {type(error).__name__}: {error}")
        log.critical(f"Operación {numero:02d} con error inesperado: {type(error).__name__}: {error}")
    else:
        # Solo se ejecuta si la operación terminó sin errores
        exitosas += 1
        print(f"    ✓ OK -> {resultado}")
        log.info(f"Operación {numero:02d} completada: {descripcion}")


def main():
    """Simula el funcionamiento completo del sistema."""
    # Crea el gestor que contiene las listas internas
    gestor = GestorSistema()
    # Diccionario para compartir objetos creados entre operaciones
    datos = {}

    print("=" * 60)
    print("   SOFTWARE FJ - Sistema de Gestión de Clientes y Reservas")
    print("=" * 60)

    # ------------------------- CLIENTES -------------------------
    ejecutar(1, "Registrar cliente válido (Ana Gómez)",
             lambda: gestor.registrar_cliente("Ana Gómez", "1012345678", "ana.gomez@mail.com", "3001234567"))
    ejecutar(2, "Registrar cliente válido (Carlos Ruiz)",
             lambda: gestor.registrar_cliente("Carlos Ruiz", "79876543", "carlos@empresa.co", "3157654321"))
    ejecutar(3, "Registrar cliente con correo inválido",
             lambda: gestor.registrar_cliente("Laura Pérez", "52123456", "laura-arroba-mail", "3009876543"))
    ejecutar(4, "Registrar cliente con documento no numérico",
             lambda: gestor.registrar_cliente("Pedro Díaz", "ABC123", "pedro@mail.com", "3201112233"))
    ejecutar(5, "Registrar cliente duplicado (mismo documento de Ana)",
             lambda: gestor.registrar_cliente("Ana María", "1012345678", "otra@mail.com", "3001112222"))

    # ------------------------- SERVICIOS ------------------------
    def crear_sala():
        # Crea una sala válida y la guarda para usarla después
        datos["sala"] = gestor.agregar_servicio(ReservaSala, "Sala Innovación", 50000, capacidad=25)
        return datos["sala"].describir()

    def crear_equipo():
        # Crea un alquiler de equipos válido
        datos["equipo"] = gestor.agregar_servicio(AlquilerEquipo, "Portátiles Dell", 15000, "portatil", 5)
        return datos["equipo"].describir()

    def crear_asesoria():
        # Crea una asesoría válida
        datos["asesoria"] = gestor.agregar_servicio(Asesoria, "Asesoría Cloud", 80000, "Computación en la nube", "senior")
        return datos["asesoria"].describir()

    ejecutar(6, "Crear servicio de sala válido", crear_sala)
    ejecutar(7, "Crear servicio de alquiler de equipos válido", crear_equipo)
    ejecutar(8, "Crear servicio de asesoría válido", crear_asesoria)
    ejecutar(9, "Crear alquiler de equipos con cantidad 0",
             lambda: gestor.agregar_servicio(AlquilerEquipo, "Proyectores", 20000, "proyector", 0))
    ejecutar(10, "Crear asesoría con nivel inexistente",
             lambda: gestor.agregar_servicio(Asesoria, "Asesoría Datos", 70000, "Big Data", "maestro"))
    ejecutar(11, "Crear sala con tarifa no numérica (encadenamiento)",
             lambda: gestor.agregar_servicio(ReservaSala, "Sala Norte", "cincuenta mil", capacidad=10))
    ejecutar(12, "Crear asesoría con parámetros faltantes",
             lambda: gestor.agregar_servicio(Asesoria, "Asesoría Incompleta", 60000))
    ejecutar(13, "Instanciar la clase abstracta Servicio directamente",
             lambda: Servicio("Genérico", 1000))

    # ------------------------- RESERVAS -------------------------
    def reserva_sala_exitosa():
        # Crea, confirma y procesa una reserva con IVA del 19 %
        reserva = gestor.crear_reserva("1012345678", datos["sala"], 3)
        reserva.confirmar()
        reserva.procesar(impuesto=0.19)
        datos["reserva_procesada"] = reserva
        return str(reserva)

    def reserva_asesoria_con_descuento():
        # Reserva con descuento del 10 % e IVA (método sobrecargado)
        reserva = gestor.crear_reserva("79876543", datos["asesoria"], 2)
        reserva.confirmar()
        reserva.procesar(impuesto=0.19, descuento=0.10)
        return str(reserva)

    def reserva_servicio_no_disponible():
        # Desactiva el equipo y luego intenta confirmar una reserva
        datos["equipo"].cambiar_disponibilidad(False)
        reserva = gestor.crear_reserva("79876543", datos["equipo"], 4)
        return reserva.confirmar()

    def reserva_pendiente_para_cancelar():
        # Crea una reserva y la deja pendiente para cancelarla después
        datos["reserva_pendiente"] = gestor.crear_reserva("79876543", datos["sala"], 2)
        return str(datos["reserva_pendiente"])

    def procesar_con_descuento_invalido():
        # Crea y confirma una reserva y luego aplica un descuento del 150 %
        reserva = gestor.crear_reserva("1012345678", datos["asesoria"], 1)
        reserva.confirmar()
        return reserva.procesar(impuesto=0.19, descuento=1.5)

    ejecutar(14, "Reserva de sala exitosa (crear, confirmar y procesar)", reserva_sala_exitosa)
    ejecutar(15, "Reserva de asesoría con descuento del 10 %", reserva_asesoria_con_descuento)
    ejecutar(16, "Reserva de un servicio no disponible", reserva_servicio_no_disponible)
    ejecutar(17, "Reserva con duración negativa (encadenamiento)",
             lambda: gestor.crear_reserva("1012345678", datos["sala"], -2))
    ejecutar(18, "Reserva de sala que supera las 12 horas permitidas",
             lambda: gestor.crear_reserva("1012345678", datos["sala"], 15))
    ejecutar(19, "Reserva para un cliente no registrado",
             lambda: gestor.crear_reserva("99999999", datos["sala"], 2))
    ejecutar(20, "Cancelar una reserva ya procesada",
             lambda: datos["reserva_procesada"].cancelar("Cambio de planes"))
    ejecutar(21, "Procesar reserva con descuento del 150 % (cálculo inconsistente)",
             procesar_con_descuento_invalido)
    ejecutar(22, "Crear una reserva pendiente", reserva_pendiente_para_cancelar)
    ejecutar(23, "Cancelar la reserva pendiente",
             lambda: datos["reserva_pendiente"].cancelar("El cliente lo solicitó") or str(datos["reserva_pendiente"]))

    # ------------------------- RESUMEN --------------------------
    print(gestor.resumen())
    print("\n" + "=" * 60)
    print(f"Operaciones exitosas: {exitosas} | Operaciones con error controlado: {fallidas}")
    print(f"El sistema terminó sin interrupciones. Log: {ARCHIVO_LOG}")
    print("=" * 60)
    log.info(f"===== Fin de la simulación: {exitosas} exitosas, {fallidas} fallidas =====")


# Ejecuta main() solo si el archivo se ejecuta directamente
if __name__ == "__main__":
    main()














