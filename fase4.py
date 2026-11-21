# Importamos esto únicamente para poder crear clases "plantilla" (abstractas)
from abc import ABC, abstractmethod


# GUARDAR LOGS (Archivos básicos)
def guardar_log(mensaje):
    """
    Guarda un mensaje en un archivo de texto.
    Usamos la letra 'a' (append) para que agregue texto al final sin borrar lo anterior.
    """
    try:
        with open("registro_errores.txt", "a", encoding="utf-8") as archivo:
            archivo.write(str(mensaje) + "\n")
    except Exception as e:
        print("Error al intentar guardar en el archivo de texto:", e)

# CREAR LOS PROPIOS ERRORES
class ErrorSoftwareFJ(Exception):
    """Error base del sistema."""
    pass

class ErrorDatoInvalido(ErrorSoftwareFJ):
    """Se usa cuando un dato recibido no cumple la validación necesaria."""
    pass

class ErrorNoDisponible(ErrorSoftwareFJ):
    """Se usa cuando se intenta reservar o usar un servicio que ya está ocupado."""
    pass

class EntidadGeneral(ABC):
    """Esta es una clase abstracta. No podemos crear objetos directamente de ella.
    Sirve para heredar el 'id_codigo' a Clientes y Servicios
    """

    def __init__(self, id_codigo):
        if id_codigo is None or str(id_codigo).strip() == "":
            raise ErrorDatoInvalido("El código no puede estar vacío.")
        self.id_codigo = str(id_codigo).strip()

    @abstractmethod
    def mostrar_detalles(self):
        # Al poner @abstractmethod, obligamos a los "hijos" a escribir esta función
        pass

class Servicio(EntidadGeneral):
    def __init__(self, id_codigo, nombre_servicio, precio_base):
        # super().__init__ llama al constructor del padre (EntidadGeneral)
        super().__init__(id_codigo)
        if nombre_servicio is None or str(nombre_servicio).strip() == "":
            raise ErrorDatoInvalido("El nombre del servicio no puede estar vacío.")
        try:
            precio_base = float(precio_base)
        except (TypeError, ValueError):
            raise ErrorDatoInvalido("El precio base debe ser un valor numérico.")
        if precio_base < 0:
            raise ErrorDatoInvalido("El precio base no puede ser negativo.")

        self.nombre_servicio = str(nombre_servicio).strip()
        self.precio_base = precio_base
        self.esta_disponible = True  # Por defecto, todo servicio nuevo está disponible

    def reservar(self):
        if not self.esta_disponible:
            raise ErrorNoDisponible(f"El servicio {self.id_codigo} no está disponible.")
        self.esta_disponible = False
        guardar_log(f"Reservado: {self.id_codigo} - {self.nombre_servicio}")
        return True

    def liberar(self):
        self.esta_disponible = True
        guardar_log(f"Liberado: {self.id_codigo} - {self.nombre_servicio}")
        return True

    @abstractmethod
    def calcular_costo_total(self, *args, **kwargs):
        # Cada servicio (Sala, Equipo, Asesoría) calculará su costo diferente
        pass

    def mostrar_detalles(self):
        estado = "Disponible" if self.esta_disponible else "No disponible"
        return (
            f"Servicio {self.id_codigo}: {self.nombre_servicio} | "
            f"Precio base: ${self.precio_base:.2f} | Estado: {estado}"
        )

class Cliente(EntidadGeneral):
    def __init__(self, id_codigo, nombre, telefono=None):
        super().__init__(id_codigo)
        if nombre is None or str(nombre).strip() == "":
            raise ErrorDatoInvalido("El nombre del cliente no puede estar vacío.")
        self.nombre = str(nombre).strip()
        self.telefono = telefono
        self.servicios_reservados = []

    def reservar_servicio(self, servicio):
        if not isinstance(servicio, Servicio):
            raise ErrorDatoInvalido("Debe reservar un objeto de tipo Servicio.")
        servicio.reservar()
        self.servicios_reservados.append(servicio)
        guardar_log(f"Cliente {self.id_codigo} reservó {servicio.id_codigo}")
        return servicio

    def mostrar_detalles(self):
        telefono = self.telefono if self.telefono is not None else "Sin teléfono"
        return f"Cliente {self.id_codigo}: {self.nombre} | Teléfono: {telefono}"

