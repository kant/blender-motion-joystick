import random # just for testing, gen random vals

import RPi.GPIO as GPIO

try:
    from . import mpu9250_i2c
    error_message = False
except:
    error_message = True

class JoystickReader:
    def __init__(self, trigger_pin, top_pin, keepvals=10, weight=0):
        self.trigger_pin = trigger_pin
        self.top_pin = top_pin
        GPIO.setmode(GPIO.BCM)
        GPIO.setup( [self.trigger_pin, self.top_pin], GPIO.IN, pull_up_down = GPIO.PUD_UP)
        # GPIO.remove_event_detect(self.top_pin)
        self.acceleration_x = Axis('acceleration x', keep_vals=keepvals, weight=weight)
        self.acceleration_y = Axis('acceleration y', keep_vals=keepvals, weight=weight)
        self.acceleration_z = Axis('acceleration z', keep_vals=keepvals, weight=weight)
        self.gyro_x = Axis('gyro x', keep_vals=keepvals, weight=weight)
        self.gyro_y = Axis('gyro y', keep_vals=keepvals, weight=weight)
        self.gyro_z = Axis('gyro z', keep_vals=keepvals, weight=weight)
        self.axes = []
        self.axes.append(self.acceleration_x)
        self.axes.append(self.acceleration_y)
        self.axes.append(self.acceleration_z)
        self.axes.append(self.gyro_x)
        self.axes.append(self.gyro_y)
        self.axes.append(self.gyro_z)
        
    def load_pins(self, trigger_pin, top_pin):
        GPIO.setup([self.trigger_pin, self.top_pin], GPIO.IN, pull_up_down = GPIO.PUD_OFF)
        # GPIO.remove_event_detect(self.top_pin)
        self.trigger_pin = trigger_pin
        self.top_pin = top_pin
        GPIO.setup( [self.trigger_pin, self.top_pin], GPIO.IN, pull_up_down = GPIO.PUD_UP)
        # GPIO.add_event_detect(self.top_pin, GPIO.RISING, callback=self.zero_gyro, bouncetime=200)

    def load_keep_vals_and_weight(self, new_keep_vals, new_weight):
        for ax in self.axes:
            ax.weight = new_weight
            ax.keep_vals = new_keep_vals
        
    def end(self):
        GPIO.setup([self.trigger_pin, self.top_pin], GPIO.IN, pull_up_down = GPIO.PUD_OFF)
        # GPIO.remove_event_detect(self.top_pin)
        
    def top_press(self, empty):
        pass
    
    def trigger_press(self, empty):
        pass
        
    def get_round_of_random_values(self): # for testing without RPi.GPIO
        rand_min = -5
        rand_max = 5
        ax = random.randrange(rand_min,rand_max)/100
        ay = random.randrange(rand_min,rand_max)/100
        az = random.randrange(rand_min,rand_max)/100
        wx = random.randrange(rand_min,rand_max)/100
        wy = random.randrange(rand_min,rand_max)/100
        wz = random.randrange(rand_min,rand_max)/100
        self.acceleration_x.add_val(ax)
        self.acceleration_y.add_val(ay)
        self.acceleration_z.add_val(az)
        self.gyro_x.add_val(wx)
        self.gyro_y.add_val(wy)
        self.gyro_z.add_val(wz)

    def zero_gyro(self):
        self.gyro_x.zero()
        self.gyro_y.zero()
        self.gyro_z.zero()

    def get_vals_from_sensor(self):
        global error_message
        try:
            ax, ay, az, wx, wy, wz = mpu9250_i2c.mpu6050_conv()
            # print(wx,wy,wz)
            # self.acceleration_x.add_val(ax)
            # self.acceleration_y.add_val(ay) + 0.98  # grav offset
            # self.acceleration_z.add_val(az)
            self.gyro_x.add_val(wx)
            self.gyro_y.add_val(wy)
            self.gyro_z.add_val(wz)
            error_message = False
        except:
            error_message = True
        
        
    def get_averages(self): # possibly add "top and trigger" to this 
        return {
            'ax':self.acceleration_x.average,
            'ay':self.acceleration_y.average,
            'az':self.acceleration_z.average,
            'wx':self.gyro_x.average,
            'wy':self.gyro_y.average,
            'wz':self.gyro_z.average,
            'top': GPIO.input(self.top_pin),
            'trigger': GPIO.input(self.trigger_pin)
        }
    
    def get_last(self):
        return {
            'ax':self.acceleration_x.get_last_val(),
            'ay':self.acceleration_y.get_last_val(),
            'az':self.acceleration_z.get_last_val(),
            'wx':self.gyro_x.get_last_val(),
            'wy':self.gyro_y.get_last_val(),
            'wz':self.gyro_z.get_last_val(),
            'top': GPIO.input(self.top_pin),
            'trigger': GPIO.input(self.trigger_pin)
        }

    
class Axis:
    def __init__(self, name, keep_vals=10, weight=0):
        """ 
        Stores rolling average of recorded values for an axis.
        """
        self.name = name
        """ name of the axis """
        self.vals = []
        """ last few values recorded """
        self.average = 0
        """ current average """
        self.keep_vals = keep_vals
        """ number of values to keep """
        self.weight=weight
        """ weights the last reading """
        
    def add_val(self, val):
        self.vals.append(val)
        while len(self.vals) > self.keep_vals:
            self.vals.pop(0)
        total = 0
        for each in self.vals:
            total += each
        self.average = (total + val*self.weight)/ (len(self.vals)+self.weight)
        # print(f"{val} added to {self.name}, new avg: {self.average}")
        
    def get_last_val(self):
        return self.vals[len(self.vals)-1]

    def zero(self):
        self.vals = []
        self.average = 0
        