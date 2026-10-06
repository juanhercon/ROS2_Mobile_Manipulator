#include "zimmer_gripper_ros2/gripper_interface.hpp"

GripperInterface::GripperInterface(rclcpp::Node* node)
: tool_io_(node)
{
}

bool GripperInterface::connect()
{
    return tool_io_.connect();
}

void GripperInterface::disconnect()
{
    tool_io_.disconnect();
}

bool GripperInterface::open()
{
    return tool_io_.open();
}

bool GripperInterface::close()
{
    return tool_io_.close();
}

bool GripperInterface::stop()
{
    return tool_io_.stop();
}