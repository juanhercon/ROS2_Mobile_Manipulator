from .database import Database


class CameraTable:

    def __init__(self):

        self.db = Database()

    def insertar(
        self,
        estado,
        fruto_detectado,
        porcentaje_verde,
        id_camara = 1,
        id_fruto = 1,
        id_brazo = 1
    ):

        consulta = """

        INSERT INTO Camara (

            id_brazo,
            estado,
            fruto_detectado,
            porcentaje_verde

        )

        VALUES(

            1,
            %s,
            %s,
            %s

        );

        """

        self.db.execute(
            consulta,
            (
                estado,
                fruto_detectado,
                porcentaje_verde
            )
        )
        #Creamos la relacion Camara-brazo

        consulta_relacion = """

        INSERT INTO Camara_Brazo (
            id_camara,
            id_brazo
        )

        VALUES (
            %s,
            %s
        )

        ON CONFLICT (id_camara, id_brazo)
        DO NOTHING;

        """

        self.db.execute(
            consulta_relacion,
            (
                id_camara,
                id_brazo
            )
        )

        return id_camara