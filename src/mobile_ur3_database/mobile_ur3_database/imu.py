from .database import Database


class ImuTable:

    def __init__(self):

        self.db = Database()

    def insertar(
        self,
        ax,
        ay,
        az,
        gx,
        gy,
        gz,
        mx,
        my,
        mz,
        estado
    ):

        consulta = """

        INSERT INTO IMU(

            id_robot,
            modelo,

            aceleracion_x,
            aceleracion_y,
            aceleracion_z,

            velocidad_rotacion_x,
            velocidad_rotacion_y,
            velocidad_rotacion_z,

            campo_magnetico_x,
            campo_magnetico_y,
            campo_magnetico_z,

            estado
        )

        VALUES(
            1,
            'IMU',
            %s,
            %s,
            %s,
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
                ax,
                ay,
                az,
                gx,
                gy,
                gz,
                mx,
                my,
                mz,
                estado
            )
        )