#!/bin/bash
source ~/.bashrc
password=agx

gnome-terminal -t "can" -x bash -c "source ~/.bashrc;source /opt/ros/noetic/setup.bash;echo $password | sudo -S slcand -o -f -s8 /dev/canable0 can0;sudo ifconfig can0 up;exec bash;"
gnome-terminal -t "can" -x bash -c "source ~/.bashrc;source /opt/ros/noetic/setup.bash;echo $password | sudo -S slcand -o -f -s8 /dev/canable0 can0;sudo ifconfig can0 up;exec bash;"
gnome-terminal -t "can" -x bash -c "source ~/.bashrc;source /opt/ros/noetic/setup.bash;echo $password | sudo -S slcand -o -f -s8 /dev/canable0 can0;sudo ifconfig can0 up;exec bash;"

gnome-terminal -t "can" -x bash -c "source ~/.bashrc;source /opt/ros/noetic/setup.bash;echo $password | sudo -S slcand -o -f -s8 /dev/canable1 can1;sudo ifconfig can1 up;exec bash;"
gnome-terminal -t "can" -x bash -c "source ~/.bashrc;source /opt/ros/noetic/setup.bash;echo $password | sudo -S slcand -o -f -s8 /dev/canable1 can1;sudo ifconfig can1 up;exec bash;"
gnome-terminal -t "can" -x bash -c "source ~/.bashrc;source /opt/ros/noetic/setup.bash;echo $password | sudo -S slcand -o -f -s8 /dev/canable1 can1;sudo ifconfig can1 up;exec bash;"

gnome-terminal -t "can" -x bash -c "source ~/.bashrc;source /opt/ros/noetic/setup.bash;echo $password | sudo -S slcand -o -f -s8 /dev/canable2 can2;sudo ifconfig can2 up;exec bash;"
gnome-terminal -t "can" -x bash -c "source ~/.bashrc;source /opt/ros/noetic/setup.bash;echo $password | sudo -S slcand -o -f -s8 /dev/canable2 can2;sudo ifconfig can2 up;exec bash;"
gnome-terminal -t "can" -x bash -c "source ~/.bashrc;source /opt/ros/noetic/setup.bash;echo $password | sudo -S slcand -o -f -s8 /dev/canable2 can2;sudo ifconfig can2 up;exec bash;"

gnome-terminal -t "can" -x bash -c "source ~/.bashrc;source /opt/ros/noetic/setup.bash;echo $password | sudo -S slcand -o -f -s8 /dev/canable3 can3;sudo ifconfig can3 up;exec bash;"
gnome-terminal -t "can" -x bash -c "source ~/.bashrc;source /opt/ros/noetic/setup.bash;echo $password | sudo -S slcand -o -f -s8 /dev/canable3 can3;sudo ifconfig can3 up;exec bash;"
gnome-terminal -t "can" -x bash -c "source ~/.bashrc;source /opt/ros/noetic/setup.bash;echo $password | sudo -S slcand -o -f -s8 /dev/canable3 can3;sudo ifconfig can3 up;exec bash;"






