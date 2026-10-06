from .database import Database


class LidarTable:

    def __init__(self):

        self.db = Database()

    def actualizar(self,
                   distancia,
                   frecuencia):

        consulta = """

        UPDATE Lidar

        SET

            distancia_media=%s,
            frecuencia=%s

        WHERE id_lidar=1;

        """

        self.db.execute(
            consulta,
            (
                distancia,
                frecuencia
            )
        )