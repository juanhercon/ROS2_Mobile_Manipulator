from .database import Database
import time

class BasketTable:

    def __init__(self):
        self.db = Database()

    # =========================================================
    # REGISTRAR LA DESCARGA DE UN FRUTO (Y ACTUALIZAR PESO)
    # =========================================================
    def add_fruit_weight_with_trazability(self, fruit_weight, id_fruto, id_robot=1):
        # Forzamos que el cesto físico sea siempre el 1
        id_cesto = 1
        id_fruto = 1

        # -----------------------------------------------------
        # 1. Buscar el estado actual del cesto 1
        # -----------------------------------------------------
        consulta_buscar = """
            SELECT capacidad_restante, cestos_llenos, peso_actual, peso_total
            FROM Cesto
            WHERE id_cesto = %s;
        """
        resultado = self.db.fetch_one(consulta_buscar, (id_cesto,))

        if resultado is None:
            capacidad_restante = 30.0
            cestos_llenos = 0
            peso_actual = 0.0
            peso_total = 0.0
        else:
            capacidad_restante = float(resultado[0])
            cestos_llenos = int(resultado[1])
            peso_actual = float(resultado[2])
            peso_total = float(resultado[3])

        # -----------------------------------------------------
        # 2. Sumar el peso del fruto recolectado
        # -----------------------------------------------------
        peso_actual += float(fruit_weight)

        # -----------------------------------------------------
        # 3. Comprobar si se ha llenado (Simulamos vaciado automático)
        # -----------------------------------------------------
        if peso_actual >= 30.0:
            cestos_llenos += 1
            exceso = peso_actual - 30.0
            peso_actual = exceso  # El sobrante pasa al cesto limpio

        capacidad_restante = 30.0 - peso_actual
        if capacidad_restante < 0:
            capacidad_restante = 0.0

        peso_total = (30.0 * cestos_llenos) + peso_actual

        # -----------------------------------------------------
        # 4. Actualizar las métricas físicas del cesto 1
        # -----------------------------------------------------
        consulta_update = """
            UPDATE Cesto
            SET
                capacidad_restante = %s,
                cestos_llenos = %s,
                peso_actual = %s,
                peso_total = %s
            WHERE id_cesto = %s;
        """
        self.db.execute(
            consulta_update,
            (capacidad_restante, cestos_llenos, peso_actual, peso_total, id_cesto)
        )

        #Relacion Cesto-robot
        consulta_relacion = """
            INSERT INTO cesto_robot (id_robot, id_cesto) VALUES (%s, %s) 
            ON CONFLICT (id_robot, id_cesto) DO NOTHING;
        """
        self.db.execute(consulta_relacion, (id_robot, id_cesto))


        #Creamos la relacion Cesto-fruto
        consulta_relacion = """

        INSERT INTO Cesto_Fruto (
            id_cesto,
            id_fruto
        )

        VALUES (
            %s,
            %s
        )

        ON CONFLICT (id_cesto, id_fruto)
        DO NOTHING;

        """

        self.db.execute(
            consulta_relacion,
            (
                id_cesto,
                id_fruto
            )
        )

        return id_cesto