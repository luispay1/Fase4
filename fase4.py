# Importamos esto únicamente para poder crear clases "plantilla" (abstractas)
from abc import ABC, abstractmethod


#GUARDAR LOGS (Archivos básicos)

def guardar_log(mensaje):
    """
    Guarda un mensaje en un archivo de texto.
    Usamos la letra 'a' (append) para que agregue texto al final sin borrar lo anterior.
    """
    try:
        archivo = open("registro_errores.txt", "a", encoding="utf-8")
        archivo.write(mensaje + "\n")
        archivo.close()
    except Exception as e:
        print("Error al intentar guardar en el archivo de texto:", e)

#CREAR LOS PROPIOS ERRORES

#errores heredando de 'Exception'.
class ErrorSoftwareFJ(Exception):
    #Este será nuestro error principal
    pass

class ErrorDatoInvalido(ErrorSoftwareFJ):
    #Lo usaremos si nos envían un texto cuando pedimos un número, por ejemplo
    pass

class ErrorNoDisponible(ErrorSoftwareFJ):
    #Lo usaremos si alguien intenta reservar algo que ya está ocupado
    pass

#CLASES ABSTRACTAS (Plantillas)

class EntidadGeneral(ABC):
    """Esta es una clase abstracta. No podemos crear objetos directamente de ella.
    Sirve para heredar el 'id_codigo' a Clientes y Servicios"""
    def __init__(self, id_codigo):
        self.id_codigo = id_codigo
    
    @abstractmethod
    def mostrar_detalles(self):
        #Al poner @abstractmethod, obligamos a los "hijos" a escribir esta función
        pass


class Servicio(EntidadGeneral):
    def __init__(self, id_codigo, nombre_servicio, precio_base):
        #super().__init__ llama al constructor del padre (EntidadGeneral)
        super().__init__(id_codigo)
        self.nombre_servicio = nombre_servicio
        self.precio_base = precio_base
        self.esta_disponible = True # Por defecto, todo servicio nuevo está disponible
        
    @abstractmethod
    def calcular_costo_total(self):
        # Cada servicio (Sala, Equipo, Asesoría) calculará su costo diferente
        pass

# Pequeña prueba para ver que el Log funciona
if __name__ == "__main__":
    print("realizo el archivo de prueba de log")
    guardar_log("PRIMERAS PRUEBAS - Se han cargado las clases base correctamente")
