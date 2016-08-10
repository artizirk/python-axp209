A Python library for talking to the AXP209 power management unit
================================================================

It should run on python2 and python3
and uses patched smbus library https://github.com/artizirk/smbus2

Installation
------------


        pip install git+https://github.com/artizirk/smbus2
        pip install git+https://github.com/artizirk/python-axp209


Examples
--------

        >>> from axp209 import AXP209
        >>> axp = AXP209()
        >>> axp.battery_voltage
        4144.8
        >>> axp.battery_discharge_current
        269.0
        >>>
