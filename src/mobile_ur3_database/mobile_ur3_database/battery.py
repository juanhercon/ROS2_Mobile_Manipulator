from .database import Database


class BatteryTable:

    def __init__(self):

        self.db = Database()

    def insertar(
        self,
        carga,
        voltaje,
        corriente,
        tiempo_restante,
        estado
    ):

        consulta = """

        INSERT INTO Bateria(

            id_robot,
            estado_carga,
            voltaje,
            corriente,
            hora_estimada_descarga,
            estado_bateria

        )

        VALUES(

            1,
            %s,
            %s,
            %s,
            %s,
            %s

        );

        """

        self.db.execute(
            consulta,
            (
                carga,
                voltaje,
                corriente,
                tiempo_restante,
                estado
            )
        )

    def carga(self):

        consulta = """
        SELECT estado_carga
        FROM Bateria
        ORDER BY id_bateria DESC
        LIMIT 1;
        """

        resultado = self.db.fetch_one(consulta)

        if resultado is None:
            return 100.0

        return float(resultado[0])