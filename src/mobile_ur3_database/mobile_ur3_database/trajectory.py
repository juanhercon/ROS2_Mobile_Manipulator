from .database import Database


class TrajectoryTable:

    def __init__(self):

        self.db = Database()

    def insertar(
        self,
        ox,
        oy,
        oz,
        dx,
        dy,
        dz,
        distancia,
        id_trayectoria=1,
        id_camara=1
    ):

        consulta = """

        INSERT INTO Trayectoria(
            id_robot,
            fecha,

            origen_x,
            origen_y,
            origen_z,

            destino_x,
            destino_y,
            destino_z,

            distancia

        )

        VALUES(

            1,
            NOW(),

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
                ox,
                oy,
                oz,
                dx,
                dy,
                dz,
                distancia
            )
        )
        #Cremaos la relacion Trayectoria-camara
        consulta_relacion = """

        INSERT INTO Trayectoria_Camara (
            id_trayectoria,
            id_camara
        )

        VALUES (
            %s,
            %s
        )

        ON CONFLICT (id_trayectoria, id_camara)
        DO NOTHING;

        """

        self.db.execute(
            consulta_relacion,
            (
                id_trayectoria,
                id_camara
            )
        )

        return id_trayectoria