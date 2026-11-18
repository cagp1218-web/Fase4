from sistema import AlquilerEquipo, Asesoria, GestorSistema, ReservaSala, Servicio
from sistema.excepciones import SoftwareFJError  # Excepción base del sistema
from sistema.logger import ARCHIVO_LOG, log  # Logger y ruta del archivo de logs

# Contadores globales para el resumen final
exitosas = 0
fallidas = 0


def ejecutar(numero, descripcion, operacion):
   
