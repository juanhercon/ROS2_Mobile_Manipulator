#!/usr/bin/env python3

import cv2
import numpy as np

import rclpy

from rclpy.node import Node

from sensor_msgs.msg import Image

from std_msgs.msg import Bool

from cv_bridge import CvBridge #Conversor de imagenes entre ROS y OpenCV
from sensor_msgs.msg import CameraInfo

from geometry_msgs.msg import Point
from geometry_msgs.msg import PointStamped

from rclpy.parameter import Parameter

import tf2_ros

from geometry_msgs.msg import PointStamped

from tf2_geometry_msgs import do_transform_point

from mobile_ur3_database.fruit import FruitTable

from std_msgs.msg import Float32

import time

class MobileUR3Vision(Node):

    def __init__(self):

        super().__init__("mobile_ur3_vision",
            parameter_overrides=[
                Parameter(
                    "use_sim_time",
                    Parameter.Type.BOOL,
                    True
                )
            ]
        ) #Definicion del archivo

        self.bridge = CvBridge() #Utilizar Bridge para convertir imagenes de ROS a OpenCV

        self.image = None #Variable imagen de la camara RGB

        self.depth_image = None #Variable profundidad de la imagen de la camara RGBD

        #Parametros intrinsecos de la camara
        self.fx = None #Distancia focal en el eje x
        self.fy = None #Distancia focal en el eje y

        self.cx = None #Centro optico en el eje x
        self.cy = None #Centro optico en el eje y

        #Subscriptor para conseguir la imagen de la camara RGBD
        self.create_subscription(
            Image,
            "/wrist_camera/image_raw",
            self.image_callback,
            10
        )

        #subscriptor para conseguir la profundidad de la imagen de la camara RGBD
        self.create_subscription(
            Image,
            "/wrist_camera/depth/image_raw",
            self.depth_callback,
            10
        )

        #Subscriptor para conseguir informacion de la camara RGBD
        self.create_subscription(
            CameraInfo,
            "/wrist_camera/camera_info",
            self.camera_info_callback,
            10
        )

        #Creamos el publicador para indicar que se ha detectado una planta
        self.result_pub = self.create_publisher(
            Bool,
            "/plant_detected",
            10
        )

        #Creamos el publicador para determinar la posicion del fruto detectado
        self.fruit_pub = self.create_publisher(
            PointStamped,
            "/fruit_position",
            10
        )

        self.image_header = None

        #Buffer de las transformaciones TF2
        self.tf_buffer = tf2_ros.Buffer()

        #Listener que recibe las transformaciones
        self.tf_listener = tf2_ros.TransformListener(
            self.tf_buffer,
            self
        )

        self.fruit_table = FruitTable() #Variable para modificar la tabla Fruto
        self.last_fruit_db_time = 0.0 #Inicializar a 0 el tiempo
        self.fruit_db_interval = 1.0 #Intervalo de tiempo

        self.green_ratio_pub = self.create_publisher( #Creamos el publicador para el topic \green_ratio
            Float32,
            "/green_ratio",
            10
        )

