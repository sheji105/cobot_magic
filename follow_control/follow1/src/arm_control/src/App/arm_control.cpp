#include "App/arm_control.h"


extern OD_Motor_Msg rv_motor_msg[10];

extern float magic_pos[3];
extern float magic_angle[3];
extern int magic_switch[2];

float arx_arm::joystick_projection(float joy_axis)

{
    float cmd = 0.0f;
    if(abs(joy_axis) >= JOYSTICK_DEADZONE)
    {
        cmd = (joy_axis - JOYSTICK_DEADZONE) / (1.0 - JOYSTICK_DEADZONE);
    }
    return cmd;
}

float arx_arm::ramp(float goal, float current, float ramp_k)
{
    float retval = 0.0f;
    float delta = 0.0f;
    delta = goal - current;
    if (delta > 0)
    {
        if (delta > ramp_k)
        {  
                current += ramp_k;
        }   
        else
        {
                current += delta;
        }
    }
    else
    {
        if (delta < -ramp_k)
        {
                current += -ramp_k;
        }
        else
        {
                current += delta;
        }
    }	
    retval = current;
    return retval;
}

arx_arm::arx_arm(int CONTROL_MODE)
{


    // is_real = real_flg;
    control_mode=CONTROL_MODE;

    arx5_cmd.reset = false;
    arx5_cmd.x = 0.0;
    arx5_cmd.y = 0.0;
    arx5_cmd.z = 0.01; // if 0.0 is also ok but isaac sim joint 3 direction will be confused
    arx5_cmd.base_yaw = 0;
    arx5_cmd.gripper = 0;
    arx5_cmd.waist_roll = 0;
    arx5_cmd.waist_pitch = 0;
    arx5_cmd.waist_yaw = 0;
    arx5_cmd.mode = FORWARD;

    // Read robot model from urdf model
    if(control_mode == 0 ||  control_mode == 2 || control_mode ==4){
        model_path = ros::package::getPath("arm_control") + "/models/ultron_v1.1_aa.urdf"; 
    }else if(control_mode == 1 ||  control_mode == 3 || control_mode ==5) {
        model_path = ros::package::getPath("arm_control") + "/models/arx5h.urdf";
    }
    
    if (play.modifyLinkMass(model_path, model_path, 0.581)) { //默认单位kg 夹爪质量 0.381 0.581
        std::cout << "Successfully modified the mass of link6." << std::endl;
    } else {
        std::cout << "Failed to modify the mass of link6." << std::endl;
    }    
    
    solve.solve_init(model_path);

    if(control_mode == 0 || control_mode == 2 || control_mode==4){
        CAN_Handlej.Send_moto_Cmd1(1, 0, 0, 0, 0, 0);        
    }else{CAN_Handlej.Enable_Moto(0x01); }
    usleep(1000);
    CAN_Handlej.Send_moto_Cmd1(2, 0, 0, 0, 0, 0);
    usleep(1000);
    CAN_Handlej.Send_moto_Cmd1(4, 0, 0, 0, 0, 0);
    usleep(1000);
    CAN_Handlej.Enable_Moto(0x05);
    usleep(1000);
    CAN_Handlej.Enable_Moto(0x06);
    usleep(1000);
    CAN_Handlej.Enable_Moto(0x07);
    usleep(1000);
    CAN_Handlej.Enable_Moto(0x08);
    usleep(1000);


}
void arx_arm::get_pos()
{

        arx5_cmd.x           = ramp(arx5_cmd.x_t  ,  arx5_cmd.x ,0.0045 );
        arx5_cmd.y           = ramp(arx5_cmd.y_t  ,  arx5_cmd.y ,0.0045 );
        arx5_cmd.z           = ramp(arx5_cmd.z_t  ,  arx5_cmd.z ,0.0045 );


        // arx5_cmd.x           = arx5_cmd.x_t  ;
        // arx5_cmd.y           = arx5_cmd.y_t  ;
        // arx5_cmd.z           = arx5_cmd.z_t  ;



        arx5_cmd.x           = limit<float>(arx5_cmd.x             , lower_bound_waist[0], upper_bound_waist[0]);
        arx5_cmd.y           = limit<float>(arx5_cmd.y             , lower_bound_waist[1], upper_bound_waist[1]);
        arx5_cmd.z           = limit<float>(arx5_cmd.z             , lower_bound_waist[2], upper_bound_waist[2]);
        arx5_cmd.waist_roll  = limit<float>(arx5_cmd.waist_roll    , lower_bound_pitch, upper_bound_pitch);
        arx5_cmd.waist_pitch = limit<float>(arx5_cmd.waist_pitch   , lower_bound_yaw, upper_bound_yaw);
        arx5_cmd.waist_yaw   = limit<float>(arx5_cmd.waist_yaw     , lower_bound_roll, upper_bound_roll);        

}

