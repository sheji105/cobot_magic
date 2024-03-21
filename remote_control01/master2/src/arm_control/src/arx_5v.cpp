#include <ros/ros.h>
#include <cmath>
#include <iostream>
#include <std_msgs/Float32MultiArray.h>
#include "utility.h"
#include "Hardware/can.h"
#include "Hardware/motor.h"
#include "Hardware/teleop.h"
#include "App/arm_control.h"
#include "App/arm_control.cpp"
#include "App/keyboard.h"
#include "App/play.h"
#include "App/solve.h"
#include <termios.h>
#include <unistd.h>
#include <fcntl.h>
#include <thread>
#include <atomic>
#include "App/arx_s.h"
#include "arm_control/JointControl.h"
#include "arm_control/JointInformation.h"
#include "arm_control/PosCmd.h"

int CONTROL_MODE=0; // 0 arx5 rc ，1 5a rc ，2 arx5 ros ，3 5a ros
command cmd;
can CAN_Handlej;

int main(int argc, char **argv)
{
    ros::init(argc, argv, "arm3"); 
    ros::NodeHandle node;
    Teleop_Use()->teleop_init(node);

    arx_arm ARX_ARM((int) CONTROL_MODE);

    ros::Publisher pub_joint01 = node.advertise<sensor_msgs::JointState>("/master/joint_left", 10);

    ros::Subscriber sub_information = node.subscribe<arm_control::JointInformation>("/joint_information2", 10, 
                                  [&ARX_ARM](const arm_control::JointInformation::ConstPtr& msg) {
                                      ARX_ARM.ros_control_cur_t[0] = msg->joint_cur[0];
                                      ARX_ARM.ros_control_cur_t[1] = msg->joint_cur[1];
                                      ARX_ARM.ros_control_cur_t[2] = msg->joint_cur[2];
                                      ARX_ARM.ros_control_cur_t[3] = msg->joint_cur[3];
                                      ARX_ARM.ros_control_cur_t[4] = msg->joint_cur[4];
                                      ARX_ARM.ros_control_cur_t[5] = msg->joint_cur[5];
                                      ARX_ARM.ros_control_cur_t[6] = msg->joint_cur[6];
                                      ARX_ARM.ros_control_pos_t[6] = msg->joint_pos[6];
                                  });
    ros::Publisher pub_joint = node.advertise<arm_control::JointControl>("/joint_control2", 10);
    ros::Publisher pub_pos = node.advertise<arm_control::PosCmd>("/master2_pos_back", 10);
    
    arx5_keyboard ARX_KEYBOARD;

    ros::Rate loop_rate(200);

    std::thread keyThread(&arx5_keyboard::detectKeyPress, &ARX_KEYBOARD);
    sleep(1);

    while(ros::ok())
    { 

        ROS_INFO("master 2>>>>>>>>>>>>>>>>>>>>>");
//程序主逻辑
        char key = ARX_KEYBOARD.keyPress.load();
        ARX_ARM.getKey(key);

        ARX_ARM.get_curr_pos();
        if(!ARX_ARM.is_starting){
             cmd = ARX_ARM.get_cmd();
        }
        ARX_ARM.update_real(cmd);
    
//自定义话题
            //发布关节信息
            arm_control::JointControl msg_joint;            

            for(int i=0;i<6;i++)
            {
                msg_joint.joint_pos[i] = ARX_ARM.current_pos[i];
                msg_joint.joint_vel[i] = ARX_ARM.current_vel[i];
                msg_joint.joint_cur[i] = ARX_ARM.current_torque[i];
            }  

                msg_joint.joint_vel[6] = ARX_ARM.current_vel[6];
                msg_joint.joint_cur[6] = ARX_ARM.current_torque[6];
                //ARX_ARM.current_pos[6]=ARX_ARM.Data_process(ARX_ARM.current_pos[6]);
                msg_joint.joint_pos[6]=ARX_ARM.current_pos[6]*12; // 映射放大
                msg_joint.mode = ARX_ARM.arx5_cmd.key_t;
            
            pub_joint.publish(msg_joint);

            //发布末端位置
            arm_control::PosCmd msg_pos_back;            
            msg_pos_back.x      =ARX_ARM.solve.solve_pos[0];
            msg_pos_back.y      =ARX_ARM.solve.solve_pos[1];
            msg_pos_back.z      =ARX_ARM.solve.solve_pos[2];
            msg_pos_back.roll   =ARX_ARM.solve.solve_pos[3];
            msg_pos_back.pitch  =ARX_ARM.solve.solve_pos[4];
            msg_pos_back.yaw    =ARX_ARM.solve.solve_pos[5];
            msg_pos_back.gripper=ARX_ARM.current_pos[6];

            pub_pos.publish(msg_pos_back);
        
        // 发布姿态
            sensor_msgs::JointState msg_joint01;
            msg_joint01.header.stamp = ros::Time::now();
            // msg_joint01.header.frame_id = "map";
            size_t num_joint = 7;
            msg_joint01.name.resize(num_joint);
            msg_joint01.velocity.resize(num_joint);
            msg_joint01.position.resize(num_joint);
            msg_joint01.effort.resize(num_joint);
            
            for (size_t i=0; i < 7; ++i)
            {   
                msg_joint01.name[i] = "joint" + std::to_string(i);
                msg_joint01.position[i] = ARX_ARM.current_pos[i];
                msg_joint01.velocity[i] = ARX_ARM.current_vel[i];
                msg_joint01.effort[i] = ARX_ARM.current_torque[i];
                if (i == 6) msg_joint01.position[i] *=9;
            }
            pub_joint01.publish(msg_joint01);


        ros::spinOnce();
        loop_rate.sleep();
   
        if (arx_flag)
        {
            break;
        }

    }
    arx_2(CAN_Handlej);
    return 0;
}