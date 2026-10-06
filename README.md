ROS2 Mobile Manipulator

Sistema de manipulador móvil basado en ROS 2 Humble, compuesto por una plataforma móvil y un brazo robótico Universal Robots UR3. El proyecto está orientado al desarrollo de una plataforma robótica para aplicaciones de agricultura inteligente, incluyendo simulación, control del manipulador, visión artificial, adquisición de datos y comunicación con dispositivos y sensores.

Descripción

Este proyecto desarrolla un sistema robótico móvil capaz de desplazarse por un entorno agrícola mientras transporta un brazo robótico UR3.

La plataforma integra diferentes elementos de percepción, control y procesamiento:

Plataforma móvil.
Brazo robótico Universal Robots UR3.
Pinza Zimmer.
Cámara RGB-D.
LiDAR.
IMU.
Controladores de motores.
Ordenador de control.
Sistema de almacenamiento y gestión de datos.
Entorno de simulación mediante Gazebo.
Visualización y monitorización mediante RViz2.
Comunicación entre los diferentes componentes mediante ROS 2.

El objetivo general es disponer de una arquitectura modular que permita desarrollar y probar el sistema inicialmente en simulación y posteriormente utilizar el mismo software con el robot físico.

Características principales
ROS 2 Humble sobre Ubuntu 22.04.
Integración con un brazo robótico Universal Robots UR3.
Plataforma móvil con descripción URDF/Xacro.
Simulación mediante Gazebo.
Visualización mediante RViz2.
Integración con MoveIt 2 para el manipulador.
Control del UR3 mediante ROS 2.
Secuencias de pick-and-place.
Integración de una pinza Zimmer.
Procesamiento de información procedente de sensores.
Gestión de información del sistema mediante un paquete de base de datos.
Arquitectura modular basada en paquetes ROS 2.
Separación entre código propio y dependencias externas de Universal Robots.
Arquitectura del sistema

La arquitectura general del manipulador móvil está formada por cuatro bloques principales:

                         ┌─────────────────────────┐
                         │       ROS 2 Humble      │
                         └────────────┬────────────┘
                                      │
          ┌───────────────────────────┼───────────────────────────┐
          │                           │                           │
          ▼                           ▼                           ▼
 ┌─────────────────┐       ┌──────────────────┐        ┌─────────────────┐
 │ Plataforma móvil│       │    Manipulador   │        │     Visión      │
 │                 │       │      UR3         │        │    artificial   │
 └────────┬────────┘       └────────┬─────────┘        └────────┬────────┘
          │                         │                           │
          ▼                         ▼                           ▼
      Motores                  MoveIt 2                    Cámara RGB-D
      ODrive                   UR Controller                Sensores
          │                         │
          ▼                         ▼
      Encoders                Zimmer Gripper
          
          └───────────────────────┬─────────────────────────────┘
                                  │
                                  ▼
                         ┌─────────────────┐
                         │ Gestión de datos│
                         │   y sensores    │
                         └─────────────────┘
Arquitectura física

El sistema móvil está concebido como una plataforma que transporta el brazo UR3 y los elementos necesarios para su funcionamiento.

Los principales componentes son:

┌─────────────────────────────────────────────────────────────┐
│                    PLATAFORMA MÓVIL                         │
│                                                             │
│   LiDAR        IMU         Ordenador / ROS 2        Cámara   │
│     │           │                 │                    │     │
│     └───────────┴─────────────────┴────────────────────┘     │
│                                                             │
│                  ┌───────────────────┐                      │
│                  │      UR3          │                      │
│                  │ Brazo robótico    │                      │
│                  └─────────┬─────────┘                      │
│                            │                                │
│                     Zimmer Gripper                          │
│                                                             │
│       Motores / ODrive              Motores / ODrive        │
│              │                              │               │
│        Ruedas izquierdas              Ruedas derechas       │
│                                                             │
└─────────────────────────────────────────────────────────────┘
Arquitectura software

El software está organizado en paquetes ROS 2 independientes:

ROS2 Mobile Manipulator
│
├── mobile_ur3_controller
│   └── Control de la plataforma móvil
│
├── mobile_ur3_database
│   └── Gestión y almacenamiento de información
│
├── mobile_ur3_description
│   └── URDF / Xacro / Gazebo / RViz2
│
├── mobile_ur3_vision
│   └── Procesamiento de visión
│
├── ur3_controller
│   └── Control del brazo UR3
│
├── ur3_pick_place
│   └── Secuencias de manipulación
│
└── zimmer_gripper_ros2
    └── Interfaz ROS 2 para la pinza Zimmer
Paquetes ROS 2
mobile_ur3_controller