############################################################################################
    
    def image_callback(self,msg):
        #Obtener imagen en RGB
        self.image = self.bridge.imgmsg_to_cv2(
        msg,
        desired_encoding="bgr8"
    )

        self.image_header = msg.header


    def camera_info_callback(self,msg):
        
        self.fx = msg.k[0] #Distancia focal eje x
        self.fy = msg.k[4] #Distancia focal eje y

        self.cx = msg.k[2] #Centro optico eje x
        self.cy = msg.k[5] #Centro optico eje y

    '''Funcion para detectar porcentaje de verde en la imagen captada por la camara RGBD'''
    def detect_green(self):

        if self.image is None: #Si no existe imagen
            return False #Devolver None

        hsv = cv2.cvtColor(self.image,cv2.COLOR_BGR2HSV) #Convertir RGB a HSV

        lower = np.array([15,40,40]) #Rango bajo de deteccion del color verde
        upper = np.array([90,255,255]) #Rango alto de deteccion del color verde

        #Segmentacion del color verde hallado en la imagen de la camara RGB
        mask = cv2.inRange(
            hsv,
            lower,
            upper
        )

        pixels_green = np.count_nonzero(mask) #Pixeles verdes en la imagen = pixeles que no valen 0

        total = mask.shape[0]*mask.shape[1] #Numero total de pixeles

        ratio = pixels_green/total #Porcentaje de verde

        porcentaje_verde = ratio * 100.0

        # =====================================================
        # PUBLICAR EL PORCENTAJE REAL
        # =====================================================

        msg_green = Float32() #Creamos una variable para almacenar porcentaje de color verde (atributo en tabla Camara)

        msg_green.data = float(porcentaje_verde) #Obtenemos el porcentaje verde

        #Publicamos el porcentaje de verde
        self.green_ratio_pub.publish(
            msg_green
        )

        #Mostramos por terminal

        self.get_logger().info(
            f"Verde = {porcentaje_verde:.1f}%"
        )

        #Clasificamos correctamente

        return ratio > 0.20
    
    '''Funcion para publicar la deteccion'''
    def publish_result(self):

        msg = Bool()

        msg.data = self.detect_green() #True o False segun detect_green

        self.result_pub.publish(msg) #Publicar el resultado en el publicador de deteccion de la planta

    '''Funcion para detectar el producto a recolectar'''
    def detect_fruit(self):

        #Si la imagen es None o la profundidad de la imagen es none o el focal x
        if self.image is None or self.depth_image is None or self.fx is None:
            return []

        hsv = cv2.cvtColor(self.image, cv2.COLOR_BGR2HSV) #Segmentaciion de color
        
        #Rango establecido para el morado (color de la fruta a recolectar)
        lower = np.array([130, 40, 40]) 
        upper = np.array([165, 255, 255])

        mask = cv2.inRange(hsv, lower, upper)

        kernel = np.ones((3,3), np.uint8)
        mask = cv2.morphologyEx(mask, cv2.MORPH_OPEN, kernel)
        mask = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, kernel)

        contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        image_draw = self.image.copy()
        fruits = []

        for cnt in contours:
            area = cv2.contourArea(cnt)
            if area < 250: #Evitar errores
                continue

            #Bounding box del fruto
            x, y, w, h = cv2.boundingRect(cnt)

            #Extraemos la region de la camara y profundidad
            roi_depth = self.depth_image[y:y+h, x:x+w]
            
            #Creamos una mascara local
            fruit_mask_roi = np.zeros((h, w), dtype=np.uint8)
            cnt_shifted = cnt - [x, y] #Desplazamos el entorno
            cv2.drawContours(fruit_mask_roi, [cnt_shifted], -1, 255, -1)

            #Encontramos en el ROI los pixeles del fruto
            ys_local, xs_local = np.where(fruit_mask_roi == 255)

            if len(xs_local) == 0:
                continue

            #Calculamos el centroide
            cx = int(np.mean(xs_local) + x)
            cy = int(np.mean(ys_local) + y)

            if self.image.shape[:2] != self.depth_image.shape[:2]:
            #Redimensionamos la profundidad para que coincida con la imagen RGB
                self.depth_image = cv2.resize(self.depth_image, (self.image.shape[1], self.image.shape[0]), interpolation=cv2.INTER_NEAREST)

            #Extraemos los valores de profundidad provenientes del ROI
            depth_values = roi_depth[ys_local, xs_local]

            #Obtencion de profundidad valida
            valid_depth_mask = np.isfinite(depth_values) & (depth_values > 0)
            valid_depth_values = depth_values[valid_depth_mask]

            if len(valid_depth_values) == 0:
                cv2.putText(image_draw, "Sin depth", (x, y-10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0,255,255), 2)
                continue

            #Seleccionamos punto mas cercano del fruto
            depth = float(np.min(valid_depth_values))

            #Proyeccion de las coordenadas 3D
            X = (cx - self.cx) * depth / self.fx
            Y = (cy - self.cy) * depth / self.fy
            Z = depth

            #Dibujamos rectangulo
            cv2.rectangle(image_draw, (x, y), (x+w, y+h), (255, 0, 255), 2)
            cv2.circle(image_draw, (cx, cy), 5, (0, 255, 255), -1)
            
            cv2.putText(image_draw, f"X={X:.2f}", (x, y-35), cv2.FONT_HERSHEY_SIMPLEX, 0.4, (255,255,255), 1)
            cv2.putText(image_draw, f"Y={Y:.2f}", (x, y-22), cv2.FONT_HERSHEY_SIMPLEX, 0.4, (255,255,255), 1)
            cv2.putText(image_draw, f"Z={Z:.2f}m", (x, y-9), cv2.FONT_HERSHEY_SIMPLEX, 0.4, (255,255,255), 1)

            fruits.append({"cx": cx, "cy": cy, "X": X, "Y": Y, "Z": Z, "area": area})
            self.fruit_table.insertar(
                "Uva",
                X,
                Y,
                Z,
                82.5
            )

        #Mostramos imagenes
        cv2.imshow("Mascara", mask)
        cv2.imshow("Frutos", image_draw)
        cv2.waitKey(1)

        #Si detecta mas de un fruto
        if len(fruits)>0:
            #Recolecta el fruto mayor
            best = max(
                fruits,
                key=lambda f:f["area"]
            )
            ahora = time.time() #Variable ahora que almacenara el tiempo actual

            if ahora - self.last_fruit_db_time >= self.fruit_db_interval: #Si superamos el intervalo de espera insertamos en la tabla fruto

                self.fruit_table.insertar(
                    "Uva",
                    float(best["X"]),
                    float(best["Y"]),
                    float(best["Z"]),
                    82.5
                )

                self.last_fruit_db_time = ahora

            msg = PointStamped() #Definimos msg

            msg.header = self.image_header #Frame/tiempo de la imagen

            msg.point.x = best["X"] #Mejor x
            msg.point.y = best["Y"] #Mejor y
            msg.point.z = best["Z"] #Mejor z

            self.fruit_pub.publish(msg) #Publicamos

            x_optical = (cx - self.cx) * depth / self.fx #Definimos el calculo de la coordenada x del fruto respecto de la camara
            y_optical = (cy - self.cy) * depth / self.fy #Definimos el calculo de la coordenada y del fruto respecto de la camara
            z_optical = depth #Definimos el calculo de la coordenada z del fruto respecto de la camara
    
            #Posicion punto-camara
            fruit_point_cam = PointStamped()
            fruit_point_cam.header = self.image_header
    
            # Aplicamos la equivalencia de ejes
            fruit_point_cam.point.x = float(z_optical)   # Adelante es X
            fruit_point_cam.point.y = float(-x_optical)  # Izquierda es Y
            fruit_point_cam.point.z = float(-y_optical)  # Arriba es Z
                        
            try:
                #Modifica el stamp para pedir el tiempo a ROS2
                fruit_point_cam.header.stamp = rclpy.time.Time().to_msg() 

                #Transfromacion necesaria para detectar la posicion correctamente
                transform = self.tf_buffer.lookup_transform(
                    "odom",
                    fruit_point_cam.header.frame_id,
                    fruit_point_cam.header.stamp,
                    rclpy.duration.Duration(seconds=0.1)
                )
                fruit_point_odom = do_transform_point(fruit_point_cam, transform)
                self.fruit_pub.publish(fruit_point_odom)
                
                #Publica la posicion real en ODOM
                self.fruit_pub.publish(fruit_point_odom)

                self.get_logger().info(
                    f"¡ÉXITO! Fruto con respecto a origen -> "
                    f"X={fruit_point_odom.point.x:.3f} "
                    f"Y={fruit_point_odom.point.y:.3f} "
                    f"Z={fruit_point_odom.point.z:.3f}"
                )

            except Exception as e:
                self.get_logger().error(
                    f"No se pudo transformar el fruto a ODOM: {e}"
                )
            #Printear el fruto seleccionado que se va a recolectar
            self.get_logger().info(
                f"Fruto seleccionado -> "
                f"X={best['X']:.3f} "
                f"Y={best['Y']:.3f} "
                f"Z={best['Z']:.3f}"
            )
            self.get_logger().info(
            f"Frame cámara: {self.image_header.frame_id}"
            )

        #Numero total de frutos mostrados
        self.get_logger().info(
            f"Frutos detectados: {len(fruits)}"
        )

        print("RGB:", self.image.shape)
        print("DEPTH:", self.depth_image.shape)

        return fruits

    '''Funcion para mostrar los '''
    def depth_callback(self,msg):
        #Convierte la profundidad de ROS a OpenCV
        self.depth_image = self.bridge.imgmsg_to_cv2(
        msg,
        desired_encoding="32FC1"
    )

        #Mostran por pantalla
        if not hasattr(self, "_depth_info"):

            self._depth_info = True

            print("\n===== INFORMACION DEPTH =====")
            print("Shape:", self.depth_image.shape)
            print("Tipo:", self.depth_image.dtype)

            print("Min:", np.nanmin(self.depth_image))
            print("Max:", np.nanmax(self.depth_image))

            print("Pixeles finitos:",
                np.isfinite(self.depth_image).sum())

            print("=============================\n")
        
def main():

    rclpy.init() #Inicializar ROS2

    node = MobileUR3Vision() #Crear nodo

    while rclpy.ok(): #Mientras ROS2 este activo

        rclpy.spin_once(node) #Ejecuta el nodo

        if node.image is not None: #Si existe imagen

            node.publish_result() #Publicar si existe planta

            fruits = node.detect_fruit() #Detectar fruto

            print(fruits)

    node.destroy_node() #Eliminar el nodo creado

    rclpy.shutdown()