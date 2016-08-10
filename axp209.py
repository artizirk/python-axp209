#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from __future__ import print_function
from ctypes import c_uint8, BigEndianStructure, Union

# probably need to use my fork: pip install git+https://github.com/artizirk/smbus2
from smbus2 import SMBus


AXP209_ADDRESS = 0x34      #7 bit address (will be left shifted to add the read write bit)

# from CHIP battery.sh script
POWER_INPUT_STATUS_REG = 0x00
POWER_OPERATING_MODE_REG = 0x01
CHARGE_CONTROL_REG = 0x33
CHARGE_CONTROL2_REG = 0x34
ADC_ENABLE1_REG = 0x82
INTERNAL_TEMPERATURE_MSB_REG = 0x5e
INTERNAL_TEMPERATURE_LSB_REG = 0x5f
BATTERY_VOLTAGE_MSB_REG = 0x78
BATTERY_VOLTAGE_LSB_REG = 0x79
BATTERY_CHARGE_CURRENT_MSB_REG = 0x7a
BATTERY_CHARGE_CURRENT_LSB_REG = 0x7b
BATTERY_DISCHARGE_CURRENT_MSB_REG = 0x7c
BATTERY_DISCHARGE_CURRENT_LSB_REG = 0x7d
GPIO0_FEATURE_SET_REG = 0x90
GPIO1_FEATURE_SET_REG = 0x92
GPIO2_FEATURE_SET_REG = 0x93
BATTERY_GAUGE_REG = 0xb9

class Union(Union):

    def __repr__(self):
        return self.__str__()

    def __str__(self):
        flags = " ".join("{}: {}".format(t[0], getattr(self._b, t[0])) for t in self._b._fields_)
        return "<{}>".format(flags)

class ADC_ENABLE1_FLAGS(Union):
    class _b(BigEndianStructure):
        _fields_ = [
            ("battery_voltage_adc_enable", c_uint8, 1),
            ("battery_current_adc_enable", c_uint8, 1),
            ("acin_voltage_adc_enable", c_uint8, 1),
            ("acin_current_adc_enable", c_uint8, 1),
            ("vbus_voltage_adc_enable", c_uint8, 1),
            ("vbus_current_adc_enable", c_uint8, 1),
            ("aps_voltage_adc_enable", c_uint8, 1),
            ("ts_pin_adc_function_enable", c_uint8, 1),
        ]

    _fields_ = [("_b", _b),
                ("asbyte", c_uint8)]

    _anonymous_ = ("_b",)


class POWER_INPUT_STATUS_FLAGS(Union):
    class _b(BigEndianStructure):
        _fields_ = [
            ("acin_present", c_uint8, 1),
            ("acin_available", c_uint8, 1),
            ("vbus_present", c_uint8, 1),
            ("vbus_available", c_uint8, 1),
            ("vbus_direction", c_uint8, 1),
            ("battery_current_direction", c_uint8, 1),  # 1: charging, 0: discharging
            ("acin_vbus_shorted", c_uint8, 1),
            ("start_source", c_uint8, 1)
        ]

    _fields_ = [("_b", _b),
                ("asbyte", c_uint8)]

    _anonymous_ = ("_b",)

class POWER_OPERATING_STATUS_FLAGS(Union):
    class _b(BigEndianStructure):
        _fields_ = [
            ("over-temperature", c_uint8, 1),
            ("battery_charging", c_uint8, 1),  # 1: charging, 0: not charging or charging done
            ("battery_exists", c_uint8, 1), # 1: battery is connected, 0: not connected
            ("_reserved_", c_uint8, 1),
            ("battery_active", c_uint8, 1),
            ("reached_desired_charge_current", c_uint8, 1),
            ("_reserved_", c_uint8, 2),
        ]

    _fields_ = [("_b", _b),
                ("asbyte", c_uint8)]

    _anonymous_ = ("_b",)


class GPIO012_FEATURE_SET_FLAGS(Union):
    class _b(BigEndianStructure):
        _fields_ = [
            ("gpio_rising_edge_interupt", c_uint8, 1),
            ("gpio_falling_edge_interupt", c_uint8, 1),
            ("_reserved_", c_uint8, 3),
            ("gpio_function", c_uint8, 3),
        ]

    _fields_ = [("_b", _b),
                ("asbyte", c_uint8)]

    _anonymous_ = ("_b",)


