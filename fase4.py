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
        mi_cliente.set_correo("luis_sin_arroba.com")
        # Intentamos ponerle un correo malo para ver si nuestra excepción funciona

        # Creamos una sala y calculamos su costo (ej. 2 horas a 50000 la hora)
        mi_sala = ReservaSala("S001", "Sala de Juntas A", 50000, 10)
        costo_sala = mi_sala.calcular_costo_total(2)
        print(mi_sala.mostrar_detalles())
        print(f"Costo por 2 horas (con limpieza): ${costo_sala}")
        
    except ErrorSoftwareFJ as error:
        print(f"Ocurrió un error en el sistema: {error}")
        guardar_log(f"ERROR para commit 2: {error}")

class Reserva:
    def __init__(self, id_reserva, cliente, servicio, tiempo):

        self.id_reserva = id_reserva
        self.cliente = cliente
        self.servicio = servicio
        self.tiempo = tiempo
        self.estado = "Pendiente" # Estados: Pendiente, Confirmada, Cancelada
        self.costo_total = 0.0

    def confirmar_reserva(self):
        
        """Confirma la reserva pero primero hace validaciones estrictas."""
        
        # Validación 1: ¿El servicio está disponible?
        if not self.servicio.esta_disponible:
            # Aquí usamos el error que creamos en el Día 1
            mensaje = f"Error: El servicio {self.servicio.nombre_servicio} no está disponible."
            guardar_log(f"FALLO DE RESERVA - {mensaje}")
            raise ErrorNoDisponible(mensaje)

        # Si pasamos la validación, calculamos el costo y ocupamos el servicio
        self.costo_total = self.servicio.calcular_costo_total(self.tiempo)
        self.servicio.esta_disponible = False # Lo marcamos como ocupado
        self.estado = "Confirmada"
        
        # Guardamos en el archivo de texto que todo salió bien
        log_msg = (f"Reserva {self.id_reserva} CONFIRMADA - "
                   f"Cliente: {self.cliente.get_nombre()} - "
                   f"Servicio: {self.servicio.nombre_servicio} - "
                   f"Total: ${self.costo_total}")
        guardar_log(log_msg)
        return log_msg

    def cancelar_reserva(self, motivo_cancelacion=None):
        """
        Cancela la reserva. Si no se pasa un motivo, asume "Sin especificar".
        """
        if self.estado == "Cancelada":
            raise ErrorSoftwareFJ(f"La reserva {self.id_reserva} ya estaba cancelada.")
            
        self.estado = "Cancelada"
        self.servicio.esta_disponible = True # Volvemos a liberar el servicio
        
        # Aquí decidimos qué mensaje guardar dependiendo de si nos dieron un motivo o no
        if motivo_cancelacion is None:
            razon = "Sin especificar"
        else:
            razon = motivo_cancelacion
            
        mensaje = f"Reserva {self.id_reserva} CANCELADA. Motivo: {razon}"
        guardar_log(mensaje)
        return mensaje

    def mostrar_reserva(self):
        return (f"Reserva [{self.id_reserva}] | Estado: {self.estado} | "
                f"{self.cliente.get_nombre()} reservó {self.servicio.nombre_servicio}")

if __name__ == "__main__":
    print("\nmi 4 commit de reserva con error")
    try:
        # 1. Usamos el cliente y la sala
        cliente1 = Cliente("C002", "Ana", "ana@correo.com")
        sala1 = ReservaSala("S002", "Sala VIP", 100000, 5)
        
        # 2. Creamos la reserva (Ana reserva la sala por 3 horas)
        reserva1 = Reserva("R001", cliente1, sala1, 3)
        print(reserva1.mostrar_reserva())
        
        # 3. Confirmamos la reserva (esto calcula el costo y la marca ocupada)
        print(reserva1.confirmar_reserva())
        
        # 4. Probamos el manejo de errores:
        # Intentamos que OTRO cliente reserve la MISMA sala que ya ocupó Ana
        cliente2 = Cliente("C003", "Carlos", "carlos@correo.com")
        reserva_fallida = Reserva("R002", cliente2, sala1, 2)
        
        print("\nIntentando reservar una sala ocupada...")
        reserva_fallida.confirmar_reserva() # ¡Esto va a lanzar el ErrorNoDisponible!

    except ErrorSoftwareFJ as error:
        # Atrapamos nuestro error personalizado
        print(f"-> el sistema bloqueo la accion: {error}")
        
    print("\nRevisa tu archivo 'registro_errores.txt' para ver los movimientos.")

