#!/bin/bash
source ~/.bashrc
workspace=$(pwd)
password=agx
# workdir=$(cd $(dirname $0); pwd)




# 2 启动roscore
gnome-terminal -t "roscore" -- bash -c "source ~/.bashrc;source /opt/ros/${ROS_DISTRO}/setup.bash;roscore;exec bash;"
sleep 1

# 3 启动相机
gnome-terminal -t "launcher" -- bash -c " roslaunch astra_camera multi_camera.launch;exec bash;"

# 4 启动臂
gnome-terminal -t "launcher" -- bash -c "source ~/.bashrc;source /opt/ros/${ROS_DISTRO}/setup.bash;cd ${workspace}/follow1;source ${workspace}/follow1/devel/setup.bash;roslaunch arm_control arx5v.launch; exec bash;"
gnome-terminal -t "launcher" -- bash -c "source ~/.bashrc;source /opt/ros/${ROS_DISTRO}/setup.bash;cd ${workspace}/follow2;source ${workspace}/follow2/devel/setup.bash;roslaunch arm_control arx5v.launch; exec bash;"