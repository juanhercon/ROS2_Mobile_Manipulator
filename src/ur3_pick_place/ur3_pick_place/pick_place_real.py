import rclpy
import time
from ur3_pick_place.robot import Robot
from ur3_pick_place.gripper import Gripper
from ur3_pick_place.poses import *

def main():

    rclpy.init()

    robot = Robot()

    gripper = Gripper(robot)


    robot.movej(HOME)
    time.sleep(1)
    
    #Escaner2
    '''robot.movej(HOME)
    robot.movej(ESCANEO1)
    time.sleep(1)
    robot.movej(ESCANEO2)
    time.sleep(1)
    robot.movej(HOME)
    time.sleep(1)
    robot.movej(PRE_PICK)'''

    #Escaner3
    robot.movej(HOME)
    time.sleep(1)
    robot.movej(ESCANEO1)
    time.sleep(1)
    robot.movej(ESCANEO2)
    time.sleep(1)
    robot.movej(ESCANEO3)
    time.sleep(1)
    robot.movej(HOME)
    time.sleep(1)
    robot.movej(PRE_PICK)

    robot.movej(PICK)

    time.sleep(0.5)

    gripper.close()

    time.sleep(1)

    robot.movej(HOME)


    robot.movej(PLACE)

    time.sleep(0.5)

    gripper.open()

    time.sleep(0.5)

    robot.movej(HOME)

    robot.destroy_node()

    rclpy.shutdown()


if __name__ == "__main__":
    main()