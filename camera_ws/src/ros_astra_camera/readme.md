
# 1 ros_astra_camera配置

[ros_astra_camera-github地址](https://github.com/orbbec/ros_astra_camera)

---
+ **相机参数**


|||
| :------- | -------------------------------------------- |
| Baseline | 40mm                                         |
| 深度距离     | 0.3-3m                                       |
| 深度图分辨率   | 640x400x30fps、320x200x30fps                  |
| 彩色图分辨率   | 1920x1080x30fps、1280x720x30fps、640x480x30fps |
| 精度       | 6mm@1m (81%FOV区域参与精度计算)                      |
| 深度FOV    | H 67.9° V 45.3°                              |
| 彩色FOV    | H 71° V 43.7° @ 1920x1080                    |
| 延迟       | 30-45ms                                      |
| 数据传输     | USB2.0或以上                                    |
| 工作温度     | 10°C~40°C                                    |
| 尺寸       | 长59.5x宽17.4x厚11.1 mm                         |


---

# 1 OrbbecSDK_ROS1驱动安装

~~~python
# 1 安装依赖
sudo apt install libgflags-dev  ros-$ROS_DISTRO-image-geometry ros-$ROS_DISTRO-camera-info-manager ros-$ROS_DISTRO-image-transport ros-$ROS_DISTRO-image-publisher ros-$ROS_DISTRO-libuvc-ros libgoogle-glog-dev libusb-1.0-0-dev libeigen3-dev 

# 2 下载源码
## 2.1 github下载
git clone https://github.com/orbbec/ros_astra_camera.git astra_ws/src/ros_astra_camera

## 2.2 gitee下载地址 中国区请使用gitee
git clone https://gitee.com/hylin123/ros_astra_camera.git astra_ws/src/ros_astra_camera

# 3 编译orbbec_camera
## 3.1 进入astra_ws工作空间
cd astra_ws
## 3.2 编译orbbec_camera
catkin_make

# 4 Install udev rules.
source devel/setup.bash && rospack list
roscd astra_camera
./scripts/create_udev_rules
sudo udevadm control --reload && sudo  udevadm trigger

# 5 增加ros_astra_camera包的环境变量
## 5.1 进入astra_ws目录
cd astra_ws
## 5.2 增加环境变量
echo "source $(pwd)/devel/setup.bash" >> ~/.bashrc 
## 5.3 环境变量生效

# 6 启动
## 如果没有执行第5步,每次启动时都需要执行6.2的代码使ros工作空间环境生效
## 6.1 astra_ws工作空间
cd astra_ws
## 6.2 工作空间环境生效
source devel/setup.bash
## 6.3 启动astra.launch
roslaunch astra_camera astra.launch
## 6.4 启动dabai.launch
roslaunch astra_camera dabai.launch
~~~


# 2 配置orbbec_camera多相机节点

1. 查看设备号
+ 插上相机后, 运行下面代码

~~~python
rosrun astra_camera list_devices_node
~~~

+ 终端输出显示：
~~~python
[ INFO] [1709807731.111663202]: Found 1 devices
Device connected: Astra
URI: 2bc5/060e@1/9
Serial number: AU1L12100AZ # 记住这个Serial number号, 每个相机对应一个唯一Serial number
~~~

2. 配置多相机节点

+ cobot_magic采用3个astra_camera的dabai相机, 因此需要根据每个相机的Serial number配置对应的相机
+ 工控机PC插上3个相机的usb数据线，并运行`1. 查看设备号小节中`的代码，可以查看3个相机的Serial number
+ 为后续开发中，分清每个相机对应的话题，请按顺序填入Serial number
+ 在`astra_ws/src/launch`目录下创建`multi_camera.launch`文件，内容如下：

~~~python
# 主要修改1 相机名称前缀、2 Serial number即可
<launch>
    <arg name="camera_name" default="camera"/>
    <arg name="3d_sensor" default="dabai"/>
    
     <!-- 1 相机名称前缀 -->
    <arg name="camera1_prefix" default="01"/>
    <arg name="camera2_prefix" default="02"/>
    <arg name="camera3_prefix" default="03"/>
    
    <!-- # 2 Serial number 填入相机的Serial number -->
    <arg name="camera1_usb_port" default="相机1的serial number"/>
    <arg name="camera2_usb_port" default="相机2的serial number"/>
    <arg name="camera3_usb_port" default="相机3的serial number"/>

    <arg name="device_num" default="3"/>
    <include file="$(find orbbec_camera)/launch/$(arg 3d_sensor).launch">
        <arg name="camera_name" value="$(arg camera_name)_$(arg camera1_prefix)"/>
        <arg name="usb_port" value="$(arg camera1_usb_port)"/>
        <arg name="device_num" value="$(arg device_num)"/>
    </include>

    <include file="$(find orbbec_camera)/launch/$(arg 3d_sensor).launch">
        <arg name="camera_name" value="$(arg camera_name)_$(arg camera2_prefix)"/>
        <arg name="usb_port" value="$(arg camera2_usb_port)"/>
        <arg name="device_num" value="$(arg device_num)"/>
    </include>
    
    <include file="$(find orbbec_camera)/launch/$(arg 3d_sensor).launch">
        <arg name="camera_name" value="$(arg camera_name)_$(arg camera3_prefix)"/>
        <arg name="usb_port" value="$(arg camera3_usb_port)"/>
        <arg name="device_num" value="$(arg device_num)"/>
    </include>
</launch>
~~~

+ 添加权限
~~~python
# 1 进入astra_camera/launch/目录
roscd astra/launch/

# 2 multi_camera.launch添加权限
chmod +x multi_camera.launch
~~~

+ 启动ros
~~~python
roslaunch astra multi_camera.launch
~~~