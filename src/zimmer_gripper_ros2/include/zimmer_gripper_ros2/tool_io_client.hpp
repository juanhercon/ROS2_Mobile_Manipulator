#pragma once

#include <memory>

#include "rclcpp/rclcpp.hpp"
#include "ur_msgs/srv/set_io.hpp"

class ToolIOClient
{
public:

    explicit ToolIOClient(rclcpp::Node* node);

    bool connect();

    bool disconnect();

    bool open();

    bool close();

    bool stop();

private:

    bool setOutput(uint8_t pin, bool state);

    bool pulseOutput(uint8_t pin);

    rclcpp::Node* node_;

    rclcpp::Client<ur_msgs::srv::SetIO>::SharedPtr io_client_;

    bool connected_;
};