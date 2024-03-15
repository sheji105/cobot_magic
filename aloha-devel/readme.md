
# Mobile ALOHA

A Low-cost Open-source Hardware System for Bimanual Teleoperation

详情请参考[mobile-aloha](https://github.com/MarkFzp/mobile-aloha) 、[act-plus-plus](https://github.com/MarkFzp/act-plus-plus)


# 1 环境配置

+ ubuntu-20.04,cuda-11.8,cudnn-8.6.0,torch-2.1.1已测试通过

~~~python
# 1 torch安装
pip install torch==2.1.1 torchvision==0.16.1 torchaudio==2.1.1 --index-url https://download.pytorch.org/whl/cu118

# 2 requrements.txt安装
pip install -r requrements.txt

# 3 安装detr
cd act/detr && pip install -v -e .
~~~

详情请参考[mobile-aloha](https://github.com/MarkFzp/mobile-aloha) 、[act-plus-plus](https://github.com/MarkFzp/act-plus-plus)


# 2 采集数据集



+ 详细参考collect_data工程

# 3 训练

~~~python
python act/train.py --dataset /media/lin/T7/data0314/ --ckpt_dir train_dir --batch_size 48 --num_epochs 2000
~~~

1. 主要参数参数说明 目前仅支持ACT模型训练
    + --dataset     数据集目录
    + --ckpt_dir    训练模型保存目录
    + --batch_size  训练批量大小
    + --num_epochs  训练周期
    + --task_name   任务名称
    + --pretrain_ckpt_dir 预训练模型路径
    + --ckpt_name   模型名称


# 4 推理
~~~python
# 1 启动roscore
roscore

# 2 启动从臂与相机


# 3 推理
python inference.py --ckpt_dir train_dir
~~~