Paquete destinado al control de la plataforma móvil.

Su función es proporcionar los nodos y componentes necesarios para controlar el movimiento de la plataforma y servir como interfaz entre ROS 2 y los elementos de accionamiento del sistema móvil.

mobile_ur3_database

Paquete destinado a la gestión de la información generada por el sistema robótico.

Incluye diferentes entidades relacionadas con el manipulador móvil, entre ellas:

Robot móvil.
Brazo robótico.
Fruto.
Batería.
Cámara.
IMU.
LiDAR.
Cesto.
Trayectoria.
Estadísticas del robot.

El paquete proporciona una estructura software para almacenar y gestionar información relacionada con el estado y funcionamiento del sistema.

mobile_ur3_description

Paquete que contiene la descripción del manipulador móvil.

Incluye:

Modelos URDF.
Modelos Xacro.
Configuración de ros2_control.
Modelos para Gazebo.
Mundo de simulación.
Modelo de la plataforma móvil.
Modelo del UR3.
Entorno agrícola.
Modelo de filas de cultivo.
Modelo de racimos de uva.
Configuraciones para RViz2.

Este paquete constituye la base de la representación virtual del sistema.

mobile_ur3_vision

Paquete destinado al procesamiento de información visual.

Su objetivo es proporcionar la infraestructura necesaria para incorporar visión artificial al manipulador móvil mediante cámaras y algoritmos de procesamiento de imágenes.

ur3_controller

Paquete destinado al control del brazo robótico UR3.

Proporciona nodos ROS 2 relacionados con el movimiento del manipulador y permite integrar el brazo dentro de la arquitectura general del sistema.

ur3_pick_place

Paquete destinado a las operaciones de manipulación.

Incluye componentes relacionados con:

Movimiento del robot.
Definición de posiciones.
Control de la pinza.
Secuencias de pick-and-place.
Control del robot real.

Este paquete permite desarrollar y ejecutar secuencias de manipulación de objetos.

zimmer_gripper_ros2

Paquete desarrollado para integrar una pinza Zimmer con ROS 2.

Incluye:

Interfaz de la pinza.
Servidor de acciones.
Servicio de comandos.
Comunicación TCP.
Comunicación con las entradas/salidas de herramienta.
Definición de acciones ROS 2.

La arquitectura del paquete permite utilizar la pinza desde otros nodos del sistema mediante interfaces estándar de ROS 2.

Dependencias externas

Este repositorio contiene únicamente los paquetes desarrollados específicamente para el proyecto.

Los componentes oficiales de Universal Robots se mantienen como dependencias externas y no forman parte de este repositorio.

Las principales dependencias externas son:

Universal Robots ROS 2 Description.
Universal Robots ROS 2 Driver.
Universal Robots ROS 2 Gazebo Simulation.
Universal Robots Client Library.
MoveIt 2.

Esto permite mantener separado el código desarrollado para el proyecto de las bibliotecas y paquetes mantenidos por terceros.

Las dependencias externas deben descargarse desde sus repositorios oficiales antes de compilar el workspace.

Requisitos
Sistema operativo
Ubuntu 22.04 LTS
ROS 2
ROS 2 Humble
Herramientas principales
ROS 2 Humble
Gazebo
RViz2
MoveIt 2
Colcon
Git
rosdep

Para trabajar con el robot físico también se requiere:

Universal Robots UR3.
Control Box de Universal Robots.
PolyScope.
Conexión Ethernet entre el ordenador y el robot.
URCap de External Control configurado en el robot.
Instalación
1. Clonar el repositorio
cd ~
git clone git@github.com:juanhercon/ROS2_Mobile_Manipulator.git
cd ROS2_Mobile_Manipulator

El workspace puede utilizarse directamente como:

~/ROS2_Mobile_Manipulator

Si se desea mantener el nombre utilizado durante el desarrollo:

mv ROS2_Mobile_Manipulator ur3_ws
2. Cargar ROS 2 Humble
source /opt/ros/humble/setup.bash
3. Descargar las dependencias de Universal Robots

Los repositorios oficiales de Universal Robots deben descargarse dentro de src/.

La rama utilizada debe ser compatible con ROS 2 Humble.

La estructura resultante será similar a:

src/
├── mobile_ur3_controller/
├── mobile_ur3_database/
├── mobile_ur3_description/
├── mobile_ur3_vision/
├── ur3_controller/
├── ur3_pick_place/
├── zimmer_gripper_ros2/
│
├── Universal_Robots_Client_Library/
├── Universal_Robots_ROS2_Description/
├── Universal_Robots_ROS2_Driver/
└── Universal_Robots_ROS2_Gazebo_Simulation/

