#!/bin/bash
source ~/.bashrc
workspace=$(pwd)
password=123456
# workdir=$(cd $(dirname $0); pwd)

# 1 生效can口
gnome-terminal -t "can" -- bash -c "$(pwd)/tools/can.sh"
# gnome-terminal -t "can" -x bash -c "source ~/.bashrc;source /opt/ros/noetic/setup.bash;echo $password | sudo -S slcand -o -f -s8 /dev/canable0 can0;sudo ifconfig can0 up;exec bash;"
# gnome-terminal -t "can" -x bash -c "source ~/.bashrc;source /opt/ros/noetic/setup.bash;echo $password | sudo -S slcand -o -f -s8 /dev/canable1 can1;sudo ifconfig can1 up;exec bash;"
# gnome-terminal -t "can" -x bash -c "source ~/.bashrc;source /opt/ros/noetic/setup.bash;echo $password | sudo -S slcand -o -f -s8 /dev/canable2 can2;sudo ifconfig can2 up;exec bash;"
# gnome-terminal -t "can" -x bash -c "source ~/.bashrc;source /opt/ros/noetic/setup.bash;echo $password | sudo -S slcand -o -f -s8 /dev/canable3 can3;sudo ifconfig can3 up;exec bash;"

sleep 3

# 2 启动roscore
gnome-terminal -t "roscore" -- bash -c "source ~/.bashrc;source /opt/ros/${ROS_DISTRO}/setup.bash;roscore;exec bash;"
sleep 1

# 3 启动相机
gnome-terminal -t "launcher" -- bash -c " roslaunch astra_camera multi_camera.launch;exec bash;"

# 4 启动臂
gnome-terminal -t "launcher" -- bash -c "source ~/.bashrc;conda deactivate;source /opt/ros/${ROS_DISTRO}/setup.bash;cd ${workspace}/follow1;source ${workspace}/follow1/devel/setup.bash;roslaunch arm_control arx5v.launch; exec bash;"
gnome-terminal -t "launcher" -- bash -c "source ~/.bashrc;conda deactivate;source /opt/ros/${ROS_DISTRO}/setup.bash;cd ${workspace}/follow2;source ${workspace}/follow2/devel/setup.bash;roslaunch arm_control arx5v.launch; exec bash;"

gnome-terminal -t "launcher" -- bash -c "source ~/.bashrc;conda deactivate;source /opt/ros/${ROS_DISTRO}/setup.bash;cd ${workspace}/master1;source ${workspace}/master1/devel/setup.bash;roslaunch arm_control arx5v.launch; exec bash;"
gnome-terminal -t "launcher" -- bash -c "source ~/.bashrc;conda deactivate;source /opt/ros/${ROS_DISTRO}/setup.bash;cd ${workspace}/master2;source ${workspace}/master2/devel/setup.bash;roslaunch arm_control arx5v.launch; exec bash;"