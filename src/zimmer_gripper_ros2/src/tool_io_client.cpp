#include "zimmer_gripper_ros2/tool_io_client.hpp"

#include <iostream>

ToolIOClient::ToolIOClient(rclcpp::Node* node)
: node_(node),
  connected_(false)
{
    io_client_ =
        node_->create_client<ur_msgs::srv::SetIO>(
            "/io_and_status_controller/set_io");
}

bool ToolIOClient::connect()
{
    if (!io_client_->wait_for_service(std::chrono::seconds(3)))
    {
        RCLCPP_ERROR(node_->get_logger(),
                     "Servicio set_io no disponible");
        return false;
    }

    connected_ = true;

    RCLCPP_INFO(node_->get_logger(),
                "Conectado al servicio set_io");

    return true;
}

bool ToolIOClient::disconnect()
{
    connected_ = false;
    return true;
}

bool ToolIOClient::open()
{
    return pulseOutput(
        ur_msgs::srv::SetIO::Request::PIN_TOOL_DOUT0);
}

bool ToolIOClient::close()
{
    return pulseOutput(
        ur_msgs::srv::SetIO::Request::PIN_TOOL_DOUT1);
}

bool ToolIOClient::stop()
{
    return true;
}

bool ToolIOClient::setOutput(uint8_t pin, bool state)
{
    auto request =
        std::make_shared<ur_msgs::srv::SetIO::Request>();

    request->fun =
        ur_msgs::srv::SetIO::Request::FUN_SET_DIGITAL_OUT;

    request->pin = pin;

    request->state =
        state ?
        ur_msgs::srv::SetIO::Request::STATE_ON :
        ur_msgs::srv::SetIO::Request::STATE_OFF;

    RCLCPP_INFO(
        node_->get_logger(),
        "SetIO pin=%d state=%d",
        pin,
        state);

    auto future = io_client_->async_send_request(request);

    auto ret =
        rclcpp::spin_until_future_complete(
            node_->get_node_base_interface(),
            future,
            std::chrono::seconds(2));

    if (ret != rclcpp::FutureReturnCode::SUCCESS)
    {
        RCLCPP_ERROR(
            node_->get_logger(),
            "Timeout esperando respuesta");

        return false;
    }

    auto response = future.get();

    RCLCPP_INFO(
        node_->get_logger(),
        "Respuesta success=%d",
        response->success);

    return response->success;
}

bool ToolIOClient::pulseOutput(uint8_t pin)
{
    if (!connected_)
        return false;

    if (!setOutput(pin, true))
        return false;

    rclcpp::sleep_for(std::chrono::seconds(1));

    if (!setOutput(pin, false))
        return false;

    return true;
}