class GestorSoftwareFJ:
    def __init__(self):
        # Aquí guardaremos nuestros objetos en memoria (sin bases de datos)
        self.lista_clientes = []
        self.lista_servicios = []
        self.lista_reservas = []

    def registrar_cliente(self, cliente):
        """Añade un objeto Cliente a la lista interna."""
        self.lista_clientes.append(cliente)
        guardar_log(f"Cliente registrado: {cliente.get_nombre()}")

    def registrar_servicio(self, servicio):
        """Añade un objeto Servicio a la lista interna."""
        self.lista_servicios.append(servicio)
        guardar_log(f"Servicio registrado: {servicio.nombre_servicio}")

    def buscar_cliente(self, id_buscar):
        """
        Busca un cliente por su ID en la lista.
        Utiliza try/except/else/finally para demostrar manejo avanzado de errores.
        """
        print(f"\n--- Iniciando búsqueda del cliente ID: {id_buscar} ---")
        cliente_encontrado = None

        try:
            # TRY: Intentamos buscar
            # Si el ID buscar está vacío o no es texto, forzamos un error
            if not id_buscar or not isinstance(id_buscar, str):
                raise ErrorDatoInvalido("El ID de búsqueda debe ser un texto válido.")

            # Recorremos la lista buscando el ID
            for cliente in self.lista_clientes:
                if cliente.id_codigo == id_buscar:
                    cliente_encontrado = cliente
                    break # Lo encontramos, rompemos el ciclo
            
            # Si terminamos de buscar y no lo encontramos, lanzamos un error general
            if cliente_encontrado is None:
                raise ErrorSoftwareFJ(f"No se encontró ningún cliente con el ID {id_buscar}.")

        except ErrorDatoInvalido as e_dato:
            # EXCEPT 1: Atrapa nuestro error de datos inválidos
            mensaje = f"Error de formato al buscar: {e_dato}"
            print(mensaje)
            guardar_log(mensaje)

        except ErrorSoftwareFJ as e_sistema:
            # EXCEPT 2: Atrapa nuestro error de "no encontrado"
            mensaje = f"Error de búsqueda: {e_sistema}"
            print(mensaje)
            guardar_log(mensaje)
            
        except Exception as e_inesperado:
            # EXCEPT 3: Atrapa CUALQUIER otro error raro que no hayamos previsto
            mensaje = f"Error inesperado durante la búsqueda: {e_inesperado}"
            print(mensaje)
            guardar_log(mensaje)

        else:
            # ELSE: Se ejecuta SOLO si el bloque 'try' terminó SIN NINGÚN ERROR
            print(f"¡Éxito! Cliente encontrado: {cliente_encontrado.get_nombre()}")
            return cliente_encontrado

        finally:
            # FINALLY: Se ejecuta SIEMPRE, haya fallado o no.
            print("Finalizando proceso de búsqueda en el sistema.")

if __name__ == "__main__":
    print("\n---este es el manejo de listas internas ---")
    gestor = GestorSoftwareFJ()
    
    # Creamos y registramos un cliente
    cliente_prueba = Cliente("C100", "Pedro", "pedro@correo.com")
    gestor.registrar_cliente(cliente_prueba)
    
    # Prueba 1: Búsqueda exitosa (activará el ELSE)
    print("\nPrueba 1: Buscar cliente que SI existe")
    resultado1 = gestor.buscar_cliente("C100")
    
    # Prueba 2: Búsqueda fallida (activará el EXCEPT de ErrorSoftwareFJ)
    print("\nPrueba 2: Buscar cliente que NO existe")
    resultado2 = gestor.buscar_cliente("C999")
    
    # Prueba 3: Error provocado (activará el EXCEPT de ErrorDatoInvalido)
    print("\nPrueba 3: Buscar con un ID inválido (un número en vez de texto)")
    resultado3 = gestor.buscar_cliente(12345)

