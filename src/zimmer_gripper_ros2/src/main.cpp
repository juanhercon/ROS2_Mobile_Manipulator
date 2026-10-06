#include "rclcpp/rclcpp.hpp"
#include "zimmer_gripper_ros2/gripper_server.hpp"

int main(int argc, char * argv[])
{
    rclcpp::init(argc, argv);

    auto node = std::make_shared<GripperServer>();

    rclcpp::spin(node);

    rclcpp::shutdown();

    return 0;
}