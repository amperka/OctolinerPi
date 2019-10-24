from octoliner import Octoliner
import time


# Create an object for working with 8-channel line sensor.
octo = Octoliner(42)
# Set the sensitivity of the photodetectors.
octo.set_sensitivity(1.0)


def main():
    try:
        while True:
            # List for storing data values from line sensors.
            data_from_sensors = octo.analog_read_all()
            # Print the current line position in the console.
            print(octo.track_line(data_from_sensors))
            # Wait 0.5 seconds.
            time.sleep(0.5)
    except KeyboardInterrupt:
        pass


if __name__ == "__main__":
    main()