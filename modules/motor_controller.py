'''
    GPIOからモーターを制御するクラス
    Raspberry Pi Zero W で動作確認
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
import pigpio, time
import numpy as np
class MotorController(object):
    """docstring for MotorController."""
    def __init__(self):
        self.__R_PWM_PIN = 18
        self.__L_PWM_PIN = 13
        self.__PWM_FREQUENCY = 10000 # 10kHz
        self.__R1_INPUT = 27
        self.__R2_INPUT = 22
        self.__L1_INPUT = 6
        self.__L2_INPUT = 5

        self.__pi = pigpio.pi()
        self.__output_pin_list = [self.__R_PWM_PIN, self.__L_PWM_PIN, self.__R1_INPUT, self.__R2_INPUT, self.__L1_INPUT, self.__L2_INPUT]
        for output_pin in self.__output_pin_list:
            self.__pi.set_mode(output_pin, pigpio.OUTPUT)

        # 超信地旋回するスティックの角度（sin）
        self.__spin_turn_stick_val_cos = np.cos(np.pi/12) # 弧度法15度

        # モーターの回転方向が変化する操作受付時の時間を入力
        # 一時停止処理終了時に0にする
        self.__r_direction_changed_ms = 0
        self.__l_direction_changed_ms = 0


    # モーターの出力と回転方向を変更する（pwm）
    # 回転方向逆転時の停止処理は無い
    # WARNING: -1.0 <= value_l, value_r <= 1.0
    # HACK: PWM制御とそれ以外の信号制御の処理は分けるべきかも
    def __operate_motor(self, value_r=0, value_l=0):
        # NOTE: hardware PWM dutycycle 0-1000000
        self.__pi.hardware_PWM(self.__R_PWM_PIN, self.__PWM_FREQUENCY, abs(int(value_r * 1000000)))
        self.__pi.hardware_PWM(self.__L_PWM_PIN, self.__PWM_FREQUENCY, abs(int(value_l * 1000000)))
        if value_r == 0 and value_l == 0: # 停止（ニュートラル）
            print("ニュートラル")
            self.__pi.write(self.__R1_INPUT, 0)
            self.__pi.write(self.__L1_INPUT, 0)
            self.__pi.write(self.__R2_INPUT, 0)
            self.__pi.write(self.__L2_INPUT, 0)
        elif value_r >= 0 and value_l >= 0: # 前進
            # print("前進")
            self.__pi.write(self.__R1_INPUT, 1)
            self.__pi.write(self.__L1_INPUT, 1)
            self.__pi.write(self.__R2_INPUT, 0)
            self.__pi.write(self.__L2_INPUT, 0)
        elif value_r >= 0 and value_l <= 0: # 左折
            # print("左折")
            self.__pi.write(self.__R1_INPUT, 0)
            self.__pi.write(self.__L1_INPUT, 1)
            self.__pi.write(self.__R2_INPUT, 1)
            self.__pi.write(self.__L2_INPUT, 0)
        elif value_r <= 0 and value_l >= 0: # 右折
            # print("右折")
            self.__pi.write(self.__R1_INPUT, 1)
            self.__pi.write(self.__L1_INPUT, 0)
            self.__pi.write(self.__R2_INPUT, 0)
            self.__pi.write(self.__L2_INPUT, 1)
        elif value_r <= 0 and value_l <= 0: # 後進
            # print("後進")
            self.__pi.write(self.__R1_INPUT, 0)
            self.__pi.write(self.__L1_INPUT, 0)
            self.__pi.write(self.__R2_INPUT, 1)
            self.__pi.write(self.__L2_INPUT, 1)
        # else:
            # print("該当なし")


    def __calc_radius(self, value_x=0, value_y=0):
        radius = np.sqrt(value_x*value_x + value_y*value_y)
        if radius >= 1:
            return 1
        return radius

    def apply_brake(self):
        self.__pi.write(self.__R1_INPUT, 1)
        self.__pi.write(self.__L1_INPUT, 1)
        self.__pi.write(self.__R2_INPUT, 1)
        self.__pi.write(self.__L2_INPUT, 1)

    # value_x 左右の方向を決定する
    # value_y 前進、後進とモーターの出力を決定する
    def apply_operation(self, value_x=0, value_y=0):
        radius = self.__calc_radius(value_x, value_y)
        # print(radius)
        stick_val_sin = abs(value_x) / radius
        print("stick val:{0}, spin turn val:{1}".format(stick_val_sin, self.__spin_turn_stick_val_cos))
        if stick_val_sin >= self.__spin_turn_stick_val_cos: # 超信地旋回
            self.__operate_motor(value_x, -1*value_x)
            return
        front_or_back = np.sign(value_y) # y 軸の方向によって前後の回転量が決まる
        # print(front_or_back)
        if value_x >= 0:
            self.__operate_motor(front_or_back*(radius - value_x), front_or_back*radius)
            return
        else:
            self.__operate_motor(front_or_back*radius, front_or_back*(radius + value_x))
            return

    def __del__(self):
        self.__pi.stop()