def ejecutar_simulacion():
    print("\n" + "="*50)
    print("SOFTWARE FJ")
    print("="*50)
    
    # inicio el gestor central
    gestor = GestorSoftwareFJ()
    # ---------------------------------------------------------
    # OPERACIÓN 1: Registro válido de cliente
    print("\n[Operación 1] Registrando cliente válido...")
    cliente1 = Cliente("C001", "Diana", "diana@correo.com")
    gestor.registrar_cliente(cliente1)
    print("-> OK: Cliente Diana registrada.")
    # ---------------------------------------------------------
    # OPERACIÓN 2: Registro inválido de cliente (Fallo provocado)
    print("\n[Operación 2] Intentando modificar correo inválido (sin @)...")
    try:
        cliente_error = Cliente("C002", "Javier", "javiercorreo.com")
        cliente_error.set_correo("javiercorreo.com") # Aquí estalla
    except ErrorDatoInvalido as e:
        print(f"-> OK MANEJO DE ERROR: {e}")
        guardar_log(f"Fallo Operación 2: {e}")

    # OPERACIÓN 3: Creación correcta de un servicio (Sala)
    print("\n[Operación 3] Creando servicio válido (Sala)...")
    sala1 = ReservaSala("S001", "Sala de Conferencias B", 60000, 20)
    gestor.registrar_servicio(sala1)
    print("-> OK: Sala de Conferencias B registrada.")

    # OPERACIÓN 4: Creación correcta de un servicio (Equipo)
    print("\n[Operación 4] Creando servicio válido (Equipo)...")
    equipo1 = AlquilerEquipo("E001", "Proyector 4K", 30000, "Audiovisual")
    gestor.registrar_servicio(equipo1)
    print("-> OK: Proyector 4K registrado.")
    
    # OPERACIÓN 5: Búsqueda exitosa usando try/except/else/finally
    print("\n[Operación 5] Buscando cliente existente en el gestor...")
    cliente_encontrado = gestor.buscar_cliente("C001")
    # No imprimimos OK aquí porque el método buscar_cliente ya imprime sus mensajes
    # OPERACIÓN 6: Reserva exitosa (Diana reserva la Sala)
    print("\n[Operación 6] Realizando reserva exitosa...")
    try:
        # Reserva por 4 horas
        reserva1 = Reserva("R001", cliente1, sala1, 4)
        mensaje_res = reserva1.confirmar_reserva()
        gestor.lista_reservas.append(reserva1)
        print(f"-> OK: {mensaje_res}")
    except Exception as e:
        print(f"Error inesperado: {e}")

    # OPERACIÓN 7: Reserva fallida (Servicio no disponible)
    print("\n[Operación 7] Intentando reservar un servicio ya ocupado...")
    try:
        # Intentamos que Diana reserve la MISMA sala que ya está confirmada y ocupada
        reserva2 = Reserva("R002", cliente1, sala1, 2)
        reserva2.confirmar_reserva() 
    except ErrorNoDisponible as e:
        print(f"-> OK MANEJO DE ERROR: {e}")
        guardar_log(f"Fallo Operación 7: {e}")

    # OPERACIÓN 8: Cancelación de reserva sin motivo (Sobrecarga simulada 1)
    print("\n[Operación 8] Cancelando reserva SIN motivo (simulación sobrecarga)...")
    try:
        msg_cancela1 = reserva1.cancelar_reserva()
        print(f"-> OK: {msg_cancela1}")
    except Exception as e:
        print(f"Error: {e}")

    # OPERACIÓN 9: Cancelación de reserva CON motivo (Sobrecarga simulada 2)
    print("\n[Operación 9] Cancelando reserva CON motivo (simulación sobrecarga)...")
    try:
        # Primero volvemos a confirmar la reserva para poder cancelarla (está liberada)
        reserva1.confirmar_reserva()
        # Ahora la cancelamos pasando el parámetro opcional
        msg_cancela2 = reserva1.cancelar_reserva("Cambio de fecha por parte del cliente")
        print(f"-> OK: {msg_cancela2}")
    except Exception as e:
        print(f"Error: {e}")

    # OPERACIÓN 10: Intento de cancelar una reserva ya cancelada
    print("\n[Operación 10] Intentando cancelar una reserva que ya está cancelada...")
    try:
        reserva1.cancelar_reserva() # Va a estallar porque acabamos de cancelarla en el paso 9
    except ErrorSoftwareFJ as e:
        print(f"-> OK MANEJO DE ERROR: {e}")
        guardar_log(f"Fallo Operación 10: {e}")

    print("\n" + "="*50)
    print("SIMULACIÓN FINALIZADA. El programa NO se cerró abruptamente.")
    print("Revise el archivo 'registro_errores.txt' finnnnnnnnnnnnnn.")
    print("="*50)

# PUNTO DE ENTRADA DEL PROGRAMA

if __name__ == "__main__":
    # Creamos/limpiamos el log al inicio de la ejecución final para empezar fresco
    try:
        with open("registro_errores.txt", "w", encoding="utf-8") as f:
            f.write("=== INICIO DE LOG DEL SISTEMA SOFTWARE FJ ===\n")
    except Exception:
        pass
        
    ejecutar_simulacion()