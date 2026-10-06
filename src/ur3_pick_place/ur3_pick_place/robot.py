import rclpy

from rclpy.action import ActionClient
from rclpy.node import Node

from control_msgs.action import FollowJointTrajectory
from trajectory_msgs.msg import JointTrajectory
from trajectory_msgs.msg import JointTrajectoryPoint


JOINT_NAMES = [
    "shoulder_pan_joint",
    "shoulder_lift_joint",
    "elbow_joint",
    "wrist_1_joint",
    "wrist_2_joint",
    "wrist_3_joint"
]


class Robot(Node):

    def __init__(self):

        super().__init__("robot_controller")

        self.client = ActionClient(
            self,
            FollowJointTrajectory,
            "/scaled_joint_trajectory_controller/follow_joint_trajectory"
        )

        self.client.wait_for_server()

    def movej(self, joints, time=3.0):

        goal = FollowJointTrajectory.Goal()

        traj = JointTrajectory()
        traj.joint_names = JOINT_NAMES

        point = JointTrajectoryPoint()

        point.positions = joints
        point.time_from_start.sec = int(time)

        traj.points.append(point)

        goal.trajectory = traj

        future = self.client.send_goal_async(goal)

        rclpy.spin_until_future_complete(self, future)

        goal_handle = future.result()

        if not goal_handle.accepted:
            self.get_logger().error("Trayectoria rechazada")
            return

        result = goal_handle.get_result_async()

        rclpy.spin_until_future_complete(self, result)