void arx_arm::get_joint()
{
    current_pos[0] = rv_motor_msg[0].angle_actual_rad;
    current_pos[1] = rv_motor_msg[1].angle_actual_rad;
    current_pos[2] = rv_motor_msg[3].angle_actual_rad;
    current_pos[3] = rv_motor_msg[4].angle_actual_rad;
    current_pos[4] = rv_motor_msg[5].angle_actual_rad;
    current_pos[5] = rv_motor_msg[6].angle_actual_rad;
    current_pos[6] = rv_motor_msg[7].angle_actual_rad;

    current_vel[0] = rv_motor_msg[0].speed_actual_rad;
    current_vel[1] = rv_motor_msg[1].speed_actual_rad;
    current_vel[2] = rv_motor_msg[3].speed_actual_rad;
    current_vel[3] = rv_motor_msg[4].speed_actual_rad;
    current_vel[4] = rv_motor_msg[5].speed_actual_rad;
    current_vel[5] = rv_motor_msg[6].speed_actual_rad;
    current_vel[6] = rv_motor_msg[7].speed_actual_rad;


    for(int i=0;i<6;++i)
    {
        if(current_pos[i]==0)
        ROS_ERROR("motor %d is not connected",i+1);
    }

    current_torque[0] = rv_motor_msg[0].current_actual_float;
    current_torque[1] = rv_motor_msg[1].current_actual_float;
    current_torque[2] = rv_motor_msg[3].current_actual_float;
    current_torque[3] = rv_motor_msg[4].current_actual_float;
    current_torque[4] = rv_motor_msg[5].current_actual_float;
    current_torque[5] = rv_motor_msg[6].current_actual_float;
    current_torque[6] = rv_motor_msg[7].current_actual_float;

    int set_max_torque = 9;
    
        for (float num : current_torque) {
            if (abs(num) > set_max_torque) {
                temp_current_normal++;
            }
        }

        for (float num : current_torque) {
            if(abs(num) > set_max_torque)
            {
                temp_condition = false;
            }
        }
        if(temp_condition)
        {
            temp_current_normal=0;
        }

        if(temp_current_normal>300)
        {
            current_normal = false;
        }

}

void arx_arm::update_real()
{
    arx5_state state = NORMAL;
    //解算后 力矩 solve.jointTorques   关节角度  target_pos   末端姿态solve.End_Effector_Pose
    solve.arm_calc1(arx5_cmd,current_pos,control_mode);
    state = solve.arm_calc2(arx5_cmd,current_pos,target_pos,control_mode,0.0);// 0.115
    
    if(is_starting)
    {
        init_step();//复位及初始化
    }
    else
    {
        if(control_mode == 0  ||  control_mode == 1 ||control_mode==4 || control_mode==5 )//通过解算控制关节
        {
            if(state == OUT_BOUNDARY) ROS_ERROR("waist command out of joint boundary!  please enter >>> R ");
            else if(state == OUT_RANGE) {ROS_ERROR("waist command out of arm range! please enter >>> R ");}
            is_starting=0;
            motor_control();;ROS_INFO("pos_control>>>>>>>>>");
        }

        if(control_mode == 2  ||  control_mode == 3)//直接控制关节
        {
            joint_control();ROS_INFO("joint_control>>>>>>>>>");
        }
    }
            gripper_control();
    //末端姿态solve.End_Effector_Pose 数组中 xyz rpy
    // ROS_INFO("End_Effector_Pose>>>>>>>>> x%f>>,y%f>>,z%f>>,r%f>>,p%f>>,z%f>>",solve.End_Effector_Pose[0],solve.End_Effector_Pose[1],solve.End_Effector_Pose[2],solve.End_Effector_Pose[3],solve.End_Effector_Pose[4],solve.End_Effector_Pose[5]);

    return;
}

