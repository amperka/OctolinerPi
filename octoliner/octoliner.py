import math

from .gpioexp import gpioexp
from .gpioexp import GPIO_EXPANDER_DEFAULT_I2C_ADDRESS as DFLT_ADDR, OUTPUT


class Octoliner(gpioexp):
    """
    Class for 8-channel Line sensor.

    Methods:
    --------
    set_sensitivity(sense: float) -> None
        Sets the sensitivity of the photodetectors in the range
        from 0 to 1.0.

    analog_read(sensor: float) -> float
        Reads the value from one line sensor.
        Return value in range from 0 to 1.0.

    analog_read_all(analog_values: list) -> None
        Reads all 8 channels to the analog_values list.

    map_analog_to_pattern(analog_values: list) -> int
        Creates a 8-bit pattern from the analog_values list.

    map_pattern_to_line(binary_line: int) -> float
        Interprets channel pattern as a line position in the range from
        -1.0 (on the left extreme) to +1.0 (on the right extreme).
        When the line is under the sensor center, the return value
        is 0.0. If the current sensor reading does not allow
        understanding of the line position the NaN value is returned.

    digital_read_all() -> int
        Reads all 8 channels and interpret them as a binary pattern.

    track_line(values: None, list or int) -> float
        Estimates line position under the sensor and returns the value
        in the range from -1.0 (on the left extreme) to +1.0 (on the
        right extreme). When the line is under the sensor center,
        the return value is 0.0.

    change_address(new_addres: int) -> None
        Changes the I²C address of the module.

    save_address() -> None
        Permanently saves the current board I²C address.

    """

    def __init__(self, i2c_address=DFLT_ADDR):
        """
        The constructor for Octoliner class.

        Parameters:
        -----------
        i2c_address: int
            Board address on I2C bus (default is 42).
        """
        super().__init__(i2c_address)

        self._ir_leds_pin = 9
        self.pinMode(self._ir_leds_pin, OUTPUT)
        self.digitalWrite(self._ir_leds_pin, 1)

        self.pwmFreq(8000)

        self._sense_pin = 0
        self._sensor_pin_map = (4, 5, 6, 8, 7, 3, 2, 1)
        self._previous_value = 0

    def set_sensitivity(self, sense):
        """
        Sets the sensitivity of the photodetectors in the range
        from 0 to 1.0.

        Parameters:
        -----------
        sense: float
            Sensitivity of the photodetectors in the range
            from 0 to 1.0.
        """
        self.analogWrite(self._sense_pin, sense)

    def analog_read(self, sensor):
        """
        Reads the value from one line sensor.
        Return value in range from 0 to 1.0.

        Parameters:
        -----------
        sensor: int
            Pin number to get value from.
        """
        sensor &= 0x07
        return self.analogRead(self._sensor_pin_map[sensor])

    def analog_read_all(self, analog_values):
        """
        Reads all 8 channels to the analog_values list.

        Parameters:
        -----------
        analog_values: list
            A list to which line sensors data is recorded.
        """
        for i in range(8):
            analog_values.append(self.analog_read(i))

    def map_analog_to_pattern(self, analog_values):
        """
        Creates a 8-bit pattern from the analog_values list.
        One bit for one channel. "1" is for dark and "0" is for light.

        Parameters:
        -----------
        analog_values: list
            List of data values from line sensors.
        """
        pattern = 0
        # Search min and max values in analog_values list.
        min_val = float("inf")
        max_val = 0
        for val in analog_values:
            if val < min_val:
                min_val = val
            if val > max_val:
                max_val = val
        threshold = min_val + (max_val - min_val) / 2
        for val in analog_values:
            pattern = (pattern << 1) + (0 if val < threshold else 1)
        return pattern

    def map_pattern_to_line(self, binary_line):
        """
        Interprets channel pattern as a line position in the range from
        -1.0 (on the left extreme) to +1.0 (on the right extreme).
        When the line is under the sensor center, the return value
        is 0.0. If the current sensor reading does not allow
        understanding of the line position the NaN value is returned.

        Parameters:
        -----------
        binary_line: int
            Combination of data from line sensors.
        """
        patterns_dict = {
            0b00011000: 0,
            0b00010000: 0.25,
            0b00111000: 0.25,
            0b00001000: -0.25,
            0b00011100: -0.25,
            0b00110000: 0.375,
            0b00001100: -0.375,
            0b00100000: 0.5,
            0b01110000: 0.5,
            0b00000100: -0.5,
            0b00001110: -0.5,
            0b01100000: 0.625,
            0b11100000: 0.625,
            0b00000110: -0.625,
            0b00000111: -0.625,
            0b01000000: 0.75,
            0b11110000: 0.75,
            0b00000010: -0.75,
            0b00001111: -0.75,
            0b11000000: 0.875,
            0b00000011: -0.875,
            0b10000000: 1.0,
            0b00000001: -1.0,
        }
        # If pattern key exists in patterns_dict return it,
        # else return NaN.
        return patterns_dict.get(binary_line, float("nan"))

    def digital_read_all(self):
        """
        Reads all 8 channels and interpret them as a binary pattern.
        One bit for one channel. 1 is for dark and 0 is for light.
        Returns 8-bit binary pattern.
        """
        analog_values = []
        self.analog_read_all(analog_values)
        return self.map_analog_to_pattern(analog_values)

    def track_line(self, values=None):
        """
        Estimates line position under the sensor and returns the value
        in the range from -1.0 (on the left extreme) to +1.0 (on the
        right extreme). When the line is under the sensor center,
        the return value is 0.0.

        Parameters:
        -----------
        values: None, list or int
            If the argument is None, method reads all channels.
            If the argument is a list of data from line sensors, the
            method converts this list into a pattern and tracks the
            line position using it.
            If the argument is an 8-bit pattern (int), the method
            evaluates the position of the line under the sensor
            based on this pattern.

        """
        if values is None:
            return self.track_line(self.digital_read_all())
        elif isinstance(values, list):
            return self.track_line(self.map_analog_to_pattern(values))
        elif isinstance(values, int):
            result = self.map_pattern_to_line(values)
            result = self._previous_value if math.isnan(result) else result
            self._previous_value = result
            return result

    def change_address(self, new_address):
        """
        Changes the I²C address of the module. The change is in effect
        only while the board is powered on. If you want to save it
        permanently call the save_address method.

        Parameters:
        -----------
        new_address: int
            New I2C address.
        """
        super().changeAddr(new_address)

    def save_address(self):
        """
        Permanently saves the current board I²C address.
        """
        super().saveAddr()
