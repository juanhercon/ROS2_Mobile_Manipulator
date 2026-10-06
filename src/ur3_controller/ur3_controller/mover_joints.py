import rclpy

from rclpy.node import Node
from sensor_msgs.msg import JointState

class JointMover(Node):

    def __init__(self):

        super().__init__('joint_mover')

        self.publisher = self.create_publisher(
            JointState,
            '/joint_states',
            10
        )

        self.timer = self.create_timer(
            0.1,
            self.send_joint_state
        )

    def send_joint_state(self):

        msg = JointState()

        msg.header.stamp = self.get_clock().now().to_msg()

        msg.name = [
            'shoulder_pan_joint',
            'shoulder_lift_joint',
            'elbow_joint',
            'wrist_1_joint',
            'wrist_2_joint',
            'wrist_3_joint'
        ]

        msg.position = [
            0.5,
            -1.0,
            1.2,
            -0.5,
            0.3,
            0.0
        ]

        self.publisher.publish(msg)

def main(args=None):

    rclpy.init(args=args)

    node = JointMover()

    rclpy.spin(node)

    node.destroy_node()

    rclpy.shutdown()

if __name__ == '__main__':
    main()