# 1 act模仿学习算法和共同训练用于移动的aloha

# 2 aloha远程操作 低成本远程操控学习双手移动操作

强化学习概念

1. "Episode"（回合）

+ 一个 episode 表示智能体从环境的初始状态开始，经过一系列动作和状态转换，直到达到某个终止条件为止的完整过程

2. "TimeStep"（时间步）
+ 一个时间步表示智能体与环境进行一次互动的基本单元，包括从环境接收观测、选择动作、执行动作、接收奖励和状态转换等。
+ 一个时间步通常包括当前观测、执行的动作、环境的奖励、下一个状态等信息。

+ 在一个 episode 中，可能包含多个时间步，因为一个 episode 会涉及到从初始状态到达终止条件的一系列时间步。时间步是描述这些过程中的每一个瞬间的概念

+ episode 是一个更大的单位，表示完整的任务执行过程，而时间步是构成这个过程的基本单位，描述智能体与环境的每一步互动。在实际的强化学习任务中，智能体通常会经历多个 episode，每个 episode 由多个时间步组成。

---

1. 利用Mobile ALOHA系统收集的数据，我们进行了有监督的行为克隆，并发现与现有静态 ALOHA 数据集进行联合训练可提高移动操作任务的性能。

底盘移动+全身控制+臂协调

+ 扩散模型和Transformer等表现力很强的策略类可以在细粒度

+ ALOHA 的 14-DoF 关节位置与移动底座的线速度和角速度连接起来，形成一个 16 维的动作向量

+ 进行预训练和协同训练的启发 注意到几乎没有可访问的双臂移动操作数据集

+ 而每项任务只需 50 次人类示范，与不进行联合训练相比，绝对成功率平均提高了 34%

# 1 制作数据集

# 1.1 TimeStep介绍

+ TimeStep表示强化学习中的时间步

~~~python
以下是一个一般化的 "TimeStep" 的概述：
    1. step_type： 表示时间步的类型。它通常有以下几种取值：
        FIRST：表示一个新的 episode 的开始。
        MID：表示 episode 中的中间步骤。
        LAST：表示 episode 中的最后一步。
        ONLY：当环境只有一个时间步时使用。
    
    2. observation： 表示环境在当前时间步的观测或状态。这通常是一个 NumPy 数组、字典或数组列表，包含了智能体在当前时刻感知到的环境信息。
    3. reward： 表示在当前时间步智能体获得的奖励。奖励是一个标量值，表示智能体执行某个动作后环境对其的反馈。
    3. discount： 表示折扣因子，用于计算未来奖励的折现值。通常是一个介于 0 到 1 之间的值。在某些情况下，可能为 None，表示没有折扣因子的概念。
~~~

## 1.2 aloha中好像(本人刚学)只用的2个状态 FIRST MID

~~~python
ts = env.reset(fake=True)  # FIRST 初始状态
ts = env.step(action)      # MID   根据动作 获取奖励 
~~~

1. **env.reset(fake=True)**

+ 重启从臂从爪->从臂从爪运动到初始状态->返回dm_env.StepType.FIRST
+ reward=0,discount=None
+ observation观察状态值后面介绍具体内容

~~~python
# fake=True
def reset(self, fake=False):
        if not fake:
            # Reboot puppet robot gripper motors 重启从臂和从爪
            self.puppet_bot_left.dxl.robot_reboot_motors("single", "gripper", True)
            self.puppet_bot_right.dxl.robot_reboot_motors("single", "gripper", True)
            
            self._reset_joints()
            self._reset_gripper()

        # DM-Env库中表示强化学习环境中时间步的类。通常包含有关特定时间步的环境状态的信息。
        return dm_env.TimeStep(
            step_type=dm_env.StepType.FIRST,
            reward=self.get_reward(),
            discount=None,
            observation=self.get_observation())
~~~

2. env.step(action)

+ 喂入主臂和主爪的action->通过该action操作从臂从爪->返回dm_env.StepType.MID