void arx_arm::motor_control()
{
    if(current_normal)
    {   
        //J1-J3 Send_moto_Cmd1控制  
        //J4-J6 Send_moto_Cmd2控制
        //Send_moto_Cmd (ID，kd,kd，pos,vel,torque)

        solve.send_pos(target_pos,target_pos_temp);

        limit_joint(target_pos_temp);
        if(control_mode == 0 || control_mode==2 || control_mode==4){
            CAN_Handlej.Send_moto_Cmd1(1, 150, 12, target_pos_temp[0], 0, solve.joint_torque[0]);}else if(control_mode == 1 || control_mode==3 || control_mode ==5 ){
            CAN_Handlej.Send_moto_Cmd2(1, 39, 0.8, target_pos_temp[0], 0, solve.joint_torque[0]);}
            CAN_Handlej.Send_moto_Cmd1(2, 150, 12, target_pos_temp[1], 0, solve.joint_torque[1]); usleep(200);
            CAN_Handlej.Send_moto_Cmd1(4, 150, 12, target_pos_temp[2], 0, solve.joint_torque[2]); usleep(200);
            CAN_Handlej.Send_moto_Cmd2(5, 30, 0.8, target_pos_temp[3], 0, solve.joint_torque[3]); usleep(200);
            CAN_Handlej.Send_moto_Cmd2(6, 25, 0.8, target_pos_temp[4], 0, solve.joint_torque[4]); usleep(200);
            CAN_Handlej.Send_moto_Cmd2(7, 10, 1  , target_pos_temp[5], 0, solve.joint_torque[5]); usleep(200); 
    }else
    {              
            //保护模式 
            CAN_Handlej.Send_moto_Cmd1(1, 0, 12, 0, 0, 0);usleep(200);
            CAN_Handlej.Send_moto_Cmd1(2, 0, 12, 0, 0, 0);usleep(200);
            CAN_Handlej.Send_moto_Cmd1(4, 0, 12, 0, 0, 0);usleep(200);
            CAN_Handlej.Send_moto_Cmd2(5, 0, 1, 0, 0, 0);usleep(200);
            CAN_Handlej.Send_moto_Cmd2(6, 0, 1, 0, 0, 0);usleep(200);
            CAN_Handlej.Send_moto_Cmd2(7, 0, 1, 0, 0, 0);usleep(200);
            ROS_WARN("safe mode!!!!!!!!!");
    }
    // ROS_INFO("\033[32mangle_ current_pos = 1>%f 2>%f 3>%f 4>%f 5>%f 6>%f 7>%f \033[0m",    current_pos[0], \
    //                                                                                      current_pos[1], \
    //                                                                                      current_pos[2], \
    //                                                                                      current_pos[3], \
    //                                                                                      current_pos[4], \
    //                                                                                      current_pos[5], \
    //                                                                                      current_pos[6]); 

    // ROS_INFO("\033[32mangle_ target_pos_temp = 1>%f 2>%f 3>%f 4>%f 5>%f 6>%f 7>%f \033[0m",    target_pos_temp[0], \
    //                                                                                      target_pos_temp[1], \
    //                                                                                      target_pos_temp[2], \
    //                                                                                      target_pos_temp[3], \
    //                                                                                      target_pos_temp[4], \
    //                                                                                      target_pos_temp[5], \
    //                                                                                      target_pos_temp[6]); 

}

