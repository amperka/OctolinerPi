import math
import time

from .gpioexp import gpioexp
from .gpioexp import GPIO_EXPANDER_DEFAULT_I2C_ADDRESS as DFLT_ADDR, OUTPUT


MIN_SENSITIVITY = 0.47
BLACK_THRESHOLD = 0.39


class Octoliner(gpioexp):
    """
    Class for 8-channel Line sensor.

    Methods:
    --------
    set_sensitivity(sense: float) -> None
        Sets the sensitivity of the photodetectors in the range
        from 0 to 1.0.

    get_sensitivity() -> float
        Returns the current sensitivity level previously set with
        set_sensitivity or optimize_sensitivity_on_blacki methods.
        Return value in range from 0 to 1.0.

    optimize_sensitivity_on_black() -> bool
        Performs automatic sensitivity set up. Before the optimization,
        place Octoliner over the track in a way where all its sensors
        point to the black line/field.
        The method returns true if succeed. If the calibration fails
        it returns false, for example, if the sensors are placed over
        a contrast black/white or a completely white surface. In the
        case of failure, the previous sensitivity level is left intact.
        The measurement time depends on the blackness level. The typical
        value is less than 1 sec, the maximum is 3 sec.

    analog_read(sensor: float) -> float
        Reads the value from one line sensor.
        Return value in range from 0 to 1.0.

    analog_read_all() -> list(float)
        Creates a list and reads data from all 8 channels into it.

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
        self._sensitivity = 0.8

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
        self._sensitivity = sense
        self.analogWrite(self._sense_pin, self._sensitivity)

    def get_sensitivity(self):
        """
        Returns the current sensitivity level previously set with
        set_sensitivity or optimize_sensitivity_on_blacki methods.
        Return value in range from 0 to 1.0.
        """
        return self._sensitivity

    def _count_of_black(self):
        """
        Returns the number of sensors whose values exceed
        the BLACK_THRESHOLD.
        """
        count = 0
        for i in range(8):
            if self.analog_read(i) > BLACK_THRESHOLD:
                count += 1
        return count

    def optimize_sensitivity_on_black(self):
        """
        Performs automatic sensitivity set up. Before the optimization,
        place Octoliner over the track in a way where all its sensors
        point to the black line/field.
        The method returns true if succeed. If the calibration fails
        it returns false, for example, if the sensors are placed over
        a contrast black/white or a completely white surface.  In the
        case of failure, the previous sensitivity level is left intact.
        The measurement time depends on the blackness level. The typical
        value is less than 1 sec, the maximum is 3 sec.
        """
        # Save backup sensitivity value.
        sensitivity_backup = self.get_sensitivity()

        self.set_sensitivity(1.0)
        time.sleep(0.2)

        # Starting at the highest possible sensitivity read all channels
        # at each iteration to find the level when all the channels
        # become black.
        sens = 1.0
        while sens > MIN_SENSITIVITY:
            self.set_sensitivity(sens)
            time.sleep(0.1)
            if self._count_of_black() == 8:
                break
            # Choose step size as 1.0 / 50.
            sens -= 0.02

        # Something is broken
        if sens <= MIN_SENSITIVITY:
            self.set_sensitivity(sensitivity_backup)
            return False

        # Forward fine search to find the level when at least one sensor
        # value will become back white.
        while sens < 1.0:
            self.set_sensitivity(sens)
            time.sleep(0.05)
            if self._count_of_black() != 8:
                break
            # Choose a more accurate step value as 1.0 / 250.
            sens += 0.004

        # Environment has changed since the start of the process.
        if sens >= 1.0:
            self.set_sensitivity(sensitivity_backup)
            return False

        # Step back to fall back to all-eight-black.
        sens -= 0.02
        self.set_sensitivity(sens)
        return True

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

    def analog_read_all(self):
        """
        Creates a list and reads data from all 8 channels into it.

        """
        analog_values = []
        for i in range(8):
            analog_values.append(self.analog_read(i))
        return analog_values

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
        analog_values = self.analog_read_all()
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
        self.changeAddr(new_address)

    def save_address(self):
        """
        Permanently saves the current board I²C address.
        """
        self.saveAddr()
