class Jugador:
    def __init__(self, id, nombre, posicion, precio, goles=0, asistencias=0, porterias_cero=0):
        self.id = id
        self.nombre = nombre
        self.posicion = posicion
        self.precio = precio
        self.goles = goles
        self.asistencias = asistencias
        self.porterias_cero = porterias_cero

    def calcular_puntos(self):
        # Ejemplo de cálculo básico de puntos
        puntos = self.goles * (5 if self.posicion == 'delantero' else 3)
        puntos += self.asistencias * 2
        if self.posicion == 'portero' and self.porterias_cero:
            puntos += 4
        return puntos

class Usuario:
    def __init__(self, id, nombre, presupuesto):
        self.id = id
        self.nombre = nombre
        self.presupuesto = presupuesto
        self.equipo = []  # Lista de objetos Jugador

    def agregar_jugador(self, jugador):
        if len(self.equipo) < 7:
            costo_actual = sum(j.precio for j in self.equipo)
            if costo_actual + jugador.precio <= self.presupuesto:
                self.equipo.append(jugador)
                return True
            else:
                raise ValueError("Presupuesto excedido.")
        else:
            raise ValueError("Equipo completo. No se pueden agregar más jugadores.")


class Equipo:
    def __init__(self, jugadores, capitan):
        if len(jugadores) != 7:
            raise ValueError("Un equipo debe tener exactamente 7 jugadores.")
        self.jugadores = jugadores
        self.capitan = capitan

    def calcular_puntos_totales(self):
        puntos_totales = sum(j.calcular_puntos() for j in self.jugadores)
        puntos_totales += self.capitan.calcular_puntos()  # Duplicar puntos del capitán
        return puntos_totales


class Jornada:
    def __init__(self, id, nombre, estadisticas):
        self.id = id
        self.nombre = nombre
        self.estadisticas = estadisticas  # Diccionario {id_jugador: {'goles': X, 'asistencias': Y}}

    def actualizar_estadisticas(self, jugadores):
        for jugador in jugadores:
            if jugador.id in self.estadisticas:
                stats = self.estadisticas[jugador.id]
                jugador.goles += stats.get('goles', 0)
                jugador.asistencias += stats.get('asistencias', 0)
                jugador.porterias_cero += stats.get('porterias_cero', 0)