void arx_arm::joint_control()
{

    if(current_normal)
    {

        solve.send_pos(ros_control_pos_t,ros_control_pos);
        limit_joint(ros_control_pos);
        if(control_mode == 2){
            CAN_Handlej.Send_moto_Cmd1(1, 150, 12, ros_control_pos[0], 0, solve.joint_torque[0]);}else if(control_mode == 3){
            CAN_Handlej.Send_moto_Cmd2(1, 39, 0.8, ros_control_pos[0], 0, solve.joint_torque[0]);}usleep(200);
            CAN_Handlej.Send_moto_Cmd1(2, 150, 12, ros_control_pos[1], 0, solve.joint_torque[1]);usleep(200);
            CAN_Handlej.Send_moto_Cmd1(4, 150, 12, ros_control_pos[2], 0, solve.joint_torque[2]);usleep(200);
            CAN_Handlej.Send_moto_Cmd2(5, 20, 0.8, ros_control_pos[3], 0, solve.joint_torque[3]);usleep(200);
            CAN_Handlej.Send_moto_Cmd2(6, 20, 0.8, ros_control_pos[4], 0, solve.joint_torque[4]);usleep(200);
            CAN_Handlej.Send_moto_Cmd2(7, 20, 1  , ros_control_pos[5], 0, solve.joint_torque[5]);usleep(200); 
            // ROS_INFO("\033[32mangle_ ros_joint = 1>%f 2>%f 3>%f 4>%f 5>%f 6>%f 7>%f \033[0m",    ros_control_pos_t[0], \
            //                                                                                     ros_control_pos_t[1], \
            //                                                                                     ros_control_pos_t[2], \
            //                                                                                     ros_control_pos_t[3], \
            //                                                                                     ros_control_pos_t[4], \
            //                                                                                     ros_control_pos_t[5], \
            //                                                                                     ros_control_pos_t[6]); 

    }
    else{

                    //保护模式 
            CAN_Handlej.Send_moto_Cmd1(1, 0, 12, 0, 0, 0);usleep(200);
            CAN_Handlej.Send_moto_Cmd1(2, 0, 12, 0, 0, 0);usleep(200);
            CAN_Handlej.Send_moto_Cmd1(4, 0, 12, 0, 0, 0);usleep(200);
            CAN_Handlej.Send_moto_Cmd2(5, 0, 1, 0, 0, 0);usleep(200);
            CAN_Handlej.Send_moto_Cmd2(6, 0, 1, 0, 0, 0);usleep(200);
            CAN_Handlej.Send_moto_Cmd2(7, 0, 1, 0, 0, 0);usleep(200);
            ROS_WARN("safe mode!!!!!!!!!");
    }

}

void arx_arm::init_step()
{
    solve.init_pos(target_pos,current_pos,target_pos_temp,is_starting,is_arrived ,teach2pos_returning,temp_init);

        if(control_mode == 0 || control_mode == 2 || control_mode ==4){
        CAN_Handlej.Send_moto_Cmd1(1, 150, 12, target_pos_temp[0], 0,   solve.joint_torque[0] );}else if(control_mode == 1 || control_mode == 3 || control_mode ==5){
        CAN_Handlej.Send_moto_Cmd2(1, 20, 1,   target_pos_temp[0], 0,   solve.joint_torque[0] );} usleep(200);          
        CAN_Handlej.Send_moto_Cmd1(2, 150, 12, target_pos_temp[1], 0,   solve.joint_torque[1] );usleep(200);
        CAN_Handlej.Send_moto_Cmd1(4, 150, 12, target_pos_temp[2], 0,   solve.joint_torque[2] );usleep(200);
        CAN_Handlej.Send_moto_Cmd2(5, 30, 1 ,  target_pos_temp[3], 0,   solve.joint_torque[3] );usleep(200);
        CAN_Handlej.Send_moto_Cmd2(6, 25, 0.8, target_pos_temp[4], 0,   solve.joint_torque[4] );usleep(200);
        CAN_Handlej.Send_moto_Cmd2(7, 10, 1,   target_pos_temp[5], 0,   solve.joint_torque[5] );usleep(200);  
        CAN_Handlej.Send_moto_Cmd2(8, 3, 1, 0, 0, 0 );usleep(200); 

    cmd_init();
    is_teach_mode = false;
    is_torque_control = false;
    current_normal=true;
    ROS_WARN(">>>is_init>>>");
      
}

int arx_arm::rosGetch()
{ 
    static struct termios oldTermios, newTermios;
    tcgetattr( STDIN_FILENO, &oldTermios);          
    newTermios = oldTermios; 
    newTermios.c_lflag &= ~(ICANON);                      
    newTermios.c_cc[VMIN] = 0; 
    newTermios.c_cc[VTIME] = 0;
    tcsetattr( STDIN_FILENO, TCSANOW, &newTermios);  

    int keyValue = getchar(); 

    tcsetattr( STDIN_FILENO, TCSANOW, &oldTermios);  
    return keyValue;
}