+ 这里调用step后，参数`action, base_action=None, get_tracer_vel=False, get_obs=True`
+ action是主臂和主爪的action
+ base_action=None, get_tracer_vel=False，也就是没有base_action不记录,tracer底盘速度也不记录
+ get_obs=True 只记录观察状态值, 具体值后面解释


+ 疑惑是这里返回的奖励还是0


~~~python
def step(self, action, base_action=None, get_tracer_vel=False, get_obs=True):
    state_len = int(len(action) / 2)
    
    left_action = action[:state_len]  # 取7维度
    right_action = action[state_len:]
    
    # 设置从臂的位置
    self.puppet_bot_left.arm.set_joint_positions(left_action[:6], blocking=False)
    # 设置从臂的位置
    self.puppet_bot_right.arm.set_joint_positions(right_action[:6], blocking=False)
    # 设置从爪的位置
    self.set_gripper_pose(left_action[-1], right_action[-1])
    
    # 基础状态 = None 
    if base_action is not None:
        base_action_linear, base_action_angular = base_action
        # tracer的速度
        self.tracer.SetMotionCommand(linear_vel=base_action_linear, angular_vel=base_action_angular)
    # time.sleep(DT)
    
    if get_obs:
        obs = self.get_observation(get_tracer_vel)
    else:
        obs = None

    return dm_env.TimeStep(
        step_type=dm_env.StepType.MID,
        reward=self.get_reward(),
        discount=None,
        observation=obs)


~~~

3. **get_observation**

+ (从臂从爪)qpos，qvel，effort   sensor_msgs/JointState
+ (高、低、左手腕、右手腕)images   没有就设为None
+ (车体线速度、角速度)base_vel     线速度、角速度
+ get_tracer_vel=False          该值没有记录因为已经有了base_vel

~~~python
#  get_observation状态值
def get_observation(self, get_tracer_vel=False):
    obs = collections.OrderedDict()
    obs['qpos'] = self.get_qpos()
    obs['qvel'] = self.get_qvel()
    obs['effort'] = self.get_effort()
    obs['images'] = self.get_images()
    # obs['base_vel_t265'] = self.get_base_vel_t265()
    obs['base_vel'] = self.get_base_vel()
    if get_tracer_vel:
        obs['tracer_vel'] = self.get_tracer_vel()
    return obs

# 函数解析
# 函数太多这里直接简化只写返回值， 注意各位数字的顺序就行
# 这里爪的gripper_qpos，gripper_qvel归一化后的值，具体方式参考get_qpos()，get_qvel()

# 1 从臂从爪的状态 sensor_msgs/JointState
## 1.1 位置
obs['qpos'] = np.concatenate([left_arm_qpos, left_gripper_qpos, right_arm_qpos, right_gripper_qpos])
## 1.2 速度
obs['qvel'] = np.concatenate([left_arm_qvel, left_gripper_qvel, right_arm_qvel, right_gripper_qvel])
## 1.3 扭矩
obs['effort'] = np.concatenate([left_robot_effort, right_robot_effort])

# 2 图像
obs['images']
def get_images(self):
    image_dict = dict()
    for cam_name in self.camera_names:
        image_dict[cam_name] = getattr(self, f'{cam_name}_image')
    return image_dict

# 3 base_vel 载体速度
obs['base_vel']    
def get_base_vel(self):
    left_vel, right_vel = self.dxl_client.read_pos_vel_cur()[1]
    # 轮子是对称安装的 
    right_vel = -right_vel # right wheel is inverted
    
    # 线速度： 左右轮速度相加 / 轮距的一半   # 具体还的看底盘样式 
    base_linear_vel = (left_vel + right_vel) * self.wheel_r / 2
    
    # 角速度 这个还没弄清楚 等会看实车^_^
    base_angular_vel = (right_vel - left_vel) * self.wheel_r / self.base_r
    
    return np.array([base_linear_vel, base_angular_vel])

# 4 tracer_vel 
obs['tracer_vel']
# 这里应该为了通用性考虑用了3-base_vel就不需要额外记录tracer车封装的ros车速消息
~~~