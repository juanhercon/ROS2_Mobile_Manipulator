from .database import Database


class FruitTable:

    def __init__(self):

        self.db = Database()

    def insertar(
        self,
        tipo,
        x,
        y,
        z,
        madurez,
        id_camara = 1,
        id_brazo = 1,
        id_fruto = 1
    ):

        consulta = """

        INSERT INTO Fruto(

            id_camara,
            tipo,
            coordenada_x,
            coordenada_y,
            coordenada_z,
            umbral_madurez

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
                tipo,
                x,
                y,
                z,
                madurez
            )
        )
        #Creamos la relacion Camara-fruto

        consulta_relacion = """

        INSERT INTO Camara_Fruto (
            id_camara,
            id_fruto
        )

        VALUES (
            %s,
            %s
        )

        ON CONFLICT (id_camara, id_fruto)
        DO NOTHING;

        """

        self.db.execute(
            consulta_relacion,
            (
                id_camara,
                id_fruto
            )
        )
        #Creamos la relacion Brazo-fruto

        consulta_relacion = """

        INSERT INTO Brazo_Fruto (
            id_brazo,
            id_fruto
        )

        VALUES (
            %s,
            %s
        )

        ON CONFLICT (id_brazo, id_fruto)
        DO NOTHING;

        """

        self.db.execute(
            consulta_relacion,
            (
                id_brazo,
                id_fruto
            )
        )
        return id_fruto