void arx_arm::getKey(char key_t) {
   int wait_key=100;

    if(key_t == 'w')
    arx5_cmd.key_x = arx5_cmd.key_x_t=1;
    else if(key_t == 's')
    arx5_cmd.key_x = arx5_cmd.key_x_t=-1;
    else arx5_cmd.key_x_t++;
    if(arx5_cmd.key_x_t>wait_key)
    arx5_cmd.key_x = 0;

    if(key_t == 'a')
    arx5_cmd.key_y =arx5_cmd.key_y_t= 1;
    else if(key_t == 'd')
    arx5_cmd.key_y =arx5_cmd.key_y_t= -1;
    else if(key_t == 'R')
    arx5_cmd.key_y =arx5_cmd.key_y_t= -1;
    else if(key_t == 'L')
    arx5_cmd.key_y =arx5_cmd.key_y_t= 1;
    else arx5_cmd.key_y_t++;
    if(arx5_cmd.key_y_t>wait_key)
    arx5_cmd.key_y = 0;   

    if(key_t == 'U')
    arx5_cmd.key_z =arx5_cmd.key_z_t= 1;
    else if(key_t == 'D')
    arx5_cmd.key_z =arx5_cmd.key_z_t= -1;
    else arx5_cmd.key_z_t++;
    if(arx5_cmd.key_z_t>wait_key)
    arx5_cmd.key_z = 0;

    if(key_t == 'q')
    arx5_cmd.key_base_yaw =arx5_cmd.key_base_yaw_t= 1;
    else if(key_t == 'e')
    arx5_cmd.key_base_yaw =arx5_cmd.key_base_yaw_t= -1;
    else arx5_cmd.key_base_yaw_t++;
    if(arx5_cmd.key_base_yaw_t>wait_key)
    arx5_cmd.key_base_yaw = 0;

    if(key_t == 'r')
    arx5_cmd.key_reset =arx5_cmd.key_reset_t=1;
    else arx5_cmd.key_reset_t++;
    if(arx5_cmd.key_reset_t>wait_key)
    arx5_cmd.key_reset =0;

    if(key_t == 'i')
    arx5_cmd.key_i =arx5_cmd.key_i_t=1;
    else arx5_cmd.key_i_t++;
    if(arx5_cmd.key_i_t>wait_key)
    arx5_cmd.key_i =0;

    if(key_t == 'p')
    arx5_cmd.key_p =arx5_cmd.key_p_t=1;
    else arx5_cmd.key_p_t++;
    if(arx5_cmd.key_p_t>wait_key)
    arx5_cmd.key_p =0;

    if(key_t == 'o')
    arx5_cmd.key_o =arx5_cmd.key_o_t=1;
    else arx5_cmd.key_o_t++;
    if(arx5_cmd.key_o_t>wait_key)
    arx5_cmd.key_o =0;

    if(key_t == 'c')
    arx5_cmd.key_c =arx5_cmd.key_c_t=1;
    else arx5_cmd.key_c_t++;
    if(arx5_cmd.key_c_t>wait_key)
    arx5_cmd.key_c =0;

    if(key_t == 't')
    arx5_cmd.key_t =arx5_cmd.key_t_t=1;
    else arx5_cmd.key_t_t++;
    if(arx5_cmd.key_t_t>wait_key)
    arx5_cmd.key_t =0;

    if(key_t == 'g')
    arx5_cmd.key_g =arx5_cmd.key_g_t=1;
    else arx5_cmd.key_g_t++;
    if(arx5_cmd.key_g_t>wait_key)
    arx5_cmd.key_g =0; 

    if(key_t == 'm')
    arx5_cmd.key_m =arx5_cmd.key_m_t=1;
    else arx5_cmd.key_m_t++;
    if(arx5_cmd.key_m_t>wait_key)
    arx5_cmd.key_m =0;

    if(key_t == 'n')
    arx5_cmd.key_roll =arx5_cmd.key_roll_t= 1;
    else if(key_t == 'm')
    arx5_cmd.key_roll =arx5_cmd.key_roll_t= -1;
    else arx5_cmd.key_roll_t++;
    if(arx5_cmd.key_roll_t>wait_key)
    arx5_cmd.key_roll = 0;  

    if(key_t == 'l')
    arx5_cmd.key_pitch =arx5_cmd.key_pitch_t= 1;
    else if(key_t == '.')
    arx5_cmd.key_pitch =arx5_cmd.key_pitch_t= -1;
    else arx5_cmd.key_pitch_t++;
    if(arx5_cmd.key_pitch_t>wait_key)
    arx5_cmd.key_pitch = 0;  

    if(key_t == ',')
    arx5_cmd.key_yaw =arx5_cmd.key_yaw_t= 1;
    else if(key_t == '/')
    arx5_cmd.key_yaw =arx5_cmd.key_yaw_t= -1;
    else arx5_cmd.key_yaw_t++;
    if(arx5_cmd.key_yaw_t>wait_key)
    arx5_cmd.key_yaw = 0;  

    if(key_t == 'u')
    arx5_cmd.key_u =arx5_cmd.key_u_t=1;
    else arx5_cmd.key_u_t++;
    if(arx5_cmd.key_u_t>wait_key)
    arx5_cmd.key_u =0;

    if(key_t == 'j')
    arx5_cmd.key_j =arx5_cmd.key_j_t=1;
    else arx5_cmd.key_j_t++;
    if(arx5_cmd.key_j_t>wait_key)
    arx5_cmd.key_j =0;

    if(key_t == 'h')
    arx5_cmd.key_h =arx5_cmd.key_h_t=1;
    else arx5_cmd.key_h_t++;
    if(arx5_cmd.key_h_t>wait_key)
    arx5_cmd.key_h =0;

    if(key_t == 'k')
    arx5_cmd.key_k =arx5_cmd.key_k_t=1;
    else arx5_cmd.key_k_t++;
    if(arx5_cmd.key_k_t>wait_key)
    arx5_cmd.key_k =0;

    if(key_t == 'v')
    arx5_cmd.key_v =arx5_cmd.key_v_t=1;
    else arx5_cmd.key_v_t++;
    if(arx5_cmd.key_v_t>wait_key)
    arx5_cmd.key_v =0;

    if(key_t == 'b')
    arx5_cmd.key_b =arx5_cmd.key_b_t=1;
    else arx5_cmd.key_b_t++;
    if(arx5_cmd.key_b_t>wait_key)
    arx5_cmd.key_b =0;
    
    return ;
}

