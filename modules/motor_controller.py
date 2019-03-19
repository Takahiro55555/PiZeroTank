'''
GPIOからモーターを制御するクラス
Raspberry Pi Zero 専用（他のボードではピン番号が異なるため）
Author:Takahiro55555

MOTOR DRIVER : TA7291P
____________________________________
| IN1 | IN2 | OUT1 | OUT2 |  MODE  |
------------------------------------
|  0  |  0  |  ∞   |  ∞   |  STOP  |
|  1  |  0  |  H   |  L   | CW/CCW | *
|  0  |  1  |  L   |  H   | CCW/CW |
|  1  |  1  |  L   |  L   |  BRAKE |
""""""""""""""""""""""""""""""""""""
* の状態を前進とする
'''
import pigpio
class MotorController(object):
    """docstring for MotorController."""
    def __init__(self):
        self.__R_PWM_PIN = 18
        self.__L_PWM_PIN = 13
        self.__PWM_FREQUENCY = 10000 # 10kHz
        self.__R1_INPUT = 27
        self.__R2_INPUT = 22
        self.__L1_INPUT = 5
        self.__L2_INPUT = 6

        self.__pi = pigpio.pi()
        output_pin_list = [self.__R_PWM_PIN, self.__L_PWM_PIN, self.__R1_INPUT, self.__R2_INPUT, self.__L1_INPUT, self.__L2_INPUT]
        for output_pin in output_pin_list:
            self.__pi.set_mode(output_pin, pigpio.OUTPUT)

        self.__r_before_direction = 0
        self.__l_before_direction = 0

    # モーターの出力と回転方向を変更する（pwm）
    # 回転方向逆転時の停止処理は無い
    # -1.0 <= value_l, value_r <= 1.0
    def __operate_motor(self, value_r=0, value_l=0):
        # NOTE: hardware PWM dutycycle 0-1000000
        self.__pi.hardware_PWM(self.__R_PWM_PIN, self.__PWM_FREQUENCY, abs(int(value_r * 1000000)))
        self.__pi.hardware_PWM(self.__L_PWM_PIN, self.__PWM_FREQUENCY, abs(int(value_l * 1000000)))
        if value_r == 0 and value_l == 0: # 停止（非ブレーキ）
            self.__pi.write(self.__R1_INPUT, 0)
            self.__pi.write(self.__L1_INPUT, 0)
            self.__pi.write(self.__R2_INPUT, 0)
            self.__pi.write(self.__L2_INPUT, 0)
        elif value_r >= 0 and value_l >= 0: # 前進
            self.__pi.write(self.__R1_INPUT, 1)
            self.__pi.write(self.__L1_INPUT, 1)
            self.__pi.write(self.__R2_INPUT, 0)
            self.__pi.write(self.__L2_INPUT, 0)
        elif value_r >= 0 and value_l <= 0: # 左折
            self.__pi.write(self.__R1_INPUT, 1)
            self.__pi.write(self.__L1_INPUT, 0)
            self.__pi.write(self.__R2_INPUT, 0)
            self.__pi.write(self.__L2_INPUT, 1)
        elif value_r <= 0 and value_l >= 0: # 右折
            self.__pi.write(self.__R1_INPUT, 0)
            self.__pi.write(self.__L1_INPUT, 1)
            self.__pi.write(self.__R2_INPUT, 1)
            self.__pi.write(self.__L2_INPUT, 0)
        elif value_r >= 0 and value_l >= 0: # 後進
            self.__pi.write(self.__R1_INPUT, 0)
            self.__pi.write(self.__L1_INPUT, 0)
            self.__pi.write(self.__R2_INPUT, 1)
            self.__pi.write(self.__L2_INPUT, 1)


    def apply_brake(self):
        self.__pi.write(self.__R1_INPUT, 1)
        self.__pi.write(self.__L1_INPUT, 1)
        self.__pi.write(self.__R2_INPUT, 1)
        self.__pi.write(self.__L2_INPUT, 1)

    # value_x 左右の方向を決定する
    # value_y 前進、後進とモーターの出力を決定する
    def apply_operation(self, value_x=0, value_y=0):
        self.__operate_motor(value_x, value_y)
        if(value_y > 0):
            pass
        elif(value_x < 0):
            pass
        else:
            pass

    def __del__(self):
        self.__pi.stop()
