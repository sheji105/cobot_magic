# 1 环境配置

+ 使用cobot提供的iso镜像文件安装系统，该镜像已经完美适配cobot-magic工程，镜像[百度网盘下载地址]()
+ 原生ubuntu系统配置cobot-magic工程请[参考链接](https://github.com/agilexrobotics/cobot_magic/blob/main/readme.md)

1. 下载cobot-magic工程
~~~python
git clone https://github.com/agilexrobotics/cobot_magic.git
~~~

2. 编译
~~~python
# 1 编译示教模式机械臂驱动
## 1.1 进入cobot_magic/remote_control目录
cd cobot_magic/remote_control

## 1.2 编译
./tools/build.sh

# 2 编译推理模式机械臂驱动
## 2.1 进入cobot_magic/follow_control目录
cd cobot_magic/follow_control

## 2.2 编译
./tools/build.sh

# 3 编译相机驱动
## 3.1 进入cobot_magic/camera_ws目录
cd cobot_magic/camera_ws

## 3.2 编译
catkin_make

## 3.3 设置rule
source devel/setup.bash && rospack list
roscd astra_camera
./scripts/create_udev_rules
sudo udevadm control --reload && sudo  udevadm trigger

## 3.4 设置永久环境变量,
### 3.4.1 进入cobot_magic/camera_ws目录
cd cobot_magic/camera_ws

### 3.4.2 设置环境变量
echo "source $(pwd)/devel/setup.bash" >> ~/.bashrc 

## 3.5 编译注意事项
# 3.3与3.4只需要执行一次即可, 重新编译相机不需要执行这2步
~~~

# 2 绑定serial number

# 2.1 绑定相机的serial number

1. 绑定serial number
~~~python
# 1 进入相机工作空间目录
cd camera_ws

# 2 环境变量生效
source devel/setup.bash

# 3 打印相机序列号
./devel/lib/astra_camera/list_devices_node

# 4 修改multi_camera.launch配置文件
vim camera_ws/src/ros_astra_camera/launch/multi_camera.launch
## 修改camera_ws/src/ros_astra_camera/launch/multi_camera.launch第13左右相机的Serial number值
## 将1中输出的3个Serial number值，分别填入下面代码中即可
<arg name="camera1_serila_number" default="AU1231201GE"/>
<arg name="camera2_serila_number" default="AU1953304F2"/>
<arg name="camera3_serila_number" default="AU1P32201SA"/>
~~~

+ 一个相机单独连接usb线，查看该相机的Serial number, 然后再拔掉该usb线，同理操作下一个相机，便于区别相机id

2. 测试
~~~python
# 1 启动相机
roslaunch astra_camera multi_camera.launch

# 2 查看相机话题
rqt_image_view
## 能够分别查看到3个相机的图像话题即表示相机配置成功
~~~


## 2.2 查看机械臂的serial number

1. 绑定serial number

一个机械臂进行以下操作：
+ 机械臂上电
+ 机械臂usb插入工控机
+ 查看serial号
+ 操作完成后，拔掉该usb，另外一条臂重复上面步骤

~~~python
# 1 查看已连接的can2usb线
ls /dev/ttyACM*

# 显示如下： 插入一个can2usb线就显示一个，这里显示的插了4个can2usb的线
/dev/ttyACM0  /dev/ttyACM1  /dev/ttyACM2  /dev/ttyACM3

# 2 查看ttyACM0的serial号
# 这里可以查看上面ls /dev/ttyACM*所列出的设备号
udevadm info -a -n /dev/ttyACM0 | grep serial -m 1
# 显示如下：
# ATTRS{serial}=="2079389E4D4D"
# 2079389E4D4D即为serial号

# 3 修改arx_can.rules的serial number
vim remote_control/doc/arx_can.rules
## 将4个机械臂的的serial number依次更换, 顺序很重要
## canable0使用master_right臂的serial number
## canable1使用follow_right臂的serial number
## canable2使用master_left臂的serial number
## canable3使用follow_left臂的serial number

SUBSYSTEM=="tty", ATTRS{idVendor}=="16d0", ATTRS{idProduct}=="117e", ATTRS{serial}=="206438674D4D", SYMLINK+="canable0"
SUBSYSTEM=="tty", ATTRS{idVendor}=="16d0", ATTRS{idProduct}=="117e", ATTRS{serial}=="207938A14D4D", SYMLINK+="canable1"
SUBSYSTEM=="tty", ATTRS{idVendor}=="16d0", ATTRS{idProduct}=="117e", ATTRS{serial}=="207638884D4D", SYMLINK+="canable2"
SUBSYSTEM=="tty", ATTRS{idVendor}=="16d0", ATTRS{idProduct}=="117e", ATTRS{serial}=="208E386A4D4D", SYMLINK+="canable3"

# 4 拷贝arx_can.rules进/etc/udev/rules.d/
cp remote_control/doc/arx_can.rules /etc/udev/rules.d/

# 5 更新rule
sudo udevadm control --reload-rules && sudo udevadm trigger
~~~

+ 注意第3步，更换arx_can.rules的serial number顺序

2. 测试机械臂

+ 完成绑定serial number后，连接上4条臂的can2usb线，进行如下操作测试机械臂是否正常工作

~~~python
# 1 进入remote_control
cd remote_control

# 2 can生效
## 启动改文件前需要修改./tools/can.sh中password参数, 改成自己主机密码即可
./tools/can.sh
## 每个终端不报错即can生效

# 3 测试master1
## 3.1 进入master1
cd master1
## 3.2 ros空间生效
source devel/setup.bash
## 3.3 启动机器臂
roslaunch arm_control arx5v.launch
## 3.4 启动后, 直接键盘上，按上下左右键，机械臂能相应运动, 即表示master1臂配置成功
## 3.5 依次按3步骤操作master2,follow1,follow2，对应机械臂能正常运动即该臂配置成功
~~~


# 3 采集数据

1. 启动机械臂与相机
~~~python
# 1 启动roscore
roscore

# 2 启动机器臂与相机
## 2.1 进入remote_control目录
cd remote_control

## 2.2 启动机器臂与相机的驱动脚本
./tools/start.sh

# 3 采集数据
## 3.1 进入collect_data目录
cd collect_data

## 3.2 激活虚拟环境
conda activate aloha

## 3.3 收集数据
python collect_data.py --max_timesteps 500 --dataset_dir ./data --episode_idx 0

## 3.4 可视化
python visualize_episodes.py --dataset_dir ./data --task_name aloha_mobile_dummy --episode_idx 0

## 3.5 播放数据集
python replay_data.py --dataset_dir ./data --task_name aloha_mobile_dummy --episode_idx 0
~~~

# 4 训练

~~~python
# 1 进入aloha-devel目录
cd aloha-devel

# 2 激活虚拟环境
conda activate aloha

# 3 启动训练代码
python act/train.py --dataset /media/lin/T7/data0314/ --ckpt_dir ~/train0314/ --batch_size 48 --num_epochs 3000
~~~

# 5 推理

~~~python
# 1 启动roscore
roscore

# 2 启动从臂与相机
## 2.1 进入follow_control目录
cd follow_control

## 2.2 启动从臂与相机驱动脚本
./tools/start.sh

# 3 推理
## 3.1 进入aloha-devel目录
cd aloha-devel

## 3.2 激活虚拟环境
conda activate aloha
a
## 3.3 进行推理
python act/inference.py --ckpt_dir ~/train0314/
~~~
