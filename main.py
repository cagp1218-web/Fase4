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
