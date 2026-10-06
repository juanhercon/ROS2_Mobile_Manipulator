#pragma once

#include "zimmer_gripper_ros2/tool_io_client.hpp"

class GripperInterface
{
public:

    explicit GripperInterface(rclcpp::Node* node);

    bool connect();
    void disconnect();

    bool open();
    bool close();
    bool stop();

private:
    ToolIOClient tool_io_;
};