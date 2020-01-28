# OctolinerPi

A library for Raspberry Pi to interface with the Amperka [Octoliner](https://my.amperka.com/modules/octoliner) 8-channel line sensor.

## Installation

Open the terminal on your Raspberry Pi and use `pip` to install the library:

```shell
pip3 install octoliner
```

If you haven’t enabled I²C support in your Raspbian Linux yet, run the configuration tool to turn it on:

```shell
sudo raspi-config
```

Then: Interfacing Options → I2C → Yes (enable) → Yes (autoload) → \<Finish\> → Yes (reboot). The setting preserves across reboots.

## Testing connection

```console
$ python3 -m octoliner
0
0.5
0.675
0
1
# Ctrl+C to exit
```

## API

Quickstart example:

```python
import time

# Import the class required
# from the library octoliner
from octoliner import Octoliner

# Sensor on the standard bus and address
octoliner = Octoliner()

# Lower sensitivity to 80%
octoliner.set_sensitivity(0.8)

while True:
    # Read all channel values
    values = [octoliner.analog_read(i) for i in range(8)]

    # Print them to console
    print(values)

    # Repeat forever, twice per second
    time.sleep(0.5)
```

See full [API reference in API.md](./API.md).
