A Python library for talking to the AXP209 power management unit
================================================================

AXP209 is a pmu that is used on quite few Allwinner embeded boards, like C.H.I.P
and Cubietruck.

Because currently the sysfs api for AXP209 is in flux I wrote
this library that bypasses the kernel and directly talks to the AXP209 over I2C
bus using `smbus2 <https://github.com/kplindegaard/smbus2>`_ library.

This library runs on both Python 2.7 and Python 3

Installation
------------

.. code::

    pip install smbus2
    pip install axp209


Examples
--------



.. code::

    >>> from axp209 import AXP209
    >>> axp = AXP209()
    >>> axp.battery_voltage
    4144.8
    >>> axp.battery_discharge_current
    269.0
    >>>


Read and print out all the battery status values

.. code:: python

    from axp209 import AXP209

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


Blink CHIP status led

.. code:: python

    from time import sleep
    from axp209 import AXP209

    with AXP209() as axp:
        while True:
            axp.gpio2_output = False
            sleep(1)
            axp.gpio2_output = True
            sleep(1)