Estas dependencias no se almacenan en el repositorio principal porque son proyectos externos.

4. Instalar dependencias ROS

Desde la raíz del workspace:

cd ~/ROS2_Mobile_Manipulator

Ejecutar:

rosdep update
rosdep install --from-paths src --ignore-src -r -y
Compilación

Antes de compilar:

source /opt/ros/humble/setup.bash

Desde la raíz del workspace:

cd ~/ROS2_Mobile_Manipulator

Compilar:

colcon build --symlink-install

Una vez finalizada la compilación:

source install/setup.bash

Para comprobar que los paquetes están disponibles:

ros2 pkg list | grep mobile_ur3

También se pueden comprobar los paquetes relacionados con el UR3:

ros2 pkg list | grep ur3
Simulación

La simulación permite desarrollar y probar el sistema antes de utilizar el robot físico.

Gazebo

La descripción del sistema se encuentra en:

src/mobile_ur3_description/

Los principales elementos de simulación incluyen:

models/
worlds/
urdf/
config/
launch/

El entorno agrícola incluye un modelo de fila de cultivo:

models/vineyard_row/

y un mundo de simulación:

worlds/vineyard.world

Para lanzar la simulación se utilizará el archivo de lanzamiento correspondiente del paquete:

source /opt/ros/humble/setup.bash
source ~/ROS2_Mobile_Manipulator/install/setup.bash

ros2 launch mobile_ur3_description mobile_ur3.launch.py
RViz2

RViz2 permite visualizar el modelo del manipulador móvil, sus articulaciones y diferentes elementos de información publicados mediante ROS 2.

El paquete contiene una configuración específica:

src/mobile_ur3_description/rviz/rviz_topics.rviz

RViz2 puede iniciarse mediante:

rviz2

o utilizando el archivo de configuración correspondiente.

MoveIt 2

El manipulador UR3 puede integrarse con MoveIt 2 para realizar planificación y control de movimiento.

La configuración de MoveIt utilizada para el UR3 procede de las dependencias de Universal Robots.

Un ejemplo de lanzamiento es:

source /opt/ros/humble/setup.bash
source ~/ROS2_Mobile_Manipulator/install/setup.bash

ros2 launch ur_moveit_config ur_moveit.launch.py ur_type:=ur3

El parámetro:

ur_type:=ur3

indica que el robot utilizado es un Universal Robots UR3.

Control del UR3 real

El sistema también puede utilizarse con un UR3 físico mediante el driver oficial de Universal Robots para ROS 2.

Por motivos de seguridad y privacidad, la dirección IP del robot no se almacena en este repositorio.

El lanzamiento debe realizarse utilizando:

ros2 launch ur_robot_driver ur_control.launch.py \
    ur_type:=ur3 \
    robot_ip:=<ROBOT_IP>

donde:

<ROBOT_IP>

debe sustituirse por la dirección IP configurada en el controlador del robot.

Configuración previa

Antes de iniciar el driver es necesario comprobar:

El UR3 está encendido.
El ordenador y el robot tienen conectividad Ethernet.
La configuración de red es correcta.
PolyScope está correctamente configurado.
El robot permite el control externo.
El URCap External Control está instalado y configurado cuando sea necesario.
El robot se encuentra en un estado compatible con la ejecución remota.
Conexión

Una vez configurado el robot:

source /opt/ros/humble/setup.bash
source ~/ROS2_Mobile_Manipulator/install/setup.bash

Ejecutar:

ros2 launch ur_robot_driver ur_control.launch.py \
    ur_type:=ur3 \
    robot_ip:=<ROBOT_IP>

Nunca se debe incluir una dirección IP privada específica del laboratorio en el repositorio público.

Pinza Zimmer

La integración de la pinza se realiza mediante el paquete:

zimmer_gripper_ros2

El paquete proporciona interfaces ROS 2 para controlar la pinza y comunicarse con ella mediante los mecanismos implementados en el proyecto.

Las interfaces incluyen:

action/gripper.action
srv/GripperCommand.srv

y componentes de comunicación:

src/gripper_interface.cpp
src/gripper_server.cpp
src/tcp.client.cpp
src/tool_io_client.cpp
Visión artificial

La arquitectura incorpora una cámara RGB-D para proporcionar información visual al sistema.

La cámara puede utilizarse para tareas relacionadas con:

Percepción del entorno.
Localización de objetos.
Identificación de frutos.
Estimación de posiciones.
Apoyo a las operaciones de manipulación.

El código relacionado con visión se encuentra en:

src/mobile_ur3_vision/
Sensores

El sistema está preparado para integrar diferentes sensores:

