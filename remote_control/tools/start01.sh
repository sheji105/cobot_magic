#!/bin/bash
source ~/.bashrc
# workspace=${HOME}/follow
workspace=$(pwd)
password=123456
# current_path=$(pwd) 
# echo $current_path
# workdir=$(cd $(dirname $0); pwd)


# # 1 启动roscore
gnome-terminal -t "roscore" -- bash -c "source ~/.bashrc;source /opt/ros/${ROS_DISTRO}/setup.bash;roscore;exec bash;"
# sleep 1

# # 2 ip配置 can口
# gnome-terminal -t "can" -- bash -c "source ~/.bashrc; source /opt/ros/${ROS_DISTRO}/setup.bash; echo ${password} | sudo -S ${workspace}/setup_can.sh; candump can0; exec bash;"

# # 3 启动臂

#gnome-terminal -t "launcher" -- bash -c "source ~/.bashrc;source /opt/ros/${ROS_DISTRO}/setup.bash;cd ${workspace}/master1;source ${workspace}/master1/devel/setup.bash;roslaunch arm_control arx5v.launch; exec bash;"
gnome-terminal -t "launcher" -- bash -c "source ~/.bashrc;source /opt/ros/${ROS_DISTRO}/setup.bash;cd ${workspace}/follow1;source ${workspace}/follow1/devel/setup.bash;roslaunch arm_control arx5v.launch; exec bash;"
#gnome-terminal -t "launcher" -- bash -c "source ~/.bashrc;source /opt/ros/${ROS_DISTRO}/setup.bash;cd ${workspace}/master2;source ${workspace}/master2/devel/setup.bash;roslaunch arm_control arx5v.launch; exec bash;"
gnome-terminal -t "launcher" -- bash -c "source ~/.bashrc;source /opt/ros/${ROS_DISTRO}/setup.bash;cd ${workspace}/follow2;source ${workspace}/follow2/devel/setup.bash;roslaunch arm_control arx5v.launch; exec bash;"

# # gnome-terminal -t "launcher" -- bash -c "roslaunch realsense2_camera rs_multiple_devices.launch;exec bash;"


