# Octoliner API

## `class Octoliner`

Create an object `Octoliner` to communicate with a particular Octoliner board.

### `Octoliner(i2c_address=42)`

The constructor for Octoliner class. The `i2c_address` specifies the board
I²C address which is `42` factory-default but can be changed programmatically.

### `set_sensitivity(sense: float) -> None`

Sets the sensitivity of the photodetectors in the range from `0` to `1.0`.

### `analog_read(sensor: int) -> float`

Reads the value from one line sensor. Return value in range from `0` to `1.0`.

### `analog_read_all(analog_values: list) -> None`

Reads all 8 channels to the `analog_values` list.

### `map_analog_to_pattern(analog_values: list) -> int`

Creates a 8-bit pattern from the `analog_values` list. One bit for one channel.
`1` is for dark and `0` is for light.

### `map_pattern_to_line(binary_line: int) -> float`

Interprets channel pattern as a line position in the range from `-1.0` (on the
left extreme) to `+1.0` (on the right extreme).
When the line is under the sensor center, the return value is `0.0`.
If the current sensor reading does not allow understanding of the line position
the `NaN` value is returned.

### `digital_read_all() -> int`

Reads all 8 channels and interpret them as a binary pattern. One bit for one
channel. `1` is for dark and `0` is for light. Returns 8-bit binary pattern.

### `track_line(values: None, list or int) -> float`

Estimates line position under the sensor and returns the value in the range
from `-1.0` (on the left extreme) to `+1.0` (on the right extreme). When the
line is under the sensor center, the return value is `0.0`.

If the argument `values` is `None`, method reads all channels.

If the argument `values` is a list of data from line sensors, the method
converts this list into a pattern and tracks the line position using it.

If the argument `values` is an 8-bit pattern (`int`), the method evaluates the
position of the line under the sensor based on this pattern.

### `change_address(new_address: int) -> None`

Changes the I²C address of the module. The change is in effect only while the
board is powered on. If you want to save it permanently call the `save_address`
method.

### `save_address() -> None`

Permanently saves the current board I²C address.