class Sala(Servicio):
    def __init__(self, id_codigo, nombre_servicio, precio_base, capacidad, tarifa_extra=0):
        super().__init__(id_codigo, nombre_servicio, precio_base)
        try:
            self.capacidad = int(capacidad)
        except (TypeError, ValueError):
            raise ErrorDatoInvalido("La capacidad debe ser un número entero.")
        if self.capacidad <= 0:
            raise ErrorDatoInvalido("La capacidad debe ser mayor que cero.")
        try:
            self.tarifa_extra = float(tarifa_extra)
        except (TypeError, ValueError):
            raise ErrorDatoInvalido("La tarifa extra debe ser numérica.")

    def calcular_costo_total(self, horas=1, numero_personas=1):
        if horas <= 0 or numero_personas <= 0:
            raise ErrorDatoInvalido("Las horas y la cantidad de personas deben ser positivas.")
        costo = self.precio_base * horas
        if numero_personas > self.capacidad:
            costo += self.tarifa_extra * (numero_personas - self.capacidad)
        return round(costo, 2)

    def mostrar_detalles(self):
        return (
            f"Sala {self.id_codigo}: {self.nombre_servicio} | "
            f"Capacidad: {self.capacidad} | Precio base: ${self.precio_base:.2f} | "
            f"Estado: {'Disponible' if self.esta_disponible else 'No disponible'}"
        )

class Equipo(Servicio):
    def __init__(self, id_codigo, nombre_servicio, precio_base, cantidad_disponible):
        super().__init__(id_codigo, nombre_servicio, precio_base)
        try:
            self.cantidad_disponible = int(cantidad_disponible)
        except (TypeError, ValueError):
            raise ErrorDatoInvalido("La cantidad disponible debe ser un número entero.")
        if self.cantidad_disponible <= 0:
            raise ErrorDatoInvalido("La cantidad disponible debe ser mayor que cero.")

    def calcular_costo_total(self, cantidad=1, dias=1):
        if cantidad <= 0 or dias <= 0:
            raise ErrorDatoInvalido("La cantidad y los días deben ser positivos.")
        if cantidad > self.cantidad_disponible:
            raise ErrorNoDisponible("No hay suficientes unidades disponibles para esa cantidad.")
        return round(self.precio_base * dias * cantidad, 2)

    def mostrar_detalles(self):
        return (
            f"Equipo {self.id_codigo}: {self.nombre_servicio} | "
            f"Unidades disponibles: {self.cantidad_disponible} | "
            f"Precio base: ${self.precio_base:.2f} | "
            f"Estado: {'Disponible' if self.esta_disponible else 'No disponible'}"
        )
class Asesoria(Servicio):
    def __init__(self, id_codigo, nombre_servicio, precio_base, tarifa_hora=0):
        super().__init__(id_codigo, nombre_servicio, precio_base)
        try:
            self.tarifa_hora = float(tarifa_hora)
        except (TypeError, ValueError):
            raise ErrorDatoInvalido("La tarifa por hora debe ser numérica.")
        if self.tarifa_hora < 0:
            raise ErrorDatoInvalido("La tarifa por hora no puede ser negativa.")

    def calcular_costo_total(self, horas=1):
        if horas <= 0:
            raise ErrorDatoInvalido("Las horas deben ser mayores que cero.")
        return round((self.precio_base + self.tarifa_hora) * horas, 2)

    def mostrar_detalles(self):
        return (
            f"Asesoría {self.id_codigo}: {self.nombre_servicio} | "
            f"Tarifa por hora: ${self.tarifa_hora:.2f} | "
            f"Precio base: ${self.precio_base:.2f} | "
            f"Estado: {'Disponible' if self.esta_disponible else 'No disponible'}"
        )
class Reserva:
    def __init__(self, cliente, servicio, cantidad=1, detalle=""):
        if not isinstance(cliente, Cliente):
            raise ErrorDatoInvalido("El cliente de la reserva es inválido.")
        if not isinstance(servicio, Servicio):
            raise ErrorDatoInvalido("El servicio de la reserva es inválido.")
        self.cliente = cliente
        self.servicio = servicio
        self.cantidad = cantidad
        self.detalle = detalle

        if isinstance(servicio, Sala):
            self.total = servicio.calcular_costo_total(horas=self.cantidad, numero_personas=1)
        elif isinstance(servicio, Equipo):
            self.total = servicio.calcular_costo_total(cantidad=self.cantidad, dias=1)
        elif isinstance(servicio, Asesoria):
            self.total = servicio.calcular_costo_total(horas=self.cantidad)
        else:
            self.total = servicio.precio_base * self.cantidad

    def mostrar_detalles(self):
        return (
            f"Reserva: cliente {self.cliente.id_codigo}, servicio {self.servicio.id_codigo}, "
            f"cantidad {self.cantidad}, total ${self.total:.2f}."
        )


