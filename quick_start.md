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

# 2 采集数据

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

# 3 训练

~~~python
# 1 进入aloha-devel目录
cd aloha-devel

# 2 激活虚拟环境
conda activate aloha

# 3 启动训练代码
python act/train.py --dataset /media/lin/T7/data0314/ --ckpt_dir ~/train0314/ --batch_size 48 --num_epochs 3000
~~~

# 4 推理

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
