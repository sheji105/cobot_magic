# 1 环境配置

+ 使用cobot提供的iso镜像文件安装系统，该镜像已经完美适配cobot-magic工程，镜像[百度网盘下载地址]()


1. 下载cobot-magic工程
~~~python
git clone https://github.com/agilexrobotics/cobot_magic.git
~~~

2. 编译
~~~python
cd cobot_magic/remote_control
./tools/build.sh

cd cobot_magic/camera_ws
catkin_make
~~~


2. 测试机械臂

~~~python
cd remote_control
./tools/can.sh

cd master1

source devel/setup.bash

roslaunch arm_control arx5v.launch
~~~


# 3 采集数据

~~~python
# 1 启动roscore
roscore

# 2 启动机器臂与相机
./tools/start.sh

## 3 采集数据
python collect_data.py --max_timesteps 500 --dataset_dir ./data --episode_idx 0
~~~

# 4 模型训练推理

~~~python
# 1 激活虚拟环境
conda activate aloha

# 2 训练
python act/train.py --dataset /media/lin/T7/data0314/ --ckpt_dir ~/train0314/ --batch_size 48 --num_epochs 3000

# 3 推理
python act/inference.py --ckpt_dir ~/train0314/
~~~


