cmake_minimum_required(VERSION 3.8)
project(zimmer_gripper_ros2)

if(CMAKE_COMPILER_IS_GNUCXX OR CMAKE_CXX_COMPILER_ID MATCHES "Clang")
  add_compile_options(-Wall -Wextra -Wpedantic)
endif()

# find dependencies
find_package(ament_cmake REQUIRED)
find_package(rclcpp REQUIRED)
find_package(std_msgs REQUIRED)
find_package(std_srvs REQUIRED)
find_package(rosidl_default_generators REQUIRED)
find_package(ur_msgs REQUIRED)

add_executable(gripper_server
    src/main.cpp
    src/gripper_server.cpp
    src/gripper_interface.cpp
    src/tool_io_client.cpp
)

target_include_directories(gripper_server PUBLIC
  $<BUILD_INTERFACE:${CMAKE_CURRENT_SOURCE_DIR}/include>
  $<INSTALL_INTERFACE:include>
)

ament_target_dependencies(gripper_server
  rclcpp
  std_msgs
  std_srvs
  ur_msgs
)

add_dependencies(gripper_server
  ${PROJECT_NAME}__rosidl_generator_cpp
)

rosidl_generate_interfaces(${PROJECT_NAME}
  "srv/GripperCommand.srv"
)

rosidl_get_typesupport_target(cpp_typesupport_target
  ${PROJECT_NAME}
  "rosidl_typesupport_cpp"
)

target_link_libraries(gripper_server
  ${cpp_typesupport_target}
)

# Instalar el ejecutable
install(TARGETS
  gripper_server
  DESTINATION lib/${PROJECT_NAME}
)

if(BUILD_TESTING)
  find_package(ament_lint_auto REQUIRED)
  # the following line skips the linter which checks for copyrights
  # comment the line when a copyright and license is added to all source files
  set(ament_cmake_copyright_FOUND TRUE)
  # the following line skips cpplint (only works in a git repo)
  # comment the line when this package is in a git repo and when
  # a copyright and license is added to all source files
  set(ament_cmake_cpplint_FOUND TRUE)
  ament_lint_auto_find_test_dependencies()
endif()

ament_export_dependencies(rosidl_default_runtime)

install(
  DIRECTORY include/
  DESTINATION include
)

ament_package()
