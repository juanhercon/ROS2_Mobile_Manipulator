#pragma once

#include <memory>

#include "rclcpp/rclcpp.hpp"
#include "zimmer_gripper_ros2/gripper_interface.hpp"
#include "zimmer_gripper_ros2/srv/gripper_command.hpp"

class GripperServer : public rclcpp::Node
{
public:

    GripperServer();

private:

    void callback(
        const std::shared_ptr<
            zimmer_gripper_ros2::srv::GripperCommand::Request> request,
        std::shared_ptr<
            zimmer_gripper_ros2::srv::GripperCommand::Response> response);

    GripperInterface interface_;

    rclcpp::Service<
        zimmer_gripper_ros2::srv::GripperCommand>::SharedPtr service_;
};