Sensor	Función
RGB-D	Percepción visual y profundidad
LiDAR	Percepción del entorno y navegación
IMU	Estimación de orientación y movimiento
Encoders	Medición del movimiento de las ruedas
Sensores del robot	Estado del UR3
Sensores de la plataforma	Monitorización del sistema

La información de estos sensores puede integrarse dentro de la arquitectura ROS 2 y almacenarse mediante el sistema de gestión de datos.

Gestión de datos

El paquete:

mobile_ur3_database

proporciona una estructura para gestionar información relacionada con:

Robot
Brazo robótico
Fruto
Batería
Cámara
IMU
LiDAR
Cesto
Trayectoria
Estadísticas

Esta arquitectura permite ampliar posteriormente el sistema con tecnologías de almacenamiento y monitorización externas.

Estructura del proyecto

La estructura principal del repositorio es:

ROS2_Mobile_Manipulator/
│
├── .gitignore
├── README.md
│
└── src/
    │
    ├── mobile_ur3_controller/
    │
    ├── mobile_ur3_database/
    │
    ├── mobile_ur3_description/
    │
    ├── mobile_ur3_vision/
    │
    ├── ur3_controller/
    │
    ├── ur3_pick_place/
    │
    └── zimmer_gripper_ros2/

Los directorios generados durante la compilación no se almacenan en Git:

build/
install/
log/

Las dependencias oficiales de Universal Robots también están excluidas del repositorio mediante .gitignore.

Flujo de desarrollo

El desarrollo del sistema sigue una estrategia de validación progresiva:

        Desarrollo ROS 2
               │
               ▼
       ┌───────────────┐
       │  URDF / Xacro │
       └───────┬───────┘
               │
               ▼
          Gazebo / RViz2
               │
               ▼
           MoveIt 2
               │
               ▼
       Pruebas de control
               │
               ▼
       Integración sensores
               │
               ▼
       Integración de pinza
               │
               ▼
          UR3 físico
               │
               ▼
       Sistema completo

Este enfoque permite probar individualmente los diferentes componentes antes de realizar la integración completa del sistema.

Control de versiones

El proyecto utiliza Git para el control de versiones.

El repositorio contiene únicamente el código desarrollado específicamente para el manipulador móvil.

Las dependencias externas se mantienen separadas para facilitar:

Mantenimiento.
Actualización de dependencias.
Reutilización del proyecto.
Control del código desarrollado.
Reproducibilidad del entorno.

Los cambios deben incorporarse mediante commits descriptivos.

Ejemplos:

git add README.md
git commit -m "docs: add project README"
git push

Para cambios de funcionalidades:

git add src/mobile_ur3_controller
git commit -m "feat: improve mobile platform control"
git push

Para correcciones:

git add src/ur3_controller
git commit -m "fix: correct UR3 joint control"
git push
Convención de commits

Se recomienda utilizar una convención basada en los siguientes tipos:

Tipo	Uso
feat	Nueva funcionalidad
fix	Corrección de errores
docs	Documentación
refactor	Refactorización
test	Pruebas
build	Cambios relacionados con compilación
chore	Mantenimiento

Ejemplos:

feat: add mobile platform controller
feat: add vineyard simulation model
feat: add Zimmer gripper interface
fix: correct UR3 joint control
docs: add installation instructions
docs: document real robot connection
refactor: reorganize database nodes
Licencia

El código desarrollado específicamente para este proyecto se distribuirá bajo la licencia indicada en el archivo:

LICENSE

Las dependencias de terceros, incluyendo los paquetes de Universal Robots, mantienen sus respectivas licencias y condiciones de distribución.

Antes de redistribuir o modificar componentes externos, debe consultarse la licencia correspondiente de cada proyecto.

Estado del proyecto

El proyecto se encuentra en desarrollo.

Las principales líneas de trabajo incluyen:

Integración completa de la plataforma móvil.
Control del UR3.
Integración de la pinza Zimmer.
Simulación del sistema completo.
Integración de sensores.
Visión artificial.
Gestión de datos.
Validación experimental con el robot real.
Integración de tecnologías IoT.
Desarrollo de aplicaciones orientadas a agricultura inteligente.
Autor

Juan Nandez

Proyecto desarrollado como parte del trabajo de investigación y desarrollo de un sistema robótico móvil basado en ROS 2 para aplicaciones de agricultura inteligente.

Tecnologías utilizadas
Ubuntu 22.04
ROS 2 Humble
Gazebo
RViz2
MoveIt 2
Python
C++
URDF
Xacro
ros2_control
Universal Robots UR3
Zimmer Gripper
Git
GitHub
Repositorio

Código fuente:

https://github.com/juanhercon/ROS2_Mobile_Manipulator
