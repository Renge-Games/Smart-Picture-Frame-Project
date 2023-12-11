#!/usr/bin/python3
# -*- coding: utf-8 -*-

from settings import *

if RUNS_ON_RPI:
    import smbus
    import math
    import numpy as np
    from time import sleep
    import os
    from datetime import datetime

    # code inspired by http://tutorials-raspberrypi.de/rotation-und-beschleunigung-mit-dem-raspberry-pi-messen/

    # Register
    power_mgmt_1 = 0x6b
    power_mgmt_2 = 0x6c


    class Gyroscope:
        def __init__(self, gy_xout, gy_yout, gy_zout, acc_xout, acc_yout, acc_zout):
            self.gyroskop_xout = gy_xout
            self.gyroskop_yout = gy_yout
            self.gyroskop_zout = gy_zout

            self.gyroskop_xout_scaled = self.gyroskop_xout / 131
            self.gyroskop_yout_scaled = self.gyroskop_yout / 131
            self.gyroskop_zout_scaled = self.gyroskop_zout / 131

            self.acceleration_xout = acc_xout
            self.acceleration_yout = acc_yout
            self.acceleration_zout = acc_zout

            self.acceleration_xout_scaled = self.acceleration_xout / 16384.0
            self.acceleration_yout_scaled = self.acceleration_yout / 16384.0
            self.acceleration_zout_scaled = self.acceleration_zout / 16384.0

            self.rotation_x = get_x_rotation(self.acceleration_xout_scaled, self.acceleration_yout_scaled, self.acceleration_zout_scaled)
            self.rotation_y = get_y_rotation(self.acceleration_xout_scaled, self.acceleration_yout_scaled, self.acceleration_zout_scaled)


    def read_byte(reg):
        return bus.read_byte_data(address, reg)


    def read_word(reg):
        h = bus.read_byte_data(address, reg)
        l = bus.read_byte_data(address, reg + 1)
        value = (h << 8) + l
        return value


    def read_word_2c(reg):
        val = read_word(reg)
        if val >= 0x8000:
            return -((65535 - val) + 1)
        else:
            return val


    def dist(a, b):
        return np.linalg.norm((a, b))


    def get_y_rotation(x, y, z):
        radians = math.atan2(x, dist(y, z))
        return -math.degrees(radians)


    def get_x_rotation(x, y, z):
        radians = math.atan2(y, dist(x, z))
        return math.degrees(radians)


    bus = smbus.SMBus(1)  # bus = smbus.SMBus(0) fuer Revision 1
    address = 0x68  # via i2cdetect

    # Aktivieren, um das Modul ansprechen zu koennen
    bus.write_byte_data(address, power_mgmt_1, 0)


    def read_gyroscope() -> Gyroscope:
        gyroskop_xout = read_word_2c(0x43)
        gyroskop_yout = read_word_2c(0x45)
        gyroskop_zout = read_word_2c(0x47)

        acceleration_xout = read_word_2c(0x3b)
        acceleration_yout = read_word_2c(0x3d)
        acceleration_zout = read_word_2c(0x3f)

        gy = Gyroscope(gyroskop_xout, gyroskop_yout, gyroskop_zout, acceleration_xout, acceleration_yout, acceleration_zout)
        return gy

    now_shake = datetime.now()
    # run xrandr --listmonitors
    def rotate_screen(gy: Gyroscope, uiapp=None):
        global now_shake

        if gy.acceleration_zout > 1.8 and (datetime.now() - now_shake).seconds > 1 and uiapp is not None:
            print("shaking")
            uiapp.show_next_img()
            now_shake = datetime.now()


    def main():
        while True:
            gy = read_gyroscope()

            print("Gyroskop")
            print("--------")

            print("gyroskop_yout: ", ("%5d" % gy.gyroskop_yout), " skaliert: ", gy.gyroskop_yout_scaled)
            print("gyroskop_zout: ", ("%5d" % gy.gyroskop_zout), " skaliert: ", gy.gyroskop_zout_scaled)
            print("gyroskop_xout: ", ("%5d" % gy.gyroskop_xout), " skaliert: ", gy.gyroskop_xout_scaled)

            print()
            print("Beschleunigungssensor")
            print("---------------------")

            print("beschleunigung_xout: ", ("%6d" % gy.acceleration_xout), " skaliert: ", gy.acceleration_xout_scaled)
            print("beschleunigung_yout: ", ("%6d" % gy.acceleration_yout), " skaliert: ", gy.acceleration_yout_scaled)
            print("beschleunigung_zout: ", ("%6d" % gy.acceleration_zout), " skaliert: ", gy.acceleration_zout_scaled)

            print()
            print("Rotation")
            print("--------")
            print("X Rotation: ", gy.rotation_x)
            print("Y Rotation: ", gy.rotation_y)

            rotate_screen(gy)

            sleep(0.1)


    if __name__ == "__main__":
        main()

else:  # mock methods

    def rotate_screen(gy):
        pass

    def read_gyroscope():
        pass
