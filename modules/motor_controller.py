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
import RPi.GPIO as GPIO
class MotorController(object):
    """docstring for MotorController."""
    def __init__(self):
        self.__R_PWM_PIN = 32
        self.__L_PWM_PIN = 33
        self.__PWM_FREQUENCY = 1000
        self.__R1_INPUT = 11
        self.__R2_INPUT = 13
        self.__L1_INPUT = 15
        self.__L2_INPUT = 37

        chan_list = [self.__R_PWM_PIN, self.__L_PWM_PIN, self.__R1_INPUT, self.__R2_INPUT, self.__L1_INPUT, self.__L2_INPUT]
        GPIO.setmode(GPIO.BOARD)
        GPIO.setup(chan_list, GPIO.OUT)
        self.__r_pwm = GPIO.PWM(self.__R_PWM_PIN, self.__PWM_FREQUENCY)
        self.__l_pwm = GPIO.PWM(self.__L_PWM_PIN, self.__PWM_FREQUENCY)
        self.__r_pwm.start(0)
        self.__l_pwm.start(0)

        self.__r_before_direction = 0
        self.__l_before_direction = 0

    # モーターの出力と回転方向を変更する（pwm）
    # 回転方向逆転時の停止処理は無い
    def __operate_motor(self, value_r=0, value_l=0):
        # NOTE: 片方のPWMを0にしてしまうと、もう片方の出力も0になってしまうのを回避するため微小値を加算
        self.__r_pwm.ChangeDutyCycle(abs(value_r))
        self.__l_pwm.ChangeDutyCycle(abs(value_l))
        if value_r > 0 and value_l > 0: # 前進
            GPIO.output([self.__R1_INPUT, self.__L1_INPUT], GPIO.HIGH)
            GPIO.output([self.__R2_INPUT, self.__L2_INPUT], GPIO.LOW)
        elif value_r > 0 and value_l < 0: # 左折
            GPIO.output([self.__R1_INPUT, self.__L2_INPUT], GPIO.HIGH)
            GPIO.output([self.__R2_INPUT, self.__L1_INPUT], GPIO.LOW)
        elif value_r < 0 and value_l > 0: # 右折
            GPIO.output([self.__R2_INPUT, self.__L1_INPUT], GPIO.HIGH)
            GPIO.output([self.__R1_INPUT, self.__L2_INPUT], GPIO.LOW)
        elif value_r > 0 and value_l > 0: # 後進
            GPIO.output([self.__R2_INPUT, self.__L2_INPUT], GPIO.HIGH)
            GPIO.output([self.__R1_INPUT, self.__L1_INPUT], GPIO.LOW)
        else: # 停止（非ブレーキ）
            GPIO.output([self.__R1_INPUT, self.__R2_INPUT, self.__L1_INPUT, self.__L2_INPUT], GPIO.LOW)

    def apply_brake(self):
        GPIO.output([self.__R1_INPUT, self.__R2_INPUT, self.__L1_INPUT, self.__L2_INPUT], GPIO.HIGH)

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
        self.__r_pwm.stop()
        self.__l_pwm.stop()
        GPIO.cleanup()
