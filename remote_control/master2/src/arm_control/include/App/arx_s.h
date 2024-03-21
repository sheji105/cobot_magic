#ifndef _arx_s_H_
#define _arx_s_H_
  
#include <signal.h>  
#include "../Hardware/can.h"
#include <unistd.h>

bool arx_flag = false;
void arx_1(int arx_1);
void arx_2(can CAN_Handlej);

#endif