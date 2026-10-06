#!/usr/bin/env python3

import rclpy
from rclpy.node import Node

from .database import Database

class Statistics:

    def __init__(self):

        self.db = Database()

    ###################################################
    # Distancia total recorrida
    ###################################################

    def distancia_total(self):

        consulta = """
        SELECT COALESCE(SUM(distancia),0)
        FROM Trayectoria;
        """

        return self.db.fetch_one(consulta)[0]

    ###################################################
    # Número de trayectorias
    ###################################################

    def numero_trayectorias(self):

        consulta = """
        SELECT COUNT(*)
        FROM Trayectoria;
        """

        return self.db.fetch_one(consulta)[0]

    ###################################################
    # Número de frutos
    ###################################################

    def numero_frutos(self):

        consulta = """
        SELECT COUNT(*)
        FROM Fruto;
        """

        return self.db.fetch_one(consulta)[0]

    ###################################################
    # Madurez media
    ###################################################

    def madurez_media(self):

        consulta = """
        SELECT COALESCE(AVG(umbral_de_madurez),0)
        FROM Fruto;
        """

        return self.db.fetch_one(consulta)[0]

    ###################################################
    # Peso actual del cesto
    ###################################################

    def peso_cesto(self):

        consulta = """
        SELECT peso_actual
        FROM Cesto
        WHERE id_cesto=1;
        """

        return self.db.fetch_one(consulta)[0]

    ###################################################
    # Batería
    ###################################################

    def bateria(self):

        consulta = """
        SELECT
            estado_carga,
            voltaje,
            corriente,
            hora_estimada_descarga
        FROM Bateria
        WHERE id_bateria=1;
        """

        return self.db.fetch_one(consulta)

    def brazo(self):

        consulta = """
        SELECT
            articulacion_1,
            articulacion_2,
            articulacion_3,
            articulacion_4,
            articulacion_5,
            articulacion_6,
            gripper
        FROM Brazo_robot
        WHERE id_brazo=1;
        """

        return self.db.fetch_one(consulta)

    def lidar(self):

        consulta = """
        SELECT
            frecuencia,
            distancia_media
        FROM Lidar
        WHERE id_lidar=1;
        """

        return self.db.fetch_one(consulta)

    def estado_robot(self):

        consulta = """
        SELECT estado
        FROM Robot_movil
        WHERE id_robot=1;
        """

        return self.db.fetch_one(consulta)[0]

class RobotStatistics(Node):

    def __init__(self):

        super().__init__("robot_statistics")

        self.stats = Statistics()

        self.create_timer(
            5.0,
            self.statistics_callback
        )

    def statistics_callback(self):

        estado = self.stats.estado_robot()
        self.get_logger().info(f"Estado: {estado}")

        distancia = self.stats.distancia_total()
        self.get_logger().info(f"Distancia: {distancia:.2f} m")

        frutos = self.stats.numero_frutos()
        self.get_logger().info(f"Frutos: {frutos}")

        peso = self.stats.peso_cesto()
        self.get_logger().info(f"Cesto: {peso:.2f} kg")

        bateria = self.stats.bateria()
        self.get_logger().info(f"Batería: {bateria[0]} %")

        brazo = self.stats.brazo()

        self.get_logger().info("------------ BRAZO ------------")
        self.get_logger().info(f"J1 : {brazo[0]:.2f}")
        self.get_logger().info(f"J2 : {brazo[1]:.2f}")
        self.get_logger().info(f"J3 : {brazo[2]:.2f}")
        self.get_logger().info(f"J4 : {brazo[3]:.2f}")
        self.get_logger().info(f"J5 : {brazo[4]:.2f}")
        self.get_logger().info(f"J6 : {brazo[5]:.2f}")
        self.get_logger().info(f"Gripper : {brazo[6]}")

        lidar = self.stats.lidar()

        self.get_logger().info("------------ LIDAR ------------")
        self.get_logger().info(f"Frecuencia : {lidar[0]:.2f} Hz")
        self.get_logger().info(f"Distancia  : {lidar[1]:.2f} m")


    ##################################################




def main(args=None):

    rclpy.init(args=args)

    node = RobotStatistics()

    rclpy.spin(node)

    node.destroy_node()

    rclpy.shutdown()


if __name__ == "__main__":
    main()