# Pequeña prueba para ver que el Log funciona
if __name__ == "__main__":
    print("realizo el archivo de prueba de log")
    guardar_log("PRIMERAS PRUEBAS - Se han cargado las clases base correctamente")


class Cliente(EntidadGeneral):
    def __init__(self, id_codigo, nombre, correo):
        super().__init__(id_codigo)  # El padre (EntidadGeneral) guarda el ID
        
        # ENCAPSULAMIENTO: Poner dos guiones bajos (__) antes del nombre 
        # hace que la variable sea "privada". No se puede modificar desde afuera.
        self.__nombre = nombre
        self.__correo = correo
        
    # Como las variables son privadas, creamos funciones para poder verlas (GET)
    def get_nombre(self):
        return self.__nombre
        
    def get_correo(self):
        return self.__correo
        
    # Y funciones para poder modificarlas de forma segura (SET)
    def set_correo(self, nuevo_correo):
        # Aquí metemos una validación estricta usando nuestra propia excepción
        if "@" not in nuevo_correo:
            raise ErrorDatoInvalido(f"El correo '{nuevo_correo}' no es válido. Falta el @.")
        self.__correo = nuevo_correo

    # Cumplimos con el contrato del padre de implementar esta función
    def mostrar_detalles(self):
        return f"Cliente: {self.__nombre} (ID: {self.id_codigo}) - Correo: {self.__correo}"



# SERVICIO 1: Salas
class ReservaSala(Servicio):
    def __init__(self, id_codigo, nombre_servicio, precio_base, capacidad):
        super().__init__(id_codigo, nombre_servicio, precio_base)
        self.capacidad = capacidad
        
    # POLIMORFISMO: Cada servicio calcula su costo a su manera
    def calcular_costo_total(self, horas):
        # La sala cobra por hora + un 10% de tarifa de limpieza
        costo = self.precio_base * horas
        return costo * 1.10
        
    def mostrar_detalles(self):
        return f"Sala: {self.nombre_servicio} (Capacidad: {self.capacidad} pers.)"


# SERVICIO 2: Equipos
class AlquilerEquipo(Servicio):
    def __init__(self, id_codigo, nombre_servicio, precio_base, tipo_equipo):
        super().__init__(id_codigo, nombre_servicio, precio_base)
        self.tipo_equipo = tipo_equipo
        
    def calcular_costo_total(self, dias):
        # El equipo cobra por día. Si son más de 3 días, hay 5% de descuento
        costo = self.precio_base * dias
        if dias > 3:
            costo = costo * 0.95
        return costo
        
    def mostrar_detalles(self):
        return f"Equipo: {self.nombre_servicio} ({self.tipo_equipo})"


# SERVICIO 3: Asesorías
class Asesoria(Servicio):
    def __init__(self, id_codigo, nombre_servicio, precio_base, experto):
        super().__init__(id_codigo, nombre_servicio, precio_base)
        self.experto = experto
        
    def calcular_costo_total(self, sesiones):
        # Las asesorías tienen un costo fijo por sesión, sin impuestos ni descuentos extra
        return self.precio_base * sesiones
        
    def mostrar_detalles(self):
        return f"Asesoría: {self.nombre_servicio} - Impartida por: {self.experto}"


if __name__ == "__main__":

    try:
        # Creamos un cliente
        mi_cliente = Cliente("C001", "Luis", "luis@correo.com")
        print(mi_cliente.mostrar_detalles())
        
        # Intentamos ponerle un correo malo para ver si nuestra excepción funciona

        # Creamos una sala y calculamos su costo (ej. 2 horas a 50000 la hora)
        mi_sala = ReservaSala("S001", "Sala de Juntas A", 50000, 10)
        costo_sala = mi_sala.calcular_costo_total(2)
        print(mi_sala.mostrar_detalles())
        print(f"Costo por 2 horas (con limpieza): ${costo_sala}")
        
    except ErrorSoftwareFJ as error:
        print(f"Ocurrió un error en el sistema: {error}")
        guardar_log(f"ERROR para commit 2: {error}")