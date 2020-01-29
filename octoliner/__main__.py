import time

from .octoliner import Octoliner


def main():
    # Create an object for working with 8-channel line sensor.
    octo = Octoliner(42)
    # Set the sensitivity of the photodetectors.
    octo.set_sensitivity(1.0)

    try:
        while True:
            # Print the current line position in the console.
            print(octo.track_line())
            # Wait 0.5 seconds.
            time.sleep(0.5)
    except KeyboardInterrupt:
        pass


if __name__ == "__main__":
    main()