class AXP209(object):

    def __init__(self, bus=0):
        """
        Initialize the AXP209 object
        :param bus: i2c bus number or a SMBus object
        :type bus: Integer or SMBus object
        """

        if isinstance(bus, int):
            self.bus = SMBus(bus, force=True)
            self.autocleanup = True
        else:
            self.bus = bus
            self.autocleanup = False

        # force ADC enable for battery voltage and current
        self.adc_enable1 = 0xc3


    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        if self.autocleanup:
            self.close()

    def close(self):
        self.bus.close()

    @property
    def gpio2_output(self):
        pass

    @gpio2_output.setter
    def gpio2_output(self, val):
        flags = GPIO012_FEATURE_SET_FLAGS()
        if bool(val):
            flags.gpio_function = 0b111
        else:
            flags.gpio_function = 0b000
        self.bus.write_byte_data(AXP209_ADDRESS, GPIO2_FEATURE_SET_REG, flags.asbyte)

    @property
    def adc_enable1(self):
        flags = ADC_ENABLE1_FLAGS()
        flags.asbyte = self.bus.read_byte_data(AXP209_ADDRESS, ADC_ENABLE1_REG)
        return flags

    @adc_enable1.setter
    def adc_enable1(self, flags):
        if hasattr(flags, "asbyte"):
            flags = flags.asbyte
        self.bus.write_byte_data(AXP209_ADDRESS, ADC_ENABLE1_REG, flags)

    @property
    def power_input_status(self):
        flags = POWER_INPUT_STATUS_FLAGS()
        flags.asbyte = self.bus.read_byte_data(AXP209_ADDRESS, POWER_INPUT_STATUS_REG)
        return flags

    @property
    def battery_current_direction(self):
        return bool(self.power_input_status.battery_current_direction)

    @property
    def power_operating_mode(self):
        flags = POWER_OPERATING_STATUS_FLAGS()
        flags.asbyte = self.bus.read_byte_data(AXP209_ADDRESS, POWER_OPERATING_MODE_REG)
        return flags

    @property
    def battery_exists(self):
        return bool(self.power_operating_mode.battery_exists)

    @property
    def battery_charging(self):
        return bool(self.power_operating_mode.battery_charging)

    @property
    def battery_voltage(self):
        """ Returns voltage in mV """
        msb = self.bus.read_byte_data(AXP209_ADDRESS, BATTERY_VOLTAGE_MSB_REG)
        lsb = self.bus.read_byte_data(AXP209_ADDRESS, BATTERY_VOLTAGE_LSB_REG)
        voltage_bin = msb << 4 | lsb & 0x0f
        return voltage_bin * 1.1

    @property
    def battery_charge_current(self):
        """ Returns current in mA """
        msb = self.bus.read_byte_data(AXP209_ADDRESS, BATTERY_CHARGE_CURRENT_MSB_REG)
        lsb = self.bus.read_byte_data(AXP209_ADDRESS, BATTERY_CHARGE_CURRENT_LSB_REG)
        # (12 bits)
        charge_bin = msb << 4 | lsb & 0x0f
        # 0 mV -> 000h,	0.5 mA/bit	FFFh -> 1800 mA
        return charge_bin * 0.5

    @property
    def battery_discharge_current(self):
        """ Returns current in mA """
        msb = self.bus.read_byte_data(AXP209_ADDRESS, BATTERY_DISCHARGE_CURRENT_MSB_REG)
        lsb = self.bus.read_byte_data(AXP209_ADDRESS, BATTERY_DISCHARGE_CURRENT_LSB_REG)
        # 13bits
        discharge_bin = msb << 5 | lsb & 0x1f
        # 0 mV -> 000h,	0.5 mA/bit	1FFFh -> 1800 mA
        return discharge_bin * 0.5

    @property
    def internal_temperature(self):
        """ Returns temperature in celsius C """
        temp_msb = self.bus.read_byte_data(AXP209_ADDRESS, INTERNAL_TEMPERATURE_MSB_REG)
        temp_lsb = self.bus.read_byte_data(AXP209_ADDRESS, INTERNAL_TEMPERATURE_LSB_REG)
        # MSB is 8 bits, LSB is lower 4 bits
        temp = temp_msb << 4 | temp_lsb & 0x0f
        # -144.7c -> 000h,	0.1c/bit	FFFh -> 264.8c
        return temp*0.1-144.7

    @property
    def battery_gauge(self):
        gauge_bin = self.bus.read_byte_data(AXP209_ADDRESS, BATTERY_GAUGE_REG)
        gauge = gauge_bin & 0x7f
        if gauge > 100:
            return -1
        return gauge

def main():
    axp = AXP209()
    print("internal_temperature: %.2fC" % axp.internal_temperature)
    print("battery_exists: %s" % axp.battery_exists)
    print("battery_charging: %s" % ("charging" if axp.battery_charging else "done"))
    print("battery_current_direction: %s" % ("charging" if axp.battery_current_direction else "discharging"))
    print("battery_voltage: %.1fmV" % axp.battery_voltage)
    print("battery_discharge_current: %.1fmA" % axp.battery_discharge_current)
    print("battery_charge_current: %.1fmA" % axp.battery_charge_current)
    print("battery_gauge: %d%%" % axp.battery_gauge)
    axp.close()

if __name__ == "__main__":
    main()
