import rclpy
import time

from ur_msgs.srv import SetIO

class Gripper:

    def __init__(self, node):

        self.node = node

        self.client = node.create_client(
            SetIO,
            "/io_and_status_controller/set_io"
        )

        while not self.client.wait_for_service(timeout_sec=1.0):
            self.node.get_logger().info("Esperando servicio de la pinza...")
    
    def set_output(self, pin, state):

        request = SetIO.Request()

        request.fun = SetIO.Request.FUN_SET_DIGITAL_OUT
        request.pin = pin
        request.state = 1.0 if state else 0.0

        future = self.client.call_async(request)

        rclpy.spin_until_future_complete(self.node, future)

        if future.result() is None:
            self.node.get_logger().error("Error llamando a SetIO")
            return False

        return future.result().success
    
    def open(self):

        self.node.get_logger().info("Abriendo pinza")

        self.set_output(16, True)

        time.sleep(0.2)

        self.set_output(16, False)

    def close(self):

        self.node.get_logger().info("Cerrando pinza")

        self.set_output(17, True)

        time.sleep(0.2)

        self.set_output(17, False)