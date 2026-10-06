import rclpy
from rclpy.node import Node
from trajectory_msgs.msg import JointTrajectory, JointTrajectoryPoint

class PickPlace(Node):
    def __init__(self):
        super().__init__('ur3_pick_place')

        self.pub = self.create_publisher(
            JointTrajectory,
            '/joint_trajectory_controller/joint_trajectory',
            10
        )

        self.timer = self.create_timer(2.0, self.send_trajectory)
        self.sent = False

        self.joint_names = [
            'shoulder_pan_joint',
            'shoulder_lift_joint',
            'elbow_joint',
            'wrist_1_joint',
            'wrist_2_joint',
            'wrist_3_joint'
        ]

    def send_trajectory(self):
        if self.sent:
            return

        msg = JointTrajectory()
        msg.joint_names = self.joint_names

        point1 = JointTrajectoryPoint()
        point1.positions = [1.57, -1.57, 0.0, -1.57, 0.0, 1.151]
        point1.time_from_start.sec = 3

        point2 = JointTrajectoryPoint()
        point2.positions = [1.57, -1.57, 0.0, -1.57, 0.0, 1.151]
        point2.time_from_start.sec = 6

        point3 = JointTrajectoryPoint()
        point3.positions = [0.0, -2.155, -1.0, 0.0, 1.57, 1.151]
        point3.time_from_start.sec = 9

        point4 = JointTrajectoryPoint()
        point4.positions = [0.0, -2.155, -1.0, 0.0, 1.57, 1.151]
        point4.time_from_start.sec = 12

        point5 = JointTrajectoryPoint()
        point5.positions = [-1.57, -1.5, -2.30, -1.27, 1.57, 1.151]
        point5.time_from_start.sec = 15

        point6 = JointTrajectoryPoint()
        point6.positions = [-1.57, -1.5, -2.30, -1.27, 1.57, 1.151]
        point6.time_from_start.sec = 18

        point7 = JointTrajectoryPoint()
        point7.positions = [1.57, -1.57, 0.0, -1.57, 0.0, 1.151]
        point7.time_from_start.sec = 21

        msg.points = [point1, point2, point3, point4, point5, point6, point7]

        self.pub.publish(msg)
        

        self.get_logger().info("Trayectoria enviada (pick & place simulado)")
        self.sent = True


def main():
    rclpy.init()
    node = PickPlace()
    rclpy.spin(node)
    rclpy.shutdown()

if __name__ == '__main__':
    main()