void arx_arm::gripper_control()
{

            gripper_pos=arx5_cmd.gripper;
            if(gripper_pos<-0.1 )
                gripper_pos=-0.1;
            else if(gripper_pos>5)
                gripper_pos=5;

            CAN_Handlej.Send_moto_Cmd2(8, 3, 1,   gripper_pos, 0,  0 );usleep(200);
}

void arx_arm::arm_reset_mode(){
        if((Teleop_Use()->buttons_[1] == 1)|| (arx5_cmd.key_reset==1)) // reset
        {    
            is_starting=1;
        } 
        arx5_cmd.reset = false;
}

void arx_arm::cmd_init()
{
    arx5_cmd.waist_pitch  = arx5_cmd.waist_pitch_t  =arx5_cmd.control_pit   = joy_pitch_t  =joy_pitch      =0      ;
    arx5_cmd.x            = arx5_cmd.x_t            =arx5_cmd.control_x   = joy_x_t      =joy_x            =0   ;
    arx5_cmd.y            = arx5_cmd.y_t            =arx5_cmd.control_y  = joy_y_t      =joy_y             =0   ;
    arx5_cmd.z            = arx5_cmd.z_t            =arx5_cmd.control_z   = joy_z_t      =joy_z            =0   ;      
    arx5_cmd.base_yaw     = arx5_cmd.base_yaw_t     =      0 ;
    arx5_cmd.waist_roll = arx5_cmd.waist_roll_t =arx5_cmd.control_roll   = joy_roll_t   =joy_roll       =0      ;
    arx5_cmd.waist_yaw    = arx5_cmd.waist_yaw_t    =arx5_cmd.control_yaw   = joy_yaw_t    =joy_yaw        =0      ;
    arx5_cmd.mode = FORWARD;

}

void arx_arm::limit_joint(float* Set_Pos)
{
        Set_Pos[0] = limit<float>(Set_Pos[0], solve.Lower_Joint[0], solve.Upper_Joint[0]);
        Set_Pos[1] = limit<float>(Set_Pos[1], solve.Lower_Joint[1], solve.Upper_Joint[1]);
        Set_Pos[2] = limit<float>(Set_Pos[2], solve.Lower_Joint[2], solve.Upper_Joint[2]);
        Set_Pos[3] = limit<float>(Set_Pos[3], solve.Lower_Joint[3], solve.Upper_Joint[3]);
        Set_Pos[4] = limit<float>(Set_Pos[4], solve.Lower_Joint[4], solve.Upper_Joint[4]);
        Set_Pos[5] = limit<float>(Set_Pos[5], solve.Lower_Joint[5], solve.Upper_Joint[5]);
}