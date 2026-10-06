#!/usr/bin/env python3

import time
import math

import rclpy
from rclpy.node import Node
from rclpy.action import ActionClient

from geometry_msgs.msg import Twist

from control_msgs.action import FollowJointTrajectory
from trajectory_msgs.msg import JointTrajectoryPoint
from builtin_interfaces.msg import Duration

from sensor_msgs.msg import LaserScan
from std_msgs.msg import Bool
from geometry_msgs.msg import PointStamped
from mobile_ur3_database.battery import BatteryTable

from gazebo_msgs.srv import DeleteEntity

from gazebo_msgs.srv import DeleteEntity, SetEntityState
from gazebo_msgs.msg import EntityState
from geometry_msgs.msg import Pose

import random

from mobile_ur3_database.basket import BasketTable
from mobile_ur3_database.lidar import LidarTable


class MobileUR3Controller(Node):

    def __init__(self):

        super().__init__("mobile_ur3_controller")
        #Creamos un publicador para enviar las velocidades correspondientes a la base movil
        self.cmd_vel_pub = self.create_publisher(
            Twist,
            "/diff_drive_controller/cmd_vel_unstamped",
            10,
        )

        #Creamos un cliente de acciones para controlar la trayectoria del brazo
        self.arm_client = ActionClient(
            self,
            FollowJointTrajectory,
            "/joint_trajectory_controller/follow_joint_trajectory",
        )

        self.get_logger().info("Esperando al controlador del brazo...") #Mostramos mensaje por terminal

        self.arm_client.wait_for_server() #Esperamos hasta que el servidor este disponible

        self.get_logger().info("Controlador encontrado.") #Mostramos mensaje por terminal

        self.distance_mean = None #Variable que se utilizara para almacenar distancia captada por el haz intermedio del LiDAR

        #Creamos un suscriptor al topic /scan, se ejecuta cada vez que llegue una medida del LiDAR
        self.scan_sub = self.create_subscription(
            LaserScan,
            "/scan",
            self.scan_callback,
            10
        )

        self.plant_detected = False #Variable que indica si se ha detectado planta

        #Suscripcion al topic /plant_detected, topic publicado por el sistema de vision
        self.create_subscription(
            Bool,
            "/plant_detected",
            self.plant_callback,
            10
        )

        self.battery = BatteryTable() #Creamos la variable encargada de de consultar el valor de la bateria

        self.fruit_position = None #Variable donde se almacenara las coordenadas del fruto detectado

        #Suscribe al topic /fruit_position, recibiremos coordenadas del fruto
        self.create_subscription(

            PointStamped,

            "/fruit_position",

            self.fruit_callback,

            10

        )
        self.arm_client.wait_for_server() #Volvemos a comprobar que el controlador del brazo este disponible

        self.get_logger().info("Controlador encontrado.") #Mostramos mensaje por terminal

        #Creamos un cliente para poder utilizar el servicio /delete_entity para eliminar el fruto recolectado
        self.delete_entity_client = self.create_client(
            DeleteEntity,
            "/delete_entity"
        )

        #Muestra mensaje por terminal
        self.get_logger().info(
            "Esperando servicio /delete_entity..."
        )

        #Mientras que el servicio no este disponible esperamos
        while not self.delete_entity_client.wait_for_service(
            timeout_sec=1.0
        ):  #Esperamos
            self.get_logger().info(
                "Esperando /delete_entity..."
            )
        #Servicio disponible
        self.get_logger().info(
            "Servicio /delete_entity disponible."
        )

        self.plant_number = 0 #Contador de plantas detectadas
        self.fruits_collected = 0       # Número de frutos recogidos

        self.start_time = None          # Instante de inicio del proceso
        self.ultima_actualizacion_bd = 0.0 #Variable para saber la ultima actualizacion de la base de datos

        self.basket = BasketTable() #Tabla basket, corresponde al cesto, para poder tratar con los diferentes pesos de la recoleccion
        self.lidar = LidarTable() #Tabla LiDAR, para guardar los datos correspondientes 

