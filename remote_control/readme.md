# rule 安装依赖
1. 安装依赖
~~~python
sudo apt install can-utils net-tools libkdl-parser-dev -y
~~~


2. 查看机械臂的serial号

机械臂按顺序依次进行以下操作：
+ 机械臂上电
+ 机械臂usb插入工控机
+ 查看serial号
~~~python
# 1 查看已连接的can线
ls /dev/ttyACM*
# 显示如下：
/dev/ttyACM0  /dev/ttyACM1  /dev/ttyACM2  /dev/ttyACM3

# 2 查看ttyACM0的serial号
# 这里可以查看上面ls /dev/ttyACM*所列出的设备号
udevadm info -a -n /dev/ttyACM0 | grep serial -m 1
# 显示如下：
# ATTRS{serial}=="2079389E4D4D"
# 2079389E4D4D即为serial号
~~~

+ 拔掉usb, 换下一条臂继续上面操作, 记录下每条臂的serial号


3. 构建规则


新建arx_can.rules文件，内容如下

+ 需要修改serial号内容
~~~python
# ATTRS{serial}=="自己对应的串口号内容"
SUBSYSTEM=="tty", ATTRS{idVendor}=="16d0", ATTRS{idProduct}=="117e", ATTRS{serial}=="207D38544D4D", SYMLINK+="canable0"
SUBSYSTEM=="tty", ATTRS{idVendor}=="16d0", ATTRS{idProduct}=="117e", ATTRS{serial}=="207938A14D4D", SYMLINK+="canable1"
SUBSYSTEM=="tty", ATTRS{idVendor}=="16d0", ATTRS{idProduct}=="117e", ATTRS{serial}=="2068385D4D4D", SYMLINK+="canable2"
SUBSYSTEM=="tty", ATTRS{idVendor}=="16d0", ATTRS{idProduct}=="117e", ATTRS{serial}=="208E386A4D4D", SYMLINK+="canable3"
~~~

4. 更新rule
~~~python
# 1 添加权限
chmod +x arx_can.rules

# 2 将arx_can.rules拷贝到/etc/udev/rules.d/目录下
sudo cp arx_can.rules /etc/udev/rules.d/

# 3 更新rule
sudo udevadm control --reload-rules && sudo udevadm trigger
~~~


# 2 绑定机械臂can口

1. 绑定can口
开机上电, 电脑插上机械臂的can转usb口接线

2. 新建can.sh文件，can.sh内容如下
+ 需要将password设置成本机的密码
~~~python
#!/bin/bash
source ~/.bashrc
password=1

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


gnome-terminal -t "can" -x bash -c "source ~/.bashrc;source /opt/ros/noetic/setup.bash;echo $password | sudo -S slcand -o -f -s8 /dev/canable6 can6;sudo ifconfig can6 up;exec bash;"
gnome-terminal -t "can" -x bash -c "source ~/.bashrc;source /opt/ros/noetic/setup.bash;echo $password | sudo -S slcand -o -f -s8 /dev/canable6 can6;sudo ifconfig can6 up;exec bash;"
gnome-terminal -t "can" -x bash -c "source ~/.bashrc;source /opt/ros/noetic/setup.bash;echo $password | sudo -S slcand -o -f -s8 /dev/canable6 can6;sudo ifconfig can6 up;exec bash;"
~~~

+ can.sh文件加权限
~~~python
chmod +x can.sh
~~~



3. 执行can.sh

~~~python
./can.sh
~~~

+ 执行后参考can口是否生效

~~~python
ifconfig | grep can
# 显示内容如下即can口, 即可以正常启动机械臂：
can0: flags=193<UP,RUNNING,NOARP>  mtu 16
can1: flags=193<UP,RUNNING,NOARP>  mtu 16
can2: flags=193<UP,RUNNING,NOARP>  mtu 16
can3: flags=193<UP,RUNNING,NOARP>  mtu 16
~~~

# 3 下载编译机械臂驱动

~~~python
# 3 进入remote_control目录
cd remote_control

# 4 编译
./tools/build.sh
~~~

# 4 启动机械臂

1. 拔掉电脑端can2usb接线，重新上电机械臂，再将can2usb接到电脑的usb口即可, 注意顺序

2. 绑定can
+ 运行第2小节的can.sh文件即可
~~~python
./can.sh
~~~

3. 启动机械臂
~~~python
# 1 进入remote_control目录
cd remote_control

# 2 启动机械臂
# 需要修改start.sh文件的password参数，改成本机的密码即可
./tools/start.sh
~~~

+ 如果拔掉can2usb线、断开机械臂电源、电脑重启,都需要重新运行上面的步骤
