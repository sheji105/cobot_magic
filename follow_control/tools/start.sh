#!/bin/bash
source ~/.bashrc
workspace=$(pwd)
password=password=123456
# workdir=$(cd $(dirname $0); pwd)


# 1 机器臂绑定can
gnome-terminal -t "can" -- bash -c "$(pwd)/tools/can.sh"

# 1 启动roscore
gnome-terminal -t "roscore" -- bash -c "source ~/.bashrc;source /opt/ros/${ROS_DISTRO}/setup.bash;roscore;exec bash;"
sleep 1

# 2 启动相机
gnome-terminal -t "launcher" -- bash -c " roslaunch astra_camera multi_camera.launch;exec bash;"
sleep 2

# 3 启动臂
gnome-terminal -t "launcher" -- bash -c "source ~/.bashrc;source /opt/ros/${ROS_DISTRO}/setup.bash;cd ${workspace}/follow1;source ${workspace}/follow1/devel/setup.bash;roslaunch arm_control arx5.launch; exec bash;"
gnome-terminal -t "launcher" -- bash -c "source ~/.bashrc;source /opt/ros/${ROS_DISTRO}/setup.bash;cd ${workspace}/follow2;source ${workspace}/follow2/devel/setup.bash;roslaunch arm_control arx5.launch; exec bash;"