########################## FIN DEL __INIT__ ###################################################################

    '''
    Funcion que se ejecuta cada vez que llega un mensaje del LiDAR, para detectar el poste o planta
    '''
    def scan_callback(self, msg):

        target_angle = 1.6 #Angulo del LiDAR que queremos utilizar

        #Calculamos posicion del array correspondiente al angulo
        index = int(
            (target_angle - msg.angle_min) /
            msg.angle_increment
        )

        #Comprobamos que el indice calculado sea valido
        if 0 <= index < len(msg.ranges):
            self.distance_mean = msg.ranges[index]

        #Temporizador creador por si el nodo no existe
            if not hasattr(self, '_last_db_update_time'):
                self._last_db_update_time = 0.0

            ahora = time.perf_counter() #Variable de tiempo
            
            #Frecuencia con la que enviamos la informacion a la base de datos
            if (ahora - self._last_db_update_time) > 0.2:
                
                distancia_a_guardar = self.distance_mean #Guardamos la distancia del haz de laser intermedio
                
                if math.isinf(distancia_a_guardar) or distancia_a_guardar > 30.0: #SI el laser nos da infinito o la distnacia es mayor
                    distancia_a_guardar = 30.0 #Guardamos la distancia media
                
                try:
                    #Enviamos a la tabla lidar
                    self.lidar.actualizar(
                        distancia=float(distancia_a_guardar),
                        frecuencia=15
                    )
                    self._last_db_update_time = ahora
                except Exception as e:
                    self.get_logger().error(f"Error al escribir en la BD: {e}")
            # -----------------------------------------------------------------

    '''
    Funcion detectar la planta
    '''
    def plant_callback(self, msg):

        self.plant_detected = msg.data #Guardamos el valor True/False recibido


    '''
    Funcion para mover la base movil del robot
    '''
    def move_base(self, velocity):

        msg = Twist() #Creamos un mensaje tipo Twist()
        msg.linear.x = velocity #Establecemos la velocidad en el eje x (avance)

        #Mientras ROS2 este funcionando
        while rclpy.ok():

            rclpy.spin_once(self, timeout_sec=0.01) #Procesamos los mensajes recibidos por nodo

            self.cmd_vel_pub.publish(msg) #Publicamos la velocidad correspondiente al avance

            #Comprobamos que tengamos una medida valida del LiDAR
            if self.distance_mean is not None: 
                #Mostramos por terminal la distancia
                self.get_logger().info(
                    f"Distancia = {self.distance_mean:.2f}"
                )
                #Si la distancia es menor que 0.60 m paramos el robot movil
                if self.distance_mean < 0.60:
                    break

            time.sleep(0.02) #Esperamos para volver a realizar otra iteracion

        msg.linear.x = 0.0 #Ponemos la velocidad lineal a cero para detener la base

        #Publicamos varias veces el mensaje de parada
        for _ in range(10):
            self.cmd_vel_pub.publish(msg)
            time.sleep(0.05)

    '''
    Funcion para mover el brazo a la posicion de recoleccion 1
    '''
    def move_arm_position_1(self):
        #Mostramos mensaje por terminal
        self.get_logger().info(
            "Moviendo brazo a la POSICIÓN 1..."
        )

        goal = FollowJointTrajectory.Goal() #Creamos el objetivo de la trayectoria

        #Articulaciones del robot
        goal.trajectory.joint_names = [
            "shoulder_pan_joint",
            "shoulder_lift_joint",
            "elbow_joint",
            "wrist_1_joint",
            "wrist_2_joint",
            "wrist_3_joint",
        ]

        point = JointTrajectoryPoint() #Creamos el punto de la trayectoria

        # Primera posición
        point.positions = [
            1.64,
            -0.855,
            0.20,
            -2.47,
            -1.6,
            1.151,
        ]

        
        point.time_from_start = Duration(sec=3) #Tiempo que tarda en alcanzar la posición

        goal.trajectory.points.append(point) #Añadimos el punto a la trayectoria

        
        future = self.arm_client.send_goal_async(goal) #Enviar trayectoria al controlador

        rclpy.spin_until_future_complete(self, future) #Esperar hasta recibir la respuesta del controlador

        goal_handle = future.result() #Obtenemos el identificador del objetivo enviado

        #Si el controlador no ha aceptado el movimiento
        if not goal_handle.accepted:
            #Mensaje por teminal
            self.get_logger().error(
                "Movimiento a la POSICIÓN 1 rechazado."
            )

            return False
        #Si se ha aceptado el movimiento mostramos por la terminal
        self.get_logger().info(
            "Movimiento a la POSICIÓN 1 aceptado."
        )

        
        result_future = goal_handle.get_result_async() #Esperar a que termine el movimiento
        #Esperamos hasta que el movimiento haya terminado
        rclpy.spin_until_future_complete(
            self,
            result_future
        )
        #Mostramos mensaje por la terminal
        self.get_logger().info(
            "Brazo colocado en la POSICIÓN 1."
        )

        return True


    '''
    Funcion para mover el brazo a la posicion de dejar el fruto en el cesto
    '''
    def left_product(self):
        #Mostramos mensaje por la terminal
        self.get_logger().info(
            "Moviendo brazo a la POSICIÓN 2..."
        )

        goal = FollowJointTrajectory.Goal() #Creamos el objetivo de la trayectoria

        #Articulaciones del robot
        goal.trajectory.joint_names = [
            "shoulder_pan_joint",
            "shoulder_lift_joint",
            "elbow_joint",
            "wrist_1_joint",
            "wrist_2_joint",
            "wrist_3_joint",
        ]

        point = JointTrajectoryPoint() #Creamos el punto de la trayectoria

        # Posición dejar fruto
        point.positions = [
            1.57,
            -1.57,
            -1.270,
            -1.57,
            1.57,
            1.151,
        ]

       
        point.time_from_start = Duration(sec=3)  #Tiempo que tarda en alcanzar la posición

        goal.trajectory.points.append(point) #Añadimos el punto a la trayectoria
        
        future = self.arm_client.send_goal_async(goal) #Enviar trayectoria al controlador

        rclpy.spin_until_future_complete(self, future) #Esperar hasta recibir la respuesta del controlador

        goal_handle = future.result() #Obtenemos el identificador del objetivo enviado

        #Si el controlador no ha aceptado el movimiento
        if not goal_handle.accepted:
            #Mostramos mensaje por terminal
            self.get_logger().error(
                "Movimiento a la POSICIÓN 2 rechazado."
            )

            return False
        #Si se ha aceptado el movimiento mostramos por la terminal
        self.get_logger().info(
            "Movimiento a la POSICIÓN 2 aceptado."
        )

        
        result_future = goal_handle.get_result_async() #Esperar a que termine el movimiento
        #Esperamos hasta que el movimiento haya terminado
        rclpy.spin_until_future_complete(
            self,
            result_future
        )
        #Mostramos mensaje por la terminal
        self.get_logger().info(
            "Brazo colocado en la POSICIÓN 2."
        )

        return True

    '''
    Funcion para establecer la posicion inicial del robot (posicion en la que se mantiene el robot para avanzar, escanear,...)
    '''
    def initial_position(self):
            #Mostramos mensaje por terminal
            self.get_logger().info(
                "Moviendo brazo a la POSICIÓN inicial..."
            )
    
            goal = FollowJointTrajectory.Goal() #Creamos el objetivo de la trayectoria

            #Articulaciones del robot
            goal.trajectory.joint_names = [
                "shoulder_pan_joint",
                "shoulder_lift_joint",
                "elbow_joint",
                "wrist_1_joint",
                "wrist_2_joint",
                "wrist_3_joint",
            ]
    
            point = JointTrajectoryPoint() #Creamos el punto de la trayectoria
    
            # Posición inicial
            point.positions = [
                0.0,
                -1.57,
                0.0,
                -1.57,
                0.0,
                1.151,
            ]
    
            
            point.time_from_start = Duration(sec=3) #Tiempo que tarda en alcanzar la posición
    
            goal.trajectory.points.append(point) #Añadimos el punto a la trayectoria
    
            future = self.arm_client.send_goal_async(goal) #Enviar trayectoria al controlador
    
            rclpy.spin_until_future_complete(self, future) #Esperar hasta recibir la respuesta del controlador
    
            goal_handle = future.result() #Obtenemos el identificador del objetivo enviado

            #Si el controlador no ha aceptado el movimiento
            if not goal_handle.accepted:
                #Mensaje por terminal
                self.get_logger().error(
                    "Movimiento a la POSICIÓN inicial rechazado."
                )
    
                return False
            #Si se ha aceptado el movimiento mostramos por la terminal
            self.get_logger().info(
                "Movimiento a la POSICIÓN inicial aceptado."
            )
    
            
            result_future = goal_handle.get_result_async() #Esperar a que termine el movimiento
            #Esperamos hasta que el movimiento haya terminado
            rclpy.spin_until_future_complete(
                self,
                result_future
            )
            #Mostramos mensaje por la terminal
            self.get_logger().info(
                "Brazo colocado en la POSICIÓN inicial."
            )
    
            return True

    '''
    Funcion para mover el brazo hacia la segunda posicion de recoleccion
    '''
    def move_arm_position_2(self):
            #Mensaje por terminal
            self.get_logger().info(
                "Moviendo brazo a la POSICIÓN 2..."
            )
    
            goal = FollowJointTrajectory.Goal() #Creamos el objetivo de la trayectoria

            #Articulaciones del robot
            goal.trajectory.joint_names = [
                "shoulder_pan_joint",
                "shoulder_lift_joint",
                "elbow_joint",
                "wrist_1_joint",
                "wrist_2_joint",
                "wrist_3_joint",
            ]
    
            point = JointTrajectoryPoint() #Creamos el punto de la trayectoria
    
            #Segunda posicion de las articulaciones
            point.positions = [
                -1.30,
                -2.03,
                -0.66,
                -0.65,
                1.1,
                1.151,
            ]
    
            
            point.time_from_start = Duration(sec=3) #Tiempo que tarda en alcanzar la posición
    
            goal.trajectory.points.append(point) #Añadimos el punto a la trayectoria
    
            future = self.arm_client.send_goal_async(goal) #Enviar trayectoria al controlador
    
            rclpy.spin_until_future_complete(self, future) #Esperar hasta recibir la respuesta del controlador
    
            goal_handle = future.result() #Obtenemos el identificador del objetivo enviado

            #Si el controlador no ha aceptado el movimiento
            if not goal_handle.accepted:
                #Mensaje por terminal
                self.get_logger().error(
                    "Movimiento a la POSICIÓN 2 rechazado."
                )
    
                return False
            #Si se ha aceptado el movimiento mostramos por la terminal
            self.get_logger().info(
                "Movimiento a la POSICIÓN 2 aceptado."
            )
    
           
            result_future = goal_handle.get_result_async()  #Esperar a que termine el movimiento
            #Esperamos hasta que el movimiento haya terminado
            rclpy.spin_until_future_complete(
                self,
                result_future
            )
            #Mostramos mensaje por terminal
            self.get_logger().info(
                "Brazo colocado en la POSICIÓN 2."
            )
    
            return True

    '''
    Funcion para avanzar cuando se detecta un poste
    '''
    def pass_obstacle(self):

        msg = Twist() #Creamos un mensaje tipo Twist()
        msg.linear.x = 0.4 #Avance en el eje x de 0.4 m/s

        #Mientras que ROS2 esta funcionando
        while rclpy.ok():

            rclpy.spin_once(self, timeout_sec=0.02) #Leemos los nuevos mensajes

            self.cmd_vel_pub.publish(msg) #Publicamos/enviamos la velocidad a la base

            #Si el objetivo esta a mas de un metro o si es infinito
            if (
                self.distance_mean > 1.0 or
                self.distance_mean == float("inf")
            ):
                break #Se considera el obstaculo superado

        msg.linear.x = 0.0 #Frenamos al robot movil
        self.cmd_vel_pub.publish(msg) #Publicamos la velocidad del robot movil

    '''
    Funcion para recibir las coordenadas del fruto detectado
    '''
    def fruit_callback(self,msg):

        #Guardamos las coordenadas X,Y y Z del fruto detectado por la camara
        self.fruit_position = [

            msg.point.x,

            msg.point.y,

            msg.point.z

        ]
        #Mostramos mensaje por terminal
        self.get_logger().info(

            f"Fruto: "

            f"{msg.point.x:.3f}, "

            f"{msg.point.y:.3f}, "

            f"{msg.point.z:.3f}"

        )

    
    '''
    Funcion para eliminar el fruto recolectado
    '''
    def delete_grape(self, grape_number):

        grape_name = f"grape_{grape_number}" #Variable que se asigna al fruto

        #Mensaje por terminal
        self.get_logger().info(
            f"Eliminando {grape_name}..."
        )

        request = DeleteEntity.Request() #Peticion para eliminar

        request.name = grape_name #Nombre del fruto que queremos eliminar

        future = self.delete_entity_client.call_async(request) #Enviamos la peticion de forma sincrona

        #Esperamos respuesta por parte de Gazebo
        rclpy.spin_until_future_complete(
            self,
            future
        )

        response = future.result() #Obteneos respuesta

        if response.success: #Si Gazebo ha eliminado el fruto
            #Mensaje por terminal
            self.get_logger().info(
                f"fruto {grape_name} recogido correctamente."
            )

            return True

        else: #Si el fruto no se ha eliminado
            #Mensaje por terminal
            self.get_logger().error(
                f"No se pudo eliminar {grape_name}: "
                f"{response.status_message}"
            )

            return False

    
    '''
    Funcion para abandonar la planta recolectada
    '''
    def leave_plant(self):
        #Mostramos mensaje por terminal
        self.get_logger().info(
            "Abandonando la planta actual..."
        )

        msg = Twist() #Creamos un mensaje tipo Twist()

        
        msg.linear.x = 0.30 #Velocidad de avance

        #Mientras ROS2 siga funcionando
        while rclpy.ok():
            #Procesamos los mensajes obtenidos
            rclpy.spin_once(
                self,
                timeout_sec=0.02
            )
            
            self.cmd_vel_pub.publish(msg) #Publicamos la velocidad de avance

            if self.distance_mean is not None: #Comprobamos que exista la medida del LiDAR
                #Mostramos mensaje por terminal
                self.get_logger().info(
                    f"Alejándose... "
                    f"distancia = {self.distance_mean:.2f} m"
                )
                #Si la planta esta a mas de 1.20 metros
                if self.distance_mean > 1.20:

                    break #Terminamos le movimiento

            time.sleep(0.02)

        

        msg.linear.x = 0.0 #Parar la base

        for _ in range(10): #Publicamos 10 veces el mensaje de parada (aseguramos de la parada)

            self.cmd_vel_pub.publish(msg) #Enviamos velocidad 0

            time.sleep(0.05)

        #Mensaje por terminal
        self.get_logger().info(
            "Planta abandonada."
        )

    '''
    Funcion para realizar el postpick despues de recolectar el producto (1,3,5,7)
    '''
    def prostpick_1(self):
            #Mostramos mensaje por terminal
            self.get_logger().info(
                "Moviendo brazo a la POSICIÓN postpick 1..."
            )
    
            goal = FollowJointTrajectory.Goal() #Creamos el objetivo de la trayectoria
    
            #Articulaciones del robot
            goal.trajectory.joint_names = [
                "shoulder_pan_joint",
                "shoulder_lift_joint",
                "elbow_joint",
                "wrist_1_joint",
                "wrist_2_joint",
                "wrist_3_joint",
            ]
    
            point = JointTrajectoryPoint() #Creamos el punto de la trayectoria
    
            #Postpick usado entre move_arm_position_1 y left_product
            point.positions = [
                1.64,
                -1.22,
                0.77,
                -2.44,
                -1.57,
                1.151,
            ]
    
            
            point.time_from_start = Duration(sec=3) #Tiempo que tarda en alcanzar la posición
    
            goal.trajectory.points.append(point) #Añadimos el punto a la trayectoria
    
            
            future = self.arm_client.send_goal_async(goal) #Enviar trayectoria al controlador
    
            rclpy.spin_until_future_complete(self, future) #Esperar hasta recibir la respuesta del controlador
    
            goal_handle = future.result() #Obtenemos el identificador del objetivo enviado
    
            #Si el controlador no ha aceptado el movimiento
            if not goal_handle.accepted:
                #Mensaje por teminal
                self.get_logger().error(
                    "Movimiento a la POSICIÓN 1 rechazado."
                )
    
                return False
            #Si se ha aceptado el movimiento mostramos por la terminal
            self.get_logger().info(
                "Movimiento a POSICIÓN postpick 1 aceptado."
            )
    
            
            result_future = goal_handle.get_result_async() #Esperar a que termine el movimiento
            #Esperamos hasta que el movimiento haya terminado
            rclpy.spin_until_future_complete(
                self,
                result_future
            )
            #Mostramos mensaje por la terminal
            self.get_logger().info(
                "Brazo colocado en la POSICIÓN POSTPICK 1."
            )
    
            return True

    '''
    Funcion para realizar el postpick despues de recolectar el producto (2,4,6,8)
    '''
    def prostpick_2(self):
        #Mostramos mensaje por terminal
        self.get_logger().info(
            "Moviendo brazo a la POSICIÓN postpick 2..."
        )

        goal = FollowJointTrajectory.Goal() #Creamos el objetivo de la trayectoria

        #Articulaciones del robot
        goal.trajectory.joint_names = [
            "shoulder_pan_joint",
            "shoulder_lift_joint",
            "elbow_joint",
            "wrist_1_joint",
            "wrist_2_joint",
            "wrist_3_joint",
        ]

        point = JointTrajectoryPoint() #Creamos el punto de la trayectoria

        #Postpick usado entre move_arm_position_2 y left_product
        point.positions = [
            -1.6,
            -1.7,
            -0.68,
            -0.50,
            1.12,
            1.151,
        ]

        
        point.time_from_start = Duration(sec=3) #Tiempo que tarda en alcanzar la posición

        goal.trajectory.points.append(point) #Añadimos el punto a la trayectoria

        
        future = self.arm_client.send_goal_async(goal) #Enviar trayectoria al controlador

        rclpy.spin_until_future_complete(self, future) #Esperar hasta recibir la respuesta del controlador

        goal_handle = future.result() #Obtenemos el identificador del objetivo enviado

        #Si el controlador no ha aceptado el movimiento
        if not goal_handle.accepted:
            #Mensaje por teminal
            self.get_logger().error(
                "Movimiento a la POSICIÓN 2 rechazado."
            )

            return False
        #Si se ha aceptado el movimiento mostramos por la terminal
        self.get_logger().info(
            "Movimiento a POSICIÓN postpick 2 aceptado."
        )

        
        result_future = goal_handle.get_result_async() #Esperar a que termine el movimiento
        #Esperamos hasta que el movimiento haya terminado
        rclpy.spin_until_future_complete(
            self,
            result_future
        )
        #Mostramos mensaje por la terminal
        self.get_logger().info(
            "Brazo colocado en la POSICIÓN POSTPICK 2."
        )

        return True

    # =========================================================
    # AÑADIR PESO DEL FRUTO AL CESTO
    # =========================================================

    '''
    Funcion para añadir el peso al cesto del fruto recolectado
    '''
    def add_fruit_to_basket(self, id_fruto_recolectado, id_robot=1):

        fruit_weight = random.uniform(0.5, 3.0) #Generamos un numero aleatorio entre 0.5 y 3, este sera el peso del fruto recolectado actual

        #Mostramos por pantalla
        self.get_logger().info("==============================================")
        self.get_logger().info(f"FRUTO RECOGIDO: id_fruto={id_fruto_recolectado}")
        self.get_logger().info(f"Peso simulado = {fruit_weight:.2f} kg")

        #Llamamos al nuevo metodo de basket.py para poder añadir correctamente id_fruto
        id_cesto_fijo = self.basket.add_fruit_weight_with_trazability(
            fruit_weight=fruit_weight,
            id_fruto=id_fruto_recolectado,
            id_robot=id_robot
        )

        #Mostramos por pantalla
        self.get_logger().info(
            f"🤖 ¡ÉXITO!: El robot {id_robot} ha soltado en el cesto {id_cesto_fijo} el fruto {id_fruto_recolectado}"
        )
        self.get_logger().info("==============================================")

    '''
    Funcion para la ejecucion completa del codigo/comportamiento
    '''
    def execute(self):

        self.start_time = time.perf_counter() #Inicio del cronometro para contrastar resultados de optimización del comportamiento
        while rclpy.ok(): #Mientras ROS2 este funcionando

            nivel = self.battery.carga() #Consultamos la bateria disponible
            ahora = time.perf_counter()
            #Actualizamos si el valor no es nulo, no es infinito y han pasado, como mínimo, 0.2 segundos
            if (self.distance_mean is not None and self.distance_mean != float('inf') and (ahora - ultima_actualizacion_bd) > 0.2):

                #Definimos los datos representados en la tabla lidar
                self.lidar.actualizar(
                    distancia=float(self.distance_mean),
                    frecuencia=15
                )
                ultima_actualizacion_bd = ahora #Reseteamos tiempo para almacenar datos en la base de datos

            if nivel <= 10: #Si el nivel es menor que 10
                #Mensaje por terminal y se mantiene quieto
                self.get_logger().warn(
                    "🔋 Batería baja. No se puede avanzar."
                )
                self.move_base(0.0) #Robot se para

                return

            self.plant_detected = False #Inicializamos la variable que nos indica si se ha detectado alguna planta

            #Mensajes por terminal
            self.get_logger().info(
                "========================================"
            )

            self.get_logger().info(
                "Buscando siguiente objeto..."
            )

            self.get_logger().info(
                "========================================"
            )

            self.move_base(0.25) #Avanza hasta detectar un objeto
            #Mostramos mensaje por terminal
            self.get_logger().info(
                "Objeto detectado por LiDAR."
            )
            #Mostramos mensaje por terminal
            self.get_logger().info(
                "Analizando objeto para determinar si es planta..."
            )

            self.plant_detected = False #Eliminamos cualquier clasificación anterior

            start = time.time() #Guardamos el instante del analisis

            while time.time() - start < 1.0: #Mantenemos el instante del analisis durante 1 segundo
                #Procesamos los mensajes
                rclpy.spin_once(
                    self,
                    timeout_sec=0.05
                )

            if self.plant_detected: #Si detectamos una planta
                #Mostramos mensaje por terminal
                self.get_logger().info(
                    "PLANTA DETECTADA."
                )
                #Añadimos la planta al contador
                self.plant_number += 1

                grape_1 = 2 * self.plant_number - 1 #Calculamos el fruto correspondiente
                grape_2 = 2 * self.plant_number #Calculamos el fruto correspondiente

                #Mostramos mensaje por terminal
                self.get_logger().info(
                    f"Planta número {self.plant_number}"
                )
                #Mostramos mensaje por terminal
                self.get_logger().info(
                    f"Frutos: grape_{grape_1} y grape_{grape_2}"
                )

                success = self.initial_position() #Posicion inicial del brazo

                if not success: #Comprobamos si el movimiento ha fallado
                    #Mostramos mensaje por terminal
                    self.get_logger().error(
                        "No se pudo alcanzar la posición inicial."
                    )

                    return

                time.sleep(2) #Esperamos 2 segundos

                success = self.move_arm_position_1() #Movemos el brazo a la posicion del primer fruto

                if not success: #Comprobamos si el movimiento ha fallado
                    #Mostramos mensaje por terminal
                    self.get_logger().error(
                        "No se pudo alcanzar la posición 1."
                    )

                    return

                time.sleep(2) #Esperamos 2 segundos

                #Si no se ha eliminado el fruto = no se ha recogido todavia
                if not self.delete_grape(grape_1):
                    #Mostramos mensaje por terminal
                    self.get_logger().error(
                        f"No se pudo recoger grape_{grape_1}."
                    )

                    return

                self.fruits_collected += 1 #Añadimos 1 al contador de frutos

                self.get_logger().info(
                    f"Frutos recogidos: "
                    f"{self.fruits_collected}/8"
                )

                time.sleep(1) #Esperamos 1 segundo

                success = self.prostpick_1() #Movemos el brazo a la posicion del primer fruto
                
                if not success: #Comprobamos si el movimiento ha fallado
                    #Mostramos mensaje por terminal
                    self.get_logger().error(
                        "No se pudo alcanzar postpick posición 1."
                    )

                    return

                time.sleep(2) #Esperamos 2 segundos

                success = self.left_product() #Movemos el brazo para depositar el fruto recolectado en el cesto

                if not success: #Comprobamos si ha fallado
                    #Mostramos mensaje por terminal
                    self.get_logger().error(
                        "No se pudo dejar el primer fruto."
                    )

                    return

                self.add_fruit_to_basket(grape_1) #Añadimos el peso del fruto al cesto

                time.sleep(0.5) #Esperamos 2 segundos
                success = self.initial_position() #Colocamos el brazo en la posicion inicial

                if not success: #Si el movimiento ha fallado
                    #Mostramos mensaje por terminal
                    self.get_logger().error(
                        "No se pudo volver a la posición inicial."
                    )

                    return
                success = self.move_arm_position_2() #Colocamos el brazo en la posicion de recoleccion 2

                if not success: #Si e movimiento ha fallado
                    #Mostramos mensaje por terminal
                    self.get_logger().error(
                        "No se pudo alcanzar la posición 2."
                    )

                    return

                time.sleep(2) #Esperamos 2 segundos

                if not self.delete_grape(grape_2): #Si no se ha eliminado el fruto 2
                    #Mostramos mensaje por terminal
                    self.get_logger().error(
                        f"No se pudo recoger grape_{grape_2}."
                    )

                    return

                self.fruits_collected += 1 #Añadimos 1 al contador de frutos
                #Mostramos mensaje
                self.get_logger().info(
                    f"Frutos recogidos: "
                    f"{self.fruits_collected}/8"
                )

                time.sleep(1) #Esperar 1 segundo

                success = self.prostpick_2() #Movemos el brazo a la posicion del primer fruto
                                
                if not success: #Comprobamos si el movimiento ha fallado
                    #Mostramos mensaje por terminal
                    self.get_logger().error(
                        "No se pudo alcanzar postpick posición 2."
                    )

                    return

                time.sleep(2) #Esperamos 2 segundos

                success = self.left_product() #Soltar el fruto recolectado en el cesto

                if not success: #Si no se ha podido llegar a esa posicion
                    #Mostramos mensaje por terminal
                    self.get_logger().error(
                        "No se pudo dejar el segundo fruto."
                    )

                    return

                self.add_fruit_to_basket(grape_2) #Añadimos el peso del fruto al cesto

                success = self.initial_position() #Volver a la posicion inicial

                if not success: #Si no puede ir a la posicion
                    #Mostramos mensaje por terminal
                    self.get_logger().error(
                        "No se pudo volver a la posición inicial."
                    )

                    return
                #Mostramos mensaje por terminal
                self.get_logger().info(
                    "Los dos frutos han sido recogidos."
                )

                self.leave_plant() #Avanzar pasando la planta ya recolectada
                #Mostramos mensaje por terminal
                self.get_logger().info(
                    "========================================"
                )
                #Mostramos mensaje por terminal
                self.get_logger().info(
                    f"Planta {self.plant_number} completada."
                )
                if self.fruits_collected >= 8: #Condicion de parada en el entorno de simulacion. Si se han recolectado 8 frutos

                    elapsed_time = time.perf_counter() - self.start_time #Obtenemos el tiempo de recoleccion temporal

                    #Mostramos por pantalla
                    self.get_logger().info(
                        "========================================"
                    )

                    self.get_logger().info(
                        "LOS 8 FRUTOS HAN SIDO RECOGIDOS"
                    )

                    #Mostramos el tiempo total tardado en ejecutar la recoleccion
                    self.get_logger().info(
                        f"TIEMPO TOTAL DE RECOLECCIÓN: "
                        f"{elapsed_time:.2f} segundos"
                    )

                    #Pasamos el tiempo de segundos a minutos y segundos
                    minutes = int(elapsed_time // 60) #Obtencion de los minutos
                    seconds = elapsed_time % 60 #Obtencion de los segundos

                    #Mostramos por pantalla
                    self.get_logger().info(
                        f"Tiempo total: "
                        f"{minutes} min {seconds:.2f} s"
                    )

                    self.get_logger().info(
                        "========================================"
                    )


                    break
                #Mostramos mensaje por terminal
                self.get_logger().info(
                    "Buscando siguiente objeto..."
                )
                #Mostramos mensaje por terminal
                self.get_logger().info(
                    "========================================"
                )

                self.plant_detected = False #Cambiamos la variable y le atribuimos False para poder continuar con el comportamiento/recoleccion

                continue

            else: #Si detectamos un obstaculo (no es una planta), en este caso en un poste

                #Mostramos mensaje por terminal
                self.get_logger().info(
                    "El objeto NO es una planta."
                )
                #Mostramos mensaje por terminal
                self.get_logger().info(
                    "Pasando el obstáculo..."
                )

                self.pass_obstacle() #Pasamos el obstaculo
                #Mostramos mensaje por terminal
                self.get_logger().info(
                    "Obstáculo superado."
                )

                self.plant_detected = False #Establecemos nuevo valor para la variable

                continue #Volvemos a buscar la planta

'''
Funcion para realizar el comportamiento definido
'''

def main(args=None):

    rclpy.init(args=args) #Iniciamos ROS2

    robot = MobileUR3Controller() #Atribuimos el controlador a la variable robot

    robot.execute() #Ejecutamos la funcion para realizar el comportamiento

    robot.destroy_node() #Eliminamos el nodo creado

    rclpy.shutdown() #Finalizamos ROS2


if __name__ == "__main__": #Comprobamos que el programa se esta eecutando correctamente
    main() #Ejecutamos la funcion para realizar el comportamiento definido