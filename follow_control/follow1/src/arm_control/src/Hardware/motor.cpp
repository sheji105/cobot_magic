#include "Hardware/motor.h"
#define KP_MIN 0.0f
#define KP_MAX 500.0f
#define KD_MIN 0.0f
#define KD_MAX 50.0f
#define POS_MIN -12.5f
#define POS_MAX 12.5f
#define SPD_MIN -18.0f
#define SPD_MAX 18.0f
#define T_MIN -30.0f
#define T_MAX 30.0f
#define I_MIN -30.0f
#define I_MAX 30.0f


#define DM_P_MIN  -12.5f // Radians
#define DM_P_MAX  12.5f
#define DM_V_MIN  -45.0f // Rad/s
#define DM_V_MAX  45.0f
#define DM_KP_MIN 0.0f  // N-m/rad
#define DM_KP_MAX 500.0f
#define DM_KD_MIN 0.0f // N-m/rad/s
#define DM_KD_MAX 5.0f
#define DM_T_MIN  -18.0f
#define DM_T_MAX  18.0f





union RV_TypeConvert1
{
	float to_float;
	int to_int;
	unsigned int to_uint;
	uint8_t buf[4];
}rv_type_convert1;

union RV_TypeConvert
{
	float to_float;
	int to_int;
	unsigned int to_uint;
	uint8_t buf[4];
}rv_type_convert;


MotorCommFbd motor_comm_fbd = {0};
OD_Motor_Msg rv_motor_msg[10] = {};
float magic_pos[3]={0,0,0};
float magic_angle[3]={0,0,0};
int t_magic_pos[3]={0,0,0};
int t_magic_angle[3]={0,0,0};
int magic_switch[2]={0,0};





void MotorSetting(uint16_t motor_id,uint8_t cmd,uint8_t* Data,uint32_t* canID)
{
    *canID = motor_id;
	if(cmd==0) return;
    Data[0] = motor_id>>8;
    Data[1] = motor_id&0xff;
    Data[2] = 0x00;
    Data[3] = cmd;
    
}


void Moto_reback(uint32_t msgID, uint8_t* Data, int32_t databufferlen, uint8_t comm_mode)
{
    uint8_t motor_id_t = 0;
    uint8_t ack_status = 0;
    int pos_int = 0;
    int spd_int = 0;
    int cur_int = 0;
        if (comm_mode == 0x00) // Response mode
    {
        ack_status = Data[0] >> 5;
        motor_id_t = msgID - 1;
        rv_motor_msg[motor_id_t].motor_id = motor_id_t;
        rv_motor_msg[motor_id_t].error = Data[0] & 0x1F;
        if (ack_status == 1) // response frame 1
        {
            pos_int = Data[1] << 8 | Data[2];
            spd_int = Data[3] << 4 | (Data[4] & 0xF0) >> 4;
            cur_int = (Data[4] & 0x0F) << 8 | Data[5];

            rv_motor_msg[motor_id_t].angle_actual_rad = uint_to_float(pos_int, POS_MIN, POS_MAX, 16);
            rv_motor_msg[motor_id_t].speed_actual_rad = uint_to_float(spd_int, SPD_MIN, SPD_MAX, 12);
            rv_motor_msg[motor_id_t].current_actual_float = uint_to_float(cur_int, I_MIN, I_MAX, 12);
            rv_motor_msg[motor_id_t].temperature = (Data[6] - 50) / 2;
        }
        else if (ack_status == 2) // response frame 2
        {
            rv_type_convert.buf[0] = Data[4];
            rv_type_convert.buf[1] = Data[3];
            rv_type_convert.buf[2] = Data[2];
            rv_type_convert.buf[3] = Data[1];
            rv_motor_msg[motor_id_t].angle_actual_float = rv_type_convert.to_float;
            rv_motor_msg[motor_id_t].current_actual_int = Data[5] << 8 | Data[6];
            rv_motor_msg[motor_id_t].temperature = (Data[7] - 50) / 2;
            rv_motor_msg[motor_id_t].current_actual_float = rv_motor_msg[motor_id_t].current_actual_int / 100.0f;
        }
        
        
    }

}

void Moto_back2(uint32_t msgID, uint8_t* Data)
{
    switch(Data[0])
    {
        case 0x01:
        case 0x02:
        case 0x03:
        case 0x04:
        case 0x05:
        case 0x06:
        case 0x07:
        {
            Moto_reback2(Data);
            break;
        }

    }

    
}
void Moto_reback2(uint8_t* Data)
{
    uint8_t motor_id_t = 0;
    uint8_t ack_status = 0;
    int pos_int,spd_int,cur_int;

    // motor_id_t = Data[0] - 1;
    motor_id_t = (Data[0]&0x0F)-1;
    rv_motor_msg[motor_id_t].motor_id = motor_id_t;
    pos_int = (Data[1] << 8) | (Data[2]);
    spd_int = (Data[3] << 4) | (Data[4] >> 4);
    cur_int = ((Data[4] & 0x0F) << 8) | (Data[5]);

    rv_motor_msg[motor_id_t].angle_actual_rad = (float)uint_to_float(pos_int, -12.5, 12.5, 16);
    rv_motor_msg[motor_id_t].speed_actual_rad = uint_to_float(spd_int, -45.0, 45.0, 12);
    rv_motor_msg[motor_id_t].current_actual_float = uint_to_float(cur_int, -18.0, 18.0, 12);
    // ROS_WARN("moto 7 >> %f",rv_motor_msg[motor_id_t].angle_actual_rad);

}

void Gripper_can_data_repack(uint32_t msgID, uint8_t* Data)
{
    rv_motor_msg[8].gripper_last_pos=rv_motor_msg[8].gripper_pos;
    rv_motor_msg[8].gripper_spd=((int16_t)(Data[5]<<8) |(Data[4]))/57.3f;
    rv_motor_msg[8].gripper_pos=((int16_t)(Data[7]<<8) |(Data[6]))+32768;//	32768
    rv_motor_msg[8].gripper_cur=((int16_t)(Data[2]<<8) |(Data[3]));
    if (rv_motor_msg[8].gripper_pos - rv_motor_msg[8].gripper_last_pos > 32768)
        rv_motor_msg[8].round_cnt--;
    else if (rv_motor_msg[8].gripper_pos - rv_motor_msg[8].gripper_last_pos < -32768)
        rv_motor_msg[8].round_cnt++;
    rv_motor_msg[8].gripper_totalangle = rv_motor_msg[8].round_cnt * 65536 + rv_motor_msg[8].gripper_pos;
   
}