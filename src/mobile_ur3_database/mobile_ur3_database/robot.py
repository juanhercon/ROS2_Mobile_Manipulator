from .database import Database


class RobotTable:

    def __init__(self):

        self.db = Database()

    def actualizar_velocidades(
        self,
        v1,
        v2,
        v3,
        v4
    ):

        consulta = """

        UPDATE Robot_movil

        SET

        velocidad_rueda_delantera_izquierda=%s,

        velocidad_rueda_delantera_derecha=%s,

        velocidad_rueda_trasera_izquierda=%s,

        velocidad_rueda_trasera_derecha=%s

        WHERE id_robot=1;

        """

        self.db.execute(
            consulta,
            (
                v1,
                v2,
                v3,
                v4
            )
        )
    def actualizar_estado(self,estado):
        consulta ="""
        UPDATE Robot_movil
        SET
        estado = %s
        WHERE id_robot = 1;
        """

        self.db.execute(consulta,(estado, ))

    def leer_robot(self):
        consulta = """

        SELECT
            id_robot,
            estado,
            velocidad_rueda_delantera_izquierda,
            velocidad_rueda_delantera_derecha,
            velocidad_rueda_trasera_izquierda,
            velocidad_rueda_trasera_derecha

        FROM Robot_movil;

        """

        return self.db.fetchall(consulta)