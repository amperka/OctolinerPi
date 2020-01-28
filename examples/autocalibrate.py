from octoliner import Octoliner


# Create an object for working with 8-channel line sensor.
octo = Octoliner()


def main():
    try:
        while True:
            print(
                "Press Enter to calculate the sensitivity or Ctrl^C to exit."
            )
            input()
            # Optimal sensitivity calculation.
            octo.optimize_sensitivity_on_black()
            print("Optimal sensitivity: %.2f\n" % octo.get_sensitivity())
    except KeyboardInterrupt:
        pass


if __name__ == "__main__":
    main()
