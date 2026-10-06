#!/usr/bin/env python3

import math
import rclpy
from rclpy.node import Node

from geometry_msgs.msg import Twist
from sensor_msgs.msg import LaserScan
from sensor_msgs.msg import JointState
from std_msgs.msg import Bool, Float32
from sensor_msgs.msg import Imu
from nav_msgs.msg import Odometry

from .robot import RobotTable
from .lidar import LidarTable
from .camera import CameraTable
from .arm import ArmTable
from .trajectory import TrajectoryTable
from .fruit import FruitTable
from .imu import ImuTable
from .battery import BatteryTable
from .basket import BasketTable

class DatabaseNode(Node):

    def __init__(self):

        super().__init__("database_node")

        self.get_logger().info("Conectando...")

        self.robot = RobotTable()
        self.lidar = LidarTable()
        self.camera = CameraTable()
        self.arm = ArmTable()
        self.trajectory = TrajectoryTable()
        self.fruit = FruitTable()
        self.imu = ImuTable()
        self.battery = BatteryTable()
        self.basket = BasketTable()

        #Velocidad
        self.create_subscription(
            Twist,
            "/diff_drive_controller/cmd_vel_unstamped",
            self.cmd_vel_callback,
            10
        )
        #LiDAR
        self.create_subscription(
            LaserScan,
            "/scan",
            self.scan_callback,
            10
        )
        #Camara
        self.create_subscription(
            Bool,
            "/plant_detected",
            self.plant_callback,
            10
        )
        #Brazo
        self.create_subscription(
            JointState,
            "/joint_states",
            self.joint_callback,
            10
        )
        #Mostrar informacion
        self.timer = self.create_timer(
            1.0,
            self.mostrar_robot
        )
        #IMU
        self.create_subscription(
            Imu,
            "/imu/data",
            self.imu_callback,
            10
        )
        #Bateria
        self.battery_level = 100.0
        self.create_timer(
            5.0,
            self.battery_callback
        )

        # Cesto
        self.id_robot = 1  # Añade el ID asignado a tu robot móvil
        self.peso_cesto = 0.0
        self.cestos_llenos = 0

        '''self.basket.insertar(
            id_robot=self.id_robot,
            capacidad=30.0 - self.peso_cesto,
            cestos_llenos=self.cestos_llenos,
            peso_actual=self.peso_cesto,
            peso_total=(self.cestos_llenos * 30.0) + self.peso_cesto
        )'''
        #Trayectoria
        self.last_position = None
        self.create_subscription(

            Odometry,

            "/diff_drive_controller/odom",

            self.odom_callback,

            10

        )

        self.green_ratio = 0.0

        self.create_subscription(
            Float32,
            "/green_ratio",
            self.green_ratio_callback,
            10
        )


    def mostrar_robot(self):

        filas = self.robot.leer_robot()

        for fila in filas:

            self.get_logger().info(f"Robot {fila[0]}")
            self.get_logger().info(f"Estado {fila[1]}")
            self.get_logger().info(
                f"Velocidades {fila[2]}, {fila[3]}, {fila[4]}, {fila[5]}"
            )

    def cmd_vel_callback(self,msg):

        velocidad = msg.linear.x

        if abs(velocidad)<0.001:
            estado="Reposo"
        else:
            estado="Movimiento"
        
        self.robot.actualizar_velocidades(
            velocidad,
            velocidad,
            velocidad,
            velocidad
        )

        self.robot.actualizar_estado(estado)

    def scan_callback(self,msg):

        
        distancias = [
            r for r in msg.ranges
            if math.isfinite(r)
        ]

        if len(distancias) == 0:
            return

        distancia = min(distancias)

        ahora = self.get_clock().now()

        if hasattr(self, "ultimo_scan"):

            dt = (ahora-self.ultimo_scan).nanoseconds*1e-9

            frecuencia = 1.0/dt

        else:

            frecuencia = 0.0

        self.ultimo_scan = ahora

    def joint_callback(self, msg):

        idx = {name: i for i, name in enumerate(msg.name)}

        self.arm.insertar(

            msg.position[idx["shoulder_pan_joint"]],
            msg.position[idx["shoulder_lift_joint"]],
            msg.position[idx["elbow_joint"]],
            msg.position[idx["wrist_1_joint"]],
            msg.position[idx["wrist_2_joint"]],
            msg.position[idx["wrist_3_joint"]],
            "Abierto"

        )
    def plant_callback(self,msg):

        self.get_logger().info(
            f"Planta detectada = {msg.data}"
        )
    def imu_callback(self, msg):


        self.imu.insertar(

            msg.linear_acceleration.x,
            msg.linear_acceleration.y,
            msg.linear_acceleration.z,

            msg.angular_velocity.x,
            msg.angular_velocity.y,
            msg.angular_velocity.z,

            0.0,
            0.0,
            0.0,

            "Activo"
        )

    def battery_callback(self):

        if self.battery_level > 0:
            self.battery_level -= 0.02

        autonomia = self.battery_level / 12.0

        self.battery.insertar(

            self.battery_level,
            48.0,
            6.3,
            autonomia,
            "Descargando"

        )

        self.get_logger().info(

            f"Batería: {self.battery_level:.1f}% | "
            f"Autonomía: {autonomia:.2f} h"

        )

    def recoger_racimo(self, peso):

        self.peso_cesto += peso

        if self.peso_cesto >= 30:

            self.cestos_llenos += 1
            self.peso_cesto = 0

        self.basket.insertar(

            30-self.peso_cesto,
            self.cestos_llenos,
            self.peso_cesto,
            30

        )

    def odom_callback(self, msg):

        x = msg.pose.pose.position.x
        y = msg.pose.pose.position.y
        z = msg.pose.pose.position.z

        if self.last_position is None:

            self.last_position = (x, y, z)
            return

        ox, oy, oz = self.last_position

        distancia = math.sqrt(
            (x-ox)**2 +
            (y-oy)**2 +
            (z-oz)**2
        )

        if distancia > 0:

            print(distancia)

            self.trajectory.insertar(

                ox,
                oy,
                oz,

                x,
                y,
                z,

                distancia

            )

            self.last_position = (x, y, z)

    # =========================================================
    # CALLBACK DEL PORCENTAJE DE VERDE
    # =========================================================

    def green_ratio_callback(self, msg):

        porcentaje_verde = msg.data

        # Determinar si se considera que hay planta
        fruto_detectado = porcentaje_verde > 20.0

        # Guardar una NUEVA FILA en Camara
        self.camera.insertar(
            "Activa",
            fruto_detectado,
            porcentaje_verde
        )

        self.get_logger().info(
            f"Cámara -> "
            f"Verde={porcentaje_verde:.2f}% | "
            f"Planta={fruto_detectado}"
        )
    

def main(args=None):

    rclpy.init(args=args)

    node = DatabaseNode()

    rclpy.spin(node)

    node.destroy_node()

    rclpy.shutdown()


if __name__ == "__main__":
    main()