from .database import Database


class ArmTable:

    def __init__(self):
        self.db = Database()

    def insertar(
        self,
        j1,
        j2,
        j3,
        j4,
        j5,
        j6,
        gripper,
        id_brazo=1,
        id_bateria=1,
        id_fruto=1
    ):

        consulta = """

        INSERT INTO Brazo_robot(

            id_robot,
            articulacion_1,
            articulacion_2,
            articulacion_3,
            articulacion_4,
            articulacion_5,
            articulacion_6,
            gripper

        )

        VALUES(

            1,
            %s,
            %s,
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
                j1,
                j2,
                j3,
                j4,
                j5,
                j6,
                gripper
            )
        )

        # =====================================================
        # 2. Crear relación Brazo-Cesto
        # =====================================================
        #Creamos relacion Brazo-cesto

        consulta_relacion = """

        INSERT INTO Brazo_bateria (
            id_brazo,
            id_bateria
        )

        VALUES (
            %s,
            %s
        )

        ON CONFLICT (id_brazo, id_bateria)
        DO NOTHING;

        """

        self.db.execute(
            consulta_relacion,
            (
                id_brazo,
                id_bateria
            )
        )
        return id_brazo