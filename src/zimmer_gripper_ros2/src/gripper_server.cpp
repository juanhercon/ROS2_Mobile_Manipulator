#include "zimmer_gripper_ros2/gripper_server.hpp"

using std::placeholders::_1;
using std::placeholders::_2;

GripperServer::GripperServer()
: Node("gripper_server"),
interface_(this)
{
    if (!interface_.connect())
    {
        RCLCPP_FATAL(get_logger(), "No se pudo conectar con la pinza.");
        throw std::runtime_error("Error conectando con la pinza");
    }

    service_ = create_service<zimmer_gripper_ros2::srv::GripperCommand>(
        "gripper_command",
        std::bind(&GripperServer::callback, this, _1, _2));

    RCLCPP_INFO(get_logger(), "Servidor iniciado");
}

void GripperServer::callback(
    const std::shared_ptr<
        zimmer_gripper_ros2::srv::GripperCommand::Request> request,
    std::shared_ptr<
        zimmer_gripper_ros2::srv::GripperCommand::Response> response)
{
    bool ok = false;

    RCLCPP_INFO(
    get_logger(),
    "Comando recibido: %d",
    request->command);

    switch (request->command)
    {
        case 0:
            ok = interface_.open();
            break;

        case 1:
            ok = interface_.close();
            break;

        case 2:
            ok = interface_.stop();
            break;

        default:
            ok = false;
            break;
    }

    response->success = ok;

    if (ok)
        response->message = "Comando ejecutado correctamente";
    else
        response->message = "Comando no válido o error";
}